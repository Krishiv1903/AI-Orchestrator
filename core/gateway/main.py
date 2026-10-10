from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from pathlib import Path
from core.utils.logger import setup_logger
logger = setup_logger("gateway")

load_dotenv()

app = FastAPI()
STATIC_DIR = Path(__file__).resolve().parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL")
API_KEY = os.getenv("GATEWAY_API_KEY")

class RunRequest(BaseModel):
    prompt: str

@app.get("/")   
def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/authenticate")
def authenticate(x_api_key: str | None = Header(default=None)):

    if not API_KEY or not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {"message": "Authenticated successfully"}


@app.post("/run")
def run(req: RunRequest, x_api_key: str | None = Header(default=None)):
    logger.info("Incoming request")
    
    if not API_KEY or not x_api_key or x_api_key != API_KEY:
        logger.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if not ORCHESTRATOR_URL:
        logger.error("ORCHESTRATOR_URL is not configured")
        raise HTTPException(status_code=503, detail="Orchestrator is not configured")

    try:
        logger.info("Calling orchestrator")
        response = requests.post(
            f"{ORCHESTRATOR_URL}/run",
            json={"prompt": req.prompt},
            headers={"x-api-key": x_api_key},
            timeout=120,
        )
        response.raise_for_status()
        logger.info("Received response from orchestrator")
        return response.json()

    except (requests.RequestException, ValueError) as e:
        logger.error(f"Error calling orchestrator: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Failed to reach orchestrator",
        ) from e
