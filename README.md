
# 🛒 Microsserviço Orders - Ateliê Digital

## 📖 Sobre o Projeto
O **Ateliê Digital** é um sistema web que funciona como um marketplace exclusivo para produtos artesanais. O objetivo da plataforma é conectar diretamente os artesãos independentes aos consumidores, oferecendo ferramentas para que os vendedores gerenciem seus negócios e os clientes encontrem produtos com facilidade e segurança.

Neste repositório encontra-se o microsserviço de **Orders (Pedidos)**. Dentro da arquitetura do sistema, ele é a API responsável por gerenciar o carrinho de compras e processar o checkout (finalização das compras), bem como gerenciar os pedidos das lojas. 

Apesar de rodar de forma independente, este microsserviço se comunica ativamente com as APIs de *Catalog* (para resgatar dados dos produtos) e *Accounts* (para validar os dados do usuário conectado), além de realizar integrações externas essenciais para o fluxo de compra.

## 🚀 Tecnologias e Recursos
Este microsserviço foi construído utilizando as seguintes tecnologias:

* **FastAPI:** Framework principal para a construção ágil da API.
* **PostgreSQL:** Banco de dados relacional para armazenar com segurança as informações de pedidos.
* **Autenticação JWT:** Validação de acesso utilizando a biblioteca `python-jose`.
* **RabbitMQ:** Mensageria utilizada em pontos importantes do fluxo para comunicação assíncrona entre os microsserviços.
* **Integrações Externas:** Comunicação com API de Frete e escuta de Webhook de pagamento.
* **Ferramentas de Suporte:**
    * **uv:** Gerenciador de pacotes e ambientes virtuais ultrarrápido.
    * **Pytest:** Para criação e execução de testes automatizados.
    * **Ruff:** Linter e formatador de código para manter o padrão de qualidade.
    * **Taskipy:** Executor de tarefas para facilitar o uso de comandos no terminal.

---

## ⚙️ Configuração do Ambiente

Para rodar este projeto, utilizaremos o **uv** para gerenciar o ambiente e as bibliotecas.

### 1. Instalação do uv
Se você ainda não tem o `uv` instalado, abra o seu terminal e execute o comando correspondente ao seu sistema operacional:

**No Linux (ou macOS):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**No Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Criando o Ambiente Virtual
Na pasta raiz do projeto, crie um ambiente virtual limpo executando:
```bash
uv venv
```

Após a criação, **ative o ambiente virtual**:
* **Linux / macOS:**
    ```bash
    source .venv/bin/activate
    ```
* **Windows:**
    ```cmd
    .venv\Scripts\activate
    ```

### 3. Instalando as Bibliotecas
Com o ambiente ativado, instale as dependências listadas nas tecnologias utilizando o `uv`. Você pode instalar todas de uma vez através do seu arquivo de dependências (como o `pyproject.toml` ou `requirements.txt`):

```bash
uv pip install -r requirements.txt
```

*Caso precise instalar as bibliotecas manualmente para testar o ambiente, o comando base seria:*
```bash
uv pip install fastapi uvicorn psycopg2-binary sqlalchemy python-jose[cryptography] pika pytest ruff taskipy
```

---

## ▶️ Como Executar a API

Como o projeto utiliza o **Taskipy**, as rotinas de execução estão simplificadas. Para iniciar o servidor local de desenvolvimento, basta rodar:

```bash
task run
```

*(Se não tiver os scripts do taskipy configurados, você pode iniciar o servidor padrão do FastAPI rodando `fastapi dev` ou `uvicorn main:app --reload`)*.
