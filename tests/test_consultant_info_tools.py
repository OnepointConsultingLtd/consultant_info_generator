from consultant_info_generator.consultant_info_tools import extract_profile, extract_consultant


def test_extract_profile():
    profile = extract_profile("alexander-polev-cto")
    assert profile is not None, "The profile cannot be retrieved."


def test_extract_consultant():
    consultant = extract_consultant("alexander-polev-cto")
    assert consultant is not None, "The consultant data cannot be retrieved and the consultant created."