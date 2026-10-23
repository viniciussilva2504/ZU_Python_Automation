"""Pytest options, hooks, and the managed Appium driver fixture."""

import pytest

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import InvalidSessionIdException

from zu_automation.artifacts import artifact_name, save_recording, save_screenshot
from zu_automation.config import AppConfig


def pytest_addoption(parser):
    parser.addoption(
        "--no-record-video",
        action="store_true",
        default=False,
        help="Desativa a gravação de ecrã dos testes Appium.",
    )
    parser.addoption(
        "--interactive-onboarding",
        action="store_true",
        default=False,
        help="Pausa em cada ecrã do onboarding e no ecrã final para inspeção manual.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def appium_driver(request):
    """Create one Appium session per test and close it after capturing artifacts."""
    config = AppConfig.from_environment()
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = config.device_name
    options.app_package = config.app_package
    options.app_activity = config.app_activity

    options.set_capability("appium:uiautomator2ServerInstallTimeout", 120000)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", 120000)
    options.set_capability("appium:adbExecTimeout", 120000)
    interactive = request.config.getoption("--interactive-onboarding")
    options.set_capability("appium:newCommandTimeout", 3600 if interactive else 300)

    driver = webdriver.Remote(config.appium_url, options=options)
    recording_started = False
    name = artifact_name(request.node.nodeid)
    try:
        if not request.config.getoption("--no-record-video"):
            try:
                driver.start_recording_screen(timeLimit=180, bitRate=2_000_000)
                recording_started = True
            except Exception as error:
                print(f"\n[artifacts] Não foi possível iniciar a gravação: {error}")
        yield driver
    finally:
        if recording_started:
            save_recording(driver, name, request.node)
        save_screenshot(driver, name, request.node)
        try:
            driver.quit()
        except InvalidSessionIdException:
            # Appium may have already ended the session after an external failure.
            pass
