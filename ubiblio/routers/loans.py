from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import crud, schemas, models
from ..database import SessionLocal
from ..dependencies import admin_user, current_user

router = APIRouter(prefix="/loans", tags=["loans"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/checkout", response_model=schemas.LoanResponse)
def checkout_book(loan_req: schemas.LoanCreate, db: SessionLocal = Depends(get_db), user: models.User = Depends(admin_user)):
    loan = crud.checkout_book(
        db=db, 
        user_id=loan_req.user_id, 
        copy_id=loan_req.copy_id,
        expected_return_date=loan_req.expected_return_date
    )
    if not loan:
        raise HTTPException(status_code=400, detail="Copy not available or user not found")
    return loan

@router.post("/return", response_model=schemas.LoanResponse)
def return_book(return_req: schemas.LoanReturn, db: SessionLocal = Depends(get_db), user: models.User = Depends(admin_user)):
    loan = crud.return_book(db=db, copy_id=return_req.copy_id)
    if not loan:
        raise HTTPException(status_code=400, detail="No active loan found for this copy")
    return loan

@router.get("/user/{user_id}", response_model=List[schemas.LoanResponse])
def get_user_loans(user_id: int, db: SessionLocal = Depends(get_db), user: models.User = Depends(current_user)):
    if not user.isAdmin and user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_user_loans(db=db, user_id=user_id)

@router.get("/copy/{copy_id}", response_model=List[schemas.LoanResponse])
def get_copy_loans(copy_id: int, db: SessionLocal = Depends(get_db), user: models.User = Depends(admin_user)):
    return crud.get_copy_loans(db=db, copy_id=copy_id)

@router.get("/overdue", response_model=List[schemas.LoanResponse])
def get_overdue_loans(db: SessionLocal = Depends(get_db), user: models.User = Depends(admin_user)):
    return crud.get_overdue_loans(db=db)
