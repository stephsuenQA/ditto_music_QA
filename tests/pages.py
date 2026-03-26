from playwright.sync_api import Page, expect


class SignUpPage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Join now").first.click()
        self.page.get_by_label("Email Address").wait_for()

    def fill_form(self, email: str, password: str):
        # Email field
        self.page.get_by_label("Email Address").fill(email)

        # Password field
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_label("Password").press("Tab")


    def checkbox(self):
        # Check terms checkbox
        self.page.locator("label.custom-control-label").nth(1).click()

    def submit(self):
        self.page.locator("button:has-text('Sign up')").first.click()

    def error_message_duplicate_email_isdisplayed(self):
        error = self.page.locator(".toast-body:visible")
        expect(error).to_be_visible()
        expect(error).to_contain_text("already")

    def invalid_pw_message_isdisplayed(self):
        error = self.page.locator("div.invalid-feedback:visible")
        expect(error).to_be_visible()
        expect(error).to_contain_text("at least 6 characters long")
        
    def invalid_checkbox_message_isdisplayed(self):
        error = self.page.locator("div.invalid-feedback.d-block:visible")
        expect(error).to_be_visible()
        expect(error).to_contain_text("agree to our Terms and Conditions")
        
    def hit_captcha(self) -> bool:
        captcha_locators = [
            "iframe[src*='recaptcha']",
            "div[class*='rc-imageselect']",
            "div[aria-label*='recaptcha']",
            "text='Select all images with'",
        ]
        for selector in captcha_locators:
            if self.page.locator(selector).count() > 0:
                return True
        return False

    def is_success(self, email: str, url: str) -> bool:
        try:
            #Verify redirected to Subscription page
            in_subscriptions = url in self.page.url
            # Verify username matches registered email
            avatar = self.page.locator("span[class='avatar'] svg")
            avatar.click()
            username_el = self.page.locator("p.username.truncate-line")
            username_el.wait_for(state="visible", timeout=5000)
            username = username_el.text_content()  
            username_matches = username.strip() == email.strip()

            return in_subscriptions and username_matches
        except Exception:
            return False
        
    def button_is_disabled(self) -> bool:
        try:
            #Verify Signup button is disabled
            button_disable = self.page.locator("button:has-text('Sign up')").first
            return not button_disable.is_enabled()
        except Exception:
            return False