import pytest
import json
from pathlib import Path

from consultant_info_generator.model.category import Categories
from consultant_info_generator.service.category_extraction import (
    extract_dimensions,
    extract_from_profiles,
)


@pytest.mark.asyncio
async def test_extract_dimensions():
    test_cv = {
        "given_name": "John",
        "surname": "Doe",
        "cv": "Experienced software engineer with expertise in Python and cloud technologies",
        "experiences": [
            {
                "title": "Senior Software Engineer",
                "company": {"name": "Tech Corp"},
                "start": "2020-01-01",
                "end": "2023-01-01",
            }
        ],
    }

    result = await extract_dimensions([json.dumps(test_cv)])
    assert len(result) == 1
    assert result[0] is not None


@pytest.mark.asyncio
async def test_extract_from_profiles():
    test_profiles = [
        "gil-palma-fernandes",
        "allanschweitz",
        "suresh-sharma-60336159",
        "sangeethaviswanathan",
        "miguelvale",
        "ablessy",
        "alexander-polev-cto",
        "jakeraeburn",
        "rita-rajabally-96135629",
        "elza-braeken-330ba31a6",
        "shashinbshah",
        "murtaza-hassani",
        "maithilishetty",
        "louisa-ekanem",  #
        "darren-miller-1035743",
    ]
    categories = await extract_from_profiles(test_profiles)
    assert isinstance(categories, Categories)
    categories_path = Path(__file__).parent / ".." / "data" / "categories.json"
    with open(categories_path, "w") as f:
        json.dump(categories.model_dump(), f)
    assert len(categories.categories) > 0
