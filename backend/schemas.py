from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: str = Field(...)
    parties: str = Field(..., min_length=3)
    terms: str = Field(..., min_length=3)
    effective_date: str = Field(..., min_length=3)


class DocumentResponse(BaseModel):
    document: str