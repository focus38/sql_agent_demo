import config
import logging

from openai import AsyncOpenAI
from fastapi import FastAPI, Request
from agents.smol_agent import DatabaseAgent
from llm.moderator import ModeratorService
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

db_config = {
    "connection_string": config.DB_CONNECTION_STRING,
    "schema_name": config.SCHEMA_NAME,
    "excluded_table_names": config.SYSTEM_TABLE_NAMES,
    "db_metadata": config.DB_METADATA
}
ai_config = {
    "model_name": config.DEFAULT_LLM_MODEL,
    "api_key": config.AI_GATEWAY_API_KEY,
    "ai_gateway_url": config.AI_GATEWAY_URL
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

moderator_service: ModeratorService | None = None
agent: DatabaseAgent | None = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    global agent
    global moderator_service
    try:
        open_ai_client = AsyncOpenAI(base_url=config.AI_GATEWAY_URL, api_key=config.AI_GATEWAY_API_KEY)
        moderator_service = ModeratorService(config.MODERATOR_MODELS, open_ai_client)
        agent = DatabaseAgent(db_config=db_config, ai_config=ai_config)

        from controller.completion import completion_router
        application.include_router(completion_router)
        yield
    finally:
        agent.cleanup()
        del agent
        print("Resources released.")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,         
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],     
)

@app.get("/")
async def serve_index():
    return FileResponse(f"static/index.html")

@app.exception_handler(Exception)
async def uvicorn_exception_handler(request: Request, exc: Exception):
    url = getattr(request.url, 'path', 'unknown')
    method = request.method
    logger.exception(f"Error in request {method} {url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )