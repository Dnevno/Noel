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
    def decrypt(data):
        if not data or not isinstance(data, (bytes, str)):
            return None
        try:
            if isinstance(data, memoryview):
                data = data.tobytes()
            return fernet.decrypt(data).decode()
        except Exception:
            return None

    @staticmethod
    def hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()