# Authentication using JWTS

## Introduction

Now that we can create user accounts, let us build on top of that to allow users to login or have a session in our application. While there are very many approaches to authentication we shall look at JWT Authentication in this chapter. JWTs stand for JSON Web Tokens, a mechanism for transferring claims (secret data) between parties. The claims in a JWT are encoded as a JSON object that is used as a payload that can be signed or integrity protected or encrypted.

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
    user_details=Depends(acccess_token_bearer),
):
    
    print(user_details)
    books = await book_service.get_all_books(session)
    return books

... #rest of the code
```

In the code above, what we have done is to import the `AccessTokenBearer` class and create an object called `access_token_bearer` that we provide as a dependency to the path handler via `Depends()`. By doing that, we have protected an endpoints and made it a requirement for us to access it by using an `Authorization` Header in the request.

Making the request without the header being set results into the following. The user wont access the resources because they are not authenticated.
![Making request without Authorization header](./img/img28.png)

Providing the Authorization headers results into a successful response.
![Success request with Authorization  header](./img/img29.png)

