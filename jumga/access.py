import json
from cryptography.fernet import Fernet
from django.conf import settings
from datetime import datetime, timedelta
import jwt


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def encoded_reset_token(**data):
    # Converts the data object to string
    data = json.dumps(data)
    # Encrypt json with salt
    encrypted_data = encrypt(data.encode(), settings.PROJECT_ACCESS_KEY)
    # Convert from bytes to string
    encrypted_data = encrypted_data.decode()

    payload = {
        'data': encrypted_data,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS)
    }
    encoded_data = jwt.encode(
        payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return encoded_data.decode('utf-8')


def decode_reset_token(reset_token):
    try:
        decoded_data = jwt.decode(reset_token, settings.JWT_SECRET,
                                  algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None  # means expired token

    data = decoded_data['data']
    # Decrypt encrypted data. The encode() below is to convert the encrypted data from string to bytes
    data = decrypt(data.encode(), settings.PROJECT_ACCESS_KEY).decode()
    # Convert json data back to dict.
    data = json.loads(data)
    return data
