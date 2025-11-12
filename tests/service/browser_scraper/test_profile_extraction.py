from consultant_info_generator.service.browser_scraper.profile_extraction import (
    extract_consultant,
    search_consultants_by_name,
)


def test_extract_profile_full():
    profile = extract_consultant(
        "gil-palma-fernandes",
        headless=False,
        extract_educations=True,
        extract_skills=True,
    )
    assert profile is not None, "The profile cannot be retrieved."
    assert (
        profile.cv is not None and profile.cv != ""
    ), "The curriculum vitae cannot be retrieved."
    assert (
        profile.experiences is not None and len(profile.experiences) > 0
    ), "The experiences cannot be retrieved."
    assert (
        profile.educations is not None and len(profile.educations) > 0
    ), "The educations cannot be retrieved."
    assert (
        profile.skills is not None and len(profile.skills) > 0
    ), "The skills cannot be retrieved."


def test_extract_profile_mkhere():
    _basic_tester("mkhere")


def test_extract_profile_robertbaldock():
    _basic_tester("robertbaldock")


def _basic_tester(profile_id: str):
    profile = extract_consultant(profile_id, headless=False)
    assert profile is not None, "The profile cannot be retrieved."
    assert (
        profile.cv is not None and profile.cv != ""
    ), "The curriculum vitae cannot be retrieved."
    assert (
        profile.experiences is not None and len(profile.experiences) > 0
    ), "The experiences cannot be retrieved."


def test_search_consultants_by_name_alexander_polev():
    consultants = search_consultants_by_name("alexander polev", headless=False)
    assert consultants is not None, "The consultants cannot be retrieved."
    assert len(consultants) > 0, "The consultants cannot be retrieved."


def test_search_consultants_by_name_gil_palma_fernandes():
    consultants = search_consultants_by_name("gil fernandes", headless=False)
    assert consultants is not None, "The consultants cannot be retrieved."
    assert len(consultants) > 0, "The consultants cannot be retrieved."
