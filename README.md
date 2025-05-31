# AI Assistant for personal usage

## Project Overview

This project is your personal AI assistant, designed for the **long-term accumulation and efficient utilization of personal knowledge**. Its core purpose is to act as your "second brain," helping you organize thoughts, notes, messages, and events, and extract valuable context for deeper analysis. The assistant is engineered with a strong focus on **data privacy** and **architectural flexibility**, ensuring you maintain full control over your information and can adapt the system to future technological advancements. Ultimately, it aims to evolve into a comprehensive helper capable of interacting with various services and executing a wide range of tasks, leveraging both local AI models and powerful external LLMs for the most complex queries.

---

# Development Setup

## Requirements
- Postgres 17 (maybe 16 will work also)
- python 3.13
- Git
- uv package manager
- Docker or any other compatible engine

## Installation
Before you begin, please ensure you have all the **Requirements** installed.

```bash
# Clone the repository
git clone [YOUR_REPO_URL]
cd [YOUR_PROJECT_FOLDER_NAME]
```

### Setting up DB with vector support
```bash
cd dev-tools
docker-compose up

# Add pgvector extension: 
docker exec -it pgvector-db psql -U oktal -d oktaldb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Check extension:
docker exec -it pgvector-db psql -U oktal -d oktaldb -c "\dx"
# Output should be something like:
                             List of installed extensions
  Name   | Version |   Schema   |                     Description
---------+---------+------------+------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vector  | 0.8.0   | public     | vector data type and ivfflat and hnsw access methods
(2 rows)
```

## Set up Python Virtual env
Create a virtual environment:
```bash
cd "your project dir"
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from pyproject.toml
uv sync
```