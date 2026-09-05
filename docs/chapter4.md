# Large Project Structure Using Routers

### Current folder structure
So far, our project structure is quite simple:

```console title="Current Project structure"
.
├── database.py
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
├── schemas.py
└── uv.lock
```

All our API endpoints live in `main.py`, the database helper functions live in `database.py`, and the Pydantic models live in `schemas.py`.

### Current code structure
Additionally, our `main.py` file looks like this:

```python title="main.py"
import sqlite3

from fastapi import FastAPI, HTTPException, status
from database import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    init_db,
    list_all_customers,
    update_customer,
)
from schemas import Customer, CustomerCreate, CustomerUpdate

init_db()

app = FastAPI()


@app.get("/customers", status_code=status.HTTP_200_OK)
async def get_all_customers() -> list[Customer]:
    customers = list_all_customers()
    return [Customer(**x) for x in customers]


@app.post("/customers", status_code=status.HTTP_201_CREATED)
async def add_customer(create_data: CustomerCreate) -> Customer:
    data_dict = create_data.model_dump()
    try:
        customer_id = create_customer(data_dict)
    except sqlite3.IntegrityError:
        raise HTTPException(
            detail={"message": "A customer with that email, national id or phone number already exists"},
            status_code=status.HTTP_409_CONFLICT,
        )
    return Customer(**get_customer_by_id(customer_id))


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: int) -> Customer:
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Customer(**customer)


@app.patch("/customers/{customer_id}")
async def update_customer_partial(
    customer_id: int, update_data: CustomerUpdate
) -> Customer:
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    data_dict = update_data.model_dump()
    try:
        updated_customer = update_customer(customer_id, data_dict)

        return Customer(**updated_customer)
    except sqlite3.DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to update customer"},
        )


@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_customer(customer_id: int) -> None:
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    deleted = delete_customer(customer_id)

    if not deleted:
        raise HTTPException(
            detail={"message": "Failed to delete customer"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
```
## Restructuring the project

The problem here is that if we add more code to these files, our code will become messy and hard to maintain because related pieces of code will be scattered across a few large files at the root of our project. To address this, we need to create a more organized project structure. To start, let's create a new folder called `src`, which will contain an `__init__.py` file to make it a Python package:

```console title="creating the src directory"
.
├── database.py
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
├── schemas.py
├── src
│   └── __init__.py
└── uv.lock
```

Now, create three folders named `db`, `routes` and `schemas` inside the `src` directory. Inside each of these folders, add an `__init__.py` file. The `db` folder will contain all our database-related code. The `routes` folder will contain all the project routes. The `schemas` folder will contain the schemas (Pydantic models) that are currently in our root directory.

```console title="creating the new directory structure"
.
├── database.py
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
├── schemas.py
├── src
│   ├── __init__.py
│   ├── db
│   │   └── __init__.py
│   ├── routes
│   │   └── __init__.py
│   └── schemas
│       └── __init__.py
└── uv.lock
```

### Moving the database code into `src/db`

First, let's deal with `database.py`. We will split it into two modules inside the `db` folder:

- `setup.py` will hold the connection logic (`get_connection`) and the table creation logic (`init_db`).
- `customers.py` will hold all the CRUD functions that talk to the `customers` table.

We are simply relocating the code we wrote in the previous chapter, without changing any of it.

```python title="src/db/setup.py"
import os
import sqlite3

DB_PATH = os.environ.get("MICROFINANCE_DB", "microfinance.sqlite3")


def get_connection() -> sqlite3.Connection:
    """provide a connection to the db"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database by creating table"""
    conn = get_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER,
                first_name VARCHAR(25),
                surname VARCHAR(25),
                date_of_birth DATE,
                gender VARCHAR(10),
                email VARCHAR(30) UNIQUE,
                national_id VARCHAR(14) UNIQUE,
                phone_number VARCHAR(10) UNIQUE,
                status VARCHAR(10) DEFAULT 'inactive',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(id)
            );
        """)

        conn.commit()
    finally:
        conn.close()
```

