import asyncio

from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import PromptTemplate
from consultant_info_generator.config import cfg
from consultant_info_generator.model.category import Categories
from consultant_info_generator.consultant_info_tools import extract_consultant
from consultant_info_generator.logger import logger
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.model.model import Consultant


def prompt_factory_dimensions() -> PromptTemplate:
    """Create a prompt template to extract dimensions from a text"""
    return prompt_factory("dimensions")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract dimensions from a text"""
    model = cfg.selected_llm.with_structured_output(Categories)
    prompt = prompt_factory_dimensions()
    return prompt | model


def _prepare_dimensions(cvs: list[str]) -> dict[str, str]:
    """Prepare the dimensions for the chain"""
    return {"cvs": "\n\n".join(cvs)}


async def extract_dimensions(cvs: list[str]) -> list[Categories]:
    """Extract the dimensions from the chain"""
    consultant_batch_size = cfg.consultant_batch_size
    invocations = []
    chain = _chain_factory()
    for i in range(0, len(cvs), consultant_batch_size):
        input = _prepare_dimensions(cvs[i : i + consultant_batch_size])
        invocations.append(chain.ainvoke(input))
    dimensions_list = await asyncio.gather(*invocations)
    return dimensions_list


def flatten_dimensions(dimension_list: list[Categories]) -> Categories:
    """Flatten the dimensions from the list"""
    all_dims = {}
    for dims in dimension_list:
        for dim in dims.categories:
            if dim.name not in all_dims:
                all_dims[dim.name] = dim
            else:
                merged_list_of_values = set(
                    all_dims[dim.name].list_of_values + dim.list_of_values
                )
                all_dims[dim.name].list_of_values = list(merged_list_of_values)
    return Categories(categories=list(all_dims.values()))


async def extract_from_profiles(
    linkedin_profiles: list[str],
) -> tuple[Categories, list[Consultant]]:
    consultants = []
    for profile in linkedin_profiles:
        try:
            consultant = extract_consultant(profile)
            logger.info(f"Extracted consultant from {profile}")
            consultants.append(consultant)
        except Exception as e:
            logger.error(f"Error extracting consultant from {profile}: {e}")
    categories = flatten_dimensions(
        await extract_dimensions(
            [consultant.model_dump_json() for consultant in consultants]
        )
    )
    return categories, consultants
