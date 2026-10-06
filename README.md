# Pipe Builder OS - Desktop App

Este projeto é uma aplicação desktop nativa desenvolvida para o setor de Oil & Gas, focada na visualização e construção de esquemas de pipes (camadas transversais). A aplicação conta com um frontend moderno e rico (React/HTML com Glassmorphism) e um backend robusto em Python.

## Tecnologias Utilizadas
* **Backend:** Python 3.10+
* **Frontend:** HTML5, Tailwind CSS, Google Fonts, Material Icons.
* **Integração Desktop:** `pywebview` (permite renderizar a interface web nativamente em uma janela desktop offline).

## Pré-requisitos
Para executar o projeto, você precisa ter o Python instalado na sua máquina (recomendado Python 3.10 ou superior).

## Como Executar Localmente

### 1. Preparar o Ambiente Virtual (Recomendado)
Acesse a pasta do projeto através do terminal (PowerShell ou CMD) e crie um ambiente virtual:

```powershell
# Cria o ambiente virtual chamado "venv"
python -m venv venv

# Ativa o ambiente virtual (Windows PowerShell)
.\venv\Scripts\Activate
```

### 2. Instalar as Dependências
Com o ambiente virtual ativado, instale as dependências listadas no `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 3. Iniciar o Aplicativo
Execute o arquivo principal para abrir a interface desktop:

```powershell
python main.py
```
*(Uma nova janela nativa será aberta com a interface do dashboard)*

## Estrutura do Projeto
* `main.py`: O backend da aplicação. Define a lógica do negócio em Python (classe `Api`), gerencia as camadas e inicia a janela nativa através do `pywebview`.
* `ui.html`: O frontend gerado com base nas diretrizes visuais premium. Ele se comunica dinamicamente com o Python via JavaScript usando o objeto `window.pywebview.api`.
* `requirements.txt`: Lista de bibliotecas Python requeridas.

## Geração do Executável (.exe)
Para distribuir o software sem que o usuário final precise instalar o Python, você pode gerar um executável `standalone` utilizando o PyInstaller.

Para isso, instale o PyInstaller:
```powershell
pip install pyinstaller
```

Gere o executável informando para embutir o arquivo HTML:
```powershell
pyinstaller --noconsole --add-data "ui.html;." main.py
```
O executável final estará disponível dentro da pasta `dist/main`.
