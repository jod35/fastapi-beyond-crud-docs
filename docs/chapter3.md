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
| /customers/{customer_id} | PUT    | Update details of a specific customer by ID.   |
| /customers/{customer_id} | DELETE | Remove a customer using their ID.              |

The table above outlines various API endpoints, their corresponding HTTP methods, and their functionalities:

1. **`/customers` - GET: List all customers**
        - _Description:_ This endpoint retrieves information about all customers registered. When a client sends an HTTP GET request to `/customers`, the server responds with details of all customers.

2. **`/customers` - POST: Create a customer**
        - _Description:_ To add a new customer, clients can send an HTTP POST request to `/customers`. This operation involves creating and storing a new customer based on the data provided in the request body.

3. **`/customers/{customer_id}` - GET: Get a customer by ID**
        - _Description:_ By sending an HTTP GET request to `/customers/{customer_id}`, clients can retrieve detailed information about a specific customer. The `customer_id` parameter in the path specifies which customer to fetch.

4. **`/customers/{customer_id}` - PUT: Update a customer by ID**
        - _Description:_ To modify the information of a specific customer, clients can send an HTTP PUT request to `/customers/{customer_id}`. The `customer_id` parameter identifies the target customer, and the request body contains the updated data.

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
import sqlite3

def get_connection() -> sqlite3.Connection:
    """provide a connection to the db"""
    conn = sqlite3.connect("microfinance.sqlite3")
    conn.row_factory = sqlite3.Row
    return conn
```

The `get_connection` function opens a connection to the database file `microfinance.db` (it will be created on first use) and returns the connection object `conn` for later use.

We configure `conn` to return query rows as dictionaries so values can be accessed with `row["column"]`, we'll demonstrate this shortly.

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

If we restart the FastAPI server, SQLite will not create another database file. It will simply connect to the existing microfinance.sqlite3 file. Because we used CREATE TABLE IF NOT EXISTS, the customers table will also only be created if it doesn't already exist. This is one of the conveniences of SQLite: the database is just a file in our project directory, so we don't need to run a separate database server for our application.

Let us check the database we have created, I am going to be using a tool called [DB Browser For SQLite](https://sqlitebrowser.org/) to inspect our table as well to view the data we have stored in the tables. The following GIF shows how to open the database file in the app.



### Implementing the CRUD