import shutil
from typing import Optional
from pathlib import Path
from datetime import datetime
import uuid


class FileStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_image(self, image_data: bytes, person_name: str, extension: str = ".jpg") -> str:
        """Save image to person's folder and return the path."""
        # Create person's folder
        person_folder = self.base_path / person_name
        person_folder.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}{extension}"

        # Full path
        file_path = person_folder / filename

        # Save the file
        with open(file_path, "wb") as f:
            f.write(image_data)

        return str(file_path)

    def delete_person_folder(self, person_name: str) -> bool:
        """Delete a person's folder and all images."""
        person_folder = self.base_path / person_name
        if person_folder.exists():
            shutil.rmtree(person_folder)
            return True
        return False

    def get_image_path(self, person_name: str, filename: str) -> Optional[Path]:
        """Get the full path of an image."""
        file_path = self.base_path / person_name / filename
        return file_path if file_path.exists() else None