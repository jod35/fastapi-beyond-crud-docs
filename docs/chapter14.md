# Email Support

We've built many features in our application, but we intentionally skipped some that require sending emails. This allows us to dedicate a chapter to exploring email functionality in detail. Sending emails is crucial for communicating with users, verifying identities, and enabling password resets.

## FastAPI-Mail

If you're familiar with Flask, the most popular extension for adding email support is [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/). Flask-Mail allows emails to be sent with a straightforward setup. The FastAPI equivalent is [FastAPI-Mail](https://sabuhish.github.io/fastapi-mail/), which has a similar configuration process but also supports asynchronous operations and Pydantic models.

Let's begin by installing FastAPI-Mail. In your terminal, within the active virtual environment, install it with:

```console
$ pip install fastapi-mail
```

## Configuring FastAPI-Mail

Let's create a file to set up FastAPI-Mail and centralize all email-sending logic. Inside the `src/` directory, create a file called `mail.py` and add the following code:

```python
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.config import Config
from pathlib import Path


# get the parent directory
BASE_DIR = Path(__file__).resolve().parent


# create the config for sending emails
mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)


# create the object to send emails with the config
mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message
```

### Explanation

We begin by importing `FastMail`, `ConnectionConfig`, `MessageSchema`, and `MessageType`.

```python title="The imports"
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.config import Config
from pathlib import Path
```

- `FastMail`: Creates the `mail` object for accessing email-sending methods.
- `ConnectionConfig`: Sets up the email configuration for FastAPI-Mail.
- `MessageSchema`: Structures an email before sending.
- `MessageType`: Specifies the type of content to send via email (e.g., HTML).
- `Config`: Imports application-specific configurations, including email settings.
- `Path`: Used to create paths, particularly for determining the location of the templates folder.

We then proceed to configure FastAPI-Mail using values we get from our `Config` object.

```python title="email config"
mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)
```

| Key               | Explanation                                                                                                                                                                                                 |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MAIL_USERNAME`   | The username of the email address sending the emails. Set via an environment variable.                                                                                                                      |
| `MAIL_PASSWORD`   | The password for the SMTP server. For Gmail, this is an [app-specific password](https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password?hl=en). Set via an environment variable.   |
| `MAIL_FROM`       | The email address of the sender. Set via an environment variable.                                                                                                                                           |
| `MAIL_PORT`       | The port used to connect to the SMTP server (usually 587 for TLS). Set via an environment variable.                                                                                                         |
| `MAIL_SERVER`     | The SMTP server used to send emails (e.g., smtp.gmail.com). Set via an environment variable.                                                                                                                |
| `MAIL_FROM_NAME`  | The name displayed as the sender of the email. Set via an environment variable.                                                                                                                             |
| `MAIL_STARTTLS`   | Enables the STARTTLS command, which upgrades the connection to a secure TLS/SSL connection. Set to True.                                                                                                    |
| `MAIL_SSL_TLS`    | Indicates whether to use SSL/TLS for the connection from the start. Set to False if `MAIL_STARTTLS` is True.                                                                                                |
| `USE_CREDENTIALS` | Specifies whether to use credentials (username and password) to authenticate with the SMTP server. Set to True.                                                                                             |
| `VALIDATE_CERTS`  | Specifies whether to validate the server's SSL certificates. Set to True.                                                                                                                                   |
| `TEMPLATE_FOLDER` | Specifies the folder containing email templates, useful for sending HTML emails with Jinja templates. we set this up to make use of `BASE_DIR` to point to a `templates` folder we should have in our `src` |

The `mail` object is created using the `FastMail` class and is configured with `mail_config`:

```python
mail = FastMail(config=mail_config)
```

A function `create_message` is defined to create an email message. It takes `recipients`, `subject`, and `body` as parameters and returns a `MessageSchema` object:

```python
def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message
```

In the `Settings` class located in `src.config.py`, email-related configuration variables are added. These variables are used to configure the email sending settings:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    # add these
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

The `.env` file should be updated with the relevant environment variables for email configuration:

```console
DATABASE_URL=<your postgresql url>
JWT_SECRET=<your jwt secret>
JWT_ALGORITHM=<your jwt algorithm>
REDIS_HOST=localhost
REDIS_PORT=6379

