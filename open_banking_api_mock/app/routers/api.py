from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.dependencies import verify_token, SECRET_KEY
from passlib.context import CryptContext
import datetime
import json
from typing import Any, Dict

router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

fake_users = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}

fake_cases = {
    'kndCode': '1110387',
    'dateTime': '2025-02-22T21:42:00+00:00',
    'InsuranceCases': [
        {
            'insuranceCaseId': 1,
            'documentName': 'Полис ОМС',
            'documentNumber': 1111,
            'date': '2024-03-25',
            'diagnosisCode': 'trauma'
        }
    ]
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        return db[username]
    return None

@router.post('/open-data/v1.0/mfsp/token')
async def login(data: Dict[str, Any]): #OAuth2PasswordRequestForm = Depends()):
    print(data)
    user = get_user(fake_users, data['username'])

    if not user or not verify_password(data['password'], user['hashed_password']):
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    
    payload = {
        'sub': user['username'],
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/open-data/v1.0/mfsp/insurance-cases')
async def get_data(policy_number: int,  diagnosis_code: str, date: datetime.date, user: dict = Depends(verify_token)):
    if user:
        for case in fake_cases['InsuranceCases']:
            if case['documentName'] == 'Полис ОМС' and case['documentNumber'] == policy_number and case['date'] == date and case['diagnosisCode'] == diagnosis_code:
                return case       
        return HTTPException(status_code=400, detail='Case does not exist')