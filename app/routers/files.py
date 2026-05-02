from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import FileOut
from app.routers.services.file_service import (
    save_encrypted_file,
    get_user_files,
    get_decrypted_file_bytes,
    delete_user_file,
)

router = APIRouter(prefix='/files', tags=['Files'])


# ===== UPLOAD FILE =====
@router.post('/upload', response_model=FileOut)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_record = await save_encrypted_file(db, current_user, file)
    return file_record


# ===== LIST FILES =====
@router.get('/', response_model=list[FileOut])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_files(db, current_user)


# ===== DOWNLOAD FILE =====
@router.get('/{file_id}/download')
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_record, data = get_decrypted_file_bytes(db, current_user, file_id)

    return Response(
        content=data,
        media_type=file_record.mime_type,
        headers={
            'Content-Disponsition': f"attachment; filename='{file_record.original_filename}'"
        },
    )


# ===== DELETE FILE =====
@router.delete('/{file_id}')
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user_file(db, current_user, file_id)
    return {'detail': 'File deleted successfully'}