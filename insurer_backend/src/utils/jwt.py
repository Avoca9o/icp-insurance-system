from jose import jwt

from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/authorize")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_jwt_token(data: dict):
    to_encode = data.copy()
    print('secret key = ', SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("id")
