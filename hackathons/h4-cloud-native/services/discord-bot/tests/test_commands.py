"""Tests for slash command logic and embed generation."""

import pytest

from bot.embeds.todo_embed import (
    todo_detail_embed,
    todo_list_embed,
    success_embed,
    error_embed,
    constitutional_block_embed,
)
from bot.utils.pagination import paginate


# ── Embed builders ───────────────────────────────────────────────

SAMPLE_TODO = {
    "id": "a0f37fb4-11ac-43b5-9f38-b0b5c148d440",
    "title": "Review PR for auth module",
    "description": "Check security patterns and test coverage",
    "category": "work",
    "priority": "high",
    "status": "pending",
    "deadline": "2026-02-15T14:00:00",
    "created_at": "2026-02-12T10:00:00",
    "updated_at": "2026-02-12T10:00:00",
    "constitutional_check": {"passed": True, "decision": "ALLOW", "reason": None},
}


def test_todo_detail_embed_has_title():
    embed = todo_detail_embed(SAMPLE_TODO)
    assert "a0f37fb4" in embed.title
    assert embed.color.value == 0x5865F2


def test_todo_detail_embed_has_fields():
    embed = todo_detail_embed(SAMPLE_TODO)
    field_names = [f.name for f in embed.fields]
    assert any("Title" in n for n in field_names)
    assert any("Deadline" in n for n in field_names)
    assert any("Priority" in n for n in field_names)
    assert any("Category" in n for n in field_names)


def test_todo_detail_embed_shows_description():
    embed = todo_detail_embed(SAMPLE_TODO)
    field_values = [f.value for f in embed.fields]
    assert any("Check security" in v for v in field_values)


def test_todo_detail_embed_no_description():
    todo = {**SAMPLE_TODO, "description": None}
    embed = todo_detail_embed(todo)
    field_names = [f.name for f in embed.fields]
    assert not any("Description" in n for n in field_names)


def test_todo_detail_embed_constitutional_flag():
    todo = {
        **SAMPLE_TODO,
        "status": "flagged",
        "constitutional_check": {
            "passed": False,
            "decision": "FLAG",
            "reason": "Potential academic dishonesty",
        },
    }
    embed = todo_detail_embed(todo)
    field_values = [f.value for f in embed.fields]
    assert any("academic" in v.lower() for v in field_values)


def test_todo_list_embed_empty():
    embed = todo_list_embed([])
    assert "No todos" in embed.description


def test_todo_list_embed_with_items():
    todos = [
        {"id": "abc12345-full-uuid", "title": "First task", "status": "pending", "priority": "high"},
        {"id": "def67890-full-uuid", "title": "Second task", "status": "completed", "priority": "low"},
    ]
    embed = todo_list_embed(todos, page=1, total_pages=1)
    assert "First task" in embed.description
    assert "Second task" in embed.description


def test_todo_list_embed_pagination_footer():
    todos = [
        {"id": "abc12345-full-uuid", "title": "Task", "status": "pending", "priority": "medium"},
    ]
    embed = todo_list_embed(todos, page=2, total_pages=3)
    assert "2/3" in embed.footer.text


def test_todo_list_embed_no_footer_single_page():
    todos = [
        {"id": "abc12345-full-uuid", "title": "Task", "status": "pending", "priority": "medium"},
    ]
    embed = todo_list_embed(todos, page=1, total_pages=1)
    assert embed.footer is None or embed.footer.text is None or "1/1" not in (embed.footer.text or "")


def test_success_embed():
    embed = success_embed("Todo created!")
    assert embed.color.value == 0x57F287
    assert "Todo created!" in embed.description


def test_error_embed():
    embed = error_embed("Something went wrong")
    assert embed.color.value == 0xED4245
    assert "Something went wrong" in embed.description


def test_constitutional_block_embed():
    embed = constitutional_block_embed("Academic dishonesty detected")
    assert embed.color.value == 0xFEE75C
    assert "Academic dishonesty" in embed.description
    field_values = [f.value for f in embed.fields]
    assert any("rephrasing" in v.lower() for v in field_values)


# ── Pagination ───────────────────────────────────────────────────

def test_paginate_empty():
    items, page, total = paginate([], 1)
    assert items == []
    assert page == 1
    assert total == 1


def test_paginate_single_page():
    data = list(range(3))
    items, page, total = paginate(data, 1)
    assert items == [0, 1, 2]
    assert page == 1
    assert total == 1


def test_paginate_multiple_pages():
    data = list(range(12))
    items, page, total = paginate(data, 1)
    assert len(items) == 5  # default ITEMS_PER_PAGE
    assert total == 3

    items2, page2, _ = paginate(data, 2)
    assert len(items2) == 5
    assert page2 == 2

    items3, page3, _ = paginate(data, 3)
    assert len(items3) == 2
    assert page3 == 3


def test_paginate_out_of_range_clamped():
    data = list(range(7))
    items, page, total = paginate(data, 100)
    assert page == total
    assert len(items) == 2  # last page has 2 items (7 - 5)


def test_paginate_negative_page():
    data = list(range(7))
    items, page, total = paginate(data, -1)
    assert page == 1
