from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from IPython.display import Markdown

# Define models for structured outputs
class ClauseExtraction(BaseModel):
    """Extracted key clause from an NDA contract"""
    clause_name: str
    section_reference: str
    clause_text: str
    importance: int = Field(description="Importance rating from 1-10")

class PolicyMatch(BaseModel):
    """Policy match analysis for a contract clause"""
    clause_name: str
    policy_alignment: int = Field(description="Rating from 0-100 of how well the clause aligns with policy")
    policy_reference: str = Field(description="Reference to relevant policy section")
    issues: List[str] = Field(description="List of issues or concerns with the clause")
    compliant: bool = Field(description="Whether the clause is compliant with policy")

class ClauseSuggestion(BaseModel):
    """Suggested improvements for a contract clause"""
    clause_name: str
    suggested_text: str = Field(description="Suggested improved text for the clause")
    explanation: str = Field(description="Explanation of why this change is recommended")
    importance: int = Field(description="Importance of making this change, 1-10")

class FinalReview(BaseModel):
    """Final contract review with suggestions"""
    overall_score: int = Field(description="Overall compliance score from 0-100")
    key_strengths: List[str] = Field(description="Key strengths of the contract")
    key_issues: List[str] = Field(description="Key issues that need addressing")
    recommendations: List[str] = Field(description="Specific recommendations to improve the contract")

# Shared dependencies class
@dataclass
class ContractReviewDeps:
    contract_text: str
    policy_text: str
    extracted_clauses: Optional[List[ClauseExtraction]] = None
    policy_matches: Optional[List[PolicyMatch]] = None
    clause_suggestions: Optional[List[ClauseSuggestion]] = None

# Create the agents with specific roles
extractor_agent = Agent(
    model='openai:gpt-4.1-mini',
    system="""You are a legal document analysis specialist focusing on contract clause extraction.
Your job is to identify and extract key clauses from Non-Disclosure Agreements (NDAs).

Extract clauses that are most legally significant, focusing on:
- Definition of Confidential Information
- Term and termination
- Obligations of confidentiality
- Permitted disclosures/exceptions
- Return/destruction of information
- Governing law and jurisdiction
- Remedies for breach
- Personal data protection

Be precise and thorough. Extract exact text and provide accurate section references.""",
    output_type=List[ClauseExtraction]
)

policy_agent = Agent(
    model='openai:gpt-4.1',
    system="""You are a legal compliance specialist focusing on NDA policy alignment.
Your job is to compare contract clauses against a company's NDA policy to identify compliance issues.

For each clause, analyze:
1. How well it aligns with company policy (score 0-100)
2. Identify the specific policy section(s) it relates to
3. List specific issues or discrepancies
4. Determine if the clause is ultimately compliant

Be thorough in your analysis and focus on substantive legal issues.""",
    output_type=List[PolicyMatch]
)

suggestion_agent = Agent(
    model='openai:gpt-4.1-mini',
    system="""You are a legal drafting specialist focusing on contract improvement.
Your job is to suggest improved language for contract clauses that don't align with company policy.

For each non-compliant clause:
1. Draft revised text that would make the clause compliant
2. Explain why this change is recommended
3. Rate the importance of making this change (1-10)

Write in clear, precise legal language. Focus on legally significant changes.""",
    output_type=List[ClauseSuggestion]
)

# Main orchestrator agent with tools to call other agents
orchestrator = Agent(
    model='openai:gpt-4.1',
    system="""You are a legal contract review coordinator overseeing the review of an NDA.
You will:
1. Extract key clauses from the contract
2. Analyze each clause against company policy
3. Generate suggestions for improvement
4. Produce a final comprehensive review

Work systematically and ensure all important clauses are reviewed thoroughly.""",
    output_type=FinalReview,
    deps_type=ContractReviewDeps
)

# Define tools for the orchestrator
@orchestrator.tool
async def extract_clauses(ctx: RunContext[ContractReviewDeps]) -> List[ClauseExtraction]:
    """Extract key clauses from the contract"""
    result = extractor_agent.run_sync(
        f"Extract the key clauses from this NDA contract:\n\n{ctx.deps.contract_text}"
    )
    ctx.deps.extracted_clauses = result.output
    return result.output

@orchestrator.tool
async def analyze_policy_compliance(ctx: RunContext[ContractReviewDeps]) -> List[PolicyMatch]:
    """Analyze how well each clause complies with company policy"""
    if not ctx.deps.extracted_clauses:
        raise ValueError("No clauses extracted yet. Run extract_clauses first.")
    
    clauses_text = "\n\n".join([
        f"Clause: {c.clause_name}\nReference: {c.section_reference}\nText: {c.clause_text}"
        for c in ctx.deps.extracted_clauses
    ])
    
    result = policy_agent.run_sync(
        f"""Analyze these contract clauses against our company policy:

Contract Clauses:
{clauses_text}

Company NDA Policy:
{ctx.deps.policy_text}"""
    )
    
    ctx.deps.policy_matches = result.output
    return result.output

