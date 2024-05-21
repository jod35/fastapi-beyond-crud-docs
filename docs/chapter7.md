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

### Database migrations with Alembic
We have been applying our changes to the database with the lifespan event we created in [Chapter 5]('./chapter5'), and that was helpful as it allowed us to create the table each time our server started. In a production environment, we shall need to have a proper database migration system that shall enable us to migrate any changes to our database schema without having to restart our server. 

To achieve this, we are going to employ [Alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool for usage with SQLAlchemy. Since we are using SQLModel which is based on SQLAlchemy, this tool shall be of so much use.

Let us begin by installing it in our virtual environment with `pip`.
```console
(env) $ pip install alembic
```
To confirm that alembic has been installed, let us run the following command.
```console
(env) $ alembic --version
alembic 1.13.1
```

Alembic is installed and is version `1.13.1`. With that out of the way, let us go ahead to initialize alembic in our project with this command.

```console
(env) $ alembic init -t async migrations
  Creating directory '/home/jod35/Documents/fastapi-beyond-CRUD/migrations' ...  done
  Creating directory '/home/jod35/Documents/fastapi-beyond-CRUD/migrations/versions' ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/script.py.mako ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/env.py ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/alembic.ini ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/README ...  done
  Please edit configuration/connection/logging settings in '/home/jod35/Documents/fastapi-
  beyond-CRUD/alembic.ini' before proceeding.
```

What we have done in the above example is to use the alembic command to create a **migration environment**. The migration enviroment in our case is going to be the `migrations` folder that has been added to our project directory. This folder and the `alembic.ini` file, are generated by alembic and form the migration environment.

We have used the `-t` option to let alembic know the template we are to use to set up the environment. We have chosen the async template because our project is using an async DBAPI.

For now, our folder structure is going to look like this.
```console
├── alembic.ini
├── migrations
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
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

The `migrations` directory is going to contain the following
- `versions/`: Whenever we create a migration, Python scripts shall be created inside this folder to keep track of the database changes done for those migrations.
- `env.py` : The env.py script serves as the entry point for Alembic. When you run Alembic commands, such as alembic init, alembic revision, or alembic upgrade, it's this script that gets executed to perform the necessary actions.
- `README` : This file contains a descritive message about the migration environment we have set up.
- `script.py.mako` : This is a template used by Alembic to create new Python migration scripts everytime we create a new migration. 


The `alembic.ini` file contains configurations for Alembic that enable Alembic to interact with our database and project.

Now that we have an understanding of what our migration environment is, let us set up SQLModel to work with alembic. We are going to start by editing `migrations/env.py`
```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlmodel import SQLModel # new change
from src.auth.models import User # new change
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata # new change

... # the rest of env.py
```

What we have done in the above example is to import the `User` model we have created in `/src/auth/models.py`. We have done this becuase we shall Alembic to automatically generate changes to the model as we shall see in a moment. In addition to that, we have imported the `SQLModel` class from which we have accessed the `metadata` object. This is what alembic shall use to know any new changes that we shall make to our database model using SQLModel.

In addition to that, we are also going to edit the `migrations/script.py.mako` file to include SQLModel.
```console
# inside migrations/script.mako.py
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel # ADD THIS

...
```
Once we have done that, we can now edit `alembic.ini` to specify the URL to the database we want to make migrations on.
```
# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql+asyncpg://user:pswd@host/db #use the URL to your database

```
Having applied those changes, let us finally create our first database migration. For now our database shall contain only the `books` table. Let us create a migration to create the `user_accounts` table.
```
(env) $ alembic revision --autogenerate -m "init"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user_accounts'
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/versions/8cf8276d5f3c_init.py ...  done
```
When we check the newly created `migrations/versions/8cf8276d5f3c_init.py` file we shall see Alembic creating the table structure shown below.

```python
# inside src/migrations/versions/8cf8276d5f3c_init.py
"""init

Revision ID: 8cf8276d5f3c
Revises: 
Create Date: 2024-05-21 19:27:53.577277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8cf8276d5f3c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_accounts',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('uid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_accounts')
    # ### end Alembic commands ###
```




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