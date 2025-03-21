from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.config import cfg
from consultant_info_generator.model.category import Category, Categories
from consultant_info_generator.service.prompt_factory import prompt_factory

from consultant_info_generator.logger import logger


def prompt_factory_dimension_option_deduplication() -> PromptTemplate:
    """Create a prompt template to deduplicate the list of values for a category"""
    return prompt_factory("dimension_option_deduplication")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to deduplicate the list of values for a category"""
    model = cfg.selected_llm.with_structured_output(Category)
    prompt = prompt_factory_dimension_option_deduplication()
    return prompt | model


async def deduplicate_dimension_option(category: Category) -> Category:
    """Deduplicate the list of values for a category"""
    chain = _chain_factory()
    return await chain.ainvoke({
        "category_name": category.name, 
        "category_description": category.description,
        "category_list_of_values": "\n-".join(category.list_of_values)})


async def deduplicate_categories(categories: Categories) -> Categories:
    """Deduplicate the list of values for a category"""
    deduplicated_categories = Categories(categories=[])
    for category in categories.categories:
        deduplicated_category = await deduplicate_dimension_option(category)
        deduplicated_categories.categories.append(deduplicated_category)
    logger.info(f"Extracted and deduplicated{len(deduplicated_categories.categories)} categories")
    return deduplicated_categories

