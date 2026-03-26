# Ditto Music QA Automation Exercise

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. Run tests:
   ```bash
   pytest -q
   ```

## Environment
- Tested locally on macOS with Python 3.9 and Playwright Chromium.        

## Assumptions
- Tests stop when a CAPTCHA appears, as per the exercise scope.
- The invalid case is “email already in use”, as this is a common real‑world failure.
- Selectors are based on the current DOM and may need updates if the UI changes.
- `KNOWN_EXISTING_EMAIL` in test_signup.py assumes an account with test+existing@gmail.com already exists in the system. Register it manually before running if needed.

## Approach & Trade-offs
- Used a simple Page Object Model for maintainability.
- Runs headless by default; set HEADED=true to watch the browser during development.
- Generate a unique email per run (via uuid) to avoid test pollution.
- For the valid sign-up, treat a visible CAPTCHA as a hard boundary (skip) and otherwise assert a clear success state (redirect + logged‑in user).
- Current run targets Chromium only; with more time I’d extend the suite to WebKit and Firefox using Playwright’s browser matrix if needed.

## What I'd Add Next
- Data-driven tests for more invalid scenarios (format, weak password, missing fields, terms not accepted).
- CI pipeline (e.g. GitHub Actions) running headless with artifacts on failure.
- API-level checks around sign-up (e.g. email verification token endpoint).
- Allure (or similar) reporting integration.
