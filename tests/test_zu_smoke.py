from selenium.webdriver.support.ui import WebDriverWait

from zu_automation.config import AppConfig


def test_zu_app_opens(appium_driver):
    """Confirma que a app ZU fica em primeiro plano no emulador."""
    app_package = AppConfig.from_environment().app_package
    package_aberto = WebDriverWait(appium_driver, 20).until(
        lambda sessao: sessao.current_package
        if sessao.current_package == app_package
        else False
    )

    assert package_aberto == app_package
