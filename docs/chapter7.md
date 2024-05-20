# Authentication And Authorization
Now that we have a working CRUD API, let's move on to more advanced topics. The first thing we need to tackle is figuring out who our users are and what they can do in the application. This breaks down into two main points:

- **Authentication**: Making sure users are who they say they are.
- **Authorization**: Deciding what actions users are allowed to take based on their identity.
 
## Creating the user account model
To achieve that, we shall begin by having a database model for keeping information about user accounts. Our current project structure looks like.
```
├── README.md
├── requirements.txt
└── src
    ├── books
    │   ├── book_data.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── routes.py
    │   ├── schemas.py
    │   └── service.py
    ├── config.py
    ├── db
    │   ├── __init__.py
    │   └── main.py
    └── __init__.py
```

Inside the `src` folder, we shall create a directory called `auth`. This shall keep all source code associated with user account management. Inside it, we shall create a `__init__.py` file to mark it as a Python package. Our updated directory structure is now:

```
├── README.md
├── requirements.txt
└── src
    ├── auth
    │   └── __init__.py
    ├── books
    │   ├── book_data.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── routes.py
    │   ├── schemas.py
    │   └── service.py
    ├── config.py
    ├── db
    │   ├── __init__.py
    │   └── main.py
    └── __init__.py
```

Let us now add a `models.py` file in which we shall create the user account model. 

```python
# inside src/auth/models.py
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"},
        )
    )

    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    is_verified: bool = False
    email: str
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=func.now))

    def __repr__(self) -> str:
        return f"<User {self.username}>"
```

Most of the code here was explained In [Chapter 5](./chapter5.md), so I will only explain what seems new.

- We created a database model called `User` that has the table name `user accounts`.
- We have added the primary fields `uuid`, with other fields such as the `first_name`, `last_name`, `email`, `password_hash`, `created_at`, and finally `is verified`.

- The `is_verified` step is going to be necessary as it shall allow us to verify user provided email addresses so that we can deal with only valid email addresses.

Once we have created this database model let us save it and then make this table reflect inside our database.

## Different Authentication Types

### HTTP Basic Authentication
```python
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse


auth_router = APIRouter()

basic = HTTPBasic()

@auth_router.get('/login')
async def login_user(user_creds: HTTPBasicCredentials= Depends(basic)):
    test_username = "jona"
    test_password = "p455w0rd"
    
    user = user_creds.username
    password = user_creds.password

    if (user == test_username) and (password == test_password):
        return {"username":user , "password":password}

    return JSONResponse(content={"error":"Invalid username or password"}, status_code=status.HTTP_400_BAD_REQUEST)
```