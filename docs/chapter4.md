# Large Project Structure Using Routers

### Current folder structure
So far, our project structure is quite simple:

```console title="Current Project structure"
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

### Current code structure
Additionally, our `main.py` file looks like this:

```python title="main.py"
# main.py
from enum import Enum

from fastapi import FastAPI, Header, status
from typing import Optional

from pydantic import BaseModel

app = FastAPI()


members: list["Member"] = []

class MemberStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class Member(BaseModel):
    id: int
    first_name: str
    last_name: str
    address: str
    phone_number: str
    national_id_number: str
    occupation: str
    status: MemberStatus
    group_id: Optional[int] = None


@app.get("/members", tags=["Members"])
def get_members() -> list[Member]:
    return members


@app.post("/members", status_code=status.HTTP_201_CREATED, tags=["Members"])
def create_member(member: Member) -> dict:
    members.append(member)
    return {"message": "Member created successfully", "member_id": member.id}


@app.get("/members/{member_id}", tags=["Members"])
def get_member(member_id: int) -> Member | dict:
    for member in members:
        if member.id == member_id:
            return member
    return {"message": "Member not found"}


@app.put("/members/{member_id}", tags=["Members"])
def update_member(member_id: int, updated_member: Member) -> dict:
    for index, member in enumerate(members):
        if member.id == member_id:
            members[index] = updated_member
            return {"message": "Member updated successfully", "member": updated_member}
    return {"message": "Member not found"}


@app.delete(
    "/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Members"]
)
def delete_member(member_id: int) -> None:
    for index, member in enumerate(members):
        if member.id == member_id:
            del members[index]
            return
    return {"message": "Member not found"}
```
## Restructuring the project

The problem here is that if we add more code to this file, our code will become messy and hard to maintain because all our code will be in one file, `main.py`. To address this, we need to create a more organized project structure. To start, let's create a new folder called `src`, which will contain an `__init__.py` file to make it a Python package:

```console title="creating the src directory"
├── main.py
├── pyproject.toml
├── README.md
├── src
│   └── __init__.py
└── uv.lock
```

Now, create two folders named `routes` and `schemas` inside the `src` directory. Inside each of these folders, add an `__init__.py` file. The `routes` folder will contain all the project routes. The `schemas` folder will contain the schemas (Pydantic models) that are currently in our root directory. 

```console title="creating the new directory structure"
├── main.py
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── routes
│   │   └── __init__.py
│   └── schemas
│       └── __init__.py
└── uv.lock
```

First, let's move all our API endpoints in `main.py` to `src/routes/members.py`.

```python title="src/routes/members.py"
# src/routes/members.py

from fastapi import APIRouter, Header, status
from src.schemas.members import Member

member_router = APIRouter(tags=["members"])


members: list["Member"] = []

@member_router.get("/")
def get_members() -> list[Member]:
    return members


@member_router.post("/", status_code=status.HTTP_201_CREATED)
def create_member(member: Member) -> dict:
    members.append(member)
    return {"message": "Member created successfully", "member_id": member.id}


@member_router.get("/{member_id}")
def get_member(member_id: int) -> Member | dict:
    for member in members:
        if member.id == member_id:
            return member
    return {"message": "Member not found"}


@member_router.put("/{member_id}")
def update_member(member_id: int, updated_member: Member) -> dict:
    for index, member in enumerate(members):
        if member.id == member_id:
            members[index] = updated_member
            return {"message": "Member updated successfully", "member": updated_member}
    return {"message": "Member not found"}


@member_router.delete(
    "/{member_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_member(member_id: int) -> None:
    for index, member in enumerate(members):
        if member.id == member_id:
            del members[index]
            return
    return {"message": "Member not found"}
```

Not a lot has changed in this file; we just moved the code with member API endpoints from `main.py` to `src/routes/members.py`. Also, we are using a router object `member_router` instead of the app instance we used earlier to define routes. 

Routers in FastAPI can be thought of as mini `FastAPI` instances that help us modularize a FastAPI application by grouping related API endpoints together. All routers are created using the `APIRouter` class. This class has some similar attributes to the `FastAPI` class. 

In this case, we are using the `tags` attribute on the router to define the tags for the routes. The `tags` attribute is used to group related endpoints together for documentation purposes (we shall explore this in much more detail later).

Next, let's also move our Pydantic validation models from `main.py` to the `members.py` module inside the `src/schemas` directory.

```python title="src/schemas/members.py"
# src/schemas/members.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class MemberStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class Member(BaseModel):
    id: int
    first_name: str
    last_name: str
    address: str
    phone_number: str
    national_id_number: str
    occupation: str
    status: MemberStatus
    group_id: Optional[int] = None

```

Each of the Pydantic models we shall create will be placed inside the `src/schemas` folder based on where it will be needed in the routes.

Let's update our `main.py` file to adopt this modular structure:

```python title="Including the book router to our app"

# Inside main.py title
from fastapi import FastAPI
from src.routes.members import member_router

app = FastAPI(
    title="SACCO Management System",
    description="A REST API for a SACCO management web service",
    version="1.0.0"
)

app.include_router(member_router, prefix="/members")
```

First, we import the `member_router` created in the previous example. Using our FastAPI instance, we include all endpoints created with it by calling the `include_router` method.

Arguments added to the FastAPI instance are:

- `title`: The title of the API.
- `description`: The description of the API.
- `version`  : The version of the API.

While these arguments may not be particularly useful at present, they become valuable when we explore API documentation with **OpenAPI**.

Furthermore, we added the following arguments to the `include_router` method:

- `prefix`: The path through which all related endpoints can be accessed. In our case, it's named the `/members` prefix, resulting in `/members`. This implies that all member-related endpoints can be accessed using `http://localhost:8000/members`.

!!! Note
    We can also add the `tags` argument to the `include_router` method to group related endpoints together for documentation purposes. For example, we can add the following argument to the `include_router` method:
    ```python title="Adding tags to the include_router method"
    app.include_router(member_router, prefix="/members", tags=["members"])
    ```

Having moved our code, we shall now have this folder structure:
```console title="modified directory structure"
├── main.py
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── members.py
│   └── schemas
│       ├── __init__.py
│       └── members.py
└── uv.lock
```

Once more, let's start our server using `uv run fastapi dev`. Nothing changes. All the code we are going to write will now exist in the `src` directory. API endpoints will be grouped together based on their functionality. Pydantic models will also be placed in `src/schemas` based on where they will be used.


!!! Note

    The current organization of our API endpoints is as follows:

    | Endpoint	| Method |	Description |
    |-----------|--------|--------------|
    | members |	GET  | Read all members |
    | members |	POST | Create a member |
    | members/{member_id} |	GET |	Get a member by ID |
    | members/{member_id} |	PATCH |	Update a member by ID |
    | members/{member_id} |	DELETE |	Delete a member by ID |


## Conclusion
This chapter has focused on creating a folder structure that we can use even when our project gets bigger. In the next chapter, we shall focus on databases, look at how we can persist our data, and use Python to manage both a relational and a non-relational database.


