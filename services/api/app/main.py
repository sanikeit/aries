from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import time
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import engine
from app.models import models
from app.routers import auth, users, cameras, analytics, streams, websockets
from app.services import consumer_service
from app.services.detection_simulator import detection_simulator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set debug logging for our modules
logging.getLogger("app.core.dependencies").setLevel(logging.DEBUG)
logging.getLogger("app.core.security").setLevel(logging.DEBUG)
logging.getLogger("app.routers.cameras").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Aries API service...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(models.SQLModel.metadata.create_all)
    
    # Start background consumer service
    consumer_task = asyncio.create_task(consumer_service.consume_metadata())
    
    # Start detection simulator for real-time object detection
    detection_task = asyncio.create_task(detection_simulator.run_simulation())
    
    logger.info("Aries API service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aries API service...")
    
    # Stop consumer service
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    
    # Stop detection simulator
    detection_simulator.stop_simulation()
    detection_task.cancel()
    try:
        await detection_task
    except asyncio.CancelledError:
        pass
    
    logger.info("Aries API service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Aries Edge Platform API",
    description="Multi-camera intelligent video analytics platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add debug middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"=== INCOMING REQUEST ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"=== RESPONSE ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Process Time: {process_time:.3f}s")
        return response
    except Exception as e:
        logger.error(f"=== REQUEST ERROR ===")
        logger.error(f"Error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers - order matters! More specific paths first
print("DEBUG: Including auth router...")
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
print("DEBUG: Including users router...")
app.include_router(users.router, prefix="/users", tags=["users"])
print("DEBUG: Including cameras router...")
app.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
print("DEBUG: Including analytics router...")
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
print("DEBUG: Including websockets router...")
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])
# Include streams router last to avoid conflicts with camera-specific endpoints
print("DEBUG: Including streams router...")
app.include_router(streams.router, prefix="/streams", tags=["streams"])
print("DEBUG: All routers included successfully")

@app.get("/")
async def root():
    return {"message": "Aries Edge Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aries-api"}

@app.get("/test-cameras")
async def test_cameras():
    logger.info("=== TEST CAMERAS ENDPOINT CALLED ===")
    return {"message": "Test cameras endpoint working"}