"""IRT (Item Response Theory) Service — manages item calibration and learner ability estimation."""

from __future__ import annotations

import math
from typing import List, Dict

class IRTService:
    """Implements basic Rasch Model (1PL IRT) for item calibration."""

    @staticmethod
    def estimate_ability(responses: List[Dict[str, Any]], items: List[Dict[str, Any]]) -> float:
        """
        Estimate learner ability (theta) based on responses and item difficulty.
        responses: list of {"item_id": str, "correct": bool}
        items: list of {"item_id": str, "difficulty": float}
        """
        if not responses:
            return 0.0

        # Simple MLE estimation for Rasch model (simplified)
        correct_count = sum(1 for r in responses if r["correct"])
        total_count = len(responses)
        
        if correct_count == 0:
            return -3.0 # Floor
        if correct_count == total_count:
            return 3.0  # Ceiling
        
        # Logit of success rate adjusted by average difficulty
        avg_difficulty = sum(i["difficulty"] for i in items) / len(items)
        success_rate = correct_count / total_count
        ability = math.log(success_rate / (1 - success_rate)) + avg_difficulty
        
        return round(ability, 2)

    @staticmethod
    def calibrate_item(current_difficulty: float, learner_ability: float, was_correct: bool, learning_rate: float = 0.1) -> float:
        """
        Adjust item difficulty based on a single response (Stochastic Gradient Descent approach).
        If a high-ability learner fails, the item is harder than thought (difficulty increases).
        If a low-ability learner succeeds, the item is easier than thought (difficulty decreases).
        """
        # Probability of correct response according to Rasch model
        prob_correct = 1 / (1 + math.exp(-(learner_ability - current_difficulty)))
        
        actual = 1.0 if was_correct else 0.0
        # Update difficulty (sign is positive because harder items have higher difficulty)
        new_difficulty = current_difficulty + learning_rate * (prob_correct - actual)
        
        return round(new_difficulty, 3)
