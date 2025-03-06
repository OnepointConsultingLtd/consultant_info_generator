import pytest
from consultant_info_generator.service.consultant_chat_preparation import (
    prepare_consultant_chat,
)
from tests.provider.linkedin_profiles import get_profiles


@pytest.mark.asyncio
async def test_consultant_chat_preparation():
    profiles = get_profiles()
    category_questions, profile_category_assignments = await prepare_consultant_chat(profiles)
    assert len(category_questions.category_questions) > 0
    assert len(profile_category_assignments.profile_category_assignments) > 0
