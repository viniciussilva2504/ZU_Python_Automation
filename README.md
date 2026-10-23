# Automação Android da app ZU

Projeto de automação de interface Android com **Python, Appium e pytest**. A suíte valida a abertura da aplicação e percorre o onboarding até ao ecrã seguinte, guardando vídeo e screenshot de cada sessão para apoiar a análise de falhas.

![Pré-visualização da execução do teste de onboarding](docs/assets/onboarding-final.gif)

## Porquê este projeto

O objetivo é demonstrar um fluxo de QA mobile de ponta a ponta: configurar uma sessão Appium, sincronizar com o estado real da interface, validar um percurso crítico e preservar evidências que tornam o resultado mais fácil de rever. O projeto também explora como apresentar essas evidências de forma leve e reproduzível num portfólio.

## O que está coberto

| Teste | Verificação |
| --- | --- |
| `test_zu_app_opens` | A aplicação ZU fica em primeiro plano no emulador. |
| `test_zu_onboarding_leads_to_home` | O onboarding é percorrido e o botão **Next** deixa de estar visível no ecrã seguinte. |

O onboarding corre sem pausas por omissão. Para uma demonstração assistida, pode ativar-se o modo interativo, que aguarda Enter em cada etapa e no ecrã final. A execução automatizada permite integrar o fluxo num CI que tenha emulador, Appium e a app configurados.

## Evidências

As demonstrações abaixo foram geradas a partir de gravações das sessões Appium:

| Arranque da aplicação | Onboarding | Ecrã final do onboarding |
| --- | --- | --- |
| ![Teste de arranque](docs/assets/smoke-test.gif) | ![Teste de onboarding](docs/assets/home-test.gif) | ![Etapas finais do onboarding](docs/assets/onboarding-final.gif) |

## Requisitos

- Windows, Python e PowerShell.
- Node.js, Appium Server e o driver UiAutomator2.
- Android SDK Platform Tools (`adb`) e um emulador Android em execução.
- App ZU instalada no emulador, com o pacote `pt.continente.ZU`.
- FFmpeg no `PATH` para gerar o GIF de demonstração; a gravação MP4 funciona sem FFmpeg.

As capacidades usam por omissão o dispositivo `emulator-5554` e o servidor Appium em `http://127.0.0.1:4723`. Estes valores podem ser alterados com as variáveis `ZU_DEVICE_NAME`, `ZU_APP_PACKAGE`, `ZU_APP_ACTIVITY` e `ZU_APPIUM_URL`.

## Preparação e execução

No diretório do projeto, crie e ative o ambiente virtual e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Instale o driver UiAutomator2 (uma vez, se ainda não estiver instalado):

```powershell
appium driver install uiautomator2
```

Inicie o emulador e confirme que o ADB o reconhece:

```powershell
adb devices
```

Inicie o Appium numa janela PowerShell e deixe-o ativo:

```powershell
appium --address 127.0.0.1 --port 4723
```

Execute os testes numa segunda janela. Por omissão, o onboarding avança sem intervenção:

```powershell
pytest -v
```

Para pausar em cada etapa e inspecionar os ecrãs, ative o modo interativo. O `-s` deixa o pytest encaminhar os prompts de Enter para o terminal:

```powershell
pytest -s -v --interactive-onboarding
```

Exemplo de configuração alternativa no PowerShell:

```powershell
$env:ZU_DEVICE_NAME = "emulator-5556"
$env:ZU_APPIUM_URL = "http://127.0.0.1:4725"
pytest -v
```

Para executar apenas o teste de arranque:

```powershell
pytest -v tests/test_zu_smoke.py
```

Para omitir a gravação de vídeo:

```powershell
pytest -v --no-record-video tests/test_zu_smoke.py
```

## Artefactos

O fixture `appium_driver` inicia uma sessão por teste e tenta guardar:

- Vídeo MP4 em `artifacts/videos/` (limite de gravação do Android: 3 minutos por sessão).
- Screenshot da sessão em `artifacts/screenshots/`, incluindo sessões que falham.
- Quando o teste passa, screenshot de portfólio em `docs/assets/app-screen.png` e GIF em `docs/assets/demo.gif`, se o FFmpeg estiver disponível.

Os MP4 e screenshots individuais são locais e estão excluídos do Git. Os previews em `docs/assets/` são versionados para aparecerem no README. Para reconstruir o GIF a partir da gravação mais recente:

```powershell
python scripts/build_demo_gif.py
```

Também é possível escolher a gravação e o segmento:

```powershell
python scripts/build_demo_gif.py --input artifacts/videos/RECORDING_NAME.mp4 --start 5 --duration 12
```

## Estrutura

```text
.
├── tests/
│   ├── conftest.py          # Sessão Appium, navegação de onboarding e evidências
│   ├── test_zu_smoke.py     # Verificação de abertura da app
│   └── test_zu_home.py      # Percurso de onboarding
├── scripts/
│   └── build_demo_gif.py    # Conversão de MP4 para GIF com FFmpeg
├── docs/assets/             # GIFs e screenshot selecionado para o portfólio
├── artifacts/               # Evidências locais, ignoradas pelo Git
└── requirements.txt         # Dependências Python fixadas
```

## Próximos passos

- Validar conteúdo estável do ecrã final e guardar a hierarquia da interface para diagnóstico de falhas.
- Documentar uma matriz de dispositivos e versões Android suportadas.
