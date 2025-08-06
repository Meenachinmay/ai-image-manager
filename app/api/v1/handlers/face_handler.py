from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from typing import Optional, List
from app.domain.interfaces.face_service_interface import IFaceService
from app.api.dependencies import get_face_service
from pydantic import BaseModel

router = APIRouter(prefix="/faces", tags=["faces"])


class PersonResponse(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str


class UploadResponse(BaseModel):
    success: bool
    person_name: Optional[str]
    confidence: float
    image_path: str
    message: str
    is_new_person: bool


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
        file: UploadFile = File(...),
        person_name: Optional[str] = Form(None),
        service: IFaceService = Depends(get_face_service)
):
    """
    Upload an image for face recognition.
    If person_name is provided, it registers a new face.
    If not provided, it tries to identify the person.
    """
    try:
        result = await service.process_image(file, person_name)

        return UploadResponse(
            success=result.success,
            person_name=result.person_name,
            confidence=result.confidence,
            image_path=result.image_path,
            message=result.message,
            is_new_person=result.is_new_person
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/persons", response_model=List[PersonResponse])
async def get_all_persons(
        service: IFaceService = Depends(get_face_service)
):
    """Get all registered persons."""
    persons = await service.get_all_persons()

    return [
        PersonResponse(
            id=p.id,
            name=p.name,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in persons
    ]


@router.get("/persons/{name}", response_model=PersonResponse)
async def get_person_by_name(
        name: str,
        service: IFaceService = Depends(get_face_service)
):
    """Get a person by name."""
    person = await service.get_person_by_name(name)

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return PersonResponse(
        id=person.id,
        name=person.name,
        created_at=person.created_at.isoformat(),
        updated_at=person.updated_at.isoformat()
    )


@router.delete("/persons/{person_id}")
async def delete_person(
        person_id: int,
        service: IFaceService = Depends(get_face_service)
):
    """Delete a person and all their data."""
    success = await service.delete_person(person_id)

    if not success:
        raise HTTPException(status_code=404, detail="Person not found")

    return {"message": "Person deleted successfully"}