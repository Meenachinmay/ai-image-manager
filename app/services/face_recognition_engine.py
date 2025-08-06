import face_recognition
import numpy as np
from typing import Optional, Tuple, List
from PIL import Image
import io


class FaceRecognitionEngine:
    def __init__(self, tolerance: float = 0.6, model: str = "hog"):
        self.tolerance = tolerance
        self.model = model  # 'hog' or 'cnn'

    def extract_face_encoding(self, image_data: bytes) -> Optional[np.ndarray]:
        """Extract face encoding from image bytes."""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to numpy array
            image_array = np.array(image)

            # Find face locations
            face_locations = face_recognition.face_locations(
                image_array,
                model=self.model
            )

            if not face_locations:
                return None

            # Get face encodings
            face_encodings = face_recognition.face_encodings(
                image_array,
                face_locations
            )

            if not face_encodings:
                return None

            # Return the first face encoding
            return face_encodings[0]

        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None

    def compare_faces(
            self,
            known_encodings: List[np.ndarray],
            unknown_encoding: np.ndarray
    ) -> Tuple[bool, int, float]:
        """
        Compare unknown face with known faces.
        Returns: (match_found, best_match_index, distance)
        """
        if not known_encodings:
            return False, -1, 1.0

        # Calculate face distances
        distances = face_recognition.face_distance(known_encodings, unknown_encoding)

        # Get the best match
        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]

        # Check if it's a match based on tolerance
        is_match = best_distance <= self.tolerance

        # Convert distance to confidence (0-1 scale, where 1 is perfect match)
        confidence = 1.0 - best_distance if is_match else 0.0

        return is_match, int(best_match_index), float(confidence)