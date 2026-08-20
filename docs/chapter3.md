# Building a CRUD REST API 

## Introduction

Having covered the fundamentals of FastAPI, we are now ready to take the next step and put what we have learned into practice by building a real-world application.

From this point onward, we will develop a RESTful API for a **Simple Microfinance Institution**. The application will model some of the core day-to-day operations of a microfinance institution, including customer management, loan applications, loan approvals, loan disbursements, and repayment collection.

In this chapter, we will begin laying the foundation for the system by focusing on **customer management**. We will implement the complete set of CRUD operations for managing customers, making this our first fully functional CRUD feature.


## What is CRUD?

CRUD stands for the four fundamental operations for data management:

- **Create (C):**
    - _Objective:_ To add new data.
    - _Action:_ Insert a new record or entity.

- **Read (R):**
    - _Objective:_ To retrieve existing data.
    - _Action:_ Fetch data without making any modifications.

- **Update (U):**
    - _Objective:_ To modify existing data.
    - _Action:_ Update attributes or values.

- **Delete (D):**
    - _Objective:_ To remove data.
    - _Action:_ Delete a record or entity.

CRUD operations are essential for data management and are commonly utilized in applications that handle data persistence. In **FastAPI Beyond CRUD**, we will focus on extending FastAPI's capabilities beyond standard CRUD applications, exploring advanced features and use cases. However, before going into these aspects, we will first create a simple CRUD API using FastAPI.

## A Simple CRUD API Implementation

Our CRUD API will feature several endpoints to perform CRUD operations on a basic SQLite database. Below is a list of the endpoints that we will implement in our CRUD API.

| Endpoint                 | Method | Description                                    |
| ------------------------ | ------ | ---------------------------------------------- |
| /customers               | GET    | List all customers.                            |
| /customers               | POST   | Create a new customer.                         |
| /customers/{customer_id} | GET    | Retrieve details of a specific customer by ID. |
| /customers/{customer_id} | PATCH  | Update details of a specific customer by ID.   |
| /customers/{customer_id} | DELETE | Remove a customer using their ID.              |

The table above outlines various API endpoints, their corresponding HTTP methods, and their functionalities:

1. **`/customers` - GET: List all customers**
        - _Description:_ This endpoint retrieves information about all customers registered. When a client sends an HTTP GET request to `/customers`, the server responds with details of all customers.

2. **`/customers` - POST: Create a customer**
        - _Description:_ To add a new customer, clients can send an HTTP POST request to `/customers`. This operation involves creating and storing a new customer based on the data provided in the request body.

3. **`/customers/{customer_id}` - GET: Get a customer by ID**
        - _Description:_ By sending an HTTP GET request to `/customers/{customer_id}`, clients can retrieve detailed information about a specific customer. The `customer_id` parameter in the path specifies which customer to fetch.

4. **`/customers/{customer_id}` - PATCH: Update a customer by ID**
        - _Description:_ To modify the information of a specific customer, clients can send an HTTP PATCH request to `/customers/{customer_id}`. The `customer_id` parameter identifies the target customer, and the request body contains the updated data. PATCH is used here because we only need to send the fields we want to change, rather than the entire customer record.

5. **`/customers/{customer_id}` - DELETE: Delete a customer by ID**
        - _Description:_ This endpoint allows clients to delete a specific customer. By sending an HTTP DELETE request to `/customers/{customer_id}`, the customer identified by `member_id` will be removed from the records.

With a clear plan for our simple API in place, we can now proceed to implement our CRUD API by integrating the functionalities outlined above into `main.py`. We will begin by creating simple list to serve as our in-memory database for customers.


## SQLite

SQLite is a compact, fast, self-contained, and highly reliable SQL database engine with a full set of features. Because it stores data in a single file and requires no server installation or complex configuration, SQLite is an excellent choice for applications where simplicity and portability matter such as mobile apps and other environments where managing a separate database server would be impractical.

