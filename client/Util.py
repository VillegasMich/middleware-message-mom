from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM

class Util:
    TOKEN = None 

    @staticmethod
    def set_token(token: str):
        """Stores the authentication token"""
        Util.TOKEN = token

    @staticmethod
    def get_token():
        """Returns the stored authentication token"""
        return Util.TOKEN

    @staticmethod
    def get_headers():
        """Returns headers with authentication token"""
        token = Util.get_token()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
