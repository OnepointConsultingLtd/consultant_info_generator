from pydantic import BaseModel, Field


class IndustryName(BaseModel):
    """A model for an industry name"""

    industry_name: str = Field(..., description="The industry name")
    reasoning: str = Field(
        ..., description="The reasoning for why the industry name was extracted"
    )
