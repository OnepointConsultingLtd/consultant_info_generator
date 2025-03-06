from consultant_info_generator.model.category_assignments import (
    ProfileCategoryAssignments,
)
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.service.category_extraction import extract_from_profiles
from consultant_info_generator.service.question_generation import generate_questions
from consultant_info_generator.service.category_assigner import (
    assign_categories_to_profiles,
)


async def prepare_consultant_chat(
    linkedin_profiles: list[str],
) -> tuple[CategoryQuestions, ProfileCategoryAssignments]:
    categories = await extract_from_profiles(linkedin_profiles)
    category_questions = await generate_questions(categories)
    profile_category_assignments = await assign_categories_to_profiles(
        linkedin_profiles, category_questions
    )
    return category_questions, profile_category_assignments
