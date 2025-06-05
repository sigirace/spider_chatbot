from passlib.context import CryptContext


class CryptoService:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )

    def encrypt(self, secret):
        return self.pwd_context.hash(secret)

    def verify(self, secret, hashed_secret):
        return self.pwd_context.verify(secret, hashed_secret)
