from src.sieve.models.ask import Citation
from src.sieve.services.google import SearchResult
from src.sieve.services.history import HistoryStore


def make_citation(index: int) -> Citation:
    return Citation(title=f"Citation {index}", url=f"https://example.com/{index}", snippet=f"Snippet {index}", index=index)


def make_result(index: int) -> SearchResult:
    return SearchResult(title=f"Result {index}", url=f"https://search.example/{index}", snippet=f"Result snippet {index}", index=index)


def test_add_entry_prepends_and_truncates():
    store = HistoryStore(max_size=2)

    first_entry = store.add_entry(
        query="first",
        top_n=1,
        model="gpt",
        answer_markdown="**answer**",
        message=None,
        citations=[make_citation(1)],
        results=[make_result(1)],
        search_used=True,
    )

    second_entry = store.add_entry(
        query="second",
        top_n=2,
        model="gpt",
        answer_markdown="**second answer**",
        message="note",
        citations=[make_citation(2)],
        results=[make_result(2), make_result(3)],
        search_used=False,
    )

    third_entry = store.add_entry(
        query="third",
        top_n=3,
        model="gpt",
        answer_markdown="**third**",
        message=None,
        citations=[],
        results=[],
        search_used=True,
    )

    listed = store.list_entries().items

    assert listed[0].id == third_entry.id
    assert listed[1].id == second_entry.id
    assert len(listed) == 2
    assert listed[1].results[0].title == "Result 2"
    assert listed[1].citations[0].title == "Citation 2"
    assert first_entry.id not in {entry.id for entry in listed}


def test_delete_removes_entry_and_returns_flag():
    store = HistoryStore()
    entry = store.add_entry(
        query="keep",
        top_n=1,
        model="gpt",
        answer_markdown="text",
        message=None,
        citations=[],
        results=[],
        search_used=True,
    )

    assert store.delete(entry.id) is True
    assert store.list_entries().items == []
    assert store.delete(entry.id) is False


def test_clear_empties_store():
    store = HistoryStore()
    store.add_entry(
        query="clean",
        top_n=1,
        model="gpt",
        answer_markdown="text",
        message=None,
        citations=[],
        results=[],
        search_used=False,
    )

    store.clear()

    assert store.list_entries().items == []