MAIL_USERNAME=<your mail username>
MAIL_PASSWORD=<your mail password>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_FROM=<your email address>
MAIL_FROM_NAME=Bookly

DOMAIN=localhost:8000
```

!!! Note
    The `DOMAIN` environment variable shall be set to help us when we create the verification and password reset
    links.

### Sending Our First Email

To send an email, all we shall have to do is to call the `send_message` method on the `mail` object. Let us do that in `src/auth/routes.py
`.

```python title="sending emails"
.... # rest of the imports
from src.mail import mail, create_message
from src.celery_tasks import send_email
from src.auth.schemas import EmailModel

auth_router = APIRouter()


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = create_message(recipients=emails, subject=subject, body=html)
    mail.send_message(message)

    return {"message": "Email sent successfully"}
```

To send an email, we'll utilize the `send_message` method within the `mail` object. This code will reside in the `src/auth/routes.py` file.

We've constructed an API endpoint accessible at the `/auth/send_mail` path. Its corresponding handler function is named `send_mail`. This function accepts an `EmailModel` object as input, which contains a list of email addresses intended for the email. 

We extract these addresses from the `EmailModel` object. A basic HTML structure  `html` and a `subject` line are defined for the email content. Subsequently, the `create_message` function is invoked, providing the `recipient` `email` `addresses`, subject, and HTML content. This function generates a message object which is then passed to the mail.send_message method to dispatch the email. A success message is returned to indicate successful email transmission.

The `EmailModel` class, located in `src/auth/schemas.py`, is a Pydantic model designed to validate the incoming email addresses. It mandates a list of email strings within the addresses field.

```python title="pydantic model for getting recipient email addresses"
class EmailModel(BaseModel):
    addresses : List[str]

```


Here’s the revised text with improved grammar and language:

---

Let us test this. Accessing the endpoint and making a request results in the following response:

![Successful email is sent](./img/img57.png)

To confirm if our email has been sent:

![Confirming if the email is sent](./img/img58.png)

!!! Note
    You may notice a slight delay between the sending of the emails and the response indicating that an email has been successfully sent. This is because, to send the email, we are making another request to the SMTP server we use. We will explore an approach to speed this up in a later chapter.

## User Account Verification
If you have followed this series from the beginning, you will notice that we created a user authentication database model called `User`. In this model, we defined the `is_verified` field to handle the activation of user accounts. We will start by implementing this verification process using the email address provided by the user during signup.

User account verification is important as it prevents the creation of fake accounts. It also allows us to collect user email addresses for communications and other purposes.

### ItsDangerous
To safely move data from our server to an untrusted environment, we will use [ItsDangerous](https://itsdangerous.palletsprojects.com/en/2.2.x/). ItsDangerous is a Python package that allows us to cryptographically sign data and hand it over to someone else, ensuring that the data has not been tampered with when we receive it. The recipient of the data can receive and read it but cannot modify it unless they have the sender's secret key.

This package will be crucial as it will enable us to create URL-safe tokens that we will include in the user verification links we send via email.

To install it we shall run
```console
$ pip install itsdangerous
```

To set it up, let us navigate to `src/auth/utils.py` and add the following code.

```python title="serializing and deserializing user's email address"
... #rest of the imports

from itsdangerous import URLSafeTimedSerializer

... # rest of the code 

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict):
    """Serialize a dict into a URLSafe token"""

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token:str):
    """Deserialize a URLSafe token to get data"""
    try:
        token_data = serializer.loads(token)

        return token_data
    
    except Exception as e:
        logging.error(str(e))
        
```

In the code above, we start by importing the `URLSafeTimedSerializer` class, which we use to create the `serializer` object. This object is essential for serializing the user's email address. We configure the serializer with a `secret_key` (the same one used for creating access tokens) and a `salt`, which we've set to the string "email-verification."

Next, we define two functions: `create_url_safe_token` and `decode_url_safe_token`. The `create_url_safe_token` function serializes a `data` dictionary into a token. The `decode_url_safe_token` function deserializes the token, extracting the data while handling any potential errors.

With these functions in place, we can verify user emails during signup. The process flow is as follows:

1. A user creates an account with a valid email address.

2. An email verification link is sent to the user's email.

3. The user clicks the verification link.

4. The user is redirected to our app upon successful email verification, and we send them a success response.


### Sending the verification Email
To make this work, we are going to add the following code to `src/auth/routes.py`
```python title="Email verification on user signup"
... # many imports here
from .schemas import (
    ... # more imports
    UserCreateModel,
)
from .service import UserService
from .utils import (
    ... # more imports
    create_url_safe_token,
    decode_url_safe_token,
)
from src.mail import mail, create_message

