import pytest
from tests.provider.category_provider import create_dummy_category
from consultant_info_generator.service.category_value_deduplication import deduplicate_dimension_option


@pytest.mark.asyncio
async def test_deduplicate_dimension_option():
    category = create_dummy_category()
    deduplicated_category = await deduplicate_dimension_option(category)
    assert len(deduplicated_category.list_of_values) < len(category.list_of_values)
