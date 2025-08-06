from typing import Optional, List
import numpy as np
import pickle
from sqlalchemy.orm import Session
from app.domain.interfaces.face_repository_interface import IFaceRepository
from app.domain.models import Person, FaceEncoding
from app.infrastructure.database.models import PersonDB, FaceEncodingDB


class FaceRepository(IFaceRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create_person(self, name: str) -> Person:
        db_person = PersonDB(name=name)
        self.db.add(db_person)
        self.db.commit()
        self.db.refresh(db_person)

        return Person(
            id=db_person.id,
            name=db_person.name,
            created_at=db_person.created_at,
            updated_at=db_person.updated_at
        )

    async def get_person_by_id(self, person_id: int) -> Optional[Person]:
        db_person = self.db.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not db_person:
            return None

        return Person(
            id=db_person.id,
            name=db_person.name,
            created_at=db_person.created_at,
            updated_at=db_person.updated_at
        )

    async def get_person_by_name(self, name: str) -> Optional[Person]:
        db_person = self.db.query(PersonDB).filter(PersonDB.name == name).first()
        if not db_person:
            return None

        return Person(
            id=db_person.id,
            name=db_person.name,
            created_at=db_person.created_at,
            updated_at=db_person.updated_at
        )

    async def get_all_persons(self) -> List[Person]:
        db_persons = self.db.query(PersonDB).all()
        return [
            Person(
                id=p.id,
                name=p.name,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in db_persons
        ]

    async def save_face_encoding(
            self,
            person_id: int,
            encoding: np.ndarray,
            image_path: str
    ) -> FaceEncoding:
        # Serialize numpy array to binary
        encoding_binary = pickle.dumps(encoding)

        db_encoding = FaceEncodingDB(
            person_id=person_id,
            encoding=encoding_binary,
            image_path=image_path
        )
        self.db.add(db_encoding)
        self.db.commit()
        self.db.refresh(db_encoding)

        return FaceEncoding(
            id=db_encoding.id,
            person_id=db_encoding.person_id,
            encoding=encoding,
            image_path=db_encoding.image_path,
            created_at=db_encoding.created_at
        )

    async def get_all_face_encodings(self) -> List[FaceEncoding]:
        db_encodings = self.db.query(FaceEncodingDB).all()
        encodings = []

        for db_enc in db_encodings:
            # Deserialize numpy array from binary
            encoding_array = pickle.loads(db_enc.encoding)
            encodings.append(
                FaceEncoding(
                    id=db_enc.id,
                    person_id=db_enc.person_id,
                    encoding=encoding_array,
                    image_path=db_enc.image_path,
                    created_at=db_enc.created_at
                )
            )

        return encodings

    async def delete_person(self, person_id: int) -> bool:
        db_person = self.db.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not db_person:
            return False

        self.db.delete(db_person)
        self.db.commit()
        return True