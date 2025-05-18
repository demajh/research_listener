from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from db import SessionLocal
from models.user import Subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

class SubCreate(BaseModel):
    email: EmailStr
    arxiv_channel: str
    interest_description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=201)
def create_subscription(sub: SubCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(Subscription)
        .filter(
            Subscription.email == sub.email,
            Subscription.arxiv_channel == sub.arxiv_channel,
        )
        .first()
    )
    if exists:
        raise HTTPException(400, detail="Subscription already exists")
    new = Subscription(**sub.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id}

@router.get("/", response_model=list[SubCreate])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).filter(Subscription.is_active.is_(True)).all()
