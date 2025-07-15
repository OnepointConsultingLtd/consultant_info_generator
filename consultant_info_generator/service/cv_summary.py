from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.config import cfg
from consultant_info_generator.model.cv_summary import CVSummary


def prompt_factory_cv_summary() -> PromptTemplate:
    """Create a prompt template to extract dimensions from a text"""
    return prompt_factory("cv_summary")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract dimensions from a text"""
    model = cfg.selected_llm.with_structured_output(CVSummary)
    prompt = prompt_factory_cv_summary()
    return prompt | model


def prepare_cv(cv: str) -> dict[str, str]:
    """Prepare the assignments for the chain"""
    return {"cv": cv}


async def extract_cv_summary(cv: str) -> CVSummary:
    """Extract a summary from a consultant CV"""
    chain = _chain_factory()
    return await chain.ainvoke(prepare_cv(cv))
