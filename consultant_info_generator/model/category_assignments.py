from pydantic import BaseModel, Field


class CategoryAssignment(BaseModel):
    """A category assignment"""

    category_name: str = Field(description="The name of the category")
    category_element: str = Field(description="The element of the category")
    reason: str = Field(
        description="The reason for the assignment, why the category was assigned to the consultant"
    )


class ProfileCategoryAssignment(CategoryAssignment):
    """A profile category assignment"""

    profile: str = Field(description="The profile")


class ProfileCategoryAssignments(BaseModel):
    """A list of profile category assignments"""

    profile_category_assignments: list[ProfileCategoryAssignment] = Field(
        description="A list of profile category assignments"
    )
