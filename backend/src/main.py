from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging

from config import get_settings
from ai.repair_chain import RepairAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', mode='w'),  # 'w' mode to clear previous logs
        logging.StreamHandler()
    ]
)

# Set logging level for specific modules
logging.getLogger('uvicorn').setLevel(logging.INFO)
logging.getLogger('fastapi').setLevel(logging.INFO)
logging.getLogger('langchain').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    model_number: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class PartSearchRequest(BaseModel):
    model_number: str

class Part(BaseModel):
    name: str
    price: float
    url: str
    affiliate_url: str

class PartSearchResponse(BaseModel):
    parts: List[Part]

# Routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info("="*50)
        logger.info(f"Received chat request: {request.message}")
        logger.info("Request details:")
        logger.info(f"Message: {request.message}")
        logger.info(f"Model number: {request.model_number}")
        logger.info(f"Session ID: {request.session_id}")
        
        # Create or use existing session
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Using session ID: {session_id}")
        
        # Initialize repair assistant
        logger.info("Initializing repair assistant...")
        assistant = RepairAssistant(session_id)
        
        # Get repair solution
        logger.info("Getting repair solution...")
        response = await assistant.get_repair_solution(
            query=request.message,
            model_number=request.model_number
        )
        logger.info("Got repair solution response")
        
        # Return response and session ID to maintain continuity
        return ChatResponse(
            response=response,
            session_id=session_id  # Return the session ID so frontend can use it for future requests
        )
    except Exception as e:
        import traceback
        error_msg = f"Error processing request: {str(e)}"
        error_trace = traceback.format_exc()
        logger.error(error_msg)
        logger.error(f"Traceback: {error_trace}")
        # Include more details in the error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "trace": error_trace.split('\n')
            }
        )

@app.post("/api/parts", response_model=PartSearchResponse)
async def search_parts(request: PartSearchRequest):
    try:
        # Initialize repair assistant with a temporary session
        assistant = RepairAssistant(str(uuid.uuid4()))
        
        # Search for parts
        parts = await assistant.find_replacement_parts(request.model_number)
        
        return PartSearchResponse(parts=parts or [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    # Test MongoDB connection at startup
    try:
        logger.info("Testing MongoDB connection...")
        from pymongo import MongoClient
        import urllib.parse
        
        # Parse the MongoDB URI
        logger.info("Parsing MongoDB URI...")
        parsed_uri = urllib.parse.urlparse(settings.MONGODB_URI)
        
        # Log parsed components (without password)
        logger.info(f"Scheme: {parsed_uri.scheme}")
        logger.info(f"Username: {parsed_uri.username}")
        logger.info(f"Hostname: {parsed_uri.hostname}")
        logger.info(f"Port: {parsed_uri.port}")
        logger.info(f"Path: {parsed_uri.path}")
        logger.info(f"Query params: {parsed_uri.query}")
        
        # Attempt connection
        logger.info("Attempting MongoDB connection...")
        client = MongoClient(settings.MONGODB_URI, 
                           serverSelectionTimeoutMS=5000,
                           connect=True)
        
        # Test the connection
        logger.info("Testing MongoDB ping...")
        client.admin.command('ping')
        logger.info("MongoDB connection test successful at startup")
        
        # Test database access
        logger.info("Testing database access...")
        db = client[settings.MONGODB_DB]
        collections = db.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
    except Exception as e:
        import traceback
        logger.error(f"MongoDB connection test failed at startup: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"MongoDB URI: {settings.MONGODB_URI}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Starting FastAPI server...")
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="debug")
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        import traceback
        logger.error(f"Server failed to start: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
