import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from icecream import ic
import debugpy

from app.core.logger.app_logger import log
from app.config.settings import settings
from app.api.v1.routers.auth_router import router as auth_router
from app.api.v1.routers.memory_router import router as memory_router
from app.api.v1.routers.search_router import router as search_router
from app.api.v1.routers.ginarr_router import router as ginarr_router

if settings.DEBUG:
    debugpy.listen(("0.0.0.0", 5678))
    # debugpy.wait_for_client()
    print("Debugger is attached!")

ic.configureOutput(includeContext=True)

log.info("Starting the application")

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


app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(search_router)
app.include_router(ginarr_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
