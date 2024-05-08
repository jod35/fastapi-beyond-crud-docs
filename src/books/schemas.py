from pydantic import BaseModel
from datetime import datetime

class BookSchema(BaseModel):
    id:int
    title:str
    author:str
    publisher:str
    published_date: datetime
    page_count:int
    language:str

class BookUpdateSchema(BaseModel):
    title:str
    author:str
    publisher:str
    page_count:int
    language:str


class BookCreateModel(BaseModel):
    """
        This class is used to validate the request when creating or updating a book
    """
    title: str
    author: str
    isbn: str
    description: str

# "id": 1,
# "title": "Think Python",
# "author": "Allen B. Downey",
# "publisher": "O'Reilly Media",
# "published_date": "2021-01-01",
# "page_count": 1234,
# "language": "English",
