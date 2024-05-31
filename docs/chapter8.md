## Implementing JWT Authentication
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
    └── __init__.py
```


Let us begin by creating `src/auth/routes.py` and adding the folowing code to it.
```python
# inside src/auth/routes.py
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.schemas import UserCreationModel
from src.auth.service import UserService


auth_router = APIRouter()

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreationModel, session: AsyncSession = Depends(get_session)
):

    username = user_data.username
    email = user_data.email
    password = user_data.password

    user = await UserService(session).get_user(email)

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "User Account Already Exists"},
        )
    else:
        new_user = await UserService(session).create_user(user_data)
        return {"message": "User Created successfully"}
```

