from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from core.utils.logger import setup_logger
logger = setup_logger("gateway")    

load_dotenv("AI_Platform\core\config\.env")

app = FastAPI()

app.mount("/static", StaticFiles(directory="core/gateway/static"), name="static")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL")
API_KEY = os.getenv("GATEWAY_API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    prompt: str

@app.get("/")   
def serve_ui():
    return FileResponse("core/gateway/static/index.html")


@app.post("/authenticate")
def authenticate(x_api_key: str = Header(None)):

    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {"message": "Authenticated successfully"}


@app.post("/run")
async def run(req: RunRequest, x_api_key: str = Header(None)):
    logger.info(f"Incoming request: {req.prompt}")
    
    if not x_api_key or x_api_key != API_KEY:
        logger.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")


    try:
        logger.info("Calling orchestrator")
        response = requests.post(
            f"{ORCHESTRATOR_URL}/run",
            json={"prompt": req.prompt},
            timeout=10
        )
        logger.info("Received response from orchestrator")
        return response.json()

    except Exception as e:
        logger.error(f"Error calling orchestrator: {str(e)}")
        return {
            "error": "Failed to reach orchestrator",
            "details": str(e)
        }


