from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.config import cfg
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.model.questions import (
    Questions,
    CategoryQuestion,
    CategoryQuestions,
)
from consultant_info_generator.model.category import Categories


def prompt_questions() -> PromptTemplate:
    """Create a prompt template to generate questions based on the categories extracted from a consultant CVs"""
    return prompt_factory("questions")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract questions from a text"""
    model = cfg.selected_llm.with_structured_output(Questions)
    prompt = prompt_questions()
    return prompt | model


def _prepare_questions(categories: Categories) -> dict[str, str]:
    """Prepare the categories for the chain"""
    return {"categories": categories.model_dump_json()}


def adapt_categories_to_questions(
    categories: Categories, questions: Questions
) -> CategoryQuestions:
    """Adapt the categories to the questions"""
    category_questions = []
    for question in questions.questions:
        for category in categories.dimensions:
            if question.category == category.name:
                category_questions.append(
                    CategoryQuestion(
                        name=category.name,
                        description=category.description,
                        list_of_values=category.list_of_values,
                        question=question.question,
                    )
                )
    return CategoryQuestions(category_questions=category_questions)


async def generate_questions(categories: Categories) -> CategoryQuestions:
    """Generate questions from the categories"""
    chain = _chain_factory()
    input = _prepare_questions(categories)
    questions: Questions = await chain.ainvoke(input)
    return adapt_categories_to_questions(categories, questions)
