from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def bcrypt_hash(text: str):
    return pwd_context.hash(text)

def bcrypt_verify(text: str, hash: str):
    return pwd_context.verify(text, hash)

def sha512_hash(text: str):
    sha512_hash = hashlib.sha512()
    sha512_hash.update(text.encode('utf-8'))
    return sha512_hash.hexdigest()