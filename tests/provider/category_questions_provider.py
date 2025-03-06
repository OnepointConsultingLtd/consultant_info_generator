from pathlib import Path
from consultant_info_generator.model.questions import CategoryQuestions


def get_category_questions() -> CategoryQuestions:
    """Get the category questions from the file"""
    questions_path = Path(__file__) / ".." / ".." / ".." / "data/questions.json"
    questions_path = questions_path.resolve()
    assert questions_path.exists(), f"Questions file does not exist: {questions_path}"
    return CategoryQuestions.model_validate_json(
        questions_path.read_text(encoding="utf-8")
    )
