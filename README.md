# F56 AI Business Assistant

A local-first AI engineering portfolio project built around **real business data from [Force56 Audio Software](https://www.force56audio.com)**, my commercial software business.

The goal of this repository is not to publish Force56's production database or provide a plug-and-play SaaS product. Instead, it is a **public technical showcase of modern AI application engineering patterns applied to a real-world business domain**: natural-language questions are interpreted by a local LLM, converted into validated structured requests, executed through deterministic application tools, and rendered back into human-readable answers.

The underlying production database schema and business data remain private.

## Why this project exists

A lot of AI demos stop at:

```text
prompt -> LLM -> text
```

This project explores a more production-oriented architecture:

```text
user language
    |
    v
LLM reasoning / routing
    |
    v
validated structured input
    |
    v
deterministic business tools
    |
    v
real business data
    |
    v
LLM-generated response
```

The key design principle is:

> **The LLM handles language and intent. Application code owns data access, validation, SQL, and business rules.**

The assistant currently runs against a private local copy of data originating from the real Force56 Audio Software business.

Force56 Audio Software develops and sells commercial audio software worldwide: **https://www.force56audio.com**

## Architecture

```text
CLI
 |
 v
LangGraph
 |
 +--> classify / route user intent
 |       |
 |       +--> local Qwen model through Ollama
 |
 +--> generate validated structured request
 |       |
 |       +--> Pydantic models
 |
 +--> execute deterministic business tool
 |       |
 |       +--> application-owned SQL
 |       +--> private local MySQL database
 |
 +--> render tool result through the LLM
 |
 v
Natural-language answer
```

The model never receives unrestricted database access and does not generate arbitrary SQL for execution.

## Current capabilities

The MVP can answer natural-language questions around real Force56 business operations, including areas such as:

- sales volume
- net revenue
- sales by product
- sales by country
- monthly sales trends
- product information

Example questions:

```text
How many copies have I sold all time?

How many copies did I sell in July 2026?

How much net revenue did I make in 2026?

Group sales by product.

Show monthly sales during 2026.

How many sales came from the United States?

List products.
```

Equivalent questions can also be expressed in Spanish.

## AI engineering concepts demonstrated

This repository is intended primarily as an engineering showcase.

It currently demonstrates:

- Python AI application architecture
- LangGraph orchestration
- local LLM inference with Ollama
- Qwen models
- tool calling
- intent routing
- structured LLM outputs
- Pydantic validation
- deterministic tool execution
- SQL access behind an application boundary
- separation between reasoning and business logic
- provider abstraction
- bilingual natural-language interaction
- real-world data integration
- protection against unrestricted LLM-generated SQL

The interesting part of the project is deliberately **not the SQL query itself**. It is the orchestration layer that turns an ambiguous natural-language request into a safe, typed and deterministic application operation.

## Current stack

- Python
- LangGraph
- Ollama
- Qwen
- Pydantic
- MySQL
- CLI

The current version intentionally runs completely locally. It does **not** require:

- a paid LLM API
- a hosted AI service
- a VPS
- FastAPI
- a web frontend
- RAG

Those may be introduced in later iterations when they solve an actual problem rather than simply adding infrastructure.

## Local LLM provider

The application currently uses Qwen through Ollama. Verify your local installation with:

```bash
ollama list
```

Configure the model in `.env`:

```env
OLLAMA_MODEL=qwen2.5:3b
```

The exact model can be changed without changing the business tools.

## Provider boundary

LangGraph does not communicate directly with Ollama throughout the graph. Instead, application code uses a small provider boundary:

```python
from app.llm import structured_call, text_call
```

The current implementation delegates those calls to an `OllamaProvider`.

Conceptually:

```text
LLMProvider
  |
  +-- OllamaProvider      <- current
  |
  +-- OpenAIProvider      <- possible hosted provider
  |
  +-- other providers     <- possible
```

This keeps orchestration and business logic independent from the inference provider.

A hosted model can therefore be introduced later without redesigning the graph.

## Setup

### 1. Create the Python environment

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment configuration:

```cmd
copy .env.example .env
```

### 2. Configure Ollama

Example:

```env
OLLAMA_MODEL=qwen2.5:3b
```

### 3. Configure MySQL

Example:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=your_local_database
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
```

### 4. Run

```cmd
python cli.py
```

## About the database

The application used for development connects to a private local database derived from Force56 production data. For obvious privacy and security reasons, this repository does **not** include:

- the production database
- production credentials
- database dumps
- customer data
- payment data
- the complete Force56 production schema

The business tools in this repository therefore illustrate the **application and AI architecture**, while some database mappings are specific to the private Force56 environment.

Anyone adapting the project to another business would implement the same tool boundaries against their own database schema. Conceptually:

```text
Natural-language request
        |
        v
Structured tool request
        |
        v
Business tool
        |
        +--> your database
        +--> your API
        +--> your ERP
        +--> your CRM
        +--> another deterministic system
```

This is intentional: the architecture is reusable even though the underlying business data is not public.

## Why deterministic tools instead of arbitrary text-to-SQL?

Allowing an LLM to freely generate and execute SQL would make for a shorter demo. It would also give the model unnecessary authority over the database. This project instead uses controlled business tools with validated parameters. For example:

```text
"What was my net revenue in 2026?"
                |
                v
LLM extracts intent + parameters
                |
                v
{
    metric: "net_revenue",
    date_from: "2026-01-01",
    date_to: "2026-12-31"
}
                |
                v
validated application tool
                |
                v
controlled SQL
```

This keeps the LLM at the natural-language boundary while the application remains responsible for execution.

## Project status

This is an evolving MVP and portfolio project. The current focus is intentionally backend-heavy:

```text
natural language
      ->
LLM orchestration
      ->
structured tool calls
      ->
business logic
      ->
real data
```

Possible future iterations include:

- conversational memory
- additional business tools
- MCP integration
- FastAPI service layer
- web chat interface
- hosted LLM providers
- observability and tracing
- authentication and authorization
- more sophisticated multi-step workflows

The project will continue evolving as a practical testbed for AI engineering patterns applied to a real software business.

## Related project

**Force56 Audio Software** 
(https://www.force56audio.com): Commercial audio software for Windows and macOS, developed and operated independently.

## About me

I'm a Senior Backend & AI Engineer with nearly 20 years of experience building backend systems, cloud services, commercial software products, and AI-enabled applications.

- **LinkedIn:** https://www.linkedin.com/in/alonso-varas-b39747b1/
- **GitHub:** https://github.com/avarasp
- **Force56 Audio Software:** https://www.force56audio.com

---

This project was built as a practical AI engineering project, using a real business environment rather than a synthetic demo dataset.