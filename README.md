# ZU Android UI Automation

![Demonstração dos testes Appium no Android](docs/assets/demo.gif)

Automação de interface Android para a aplicação ZU, construída com Python, Appium e pytest. Cada sessão Appium grava o ecrã do emulador em MP4; quando um teste passa, o projeto atualiza o GIF de demonstração usado neste README.

> O GIF é criado na primeira execução bem-sucedida de um teste Appium. Os vídeos MP4 e screenshots completos ficam localmente em `artifacts/` e não são adicionados ao Git.

![Screenshot do ecrã da aplicação ZU capturado pelo teste](docs/assets/app-screen.png)

## O que este projeto verifica

- `test_zu_smoke.py`: abre a aplicação ZU e confirma que ela fica em primeiro plano.
- `test_zu_home.py`: trata o aviso de atualização, percorre o onboarding com o botão **Next** e confirma que a aplicação chegou ao ecrã seguinte.

O teste de onboarding tem pausas interativas para permitir observar e fotografar cada passo. Execute-o com `-s` para o pytest aceitar a tecla Enter.

## Requisitos

- Windows com Python e um ambiente virtual do projeto.
- Node.js, Appium Server e o driver UiAutomator2 do Appium.
- Android SDK Platform Tools (`adb`) e um emulador Android iniciado.
- Aplicação ZU instalada no emulador (`pt.continente.ZU`).
- FFmpeg no `PATH` para converter a gravação em GIF. Sem FFmpeg, os vídeos MP4 continuam a ser guardados.

O emulador usado por omissão nas capabilities é `emulator-5554`.

## Preparar o ambiente Python

Na pasta do projeto, abra um terminal PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Instale o driver UiAutomator2 uma vez, caso ainda não esteja instalado:

```powershell
appium driver install uiautomator2
```

## Iniciar o emulador, Appium e os testes

1. Inicie o emulador no Android Studio e espere a tela inicial carregar.
2. Confirme a ligação pelo ADB:

   ```powershell
   adb devices
   ```

   A lista deve incluir `emulator-5554` com o estado `device`.

3. Abra um terminal PowerShell para o Appium e deixe-o aberto durante os testes:

   ```powershell
   appium --address 127.0.0.1 --port 4723
   ```

   Confirme que o Appium está a escutar na porta usada pelo teste:

   ```powershell
   Test-NetConnection 127.0.0.1 -Port 4723
   ```

   O resultado esperado é `TcpTestSucceeded : True`.

4. Num segundo terminal, com `.venv` ativo, execute os dois testes:

   ```powershell
   pytest -s -v tests/test_zu_smoke.py tests/test_zu_home.py
   ```

   O `-s` deixa o teste de onboarding receber Enter nas pausas interativas. Pressione Enter em cada pausa para avançar; depois do último passo, o teste confirma que o botão **Next** desapareceu.

Para executar apenas o teste rápido de abertura:

```powershell
pytest -v tests/test_zu_smoke.py
```

Para executar sem gravar vídeo:

```powershell
pytest -v --no-record-video tests/test_zu_smoke.py
```

## Gravações e GIF do README

O fixture `appium_driver` grava o ecrã do emulador durante cada sessão Appium e, no encerramento, guarda:

- Vídeo MP4 em `artifacts/videos/`.
- Screenshot final em `artifacts/screenshots/`.
- Screenshot selecionado em `docs/assets/app-screen.png` quando o teste passou.
- GIF compacto em `docs/assets/demo.gif` quando o teste passou e o FFmpeg está instalado.

Os MP4 e screenshots completos são locais e estão ignorados pelo Git. O GIF e o screenshot selecionados são prévias pequenas para o portfólio e podem ser versionados para aparecer no README.

Para gerar novamente o GIF a partir da gravação mais recente:

```powershell
python scripts/build_demo_gif.py
```

Para escolher uma gravação ou um trecho específico:

```powershell
python scripts/build_demo_gif.py --input artifacts/videos/NOME_DA_GRAVACAO.mp4 --start 5 --duration 12
```

O gravador de ecrã do Android limita cada sessão a três minutos. O teste de onboarding pode ser mais demorado por causa das pausas manuais; o MP4 pode terminar ao atingir esse limite.

## Estrutura

```text
.
├── tests/
│   ├── conftest.py          # Fixtures Appium, onboarding e captura de artefactos
│   ├── test_zu_smoke.py     # Verificação de abertura da aplicação
│   └── test_zu_home.py      # Percurso do onboarding
├── scripts/
│   └── build_demo_gif.py    # Conversão de MP4 para GIF com FFmpeg
├── artifacts/
│   ├── videos/              # MP4 por sessão (local, ignorado pelo Git)
│   └── screenshots/         # Captura final por sessão (local, ignorada pelo Git)
├── docs/assets/
│   ├── demo.gif             # Prévia animada apresentada acima
│   └── app-screen.png       # Screenshot de uma execução bem-sucedida
└── requirements.txt
```