... # rest of the code

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    message = create_message(
        recipients=[email], subject="Verify your email", body=html_message
    )

    await mail.send_message(message)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


```

First we import both functions `create_url_safe_token` and `decode_url_safe_token`. After doing that we use pretty much the same approach we used to send a sample email to send the verification link.

```python title="creating the verification link"
token = create_url_safe_token({"email": email})

link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

html_message = f"""
<h1>Verify your Email</h1>
<p>Please click this <a href="{link}">link</a> to verify your email</p>
"""

message = create_message(
    recipients=[email], subject="Verify your email", body=html_message
)

await mail.send_message(message)
```

We start by creating the token using `create_url_safe_token`. We then use the `DOMAIN`and the token to create the verification link `link`. We create the `message` by combining the `html_message`, `subject`, and `link`. To send the `message`, we shall use the `mail.send_message` function finally send the email.


Let us test this 

![send verification email](./img/img59.png)

We can confirm that the email has been sent 

![confirm if email has been sent](./img/img60.png)

Clicking the link, we shall see that we are going to be redirected back to the app as whown below.

![email verification URL not found](./img/img61.png)


### Verifying Emails
Having sent the vetrification link, we now need to verify the user accounts of users when they click the verification link.

Just below the the signup endpoint, let us add the following code.

```python title="Verifying the user account"
from .schemas import (
    ... # more imports
    UserCreateModel,
)
from .service import UserService
from .utils import (
    ... # more imports
    create_url_safe_token,
    decode_url_safe_token,
)
from src.mail import mail, create_message


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

```

What we have done is to create the path `/verify` that will use a `token` path parameter. This path will be accessed via the GET method. Its path handler `verify_user_account` will take in the `token` path param as well as the `session` dependency. Once we get the token, we deserialize it with the `decode_url_safe_token` function.

Having got the `token_data`, we obtain the user's email, check if the email is not None and if not, we obtain the user account and update the `is_verified`  field on the account to `True`. We then raise an exception in case the email was not obtained. 


Let us make the verification link expire after a certain time by modifying the `decode_url_safe_token` function of `src/auth/utils` to the following.

```python title="create a expirable token"
def decode_url_safe_token(token:str):
    try:
        token_data = serializer.loads(token, max_age=60)

        return token_data
    
    except Exception as e:
        logging.error(str(e))

```

Note that we have added `max_age` to the `serializer` object and have given it an integer value of 60 seconds.

Let us try to verify a user account again. With different creadentials, I will create a new user account as shown below.

Creating a user account sends an email successfully.

![creating a user account with different credentials](./img/img62.png)

The verification will be sent successfully and the link will be sent as shown below.

![verification email sent successfully](./img/img63.png)

![Account Verifed Successfully](./img/img64.png)

So we have successfully verified the user account. Let us complete the user verification by adding a check to the authentication dependencies to only allow users with verified accounts to access any exnpoints. We shall do so by first of all adding a custom exception class to be raised only when a user who is not verified tries to access an API endpoint.

Let add this inside `src/errors.py`.
```python title="error class and handler for verification check"

class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass


... # there is some code here (create_exception_handler)

def register_all_errors(app: FastAPI):
    ... # other errors registered here

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account Not verified",
                "error_code": "account_not_verified",
                "resolution":"Please check your email for verification details"
            },
        ),
    )

```

What we have done is create the error class `AccountNotVerified` which is to be raised when an unverified user account tries to access a protected endpoint. To finally add this check, we shall edit the `RoleChecker` dependency in `src/auth/dependencies.py`.

```python title="check if a user is verified"
class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()

```

Before we check if the user has the right role, we shall first check if the user is verified and if not, we shall raise an exception `AccountNotVerified`. To test this, we shall create a user account with a very vague email address.

![creating user account with vague email](./img/img65.png)

After obtaining authentication credentials for the user (access and refresh tokens), Let us use them to access a protect endpoint such as that to get all books. 

![getting userr credentials](./img/img66.png)

![get all books](./img/img67.png)

And like that, we have built the user account verification.

