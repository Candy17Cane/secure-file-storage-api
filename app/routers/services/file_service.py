from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.crypto_utils import decrypt_bytes, encode_b64, encrypt_bytes, decode_b64
from app.models import File, User


STORAGE_DIR = Path(settings.STORAGE_PATH)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _build_storage_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix
    return f'{uuid4().hex}{ext}.enc'

async def save_encrypted_file(
        db: Session,
        owner: User,
        upload_file: UploadFile
) -> File:
    
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Filename is required',
        )
    
    raw_data = await upload_file.read()
    if not raw_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Uploaded file is empty',
        )
    
    ciphertext, salt, nonce = encrypt_bytes(raw_data)

    original_filename = upload_file.filename
    stored_filename = _build_storage_filename(original_filename)
    file_path = STORAGE_DIR / stored_filename

    file_path.write_bytes(ciphertext)

    mime_type = upload_file.content_type or mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

    file_record = File(
        owner_id=owner.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=len(raw_data),
        mime_type=mime_type,
        salt=encode_b64(salt),
        nonce=encode_b64(nonce),
    )

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return file_record



def get_user_files(db: Session, owner: User) -> list[File]:
    return(
        db.query(File)
        .filter(File.owner_id == owner.id)
        .order_by(File.created_at.desc())
        .all()
    )



def get_user_file_by_id(db: Session, owner: User, file_id: int) -> File:
    file_record = (
        db.query(File)
        .filter(File.id == file_id, File.owner_id == owner.id)
        .first()
    )

    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found',
        )
    
    return file_record



def get_decrypted_file_bytes(db: Session, owner: User, file_id: int) -> tuple[File, bytes]:
    file_record = get_user_file_by_id(db, owner, file_id)

    file_path = STORAGE_DIR / file_record.stored_filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Storad encrypted file not found on disk.',
        )
    
    ciphertext = file_path.read_bytes()

    salt = decode_b64(file_record.salt)
    nonce = decode_b64(file_record.nonce)

    try:
        decrypted_data = decrypt_bytes(ciphertext, salt, nonce)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to decrypt file data.',   
        )
    
    return file_record, decrypted_data


def delete_user_file(db: Session, owner: User, file_id: int) -> None:
    file_record = get_user_file_by_id(db, owner, file_id)

    file_path = STORAGE_DIR / file_record.stored_filename
    if file_path.exists() and file_path.is_file():
        os.remove(file_path)

    db.delete(file_record)
    db.commit()