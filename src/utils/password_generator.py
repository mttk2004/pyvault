"""
Advanced Password Generator for PyVault
Provides secure password generation with extensive customization options.
"""

import secrets
import string
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class PasswordStrength(Enum):
    """Password strength levels."""
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    EXCELLENT = 5

@dataclass
class CharacterSet:
    """Represents a character set with its properties."""
    name: str
    chars: str
    min_count: int = 0
    max_count: Optional[int] = None
    enabled: bool = True

@dataclass
class PasswordConfig:
    """Configuration for password generation."""
    length: int = 16
    min_length: int = 4
    max_length: int = 128
    
    # Character sets
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_numbers: bool = True
    use_special: bool = True
    
    # Constraints
    min_uppercase: int = 0
    min_lowercase: int = 0
    min_numbers: int = 0
    min_special: int = 0
    max_uppercase: Optional[int] = None
    max_lowercase: Optional[int] = None
    max_numbers: Optional[int] = None
    max_special: Optional[int] = None
    
    # Character exclusions
    exclude_ambiguous: bool = False
    exclude_similar: bool = False
    custom_excluded: str = ""
    
    # Special character set
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.length = max(self.min_length, min(self.max_length, self.length))

@dataclass
class PasswordResult:
    """Result of password generation."""
    password: str
    strength: PasswordStrength
    entropy: float
    satisfied_constraints: bool
    warnings: List[str] = field(default_factory=list)
    character_distribution: Dict[str, int] = field(default_factory=dict)

