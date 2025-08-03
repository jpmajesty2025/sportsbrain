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

The project includes comprehensive automated testing:

- **Unit Tests**: Backend functionality testing with pytest
- **Integration Tests**: Full deployment verification
- **CI/CD Testing**: Automated testing on every push to master
- **Health Monitoring**: Real-time service health checks

```bash
# Run all backend tests
cd backend && pytest tests/ -v

# Run deployment verification tests  
cd backend && pytest tests/test_deployment.py -v

# Manual deployment testing (interactive)
python test_deployment_manual.py

# Frontend tests
cd frontend && npm test
```

### Health Check Endpoints

- **Basic Health**: `GET /health` - Simple service status
- **Detailed Health**: `GET /health/detailed` - Database and Redis connectivity

### CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs unit tests for backend and frontend
2. Builds and pushes Docker images to Docker Hub
3. Deploys to Railway
4. Runs deployment verification tests
5. Verifies all 4 services are healthy (backend, frontend, PostgreSQL, Redis)

## Architecture

- **Backend**: FastAPI with SQLAlchemy, Redis, and database integrations
- **Frontend**: React with TypeScript, Material-UI
- **Agents**: LangChain-based multi-agent system
- **Databases**: PostgreSQL, Milvus (vector), Neo4j (graph)
- **Cache**: Redis
- **Deployment**: Docker, GitHub Actions CI/CD

## Production Deployment

The application is deployed on Railway with the following services:
- **Backend**: FastAPI application (sportsbrain-backend)
- **Frontend**: React application (sportsbrain-frontend)
- **Database**: PostgreSQL
- **Cache**: Redis

All services are automatically tested after each deployment to ensure reliability.

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000