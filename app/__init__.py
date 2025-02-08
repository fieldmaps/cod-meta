from fastapi import FastAPI

from .routers import health, metadata

app = FastAPI()
app.include_router(metadata.router)
app.include_router(health.router)
