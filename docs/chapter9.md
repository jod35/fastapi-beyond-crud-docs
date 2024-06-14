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
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

### How JWT Authentication works
1. **Client Authentication**: The client shall submit a payload with the user's email or password and when they are valid, the server shall genrate a JWT to send it to the client.

2. **Token Storage**: The client will store the token either in local storage or cookies.

3. **Subsequent Requests**: The client shall make requests to the server using the token inside the HTTP headers. 

4. **Token Verification**: The server verifies the token's signature and validates its payload to ensure the token has not been tampered with and is still valid.

5. **Authorization**: If the token is valid, the server processes the request; otherwise, it rejects the request.

JWTs are compact, we can pass them in the request body, headers, and also via URLs. In addition, they are self contained and can contain all information we may wish them to have therefor, reducing on the number of times we query the database. They are secure and can also be used across many domains making them ideal for ditributed systems.

To implement JWT authentication, we shall make use of PyJWT, a library for encoding and decoding JWTs using Python. Let us begin by installing it with;

```console title="Installing PyJWT"
pip install pyjwt[crypto]
```
Note how we have included crypto, stading for the cryptography module.


Inside our `auth` directory, we shall create  move to the utils file where we create the functions for our password management. Inside `utils.py`, let us add the following code.
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


#### Explanation
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