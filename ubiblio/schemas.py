from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

DEFAULT_GENRES=[
    "Sci-Fi", "Fantasy", "Classic", "Reference", "Young Adult", "Historical Fiction", "Mystery", "Anthology", "Horror", "Romance", "Animal Fiction"
]

class UserBase(BaseModel):
    username: str
    isAdmin: bool = Field(default=False)
    full_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)
    

class User(UserBase):
    id: int
    passhash: str

        
#This is so password plaintext is only sent/received by anything on account creation
class UserCreate(UserBase):
    password: str
    

class BookBase(BaseModel):
    title: str
    model_config = ConfigDict(from_attributes=True)

class Book(BookBase):
    id: int 
    author: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    genre: Optional[str] = Field(default=None)
    library: Optional[str] = Field(default=None)
    shelf: Optional[str] = Field(default=None)
    collection: Optional[str] = Field(default=None)
    ISBN: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owned: bool = Field(default=False)
    withdrawn: bool = Field(default=False)
    withdrawnBy: Optional[str] = Field(default=None)
    withdrawnDate: Optional[datetime] = Field(default=None)
    customField1: Optional[str] = Field(default=None)
    customField2: Optional[str] = Field(default=None)
    ebook: Optional[bool] = Field(default=False)

class BookCreate(BookBase):
    author: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    genre: Optional[str] = Field(default=None)
    library: Optional[str] = Field(default=None)
    shelf: Optional[str] = Field(default=None)
    collection: Optional[str] = Field(default=None)
    ISBN: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owned: Optional[bool] = Field(default=None)
    withdrawn: bool = Field(default=False)
    withdrawnBy: Optional[str] = Field(default=None)
    withdrawnDate: Optional[datetime] = Field(default=None)
    customField1: Optional[str] = Field(default=None)
    customField2: Optional[str] = Field(default=None)
    ebook: Optional[bool] = Field(default=False)
    # Transport-only: EasyCB cover resource filename passed through ISBN preview
    # form so the cover can be downloaded once the book row exists. Excluded
    # from model_dump when persisting.
    coverFilename: Optional[str] = Field(default=None, exclude=True)

class BookCopyBase(BaseModel):
    copy_identifier: str
    status: str = Field(default="available")
    condition_notes: Optional[str] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)

class BookCopyCreate(BookCopyBase):
    book_id: int

class BookCopy(BookCopyBase):
    id: int
    book_id: int

class LoanBase(BaseModel):
    user_id: int
    copy_id: int
    model_config = ConfigDict(from_attributes=True)

class LoanCreate(LoanBase):
    expected_return_date: Optional[datetime] = Field(default=None)

class Loan(LoanBase):
    id: int
    loan_date: datetime
    expected_return_date: datetime
    actual_return_date: Optional[datetime] = Field(default=None)
    status: str

class BookCopyResponse(BookCopy):
    book: Optional[Book] = None

class LoanResponse(Loan):
    user: Optional[UserBase] = None
    book_copy: Optional[BookCopyResponse] = Field(default=None, validation_alias="copy", serialization_alias="copy")

class LoanReturn(BaseModel):
    copy_id: int


class readingListItems(BaseModel):
    id: int
    book: int
    user_id: int 
    model_config = ConfigDict(from_attributes=True)
 
class readingListItemCreate(BaseModel):
    book: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
    
class bookImageBase(BaseModel):  
    bookId: int
    filename: str
    model_config = ConfigDict(from_attributes=True)
        
class bookImage(bookImageBase):  
    id: int 

class config(BaseModel):
    id: int 
    version: Optional[str] = Field(default=None)
    coverImages: bool = Field(default=False)
    customFieldName1: Optional[str] = Field(default=None)
    customFieldName2: Optional[str] = Field(default=None)
    genres: str = Field(default=",".join(DEFAULT_GENRES))
    model_config = ConfigDict(from_attributes=True)

class userEmail(BaseModel):
    id: int
    email: str
    user_id: int 
    model_config = ConfigDict(from_attributes=True)

         
class userEmailCreate(BaseModel):
    email: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class ebookBase(BaseModel):  
    bookId: int
    filename: str
    model_config = ConfigDict(from_attributes=True)
        
class ebook(ebookBase):  
    id: int 

#These are for temporary access links to create new users. Datetime will be the DB datetime.
class linkBase(BaseModel):
    accessCode: str
    
class link(linkBase):
    id: int  
    validity: datetime
    model_config = ConfigDict(from_attributes=True)

class vkeyBase(BaseModel):
    vkey: str
    url: str
    
class vkey(vkeyBase):
    id: int  
    model_config = ConfigDict(from_attributes=True)
