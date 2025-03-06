from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.config import cfg
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.model.questions import (
    Question,
    Questions,
    CategoryQuestion,
    CategoryQuestions,
)
from consultant_info_generator.model.category import Categories, Category


def prompt_questions() -> PromptTemplate:
    """Create a prompt template to generate questions based on the categories extracted from a consultant CVs"""
    return prompt_factory("questions")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract questions from a text"""
    model = cfg.selected_llm.with_structured_output(Question)
    prompt = prompt_questions()
    return prompt | model


def _prepare_questions(category: Category) -> dict[str, str]:
    """Prepare the categories for the chain"""
    return {"category": category.model_dump_json()}


async def generate_questions(categories: Categories) -> CategoryQuestions:
    """Generate questions from the categories"""
    chain = _chain_factory()
    category_questions = []
    for category in categories.categories:
        input = _prepare_questions(category)
        question: Question = await chain.ainvoke(input)
        category_questions.append(
            CategoryQuestion(
                question=question.question,
                name=category.name,
                description=category.description,
                list_of_values=category.list_of_values,
            )
        )
    return CategoryQuestions(category_questions=category_questions)