class PasswordGenerator:
    """Advanced password generator with customizable options."""
    
    # Predefined character sets
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    NUMBERS = "0123456789"
    SPECIAL_DEFAULT = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ambiguous characters (easily confused)
    AMBIGUOUS = "0OoIl1"
    
    # Similar character groups (visually similar)
    SIMILAR_GROUPS = [
        "il1|",
        "O0o",
        "5S$",
        "G6",
        "8B",
        "2Z",
        "vw",
        "mn"
    ]
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()
        self._validate_config()
    
    def update_config(self, config: PasswordConfig):
        """Update the configuration."""
        self.config = config
        self._validate_config()
    
    def generate_password(self, max_attempts: int = 100) -> PasswordResult:
        """
        Generate a password that satisfies all constraints.
        
        Args:
            max_attempts: Maximum attempts to satisfy constraints
            
        Returns:
            PasswordResult with password and metadata
        """
        warnings = []
        
        # Validate constraints first
        validation_result = self._validate_constraints()
        if not validation_result[0]:
            return PasswordResult(
                password="",
                strength=PasswordStrength.VERY_WEAK,
                entropy=0.0,
                satisfied_constraints=False,
                warnings=validation_result[1]
            )
        
        # Try to generate a valid password
        for attempt in range(max_attempts):
            password = self._generate_password_attempt()
            if self._satisfies_constraints(password):
                strength, entropy = self._calculate_strength_and_entropy(password)
                distribution = self._get_character_distribution(password)
                
                return PasswordResult(
                    password=password,
                    strength=strength,
                    entropy=entropy,
                    satisfied_constraints=True,
                    warnings=warnings,
                    character_distribution=distribution
                )
        
        # If we can't satisfy constraints, return best attempt with warnings
        password = self._generate_password_attempt()
        strength, entropy = self._calculate_strength_and_entropy(password)
        distribution = self._get_character_distribution(password)
        warnings.append(f"Could not satisfy all constraints after {max_attempts} attempts")
        
        return PasswordResult(
            password=password,
            strength=strength,
            entropy=entropy,
            satisfied_constraints=False,
            warnings=warnings,
            character_distribution=distribution
        )
    
    def _generate_password_attempt(self) -> str:
        """Generate a single password attempt."""
        char_sets = self._get_available_character_sets()
        
        if not char_sets:
            return ""
        
        # Calculate minimum required characters
        min_required = (
            self.config.min_uppercase +
            self.config.min_lowercase +
            self.config.min_numbers +
            self.config.min_special
        )
        
        # Ensure we have enough length for minimum requirements
        actual_length = max(self.config.length, min_required)
        
        password_chars = []
        
        # First, satisfy minimum requirements
        if self.config.use_uppercase and self.config.min_uppercase > 0:
            chars = self._get_filtered_chars(self.UPPERCASE)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_uppercase))
        
        if self.config.use_lowercase and self.config.min_lowercase > 0:
            chars = self._get_filtered_chars(self.LOWERCASE)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_lowercase))
        
        if self.config.use_numbers and self.config.min_numbers > 0:
            chars = self._get_filtered_chars(self.NUMBERS)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_numbers))
        
        if self.config.use_special and self.config.min_special > 0:
            chars = self._get_filtered_chars(self.config.special_chars)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_special))
        
        # Fill remaining length with random characters from all available sets
        all_chars = "".join(char_sets.values())
        all_chars = self._get_filtered_chars(all_chars)
        
        remaining_length = actual_length - len(password_chars)
        if remaining_length > 0:
            password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
        
        # Shuffle the password to avoid predictable patterns
        password_list = list(password_chars)
        for i in range(len(password_list)):
            j = secrets.randbelow(len(password_list))
            password_list[i], password_list[j] = password_list[j], password_list[i]
        
        # Trim to desired length if we overshot due to minimum requirements
        if len(password_list) > self.config.length:
            password_list = password_list[:self.config.length]
        
        return "".join(password_list)
    
    def _get_available_character_sets(self) -> Dict[str, str]:
        """Get the available character sets based on configuration."""
        char_sets = {}
        
        if self.config.use_uppercase:
            char_sets["uppercase"] = self._get_filtered_chars(self.UPPERCASE)
        if self.config.use_lowercase:
            char_sets["lowercase"] = self._get_filtered_chars(self.LOWERCASE)
        if self.config.use_numbers:
            char_sets["numbers"] = self._get_filtered_chars(self.NUMBERS)
        if self.config.use_special:
            char_sets["special"] = self._get_filtered_chars(self.config.special_chars)
        
        return {k: v for k, v in char_sets.items() if v}  # Remove empty sets
    
    def _get_filtered_chars(self, chars: str) -> str:
        """Apply filters to character set."""
        filtered = chars
        
        # Remove ambiguous characters
        if self.config.exclude_ambiguous:
            filtered = "".join(c for c in filtered if c not in self.AMBIGUOUS)
        
        # Remove similar characters
        if self.config.exclude_similar:
            for group in self.SIMILAR_GROUPS:
                group_chars = set(group)
                # Keep only the first character from each similar group
                if any(c in filtered for c in group_chars):
                    first_char = next((c for c in group if c in filtered), None)
                    if first_char:
                        filtered = "".join(c for c in filtered if c not in group_chars)
                        filtered += first_char
        
        # Remove custom excluded characters
        if self.config.custom_excluded:
            filtered = "".join(c for c in filtered if c not in self.config.custom_excluded)
        
        return filtered
    
    def _satisfies_constraints(self, password: str) -> bool:
        """Check if password satisfies all constraints."""
        distribution = self._get_character_distribution(password)
        
        # Check minimum constraints
        if (self.config.min_uppercase > 0 and 
            distribution.get("uppercase", 0) < self.config.min_uppercase):
            return False
        
        if (self.config.min_lowercase > 0 and 
            distribution.get("lowercase", 0) < self.config.min_lowercase):
            return False
        
        if (self.config.min_numbers > 0 and 
            distribution.get("numbers", 0) < self.config.min_numbers):
            return False
        
        if (self.config.min_special > 0 and 
            distribution.get("special", 0) < self.config.min_special):
            return False
        
        # Check maximum constraints
        if (self.config.max_uppercase is not None and 
            distribution.get("uppercase", 0) > self.config.max_uppercase):
            return False
        
        if (self.config.max_lowercase is not None and 
            distribution.get("lowercase", 0) > self.config.max_lowercase):
            return False
        
        if (self.config.max_numbers is not None and 
            distribution.get("numbers", 0) > self.config.max_numbers):
            return False
        
        if (self.config.max_special is not None and 
            distribution.get("special", 0) > self.config.max_special):
            return False
        
        return True
    
    def _get_character_distribution(self, password: str) -> Dict[str, int]:
        """Get the distribution of character types in the password."""
        distribution = {
            "uppercase": 0,
            "lowercase": 0,
            "numbers": 0,
            "special": 0,
            "other": 0
        }
        
        for char in password:
            if char in self.UPPERCASE:
                distribution["uppercase"] += 1
            elif char in self.LOWERCASE:
                distribution["lowercase"] += 1
            elif char in self.NUMBERS:
                distribution["numbers"] += 1
            elif char in self.config.special_chars:
                distribution["special"] += 1
            else:
                distribution["other"] += 1
        
        return distribution
    
    def _calculate_strength_and_entropy(self, password: str) -> Tuple[PasswordStrength, float]:
        """Calculate password strength and entropy."""
        if not password:
            return PasswordStrength.VERY_WEAK, 0.0
        
        # Calculate entropy
        char_sets = self._get_available_character_sets()
        charset_size = len("".join(char_sets.values()))
        
        if charset_size == 0:
            return PasswordStrength.VERY_WEAK, 0.0
        
        entropy = len(password) * math.log2(charset_size)
        
        # Adjust entropy based on patterns and repetitions
        entropy = self._adjust_entropy_for_patterns(password, entropy)
        
        # Determine strength based on entropy
        strength = self._entropy_to_strength(entropy)
        
        return strength, entropy
    
    def _adjust_entropy_for_patterns(self, password: str, base_entropy: float) -> float:
        """Adjust entropy based on detected patterns."""
        adjusted_entropy = base_entropy
        
        # Reduce entropy for repeated characters
        unique_chars = len(set(password))
        if unique_chars < len(password):
            repetition_factor = unique_chars / len(password)
            adjusted_entropy *= repetition_factor
        
        # Reduce entropy for sequential patterns
        sequential_penalty = self._calculate_sequential_penalty(password)
        adjusted_entropy *= (1.0 - sequential_penalty)
        
        return max(0, adjusted_entropy)
    
    def _calculate_sequential_penalty(self, password: str) -> float:
        """Calculate penalty for sequential patterns."""
        if len(password) < 3:
            return 0.0
        
        sequential_count = 0
        
        for i in range(len(password) - 2):
            # Check for ascending sequences
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i+1]) + 1):
                sequential_count += 1
            
            # Check for descending sequences
            if (ord(password[i+1]) == ord(password[i]) - 1 and 
                ord(password[i+2]) == ord(password[i+1]) - 1):
                sequential_count += 1
        
        # Return penalty as fraction of potential sequences
        max_possible_sequences = len(password) - 2
        return min(0.5, sequential_count / max_possible_sequences) if max_possible_sequences > 0 else 0.0
    
    def _entropy_to_strength(self, entropy: float) -> PasswordStrength:
        """Convert entropy to strength level."""
        if entropy < 25:
            return PasswordStrength.VERY_WEAK
        elif entropy < 35:
            return PasswordStrength.WEAK
        elif entropy < 50:
            return PasswordStrength.FAIR
        elif entropy < 70:
            return PasswordStrength.GOOD
        elif entropy < 90:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.EXCELLENT
    
    def _validate_config(self):
        """Validate the current configuration."""
        # Ensure at least one character type is enabled
        if not any([
            self.config.use_uppercase,
            self.config.use_lowercase,
            self.config.use_numbers,
            self.config.use_special
        ]):
            self.config.use_lowercase = True
    
    def _validate_constraints(self) -> Tuple[bool, List[str]]:
        """Validate that constraints are satisfiable."""
        warnings = []
        
        # Check if any character types are enabled
        enabled_types = sum([
            self.config.use_uppercase,
            self.config.use_lowercase,
            self.config.use_numbers,
            self.config.use_special
        ])
        
        if enabled_types == 0:
            return False, ["At least one character type must be enabled"]
        
        # Calculate minimum required length
        min_required = (
            (self.config.min_uppercase if self.config.use_uppercase else 0) +
            (self.config.min_lowercase if self.config.use_lowercase else 0) +
            (self.config.min_numbers if self.config.use_numbers else 0) +
            (self.config.min_special if self.config.use_special else 0)
        )
        
        if min_required > self.config.length:
            return False, [f"Minimum requirements ({min_required}) exceed password length ({self.config.length})"]
        
        # Check if character sets have enough characters after filtering
        char_sets = self._get_available_character_sets()
        
        if self.config.use_uppercase and not char_sets.get("uppercase"):
            warnings.append("No uppercase characters available after filtering")
        
        if self.config.use_lowercase and not char_sets.get("lowercase"):
            warnings.append("No lowercase characters available after filtering")
        
        if self.config.use_numbers and not char_sets.get("numbers"):
            warnings.append("No numbers available after filtering")
        
        if self.config.use_special and not char_sets.get("special"):
            warnings.append("No special characters available after filtering")
        
        # Check for conflicting min/max constraints
        def check_min_max(min_val, max_val, name):
            if max_val is not None and min_val > max_val:
                warnings.append(f"Minimum {name} ({min_val}) exceeds maximum {name} ({max_val})")
        
        check_min_max(self.config.min_uppercase, self.config.max_uppercase, "uppercase")
        check_min_max(self.config.min_lowercase, self.config.max_lowercase, "lowercase")
        check_min_max(self.config.min_numbers, self.config.max_numbers, "numbers")
        check_min_max(self.config.min_special, self.config.max_special, "special")
        
        return True, warnings
    
    def get_strength_description(self, strength: PasswordStrength) -> str:
        """Get human-readable strength description."""
        descriptions = {
            PasswordStrength.VERY_WEAK: "Very Weak",
            PasswordStrength.WEAK: "Weak",
            PasswordStrength.FAIR: "Fair",
            PasswordStrength.GOOD: "Good",
            PasswordStrength.STRONG: "Strong",
            PasswordStrength.EXCELLENT: "Excellent"
        }
        return descriptions.get(strength, "Unknown")
    
    def get_strength_color(self, strength: PasswordStrength) -> str:
        """Get color hex code for strength level."""
        colors = {
            PasswordStrength.VERY_WEAK: "#dc3545",   # Red
            PasswordStrength.WEAK: "#fd7e14",       # Orange
            PasswordStrength.FAIR: "#ffc107",       # Yellow
            PasswordStrength.GOOD: "#17a2b8",       # Cyan
            PasswordStrength.STRONG: "#28a745",     # Green
            PasswordStrength.EXCELLENT: "#6f42c1"   # Purple
        }
        return colors.get(strength, "#6c757d")

