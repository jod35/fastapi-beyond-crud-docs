# Chapter 2: Building Your First Web Server

## Introduction

With our environment prepared and FastAPI installed, it is time to breathe life into our project. In this chapter, we will transition from a static installation to a functional web service, exploring the core building blocks that make FastAPI so powerful and intuitive. 

At this stage, your project directory should look familiar. It contains the virtual environment we established and the foundational files created in the previous chapter:

```console title="Current directory structure"
.
├── .gitignore
├── main.py
├── pyproject.toml
├── .python-version
├── README.md
└── uv.lock
```

The heart of our application currently resides in `main.py`. Let's take a closer look at the code we’ve written so far:

```python title="main.py"
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def index() -> dict:
    return {"Hello": "World"}
```

Even in these few lines, several important things are happening. First, we import the `FastAPI` class, which serves as the main entry point to the framework. Think of this class as the orchestrator of your application through it, you'll define routes, register middleware, and manage how your server handles everything from basic requests to complex exceptions.

Next, we create an instance of this class and name it `app`. While you can technically name it anything, `app` is the industry standard and makes your code immediately recognizable to other developers.

Finally, we define our first API route by creating a Python function, `index`, and decorating it with `@app.get("/")`. This decorator tells FastAPI to execute the `index` function whenever someone visits the root URL with an HTTP GET request and return its result in this case, a simple JSON message.

```python title="Your first API endpoint"
@app.get("/")
def index() -> dict:
    return {"Hello": "World"}
```

FastAPI makes handling different types of interactions seamless. While we're using `get` here to retrieve data, the `@app` decorator supports all standard HTTP methods `post`, `put`, `delete`, `patch`, and more allowing you to build comprehensive, RESTful APIs with ease.

### Running the Application

To see our code in action, we return to the terminal. As we saw in the previous chapter, we can launch our server using the `uv` tool and the FastAPI CLI:

```console title="Running the server with the FastAPI CLI"
(env)$ uv run fastapi dev
```

The `fastapi dev` command is specifically designed for local development. It starts the server in a "hot-reload" mode, meaning it watches your files for changes. The moment you hit save on a file, the server automatically restarts to apply your updates, providing a smooth and efficient feedback loop. By default, it looks for common filenames like `main.py` or `app.py` to find your application instance.

Once the server is running, your application is live and waiting for requests at `http://localhost:8000`.

## Choosing an API Client

While you can visit your API in a web browser, a browser is limited in the types of requests it can make. To truly interact with and test your application, you will want a dedicated API client. 

