from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_legal_metadata_extraction_prompt():
    """
    Returns a LangChain prompt template for extracting key metadata from legal documents.
    Specifically extracts: Parties, Notice Date, Termination Date, Contract Value, Personal Data
    """
    system_message = """You are a legal analysis assistant specializing in metadata extraction from contracts.
Extract the following entities from the provided contract text:

1. Parties: All parties involved in the contract (including full legal names)
2. Notice Date: The date by which notice must be given (if specified)
3. Termination Date: The date when the contract terminates
4. Contract Value: The monetary value of the contract (if specified)
5. Personal Data: Whether the contract involves processing personal data (Yes/No), and if Yes, describe what kind

For each entity:
- Extract the EXACT text from the document where possible
- Provide section/clause references where the information was found
- If an entity is not found, state "Not specified in the document"
- For dates, standardize to ISO format (YYYY-MM-DD) if possible
- For contract value, include the currency

Output the results in a structured JSON format that follows this schema:
{schema_str}

Analyze the document thoroughly to find all relevant information. If there are ambiguities, note them in your response.
"""

    human_message = """Please extract the key metadata from the following contract:

{contract_text}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", human_message),
    ])
    
    return prompt

def get_nda_analysis_prompt():
    """
    Returns a LangChain prompt template for analyzing NDA contracts against company policies.
    """
    system_message = """You are a legal analysis assistant specializing in Non-Disclosure Agreements (NDAs).
Your task is to analyze the provided NDA contract and determine if it complies with the company's NDA policy.

Follow these steps in your analysis:
1. Identify key clauses in the NDA (confidentiality obligations, term, exceptions, etc.)
2. Compare each clause against the company's NDA policy requirements
3. Flag any discrepancies or concerning provisions
4. Provide recommendations for negotiation or modification

Focus on the following key areas:
- Definition of Confidential Information
- Term of confidentiality obligations
- Permitted disclosures/exceptions
- Return/destruction of confidential information
- Governing law and jurisdiction
- Remedies for breach

Output your analysis in a structured format with clear recommendations.
"""

    human_message = """Please analyze this NDA contract against our company policy:

NDA Contract:
{contract_text}

Company NDA Policy:
{policy_text}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", human_message),
    ])
    
    return prompt