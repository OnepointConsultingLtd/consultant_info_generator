from pydantic import BaseModel, Field


class CVSummary(BaseModel):
    """A summary of a consultant CV"""
    consultant_name: str = Field(..., description="The name of the consultant")
    summary: str = Field(..., description="The summary of the CV of about 100 words")
