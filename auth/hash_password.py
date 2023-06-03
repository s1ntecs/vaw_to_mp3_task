from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashToken:
    def create_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_hash(self, plain_token: str, hashed_token: str) -> bool:
        return pwd_context.verify(plain_token, hashed_token)
