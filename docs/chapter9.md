# Authentication using JWTS

## Introduction

Now that we can create user accounts, let's build on that to allow users to log in and maintain a session in our application. While there are many approaches to authentication, we will focus on JWT (JSON Web Token) authentication in this chapter. JWTs are a mechanism for transferring claims (secret data) between parties. The claims in a JWT are encoded as a JSON object, which is used as a payload that can be signed, integrity protected, or encrypted.

### Basic structure of a JWT

A JWT shall have the following components;

1. **Header** : This contains the type of the JWT as well as the signing algorithm being used to create it. It will look like this

```js
{
  "alg": "HS256",
  "typ": "JWT"
}
```

2. **Payload**: This part contains the claims which are basically the data that we may want to keep about a specific entity. This can also be any additional data that we may want to encode.

```js
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

3. **Signature**: This part explains how the header, the payload were signed using the signing algorithm and the secret.

```js
HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret);
```

### How JWT Authentication works

1. **Client Authentication**: The client shall submit a payload with the user's email or password and when they are valid, the server shall genrate a JWT to send it to the client.

2. **Token Storage**: The client will store the token either in local storage or cookies.

3. **Subsequent Requests**: The client shall make requests to the server using the token inside the HTTP headers.

4. **Token Verification**: The server verifies the token's signature and validates its payload to ensure the token has not been tampered with and is still valid.

5. **Authorization**: If the token is valid, the server processes the request; otherwise, it rejects the request.

JWTs are compact, we can pass them in the request body, headers, and also via URLs. In addition, they are self contained and can contain all information we may wish them to have therefor, reducing on the number of times we query the database. They are secure and can also be used across many domains making them ideal for ditributed systems.

### Encoding and Decoding JWTs

#### Installing PyJWT

To implement JWT authentication, we shall make use of PyJWT, a library for encoding and decoding JWTs using Python. Let us begin by installing it with;

```console title="Installing PyJWT"
pip install pyjwt[crypto]
```

Note how we have included crypto, stading for the cryptography module.

#### Creating the Necessary functions

Inside our `auth` directory, we shall create move to the utils file where we create the functions for our password management. Inside `utils.py`, let us add the following code.

```py title="src/auth/utils.py"
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext
from src.config import Config