Next, we move all the CRUD functions into `src/db/customers.py`. Again, the function bodies are exactly as they were in `database.py`. The only addition is the imports at the top. In particular, notice the line `from .setup import get_connection`: since `get_connection` now lives in a sibling module within the same package, we use a **relative import** (the leading dot refers to the current package, `src.db`) to bring it in.

```python title="src/db/customers.py"
import sqlite3
from datetime import datetime

from .setup import get_connection

UPDATEABLE_COLUMNS = {
    "first_name",
    "surname",
    "date_of_birth",
    "gender",
    "email",
    "national_id",
    "phone_number",
}


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def create_customer(data: dict) -> int:
    """Add a new customer."""

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO customers (
                first_name,
                surname,
                date_of_birth,
                gender,
                email,
                national_id,
                phone_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                data["first_name"],
                data["surname"],
                data["date_of_birth"],
                data["gender"],
                data.get("email"),
                data["national_id"],
                data["phone_number"],
            ),
        )

        conn.commit()

        return cursor.lastrowid
    finally:
        conn.close()


def list_all_customers() -> list[dict]:
    """List all customers."""

    conn = get_connection()
    try:
        cursor = conn.execute("SELECT * FROM customers;")

        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_customer_by_id(customer_id: int) -> dict | None:
    """Get a customer by their ID."""

    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM customers WHERE id = ?;",
            (customer_id,),
        )

        result = cursor.fetchone()
        return row_to_dict(result) if result is not None else None
    finally:
        conn.close()


def update_customer(customer_id: int, data: dict) -> dict | None:
    """Update a customer's information."""

    fields = {
        key: value
        for key, value in data.items()
        if key in UPDATEABLE_COLUMNS and value is not None
    }

    if not fields:
        return get_customer_by_id(customer_id)

    fields["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join(
        f"{key} = ?"
        for key in fields
    )

    values = tuple(fields.values()) + (customer_id,)

    conn = get_connection()
    try:
        conn.execute(
            f"UPDATE customers SET {set_clause} WHERE id = ?",
            values,
        )

        conn.commit()

        return get_customer_by_id(customer_id)
    finally:
        conn.close()


def delete_customer(customer_id: int) -> bool:
    """Delete a customer."""

    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM customers WHERE id = ?",
            (customer_id,),
        )

        conn.commit()

        return cursor.rowcount > 0
    finally:
        conn.close()
```

With the database code safely relocated, we can now delete `database.py` from the root of the project. Our structure now looks like this:

```console title="structure after moving the database code"
.
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
├── schemas.py
├── src
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   └── setup.py
│   ├── routes
│   │   └── __init__.py
│   └── schemas
│       └── __init__.py
└── uv.lock
```

### Moving the schemas into `src/schemas`

Next, let's move our Pydantic validation models from `schemas.py` to `customers.py` inside the `src/schemas` directory.

```python title="src/schemas/customers.py"
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    first_name: str
    surname: str
    email: str
    phone_number: str
    national_id: str
    gender: str
    date_of_birth: str


class Customer(CustomerCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    national_id: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
```

Each of the Pydantic models we shall create will be placed inside the `src/schemas` folder based on where it will be needed in the routes. We can now delete `schemas.py` from the root of the project.

### Moving the routes into `src/routes`

Finally, let's move all our API endpoints from `main.py` to `src/routes/customers.py`.

```python title="src/routes/customers.py"
import sqlite3

from fastapi import APIRouter, HTTPException, status

from src.db.customers import (
    create_customer, delete_customer,
    get_customer_by_id, list_all_customers,
    update_customer
)
from src.schemas.customers import Customer, CustomerCreate, CustomerUpdate

customer_router = APIRouter(prefix="/customers")


@customer_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_customers() -> list[Customer]:
    customers = list_all_customers()
    return [Customer(**x) for x in customers]


@customer_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_customer(create_data: CustomerCreate) -> Customer:
    data_dict = create_data.model_dump()
    try:
        customer_id = create_customer(data_dict)
    except sqlite3.IntegrityError:
        raise HTTPException(
            detail={
                "message": "A customer with that email, national id or phone number already exists"
            },
            status_code=status.HTTP_409_CONFLICT,
        )
    return Customer(**get_customer_by_id(customer_id))  # type: ignore


@customer_router.get("/{customer_id}")
async def get_customer(customer_id: int) -> Customer:
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Customer(**customer)


@customer_router.patch("/{customer_id}")
async def update_customer_partial(
    customer_id: int, update_data: CustomerUpdate
) -> Customer:
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    data_dict = update_data.model_dump()
    try:
        updated_customer = update_customer(customer_id, data_dict)

        return Customer(**updated_customer)  # type: ignore
    except sqlite3.DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to update customer"},
        ) from e


@customer_router.delete(
    "/{customer_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_customer(customer_id: int) -> None:
    customer = get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    deleted = delete_customer(customer_id)

    if not deleted:
        raise HTTPException(
            detail={"message": "Failed to delete customer"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
```

