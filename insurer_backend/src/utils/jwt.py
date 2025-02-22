from jose import jwt

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/authorize")

# TODO: read this shit from .env file
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def create_jwt_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("id")
