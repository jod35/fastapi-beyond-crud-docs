# Finishing Up the CRUD

## Creating a service class
In this chapter, we will focus on creating a dedicated service file to house the essential logic required for executing CRUD operations using our PostgreSQL database. The primary objective is to abstract away database interactions from our API routes, enhancing code readability and maintainability.

We will construct a class within this service file, which will serve as a centralized point for invoking all methods related to managing our book data.

To initiate this process, let's commence by creating the file `service.py` within the `src/books/` directory.
```python title="/src/books/service.py"
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.models import Book
from src.books.schemas import BookCreateModel
from sqlmodel import select


class BookService:
    """
    This class provides methods to create, read, update, and delete books
    """

    pass

```

We call this class `BookService` as it shall be called only when managing data about books. 


### Read all books
Let us begin by adding the method `get_all_books` that is responsible for getting all the books from the database.

```python title="Get all books"
... #the rest of the BookService class
async def get_all_books(self, session: AsyncSession):
    """
    Get a list of all books

    Returns:
        list: list of books
    """
    statement = select(Book).order_by(desc(Book.created_at))

    result = await session.exec(statement)

    return result.all()
```

To start, we craft a query utilizing the `select` function from SQLModel, initiating an SQL **SELECT** operation on our Books table. Subsequently, we sort the books based on their creation date (**created_at**) via the **order_by** method.

This constructed statement is subsequently executed through the `session` object. The resulting `result` object will return a list of books obtained by invoking the `all` method.

### Creating a new Book
Let us now add the method for creating a new book
```python title="Create a book"
... # rest of the BookService class
async def create_book(self, book_data: BookCreateModel, session:AsyncSession):
    """
    Create a new book

    Args:
        book_data (BookCreateModel): data to create a new

    Returns:
        Book: the new book
    """
    book_data_dict = book_data.model_dump()

    new_book = Book(
        **book_data_dict
    )

    new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")

    session.add(new_book)

    await session.commit()

    return new_book
```
The `create_book` method is responsible for adding a new book to the database using the provided book data. Specifically, `book_data` must adhere to the structure defined by a Pydantic model called `BookCreateModel`, which we'll soon create in our `src/books/schema.py` directory.


To create a new book record, we begin by initializing a new instance of the Book database model. This is achieved by unpacking `book_data`, which we convert into a Python dictionary utilizing the model_dump method.

Following this, we utilize our `session` object to add the new book record to the database via `session.add`. Finally, we commit the transaction to ensure that the changes are persisted in the database, accomplished with `session.commit`, not forgetting to return the newly created book record.

Before we proceed, we need to add the `BookCreateSchema` class to `src/books/schemas.py` 

Let us add the `BookCreateSchema` class to `src/books/schemas.py`.
```python title="The BookCreateModel class"
...
class BookCreateModel(BaseModel):
    """
        This class is used to validate the request when creating or updating a book
    """
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
```


### Retrieve a book by its uid
```python title="Retrieve a book by its uid"
... # the rest of the BookService class
async def get_book(self, book_uid: str, session:AsyncSession):
    """Get a book by its UUID.

    Args:
        book_uid (str): the UUID of the book

    Returns:
        Book: the book object
    """
    statement = select(Book).where(Book.uid == book_uid)

    result = await session.exec(statement)

    book = result.first()

    return book if book is not None else None
```

To retrieve a book from the database, we construct a `select` statement to fetch all books but filter by the `uid` to ensure that only the desired book is retrieved. This filtering is achieved using the `where` method.

Subsequently, we execute the statement using the `session` object, obtaining the `result`. Finally, we retrieve the book by invoking the `first` method on the result object. Note that we are returning `None` if a book matching the `uid` is not found.

### Update a book
To update a book, we need to retrieve the book to update by its `uid`. secondly, we need to get the data we shall be updating the book with (`update_data`). Finally, we shall update the book fields with the new data and  return the updated book if found or None when not.



```python title="Update a book"
... # rest of the BookService class
async def update_book(self, book_uid: str, update_data: BookCreateSchema, session: AsyncSession):
    """Update a book

    Args:
        book_uid (str): the UUID of the book
        update_data (BookCreateModel): the data to update the book

    Returns:
        Book: the updated book
    """

    book_to_update = await self.get_book(book_uid,session)

    if book_to_update is not None:
        update_data_dict = update_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(book_to_update,k ,v)

        await session.commit()

        return book_to_update
    else:
        return None
```
To implement the `update_book` method, which updates a book by its UID, we first fetch the book based on its UID, following the approach described for retrieving a book.

