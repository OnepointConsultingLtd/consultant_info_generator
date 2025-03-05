from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from consultant_info_generator.config import cfg


def prompt_factory(key: str) -> PromptTemplate:
    """Create a prompt template for a specific key"""
    prompt_dimensions = cfg.prompt_templates[key]
    human_message = prompt_dimensions["human_message"]
    system_message = prompt_dimensions["system_message"]
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate(prompt=PromptTemplate(template=system_message)),
            HumanMessagePromptTemplate(prompt=PromptTemplate(template=human_message)),
        ]
    )