@orchestrator.tool
async def generate_suggestions(ctx: RunContext[ContractReviewDeps]) -> List[ClauseSuggestion]:
    """Generate suggestions for improving non-compliant clauses"""
    if not ctx.deps.policy_matches:
        raise ValueError("No policy analysis completed. Run analyze_policy_compliance first.")
    
    # Identify non-compliant clauses
    non_compliant = [m for m in ctx.deps.policy_matches if not m.compliant]
    
    if not non_compliant:
        return []  # No improvements needed
    
    # Prepare the input for the suggestion agent
    non_compliant_details = []
    for match in non_compliant:
        # Find the original clause text
        original = next(
            (c for c in ctx.deps.extracted_clauses if c.clause_name == match.clause_name), 
            None
        )
        
        if original:
            policy_section = find_policy_section(ctx.deps.policy_text, match.policy_reference)
            
            non_compliant_details.append(
                f"Clause: {match.clause_name}\n"
                f"Section: {original.section_reference}\n"
                f"Original Text: {original.clause_text}\n"
                f"Issues: {', '.join(match.issues)}\n"
                f"Policy Section: {policy_section}"
            )
    
    if not non_compliant_details:
        return []
    
    separator = "=" * 50
    formatted_details = "\n".join([f"{separator}\n{detail}\n{separator}" for detail in non_compliant_details])
    
    prompt = f"""Generate suggested improvements for these non-compliant clauses:

{formatted_details}

For each clause, suggest revised text that would make it compliant with our policy."""
    
    result = suggestion_agent.run_sync(prompt)
    ctx.deps.clause_suggestions = result.output
    return result.output

# Helper function to find relevant policy section
def find_policy_section(policy_text, section_reference):
    # Simple implementation - in a real system this would be more sophisticated
    pattern = f"##\\s*{re.escape(section_reference)}"
    match = re.search(pattern, policy_text)
    if not match:
        return "Policy section not found"
    
    start_idx = match.start()
    next_section = re.search("##", policy_text[start_idx + 2:])
    
    if next_section:
        end_idx = start_idx + 2 + next_section.start()
        return policy_text[start_idx:end_idx].strip()
    else:
        return policy_text[start_idx:].strip()

