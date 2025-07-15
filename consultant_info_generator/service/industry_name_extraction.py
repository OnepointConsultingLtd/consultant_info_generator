from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.config import cfg
from consultant_info_generator.model.industry_name import IndustryName
from consultant_info_generator.service.cv_summary import prepare_cv


def prompt_factory_industry_name_extraction() -> PromptTemplate:
    """Create a prompt template to extract the industry name from a consultant CV"""
    return prompt_factory("industry_name_extraction")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract the industry name from a consultant CV"""
    model = cfg.selected_llm.with_structured_output(IndustryName)
    prompt = prompt_factory_industry_name_extraction()
    return prompt | model


async def extract_industry_name(cv: str) -> IndustryName:
    """Extract the industry name from a consultant CV"""
    chain = _chain_factory()
    return await chain.ainvoke(prepare_cv(cv))
