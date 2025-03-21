from pydantic import BaseModel, Field


class Category(BaseModel):
    name: str = Field(description="The name of the dimension or category")
    description: str = Field(description="The description of the dimension or category")
    list_of_values: list[str] = Field(description="The list of values for the dimension or category")


class Categories(BaseModel):
    categories: list[Category] = Field(
        description="The categories associated to the consultant"
    )
