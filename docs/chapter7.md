# Creating the User Authentication Model
Now that we have a working CRUD API, let's move on to more advanced topics. The first thing we need to tackle is figuring out who our users are and what they can do in the application. This breaks down into two main points:

- **Authentication**: Making sure users are who they say they are.
- **Authorization**: Deciding what actions users are allowed to take based on their identity.
 
## Creating the user account model
To achieve that, we shall begin by having a database model for keeping information about user accounts. Our current project structure looks like.
```console title="Current Project Structure"
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

```console title="Create the auth directory"
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

```python title="src/auth/models.py"
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


Most of the code here was explained in [Chapter 5](./chapter5.md), so I will only cover what is new.

- We created a database model called `User` with the table name `user_accounts`.
- The primary fields added include `uuid`, along with other fields such as `first_name`, `last_name`, `email`, `password_hash`, `created_at`, and `is_verified`.

- The `is_verified` field is necessary as it allows us to verify user-provided email addresses, ensuring we only deal with valid email addresses.

Once we have created this database model, let's save it and ensure the table is reflected in our database.

### Database Migrations with Alembic

Previously, we applied changes to the database using the lifespan event created in [Chapter 5](./chapter5.md). This method allowed us to create the table each time our server started, which was helpful during development. However, in a production environment, we need a proper database migration system to migrate changes to our database schema without restarting our server.

To achieve this, we will use [Alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool for use with SQLAlchemy. Since we are using SQLModel, which is based on SQLAlchemy, Alembic will be very useful.

Let's begin by installing Alembic in our virtual environment using `pip`:
```console title="Installling Alembic"
(env) $ pip install alembic
```

To confirm that Alembic has been installed, run the following command:
```console title="checking Alembic version"
(env) $ alembic --version
alembic 1.13.1
```

Alembic is installed and the version is `1.13.1`. Now, let's initialize Alembic in our project with this command:
```console title="Creating the migration environment"
(env) $ alembic init -t async migrations
  Creating directory '/home/jod35/Documents/fastapi-beyond-CRUD/migrations' ...  done
  Creating directory '/home/jod35/Documents/fastapi-beyond-CRUD/migrations/versions' ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/script.py.mako ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/env.py ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/alembic.ini ...  done
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/README ...  done
  Please edit configuration/connection/logging settings in '/home/jod35/Documents/fastapi-beyond-CRUD/alembic.ini' before proceeding.
```

The above command uses Alembic to create a **migration environment**. The migration environment, in this case, is the `migrations` folder added to our project directory. This folder and the `alembic.ini` file are generated by Alembic and form the migration environment.

We used the `-t` option to specify the template for setting up the environment. We chose the async template because our project uses an async DBAPI.

Now, our folder structure looks like this:
```console title="Current Project structure with migration environment"
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

The `migrations` directory contains the following:

- `versions/`: This folder will contain Python scripts created for each migration to track database changes.
- `env.py`: This script serves as the entry point for Alembic. When you run Alembic commands like `alembic init`, `alembic revision`, or `alembic upgrade`, this script executes the necessary actions.
- `README`: This file contains a description of the migration environment we have set up.
- `script.py.mako`: This is a template used by Alembic to create new Python migration scripts each time we create a new migration.



Sure, here is the rewritten text:

---

The `alembic.ini` file contains configurations for Alembic that enable it to interact with our database and project.

Now that we understand our migration environment, let's set up SQLModel to work with Alembic. We start by editing `migrations/env.py`:

```python title="migrations/env.py"
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

In this example, we import the `User` model we created in `/src/auth/models.py`. This is necessary because Alembic will automatically generate changes to the model. Additionally, we import the `SQLModel` class to access the `metadata` object, which Alembic uses to track changes to our database model using SQLModel.

Next, we edit the `migrations/script.py.mako` file to include SQLModel:

```python title="migrations/script.mako.py"
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

We then edit `alembic.ini` to specify the URL to the database we want to migrate:

```ini title="alembic.ini"
# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql+asyncpg://user:pswd@host/db # use the URL to your database
```

Having made these changes, let's create our first database migration. Our database currently contains only the `books` table. We'll create a migration to add the `user_accounts` table:

```console title="Creating our first Migration"
(env) $ alembic revision --autogenerate -m "init"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user_accounts'
  Generating /home/jod35/Documents/fastapi-beyond-CRUD/migrations/versions/8cf8276d5f3c_init.py ...  done
```

The newly created `migrations/versions/8cf8276d5f3c_init.py` file contains the following:

```python title="src/migrations/versions/8cf8276d5f3c_init.py"
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

This code includes:

- `revision`: The unique identifier for this migration.
- `down_revision`: The identifier of the previous migration, set to `None` for the initial migration.
- `branch_labels` and `depends_on`: Optional fields, set to `None`.

The `upgrade` function defines the changes to the database structure, creating the `user_accounts` table with specified columns. The `downgrade` function reverts these changes by dropping the `user_accounts` table if the migration is undone.

To apply these changes to the database, use the following command:

```console title="Apply migrations"
(env) $ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 8cf8276d5f3c, init
```

This command creates the `user_accounts` table in the database. To verify, list the tables in your current database:

```console title="Connecting to your PostgreSQL"
(env) $ psql --username=<your-username> --dbname=<your-db>
```

For example:

```console title="List table in database"
(env) $ psql --username=jod35 --dbname=books
psql (14.11 (Ubuntu 14.11-0ubuntu0.22.04.1))
Type "help" for help.

books=# \dt
            List of relations
 Schema |      Name       | Type  | Owner 
--------+-----------------+-------+-------
 public | alembic_version | table | jod35
 public | books           | table | jod35
 public | user_accounts   | table | jod35
(3 rows)
```

The `alembic_version` and `user_accounts` tables have been created. Let's examine their structures.

For `alembic_version`:

```console title="Structure of the alembic_version table"
books=# \d alembic_version
                    Table "public.alembic_version"
   Column    |         Type          | Collation | Nullable | Default 
-------------+-----------------------+-----------+----------+---------
 version_num | character varying(32) |           | not null | 
Indexes:
    "alembic_version_pkc" PRIMARY KEY, btree (version_num)
```

This table includes one column, `version_num`, which keeps records of the version numbers of changes made to the database structure.

For `user_accounts`:

```console title="Structure of the user accounts table"
books=# \d user_accounts
                         Table "public.user_accounts"
    Column     |            Type             | Collation | Nullable | Default 
---------------+-----------------------------+-----------+----------+---------
 uid           | uuid                        |           | not null | 
 username      | character varying           |           | not null | 
 first_name    | character varying           |           |          | 
 last_name     | character varying           |           |          | 
 is_verified   | boolean                     |           | not null | 
 email         | character varying           |           | not null | 
 password_hash | character varying           |           | not null | 
 created_at    | timestamp without time zone

```console
created_at    | timestamp without time zone |           |          | 
Indexes:
    "user_accounts_pkey" PRIMARY KEY, btree (uid)
```

Ladies and gentlemen, we have successfully created the `user_accounts` table from the `User` model. Now that we have done this, let us look at some ways to implement authentication in FastAPI.


## Conclusion
In this chapter, we have created a simple database model to enable us manage user accounts in our application. We have introduced Alembic, a database migration tool that runs on SQLAlchemy database models, allowing us to easily introduce changes to an existing database structure without haveing to delete data.

**Previous**: [Finishing Up the CRUD](./chapter6.md)

**Next**: [User Account Creation](./chapter8.md)
