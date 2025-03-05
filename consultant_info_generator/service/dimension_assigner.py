from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.config import cfg
from consultant_info_generator.model.category_assignments import (
    CategoryAssignment,
    ProfileCategoryAssignments,
    ProfileCategoryAssignment,
)
from consultant_info_generator.model.category import Category
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.consultant_info_tools import extract_consultant
from consultant_info_generator.logger import logger


def prompt_factory_dimensions_assigner() -> PromptTemplate:
    """Create a prompt template to extract dimensions from a text"""
    return prompt_factory("dimensions_assigner")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract dimensions from a text"""
    model = cfg.selected_llm.with_structured_output(CategoryAssignment)
    prompt = prompt_factory_dimensions_assigner()
    return prompt | model


def _prepare_assignments(consultant: str, category: Category) -> dict[str, str]:
    """Prepare the assignments for the chain"""
    return {
        "categories": "\n".join([f"- {v}" for v in category.list_of_values]),
        "consultant": consultant,
    }


async def assign_categories_to_profiles(
    profiles: list[str], category_questions: CategoryQuestions
) -> ProfileCategoryAssignments:
    chain = _chain_factory()
    category_assignments = []
    for profile in profiles:
        logger.info(f"Processing profile: {profile}")
        try:
            consultant = extract_consultant(profile)
            for category in category_questions.category_questions:
                input = _prepare_assignments(consultant.model_dump_json(), category)
                category_assignment: CategoryAssignment = await chain.ainvoke(input)
                
                category_assignments.append(
                    ProfileCategoryAssignment(
                        profile=profile,
                        category_name=category.name,
                        category_element=category_assignment.category_element,
                        reason=category_assignment.reason,
                    )
                )
        except Exception as e:
            logger.error(f"Error assigning category to profile {profile}: {e}")
    return ProfileCategoryAssignments(profile_category_assignments=category_assignments)