... #the password functions
def create_access_token(user_data: dict , expiry:timedelta =None, refresh: bool= False) -> str:
    payload = {
        'user':user_data,
        'exp': datetime.now() + (expiry if expiry is not None else timedelta(minutes=60)),
        'jti': str(uuid.uuid4()),
        'refresh' : refresh
    }


    token = jwt.encode(
        payload=payload,
        key= Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None

    except Exception as e:
        logging.exception(e)
        return None
```

We begin by importing necessary objects such as the `Config` object as well as PyJWT's `CryptContext`class. We also import PYJWT to allow us accss the functions necessary to encode and decode JWTs. We the create two functions.

1. The `create_access_token` function that shall help us create access or refresh tokens. Access tokens are going to be short lived and for security reasons we shall create long-lived refresh tokens to allow us create new access tokens once they are expired.

   ```py title="Encoding JWTS"
   def create_access_token(user_data: dict , expiry:timedelta =None, refresh: bool= False) -> str:
       payload = {
           'user':user_data,
           'exp': datetime.now() + (expiry if expiry is not None else timedelta(minutes=60)),
           'jti': str(uuid.uuid4()),
           'refresh' : refresh
       }


       token = jwt.encode(
           payload=payload,
           key= Config.JWT_SECRET,
           algorithm=Config.JWT_ALGORITHM
       )

       return token
   ```

The function has parameters, `user_data`, `expiry`, and `refresh`. `user_data` shall be all the data about the user to whom the token shall be issued. `expiry` shall be a datetime timedelta object that shall be used to create the expiry date of a token. We also have the `refresh` boolean that shall be used to mark a token as a refresh token or not.

We create a dictionary called `payload` to hold the neccessary claims that we want to encode the token. This contains the data about the user `user_data`, the expiry `exp`, the JWT ID `jti` and the refresh boolean`.

After doing this, our token shall be created by using the `encode` function from PyJWT. This function uses the payload, the key and the algoritm to encode the token. Note how we get the two from the `Config` object. To make these be accessed , we need to first update `src/config.py` to add the following.

```py title="Update the Config to add JWT secret and algorithm"
class Settings(BaseSettings):
    DATABASE_URL : str
    JWT_SECRET:str
    JWT_ALGORITHM:str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
```

We shall need to also modify our `.env` to have this

```console title="Adding JWT secret and algorithm to .env"
DATABASE_URL=postgresql+asyncpg://jod35:nathanoj35@localhost:5432/bookly_db
JWT_SECRET=e698218fbf1d9d46b06a6c1aa41b3124
JWT_ALGORITHM=HS256
```

Once we have created the token, we shall return it as shown above.

2. The `decode_token` is a function to help us decode the tokens and get the claims or data kept within them. It makes use of PyJWT's `decode` function to get the claims encoded in a token and handle potential exceptions that might occur during the decoding process.

```python
def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None

    except Exception as e:
        logging.exception(e)
        return None
```

It takes a JWT as a string `token` and attempts to decode it with a specified algorithm from the configuration `Config.JWT_ALGORITHM`. If the decoding process is successful, it returns a dictionary containing the decoded `token_data`. If a `jwt.PyJWTError` or any other exception occurs during the decoding process, the function logs the exception using the `logging.exception` method and returns `None`.

This ensures that any errors encountered while decoding the token are captured and logged, helping with debugging and preventing the application from crashing due to unhandled exceptions.

!!! Note
    Using `PyJWTError` is a very effective way of catching all exceptions that arise from PyJWT since it is the base class from which they are built.

### Creating the Login Endpoint

Now that we have an idea of how we shall create and decode tokens, let us build on top of this to create the login endpoint. This is going to follow the following steps;

1. **User Submission**: The user submits an email and password.
2. **Server Verification**: The server verifies if the user exists and their password matches the stored password hash in the database.
3. **Token Generation**:
   - If the verification is successful, an access token and a refresh token are granted to the user, allowing them to log in.
   - If the verification fails, an exception is raised to indicate that the provided credentials are invalid.

```python title="the login endpoint"
# src/auth/routes.py
from fastapi import APIRouter, Depends, status
from .schemas import UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, verify_password
from fastapi.responses import JSONResponse

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)}
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Or Password"
    )
```

This code defines an endpoint for user login. Using the `auth_router` object, we define the `login` path which we shall use for logging in users. The `login_users` function is handles POST requests to the /login endpoint. This function accepts `login_data`, which includes the user's email and password, and a `session` dependency session provided by `Depends(get_session)`.

Within the `login_users` function, the user's email and password are extracted from `login_data` which is an object from `UserLoginModel`.

```python title="The UserLoginModel"
# inside src/auth/routes.py
class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str  = Field(min_length=6)
```

The `user_service.get_user_by_email` function is then called to retrieve the user from the database using the provided email. If the user is found, the password provided is verified against the stored password hash using the `verify_password function`. If the password is valid, an `access_token` and a `refresh_token` are generated using the `create_access_token function`. The tokens and user information are returned in a JSON response indicating a successful login. If the user is not found or the password is invalid, an HTTP 403 Forbidden exception is raised, indicating that the email or password is incorrect.

Let us test this endpoint in Insomnia. Make a request with correct email and password.
![Successful Login](./img/img26.png)


Giving invalid credentials results into the following.
![Invalid Login](./img/img27.png)

### HTTP Bearer Authentication
Now that we can grant access tokens to users, we need to protect our API endpoints such that users require to provide access tokens to access them. This is where **HTTP Bearer Authentication** comes in. HTTP Bearer Authentication is an HTTP authentication scheme that involves security tokens called **Bearer Tokens**. This can be understood as "give accewss to the bearer of the token". Everytime a client is to make a request to a protected endpoint, they must send a string in form of
`Bearer <token>` in the request's `Authorization` header.

FastAPI comes really packed with many security classes that can allow for the implementation of different forms of Authentication such as Basic Authentication, OAuth2, OpenID Connect and HTTP Bearer. To use HTTPBearer Authentication, we shall make use of FastAPI's `HTTPBearer` class. THis is its definition.
```python title="The HTTPBearer class"
... # the rest of fastapi/security/http.py
class HTTPBearer(HTTPBase):
    def __init__(
        self,
        *,
        bearerFormat: Annotated[Optional[str], Doc("Bearer token format.")] = None,
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme name.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme description.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                By default, if the HTTP Bearer token not provided (in an
                `Authorization` header), `HTTPBearer` will automatically cancel the
                request and send the client an error.

                If `auto_error` is set to `False`, when the HTTP Bearer token
                is not available, instead of erroring out, the dependency result will
                be `None`.

                This is useful when you want to have optional authentication.

                It is also useful when you want to have authentication that can be
                provided in one of multiple optional ways (for example, in an HTTP
                Bearer token or in a cookie).
                """
            ),
        ] = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
```

The `HTTPBearer` class extends `HTTPBase` to provide HTTP Bearer token authentication. This class allows you to create an instance that can be used as a dependency via `Depends()`. When invoked, the dependency returns an `HTTPAuthorizationCredentials` object containing the authentication scheme and credentials. In the constructor, optional parameters such as bearerFormat, scheme_name, description, and auto_error are defined, allowing customization of the bearer token format, security scheme name, and description as shown in the generated OpenAPI documentation. The auto_error parameter determines whether an error is automatically raised if the token is not provided or invalid, enabling optional authentication if set to False.

The `__call__` method of the `HTTPBearer` class processes incoming requests by extracting the `Authorization` header and validating its content. It parses the header to separate the scheme and credentials, checking if they are present and if the scheme matches "bearer". If the token is missing or invalid, and auto_error is True, an HTTP 403 Forbidden exception is raised. If `auto_error` is False, the method returns None instead of raising an exception, allowing the endpoint to handle the absence of credentials gracefully. This functionality is particularly useful for endpoints that require optional or multiple methods of authentication.

Now that we have an understanding of this class, let us extend it to use it to protect  our API endpoints. To begin, we shall create a `dependencies.py` file inside the auth directory. 
```python title="dependencies.py"
from fastapi.security import HTTPBearer


class AccessTokenBearer(HTTPBearer):
    pass
```

By doing so, we have created the `AccessTokenBearer` class we are going to use  to create a dependency that we shall inject inside every path handler function that belongs to any endpoints that need protection. Let us start with the CRUD endpoints we created in the previous chapters.

```python title="src/books/routes.py"
from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from typing import List
from src.auth.dependencies import AccessTokenBearer


book_router = APIRouter()
book_service = BookService()
acccess_token_bearer = AccessTokenBearer()


@book_router.get("/", response_model=List[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books

... #rest of the code
```

In the code above, what we have done is to import the `AccessTokenBearer` class and create an object called `access_token_bearer` that we provide as a dependency to the path handler via `Depends()`. By doing that, we have protected an endpoints and made it a requirement for us to access it by using an `Authorization` Header in the request.

Making the request without the header being set results into the following. The user wont access the resources because they are not authenticated.
![Making request without Authorization header](./img/img28.png)

Providing the Authorization headers results into a successful response.
![Success request with Authorization  header](./img/img29.png)

While this is enough to add protection to API  endpoints, we may want to customize it by adding our own checks. Let us modify our `AccessTokenBearer` class to allow for those checks to be made. 

```python title="Modified AccessTokenBearer class"
# inside src/auth/dependendencies.py
class AccessTokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or expired",
                    "resolution":"Please get new token"
                }
            )
    

        return token_data

    def token_valid(self, token: str) -> bool:

        token_data = decode_token(token)

        return token_data is not None 
```

We begin by initializing the class with the `__init__` method, which accepts an optional `auto_error` parameter, defaulting to `True`, and passes this to the parent `HTTPBearer` class. The core functionality is in the `__call__` method, which makes instances of the class callable. This asynchronous method takes a `Request` object, extracts the authorization credentials by calling the `__call__` method of the parent class, and retrieves the token from these credentials.

Once the token is extracted, the `token_valid` method is invoked to verify the token's validity. This method attempts to decode the token using a `decode_token` function (that we defined in `src/auth/utils.py`). If `decode_token` successfully decodes the token, it returns some `token_data`; otherwise, it returns `None`. The `token_valid` method returns `True` if `token_data` is not `None`, indicating the token is valid, and `False` otherwise.

Back in the `__call__` method, if the token is found to be invalid, an `HTTPException` is raised with a status code of `403 Forbidden`, accompanied by a detailed message indicating that the token is invalid or expired and advising the user to obtain a new token. If the token is valid, the decoded token data is returned. This mechanism ensures that only requests with valid tokens are processed further, enhancing the security of the application by preventing unauthorized access.


We have now protected API Enpoints for CRUD on books so that they can only be accessed by providing a JWT in the Authorization header. Our routes for books should look like this.
```python title="Modified book API endpoints with HTTP Bearer Auth"
from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from typing import List
from src.auth.dependencies import AccessTokenBearer


book_router = APIRouter()
book_service = BookService()
acccess_token_bearer = AccessTokenBearer()


@book_router.get("/", response_model=List[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
):
    
    print(token_details)
    books = await book_service.get_all_books(session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
) -> dict:
    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.get("/{book_uid}", response_model=Book)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
) -> dict:

    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    else:
        return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acccess_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    else:

        return {}
```

### Renew User Access with Refresh Tokens
Now that we have implemented protection for our routes, we need to handle renewing user access by using refresh tokens. Refresh tokens are designed to be long-lived tokens that enable users to obtain new access tokens. Let's implement this functionality. To begin, we are going to refactor our dependencies so that we allow validation even for acess tokens.

```python title="modified dependencies"
from fastapi import Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or expired",
                    "resolution":"Please get new token"
                }
            )
    

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:

        token_data = decode_token(token)

        return token_data is not None 

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )

```

This code establishes a system for managing both access and refresh token authentication in a FastAPI application. It begins with the `TokenBearer` class, which extends the `HTTPBearer` class. The `TokenBearer` class overrides the `__call__` method to extract the token from incoming requests and decode it using the `decode_token` function. If the token is invalid, indicated by a failed decode, it raises an `HTTPException` with a `403 Forbidden` status. Additionally, the `verify_token_data` method is designed to be overridden by subclasses, enabling specific checks on the token data to ensure the token's purpose aligns with the request's requirements.

The system is further refined with two subclasses: `AccessTokenBearer` and `RefreshTokenBearer`. The `AccessTokenBearer` subclass overrides the `verify_token_data` method to ensure that the provided token is an access token. It does this by checking if the `refresh` field in the token data is `False`, raising an exception if it is a refresh token. On the other hand, the `RefreshTokenBearer` subclass ensures that the token is a refresh token by checking if the `refresh` field is `True`, raising an exception if it is not. This dual approach allows the application to handle authentication using both access and refresh tokens effectively, ensuring appropriate validation and error handling for each token type. 


With that out of the way, we can now creat the endpoint that will be used to generate new access tokens when a user provides a refresh token. Inside `src/auth/routes.py`, let us add the following code.
```python title="API path for creating new access tokens with a refresh token"
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Or expired token"
    )
```

This code defines an endpoint for obtaining a new access token using a refresh token in a FastAPI application. The endpoint is created at `/refresh_token` and is handled by the asynchronous function `get_new_access_token`. This function utilizes dependency injection with `Depends(RefreshTokenBearer())` to ensure that the request contains a valid refresh token. The `RefreshTokenBearer` class checks the token and returns its decoded data as `token_details`. Inside the function, the expiry timestamp is extracted from the token details, and a check is performed to determine if the refresh token is still valid by comparing the current time with the expiry timestamp. If the token is valid, a new access token is created using the `create_access_token` function, which takes user data from the refresh token, and a JSON response is returned containing the new access token.

If the refresh token is found to be invalid or expired, an `HTTPException` is raised with a status code of `400 Bad Request` and an appropriate error message. This endpoint ensures that users can obtain fresh access tokens without needing to re-authenticate, thereby maintaining secure user sessions. By validating the refresh token and generating a new access token only if the refresh token is valid and not expired, the application enhances security and user experience. This mechanism helps streamline the process of renewing user access while preventing unauthorized access with expired or invalid tokens.

### Revoking Tokens Using Redis
Now that we have granted users access using access tokens, we also need a way to invalidate these tokens when users log out. We will implement this using a token blocklist. A token blocklist will store information about revoked JWTs, ensuring that they cannot be used to access protected endpoints. 

There are many options available, but in our case, we will use Redis for this purpose. Redis will provide us with a key-value store that will be sufficient for implementing this functionality.

To use Redis with FastAPI, we are going to use Aioredis which is an asyncio based Python client for Redis. Through it, we shall get access to methods allowing us to interact with Redis using Python. So let us begin by installing it with;

```console title="Installing aioredis"
pip install aioredis
```

Once Aioredis has been installed, we are going to add this code to a new file called `src/db/redis.py`
```python title="Functions to handle token revoking"
# inside src/db/redis.py

import aioredis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blocklist(jti:str) -> bool:
   jti =  await token_blocklist.get(jti)

   return jti is not None
```



This code snippet sets up a token blocklist using Redis. It begins by importing the aioredis library, and configuration settings from the project's config module. A constant JTI_EXPIRY is defined to set the expiration time for blocklist entries to 3600 seconds (1 hour). The Redis client token_blocklist is initialized using aioredis.StrictRedis, connecting to the Redis server with the specified host, port, and database number (db=0).

The `add_jti_to_blocklist` function asynchronously adds a JWT ID (JTI) to the Redis blocklist, setting an expiration time for the entry. The `token_in_blocklist` function checks if a given JTI is in the blocklist by attempting to retrieve it from Redis; it returns `True` if the JTI is found and `False` otherwise. 

Once we have created these, we need to update our `TokenBearer` function to accomodate the checks for a token being in the token blocklist. 


```python title="Updated __call__ method"
from src.db.redis import token_in_blocklist

class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        # add this 
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "error":"This token is invalid or has been revoked",
                    "resolution":"Please get new token"
                }
            )
```

To implement the logout functionality by adding the token to the blocklist, we'll create the logout endpoint. This endpoint will ensure the token is not already in the blocklist before proceeding to block it.

```python title="the logout endpoint"
from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, verify_password
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer,AccessTokenBearer
from src.db.redis import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()


... #the rest of the code in src/auth/routes.py


@auth_router.get('/logout')
async def revoke_token(token_details:dict=Depends(AccessTokenBearer())):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )
```
The logout endpoint will be found on the `/logout` path. It is secured by the `AccessTokenBearer` class, which requires a valid access token for access. Upon receiving the token, we retrieve the relevant details `token_details` from the dependency and extract the token's JTI (JWT ID). We then call the `add_jti_to_blocklist` function to add this JTI to the blocklist in Redis. After successfully adding the JTI to the blocklist, we return a response indicating the success of the operation.


Let us test this out in the client. Let us begin by get a new token pair from the Login endpoint,
![Logging In to get new token](./img/img30.png)

Using the new access token, let us try to access the endpoint for listing all books.
![Listing all books with the new token](./img/img31.png)

Let us now revoke this token by accessing the token by using the logging endpoint.
![Logging Out](./img/img32.png)

Notice how this token cannot be used to list all books again. So this shows how revoked access tokens can not be used to access a protected endpoint.
![Protected endpoint](./img/img33.png)

## Conclusion
At this point, we have covered several key aspects of implementing JWT authentication in a FastAPI application. We started by granting users access using access tokens. We then explored protecting endpoints with HTTP Bearer Authentication, ensuring that users can only access them with valid tokens. Additionally, we implemented a way for users to renew their access tokens using refresh tokens when their current tokens expire. Finally, we demonstrated how to revoke tokens using Redis, preventing them from being used to access protected endpoints.

**Previous**: [Databases with SQLModel](./chapter5.md)

**Next**: [User Account Creation](./chapter8.md)