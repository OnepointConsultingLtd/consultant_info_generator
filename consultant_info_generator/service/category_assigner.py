from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from consultant_info_generator.service.prompt_factory import prompt_factory
from consultant_info_generator.config import cfg
from consultant_info_generator.model.category_assignments import (
    CategoryAssignmentMatch,
    ProfileCategoryAssignments,
    ProfileCategoryAssignment,
)
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.consultant_info_tools import extract_consultant
from consultant_info_generator.logger import logger
from consultant_info_generator.model.model import Consultant


def prompt_factory_dimensions_assigner() -> PromptTemplate:
    """Create a prompt template to extract dimensions from a text"""
    return prompt_factory("dimensions_assigner")


def _chain_factory() -> RunnableSequence:
    """Create a chain of functions to extract dimensions from a text"""
    model = cfg.selected_llm.with_structured_output(CategoryAssignmentMatch)
    prompt = prompt_factory_dimensions_assigner()
    return prompt | model


def _prepare_assignments(consultant: str, category_element: str) -> dict[str, str]:
    """Prepare the assignments for the chain"""
    return {
        "category_element": category_element,
        "consultant": consultant,
    }


async def assign_categories_to_profiles(
    consultants: list[Consultant], category_questions: CategoryQuestions
) -> ProfileCategoryAssignments:
    chain = _chain_factory()
    category_assignments = []
    for consultant in consultants:
        logger.info(f"Processing profile to assign categories: {consultant}")
        try:
            consultant_json = consultant.model_dump_json()
            for category in category_questions.category_questions:
                batch_size = 10
                for i in range(0, len(category.list_of_values), batch_size):
                    category_assignment_inputs = []
                    category_elements = []
                    for category_element in category.list_of_values[i : i + batch_size]:
                        input = _prepare_assignments(consultant_json, category_element)
                        category_assignment_inputs.append(input)
                        category_elements.append(category_element)
                    batch: list[CategoryAssignmentMatch] = await chain.abatch(
                        category_assignment_inputs
                    )
                    for b, category_element in zip(batch, category_elements):
                        if b.match:
                            category_assignments.append(
                                ProfileCategoryAssignment(
                                    profile=consultant.linkedin_profile_url,
                                    category_name=category.name,
                                    category_element=category_element,
                                    reason=b.reason,
                                )
                            )
        except Exception as e:
            logger.error(
                f"Error assigning category to profile {consultant.linkedin_profile_url}: {e}"
            )
    return ProfileCategoryAssignments(profile_category_assignments=category_assignments)