# Main function to run the multi-agent review
def review_contract_with_agents(contract_text, policy_text, verbose=True):
    """Run a complete multi-agent contract review with detailed intermediate outputs
    
    Args:
        contract_text: The contract text to analyze
        policy_text: The policy text to compare against
        verbose: Whether to display detailed outputs for each step
    """
    from pprint import pprint
    import json
    
    # Step 1: Extract clauses directly with extractor agent
    print("Step 1: Extracting key clauses...")
    extraction_result = extractor_agent.run_sync(
        f"Extract the key clauses from this NDA contract:\n\n{contract_text}"
    )
    extracted_clauses = extraction_result.output
    
    if verbose:
        print("\n----- EXTRACTED CLAUSES -----")
        for i, clause in enumerate(extracted_clauses, 1):
            print(f"\n{i}. {clause.clause_name} (Section {clause.section_reference})")
            print(f"   Importance: {clause.importance}/10")
            print(f"   Text: {clause.clause_text[:150]}..." if len(clause.clause_text) > 150 else f"   Text: {clause.clause_text}")
        print("\n" + "-" * 50)
    
    # Step 2: Analyze policy compliance
    print("\nStep 2: Analyzing policy compliance...")
    clauses_text = "\n\n".join([
        f"Clause: {c.clause_name}\nReference: {c.section_reference}\nText: {c.clause_text}"
        for c in extracted_clauses
    ])
    
    policy_result = policy_agent.run_sync(
        f"""Analyze these contract clauses against our company policy:

Contract Clauses:
{clauses_text}

Company NDA Policy:
{policy_text}"""
    )
    policy_matches = policy_result.output
    
    if verbose:
        print("\n----- POLICY COMPLIANCE ANALYSIS -----")
        for i, match in enumerate(policy_matches, 1):
            compliance = "✅ Compliant" if match.compliant else "❌ Non-compliant"
            print(f"\n{i}. {match.clause_name} - {compliance}")
            print(f"   Alignment: {match.policy_alignment}/100")
            print(f"   Policy Reference: {match.policy_reference}")
            if match.issues:
                print(f"   Issues:")
                for issue in match.issues:
                    print(f"     • {issue}")
        print("\n" + "-" * 50)
    
    # Step 3: Generate suggestions for non-compliant clauses
    print("\nStep 3: Generating improvement suggestions...")
    # Identify non-compliant clauses
    non_compliant = [m for m in policy_matches if not m.compliant]
    
    clause_suggestions = []
    if non_compliant:
        # Prepare the input for the suggestion agent
        non_compliant_details = []
        for match in non_compliant:
            # Find the original clause text
            original = next(
                (c for c in extracted_clauses if c.clause_name == match.clause_name), 
                None
            )
            
            if original:
                policy_section = find_policy_section(policy_text, match.policy_reference)
                
                non_compliant_details.append(
                    f"Clause: {match.clause_name}\n"
                    f"Section: {original.section_reference}\n"
                    f"Original Text: {original.clause_text}\n"
                    f"Issues: {', '.join(match.issues)}\n"
                    f"Policy Section: {policy_section}"
                )
        
        if non_compliant_details:
            separator = "=" * 50
            formatted_details = "\n".join([f"{separator}\n{detail}\n{separator}" for detail in non_compliant_details])
            
            suggestion_prompt = f"""Generate suggested improvements for these non-compliant clauses:

{formatted_details}

For each clause, suggest revised text that would make it compliant with our policy."""
            
            suggestion_result = suggestion_agent.run_sync(suggestion_prompt)
            clause_suggestions = suggestion_result.output
    
    if verbose and clause_suggestions:
        print("\n----- SUGGESTED IMPROVEMENTS -----")
        for i, suggestion in enumerate(clause_suggestions, 1):
            print(f"\n{i}. {suggestion.clause_name}")
            print(f"   Importance: {suggestion.importance}/10")
            print(f"   Explanation: {suggestion.explanation}")
            print(f"   Suggested Text:")
            print(f"   ```\n   {suggestion.suggested_text}\n   ```")
        print("\n" + "-" * 50)
    elif verbose:
        print("\nNo suggestions needed - all clauses comply with policy")
    
    # Step 4: Create final review
    print("\nStep 4: Generating final report...")
    
    # Prepare data for final review
    final_review_data = {
        "extracted_clauses": [c.model_dump() for c in extracted_clauses],
        "policy_matches": [m.model_dump() for m in policy_matches],
        "suggestions": [s.model_dump() for s in clause_suggestions]
    }
    
    if verbose:
        print("\n----- ANALYSIS SUMMARY -----")
        print(f"• Clauses extracted: {len(extracted_clauses)}")
        print(f"• Non-compliant clauses: {len(non_compliant)}")
        print(f"• Suggestions provided: {len(clause_suggestions)}")
        print("-" * 50)
    
    review_prompt = f"""Create a comprehensive review of this NDA contract based on the analysis performed.

Here is the summary of analysis performed:
```json
{json.dumps(final_review_data, indent=2)}
```

Please provide:
1. An overall compliance score (0-100)
2. Key strengths of the contract
3. Key issues that need addressing
4. Specific recommendations for improvement
"""
    
    result = orchestrator.run_sync(review_prompt)
    
    return {
        "final_report": result.output,
        "extracted_clauses": extracted_clauses,
        "policy_matches": policy_matches,
        "clause_suggestions": clause_suggestions
    }

def format_multi_agent_results(review_results):
    """Format multi-agent review results as markdown for display"""
    final_report = review_results["final_report"]
    extracted_clauses = review_results["extracted_clauses"]
    policy_matches = review_results["policy_matches"]
    clause_suggestions = review_results["clause_suggestions"]
    
    # Prepare markdown sections
    final_report_md = f"""## Contract Review Summary

**Overall Compliance Score: {final_report.overall_score}/100**

### Key Strengths
{chr(10).join([f"- {strength}" for strength in final_report.key_strengths])}

### Key Issues
{chr(10).join([f"- {issue}" for issue in final_report.key_issues])}

### Recommendations
{chr(10).join([f"- {rec}" for rec in final_report.recommendations])}
"""
    
    # Format key metrics for display
    metrics_md = f"""## Review Process Metrics

| Metric | Value |
|--------|-------|
| Clauses Extracted | {len(extracted_clauses)} |
| Non-Compliant Clauses | {len([m for m in policy_matches if not m.compliant])} |
| Suggestions Made | {len(clause_suggestions)} |
"""
    
    # Sample suggestion if available
    suggestions_md = ""
    if clause_suggestions and len(clause_suggestions) > 0:
        suggestion = clause_suggestions[0]
        suggestions_md = f"""## Sample Suggestion

**Clause:** {suggestion.clause_name}

**Suggested Revision:**
```
{suggestion.suggested_text}
```

**Explanation:** {suggestion.explanation}
**Importance:** {suggestion.importance}/10
"""
    
    # Combine all sections
    full_markdown = f"""# Multi-Agent Contract Review

{final_report_md}

{metrics_md}

{suggestions_md}

---
*Review performed using a multi-agent system with specialized legal AI roles*
"""
    
    return Markdown(full_markdown)