Not a lot has changed in this file; we just moved the code with customer API endpoints from `main.py` to `src/routes/customers.py`. Instead of importing the database functions from `database` and the schemas from `schemas`, we now import them from their new homes, `src.db.customers` and `src.schemas.customers`. Also, we are using a router object `customer_router` instead of the app instance we used earlier to define routes.

Routers in FastAPI can be thought of as mini `FastAPI` instances that help us modularize a FastAPI application by grouping related API endpoints together. All routers are created using the `APIRouter` class. This class has some similar attributes to the `FastAPI` class.

In this case, we are using one attribute on the router:

- `prefix`: A path that will be prepended to all the routes defined with this router. Because we passed `prefix="/customers"`, our route paths become shorter — `"/"` really means `/customers` and `"/{customer_id}"` means `/customers/{customer_id}`. This saves us from repeating `/customers` in every path.

We shall see another useful attribute, `tags`, in a moment.

### Updating `main.py`

Let's update our `main.py` file to adopt this modular structure:

```python title="Including the customer router in our app"

# Inside main.py
from fastapi import FastAPI

from src.db.setup import init_db
from src.routes.customers import customer_router

init_db()

app = FastAPI()

app.include_router(customer_router, tags=["customers"])
```

First, we import the `init_db` function from its new location in `src.db.setup` so the `customers` table is still created when the application starts. We then import the `customer_router` created in the previous section. Using our FastAPI instance, we include all endpoints created with the router by calling the `include_router` method.

Notice that we did not pass a `prefix` to `include_router` because the prefix is already defined on the router itself. We did, however, pass it a `tags` argument. Tags are used to group related endpoints together for documentation purposes (we shall explore this in much more detail later).

!!! note
    We can also define the prefix when including the router instead of on the router itself, and the result would be the same:

    ```python title="Defining the prefix on include_router"
    app.include_router(customer_router, prefix="/customers", tags=["customers"])
    ```

    Additionally, the `FastAPI` instance accepts arguments such as `title`, `description` and `version`. While these may not be particularly useful at present, they become valuable when we explore API documentation with **OpenAPI**.

Having moved our code, we shall now have this folder structure:

```console title="modified directory structure"
.
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   └── setup.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── customers.py
│   └── schemas
│       ├── __init__.py
│       └── customers.py
└── uv.lock
```

Once more, let's start our server using `uv run fastapi dev`. Nothing changes in how the API behaves. All the code we are going to write will now exist in the `src` directory. API endpoints will be grouped together based on their functionality in `src/routes`. Pydantic models will be placed in `src/schemas` based on where they will be used, and all database-related code will live in `src/db`.


!!! note

    The current organization of our API endpoints is as follows:

    | Endpoint             | Method | Description              |
    |----------------------|--------|--------------------------|
    | /customers           | GET    | Read all customers       |
    | /customers           | POST   | Create a customer        |
    | /customers/{customer_id} | GET    | Get a customer by ID     |
    | /customers/{customer_id} | PATCH  | Update a customer by ID  |
    | /customers/{customer_id} | DELETE | Delete a customer by ID  |


## Conclusion
This chapter has focused on creating a folder structure that we can use even when our project gets bigger. Our routes, schemas, and database code now each live in their own package under `src`. In the next chapter, we shall focus on databases, look at how we can persist our data, and use Python to manage both a relational and a non-relational database.