If you’re not familiar with SQL (**Structured Query Language**), there’s no need to worry. We’ll learn the language as we build this API. For details on SQL as implemented in SQLite, [see the official documentation](https://sqlite.org/lang.html).

SQLite enjoys broad support across modern programming languages. In Python, the standard library includes the `sqlite3` module, which implements the DB-API interface for interacting with SQLite databases. For Python-specific usage, [see the `sqlite3` documentation](https://docs.python.org/3/library/sqlite3.html).

### Connecting to a Database
The very first thing we shall do here is to get rid of all code present in the `main.py` only keeping the `FastAPI` instance we created.

```python title="current main.py"
from fastapi import FastAPI

app = FastAPI()
```

Current folder structure should look like this. 
```title="current project structure"
.
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

We shall proceed to create a new file `database.py` add add the following code to it.

```python title="connecting to the database"
import os
import sqlite3

DB_PATH = os.environ.get("MICROFINANCE_DB", "microfinance.sqlite3")


def get_connection() -> sqlite3.Connection:
    """provide a connection to the db"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

The `get_connection` function opens a connection to the database file `microfinance.sqlite3` (it will be created on first use) and returns the connection object `conn` for later use.

We configure `conn` to return query rows as dictionaries so values can be accessed with `row["column"]`, we'll demonstrate this shortly.

Notice that instead of hardcoding the database filename inside the function, we define a module-level constant `DB_PATH`. We read it from the `MICROFINANCE_DB` environment variable using `os.environ.get()`. This allows us to point our application at a different database file without changing the code, for example when running tests against a temporary database. If the environment variable is not set, the default value `microfinance.sqlite3` is used.

This helper function will provide a reusable database connection that other parts of the application can call.

### Creating the `customers` Table

Next, we'll create a helper function to create our first table in the database.

In a relational database, **tables** are used to organize and store data. A table consists of **rows**, which represent individual records, and **columns**, which represent the different pieces of information, or attributes, that we want to store about those records.

Our goal is to create a table that looks like this:

![customers table](./img/2026/customer's%20table.png)

From the diagram above, we can summarize the structure of our `customers` table as follows:

| Column          | Description                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `id`            | A unique number used to identify each customer.                                                    |
| `first_name`    | The customer's first name.                                                                         |
| `surname`       | The customer's last name.                                                                          |
| `date_of_birth` | The date the customer was born.                                                                    |
| `gender`        | The customer's gender.                                                                             |
| `email`         | The customer's email address. Each customer must have a different email address.                   |
| `national_id`   | The customer's national identification number. Each customer must have a different one.            |
| `phone_number`  | The customer's phone number. Each customer must have a different number.                           |
| `status`        | Shows whether the customer's account is active or inactive. New customers are inactive by default. |
| `created_at`    | Records the date and time when the customer's information was first added to the database.         |
| `updated_at`    | Records the date and time when the customer's information was last updated.                        |

Let's add the following code to our `database.py`:

```python
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

#### Understanding the Function

The `init_db()` function is responsible for initializing our database. It uses the `get_connection()` helper we created earlier to establish a connection to our SQLite database file.

Once we have a connection, we use `conn.execute()` to send our SQL statement to SQLite.

The following part:

```sql
CREATE TABLE IF NOT EXISTS customers
```

tells SQLite to create a table called `customers` only if that table does not already exist.

This is useful because we can call `init_db()` multiple times without getting an error simply because the table has already been created.

#### Defining the Columns

Inside the `CREATE TABLE` statement, we define the columns that make up our `customers` table:

```text
id
first_name
surname
date_of_birth
gender
email
national_id
phone_number
status
created_at
updated_at
```

For each column, we specify a **data type**. The data type describes the kind of information that the column is intended to hold.

For example:

* `id` is an `INTEGER` because it contains a number.
* `first_name`, `surname`, `gender`, and `status` use `VARCHAR` because they contain text.
* `email`, `national_id`, and `phone_number` also use `VARCHAR` because they are stored as text rather than numbers.
* `date_of_birth` uses `DATE` because it represents a date.
* `created_at` and `updated_at` use `DATETIME` because they represent both a date and a time.

#### Constraints and Default Values

We also define some rules for our columns.

For example:

```sql
email VARCHAR(30) UNIQUE
```

The `UNIQUE` constraint tells SQLite that two customers cannot have the same email address.

We do the same for:

```sql
national_id VARCHAR(14) UNIQUE
phone_number VARCHAR(10) UNIQUE
```

This prevents two customers from being registered with the same national ID or phone number.

For the `status` column, we have:

```sql
status VARCHAR(10) DEFAULT 'inactive'
```

This means that if we create a customer without specifying a status, SQLite will automatically set the status to `inactive`.

Finally, we have:

```sql
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

`created_at` will automatically contain the current date and time when the record is created.

`updated_at` will also initially contain the current date and time. However, **SQLite will not automatically change `updated_at` when the customer is modified**. We will need to update this value ourselves when we update a customer's information.

#### Committing and Cleaning Up

After executing the `CREATE TABLE` statement, we call:

```python
conn.commit()
```

This commits the changes to the database.

We also use a `finally` block:

```python
finally:
    conn.close()
```

The `finally` block ensures that the database connection is closed after we're finished, even if something goes wrong while executing the SQL statement.


!!! note
    Although we write `VARCHAR(25)`, `VARCHAR(30)`, etc., SQLite does not enforce those character limits in the same way databases such as MySQL do. 
    The numbers are useful for documenting the intended size, but if you need SQLite to enforce a maximum length, you would need an additional constraint such as `CHECK(length(first_name) <= 25)`. We shall skip this for now.

#### Creating the table 
Now that we have created our init_db() function, we need to call it when our application starts. We can do this by importing the function into main.py and calling it just before creating our FastAPI application instance.

```python title="add the init_db function"
from fastapi import FastAPI
from database import init_db

init_db()

app = FastAPI()
```
When `init_db()` is called, it uses our `get_connection()` helper to connect to `microfinance.sqlite3` and create the `customers` table if it does not already exist.

If the database file does not exist, SQLite will create it automatically when we establish the connection. Our project structure will then look something like this:

```title="current folder structure"
.
├── database.py
├── main.py
├── microfinance.sqlite3
├── pyproject.toml
├── README.md
└── uv.lock
```

If we restart the FastAPI server, SQLite will not create another database file. It will simply connect to the existing microfinance.sqlite3 file. Because we used `CREATE TABLE IF NOT EXISTS`, the customers table will also only be created if it doesn't already exist. This is one of the conveniences of SQLite: the database is just a file in our project directory, so we don't need to run a separate database server for our application.

Let us check the database we have created, I am going to be using a tool called [DB Browser For SQLite](https://sqlitebrowser.org/) to inspect our table as well to view the data we have stored in the tables. The following GIF shows how to open the database file in the app.


### Implementing the CRUD

Now that we have set up our database, we can proceed to implement the CRUD operations. All the following functions will be added to `database.py`, after the `get_connection()` and `init_db()` functions.

#### Create a Customer

```python title="create a customer"
# inside database.py

# ... more code here

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
```

The `create_customer()` function is responsible for adding a new customer to the `customers` table. It accepts a dictionary called `data`, which contains the information needed to create the customer. For example, the data might look like this:

```python
data = {
    "first_name": "John",
    "surname": "Doe",
    "date_of_birth": "1995-05-20",
    "national_id": "CM123456789",
    "phone_number": "0700000000",
    "gender": "Male",
    "email": "john@example.com",
}
```

The function uses our `get_connection()` helper to connect to the database. It then uses the connection to execute an `INSERT` statement.

```sql title="the SQL statement" 
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
```

The `INSERT INTO` statement tells SQLite that we want to add a new record to the `customers` table. We specify the columns we want to add values to and then provide a corresponding placeholder for each value. The `?` characters are called **placeholders**. The actual values are passed separately as a tuple:

```python 
(
    data["first_name"],
    data["surname"],
    data["date_of_birth"],
    data["gender"],
    data.get("email"),
    data["national_id"],
    data["phone_number"],
)
```

The values are matched with the placeholders in the same order in which they appear. Using placeholders keeps the SQL statement separate from the data being inserted and helps protect our application against SQL injection.

Using `data.get("email")`  instead of `data["email"]` allows the email address to be optional. If the `email` key is not present in the dictionary, `.get()` returns `None`, which SQLite stores as `NULL`. After the query has been executed, we call `conn.commit()`.This saves the new customer record to the database.

Finally, we return `cursor.lastrowid` which contains the ID assigned to the customer we just created. We can use this ID later to retrieve the newly created customer or perform other operations on that specific record.

Notice that the entire operation is wrapped in a `try`/`finally` block. The `finally` block calls `conn.close()` to close the database connection. This ensures that the connection is always released, even if an error occurs while inserting the customer, preventing the application from leaking database connections.

Now let's implement the remaining CRUD functions. To keep things consistent, each of them will follow the same pattern: obtain a connection with `get_connection()`, run the query inside a `try` block, and always close the connection in a `finally` block. 

#### List Customers

```python title="list all customers"
def list_all_customers() -> list[dict]:
    """List all customers."""

    conn = get_connection()
    try:
        cursor = conn.execute("SELECT * FROM customers;")

        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

The `list_all_customers()` function is responsible for retrieving all customers from the `customers` table. It uses the `get_connection()` helper to connect to the database and executes the following `SELECT` statement:

```sql title="the SQL statement"
SELECT * FROM customers;
```
The `SELECT *` statement tells SQLite to retrieve all the columns from the `customers` table.

After executing the query, we call `cursor.fetchall()` which retrieves all the rows returned by the query. Since SQLite returns each row as a `sqlite3.Row` object, we use our `row_to_dict()` helper to convert each row into a regular Python dictionary.

```python
[row_to_dict(row) for row in cursor.fetchall()]
```
The function finally returns a list containing all the customers. As before, the `finally` block ensures the connection is closed once we are done.

#### Get a Customer by ID

```python title="get a customer by ID"
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
```

The `get_customer_by_id()` function is responsible for retrieving a single customer using their ID. It accepts a `customer_id` and uses it to search for a matching record in the `customers` table.

```sql title="the SQL statement"
SELECT * FROM customers WHERE id = ?;
```

The `WHERE` clause tells SQLite to return only the customer whose `id` matches the value we provide. The `?` is a placeholder, and the value for it is passed separately `(customer_id,)`.

Notice the comma after `customer_id`. This is required because Python needs the value to be a tuple containing one item.
After executing the query, we call `cursor.fetchone()`  which will retrieve the first matching row. Since `id` is the primary key, there can only be one customer with a particular ID.

The row is then passed to `row_to_dict()`. If a matching customer exists, the function returns a dictionary containing their information. If no customer is found, `fetchone()` returns `None`, and the function returns `None` as well. We use a conditional expression to guard against calling `row_to_dict()` with `None`:

```python
return row_to_dict(result) if result is not None else None
```

This way the caller can easily tell whether a customer exists or not. The `finally` block closes the connection regardless of the outcome.


#### Update a Customer

```python title="update a customer"
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
```

Before we explain this function, we need to add one more piece of setup to `database.py`. Because the `SET` clause is built dynamically from the keys in the `data` dictionary, we want to make sure only the columns we actually allow to be updated ever end up in our SQL. We do this by defining a constant with the names of the updateable columns, right at the top of `database.py`, next to `DB_PATH`:

```python title="defining the updateable columns"
UPDATEABLE_COLUMNS = {
    "first_name",
    "surname",
    "date_of_birth",
    "gender",
    "email",
    "national_id",
    "phone_number",
}
```

The `update_customer()` function is responsible for updating an existing customer's information. It accepts the ID of the customer we want to update and a dictionary containing the new values. The first step is to remove fields whose values are `None` and that are not in our whitelist:

```python
fields = {
    key: value
    for key, value in data.items()
    if key in UPDATEABLE_COLUMNS and value is not None
}
```

The `key in UPDATEABLE_COLUMNS` check restricts the update to columns we explicitly allow, protecting the query from SQL injection by ensuring arbitrary column names can never be placed in the `SET` clause. Combined with the `value is not None` check, this allows us to update only the values that were actually provided. For example, if we only provide a new phone number, the other customer details will remain unchanged. If there are no fields to update, the function simply returns the current customer without making any changes.

Next, we update the `updated_at` field with the current date and time:

```python
fields["updated_at"] = datetime.now().isoformat()
```

The function then dynamically creates the `SET` part of the SQL statement. For example, if we are updating the customer's `first_name` and `phone_number`, the resulting query would look like this:

```sql
UPDATE customers
SET first_name = ?, phone_number = ?, updated_at = ?
WHERE id = ?;
```

The values are passed separately and matched with the placeholders in the same order and after the update is executed, we commit the changes:

```python
conn.commit()
```

Finally, the function retrieves the customer again using `get_customer_by_id()` and returns the updated record. Just like the other functions, the update runs inside a `try` block and the connection is closed in a `finally` block.


#### Delete a Customer

```python title="delete a customer"
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

The `delete_customer()` function is responsible for removing a customer from the `customers` table. It accepts the ID of the customer we want to delete and executes the following SQL statement:

```sql title="the SQL statement"
DELETE FROM customers WHERE id = ?;
```

The `DELETE FROM` statement tells SQLite to remove a record from the `customers` table, while the `WHERE` clause ensures that only the customer with the specified ID is deleted. The customer ID is passed separately as a tuple. After executing the query, we commit the changes to the database:

Finally, the function checks:

```python
cursor.rowcount > 0
```

`rowcount` tells us how many rows were affected by the query. If at least one row was deleted, the expression returns `True`. If no customer with the given ID was found, it returns `False`.

This gives the rest of our application a simple way to determine whether the customer was successfully deleted.

Now that our database layer is complete, we can expose these functions through HTTP endpoints. But before we write the endpoints, we need to define the **schemas** that will describe the shape of the data our API accepts and returns.

## Defining Validation Schemas

FastAPI uses Pydantic models to validate the data that comes into our API and to shape the data that goes out. We will keep all our schemas in a new file called `schemas.py`:

```python title="schemas.py"
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

We define three models here, each serving a different purpose:

1. **`CustomerCreate`** is the schema we use when a client wants to create a new customer. It contains exactly the fields the client is expected to provide. If any of these fields are missing or of the wrong type, FastAPI will automatically respond with a `422 Unprocessable Entity` error.

2. **`Customer`** is the schema we use when sending customer data back to the client. It extends `CustomerCreate` (notice the inheritance) and adds the fields that the database manages for us: the `id`, the `status`, and the `created_at` and `updated_at` timestamps. This way, when we create a customer, the response contains everything about the newly created record, including the ID we need to reference it later.

3. **`CustomerUpdate`** is the schema we use for updating a customer. Every field is `Optional` and defaults to `None`. This means a client can send only the fields they want to change. Fields that are not sent simply stay `None` and are ignored by our `update_customer()` function. This is what makes partial updates with `PATCH` possible.

## Implementing the API Endpoints

With our schemas in place, we can now wire everything together in `main.py`. The complete file looks like this:

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

At the top, we import the CRUD functions from `database.py`, the schemas from `schemas.py`, and the `HTTPException` and `status` utilities from FastAPI. We call `init_db()` so the `customers` table is created when the application starts, before we create our `app`.

You will also notice that every error we raise uses the same shape:

```python
detail={"message": "..."}
```

Keeping a consistent error format makes it much easier for frontend clients to handle failures, because they can always expect the message to live under the `message` key.

Let us now go through each endpoint:

### List All Customers

```python
@app.get("/customers", status_code=status.HTTP_200_OK)
async def get_all_customers() -> list[Customer]:
    customers = list_all_customers()
    return [Customer(**x) for x in customers]
```

The `get_all_customers()` endpoint handles the **GET** request to `/customers`. It calls our `list_all_customers()` function to fetch every customer from the database. Since the database returns a list of dictionaries, we convert each dictionary into a `Customer` model using the `**` unpacking operator and `Customer(**x)`. This tells Pydantic to read the keys of the dictionary as the fields of the model. The endpoint returns a list of `Customer` objects, which FastAPI serializes into JSON.

### Create a Customer

```python
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
```

The `add_customer()` endpoint handles the **POST** request to `/customers`. FastAPI validates the request body against the `CustomerCreate` schema and gives us a `create_data` object. We convert it into a dictionary with `create_data.model_dump()` so we can pass it to our `create_customer()` database function.

Remember that `email`, `national_id`, and `phone_number` are all `UNIQUE` columns in the database. If a client tries to create a customer with a value that already exists, SQLite raises a `sqlite3.IntegrityError`. We catch this specific exception and respond with a `409 Conflict` status code and a friendly message instead of exposing the raw database error.

!!! note
    A `409 Conflict` status code is the correct response when a request conflicts with the current state of the resource, such as trying to register a duplicate email. This is different from a `400 Bad Request`, which is meant for requests that are malformed in general.

When the insert succeeds, we look up the newly created customer with `get_customer_by_id(customer_id)` using the ID that SQLite assigned. We convert it to a `Customer` and return it with a `201 Created` status code. Notice that the response now includes the `id`, the `status`, and the timestamps, so the client immediately knows the details of the record it just created.

### Get a Customer by ID

```python
@app.get("/customers/{customer_id}")
async def get_customer(customer_id: int) -> Customer:
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(
            detail={"message": "Customer not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Customer(**customer)
```

The `get_customer()` endpoint handles the **GET** request to `/customers/{customer_id}`. The `{customer_id}` part of the path is a **path parameter**, and because we annotate it as an `int`, FastAPI will convert it to an integer for us and return a `422` error if it is not a valid number.

We then call `get_customer_by_id()` with that ID. If no customer is found, the function returns `None` and we raise an `HTTPException` with a `404 Not Found` status code. Otherwise, we convert the returned dictionary into a `Customer` and send it back.

### Update a Customer

```python
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
```

The `update_customer_partial()` endpoint handles the **PATCH** request to `/customers/{customer_id}`. We first check that the customer exists, returning a `404` if it does not. The request body is validated against `CustomerUpdate`, which means every field is optional, so a client can send just the fields they want to change.

After the update runs, we return the updated customer. If anything goes wrong at the database level, we catch the `sqlite3.DatabaseError` and respond with a `500 Internal Server Error` and a generic message rather than leaking the underlying exception details.

!!! note
    We use **PATCH** instead of **PUT** because PATCH is meant for partial updates. With PUT, a client is expected to send the entire resource; with PATCH, only the fields being changed. This matches our `CustomerUpdate` schema, where every field is optional.

### Delete a Customer

```python
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

Finally, the `remove_customer()` endpoint handles the **DELETE** request to `/customers/{customer_id}`. As before, we return a `404` if the customer does not exist. We then call `delete_customer()`, which returns `True` if a row was removed. A successful delete responds with a `204 No Content` status code, meaning the operation succeeded but there is no body to return. If for some reason the deletion did not happen, we respond with a `500` error.

With that, we have a fully functional CRUD API backed by SQLite. Our endpoints are now consistent, handle errors gracefully, and always return the full customer record when creating or updating. In the next chapter, we will look at how to organize this growing codebase using routers.
