# Large Project Structure Using Routers

### Current folder structure
So far, our project structure is quite simple:

```console title="Current Project structure"
├── env/
├── main.py
├── requirements.txt
```

### Currrent code structure
Additionally, our `main.py` file looks like this:

```python title="main.py"
from fastapi import FastAPI, Query


app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Think Python",
        "author": "Allen B. Downey",
        "publisher": "O'Reilly Media",
        "published_date": "2021-01-01",
        "page_count": 1234,
        "language": "English",
    },
    # ... (other book entries)
]

class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str

@app.get("/books", response_model=List[Book])
async def get_all_books():
    return books


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data: Book) -> dict:
    new_book = book_data.model_dump()

    books.append(new_book)

    return new_book


@app.get("/book/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.patch("/book/{book_id}")
async def update_book(book_id: int,book_update_data:BookUpdateModel) -> dict:
    
    for book in books:
        if book['id'] == book_id:
            book['title'] = book_update_data.title
            book['publisher'] = book_update_data.publisher
            book['page_count'] = book_update_data.page_count
            book['language'] = book_update_data.language

            return book
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.delete("/book/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)

            return {}
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
```
## Restructuring the project

The problem here is that if we add more code to this file, our code will become messy and hard to maintain beacuse all our code will be in one file `main.py`. To address this, we need to create a more organized project structure. To start, let's create a new folder called `src`, which will contain an `__init__.py` file to make it a Python package:

```console title="creating the src directory"
├── env/
├── main.py
├── requirements.txt
└── src/
    └── __init__.py
```

Now, create a folder named `books` inside the `src` directory. Inside this folder, add an `__init__.py` file, a `routes.py` file, a `schemas.py` file, and a `book_data.py` file. The `routes.py` file will contain all the book routes, similar to what we created in the previous chapter. The `schemas.py` file will contain the schemas that are currently in our root directory.

```console title="creating the books directory"
├── env/
├── main.py
├── requirements.txt
└── src/
    └── __init__.py
    └── books/
        └── __init__.py
        └── routes.py
        └── schemas.py
        └── book_data.py
```

First, let's move our `books` list from `main.py` to `book_data.py` inside the `books` directory.

```python title="src/books/book_data.py"


books = [
    {
        "id": 1,
        "title": "Think Python",
        "author": "Allen B. Downey",
        "publisher": "O'Reilly Media",
        "published_date": "2021-01-01",
        "page_count": 1234,
        "language": "English",
    },
    # ... (other book entries)
]
```

Next, let's also move our Pydantic validation models from `main.py` to the `schemas.py` module inside the `books` directory.

```python title="src/books/schemas.py"

from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
```

Now, let's update `routes.py` as follows:

```python title="src/books/routes.py"

from fastapi import APIRouter
from src.books.book_data import books
from src.books.schemas import BookSchema, BookUpdateSchema

book_router = APIRouter()

@book_router.get("/books", response_model=List[Book])
async def get_all_books():
    return books


@book_router.post("/books", status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data: Book) -> dict:
    new_book = book_data.model_dump()

    books.append(new_book)

    return new_book


@book_router.get("/book/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.patch("/book/{book_id}")
async def update_book(book_id: int,book_update_data:BookUpdateModel) -> dict:
    
    for book in books:
        if book['id'] == book_id:
            book['title'] = book_update_data.title
            book['publisher'] = book_update_data.publisher
            book['page_count'] = book_update_data.page_count
            book['language'] = book_update_data.language

            return book
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete("/book/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)

            return {}
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
```
## Introduction to FastAPI routers 
What has been accomplished is the division of our project into modules using routers. FastAPI routers allow easy modularization of our API by grouping related API routes together. Routers function similarly to FastAPI instances (similar to what we have in `main.py`). As our project expands, we will introduce additional API routes, and all of them will be organized into modules grouping related functionalities.

Let's enhance our `main.py` file to adopt this modular structure:

```python title="Including the book router to our app"

# Inside main.py title
from fastapi import FastAPI
from src.books.routes import book_router

version = 'v1'

app = FastAPI(
    title='Bookly',
    description='A RESTful API for a book review web service',
    version=version,
)

app.include_router(book_router,prefix=f"/api/{version}/books", tags=['books'])
```

Firstly, a variable called `version` has been introduced to hold the API version. Next, we import the `book_router` created in the previous example. Using our FastAPI instance, we include all endpoints created with it by calling the `include_router` method.

Arguments added to the FastAPI instance are:

- `title`: The title of the API.
- `description`: The description of the API.
- `version`  : The version of the API.

While these arguments may not be particularly useful at present, they become valuable when we explore API documentation with **OpenAPI**.

Furthermore, we added the following arguments to the include_router method:

- `prefix`: The path through which all related endpoints can be accessed. In our case, it's named the /{version}/books prefix, resulting in /v1/books or /v2/books based on the application version. This implies that all book-related endpoints can be accessed using http://localhost:8000/api/v1/books.

- `tags`: The list of tags associated with the endpoints that fall within a given router.

Let us now now move all the source code in our `main.py` module to `src/__init__.py`. (delete your `main.py`)

```python title="src/__init__.py"
from fastapi import FastAPI
from src.books.routes import book_router

version = 'v1'

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version= version,
    lifespan=life_span
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
```
Having moved our code, we shall now have this folder structure.
```console title="modified directory structure"
├── requirements.txt
├── run.py
└── src
    ├── books
    │   ├── book_data.py
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── schemas.py
    │   ├── book_data.py
    └── __init__.py
```

Once more, let's start our server using `fastapi dev src/`. Pay attention to the fact that this time we're specifying`src/`. This is because we've designated it as a package by including `__init__.py`. Additionally, our FastAPI instance named `app` is created there. Consequently, FastAPI will utilize it to operate our application.

Runnning our application will the following terminal output.
```console title="Running the server"
INFO     Using path src                                                                                                                                     
INFO     Resolved absolute path /home/jod35/Documents/fastapi-beyond-CRUD/src                                                                               
INFO     Searching for package file structure from directories with __init__.py files                                                                       
INFO     Importing from /home/jod35/Documents/fastapi-beyond-CRUD                                                                                           
                                                                                                                                                            
 ╭─ Python package file structure ─╮                                                                                                                        
 │                                 │                                                                                                                        
 │  📁 src                         │                                                                                                                        
 │  └── 🐍 __init__.py             │                                                                                                                        
 │                                 │                                                                                                                        
 ╰─────────────────────────────────╯                                                                                                                        
                                                                                                                                                            
INFO     Importing module src                                                                                                                               
INFO     Found importable FastAPI app                                                                                                                       
                                                                                                                                                            
 ╭─ Importable FastAPI app ─╮                                                                                                                               
 │                          │                                                                                                                               
 │  from src import app     │                                                                                                                               
 │                          │                                                                                                                               
 ╰──────────────────────────╯                                                                                                                               
```

### Note:

The current organization of our API endpoints is as follows:

| Endpoint	| Method |	Description |
|-----------|--------|--------------|
| /api/v1/books |	GET  | Read all books |
| /api/v1/books |	POST | Create a book |
| /api/v1/books/{book_id} |	GET |	Get a book by ID |
| /api/v1/books/{book_id} |	PATCH |	Update a book by ID |
| /api/v1/books/{book_id} |	DELETE |	Delete a book by ID |


## Conclusion
This chapter has focused on creating a folder structure that we can use even when our project gets bigger. In the next chapter, we shall focus on database and look at how we can persist our data and use Python to manage a relational database.


