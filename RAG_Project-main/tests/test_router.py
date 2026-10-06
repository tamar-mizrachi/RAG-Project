from rag.router import choose_route


def test_structured_route():
    assert choose_route("List all decisions").route == "structured"


def test_latest_route():
    assert choose_route("What is the latest RTL rule?").route == "structured"


def test_semantic_route():
    assert choose_route("How does the retrieval architecture work?").route == "semantic"
