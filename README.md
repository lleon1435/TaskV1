# TaskV1: FastAPI with Elasticsearch Integration

## Overview
TaskV1 is a FastAPI application that provides a RESTful API interface for interacting with Elasticsearch. It supports basic operations such as creating indices, writing documents, and reading data with built-in error handling and logging.

## Features
- Elasticsearch integration with authentication
- Create new indices
- Write documents to indices
- Read documents from indices
- Comprehensive error handling
- Logging system
- Multi-worker and thread support
- Health check endpoint

## Prerequisites
- Docker
- Docker Compose
- Python 3.11+
- Elasticsearch 8.x

## Environment Variables
The application requires the following environment variables:
```
ELASTIC_USER=your_elasticsearch_username
ELASTIC_PASS=your_elasticsearch_password
ELASTIC_HOST=elasticsearch
ELASTIC_PORT=9200
```

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/lleon1435/TaskV1.git
cd TaskV1
```

2. Build and run with Docker Compose:
```bash
ELASTIC_USER=Myuser ELASTIC_PASSWORD=Mypassword docker compose up -d
```

## API Endpoints

### Health Check
```
GET /
Response: Basic health check and Elasticsearch connection status
```

### Create Index
```
POST /index/{index_name}
Response: Confirmation of index creation or existing index message
```

### Write Document
```
POST /write/{index_name}
Body: JSON document to be indexed
Response: Document ID and confirmation message
```

### Read Documents
```
GET /read/{index_name}
Query Parameters:
  - size: Number of documents to return (default: 10)
Response: Array of documents from the specified index
```

## Docker Configuration

The application uses the following Docker configuration for optimal performance:
- 4 worker processes
- 2 threads per worker
- Uvicorn worker class
- Health check enabled

```dockerfile
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--threads", "2", "--bind", "0.0.0.0:8000", "--log-level", "info", "main:app"]
```

## Error Handling
The application includes comprehensive error handling for:
- Connection issues
- Authentication failures
- Invalid requests
- Missing indices
- Document format errors

## Logging
Logging is configured to provide detailed information about:
- Application startup/shutdown
- Request processing
- Error occurrences
- Elasticsearch operations

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Authors
- Initial work - [lleon1435](https://github.com/lleon1435)
