import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from icecream import ic

from app.core.logger.app_logger import get_app_logger

ic.configureOutput(includeContext=True)

logger = get_app_logger()
logger.info("Starting the application")

is_prod = False

app = FastAPI(
    redirect_slashes=True,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
)

origins = ["*"]  # if not is_prod else [""]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
