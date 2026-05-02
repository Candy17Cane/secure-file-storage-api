import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from app.config import settings


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
PBKDF2_ITERATIONS = 390000


class CryptoError(Exception):
    pass

def generate_salt() -> bytes:
    return os.urandom(SALT_SIZE)


def generate_nonce() -> bytes:
    return os.urandom(NONCE_SIZE)


def derive_key(salt: bytes) -> bytes:
    """
    Получает 256-битный ключь из MASTER_KEY и salt
    """

    if not isinstance(salt, bytes) or len(salt) != SALT_SIZE:
        raise ValueError(f'Salt должени быть длинной {SALT_SIZE} байт.')
    
    master_key_bytes = settings.MASTER_KEY.encode('utf-8')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )

    return kdf.derive(master_key_bytes)


def encrypt_bytes(data: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Шифрует байты и возвращает:
    (ciphertext, salt, nonce)
    """
    
    if not isinstance(data, bytes):
        raise ValueError('Данные должны быть типа bytes.')

    salt = generate_salt()
    nonce = generate_nonce()
    key = derive_key(salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    return ciphertext, salt, nonce


def decrypt_bytes(ciphertext: bytes, salt: bytes, nonce: bytes) -> bytes:
    """
    Расшифровывает байты по ciphertext, salt, nonce
    """

    if not isinstance(ciphertext, bytes):
        raise ValueError('Ciphertext должен быть типа bytes.')
    if not isinstance(salt, bytes) or len(salt) != SALT_SIZE:
        raise ValueError(f'Salt должен быть длиной {SALT_SIZE} байт.')
    if not isinstance(nonce, bytes) or len(nonce) != NONCE_SIZE:
        raise ValueError(f'Nonce должен быть длиной {NONCE_SIZE} байт.')
    
    key = derive_key(salt)
    aesgcm = AESGCM(key)

    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise CryptoError('Не удалось расшифровать данные.') from exc
    

def encode_b64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')


def decode_b64(data: str) -> bytes:
    return base64.b64decode(data.encode('utf-8'))
