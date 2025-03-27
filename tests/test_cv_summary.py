import pytest
from tests.provider.consultant_provider import create_dummy_consultant
from consultant_info_generator.service.cv_summary import extract_cv_summary

@pytest.mark.asyncio
async def test_generate_summary():
    consultant = create_dummy_consultant()
    cv = str(consultant)
    summary = await extract_cv_summary(cv)
    assert summary.summary is not None
    assert len(summary.summary) > 0