Next, we update the book object with the following code:

```python title="Update book"
# Unpack the book data dictionary and set fields
for key, value in update_data.model_dump().items():
    setattr(book, k, v)
```

This code iterates over the key-value pairs in the dictionary obtained from `update_data.model_dump()`, setting each field of the book object accordingly.

Finally, after updating the book object with the new data, we commit the changes to the database using session.commit(). This ensures that the modifications made to the book are saved persistently in the database.


### Delete a Book
To delete a book from the database, we follow a similar approach as when retrieving a book. Once we have obtained the book object from the database using its `uid`, we use the `session.delete` method to mark the `book` object for deletion. To finalize the deletion and apply the changes to the database, we call `session.commit()`. This ensures that the book is effectively removed from the database.

```python title="Delete a book"
... #rest of the BookService class
async def delete_book(self, book_uid:str , session:AsyncSession):
    """Delete a book

    Args:
        book_uid (str): the UUID of the book
    """
    book_to_delete = await self.get_book(book_uid,session)

    if book_to_delete is not None:
        await session.delete(book_to_delete)

        await session.commit()

        return {}

    else:
        return None
```

Let update our routes to ensure they use our newly created book database to Create, Read, Update and Delete our book database record. The source code for `src/books/service.py` should look like this at this point.

```python title="src/books/service.py"
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from datetime import datetime

class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)

        result = await session.exec(statement)

        book = result.first()

        return book if book is not None else None

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()

        new_book = Book(
            **book_data_dict
        )

        new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")

        session.add(new_book)

        await session.commit()

        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid,session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_to_update,k ,v)

            await session.commit()

            return book_to_update
        else:
            return None

    async def delete_book(self,book_uid:str, session:AsyncSession):
        
        book_to_delete = await self.get_book(book_uid,session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)

            await session.commit()

            return {}

        else:
            return None

```

## Dependency Injection
Now that we have created the `BookService` class, we need to create the `session` object that we shall use a dependency in every API route that shall interact with the database in any way.

Dependency injection in FastAPI allows for the sharing of state among multiple API routes by providing a mechanism to create Python objects, referred to as **dependencies**, and accessing them only when necessary within dependant functions. While the concept may initially seem technical and esoteric, it is a fundamental aspect of FastAPI that proves remarkably beneficial across various scenarios. Interestingly, we often employ dependency injection without realizing it, demonstrating its widespread usefulness. Some potential applications include:

- Gathering input parameters for HTTP requests (Path and query parameters)
- Validating parameters inputs
- Checking authentication and authorization (we shall look at this in coming chapters)
- Emitting logs and metrics e.t.c.


Let us create our first dependency:
```python title="src/db/main.py"
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

... # rest of main.py

async def get_session() -> AsyncSession:
"""Dependency to provide the session object"""
async_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async with async_session() as session:
    yield session
```

In the above code, we define an async function called `get_session` that should return an object of the `AsyncSesion` class. This class is what allows us to use an aync DBAPI to interact with the database. That is the object we shall create all `BookService` objects with.




Now that we have an understanding of how we shall get our session, let us go to the `src/books/routes.py` and modify it to make calls to the methods we have so far defined inside the `BookService` class.

```python title="Modified routes with updated CRUD in src/books/routes.py"
from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from typing import List

book_router = APIRouter()
book_service = BookService()


@book_router.get("/", response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel, session: AsyncSession = Depends(get_session)
) -> dict:
    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
) -> dict:

    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    else:
        return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    else:

        return {}

```

We've made minimal changes to the file but have introduced some updates that I'll outline here. Let's start by examining the dependency injection we've integrated. Take note of how we've included the following code in each route handler function.
```python
session: AsyncSession = Depends(get_session)
```
What we're accomplishing here is the sharing of the `session` generated by calling the `get_session` function we defined earlier in this chapter.

Once the `session` is established, we proceed to instantiate the `BookService` class. This instance allows us to utilize its methods for performing various **CRUD** operations as needed.

```python
books = await BookService(session).get_all_books()
```
We instantiate the `BookService` function to invoke its `get_all_books()` method, supplying the session as a dependency to the route handler that includes the above code.

### Conclusion

In this chapter, we expanded our application to incorporate CRUD operations on our book data by leveraging our persistent PostgreSQL database. We explored how to utilize SQLModel to accomplish this task efficiently.


**Previous**: [Databases with SQLModel](./chapter5.md)

**Next**: [Finishing Up the CRUD](./chapter7.md)