from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from typing import List
import os

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import desc
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


@p_router.get("/suppliers", response_model=List[models.Supplier])
async def get_suppliers(db: Session = Depends(get_db)):
    return get_suppliers(db)
    

@p_router.get("/suppliers/{supplier_id}/products", status_code=status.HTTP_200_OK)
async def get_supplier_products(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier_products = get_supplier_products_orm(db, supplier_id)
    if not db_supplier_products:
        raise HTTPException(status_code=404, detail="Supplier's products not found")
    return list(
        [ models.SupplierProduct(
            ProductID=row.Product.ProductID, 
            ProductName=row.Product.ProductName, 
            Category=models.CategoryData(
                CategoryID=row.Category.CategoryID,
                CategoryName=row.Category.CategoryName
            ),
            Discontinued=row.Product.Discontinued
            ) for row in db_supplier_products]
    )


@p_router.post("/suppliers", status_code=status.HTTP_201_CREATED, response_model=models.ReturnedSupplier)
async def create_supplier(new_supplier: models.PostedSupplier, db: Session = Depends(get_db)):
    # curl -X POST -d '{/"CompanyName/": /"CName/"}' 127.0.0.1:8000/suppliers
    
    last_supplier = db.query(models_postgres.Supplier).order_by(models_postgres.Supplier.SupplierID.desc()).first()

    orm_supplier = models_postgres.SupplierID(**new_supplier.dict())
    orm_supplier.SupplierID = last_supplier.SupplierID + 1

    db.add(orm_supplier)
    db.flus()
    db.commit()

    return orm_supplier

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


def get_supplier_products_orm(db: Session, supplier_id: int):
    return (
        db.query(models_postgres.Product, models_postgres.Category)
        .filter(models_postgres.Product.CategoryID == models_postgres.Category.CategoryID)
        .filter(models_postgres.Product.SupplierID == supplier_id)
        .order_by(models_postgres.Product.ProductID.desc())
        .all()
    )

    """
    SELECT
        p.ProductID, 
        p.ProductName,
        c.CategoryID,
        c.CategoryName,
        p.Discontinued 
    FROM Products AS p 
    JOIN Categories AS c on p.CategoryID  = c.CategoryID
    JOIN Suppliers AS s on s.SupplierID = p.SupplierID
    WHERE s.SupplierID = 1
    ORDER BY p.ProductID DESC;
    """

