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


Let us test this

