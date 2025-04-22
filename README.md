# Learnings from building legal agents @ Pocketlaw

Repository for my talk at AI Engineering Stockholm Meetup (April 23, 2025).

## Overview

This project demonstrates practical techniques for building AI agents specialized in legal document analysis using LangChain and Pydantic-AI. The focus is on extracting structured metadata from contracts, analyzing them against policies, and providing actionable insights.

## Features

- 📄 **Contract Metadata Extraction**: Extract key entities like parties, dates, contract values, and personal data clauses
- 🔍 **Policy Compliance Checking**: Compare contracts against company policies to identify issues
- 🛠️ **Specialized Tools**: Calculator and date calculator tools to handle complex date calculations and conversions
- ⚙️ **Agent-based Architecture**: Implement both LangChain and Pydantic-AI agents with different capabilities

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)

### Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/ai-eng-sto-learnings-legal-agents.git
cd ai-eng-sto-learnings-legal-agents
```

2. Install dependencies using Poetry
```bash
poetry install
```

3. Create a `.env` file with your API keys
```
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

### Running the Examples

1. Activate the Poetry environment
```bash
poetry shell
```

2. Run the Jupyter notebook
```bash
jupyter notebook AI_ENG_STO_LLA.ipynb
```

## Project Structure

```
.
├── AI_ENG_STO_LLA.ipynb     # Main presentation notebook
├── data/                    # Sample contracts and policies
│   ├── sample_nda.md        # Basic NDA contract
│   ├── complex_nda.md       # Complex NDA with potential issues
│   └── nda_policy.md        # Company NDA policy document
├── prompts.py               # LangChain prompt templates
├── Dockerfile               # Docker configuration
├── .devcontainer/           # VS Code Dev Container configuration
└── images/                  # Images for the presentation
```

## Key Examples

### 1. Metadata Extraction with LangChain

Extract structured metadata from legal contracts:

```python
from prompts import get_legal_metadata_extraction_prompt
from langchain_openai import ChatOpenAI

# Define models and chain
llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = get_legal_metadata_extraction_prompt()
chain = prompt | llm

# Extract metadata
metadata = chain.invoke({
    "schema_str": ContractMetadata.model_json_schema(),
    "contract_text": sample_nda, 
    "chat_history": []
})
```

### 2. Using Pydantic-AI Agent with Tools

Create an agent with calculator and date tools:

```python
from pydantic_ai import Agent

# Create an agent with tools
legal_agent = Agent(
    model='openai:gpt-4o',
    system_prompt=system_prompt,
    output_type=ContractMetadata,
    tools=[calculator, date_calculator],
    deps_type=ContractDeps
)

# Run the agent
result = legal_agent.run_sync(sample_nda, deps=ContractDeps(effective_date="2025-04-23"))
```

## Talk Overview

My presentation covers:

1. **Who am I?** - Introduction and background
2. **Who are Pocketlaw?** - Company overview
3. **AI and Agents in the Legal Domain** - Historical timeline and current applications
4. **Learnings from working with Agents in Legal Tech** - Key insights and challenges
5. **Conclusions** - Summary and takeaways

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or feedback, please reach out on LinkedIn or check out my blog (links in the presentation).