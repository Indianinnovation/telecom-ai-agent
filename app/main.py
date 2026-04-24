from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv
import logging
import os

# Load .env at startup
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="Telecom AI Agent",
    description="LangGraph-powered telecom root cause analysis",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
