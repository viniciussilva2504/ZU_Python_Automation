import base64
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys

import pytest

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    InvalidSessionIdException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def pytest_addoption(parser):
    parser.addoption(
        "--no-record-video",
        action="store_true",
        default=False,
        help="Desativa a gravação de ecrã dos testes Appium.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def appium_driver(request):
    """Abre uma sessão Appium para um teste e fecha-a no fim."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    options.app_package = "pt.continente.ZU"
    options.app_activity = "pt.continente.ZU.MainActivity"

    options.set_capability("appium:uiautomator2ServerInstallTimeout", 120000)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", 120000)
    options.set_capability("appium:adbExecTimeout", 120000)
    # As pausas interativas para capturas podem durar mais do que o limite padrão do Appium.
    options.set_capability("appium:newCommandTimeout", 3600)

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    recording_started = False
    artifact_name = _artifact_name(request.node.nodeid)
    try:
        if not request.config.getoption("--no-record-video"):
            try:
                driver.start_recording_screen(
                    timeLimit=180,
                    bitRate=2_000_000,
                )
                recording_started = True
            except Exception as error:
                print(f"\n[artifacts] Não foi possível iniciar a gravação: {error}")
        yield driver
    finally:
        if recording_started:
            _save_recording(driver, artifact_name, request.node)
        _save_screenshot(driver, artifact_name, request.node)
        try:
            driver.quit()
        except InvalidSessionIdException:
            # O Appium pode já ter terminado a sessão por uma falha externa.
            pass


def _artifact_name(test_id):
    safe_test_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_id).strip("._")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{safe_test_id}_{timestamp}"


def _save_recording(driver, artifact_name, test_node):
    video_dir = ARTIFACTS_DIR / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_dir / f"{artifact_name}.mp4"

    try:
        recording = driver.stop_recording_screen()
        if not recording:
            print("\n[artifacts] O Appium não devolveu dados de vídeo.")
            return

        video_path.write_bytes(base64.b64decode(recording))
        print(f"\n[artifacts] Vídeo guardado: {video_path.relative_to(PROJECT_ROOT)}")

        report = getattr(test_node, "rep_call", None)
        if report is not None and report.passed:
            _build_readme_gif(video_path)
    except Exception as error:
        print(f"\n[artifacts] Não foi possível guardar o vídeo: {error}")


def _save_screenshot(driver, artifact_name, test_node):
    screenshot_dir = ARTIFACTS_DIR / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{artifact_name}.png"

    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_path.write_bytes(screenshot)
        print(f"\n[artifacts] Screenshot guardado: {screenshot_path.relative_to(PROJECT_ROOT)}")

        report = getattr(test_node, "rep_call", None)
        if report is not None and report.passed:
            preview_path = PROJECT_ROOT / "docs" / "assets" / "app-screen.png"
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_bytes(screenshot)
            print(f"[artifacts] Screenshot de portfólio: {preview_path.relative_to(PROJECT_ROOT)}")
    except Exception as error:
        print(f"\n[artifacts] Não foi possível guardar o screenshot: {error}")


def _build_readme_gif(video_path):
    converter = PROJECT_ROOT / "scripts" / "build_demo_gif.py"
    command = [
        sys.executable,
        str(converter),
        "--input",
        str(video_path),
        "--output",
        str(PROJECT_ROOT / "docs" / "assets" / "demo.gif"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    message = result.stdout.strip() or result.stderr.strip()
    if result.returncode == 0:
        print(f"[artifacts] {message}")
    else:
        print(f"[artifacts] GIF não gerado: {message}")


@pytest.fixture
def zu_home(appium_driver):
    """Devolve o driver com a app aberta no ecrã principal."""
    driver = appium_driver

    pacote_aberto = WebDriverWait(driver, 20).until(
        lambda sessao: sessao.current_package
        if sessao.current_package == "pt.continente.ZU"
        else False
    )
    assert pacote_aberto == "pt.continente.ZU"

    localizador_next = (AppiumBy.ACCESSIBILITY_ID, "Next")
    localizador_restart = (AppiumBy.ACCESSIBILITY_ID, "Restart app")

    # Trata o aviso de atualização, que pode voltar a aparecer ao iniciar a app.
    for _ in range(3):
        tipo, botao = WebDriverWait(driver, 60).until(
            lambda sessao: _encontrar_proximo_passo(
                sessao,
                localizador_next,
                localizador_restart
            )
        )
        if tipo == "next":
            break
        botao.click()
    else:
        raise AssertionError("A app continuou a pedir reinício após 3 tentativas.")

    cliques_next = 0
    limite_cliques = 10
    while cliques_next < limite_cliques:
        try:
            botao_next = WebDriverWait(driver, 15).until(
                lambda sessao: _encontrar_botao(sessao, localizador_next)
            )
        except TimeoutException:
            if cliques_next == 0:
                raise AssertionError("Não encontrei o botão de onboarding 'Next'.")
            break

        botao_next.click()
        cliques_next += 1
        print(
            f"\nOnboarding: clique {cliques_next}. "
            "A app ficará neste ecrã até carregares Enter. "
            "Tira o print agora, se precisares."
        )
        input("Carrega Enter para avançar para o próximo passo do onboarding...")

    assert cliques_next < limite_cliques, (
        f"O onboarding ainda tinha 'Next' após {limite_cliques} cliques."
    )
    return driver


def _encontrar_botao(driver, localizador):
    for elemento in driver.find_elements(*localizador):
        try:
            if elemento.is_displayed() and elemento.is_enabled():
                return elemento
        except StaleElementReferenceException:
            # A tela pode mudar entre localizar o botão e consultar seu estado.
            # O WebDriverWait tentará localizar um elemento novo na próxima volta.
            continue
    return False


def _encontrar_proximo_passo(driver, localizador_next, localizador_restart):
    botao_next = _encontrar_botao(driver, localizador_next)
    if botao_next:
        return "next", botao_next

    botao_restart = _encontrar_botao(driver, localizador_restart)
    if botao_restart:
        return "restart", botao_restart

    return False
