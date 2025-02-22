from dotenv import load_dotenv
from fastapi import Security, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')