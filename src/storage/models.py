from dataclasses import dataclass

@dataclass
class FileRecord:
    # Represents a file stored in the system
    file_id: str
    owner_id: str
    filename: str
    size: int
    aes_nonce_hex: str
    sig_hex: str
