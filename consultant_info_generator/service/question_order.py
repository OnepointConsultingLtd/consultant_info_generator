from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

from consultant_info_generator.config import cfg
from consultant_info_generator.model.questions import QuestionOrdinals, CategoryQuestion
from consultant_info_generator.model.questions import QuestionOrdinals
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.service.persistence_service_consultants_async import (
    read_session_questions,
    save_question_ordinal,
)


def prompt_factory_sorter() -> PromptTemplate:
    """Create a prompt template to extract dimensions from a text"""
    return prompt_factory("questions_order")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract dimensions from a text"""
    model = cfg.selected_llm.with_structured_output(QuestionOrdinals)
    prompt = prompt_factory_sorter()
    return prompt | model


def _prepare_questions(questions: list[CategoryQuestion]) -> dict[str, str]:
    """Prepare the questions for the chain"""
    return {"questions": "\n\n".join([q.question for q in questions])}


async def read_questions() -> list[CategoryQuestion]:
    """Read the questions from the database"""
    return await read_session_questions()


async def _order_questions(questions: list[CategoryQuestion]) -> QuestionOrdinals:
    chain = _chain_factory()
    input = _prepare_questions(questions)
    question_ordinals: QuestionOrdinals = await chain.ainvoke(input)
    return question_ordinals


async def order_questions() -> QuestionOrdinals:
    questions = await read_questions()
    return await _order_questions(questions)


async def order_questions_and_save():
    ordinals = await order_questions()
    for ordinal in ordinals.question_ordinals:
        print(f"{ordinal.question} - {ordinal.ordinal}")
        await save_question_ordinal(ordinal)


if __name__ == "__main__":
    import asyncio

    asyncio.run(order_questions_and_save())
