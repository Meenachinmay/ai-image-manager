"""Application constants."""

# File upload constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}

# Face recognition constants
DEFAULT_FACE_TOLERANCE = 0.6
DEFAULT_ENCODING_MODEL = "hog"  # "hog" for CPU, "cnn" for GPU

# Cache TTL (seconds)
CACHE_TTL = 300  # 5 minutes

# Response messages
MSG_NO_FACE_DETECTED = "No face detected in the image"
MSG_FACE_NOT_RECOGNIZED = "Face not recognized"
MSG_NO_REGISTERED_FACES = "No registered faces in the system"
MSG_PERSON_NOT_FOUND = "Person not found"
MSG_PERSON_DELETED = "Person deleted successfully"