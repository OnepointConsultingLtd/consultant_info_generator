import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Industry(BaseModel):
    name: str = Field(..., description="The name of the industry")


class Company(BaseModel):
    name: str = Field(..., description="The name of the company")
    industries: Optional[list[Industry]] = Field(
        None, description="The industries of the company"
    )


class Skill(BaseModel):
    name: str = Field(..., description="The name of the skill")


class Experience(BaseModel):
    location: str = Field(..., description="The name of the location")
    title: str = Field(..., description="The job title")
    start: Optional[datetime.datetime] = Field(
        None, description="The start of the employment"
    )
    end: Optional[datetime.datetime] = Field(
        None, description="The end of the employment"
    )
    company: Company = Field(
        ..., description="The company in which the consultant worked"
    )


class Consultant(BaseModel):
    given_name: str = Field(..., description="The given name of the consultant")
    surname: str = Field(..., description="The surname of the consultant")
    email: str = Field(..., description="The email of the consultant")
    cv: str = Field(..., description="The curriculum vitae of the consultant")
    industry_name: str = Field(
        ..., description="The industry in which the consultant is working"
    )
    geo_location: str = Field(
        ..., description="The geographical location of the consultant"
    )
    linkedin_profile_url: str = Field(..., description="The linkedin profile")
    experiences: list[Experience] = Field(
        ..., description="The experiences of this user"
    )
    skills: list[Skill] = Field(..., description="The list of skills")
    photo_200: str | None = Field(default=None, description="The 200x200 photo of the consultant")
    photo_400: str | None = Field(default=None, description="The 400x400 photo of the consultant")

