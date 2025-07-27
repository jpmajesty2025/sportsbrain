# SportsBrain

A comprehensive sports analytics platform with AI-powered multi-agent architecture.

## Features

- FastAPI backend with async support
- React frontend with TypeScript
- Multi-agent architecture using LangChain
- Authentication system
- Vector database (Milvus) integration
- Graph database (Neo4j) support
- Redis caching
- Docker containerization
- CI/CD pipeline

## Quick Start

### Development

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start development environment:
   ```bash
   docker-compose up -d
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

5. Run development servers:
   ```bash
   # Backend
   cd backend && uvicorn app.main:app --reload

   # Frontend
   cd frontend && npm start
   ```

### Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## Architecture

- **Backend**: FastAPI with SQLAlchemy, Redis, and database integrations
- **Frontend**: React with TypeScript, Material-UI
- **Agents**: LangChain-based multi-agent system
- **Databases**: PostgreSQL, Milvus (vector), Neo4j (graph)
- **Cache**: Redis
- **Deployment**: Docker, GitHub Actions CI/CD

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000