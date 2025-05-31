# AI Assistant for Personal Usage

## Project Overview

This project is your personal AI assistant, designed for the **long-term accumulation and efficient utilization of personal knowledge**.

Its core purpose is to act as your "second brain" — helping you organize thoughts, notes, messages, and events, and extract valuable context for deeper analysis.

The assistant is engineered with a strong focus on:
- **Data privacy** — you stay in control of your own data.
- **Architectural flexibility** — easy to adapt as tech evolves.

Eventually, it should evolve into a comprehensive helper capable of:
- Interacting with external services and APIs.
- Executing a wide range of tasks.
- Leveraging both **local AI models** and powerful **external LLMs** for complex queries.

> ⚠️ This is an early-stage project. The API and structure may change.

---

# Development Setup

## Requirements

- Python 3.13
- Postgres 17 (Postgres 16 may work, but not officially tested)
- Git
- [`uv`](https://github.com/astral-sh/uv) package manager
- Docker (or any other compatible container engine)

---

## Installation

Before you begin, make sure all **Requirements** are installed.

```bash
# Clone the repository
git clone [YOUR_REPO_URL]
cd [YOUR_PROJECT_FOLDER_NAME]
```

---

### Setting up Postgres with pgvector

```bash
cd dev-tools
docker-compose up -d
```

Once the container is running, enable the `pgvector` extension:

```bash
docker exec -it pgvector-db psql -U oktal -d oktaldb -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Verify that the extension is installed:

```bash
docker exec -it pgvector-db psql -U oktal -d oktaldb -c "\dx"
```

Expected output:

```
                             List of installed extensions
  Name   | Version |   Schema   |                     Description
---------+---------+------------+------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vector  | 0.8.0   | public     | vector data type and ivfflat and hnsw access methods
(2 rows)
```

---

### Set up Python virtual environment

```bash
cd [YOUR_PROJECT_FOLDER_NAME]
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies from pyproject.toml
uv sync
```

---

## Next Steps

- [ ] Set environment variables (if needed)
- [ ] Run first test command
- [ ] Add first note or memory
- [ ] Connect a frontend or CLI interface (optional)

