## User account Creation
In the previous chapter, we created a database model for user accounts. Using this, we are going to authenticate (show that our users are who they claim to be) and also authorize (show that they have the right access to specific parts of our application.)

## Creating User Accounts
Ths first task shall be one of making users join our application through signing up. Using thisstep, users shall have user accounts that can allow them use the application.

Our current project structure is something like this.
```console
├── alembic.ini
├── migrations
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       └── 8cf8276d5f3c_init.py
├── README.md
├── requirements.txt
└── src
    ├── auth
    │   ├── __init__.py
    │   ├── models.py
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
    └── __init__.pyz
```


Let us begin by creating `src/auth/service.py` and adding the folowing code to it.
```python
# inside src/auth/service.py
from .models import User
from .schemas import UserCreateModel
from .utils import generate_passwd_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_passwd_hash(user_data_dict["password"])

        session.add(new_user)

        await session.commit()

        return new_user

```

### Retrieving a user by their email
Inside this file, we have created a class `UserService` containing some methods that shall be necessary when creating user accounts. Let us begin by looking at the first method `get_user_by_email`.
```python
#inside src/auth/service.py
async def get_user_by_email(self, email: str, session: AsyncSession):
    statement = select(User).where(User.email == email)

    result = await session.exec(statement)

    user = result.first()

    return user
```

This function is responsible for retrieving a user by their username. First we create a statement the queries for a user by their email.
```python
statement = select(User).where(User.email == email
```

Next, we create a result object from using our session object to execute the statement.
```python
result = await session.exec(statement)

user = result.first()

```

We then access to the returned user object using the `first` method. Finally, we return the user object.

### Checking if a user exists
The next method is the `user_exists` method that shows if a user exists by returning `True` if the user exists else `False`.

```python
async def user_exists(self, email, session: AsyncSession):
    user = await self.get_user_by_email(email, session)

    return True if user is not None else False
```

### Creating the user account
Lastly we have the `create_user` function that is responsible fo creating a user account.
```python
async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
    user_data_dict = user_data.model_dump()

    new_user = User(**user_data_dict)

    new_user.password_hash = generate_passwd_hash(user_data_dict["password"])

    session.add(new_user)

    await session.commit()

    return new_user
``` 

This function has two parameters, the `user_data` and the `session` object. The `user_data` parameter is of type `BookCreateModel` which we are going to define in a  `schemas.py`
we have to created inside our `auth` directory.
```python
#inside src/auth/schemas.py
class UserCreateModel(BaseModel):
    first_name: str =Field(max_length=25)
    last_name:  str =Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str  = Field(min_length=6)
```

This is a normal pydantic model for helping us define how we shall create a new user account. It has the fields defined on the `User` database model necessary for creating user accounts.

Notice how we are using `Field` to add extra validation for fields such `max_length` and `min_length`. This class alows us to validate any data that shall come from a client. The `session` object

on the other hand is one created from the `get_session` dependency.

We then create a dictionary `new_user` from the `user_data` object. We then use that dictionary to create a new `User` object by unpacking its attributes as those for the user object. Netx we use the 

`session` to add it to the session and finally commit the session to save that to the database. Finally we return the newly created user object.


## Creating the Auth Router
After creating our `UserService`, we can now create an API endpoint to make use of this route. First we shall create a `routes.py` file and add the folowing code to it.

```python
from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException


auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data, session)

    return new_user

```

Inside this file, we create a router object called `auth_router` to help group all the routes that shall be related to the authentication. In addition to that, we shall also create the `user_service`
 to allow us access the methods we defined in the `UserService`object. We then create the endpoint for creating user accounts. Inside its handler, we shall access the user email and use it to check if the user with that email exists.

If the user does not exist, we shall raise an exception informing the user that an account has been created with trhe provided email. Just in case no account exists with that email, we proceed to save the object in the database.

Let us test this. In Insomnia, we shall make a request to the endpoint. 