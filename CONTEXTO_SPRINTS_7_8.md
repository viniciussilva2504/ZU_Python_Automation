# Contexto de trabalho — Sprints 7 e 8

Resumo para reutilizar noutra conversa do Codex.

## Repositórios

- Projecto final Selenium: `C:\Users\vinic\QA-Brazil_Python_Automation`
- Exercícios POM: `C:\Users\vinic\QA-Brazil_S8-POM-Tasks`
- Fork POM: `https://github.com/viniciussilva2504/QA-Brazil_S8-POM-Tasks`

## Preferências

- Responder em português de Portugal.
- Explicar o motivo das alterações.
- Executar os testes depois das alterações sempre que possível.
- Não incluir `.venv`, `__pycache__`, vídeos, artefactos ou executáveis no Git.

## Exercícios POM concluídos

Foram praticados Selenium, localizadores, preenchimento de campos, verificações de texto/atributos, Page Object Model, métodos combinados e `setup_class()`/`teardown_class()`.

Foram testados fluxos de Scooter, Bicicleta, Duração, tarifa Camping e adição de carteira de motorista.

## Projecto final: QA-Brazil_Python_Automation

Ficheiros principais:

- `main.py`: classe `TestUrbanRoutes` com oito testes;
- `pages.py`: classe `UrbanRoutesPage` com localizadores e interacções;
- `data.py`: URL do servidor e dados de teste;
- `helpers.py`: recuperação do código SMS fornecida pela escola;
- `locators.py`: localizadores antigos/documentais.

O fluxo cobre endereços, Comfort, telefone/SMS, cartão, comentário, cobertor e lenços, dois sorvetes e pedido final.

## Correcções exigidas pela avaliação

O POM deve encapsular esperas explícitas com `WebDriverWait` e `expected_conditions`, através de métodos como `_find`, `_find_present` e `_click`.

Os testes não devem usar `driver.find_element()` nem aceder directamente aos locators. Para validações devem chamar métodos POM como:

- `get_from_value()`;
- `get_to_value()`;
- `get_comfort_text()`;
- `get_comment_text()`.

## Validação conhecida

Comando:

```powershell
python -m pytest main.py -v
```

Resultado conhecido após as correcções:

```text
8 passed
```

O URL do servidor é temporário e pode ter de ser actualizado em `data.py`.

## Como continuar noutra conversa

Anexar este ficheiro e escrever, por exemplo:

> Leia o ficheiro CONTEXTO_SPRINTS_7_8.md. Quero continuar a refazer os Sprints 7 e 8 em VS Code, passo a passo, sem executar alterações sem me explicar primeiro.

