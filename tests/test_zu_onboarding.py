from appium.webdriver.common.appiumby import AppiumBy
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from zu_automation.config import AppConfig
from zu_automation.onboarding import FINAL_SCREEN_ENTER_BUTTON


@pytest.mark.portfolio
def test_zu_onboarding_reaches_final_step(zu_onboarding_final_screen, request):
    """Confirma o título e a ação de entrada no último ecrã do onboarding."""
    driver = zu_onboarding_final_screen

    assert driver.current_package == AppConfig.from_environment().app_package

    enter_button = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(FINAL_SCREEN_ENTER_BUTTON),
        "O botão 'Enter' não ficou visível no último ecrã do onboarding.",
    )
    assert enter_button.is_enabled(), "O botão 'Enter' está desativado."

    next_buttons = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "Next")
    visible_next_buttons = [
        button for button in next_buttons if button.is_displayed()
    ]
    assert not visible_next_buttons, (
        "O onboarding ainda está visível: encontrei o botão 'Next'."
    )

    if request.config.getoption("--interactive-onboarding"):
        print("\nA app está no último ecrã do onboarding. Tira o print agora.")
        input("Carrega Enter para terminar o teste e fechar a sessão Appium...")
