import os
from pathlib import Path
from enum import StrEnum

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from consultant_info_generator.toml_support import load_toml


load_dotenv(".env")


class LLM(StrEnum):
    GEMINI = "gemini"
    OPENAI = "openai"


def create_llm(
    model: str = "gemini-2.0-flash-lite-preview-02-05",
    api_key: str = None,
    temperature: float = 0.7,
    llm_type: LLM = LLM.OPENAI,
):
    """Create a Google Gemini LLM instance"""
    match llm_type:
        case LLM.GEMINI:
            return ChatGoogleGenerativeAI(
                model=model, google_api_key=api_key, temperature=temperature
            )
        case LLM.OPENAI:
            return ChatOpenAI(
                model_name=model, openai_api_key=api_key, temperature=temperature
            )


class Config:
    linkedin_user = os.getenv("LINKEDIN_USER")
    assert linkedin_user is not None, "The LinkedIn user cannot be empty."
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    assert linkedin_password is not None, "The LinkedIn user cannot be empty."
    openai_api_key = os.getenv("OPENAI_API_KEY")
    assert openai_api_key is not None, "Please specify your API key."
    openai_api_model = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
    assert len(openai_api_model) > 0, "OpenAI model needs to be defined"
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    assert gemini_api_key is not None, "Please specify your API key."
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite-preview-02-05")
    assert len(gemini_model) > 0, "Gemini model needs to be defined"
    temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    llm = create_llm(
        model=gemini_model,
        api_key=gemini_api_key,
        temperature=temperature,
        llm_type=LLM.GEMINI,
    )
    openai_llm = create_llm(
        model=openai_api_model,
        api_key=openai_api_key,
        temperature=temperature,
        llm_type=LLM.OPENAI,
    )
    prompt_template_path = Path(os.getenv("PROMPTS", "prompts.toml"))
    assert prompt_template_path.exists(), "The prompt template file does not exist."
    prompt_templates = load_toml(prompt_template_path)
    consultant_batch_size = int(os.getenv("CONSULTANT_BATCH_SIZE", "10"))
    preferred_llm_param = os.getenv("PREFERRED_LLM", LLM.GEMINI)
    match preferred_llm_param:
        case LLM.GEMINI:
            llm = llm
            selected_llm = llm
        case LLM.OPENAI:
            llm = openai_llm
            selected_llm = openai_llm
        case _:
            raise ValueError(f"Invalid LLM: {preferred_llm_param}")
        

class DBConfig:
    db_name = os.getenv("DB_NAME")
    assert db_name is not None, "The database name cannot be empty."
    db_user = os.getenv("DB_USER")
    assert db_user is not None, "The database user cannot be empty."
    db_host = os.getenv("DB_HOST")
    assert db_host is not None, "The database host cannot be empty."
    db_port = os.getenv("DB_PORT")
    assert db_port is not None, "The database port cannot be empty."
    db_password = os.getenv("DB_PASSWORD")
    assert db_password is not None, "The database password cannot be empty."
    db_create = os.getenv("DB_CREATE")
    db_connection_string = f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"


cfg = Config()
db_cfg = DBConfig()
