"""Selenium UI tests: a real (headless) Chrome browser clicks through the app."""
import os
import sys
import threading

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture(scope="module")
def base_url(tmp_path_factory):
    """Start the Flask app in a background thread on a free port."""
    db_file = tmp_path_factory.mktemp("ui") / "ui_test.db"
    app = create_app({"TESTING": True, "DATABASE": str(db_file)})
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,900")
    if os.environ.get("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]
    service = None
    if os.environ.get("CHROMEDRIVER_PATH"):
        service = Service(os.environ["CHROMEDRIVER_PATH"])
    try:
        driver = webdriver.Chrome(options=options, service=service)
    except WebDriverException as error:
        # On GitHub Actions (CI=true) a missing browser must fail the build.
        if os.environ.get("CI"):
            raise
        pytest.skip(f"Chrome/ChromeDriver not available: {error.msg[:80]}")
    driver.implicitly_wait(3)
    yield driver
    driver.quit()


def wait_for_text(browser, text):
    """Wait until the text appears on the page."""
    WebDriverWait(browser, 10).until(lambda d: text in d.page_source)


def wait_until_gone(browser, text):
    """Wait until the text disappears from the page."""
    WebDriverWait(browser, 10).until(lambda d: text not in d.page_source)


def test_full_note_flow_in_browser(browser, base_url):
    # 1. Home page opens
    browser.get(base_url)
    assert "Notes App" in browser.title

    # 2. Add a note
    browser.find_element(By.ID, "title").send_keys("Selenium note")
    browser.find_element(By.ID, "content").send_keys("Created by Selenium")
    browser.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    wait_for_text(browser, "Selenium note")
    assert "Created:" in browser.page_source

    # 3. Edit the note
    browser.find_element(By.LINK_TEXT, "Edit").click()
    title_box = browser.find_element(By.ID, "title")
    title_box.clear()
    title_box.send_keys("Selenium note edited")
    browser.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    wait_for_text(browser, "Selenium note edited")

    # 4. Delete the note (accept the confirm popup)
    browser.find_element(By.CSS_SELECTOR, ".btn-danger").click()
    browser.switch_to.alert.accept()
    wait_until_gone(browser, "Selenium note edited")
