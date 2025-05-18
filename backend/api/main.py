from fastapi import FastAPI
from db import init_db
from api.routes import subscription

app = FastAPI(title="My Arxiv Listener API")

app.include_router(subscription.router)

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok"}



