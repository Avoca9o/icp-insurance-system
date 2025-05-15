from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from dependencies import verify_token, SECRET_KEY
from passlib.context import CryptContext
import datetime
import json
from typing import Any, Dict

from logger import logger

router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

fake_users = {
    "johndoe@example.com": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}

fake_cases = {
    'Data': {
        'InsuranceCasesList': {
            'kndCode': '1110387',
            'dateTime': '2025-02-22T21:42:00+00:00',
            'InsuranceCases': [
                {
                    'insuranceCasesId': 'ax-111-11111110',
                    'documentName': 'Список страховых случаев',
                    'documentNumber': 23456,
                    'dateOfDocument': '2025-03-09',
                    'InsuranceCaseInformation': [
                        {
                            'insuranceCaseId': 1,
                            'documentName': 'Полис ОМС',
                            'documentNumber': 1111,
                            'date': '2025-05-12',
                            'diagnosisCode': 'B23.0',
                            'registrationClinicId': 256,
                            'registrationClinic': 'Медицинский центр имени Бурназяна',
                        },
                        {
                            'insuranceCaseId': 2,
                            'documentName': 'Полис ОМС',
                            'documentNumber': 2135,
                            'date': '2025-01-01',
                            'diagnosisCode': 'A00.0',
                            'registrationClinicId': 160,
                            'registrationClinic': 'Центральная клиническая больница гражданской авиации',
                        },
                    ],
                },
            ],
        },
    },
    'Links': {},
    'Meta': {
        'totalPages': 1,
    },
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, email: str):
    if email in db:
        return db[email]
    return None

@router.post('/open-data/v1.0/mfsp/token')
async def login(data: Dict[str, Any]):
    user = get_user(fake_users, data['username'])

    if not user or not verify_password(data['password'], user['hashed_password']):
        logger.error('Incorrect username or password')
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    
    payload = {
        'sub': user['username'],
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    logger.info('Authorization successfull')
    return token


@router.get('/open-data/v1.0/mfsp/insurance-cases')
async def get_data(policy_number: int,  diagnosis_code: str, date: str, user: dict = Depends(verify_token)):
    if user:
        for case in fake_cases['Data']['InsuranceCasesList']['InsuranceCases'][0]['InsuranceCaseInformation']:
            if case['documentName'] == 'Полис ОМС' and case['documentNumber'] == policy_number and case['date'] == date and case['diagnosisCode'] == diagnosis_code:
                logger.info('Case found')
                return case
        logger.error('Case does not exist')
        raise HTTPException(status_code=400, detail='Case does not exist')