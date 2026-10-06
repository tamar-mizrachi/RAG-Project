import pytest
from rag.router import choose_route


def test_empty_question_is_rejected():
    with pytest.raises(ValueError):
        choose_route("   ")
