import os

from dotenv import load_dotenv

load_dotenv(".env")


class Config:
    linkedin_user = os.getenv("LINKEDIN_USER")
    assert linkedin_user is not None, "The LinkedIn user cannot be empty."
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    assert linkedin_password is not None, "The LinkedIn user cannot be empty."
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    assert gemini_api_key is not None, "Please specify your API key."
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite-preview-02-05")
    assert len(gemini_model) > 0, "Gemini model needs to be defined"


cfg = Config
