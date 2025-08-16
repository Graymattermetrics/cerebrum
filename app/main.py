"""Handles API endpoints.

Implements middleware on the app.
"""

from contextlib import asynccontextmanager

import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import clients, cogspeed


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()

    yield


app = fastapi.FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(clients.router)
app.include_router(cogspeed.router)


@app.get("/")
async def get_root():
    return "Hello"
