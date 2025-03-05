from consultant_info_generator.model.category import Category
from pydantic import BaseModel, Field


class Question(BaseModel):
    category: str = Field(description="The category of the question")
    question: str = Field(description="The question")


class Questions(BaseModel):
    questions: list[Question] = Field(description="The questions")


class CategoryQuestion(Category):
    question: str = Field(description="The question")


class CategoryQuestions(BaseModel):
    category_questions: list[CategoryQuestion] = Field(
        description="The category questions"
    )