While tools like [Postman](https://postman.com) and [Insomnia](https://insomnia.rest/) are widely used, [RestFox](https://github.com/flawiddsouza/Restfox/releases) stands out as an excellent open-source alternative. It operates entirely locally, ensuring your data stays on your machine without requiring a cloud account. Throughout this book, we will use RestFox to demonstrate how to test our endpoints.

Setting up your first request in RestFox is a straightforward process:

1. **Create a Request Collection**: This helps you organize your API calls into logical groups.
   ![Creating a request collection](./img/2026/create%20a%20workspace%20in%20restfox.png)

2. **Name Your Collection**: Give your project a clear, descriptive name.
   ![Naming the collection](./img/2026/new_workspace.png)

3. **Create an HTTP Request**: Add a new request to your collection.
   ![Creating an HTTP request](./img/2026/new_request.png)

4. **Execute the Request**: Enter the URL and hit "Send" to see your "Hello World" response.
   ![Making a request](./img/2026/first%20request.png)

With these simple steps, you have successfully verified that your server is running and responding as expected.

## Managing Requests and Responses

In a real-world application, a web server rarely just sends back static messages. It needs to receive data from users, process it, and respond accordingly. In FastAPI, there are several standard ways for a client to pass information to your API:

- **Path Parameters**: Data embedded directly in the URL structure.
- **Query Parameters**: Key-value pairs appended to the end of a URL.
- **Request Headers**: Metadata about the request, such as authentication tokens or content types.
- **Request Body**: Data sent as the payload of the request.


### The Importance of Type Declarations

One of FastAPI's most significant advantages is its deep integration with Python type hints. By declaring the types of your parameters, you allow FastAPI to handle data validation and documentation automatically. If you're unfamiliar with this modern Python feature, I recommend reviewing the [Python Type Hints](./type_hints.md) section carefully.

### Path Parameters

Path parameters allow you to make your URLs dynamic. For instance, instead of creating a separate route for every user, you can create a single route that accepts a "username" as part of the URL. In FastAPI, we denote these parameters using curly braces (`{}`).

```python title="path parameters"
#inside main.py
@app.get('/greet/{username}')
async def greet(username: str) -> dict:
   return {"message":f"Hello {username}"}
```

In this example, the `username` captured from the URL is passed directly into our `greet` function. Because we've annotated it as a `str`, FastAPI ensures that it is treated as a string throughout the function's execution.

![Greeting a User with a username](./img/2026/greet%20a%20user.png)

FastAPI is also smart enough to handle basic data conversion; any value provided in that segment of the URL will be automatically parsed according to your type definition.

![Path param converted to string](./img/2026/path%20param%20converted%20to%20a%20string.png)


#### Validating Path params
We can declare and validate path parameters in FastAPI using the `Path` function in FastAPI.

```py
from fastapi import Path

@app.get('/greet/{username}')
async def greet(username: str=Path(... ,max_length=100, min_length=2)) -> dict:
   return {"message":f"Hello {username}"}
```

The use of `...` specifies that the path parameter is always required. Unlike query parameters, path parameters cannot have default values.

The `Path` function accepts the following commonly used arguments:

- `gt, ge, lt, le`: numeric validations for numeric parameters
- `min_length` / `max_length`: string validations for string path parameters
- `title` / `description`: Used in OpenAPI documentation
- `pattern`: Regex pattern to match against the path parameter

For the complete list of parameters, refer to the [Path function API documentation](https://fastapi.tiangolo.com/reference/parameters/#fastapi.Path). 

### Query Parameters

Query parameters are the key-value pairs you often see at the end of a URL, following a question mark (`?`). They are ideal for optional data, such as search filters or pagination settings.

```python title="Query params"
# inside main.py
# .. more imports
from typing import Optional

user_list = [
   "Phil",
   "Jerry",
   "Joey",
]

@app.get("/search/")
def search(username:str) -> dict | None:
    message = f"user details for {username}" if username in user_list else "User not found"
    return {"message": message}
```

Notice that we didn't include `{username}` in the route path this time. In FastAPI, any function parameter that isn't part of the path is automatically treated as a query parameter. To use this endpoint, you would navigate to `/search?username=Jerry`.

![Searching for a user who exists](./img/2026/query%20param%20present2.png)

If the user isn't found, our logic handles it gracefully:

![Searching for a user who does not exist](./img/2026/not_found.png)

However, if you try to call this endpoint without providing a `username`, FastAPI returns a validation error because we haven't provided a default value, making the parameter required by default.

![Searching without the search query param](./img/2026/query%20param%20absent.png)

To make a parameter truly optional, provide a default value. By using Python's `Optional` type and assigning a fallback, you ensure your API remains robust even when certain data is missing.

```python title="Optional Query Params"
# ... more imports here
from typing import Optional
# ... some code here

@app.get("/search/")
def search(username: Optional[str] = "Jerry") -> dict:
    message = (
        f"user details for {username}" if username in user_list else "User not found"
    )
    return {"message": message}
```

Now, if a request arrives without a query string, the API will simply default to searching for "Jerry."

![Searching for a user without a query param](./img/2026/query%20param%20present3.png)

#### Refining Optional Parameters

The flexibility of FastAPI allows you to mix and match these approaches. You can even design routes that can handle a parameter as either a path element or a query string, depending on your architectural needs. Consider this alternate version of our greeting:

```python title="Optional Query Params"
from typing import Optional

@app.get('/greet/')
async def greet(username:Optional[str]="User") -> dict:
   return {"message":f"Hello {username}"}
```

By removing `{username}` from the route string and providing a default value in the function signature, we've transformed it. Now, `username` becomes an optional query parameter that defaults to "User" if not provided.

![Greeting a user with a username as a query param](./img/img17.png)

![Greeting with the default value of the username](./img/img18.png)

#### Validating Query Parameters
We can also validate query parameters FastAPI route handlers using FastAPI's `Query` function.

```py title="validating a username using the Query function"
from fastapi import Query

@app.get('/greet/')
async def greet(username: str = Query(default="User", min_length=2, max_length=100)) -> dict:
   return {"message":f"Hello {username}"}
```

The `Query` function accepts the following commonly used arguments:

- `default`: The default value if the query parameter isn't provided
- `min_length` / `max_length`: String length validations
- `le`, `lt`, `ge`, `gt`: Integer value validations
- `pattern`: Regex pattern to match against the query parameter
- `alias`: An alternative parameter name that can be used instead

For the complete list of parameters, refer to the [Query function API documentation](https://fastapi.tiangolo.com/reference/query/).

### The Request Body and Pydantic

As your application grows, you'll often need to send complex data structures to the server for example, when creating a new product or updating a user profile. While you could pass this data through query parameters, it quickly becomes difficult to manage. 

Instead, use a **Request Body**. FastAPI uses Pydantic to let you define exactly what your data should look like using simple Python classes.

```python title="Request Body"
# inside main.py
from pydantic import BaseModel

# the User model
class ProductSchema(BaseModel):
   name:str
   price:float
   description:str


@app.post("/create_product")
async def create_product(product_data:ProductSchema):
   new_product = {
      "name" : product_data.name,
      "price": product_data.price,
      "description" : product_data.description 
   }

   return new_product
```

In this example, we define a `ProductSchema` that inherits from Pydantic's `BaseModel`. This serves as a blueprint: any data sent to the `/create_product` endpoint *must* match this structure. 

```python title="A simple Pydantic model"
from pydantic import BaseModel

class ProductSchema(BaseModel):
    name: str
    price: float
    description: str
```

FastAPI handles the heavy lifting for you. It automatically parses the incoming JSON, validates the data types, and provides you with a clean Python object (`product_data`) to work with inside your function.

If a client sends an invalid request for example, by omitting the request body FastAPI automatically catches it.

![Making request without request body](./img/2026/send%20request%20body%20without%20body.png)

You’ll notice the server returns a `422 Unprocessable Entity` status. This isn't just a generic error; it’s a helpful signal that the data provided (or lack thereof) didn't meet the requirements of your schema. Similarly, if required fields are missing, FastAPI will pinpoint exactly what is wrong:

![Request with missing fields in post data](./img/2026/send%20request%20body%20with%20missing%20fields.png)

When the client provides valid data that matches our schema, everything works perfectly:

![Successful request with valid product data](./img/2026/send%20request%20body%20with%20valid%20product%20data.png)

#### Adding Values to Request Body Without Pydantic Models
By now, you understand that any parameter not defined in your path parameters is treated as a query parameter. Here's a simple example:


```python title="a param part of the request body"
from fastapi import Body

class ProductSchema(BaseModel):
    name: str
    price: float
    description: str

@app.post("/create_product")
async def create_product(product_data:ProductSchema, sku: str= Body(...)):
   new_product = {
      "name" : product_data.name,
      "price": product_data.price,
      "description" : product_data.description 
   }

   return {"product": product, "sku": sku}
```

But what if you want to include additional fields in the request body without adding them to the Pydantic model? That's where the `Body` function comes in. It allows you to include the `sku` field in the request body even if it's not part of your model.

When you send a request, the request body will include the `sku` field as shown below:
```json
{
  "product_data": {
    "name": "string",
    "price": 0,
    "description": "string"
  },
  "sku": "string"
}
```

The `Body` function can also be used for partial body extraction in situations where you may need to get individual fields without having a defined Pydantic model.

```python

@app.post('/create_product2')
async def create_product2(
   name: str=Body(..., embed=True),
   price: float=Body(..., embed=True),
   description: str=Body(..., embed=True),
   sku: str=Body(..., embed=True)
) -> dict:
   new_product = {
      "name" : name,
      "price": price,
      "description" : description,
      "sku": sku 
   }

   return {"product": new_product}
```

In this example, we're not defining the request body using a Pydantic model. Instead, we define individual fields that compose the complete request body, as shown below:

```json
{
  "name": "string",
  "price": 0,
  "description": "string",
  "sku": "string"
}
```

We're also using the `embed=True` argument, which tells FastAPI to expect these fields as top-level keys in the request body rather than nested values. This approach is useful when you have multiple individual request body parameters.

The `Body` function accepts the following commonly used arguments:

- `default`: A default value if the parameter is not provided
- `alias`: An alternative name for the field
- `media_type`: The media type (default is `application/json`)
- `embed`: If True, the field is embedded as a top-level key in the request body

For the complete list of parameters, refer to the [Body function API documentation](https://fastapi.tiangolo.com/reference/parameters/#fastapi.Body).

### Handling Form Data
At this point, we've only been handling requests with JSON data. However, many applications need to accept data from HTML forms, which are encoded as `application/x-www-form-urlencoded`. To handle this, we use the `Form` function, which works similarly to the `Body` function we saw earlier. Unlike `Body`, the `Form` function expects form-encoded data instead of JSON.

```python title="handling form encoded data"
from fastapi import Form


@app.post('/create_product2')
async def create_product2(
   name: str=Form(...),
   price: float=Form(...),
   description: str=Form(...),
   sku: str=Form(...)
) -> dict:
   new_product = {
      "name" : name,
      "price": price,
      "description" : description,
      "sku": sku 
   }

   return {"product": new_product}

```

It's worth noting that FastAPI does not allow validation of form-encoded data in Pydantic models. Instead, we must manually define validations on the fields as individual parameters in our route handlers.

The `Form` function accepts the following commonly used arguments:

- **default** - Default value if the parameter is not set. Use `...` for required fields
- **min_length** / **max_length** - String length validation
- **regex** - Regex pattern for string validation
- **title** - Short title for OpenAPI docs
- **description** - Human-readable description for OpenAPI docs

For the complete list of parameters, refer to the [Form function API documentation](https://fastapi.tiangolo.com/reference/parameters/#fastapi.Form).

### Handling Files
We can also write API endpoints that can handle file uploads using the `multipart/form-data` encoding tyoe. FastAPI provides two approaches for this.

### File Uploads 
#### The *File* function

For uploading small files which can easily load into memory, FastAPI provides the `File` function which allows us to load the file into memory like show in the example below.

```python title="uploading a file using the File function"
from fastapi import File

@app.post('/upload_file')
async def upload_file(file: bytes = File(...)) -> dict:
   return {"file_size": len(file)}
```

In the above example, the `File` function exposes the uploaded file as bytes, enabling us to show the amount of bytes the file has using the inbuilt `len` function.

The `File` function accepts the following commonly used arguments:

- `default`: Default value if the file parameter isn't provided
- `min_length`: Minimum file size in bytes
- `max_length`: Maximum file size in bytes
- `title`: Short title for OpenAPI docs
- `description`: Human-readable description for OpenAPI docs

For the complete list of parameters, refer to the [File function API documentation](https://fastapi.tiangolo.com/reference/parameters/#fastapi.File).

#### The *UploadFile* function
The *File* function can be just be enough to upload small files because by doing so, they will be loaded in memory, for larger uploads, the `UploadFile` is the way to go. 

The `UploadFile` function works differently from the `File` function. Instead of loading the entire file, it streams it and creates a file like Python object. The `UploadFile` function provides async capabilities making it better than the `File` function fo handling file uploads in FastAPI.

```python title="uploading a file using UploadFile"
from fastapi import UploadFile

@app.post('/upload_file')
async def upload_file(file: UploadFile) -> dict:
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }
```

When using `UploadFile`, FastAPI provides several attributes:

- **filename**: The name of the uploaded file
- **content_type**: The MIME type of the file (e.g., `image/png`, `application/pdf`)
- **file**: A file-like object that can be read and written to

#### Working with UploadFile Contents

To read the file contents, use the `read()` method:

```python title="reading file contents"
from fastapi import UploadFile

@app.post('/upload_file')
async def upload_file(file: UploadFile) -> dict:
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

#### Saving Uploaded Files

A common use case is saving uploaded files to disk:

```python title="saving uploaded files"
from fastapi import UploadFile
import shutil

@app.post('/upload_file')
async def upload_file(file: UploadFile) -> dict:
    save_path = f"uploads/{file.filename}"
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "saved_to": save_path}
```

The `shutil.copyfileobj()` method efficiently streams the file data without loading it entirely into memory, making it suitable for large files.

#### Multiple File Uploads

To accept multiple files, use a list of `UploadFile`:

```python title="uploading multiple files"
from fastapi import UploadFile
from typing import List

@app.post('/upload_files')
async def upload_files(files: List[UploadFile]) -> dict:
    results = []
    for file in files:
        contents = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(contents)
        })
    return {"files": results}
```

### Understanding Request Headers

Beyond the explicit data we send in the URL or the body, every HTTP request carries **Headers**. These provide essential context about the request's origin and preferences, such as:

- **User-Agent**: Identifies the client software making the request.
- **Host**: The domain name the client is reaching out to.
- **Accept-Language**: The user's preferred language for the response.
- **Authorization**: (Often used for security tokens, which we will cover later).

FastAPI makes accessing headers just as easy as any other parameter. Use the `Header` function to retrieve specific values, FastAPI automatically maps from HTTP kebab-case (like `User-Agent`) to Python snake_case (`user_agent`).

```python title="Request Headers"
# inside main.py
@app.get("/get_headers")
async def get_all_request_headers(
    user_agent: Optional[str] = Header(None),
    accept_encoding: Optional[str] = Header(None),
    referer: Optional[str] = Header(None),
    connection: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    host: Optional[str] = Header(None),
) -> dict:

    request_headers = {}
    request_headers["User-Agent"] = user_agent
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["Referer"] = referer
    request_headers["Accept-Language"] = accept_language
    request_headers["Connection"] = connection
    request_headers["Host"] = host

    return request_headers
```

Making a request to this route reveals the fascinating layer of metadata that travels with every click and API call.

![Response returning headers](./img/2026/get%20request%20headers.png)

### Handling Cookies

Cookies are small pieces of data stored in the browser that help maintain state across requests. FastAPI provides the `Cookie` function to read cookies from incoming requests.

```python title="Reading Cookies"
from fastapi import Cookie

@app.get("/read_cookies")
async def read_cookies(session_id: Optional[str] = Cookie(None)) -> dict:
    return {"session_id": session_id}
```

FastAPI automatically converts the kebab-case cookie names (like `session-id`) to snake_case Python variables (`session_id`).

#### Setting Cookies

To set cookies in a response, use FastAPI's `Response` class:

```python title="Setting Cookies"
from fastapi import Response

@app.get("/set_cookies")
async def set_cookies(response: Response) -> dict:
    response.set_cookie(key="session_id", value="abc123", httponly=True)
    return {"message": "Cookie set successfully"}
```

The `set_cookie` method accepts:

- `key`: The cookie name
- `value`: The cookie value
- `httponly`: Prevents JavaScript access (recommended for security)
- `secure`: Only sends cookie over HTTPS
- `samesite`: Controls cross-site request behavior (`strict`, `lax`, or `none`)
- `max_age`: Cookie expiration in seconds

For the complete list of parameters, refer to the [Cookie function API documentation](https://fastapi.tiangolo.com/reference/cookie/).

### The Request Object

Sometimes you need access to the raw request object itself perhaps to read raw body data, access client information, or handle advanced scenarios. FastAPI provides the `Request` object for this purpose.

```python title="Accessing the Request Object"
from fastapi import Request

@app.get("/request_info")
async def get_request_info(request: Request) -> dict:
    return {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
    }
```

The `Request` object provides access to:

- `url`: The full URL of the request
- `method`: The HTTP method (GET, POST, etc.)
- `headers`: Request headers as a dictionary
- `query_params`: Query parameters
- `path_params`: Path parameters
- `cookies`: Request cookies
- `client`: Client IP address and port
- `body()`: Raw request body as bytes
- `stream()`: Async generator for streaming body data

For the complete list of attributes and methods, refer to the [Request object API documentation](https://fastapi.tiangolo.com/reference/request/).

```python title="Accessing request body"
from fastapi import Request

@app.post("/raw_body")
async def get_raw_body(request: Request) -> dict:
    body = await request.body()
    return {"body_size": len(body)}
```

## Conclusion

In this chapter, we've moved beyond installation and built a functioning web server. We've explored the various ways clients can communicate with our API through path parameters, query strings, request bodies, and headers and seen how FastAPI uses Python type hints to make this communication safe and reliable.

In the next chapter, we'll take these concepts further and build a real-world application: a CRUD (Create, Read, Update, Delete) API for managing a bookstore, using an in-memory database to keep our focus on core web development logic.
