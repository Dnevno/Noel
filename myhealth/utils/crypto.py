from cryptography.fernet import Fernet
from django.conf import settings
import hashlib

fernet = Fernet(settings.FERNET_KEY)

class CryptoUtils:
    @staticmethod
    def encrypt(text: str) -> bytes:
        if text is None:
            return None
        if not isinstance(text, str):
            text = str(text)
        return fernet.encrypt(text.encode())

    @staticmethod
    def decrypt(data: bytes) -> str:
        if data is None:
            return None
        return fernet.decrypt(data).decode()

    @staticmethod
    def hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()