from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from typing import List
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import models_postgres
import models

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

p_router = APIRouter()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@p_router.get("/shippers/{shipper_id}")
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@p_router.get("/shippers")
async def get_shippers(db: Session = Depends(get_db)):
    return get_shippers(db)


@p_router.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


@p_router.get("/suppliers")
async def get_suppliers(db: Session = Depends(get_db)):
    return get_suppliers(db)
    

# ORM Functions - get data from DB based on Session.
def get_shippers(db: Session):
    return db.query(models_postgres.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models_postgres.Shipper).filter(models_postgres.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models_postgres.Supplier).all()


def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(models_postgres.Supplier).filter(models_postgres.Supplier.SupplierID == supplier_id).first()
    )
