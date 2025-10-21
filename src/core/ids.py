import uuid

# Generate a new unique identifier
def new_id() -> str:
    return str(uuid.uuid4())
