# tests/test_e2e.py
import pytest
import sqlite3
import os
from playwright.sync_api import sync_playwright, Page

URL = "http://127.0.0.1:5000"
DB = "library.db"

def clean():
    if os.path.exists(DB):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM books;")
        cur.execute("DELETE FROM borrow_records;")
        cur.execute("DELETE FROM sqlite_sequence;")
        conn.commit()
        conn.close()

@pytest.fixture(scope="session", autouse=True)
def browser():
    clean()
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        yield br
        br.close()

@pytest.fixture(scope="session")
def page(browser):
    context = browser.new_context()
    pg = context.new_page()
    pg.goto(f"{URL}/add_book")
    pg.fill("input[name=title]", "e2eBook")
    pg.fill("input[name=author]", "e2e")
    pg.fill("input[name=isbn]", "9781234567890")
    pg.fill("input[name=total_copies]", "5")
    pg.click("text=Add Book to Catalog")
    pg.wait_for_selector("text=has been successfully added", timeout=15000)
    yield pg
    context.close()

def test_add_book(page: Page):
    assert "5/5 Available" in page.locator("tr", has_text="e2eBook").locator("td").nth(4).inner_text()

def test_borrow_book(page: Page):
    row = page.locator("tr", has_text="e2eBook")
    row.locator("input[name=patron_id]").fill("888888")
    row.locator("button:has-text('Borrow')").click()
    page.wait_for_selector("text=Successfully borrowed", timeout=10000)
    assert "4/5 Available" in row.locator("td").nth(4).inner_text()