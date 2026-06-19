# -*- coding: utf-8 -*-
"""
??????? - ??????vs?????lambda?????????
"""
import json, os, math
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(DATA_DIR, "history", "prediction_history.json")
LEARNING_FILE = os.path.join(DATA_DIR, "history", "learning_params.json")

# Default learning parameters
DEFAULT_PARAMS = {
    "lambda_correction": {},  # {team: correction_factor} 
    "bayesian_weight": 0.7,   # How much to trust new evidence vs prior
    "total_predictions": 0,
    "correct_predictions": 0,  # Direction correct (W/D/L)
    "exact_scores": 0,
    "accuracy_by_confidence": {"high": [0,0], "medium": [0,0], "low": [0,0]},  # [correct, total]
    "upset_detected": 0,       # Correctly predicted upsets
    "upset_missed": 0,         # Failed to predict upsets
    "last_updated": ""
}

class SelfLearner:
    def __init__(self):
        self.params = self._load_params()
        self.history = self._load_history()
    
    def _load_params(self):
        if os.path.exists(LEARNING_FILE):
            try:
                with open(LEARNING_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return dict(DEFAULT_PARAMS)
    
    def _save_params(self):
        os.makedirs(os.path.dirname(LEARNING_FILE), exist_ok=True)
        self.params["last_updated"] = datetime.now().isoformat()
        with open(LEARNING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.params, f, ensure_ascii=False, indent=2)
    
    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_history(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def record_prediction(self, home, away, pred_win, pred_draw, pred_lose, pred_score, confidence):
        """Record a prediction for later review"""
        record = {
            "home": home,
            "away": away,
            "pred_win": pred_win,
            "pred_draw": pred_draw,
            "pred_lose": pred_lose,
            "pred_score": pred_score,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "actual_score": None,
            "actual_result": None,
            "reviewed": False
        }
        self.history.append(record)
        self._save_history()
        return record
    
    def review_result(self, home, away, actual_score):
        """Compare prediction with actual result and learn"""
        # Find the prediction
        pred = None
        for p in reversed(self.history):
            if p["home"] == home and p["away"] == away and not p["reviewed"]:
                pred = p
                break
        
        if not pred:
            return {"error": "No prediction found for this match"}
        
        # Parse actual score
        try:
            h_goals, a_goals = map(int, actual_score.split("-"))
        except:
            return {"error": "Invalid score format, use 'H-A'"}
        
        # Determine actual result
        if h_goals > a_goals:
            actual_result = "W"
        elif h_goals == a_goals:
            actual_result = "D"
        else:
            actual_result = "L"
        
        # Determine predicted result
        max_prob = max(pred["pred_win"], pred["pred_draw"], pred["pred_lose"])
        if max_prob == pred["pred_win"]:
            pred_result = "W"
        elif max_prob == pred["pred_draw"]:
            pred_result = "D"
        else:
            pred_result = "L"
        
        # Update record
        pred["actual_score"] = actual_score
        pred["actual_result"] = actual_result
        pred["reviewed"] = True
        pred["correct_direction"] = (pred_result == actual_result)
        pred["exact_score"] = (pred["pred_score"] == actual_score)
        
        # Update learning parameters
        self.params["total_predictions"] += 1
        
        if pred["correct_direction"]:
            self.params["correct_predictions"] += 1
        
        if pred["exact_score"]:
            self.params["exact_scores"] += 1
        
        # Accuracy by confidence
        conf_level = "high" if pred["confidence"] >= 65 else ("medium" if pred["confidence"] >= 45 else "low")
        self.params["accuracy_by_confidence"][conf_level][1] += 1
        if pred["correct_direction"]:
            self.params["accuracy_by_confidence"][conf_level][0] += 1
        
        # Upset detection
        is_upset = (max_prob < 50)  # Underdog won
        if is_upset and pred["correct_direction"]:
            self.params["upset_detected"] += 1
        elif is_upset and not pred["correct_direction"]:
            self.params["upset_missed"] += 1
        
        # Adjust lambda correction
        team_key = home
        if team_key not in self.params["lambda_correction"]:
            self.params["lambda_correction"][team_key] = 0.0
        
        # If we overestimated home (predicted win but lost), reduce home lambda
        if pred_result == "W" and actual_result == "L":
            self.params["lambda_correction"][team_key] -= 0.05
        elif pred_result == "L" and actual_result == "W":
            self.params["lambda_correction"][team_key] += 0.05
        
        # Adjust Bayesian weight based on accuracy trend
        recent = [p for p in self.history if p["reviewed"]][-20:]
        if len(recent) >= 5:
            recent_correct = sum(1 for p in recent if p["correct_direction"])
            recent_accuracy = recent_correct / len(recent)
            # Slightly adjust weight: if accurate, trust prior more; if inaccurate, trust evidence more
            self.params["bayesian_weight"] = round(0.5 + recent_accuracy * 0.4, 2)
        
        self._save_history()
        self._save_params()
        
        # Calculate stats
        stats = self.get_stats()
        
        return {
            "home": home,
            "away": away,
            "predicted_result": pred_result,
            "actual_result": actual_result,
            "predicted_score": pred["pred_score"],
            "actual_score": actual_score,
            "direction_correct": pred["correct_direction"],
            "exact_score_match": pred["exact_score"],
            "lambda_correction": self.params["lambda_correction"].get(home, 0),
            "bayesian_weight": self.params["bayesian_weight"],
            "stats": stats
        }
    
    def get_stats(self):
        """Get learning statistics"""
        total = self.params["total_predictions"]
        correct = self.params["correct_predictions"]
        accuracy = round(correct / max(total, 1) * 100, 1)
        
        # By confidence
        conf_accuracy = {}
        for level, counts in self.params["accuracy_by_confidence"].items():
            c, t = counts
            conf_accuracy[level] = round(c / max(t, 1) * 100, 1)
        
        return {
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "exact_scores": self.params["exact_scores"],
            "upset_detected": self.params["upset_detected"],
            "upset_missed": self.params["upset_missed"],
            "bayesian_weight": self.params["bayesian_weight"],
            "confidence_accuracy": conf_accuracy,
            "last_updated": self.params["last_updated"]
        }
    
    def get_team_correction(self, team):
        """Get lambda correction factor for a team"""
        return self.params["lambda_correction"].get(team, 0.0)
    
    def apply_correction(self, base_lambda, team):
        """Apply learned correction to base lambda"""
        correction = self.get_team_correction(team)
        return max(0.1, base_lambda + correction)

# Global instance
learner = SelfLearner()
