import pytest

from tests.provider.consultant_provider import create_dummy_consultant
from consultant_info_generator.service.persistence_service_consultants_async import (
    save_consultant,
    delete_consultant,
    save_category,
    delete_category,
    read_categories
)
from tests.provider.category_provider import create_dummy_category


@pytest.mark.asyncio
async def test_save_consultant():
    consultant = create_dummy_consultant()
    await save_consultant(consultant)
    await delete_consultant(consultant)


@pytest.mark.asyncio
async def test_save_category():
    category = create_dummy_category()
    await save_category(category)
    categories = await read_categories()
    assert len(categories) > 0
    assert category.name in [c.name for c in categories], "Could not find category in DB"
    await delete_category(category)
    categories = await read_categories()
    assert category.name not in [c.name for c in categories], "Could find category in DB"