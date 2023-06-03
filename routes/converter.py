from fastapi import (HTTPException, APIRouter, Depends,
                     File, Query, UploadFile, Form, status)
from database.connection import get_session
from auth.authenticate import authenticate
from models.converter import FileModel
from sqlmodel import select
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError, CouldntEncodeError
from fastapi.responses import FileResponse
import io
import tempfile

URL = "http://localhost:8080/file/record/"

file_router = APIRouter(
    tags=["Converter"],
)


@file_router.post("/upload/")
async def upload(file: UploadFile = File(...),
                 user_id: int = Form(...),
                 token: str = Form(...),
                 session=Depends(get_session)):
    try:
        # Проверяем, название файла в формате .wav
        if not file.filename.endswith('.wav'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong file format. Only .wav files."
            )
        # Проверяем есть ли ползователи с нашим токеном и user_id
        await authenticate(token=token,
                           user_id=user_id,
                           session=session)
        # Создаем буфер обмена, чтобы не сохранять файл .wav на диск
        audio_file = io.BytesIO()
        file_name = file.filename.split('.')[0]+".mp3"
        # Конвертируем .wav файл
        music = AudioSegment.from_wav(file.file)
        music.export(audio_file, format="mp3", codec="libmp3lame")
        # Сохраняем .mp3 файл в БД
        db_file = FileModel(name=file_name,
                            file=audio_file.getvalue())
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
    except HTTPException as http_exception:
        raise http_exception
    except CouldntDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to decode audio file."
                                   " Unsupported format or file.")
    except CouldntEncodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to encode audio"
                                   "file to MP3 format.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while"
                                   "processing the file.")
    finally:
        file.file.close()
    return f"{URL}?id={db_file.id}&user={user_id}"


@file_router.get("/record/")
async def record(id: str = Query(...),
                 user: str = Query(...),
                 session=Depends(get_session)):
    try:
        db_file = session.exec(
            select(FileModel)
            .where(FileModel.id == id)).first()
        if db_file:
            file_name = db_file.name
            file_bytes = db_file.file
            audio_segment = AudioSegment.from_file(io.BytesIO(file_bytes))

            # Сохраните аудиосегмент во временный файл
            with tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False) as temp_file:
                temp_file_path = temp_file.name
                audio_segment.export(temp_file_path, format="mp3")

            # Передача буфера клиенту в формате .mp3
            return FileResponse(
                temp_file_path,
                filename=file_name,
                media_type="audio/mpeg"
            )
        return {"message": "File is empty"}
    except (CouldntDecodeError, CouldntEncodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error when working with audio in pydub"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing the file"
        )
    finally:
        temp_file.close()
