# src/models/vault.py
from dataclasses import dataclass, field
from typing import List
from src.models.credential_entry import CredentialEntry
from src.category_manager import CategoryManager

@dataclass
class Vault:
    """Represents the entire user vault, containing entries and categories."""
    entries: List[CredentialEntry] = field(default_factory=list)
    category_manager: CategoryManager = field(default_factory=CategoryManager)

    def to_dict(self) -> dict:
        """Serializes the vault to a dictionary for JSON storage."""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "categories": self.category_manager.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Vault':
        """Deserializes a dictionary into a Vault object."""
        category_manager = CategoryManager()
        if "categories" in data:
            category_manager.from_dict(data["categories"])

        # Handle backward compatibility for old data formats
        raw_entries = data.get("entries", []) if isinstance(data, dict) else data

        cleaned_entries = category_manager.cleanup_entry_categories(raw_entries)

        entries = [CredentialEntry.from_dict(entry_data) for entry_data in cleaned_entries]

        return cls(entries=entries, category_manager=category_manager)
