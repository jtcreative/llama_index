# Entertwine Chatbot SDK - Deployment & Installation Guide

## Installation

### Option 1: Install from PyPI (Coming Soon)
```bash
pip install entertwine-chatbot-sdk
```

### Option 2: Install from Source
```bash
git clone https://github.com/jtcreative/llama_index.git
cd llama_index
pip install -e .
```

### Option 3: Docker Deployment
```bash
docker build -f backend/Dockerfile -t entertwine-chatbot .
docker run -p 3978:3978 --env-file .env entertwine-chatbot
```

## Configuration

### Required Environment Variables

Set these before running the chatbot:

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Azure Search
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_KEY=your-key
AZURE_SEARCH_INDEX=medichat-index

# Azure OpenAI
ENDPOINT_URL=https://your-instance.openai.azure.com
DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_KEY=your-key

# Azure Translation
AZURE_TEXT_TRANSLATION_APIKEY=your-key
AZURE_TEXT_TRANSLATION_REGION=eastus

# Optional: Teams Integration
MICROSOFT_APP_ID=your-app-id
MICROSOFT_APP_PASSWORD=your-password
MICROSOFT_TENANT_ID=your-tenant-id
```

Copy `.env.example` to `.env` and fill in your configuration:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

## Running the Server

### Development Mode
```bash
python -m backend.cli start --host 0.0.0.0 --port 3978
```

Or with uvicorn directly:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 3978 --reload
```

### Production Mode
```bash
entertwine-chatbot start --workers 4
```

Or with gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

## Validate Configuration

Before deploying, validate your configuration:
```bash
python -m backend.cli validate-config
```

## Health Check

Once running, verify the server is healthy:
```bash
curl http://localhost:3978/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Entertwine Chatbot API is running"
}
```

## API Endpoints

### Query Endpoint
```bash
curl -X POST http://localhost:3978/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "query": "Where can I find health insurance?"
  }'
```

### Teams Bot Endpoint
```
POST /api/messages
```

Used by Microsoft Teams bot framework. Configure in Teams app settings.

## Docker Compose Example

Create `docker-compose.yml`:
```yaml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  chatbot:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "3978:3978"
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
    environment:
      REDIS_URL: redis://redis:6379/0

volumes:
  redis_data:
```

Run with:
```bash
docker-compose up
```

## Monitoring & Logging

The application uses Python's standard logging module. Set log level:
```bash
# Debug mode
LOGLEVEL=DEBUG python -m backend.cli start

# Production
LOGLEVEL=INFO entertwine-chatbot start
```

## Troubleshooting

### Redis Connection Error
```
ValueError: No REDIS_URL configured
```
→ Ensure `REDIS_URL` is set and Redis server is running

### Azure Configuration Error
```
ValueError: Missing required environment variables
```
→ Run `entertwine-chatbot validate-config` to check all required vars

### Model Loading Error
```
FileNotFoundError: lid.176.bin not found
```
→ Ensure language model file exists in `models/` directory

## Performance Tuning

### For High Volume
- Increase workers: `--workers 8` (1 per CPU core recommended)
- Configure Redis connection pooling in `REDIS_URL`
- Use Azure Search's optimized tiers

### For Low Latency
- Enable model caching (done automatically)
- Use local model path if possible
- Configure connection pooling

## Security Considerations

- ✅ Never commit `.env` files with credentials
- ✅ Use environment secrets in production
- ✅ Enable HTTPS/TLS for production APIs
- ✅ Implement API authentication/authorization
- ✅ Validate all user inputs (done automatically)
- ✅ Keep dependencies updated

## Next Steps

1. Install dependencies: `pip install -e .`
2. Configure `.env` file with your Azure credentials
3. Validate configuration: `entertwine-chatbot validate-config`
4. Start server: `entertwine-chatbot start`
5. Test: `curl http://localhost:3978/health`

## Support

For issues or questions:
- Check logs: Enable debug logging
- Run validation: `entertwine-chatbot validate-config`
- See GitHub Issues: https://github.com/jtcreative/llama_index/issues
