"""Helpers and fixture for navigating the ZU onboarding flow."""

import pytest

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from zu_automation.config import AppConfig


NEXT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Next")
RESTART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Restart app")
FINAL_SCREEN_ENTER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Enter")


@pytest.fixture
def zu_onboarding_final_screen(appium_driver, request):
    """Open the app and advance onboarding to its final welcome screen."""
    driver = appium_driver
    app_package = AppConfig.from_environment().app_package

    package_open = WebDriverWait(driver, 20).until(
        lambda session: session.current_package
        if session.current_package == app_package
        else False
    )
    assert package_open == app_package

    for _ in range(3):
        step_type, button = WebDriverWait(driver, 60).until(
            lambda session: _find_next_step(session)
        )
        if step_type == "next":
            break
        button.click()
    else:
        raise AssertionError("A app continuou a pedir reinício após 3 tentativas.")

    clicks = 0
    click_limit = 10
    while clicks < click_limit:
        try:
            next_button = WebDriverWait(driver, 15).until(
                lambda session: _find_button(session, NEXT_BUTTON)
            )
        except TimeoutException:
            if clicks == 0:
                raise AssertionError("Não encontrei o botão de onboarding 'Next'.")
            break

        next_button.click()
        clicks += 1
        if request.config.getoption("--interactive-onboarding"):
            print(
                f"\nOnboarding: clique {clicks}. "
                "A app ficará neste ecrã até carregares Enter. "
                "Tira o print agora, se precisares."
            )
            input("Carrega Enter para avançar para o próximo passo do onboarding...")

    assert clicks < click_limit, (
        f"O onboarding ainda tinha 'Next' após {click_limit} cliques."
    )
    return driver


def _find_button(driver, locator):
    for element in driver.find_elements(*locator):
        try:
            if element.is_displayed() and element.is_enabled():
                return element
        except StaleElementReferenceException:
            continue
    return False


def _find_next_step(driver):
    next_button = _find_button(driver, NEXT_BUTTON)
    if next_button:
        return "next", next_button

    restart_button = _find_button(driver, RESTART_BUTTON)
    if restart_button:
        return "restart", restart_button

    return False
