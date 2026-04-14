import pytest

from scraper.validator import (
    validate_composition_data,
    validate_item_data,
    validate_augment_data,
    calculate_confidence_score,
    TIER_VALUES,
)


class TestValidators:
    def test_valid_composition(self, sample_composition):
        assert validate_composition_data(sample_composition) is True

    def test_missing_name(self):
        comp = {"tier": "S", "winrate": 50, "top4rate": 70, "avg_placement": 4}
        assert validate_composition_data(comp) is False

    def test_invalid_tier(self):
        comp = {
            "name": "Test",
            "tier": "X",
            "winrate": 50,
            "top4rate": 70,
            "avg_placement": 4,
        }
        assert validate_composition_data(comp) is False

    def test_invalid_winrate(self):
        comp = {
            "name": "Test",
            "tier": "S",
            "winrate": 150,
            "top4rate": 70,
            "avg_placement": 4,
        }
        assert validate_composition_data(comp) is False

    def test_valid_item(self):
        item = {"name": "Rabadon's Deathcap"}
        assert validate_item_data(item) is True

    def test_missing_item_name(self):
        item = {}
        assert validate_item_data(item) is False

    def test_valid_augment_prismatic(self):
        aug = {"name": "Jeweled Lotus", "tier": "prismatic", "description": "Test"}
        assert validate_augment_data(aug) is True

    def test_valid_augment_gold(self):
        aug = {"name": "Gold", "tier": "gold", "description": "Test"}
        assert validate_augment_data(aug) is True

    def test_valid_augment_silver(self):
        aug = {"name": "Silver", "tier": "silver", "description": "Test"}
        assert validate_augment_data(aug) is True

    def test_invalid_augment_tier(self):
        aug = {"name": "Test", "tier": "bronze", "description": "Test"}
        assert validate_augment_data(aug) is False


class TestConfidenceScore:
    def test_low_games(self):
        comp = {"game_count": 50}
        assert calculate_confidence_score(comp) == 0.5

    def test_medium_games(self):
        comp = {"game_count": 300}
        assert calculate_confidence_score(comp) == 0.7

    def test_high_games(self):
        comp = {"game_count": 800}
        assert calculate_confidence_score(comp) == 0.85

    def test_very_high_games(self):
        comp = {"game_count": 1500}
        assert calculate_confidence_score(comp) == 1.0


class TestTierValues:
    def test_tier_s_value(self):
        assert TIER_VALUES["S"] == 4

    def test_tier_a_value(self):
        assert TIER_VALUES["A"] == 3

    def test_tier_b_value(self):
        assert TIER_VALUES["B"] == 2

    def test_tier_c_value(self):
        assert TIER_VALUES["C"] == 1
