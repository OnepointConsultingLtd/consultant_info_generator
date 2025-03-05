import pytest
from pathlib import Path

from consultant_info_generator.model.category import Categories
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.service.question_generation import generate_questions


@pytest.mark.asyncio
async def test_generate_questions():
    path = Path(__file__).parent / ".."  / "data" / "categories.json"
    path = path.resolve()
    assert path.exists(), "The categories file does not exist"
    with open(path, "r") as f:
        categories = Categories.model_validate_json(f.read())
    questions = await generate_questions(categories)
    assert len(questions.category_questions) > 0
    questions_path = path.parent / "questions.json"
    questions_path.write_text(questions.model_dump_json(), encoding="utf-8")
