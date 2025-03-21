from consultant_info_generator.model.category_assignments import (
    ProfileCategoryAssignments,
)
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.service.category_extraction import extract_from_profiles
from consultant_info_generator.service.question_generation import generate_questions
from consultant_info_generator.service.category_assigner import (
    assign_categories_to_profiles,
)
from consultant_info_generator.logger import logger
from consultant_info_generator.service.category_value_deduplication import deduplicate_categories


async def prepare_consultant_chat(
    linkedin_profiles: list[str],
) -> tuple[CategoryQuestions, ProfileCategoryAssignments]:
    categories = await extract_from_profiles(linkedin_profiles)
    # deduplicate
    logger.info(
        f"Deduplicating {len(categories.categories)} categories"
    )
    deduplicated_categories = await deduplicate_categories(categories)

    category_questions = await generate_questions(deduplicated_categories)
    logger.info(
        f"Generated {len(category_questions.category_questions)} category questions"
    )
    profile_category_assignments = await assign_categories_to_profiles(
        linkedin_profiles, category_questions
    )
    logger.info(
        f"Assigned {len(profile_category_assignments.profile_category_assignments)} profile category assignments"
    )
    return category_questions, profile_category_assignments
