from appium.webdriver.common.appiumby import AppiumBy


def test_zu_onboarding_leads_to_home(zu_home):
    """Confirma que a app continua aberta depois de sair do onboarding."""
    driver = zu_home

    assert driver.current_package == "pt.continente.ZU"

    next_buttons = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "Next")
    visible_next_buttons = [
        button for button in next_buttons if button.is_displayed()
    ]
    assert not visible_next_buttons, (
        "O onboarding ainda está visível: encontrei o botão 'Next'."
    )

    print(
        "\nA app saiu do onboarding e está no ecrã seguinte. "
        "Tira o print agora; a sessão ficará aberta até carregares Enter."
    )
    input("Carrega Enter para terminar o teste e fechar a sessão Appium...")
