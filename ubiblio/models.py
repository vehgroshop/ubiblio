from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    passhash = Column(String)
    isAdmin = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    loans = relationship("Loan", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    summary = Column(String)
    genre = Column(String)
    library = Column(String)
    shelf = Column(String)
    collection = Column(String)
    ISBN = Column(String)
    notes = Column(String, nullable=True)
    owned = Column(Boolean)
    withdrawn = Column(Boolean)
    withdrawnBy = Column(String, nullable=True)
    customField1 = Column(String, nullable=True)
    customField2 = Column(String, nullable=True)
    ebook = Column(Boolean,nullable=True, default=False)
    copies = relationship("BookCopy", back_populates="book")

class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    copy_identifier = Column(String, unique=True, index=True)
    status = Column(String, default="available")  # available, loaned, lost, maintenance
    condition_notes = Column(String, nullable=True)
    
    book = relationship("Book", back_populates="copies")
    loans = relationship("Loan", back_populates="copy")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    copy_id = Column(Integer, ForeignKey("book_copies.id"), index=True)
    loan_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_return_date = Column(DateTime(timezone=True))
    actual_return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active")  # active, returned, overdue
    
    user = relationship("User", back_populates="loans")
    copy = relationship("BookCopy", back_populates="loans")

class readingListItems(Base):
    __tablename__ = "readinglistitems"
    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer)
    
class bookImage(Base):
    __tablename__ = "bookImages"
    id = Column(Integer, primary_key=True)
    bookId = Column(Integer, ForeignKey("books.id"))
    filename = Column(String, nullable=False)  

class config(Base):
    __tablename__= "config"
    id = Column(Integer, primary_key=True)
    version = Column(String)
    coverImages = Column(Boolean)
    customFieldName1 = Column(String, nullable=True)
    customFieldName2 = Column(String, nullable=True)
    genres = Column(String)

class ebook(Base):
    __tablename__ = "ebooks"
    id = Column(Integer, primary_key=True)
    bookId = Column(Integer, ForeignKey("books.id"))
    filename = Column(String, nullable=False) 

class emails(Base):
    __tablename__ = "userEmails"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=True)
    user_id = Column(Integer)
    
class link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    accessCode = Column(String, index=True)
    validity = Column(DateTime(timezone=True), server_default=func.now())
    
class vkey(Base):
    __tablename__ = "vkeys"
    id = Column(Integer, primary_key=True)
    vkey = Column(String, index=True)
    url = Column(String, index=True)
    
    
