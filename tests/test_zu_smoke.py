from selenium.webdriver.support.ui import WebDriverWait


def test_zu_app_opens(appium_driver):
    """Confirma que a app ZU fica em primeiro plano no emulador."""
    package_aberto = WebDriverWait(appium_driver, 20).until(
        lambda sessao: sessao.current_package
        if sessao.current_package == "pt.continente.ZU"
        else False
    )

    assert package_aberto == "pt.continente.ZU"
