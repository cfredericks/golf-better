"""Fantasy scoring calculation service using PGA Tour Fantasy-style rules."""

from typing import Dict, List, Any
import json


DEFAULT_SCORING_CONFIG = {
    "eagle_or_better": 8,
    "birdie": 3,
    "par": 0.5,
    "bogey": -0.5,
    "double_bogey_or_worse": -1,
    "streak_bonus_3": 3,
    "streak_bonus_5": 5,
    "bounce_back": 2,
    "bogey_free_round": 3,
    "position_1": 30,
    "position_2": 20,
    "position_3": 18,
    "position_4": 16,
    "position_5": 14,
    "position_6_10": 10,
    "position_11_20": 5,
    "position_21_30": 3,
    "made_cut": 1,
}


def calculate_hole_score(score_to_par: int, scoring_config: Dict) -> float:
    """Calculate points for a single hole based on score to par."""
    if score_to_par <= -2:
        return scoring_config.get("eagle_or_better", 8)
    elif score_to_par == -1:
        return scoring_config.get("birdie", 3)
    elif score_to_par == 0:
        return scoring_config.get("par", 0.5)
    elif score_to_par == 1:
        return scoring_config.get("bogey", -0.5)
    else:
        return scoring_config.get("double_bogey_or_worse", -1)


def calculate_streak_bonus(scores_to_par: List[int], scoring_config: Dict) -> float:
    """Calculate streak bonus for consecutive birdies or better."""
    bonus = 0.0
    streak = 0

    for score in scores_to_par:
        if score <= -1:  # Birdie or better
            streak += 1
            if streak == 3:
                bonus += scoring_config.get("streak_bonus_3", 3)
            elif streak == 5:
                bonus += scoring_config.get("streak_bonus_5", 5)
        else:
            streak = 0

    return bonus


def calculate_bounce_back(scores_to_par: List[int], scoring_config: Dict) -> float:
    """Calculate bounce back bonus (birdie after bogey or worse)."""
    bonus = 0.0

    for i in range(1, len(scores_to_par)):
        if scores_to_par[i - 1] >= 1 and scores_to_par[i] <= -1:
            bonus += scoring_config.get("bounce_back", 2)

    return bonus


def calculate_bogey_free_round(scores_to_par: List[int], scoring_config: Dict) -> float:
    """Calculate bonus for a bogey-free round."""
    if len(scores_to_par) >= 18 and all(s <= 0 for s in scores_to_par):
        return scoring_config.get("bogey_free_round", 3)
    return 0.0


def calculate_position_bonus(position: int, scoring_config: Dict) -> float:
    """Calculate bonus points for finishing position."""
    if position == 1:
        return scoring_config.get("position_1", 30)
    elif position == 2:
        return scoring_config.get("position_2", 20)
    elif position == 3:
        return scoring_config.get("position_3", 18)
    elif position == 4:
        return scoring_config.get("position_4", 16)
    elif position == 5:
        return scoring_config.get("position_5", 14)
    elif 6 <= position <= 10:
        return scoring_config.get("position_6_10", 10)
    elif 11 <= position <= 20:
        return scoring_config.get("position_11_20", 5)
    elif 21 <= position <= 30:
        return scoring_config.get("position_21_30", 3)
    elif position > 0:  # Made cut but outside top 30
        return scoring_config.get("made_cut", 1)
    return 0.0


def calculate_player_score(
    scorecard_data: Dict,
    leaderboard_data: Dict,
    scoring_config: Dict
) -> Dict[str, Any]:
    """
    Calculate fantasy score for a player in a tournament.

    Args:
        scorecard_data: Player's scorecard data with round-by-round scores
        leaderboard_data: Player's leaderboard data with position
        scoring_config: League's scoring configuration

    Returns:
        Dict with score breakdown and total
    """
    breakdown = {
        "eagles": 0,
        "birdies": 0,
        "pars": 0,
        "bogeys": 0,
        "doubleBogeys": 0,
        "streakBonus": 0.0,
        "bounceBack": 0.0,
        "bogeyFreeRounds": 0,
        "positionBonus": 0.0,
    }
    total_score = 0.0

    # Process scorecards if available
    if scorecard_data and "rounds" in scorecard_data:
        for round_data in scorecard_data.get("rounds", []):
            scores_to_par = []
            round_has_bogey = False

            for hole in round_data.get("holes", []):
                score_to_par = hole.get("scoreToPar", hole.get("score", 0) - hole.get("par", 0))
                scores_to_par.append(score_to_par)

                # Count by type
                if score_to_par <= -2:
                    breakdown["eagles"] += 1
                elif score_to_par == -1:
                    breakdown["birdies"] += 1
                elif score_to_par == 0:
                    breakdown["pars"] += 1
                elif score_to_par == 1:
                    breakdown["bogeys"] += 1
                    round_has_bogey = True
                else:
                    breakdown["doubleBogeys"] += 1
                    round_has_bogey = True

                # Add hole score
                total_score += calculate_hole_score(score_to_par, scoring_config)

            # Calculate round bonuses
            if scores_to_par:
                streak_bonus = calculate_streak_bonus(scores_to_par, scoring_config)
                breakdown["streakBonus"] += streak_bonus
                total_score += streak_bonus

                bounce_back = calculate_bounce_back(scores_to_par, scoring_config)
                breakdown["bounceBack"] += bounce_back
                total_score += bounce_back

                if not round_has_bogey and len(scores_to_par) >= 18:
                    breakdown["bogeyFreeRounds"] += 1
                    bogey_free_bonus = scoring_config.get("bogey_free_round", 3)
                    total_score += bogey_free_bonus

    # Add position bonus
    if leaderboard_data:
        position = leaderboard_data.get("position", 0)
        if isinstance(position, str):
            # Handle tied positions like "T5"
            position = int(position.replace("T", "").replace("CUT", "0"))
        position_bonus = calculate_position_bonus(position, scoring_config)
        breakdown["positionBonus"] = position_bonus
        total_score += position_bonus

    return {
        "breakdown": breakdown,
        "score": round(total_score, 2),
    }


def calculate_fantasy_scores(
    picks: List[Dict],
    scorecards: Dict[str, Dict],
    leaderboard: Dict[str, Dict],
    scoring_config: Dict
) -> List[Dict[str, Any]]:
    """
    Calculate fantasy scores for all picked players.

    Args:
        picks: List of tournament picks
        scorecards: Dict mapping player_id to scorecard data
        leaderboard: Dict mapping player_id to leaderboard data
        scoring_config: League's scoring configuration

    Returns:
        List of player scores with breakdowns
    """
    player_scores = []

    for pick in picks:
        player_id = pick.get("player_id")
        scorecard = scorecards.get(player_id, {})
        leaderboard_entry = leaderboard.get(player_id, {})

        result = calculate_player_score(scorecard, leaderboard_entry, scoring_config)

        player_scores.append({
            "playerId": player_id,
            "playerName": pick.get("player_name", leaderboard_entry.get("playerName", "Unknown")),
            "score": result["score"],
            "breakdown": result["breakdown"],
        })

    return player_scores


def serialize_scoring_config(config: Dict) -> str:
    """Serialize scoring config to JSON string for database storage."""
    return json.dumps(config)


def deserialize_scoring_config(config_str: str) -> Dict:
    """Deserialize scoring config from JSON string."""
    if isinstance(config_str, dict):
        return config_str
    return json.loads(config_str) if config_str else DEFAULT_SCORING_CONFIG
