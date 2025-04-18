from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import logging

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
        if not data:
            return None
        try:
            if isinstance(data, memoryview):
                data = data.tobytes()
            if not isinstance(data, (bytes, str)):
                return None
            return fernet.decrypt(data).decode()
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            return None

    @staticmethod
    def hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()