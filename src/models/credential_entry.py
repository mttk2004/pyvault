# src/models/credential_entry.py
from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class CredentialEntry:
    """Represents a single credential entry in the vault."""
    service: str
    username: str
    password: str
    url: str
    category_id: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Serializes the object to a dictionary."""
        return {
            "entry_id": self.entry_id,
            "service": self.service,
            "username": self.username,
            "password": self.password,
            "url": self.url,
            "category": self.category_id  # Keep 'category' key for backward compatibility
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CredentialEntry':
        """Deserializes a dictionary into a CredentialEntry object."""
        return cls(
            entry_id=data.get("entry_id", str(uuid.uuid4())),
            service=data.get("service", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            url=data.get("url", ""),
            category_id=data.get("category", "uncategorized") # fallback for older data
        )
