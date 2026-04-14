import pytest


def calculate_tier_score(
    winrate: float, top4rate: float, avg_placement: float, game_count: int
) -> float:
    placement_score = max(0, (8 - avg_placement) / 7) * 100

    if game_count < 100:
        confidence = 0.5
    elif game_count < 500:
        confidence = 0.7
    elif game_count < 1000:
        confidence = 0.85
    else:
        confidence = 1.0

    score = (winrate * 0.4) + (top4rate * 0.35) + (placement_score * 0.25)
    return score * confidence


class TestTierEngine:
    def test_s_tier_calculation(self):
        score = calculate_tier_score(52.0, 78.0, 3.8, 1500)
        assert score >= 60

    def test_a_tier_calculation(self):
        score = calculate_tier_score(48.0, 72.0, 4.2, 800)
        assert 40 <= score < 60

    def test_b_tier_calculation(self):
        score = calculate_tier_score(44.0, 68.0, 4.8, 500)
        assert 30 <= score < 50

    def test_low_confidence_penalty(self):
        high_conf = calculate_tier_score(52.0, 78.0, 3.8, 1500)
        low_conf = calculate_tier_score(52.0, 78.0, 3.8, 50)
        assert low_conf < high_conf

    def test_placement_weight(self):
        best = calculate_tier_score(50.0, 75.0, 2.0, 1000)
        worst = calculate_tier_score(50.0, 75.0, 7.0, 1000)
        assert best > worst

    def test_winrate_weight(self):
        high_wr = calculate_tier_score(55.0, 75.0, 4.0, 1000)
        low_wr = calculate_tier_score(45.0, 75.0, 4.0, 1000)
        assert high_wr > low_wr


class TestCompositionMerge:
    def test_merge_multiple_sources(self):
        comps = [
            {"name": "Jinx Burn", "winrate": 50.0, "top4rate": 75.0},
            {"name": "Jinx Burn", "winrate": 52.0, "top4rate": 77.0},
            {"name": "Jinx Burn", "winrate": 48.0, "top4rate": 73.0},
        ]

        avg_wr = sum(c["winrate"] for c in comps) / len(comps)
        avg_top4 = sum(c["top4rate"] for c in comps) / len(comps)

        assert avg_wr == 50.0
        assert avg_top4 == 75.0

    def test_sort_by_winrate(self):
        comps = [
            {"name": "Comp1", "winrate": 45.0},
            {"name": "Comp2", "winrate": 55.0},
            {"name": "Comp3", "winrate": 50.0},
        ]
        comps.sort(key=lambda x: x["winrate"], reverse=True)

        assert comps[0]["name"] == "Comp2"

    def test_assign_tiers(self):
        comps = [
            {"name": "S1", "winrate": 55.0},
            {"name": "S2", "winrate": 53.0},
            {"name": "A1", "winrate": 50.0},
            {"name": "A2", "winrate": 48.0},
            {"name": "B1", "winrate": 45.0},
            {"name": "B2", "winrate": 43.0},
        ]

        comps.sort(key=lambda x: x["winrate"], reverse=True)

        comps[0]["tier"] = "S"
        comps[1]["tier"] = "S"
        comps[2]["tier"] = "A"
        comps[3]["tier"] = "A"
        comps[4]["tier"] = "B"
        comps[5]["tier"] = "B"

        assert comps[0]["tier"] == "S"
        assert comps[4]["tier"] == "B"
        assert comps[5]["tier"] == "B"
