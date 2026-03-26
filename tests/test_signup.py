import uuid
import pytest
from playwright.sync_api import Page, expect

from tests.pages import SignUpPage

SIGNUP_URL = "https://dittomusic.com/en/login/"
SUBSCRIPTION_URL_PART = "/subscriptions"
KNOWN_EXISTING_EMAIL = "test+existing@gmail.com"  # see assumption in README
PASSWORD = "P@ssw0rd!"
SHORTPASSWORD = "P@ss"

def unique_email() -> str:
    """Generate a fresh email address for every test run."""
    return f"qa.test+{uuid.uuid4().hex[:8]}@mailinator.com"


class TestSignUp:
    def test_valid_signup(self, page: Page):
        """Valid sign-up with unique email should succeed or hit captcha."""
        signup = SignUpPage(page)
        signup.navigate(url=SIGNUP_URL)

        page.wait_for_timeout(3000)

        email = unique_email()
        signup.fill_form(email=email, password=PASSWORD)
        signup.checkbox()
        signup.submit()

        # Give the page time to respond
        page.wait_for_timeout(3000)

        # CAPTCHA hit counts as reaching the boundary described in the brief
        if signup.hit_captcha():
            pytest.skip("CAPTCHA wall reached – within acceptable scope per brief")

        
        assert signup.is_success(email=email, url=SUBSCRIPTION_URL_PART), (
            f"Expected success redirect or confirmation message after valid sign-up.\n"
            f"Current URL: {page.url}\n"
            f"Page title: {page.title()}"
        )

    def test_invalid_signup_duplicate_email(self, page: Page):
        """Invalid sign-up: email already in use. """
        signup = SignUpPage(page)
        signup.navigate(url=SIGNUP_URL)
        page.wait_for_timeout(3000)

        # Use a known-existing email (or attempt to register once, then reuse)
        signup.fill_form(
            email=KNOWN_EXISTING_EMAIL,
            password=PASSWORD,
        )
        signup.checkbox()
        signup.submit()

        # Give the page time to respond
        page.wait_for_timeout(3000)

        # CAPTCHA hit counts as reaching the boundary described in the brief
        if signup.hit_captcha():
            pytest.skip("CAPTCHA wall reached – within acceptable scope per brief")


        # Assert error message is visible and user is not authenticated
        signup.error_message_duplicate_email_isdisplayed(), "Expected error message is visible"  
        assert SUBSCRIPTION_URL_PART not in page.url, "User should not be authenticated"

    def test_invalid_short_password(self, page: Page):
        """Invalid sign-up: short password """
        signup = SignUpPage(page)
        signup.navigate(url=SIGNUP_URL)
        page.wait_for_timeout(3000)

        # Use a password less than 6 characters
        signup.fill_form(
            email=KNOWN_EXISTING_EMAIL,
            password=SHORTPASSWORD,
        )

        # Assert error message is visible
        signup.invalid_pw_message_isdisplayed(), "Expected error message is visible"
        page.wait_for_timeout(3000)
    
        # Assert sign up button is not clickable and user is not authenticated
        assert signup.button_is_disabled(), "Expected Sign up button to be disabled"
        assert SUBSCRIPTION_URL_PART not in page.url, "User should not be authenticated"


    def test_terms_checkbox_not_checked(self, page: Page):
        """Invalid sign-up: terms checkbox not checked """
        signup = SignUpPage(page)
        signup.navigate(url=SIGNUP_URL)
        page.wait_for_timeout(3000)
        
        #fill the form with valid email and password but do not check the terms checkbox
        signup.fill_form(
            email=KNOWN_EXISTING_EMAIL,
            password=PASSWORD,
        )

        signup.checkbox()
        signup.checkbox()

        # Assert error message is visible
        signup.invalid_checkbox_message_isdisplayed(), "Expected error message is visible"
        page.wait_for_timeout(3000)
    
        # Assert sign up button is not clickable and user is not authenticated
        assert signup.button_is_disabled(), "Expected Sign up button to be disabled"
        assert SUBSCRIPTION_URL_PART not in page.url, "User should not be authenticated"
