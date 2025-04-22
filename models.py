from typing import List, Optional
from pydantic import BaseModel, Field

class Party(BaseModel):
    name: str = Field(description="Full legal name of the party")
    role: Optional[str] = Field(None, description="Role of the party in the contract (e.g., 'Seller', 'Buyer')")
    clause_reference: Optional[str] = Field(None, description="Section or clause reference where the party is mentioned")

class DateInfo(BaseModel):
    date: str = Field(description="Date in ISO format (YYYY-MM-DD) or textual description")
    clause_reference: Optional[str] = Field(None, description="Section or clause reference where the date is mentioned")

class ContractValue(BaseModel):
    amount: str = Field(description="Amount of the contract value")
    currency: Optional[str] = Field(None, description="Currency of the contract value")
    clause_reference: Optional[str] = Field(None, description="Section or clause reference where the value is mentioned")

class PersonalDataInfo(BaseModel):
    processing: str = Field(description="Whether personal data is processed (Yes/No)")
    details: Optional[str] = Field(None, description="Description of personal data processing if applicable")
    clause_reference: Optional[str] = Field(None, description="Section or clause reference where personal data is mentioned")

class ContractMetadata(BaseModel):
    """Metadata extracted from a legal contract document"""

    parties: List[Party] = Field(
        description="List of all parties involved in the contract"
    )

    notice_date: Optional[DateInfo] = Field(
        None,
        description="Date by which notice must be given"
    )

    termination_date: Optional[DateInfo] = Field(
        None,
        description="Date when the contract terminates"
    )

    contract_value: Optional[ContractValue] = Field(
        None,
        description="Monetary value of the contract"
    )

    personal_data: Optional[PersonalDataInfo] = Field(
        None,
        description="Information about personal data processing in the contract"
    )