# Predefined presets
PRESETS = {
    "High Security": PasswordConfig(
        length=20,
        use_uppercase=True,
        use_lowercase=True,
        use_numbers=True,
        use_special=True,
        min_uppercase=2,
        min_lowercase=2,
        min_numbers=2,
        min_special=2,
        exclude_ambiguous=True
    ),
    
    "Memorable": PasswordConfig(
        length=12,
        use_uppercase=True,
        use_lowercase=True,
        use_numbers=True,
        use_special=False,
        min_uppercase=1,
        min_lowercase=1,
        min_numbers=1
    ),
    
    "PIN": PasswordConfig(
        length=6,
        use_uppercase=False,
        use_lowercase=False,
        use_numbers=True,
        use_special=False
    ),
    
    "Web Safe": PasswordConfig(
        length=16,
        use_uppercase=True,
        use_lowercase=True,
        use_numbers=True,
        use_special=True,
        special_chars="!@#$%&*",  # More compatible special chars
        min_uppercase=1,
        min_lowercase=1,
        min_numbers=1,
        min_special=1,
        exclude_ambiguous=True
    ),
    
    "Maximum Security": PasswordConfig(
        length=32,
        use_uppercase=True,
        use_lowercase=True,
        use_numbers=True,
        use_special=True,
        min_uppercase=4,
        min_lowercase=4,
        min_numbers=4,
        min_special=4,
        exclude_ambiguous=True,
        exclude_similar=True
    )
}
