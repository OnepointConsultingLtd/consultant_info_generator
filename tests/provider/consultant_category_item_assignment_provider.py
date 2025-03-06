from consultant_info_generator.model.category_assignments import (
    ProfileCategoryAssignment,
)
from consultant_info_generator.model.category import Category
from consultant_info_generator.model.model import Consultant
from tests.provider.consultant_provider import create_dummy_consultant
from tests.provider.category_provider import create_dummy_category


def create_profile_category_assignment() -> (
    tuple[Category, Consultant, ProfileCategoryAssignment]
):
    category = create_dummy_category()
    consultant = create_dummy_consultant()
    return (
        category,
        consultant,
        ProfileCategoryAssignment(
            category_name=category.name,
            category_element=category.list_of_values[0],
            reason="This is the industry in which the consultant works",
            profile=consultant.linkedin_profile_url,
        ),
    )
