from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify(plain_password: str, hashed_password: str) -> bool:
    return pwd.verify(plain_password, hashed_password)
