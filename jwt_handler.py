import time
import jwt
# from decouple import config

JWT_SECRET = "1234"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "auth_token": token,
        "token_type": "bearer",
        "status_code": 200
    }


def sign_jwt(user_id: str):
    payload = {
        "user_id": user_id,
        "expiry": time.time() + 30
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def jwt_decode(token: str):
    try:
        token_decode = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return token_decode

    except Exception as err:

        print(err)
        return None
