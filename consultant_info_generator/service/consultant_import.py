from consultant_info_generator.consultant_info_tools import extract_consultant
from consultant_info_generator.service.persistence_service_consultants_async import (
    save_consultant,
)
from consultant_info_generator.logger import logger


async def import_consultants(profile_ids: list[str]):
    """Import consultants from LinkedIn profiles"""
    for id in profile_ids:
        try:
            consultant = extract_consultant(id)
            await save_consultant(consultant)
        except Exception as e:
            logger.error(f"Error importing consultant {id}: {e}")
