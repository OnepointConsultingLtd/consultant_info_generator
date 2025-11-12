from consultant_info_generator.config import Config


def test_get_random_linkedin_credential():
    cfg = Config()
    user, password = cfg.get_random_linkedin_credential()
    assert user is not None
    assert password is not None
    assert len(user) > 0
    assert len(password) > 0
