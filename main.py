from fastapi import FastAPI, HTTPException, status
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException, RequestError
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment variables with default values for local development
e_username = os.getenv('ELASTIC_USER')
e_password = os.getenv('ELASTIC_PASS')
es_host = os.getenv('ELASTIC_HOST', 'elasticsearch')
es_port = os.getenv('ELASTIC_PORT', '9200')

# Initialize Elasticsearch connection
try:
    es = Elasticsearch(
        [f"http://{es_host}:{es_port}"],
        basic_auth=(e_username, e_password),
        retry_on_timeout=True,
        max_retries=3
    )
    logger.info("Successfully connected to Elasticsearch")
except ConnectionError as e:
    logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
    raise

@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    try:
        if es.ping():
            return {
                "message": "FastAPI with ElasticSearch",
                "status": "Connected to Elasticsearch"
            }
        return {
            "message": "FastAPI with ElasticSearch",
            "status": "Elasticsearch connection failed"
        }
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service unavailable"
        )

@app.post("/index/{index_name}", status_code=status.HTTP_201_CREATED)
async def create_index(index_name: str):
    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
            logger.info(f"Created index: {index_name}")
            return {"message": f"Index '{index_name}' created successfully"}

        logger.info(f"Index already exists: {index_name}")
        return {
            "message": f"Index '{index_name}' already exists",
            "status": "existing"
        }
    except RequestError as e:
        logger.error(f"Failed to create index {index_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid index name or settings: {str(e)}"
        )
    except ConnectionError as e:
        logger.error(f"Connection error while creating index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service unavailable"
        )

@app.post("/write/{index_name}", status_code=status.HTTP_201_CREATED)
async def write_to_index(index_name: str, document: Dict[str, Any]):
    try:
        if not es.indices.exists(index=index_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index '{index_name}' does not exist"
            )

        result = es.index(index=index_name, document=document)
        logger.info(f"Document added to index {index_name}: {result['_id']}")
        return {
            "message": "Document added successfully",
            "document_id": result['_id']
        }
    except RequestError as e:
        logger.error(f"Failed to write document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format: {str(e)}"
        )
    except ConnectionError as e:
        logger.error(f"Connection error while writing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service unavailable"
        )

@app.get("/read/{index_name}", status_code=status.HTTP_200_OK)
async def read_from_index(index_name: str, size: int = 10):
    try:
        if not es.indices.exists(index=index_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index '{index_name}' does not exist"
            )

        res = es.search(
            index=index_name,
            body={
                "query": {"match_all": {}},
                "size": size
            }
        )
        logger.info(f"Read {len(res['hits']['hits'])} documents from {index_name}")
        return {
            "total": res['hits']['total']['value'],
            "documents": res['hits']['hits']
        }
    except RequestError as e:
        logger.error(f"Failed to read from index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query parameters: {str(e)}"
        )
    except ConnectionError as e:
        logger.error(f"Connection error while reading documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service unavailable"
        )

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up")
    # You could add additional startup checks here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down")
    if es is not None:
        es.close()