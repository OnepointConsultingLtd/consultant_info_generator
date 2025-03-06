from consultant_info_generator.consultant_info_tools import extract_consultant
from consultant_info_generator.service.persistence_service_consultants_async import (
    save_consultant,
    delete_consultant_by_profile_id,
)
from consultant_info_generator.logger import logger


async def import_consultants(
    profile_ids: list[str], remove_existing: bool = False
) -> list[str]:
    """Import consultants from LinkedIn profiles"""
    imported_consultants = []
    for id in profile_ids:
        try:
            if remove_existing:
                await delete_consultant_by_profile_id(id)
            consultant = extract_consultant(id)
            await save_consultant(consultant)
            imported_consultants.append(id)
        except Exception as e:
            logger.error(f"Error importing consultant {id}: {e}")
    return imported_consultants
