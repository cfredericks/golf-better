"""Tests for fantasy scoring calculations."""

from fantasy_scoring import (
    calculate_hole_score,
    calculate_streak_bonus,
    calculate_bounce_back,
    calculate_bogey_free_round,
    calculate_position_bonus,
    calculate_player_score,
    DEFAULT_SCORING_CONFIG,
)


class TestHoleScoring:
    def test_eagle_or_better(self):
        assert calculate_hole_score(-2, DEFAULT_SCORING_CONFIG) == 8
        assert calculate_hole_score(-3, DEFAULT_SCORING_CONFIG) == 8  # Albatross

    def test_birdie(self):
        assert calculate_hole_score(-1, DEFAULT_SCORING_CONFIG) == 3

    def test_par(self):
        assert calculate_hole_score(0, DEFAULT_SCORING_CONFIG) == 0.5

    def test_bogey(self):
        assert calculate_hole_score(1, DEFAULT_SCORING_CONFIG) == -0.5

    def test_double_bogey_or_worse(self):
        assert calculate_hole_score(2, DEFAULT_SCORING_CONFIG) == -1
        assert calculate_hole_score(3, DEFAULT_SCORING_CONFIG) == -1


class TestStreakBonus:
    def test_no_streak(self):
        scores = [-1, 0, -1, 0, -1]
        assert calculate_streak_bonus(scores, DEFAULT_SCORING_CONFIG) == 0

    def test_three_birdie_streak(self):
        scores = [-1, -1, -1, 0, 0]
        assert calculate_streak_bonus(scores, DEFAULT_SCORING_CONFIG) == 3

    def test_five_birdie_streak(self):
        scores = [-1, -1, -1, -1, -1, 0]
        # Gets +3 at 3rd birdie and +5 at 5th
        assert calculate_streak_bonus(scores, DEFAULT_SCORING_CONFIG) == 8

    def test_streak_broken_by_par(self):
        scores = [-1, -1, 0, -1, -1, -1]
        # Second streak of 3 birdies
        assert calculate_streak_bonus(scores, DEFAULT_SCORING_CONFIG) == 3


class TestBounceBack:
    def test_bounce_back(self):
        scores = [1, -1, 0, 0]  # Bogey followed by birdie
        assert calculate_bounce_back(scores, DEFAULT_SCORING_CONFIG) == 2

    def test_no_bounce_back(self):
        scores = [-1, 1, 0, 0]  # Birdie followed by bogey
        assert calculate_bounce_back(scores, DEFAULT_SCORING_CONFIG) == 0

    def test_double_bounce_back_after_double(self):
        scores = [2, -1, 0, 0]  # Double bogey followed by birdie
        assert calculate_bounce_back(scores, DEFAULT_SCORING_CONFIG) == 2

    def test_multiple_bounce_backs(self):
        scores = [1, -1, 1, -1]  # Two bounce backs
        assert calculate_bounce_back(scores, DEFAULT_SCORING_CONFIG) == 4


class TestBogeyFreeRound:
    def test_bogey_free_round(self):
        scores = [0] * 18  # All pars
        assert calculate_bogey_free_round(scores, DEFAULT_SCORING_CONFIG) == 3

    def test_bogey_free_with_birdies(self):
        scores = [-1, -1, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0]
        assert calculate_bogey_free_round(scores, DEFAULT_SCORING_CONFIG) == 3

    def test_has_bogey(self):
        scores = [0] * 17 + [1]  # 17 pars and 1 bogey
        assert calculate_bogey_free_round(scores, DEFAULT_SCORING_CONFIG) == 0

    def test_incomplete_round(self):
        scores = [0] * 9  # Only front 9
        assert calculate_bogey_free_round(scores, DEFAULT_SCORING_CONFIG) == 0


class TestPositionBonus:
    def test_first_place(self):
        assert calculate_position_bonus(1, DEFAULT_SCORING_CONFIG) == 30

    def test_second_place(self):
        assert calculate_position_bonus(2, DEFAULT_SCORING_CONFIG) == 20

    def test_third_place(self):
        assert calculate_position_bonus(3, DEFAULT_SCORING_CONFIG) == 18

    def test_top_10(self):
        assert calculate_position_bonus(6, DEFAULT_SCORING_CONFIG) == 10
        assert calculate_position_bonus(10, DEFAULT_SCORING_CONFIG) == 10

    def test_top_20(self):
        assert calculate_position_bonus(11, DEFAULT_SCORING_CONFIG) == 5
        assert calculate_position_bonus(20, DEFAULT_SCORING_CONFIG) == 5

    def test_top_30(self):
        assert calculate_position_bonus(21, DEFAULT_SCORING_CONFIG) == 3
        assert calculate_position_bonus(30, DEFAULT_SCORING_CONFIG) == 3

    def test_made_cut(self):
        assert calculate_position_bonus(31, DEFAULT_SCORING_CONFIG) == 1
        assert calculate_position_bonus(70, DEFAULT_SCORING_CONFIG) == 1

    def test_no_position(self):
        assert calculate_position_bonus(0, DEFAULT_SCORING_CONFIG) == 0


class TestPlayerScore:
    def test_simple_round(self):
        scorecard = {
            "rounds": [{
                "holes": [
                    {"holeNumber": 1, "par": 4, "score": 4, "scoreToPar": 0},
                    {"holeNumber": 2, "par": 4, "score": 3, "scoreToPar": -1},
                    {"holeNumber": 3, "par": 3, "score": 3, "scoreToPar": 0},
                ]
            }]
        }
        leaderboard = {"position": 10}

        result = calculate_player_score(scorecard, leaderboard, DEFAULT_SCORING_CONFIG)

        assert result["breakdown"]["birdies"] == 1
        assert result["breakdown"]["pars"] == 2
        assert result["breakdown"]["positionBonus"] == 10
        # 2 pars (1.0) + 1 birdie (3.0) + position (10) = 14.0
        assert result["score"] == 14.0

    def test_with_position_string(self):
        scorecard = {"rounds": []}
        leaderboard = {"position": "T5"}

        result = calculate_player_score(scorecard, leaderboard, DEFAULT_SCORING_CONFIG)

        assert result["breakdown"]["positionBonus"] == 14
        assert result["score"] == 14.0
