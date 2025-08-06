#!/usr/bin/env python
"""Check if all imports are working correctly."""
import sys
import traceback


def check_imports():
    """Test all imports."""
    errors = []

    imports_to_test = [
        "from app.config import get_settings",
        "from app.domain.models import Person, FaceEncoding, ImageUploadResult",
        "from app.domain.interfaces import IFaceService, IFaceRepository",
        "from app.infrastructure.database import Base, engine, get_db",
        "from app.infrastructure.database.models import PersonDB, FaceEncodingDB",
        "from app.infrastructure.repositories import FaceRepository",
        "from app.infrastructure.storage import FileStorage",
        "from app.services import FaceService, FaceRecognitionEngine",
        "from app.utils import validate_image, resize_image, get_image_format",
        "from app.api.v1.routes import api_router",
        "from app.api.v1.handlers import face_router, health_router",
    ]

    for import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"✓ {import_statement}")
        except Exception as e:
            error_msg = f"✗ {import_statement}: {type(e).__name__}: {e}"
            errors.append(error_msg)
            print(error_msg)
            # Print detailed traceback for debugging
            if "--verbose" in sys.argv:
                traceback.print_exc()

    print("\n" + "=" * 50)
    if errors:
        print(f"❌ {len(errors)} import error(s) found")
        return False
    else:
        print("✅ All imports working correctly!")
        return True


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)