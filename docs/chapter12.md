# Error Handling in FastAPI

At this point, you are probably familiar with the concept of error handling as we have used it in previous chapters. We have been using the built-in `HTTPException` class to raise exceptions within our application. While `HTTPException` is useful for general errors, there may be situations where we need to handle errors specific to the functionalities of our application. In such cases, creating custom error classes can provide more specific and easy-to-document error handling. In this chapter, we will explore how to create custom error-handling for our application to manage errors more effectively.

## The FastAPI `HTTPException` Class

The `HTTPException` class in FastAPI is an excellent tool for raising exceptions by creating a JSON response with the appropriate status code and message. It also allows us to provide headers for the response. Here's a simple example of how it works:

```python title="A simple use of the HTTPException"
if not tag:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Tag does not exist"
    )
```

In this example, if the `tag` variable is `None`, an `HTTPException` is raised with a `404 Not Found` status code and a custom error message.

While this method is sufficient for most cases, there are situations where we may want to provide more details about what caused the error and what users can do to resolve it. This is where custom error handling comes into play.

## Creating Custom Exceptions

To implement custom error-handling, we will create exception classes and handlers that return JSON responses with detailed information about the exceptions. Start by creating a file named `errors.py` in the `src` directory. Inside `errors.py`, add the following code:

```python title="custom exception classes"
class BooklyException(Exception):
    """This is the base class for all bookly errors"""
    pass

class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is needed"""
    pass

class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is needed"""
    pass

class UserAlreadyExists(BooklyException):
    """User has provided an email for a user who exists during sign up."""
    pass

class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during log in."""
    pass

class InsufficientPermission(BooklyException):
    """User does not have the necessary permissions to perform an action."""
    pass

class BookNotFound(BooklyException):
    """Book Not found"""
    pass

class TagNotFound(BooklyException):
    """Tag Not found"""
    pass

class TagAlreadyExists(BooklyException):
    """Tag already exists"""
    pass

class UserNotFound(BooklyException):
    """User Not found"""
    pass
```

### Exception Classes and Their Descriptions

Each exception class in our application handles a specific type of error. Here’s a table summarizing the exceptions and their descriptions:

| Exception Class          | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| `BooklyException`        | This is the base class for all Bookly errors                  |
| `InvalidToken`           | User has provided an invalid or expired token                 |
| `RevokedToken`           | User has provided a token that has been revoked               |
| `AccessTokenRequired`    | User has provided a refresh token when an access token is needed |
| `RefreshTokenRequired`   | User has provided an access token when a refresh token is needed |
| `UserAlreadyExists`      | User has provided an email for a user who exists during sign up |
| `InvalidCredentials`     | User has provided wrong email or password during log in       |
| `InsufficientPermission` | User does not have the necessary permissions to perform an action |
| `BookNotFound`           | Book Not found                                                |
| `TagNotFound`            | Tag Not found                                                 |
| `TagAlreadyExists`       | Tag already exists                                            |
| `UserNotFound`           | User Not found                                                |

## Creating Error Handlers

Each exception class, when handled, will be raised when a specific error has been encountered within the application. To manage these errors effectively, we need to create error-handler functions for each exception. Manually creating these functions can be repetitive and time-consuming. To streamline this process, we can use a function that dynamically creates error-handlers, making our code cleaner and easier to maintain.

```python title="function to create error-handlers"
def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BooklyException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler
```

The `create_exception_handler` function helps us generate custom error handlers quickly. It takes two parameters: `status_code` and `initial_detail`. The `status_code` parameter is the HTTP status code that will be returned when the error occurs. The `initial_detail` parameter contains the message or content to include in the JSON response.

Within `create_exception_handler`, we define an inner function called `exception_handler`. This function handles our custom exceptions. It takes two parameters: `request`, which is an instance of `Request` from FastAPI, and `exc`, which is the exception instance. The `exception_handler` function returns a `JSONResponse` with the specified `status_code` and `initial_detail`.

The outer function, `create_exception_handler`, returns the inner `exception_handler` function. This allows us to easily create specific handlers for different exceptions by calling `create_exception_handler` with the appropriate arguments.

## Registering Error Handlers

To use this function, we can define error handlers for each custom exception by passing the relevant status code and error details. Each handler will return a consistent and informative JSON response, ensuring that each error type is managed properly. We wrap all error handlers in the `register_error_handlers` function which takes in the FastAPI `app` instance we may want to register exception handlers.

```python title="using custom error handlers"
from fastapi import FastAPI

... # rest of the file
def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Tag Not Found", "error_code": "tag_not_found"},
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Tag Already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book Not Found",
                "error_code": "book_not_found",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
```
By using the `create_exception_handler` function, we can maintain a cleaner and more manageable codebase. This approach simplifies the process of handling various exceptions and ensures that our application provides clear and helpful error messages to the users.

To make this work, we shall call the `register_error_handlers` function inside `src/__init__.py`. Let us do that:

```python title="register exceptions to the application"
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from .errors import register_error_handlers

version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
)

register_error_handlers(app)  # add this line

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
```

Calling the `register_error_handlers` function enables us to register the created error handlers so that our application makes use of them. We provide the main application instance `app` to make sure the application uses them.


# Modifying our code/
After that, we shall then modify our code to make use of the created exceptions. We shall begin with the authentication dependencies. Let us go to `src/auth/dependencies.py` and add the following code.

```python title="adding custom errors in auth dependencies"
from typing import Any, List

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.db.redis import token_in_blocklist

from .service import UserService
from .utils import decode_token
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

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
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
```

What we've accomplished is replacing every instance where we used `HTTPException` with our own custom exceptions designed for each specific type of error. 

To keep this chapter concise, I'll leave you with the task of updating the rest of our application's code to include custom error handlers similar to the ones we've created here.

## Conclusion

Throughout this chapter, we've explored the creation of custom error handlers. These handlers empower us to provide tailored error messages based on the specific issues encountered within our application. We began by creating custom exception classes to encapsulate different types of errors. Following that, we implemented handlers to manage these exceptions and ensure appropriate responses are sent back to clients. Finally, we concluded by integrating these custom error handlers into our application, thereby enhancing its robustness and user experience.