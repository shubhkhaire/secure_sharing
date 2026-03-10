from passlib.context import CryptContext
import hashlib
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash_password(password:str):
    sha256_hash = hashlib.sha256(password.encode()).digest()
    return base64.b64encode(sha256_hash).decode('utf-8')

def hash_password(password: str) -> str:
    password = _prehash_password(password)
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _prehash_password(plain_password)
    # print(f"Verifying password: {plain_password[:72]} against hash: {hashed_password}")
    # print(len(plain_password[:72]), len(hashed_password))
    return pwd_context.verify(plain_password[:72], hashed_password)

