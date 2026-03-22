# AI-Assisted Task Tracker

Small internal tool for converting messy task descriptions into structured tasks using AI.

## Quick Start

### 1. Clone and Prepare
```bash
git clone <repo_url>
cd FastAPIDemo
cp .env.example .env
```
*Note: Add your `OPENAI_API_KEY` to the `.env` file.*

### 2. Run with Docker Compose
```bash
docker-compose up --build
```

### 3. Verify
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Management**: [http://localhost:15672](http://localhost:15672) (guest/guest)
- **Redis**: `localhost:6379`
- **MongoDB**: `localhost:27017`

## Project Structure
- `app/`: FastAPI Backend implementation
  - `main.py`: Entry point
  - `api/`: REST Endpoints
  - `models/`: Pydantic models
  - `db/`: Database configuration
  - `worker/`: Celery worker and tasks
  - `core/`: Application settings
  - `services/`: AI logic
- `requirements.txt`: Python dependencies
- `.env.example`: Template for environment variables
- `docker-compose.yml`: Multi-service orchestration

## Features
1. **Sync AI Suggestion**: Immediate structured suggestion from LLM.
2. **Async AI Suggestion**: Background processing for slower LLMs using Celery.
3. **Task Storage**: Save and retrieve tasks from MongoDB.
4. **JWT Authentication**: Secure user accounts and data isolation.