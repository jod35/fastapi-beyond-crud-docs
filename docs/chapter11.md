# Model And Schema Relationships

## Introduction
At this point, the only database tables that we have in our database look like the following. If you want such good database design diagrams, please use [DB Diagrams](https://dbdiagram.io/)

![Current database structure](./img/img36.png)

To ensure that users can submit multiple books in a one-to-many relationship, we can modify the database structure. Here's how the updated structure would look:

![Modified database structure](./img/img37.png)

In  this structure, we have not really made changes to the `users` table and we have modified the `books` table by adding the `user_uid` that referencing the `uid` field on the `users` table to establish a foreign key relationship.This relationship signifies that each book entry in the books table is associated with a single user who submitted it.


### Modifying the User Table
To achieve this, let us modify the `Book` database model in `src/books/models.py` to make the above changes take effect.

```python title="the modified books table"

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    # add this line below
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Book {self.title}>"
```

The user_uid field in the Book class represents a foreign key relationship to the uid field in a hypothetical users table, linking each book entry to the user who submitted it. This field is optional (Optional[uuid.UUID]) and defaults to None, allowing for books that may not be associated with a specific user. When a user submits a book, their unique identifier (uid) would typically be stored in this field, enabling queries that link books to their respective owners. This design supports database integrity and enables efficient retrieval of books based on user ownership within the application's data model.

For this change to reflect in the database, let us create an Alembic revision for it.
```console
$ alembic revision --autogenerate -m "add user_uid foreignkey to books"
```

After that, we shall apply this revision to the database by using the following command
```console
$ alembic upgrade head
```

### Associate users with books
To ensure each book submission is associated with the currently authenticated user's user_uid, we'll modify the BookService class in src/books/service.py. Here's how you can adjust the code to accommodate this:

```python
class BookService:
    ... # rest of the code

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)

        return result.all()

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)

        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        )

        new_book.user_uid = user_uid

        session.add(new_book)

        await session.commit()

        return new_book

```

The modified `BookService` class includes two asynchronous methods to handle book submissions and retrievals, ensuring each book is associated with the currently authenticated user's `user_uid`. The `get_user_books` method retrieves all books submitted by a specific user, identified by their `user_uid`. It constructs a SQL query using SQLModel's select to fetch books where the `user_uid` matches the provided value, ordered by the book's creation date in descending order. The result of the query is executed asynchronously and returned as a list of books.

The `create_book` method handles the creation of a new book entry. It takes in book data (wrapped in a BookCreateModel), the `user_uid` of the currently authenticated user, and an asynchronous database session (AsyncSession). The method converts the book data into a dictionary format and initializes a new Book instance with this data. It then parses and sets the `published_date` field and assigns the `user_uid` to link the book with the authenticated user. The new book instance is added to the session, and the session commits the transaction asynchronously, saving the new book to the database. This ensures each book submission is correctly associated with the user who submitted it.

Let us also make these changes reflect in our routes.
```python title="modified route for creating books"
from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from typing import List
from src.auth.dependencies import AccessTokenBearer, RoleChecker


book_router = APIRouter()
book_service = BookService()
acccess_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acccess_token_bearer),
) -> dict:
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session) # change this 
    return new_book
```
The modified route for creating books now includes extracting the `user_uid` from the token details of the currently authenticated user. This `user_uid` is then passed to the `create_book` method of the `BookService` class. After we retrieve the user's unique identifier from the token:

```python title="getting the user_uid from token details"
user_id = token_details.get("user")["user_uid"]
```

To ensure that each book submission is correctly associated with the user who submitted it, we link the book to the user using the `user_uid`:

```python title="create book with user who added it"
new_book = await book_service.create_book(book_data, user_id, session)
```

Creating a Book will result in:

![creating a book](./img/img38.png)

In the database, the book will be saved with the `user_uid`.

### Relationship attributes

With the relationship between books and users established, let's explore a method of performing CRUD operations in a more object-oriented manner using relationship attributes. These attributes enable us to define fields in our model classes that serve not as database rows but as means to access related objects. For instance, we will retrieve all books added by a user using user.books, where books is the attribute that provides access to all the books submitted by the user.



To begin, we shall create the attribute on the user tables that shall enable us get the books a user has sbumitted. Let us modify the `User` database model to include the following.

```python
import uuid
from datetime import date, datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False), exclude=True
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    # add this
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User {self.username}>"
```

The change defines a relationship attribute `books` for a `User` model, which is a list of `Book` objects. The `Relationship` function establishes a two-way connection between the `User` and `Book` models, with `back_populates="user"` indicating that each `Book` instance is linked back to the `User` instance that added it. 

The `sa_relationship_kwargs={"lazy": "selectin"}` parameter optimizes the query performance by loading related `Book` objects in a single query when the `User` object is accessed, reducing the number of database queries and improving efficiency.

Let us also modify our Book model to have this change. Inside `src/books/models.py`,


```python title="books with a user relationship"
class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="books") #add this

    def __repr__(self):
        return f"<Book {self.title}>"

```

On the Book model, we have defined a relationship attribute `user`, which optionally refers to a User object. The `Relationship` function establishes a connection where each `Book` instance can be associated with a single `User` instance, specified by `back_populates="books"`. This bidirectional relationship means that for every Book, there is a corresponding User who owns or is associated with that book.


### Pydantic Relationships
Let us modify the user schemas to make sure we return a user as well as the books that are associated with their account. To begin, we shall go to `src/auth/schemas.py` and add the following.

```python title="schema for listing user submitted books"
 import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.books.schemas import Book
from src.reviews.schemas import ReviewModel

... # rest of the code

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    update_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]

... # rest of the file
```
In the above code, we have created a subclass of `UserModel` called `UserBooksModel` that inherits all its attributes. The `UserBooksModel` uses the `typing.List` type to return a list of `Book` objects that a user has submitted. Now, let's use this schema to return the currently logged-in user along with all the books associated with them. Let's go back to `src/auth/routes.py`.



```python title="return user and related books"
... # rest of imports
from .dependencies import (AccessTokenBearer, RefreshTokenBearer, RoleChecker,
                           get_current_user)
from .schemas import UserBooksModel, UserCreateModel, UserLoginModel, UserModel

... # rest of the routes

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user

```

What we have done is add the `response_model` argument to the HTTP method of the path to get the current user. This is provided the value of the `UserBooksModel`, meaning that the `user` will be returned with a list of books they have submitted. To test this, let us use our API client, Insomnia.

![Get user with books](./img/img39.png)

With that, we shall notice that we can get the currently logged in user as well as the books that they added.

