import math

BASE_DECAY_RATE = 0.003
MAX_DECAY_DAYS = 365
MAX_HEALTH = 100
MIN_HEALTH = 0
RECOVERY_RATE = 0.25  # 25% recovery toward baseline


def compute_decay_score(
    days_since_last_use: int,
    usage_frequency: float,
    skill_level: str,
    previous_health: float = None
) -> float:
    """
    Cognitive Skill Model (Final Stable Version)

    - Level defines baseline mastery
    - Exponential forgetting from baseline
    - Gradual bounded recovery toward baseline (NOT 100)
    - Small consistency bonus
    """

    # --------------------------------
    # 🎯 Level-Based Baseline
    # --------------------------------
    baseline_map = {
        "beginner": 60,
        "intermediate": 75,
        "advanced": 90
    }

    baseline = baseline_map.get(
        skill_level.lower() if skill_level else "intermediate",
        75
    )

    # --------------------------------
    # 📉 Exponential Forgetting
    # --------------------------------
    effective_days = min(days_since_last_use, MAX_DECAY_DAYS)

    decay_multiplier = math.exp(-BASE_DECAY_RATE * effective_days)
    decayed_health = baseline * decay_multiplier

    # --------------------------------
    # 📈 Controlled Recovery
    # --------------------------------
    if previous_health is not None and days_since_last_use == 0:
        # Recover only part of the gap toward BASELINE
        recovered = previous_health + RECOVERY_RATE * (baseline - previous_health)
        health = recovered
    else:
        health = decayed_health

    # --------------------------------
    # 📊 Small Usage Bonus
    # --------------------------------
    usage_bonus = min(usage_frequency * 3, 5)
    health += usage_bonus

    # --------------------------------
    # 🔒 Clamp Final Value
    # --------------------------------
    final_score = round(
        max(MIN_HEALTH, min(MAX_HEALTH, health)),
        2
    )

    # Debug Logs
    print("DEBUG → baseline:", baseline)
    print("DEBUG → previous_health:", previous_health)
    print("DEBUG → days:", days_since_last_use)
    print("DEBUG → final_score:", final_score)

    return final_score