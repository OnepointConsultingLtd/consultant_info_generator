from pathlib import Path

import pytest
from consultant_info_generator.service.category_assigner import (
    assign_categories_to_profiles,
)
from tests.provider.linkedin_profiles import get_profiles
from tests.provider.category_questions_provider import get_category_questions


@pytest.mark.asyncio
async def test_assign_categories_to_profiles():
    pass
    # profiles = get_profiles()
    # category_questions = get_category_questions()
    # profile_category_assignments = await assign_categories_to_profiles(
    #     profiles[:2], category_questions
    # )
    # assert len(profile_category_assignments.profile_category_assignments) > 0

    # path = Path(__file__).parent / ".." / "data" / "profile_category_assignments.json"
    # path.write_text(
    #     profile_category_assignments.model_dump_json(indent=4), encoding="utf-8"
    # )
