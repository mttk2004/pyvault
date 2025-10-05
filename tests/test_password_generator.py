#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from utils.password_generator import PasswordGenerator, PasswordStrength, PasswordConfig, PRESETS


class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = PasswordGenerator()

    def test_default_initialization(self):
        """Test that the password generator initializes with correct default values."""
        self.assertEqual(self.generator.config.length, 16)
        self.assertTrue(self.generator.config.use_uppercase)
        self.assertTrue(self.generator.config.use_lowercase)
        self.assertTrue(self.generator.config.use_numbers)
        self.assertTrue(self.generator.config.use_special)

    def test_custom_configuration(self):
        """Test initialization with custom configuration."""
        config = PasswordConfig(
            length=20,
            use_uppercase=False,
            min_numbers=3,
            custom_excluded="abc"
        )
        gen = PasswordGenerator(config)
        self.assertEqual(gen.config.length, 20)
        self.assertFalse(gen.config.use_uppercase)
        self.assertEqual(gen.config.min_numbers, 3)
        self.assertEqual(gen.config.custom_excluded, "abc")

    def test_password_generation(self):
        """Test basic password generation."""
        result = self.generator.generate_password()
        
        # Check that we got a valid result
        self.assertIsNotNone(result.password)
        self.assertEqual(len(result.password), 16)  # Default length
        self.assertTrue(result.satisfied_constraints)
        self.assertIsInstance(result.strength, PasswordStrength)
        self.assertGreater(result.entropy, 0)

    def test_password_length_variations(self):
        """Test that generated passwords have correct lengths."""
        for length in [8, 12, 20, 32]:
            config = PasswordConfig(length=length)
            gen = PasswordGenerator(config)
            result = gen.generate_password()
            self.assertEqual(len(result.password), length)

    def test_character_type_inclusion(self):
        """Test that generated passwords contain required character types."""
        config = PasswordConfig(
            length=16,
            min_uppercase=1,
            min_lowercase=1,
            min_numbers=1,
            min_special=1
        )
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        
        password = result.password
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in gen.config.special_chars for c in password))

    def test_character_exclusion(self):
        """Test that excluded characters are properly removed."""
        config = PasswordConfig(
            custom_excluded="aeiou123",
            length=20
        )
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        
        for char in "aeiou123":
            self.assertNotIn(char, result.password)

    def test_ambiguous_character_exclusion(self):
        """Test that ambiguous characters are excluded when requested."""
        config = PasswordConfig(exclude_ambiguous=True)
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        
        ambiguous_chars = "0OoIl1"
        for char in ambiguous_chars:
            self.assertNotIn(char, result.password)

    def test_minimum_constraints(self):
        """Test that minimum character constraints are satisfied."""
        config = PasswordConfig(
            length=20,
            min_uppercase=3,
            min_lowercase=4,
            min_numbers=2,
            min_special=1
        )
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        
        distribution = result.character_distribution
        self.assertGreaterEqual(distribution["uppercase"], 3)
        self.assertGreaterEqual(distribution["lowercase"], 4)
        self.assertGreaterEqual(distribution["numbers"], 2)
        self.assertGreaterEqual(distribution["special"], 1)

    def test_constraint_validation(self):
        """Test constraint validation."""
        # Valid constraints should pass
        result = self.generator._validate_constraints()
        self.assertTrue(result[0])
        
        # Invalid constraints (sum exceeds length) should fail
        config = PasswordConfig(
            length=5,
            min_uppercase=3,
            min_lowercase=3,
            min_numbers=3,
            min_special=3
        )
        gen = PasswordGenerator(config)
        result = gen._validate_constraints()
        self.assertFalse(result[0])

    def test_strength_calculation(self):
        """Test password strength calculation."""
        # Short, simple password should be weak
        config = PasswordConfig(
            length=6,
            use_uppercase=False,
            use_special=False
        )
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        self.assertIn(result.strength, [PasswordStrength.VERY_WEAK, PasswordStrength.WEAK])
        
        # Long, complex password should be strong
        config = PasswordConfig(
            length=24,
            min_uppercase=2,
            min_lowercase=2,
            min_numbers=2,
            min_special=2
        )
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        self.assertIn(result.strength, [PasswordStrength.GOOD, PasswordStrength.STRONG, PasswordStrength.EXCELLENT])

    def test_strength_descriptions_and_colors(self):
        """Test that strength descriptions and colors are correct."""
        gen = PasswordGenerator()
        
        self.assertEqual(gen.get_strength_description(PasswordStrength.VERY_WEAK), "Very Weak")
        self.assertEqual(gen.get_strength_description(PasswordStrength.WEAK), "Weak")
        self.assertEqual(gen.get_strength_description(PasswordStrength.FAIR), "Fair")
        self.assertEqual(gen.get_strength_description(PasswordStrength.GOOD), "Good")
        self.assertEqual(gen.get_strength_description(PasswordStrength.STRONG), "Strong")
        self.assertEqual(gen.get_strength_description(PasswordStrength.EXCELLENT), "Excellent")
        
        # Test colors are valid hex codes
        for strength in PasswordStrength:
            color = gen.get_strength_color(strength)
            self.assertTrue(color.startswith("#"))
            self.assertEqual(len(color), 7)

    def test_character_distribution_analysis(self):
        """Test character distribution analysis."""
        password = "Abc123!@#"
        distribution = self.generator._get_character_distribution(password)
        
        self.assertEqual(distribution["uppercase"], 1)
        self.assertEqual(distribution["lowercase"], 2)
        self.assertEqual(distribution["numbers"], 3)
        self.assertEqual(distribution["special"], 3)

    def test_built_in_presets(self):
        """Test that built-in presets exist and work correctly."""
        # Check that presets dictionary exists and contains expected presets
        expected_presets = ["High Security", "Memorable", "PIN", "Web Safe", "Maximum Security"]
        for preset_name in expected_presets:
            self.assertIn(preset_name, PRESETS)
        
        # Test PIN preset specifically
        pin_config = PRESETS["PIN"]
        gen = PasswordGenerator(pin_config)
        result = gen.generate_password()
        
        # PIN should be all numbers
        self.assertEqual(len(result.password), 6)
        self.assertTrue(result.password.isdigit())

    def test_preset_application(self):
        """Test applying presets to generator."""
        # Test with High Security preset
        high_sec_config = PRESETS["High Security"]
        gen = PasswordGenerator(high_sec_config)
        result = gen.generate_password()
        
        self.assertEqual(len(result.password), 20)
        self.assertTrue(result.satisfied_constraints)
        
        # Should contain all character types with minimum requirements
        distribution = result.character_distribution
        self.assertGreaterEqual(distribution["uppercase"], 2)
        self.assertGreaterEqual(distribution["lowercase"], 2)
        self.assertGreaterEqual(distribution["numbers"], 2)
        self.assertGreaterEqual(distribution["special"], 2)

    def test_multiple_password_uniqueness(self):
        """Test that multiple generated passwords are unique."""
        passwords = []
        for _ in range(20):
            result = self.generator.generate_password()
            passwords.append(result.password)
        
        # All passwords should be unique (highly probable with good entropy)
        self.assertEqual(len(passwords), len(set(passwords)))

    def test_invalid_configurations(self):
        """Test handling of invalid configurations."""
        # Test with no character types enabled - should auto-enable lowercase
        config = PasswordConfig(
            use_uppercase=False,
            use_lowercase=False,
            use_numbers=False,
            use_special=False
        )
        gen = PasswordGenerator(config)
        # Should auto-correct to enable at least lowercase
        self.assertTrue(gen.config.use_lowercase)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Minimum reasonable length
        config = PasswordConfig(length=4)
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        self.assertEqual(len(result.password), 4)

        # Very long password
        config = PasswordConfig(length=64)
        gen = PasswordGenerator(config)
        result = gen.generate_password()
        self.assertEqual(len(result.password), 64)


if __name__ == '__main__':
    unittest.main()
