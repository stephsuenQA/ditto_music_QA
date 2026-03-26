from pathlib import Path
from typing import Optional
from datetime import datetime
import os
import pytest
from playwright.sync_api import sync_playwright, Page

VIDEO_DIR = Path("videos")
SCREENSHOT_DIR = Path("screenshots")
VIDEO_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        show_browser = os.getenv("HEADED", "false").lower() == "true"
        browser = p.chromium.launch(
            headless=not show_browser,
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1280, "height": 720},
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        yield context
        context.close()
        browser.close()

@pytest.fixture
def page(browser_context) -> Page:
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call":
        page: Optional[Page] = item.funcargs.get("page")
        if not page:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if rep.failed:
            #Screenshot, Trace
            screenshot_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}_FAILED.png"
            trace_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}_FAILED.zip"
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"\nScreenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"\nCould not save screenshot for {item.name}: {e}")
            try:
                browser_context = item.funcargs.get("browser_context")
                if browser_context:
                    browser_context.tracing.stop(path=str(trace_path))
                    print(f"\nTrace saved: {trace_path}")
            except Exception as e:
                print(f"\nCould not save trace: {e}")


        # Screen Recording
        try:
            video = page.video
            if video:
                saved_path = video.path()
                new_path = VIDEO_DIR / f"{item.name}_{timestamp}.webm"
                Path(saved_path).rename(new_path)
                print(f"\nVideo saved: {new_path}")
        except Exception as e:
            print(f"\nCould not rename video for {item.name}: {e}")