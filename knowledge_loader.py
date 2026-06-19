"""
鐭ヨ瘑搴撳姞杞藉櫒 - 浠庤棰?鏂囨。瀛︿範瓒崇悆鍒嗘瀽鐭ヨ瘑
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class KnowledgeBase:
    def __init__(self):
        self.data = {"videos": [], "tactical_patterns": {}, "team_profiles": {}}
        self.load()
    
    def load(self):
        kb_file = os.path.join(DATA_DIR, "knowledge_base.json")
        try:
            with open(kb_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"[Knowledge] 鍔犺浇 {len(self.data.get('videos',[]))} 鏉¤棰戝垎鏋? {len(self.data.get('team_profiles',{}))} 鏀悆闃熻祫鏂?)
        except:
            print("[Knowledge] 鐭ヨ瘑搴撲负绌?)
    
    def get_team_profile(self, team_name):
        """鑾峰彇鐞冮槦璇︾粏璧勬枡"""
        return self.data.get("team_profiles", {}).get(team_name, {})
    
    def get_tactical_analysis(self, home_style, away_style):
        """鑾峰彇鎴樻湳瀵规姉鍒嗘瀽"""
        pattern_key = f"{home_style}_vs_{away_style}"
        return self.data.get("tactical_patterns", {}).get(pattern_key, {})
    
    def enhance_analysis(self, home, away, base_confidence):
        """鏍规嵁鐭ヨ瘑搴撳寮哄垎鏋愮粨鏋?""
        hp = self.get_team_profile(home)
        ap = self.get_team_profile(away)
        
        enhancements = []
        conf_adjust = 0
        
        if hp and ap:
            # 鎴樻湳椋庢牸瀵规姉
            if hp.get("style") and ap.get("style"):
                tactical = self.get_tactical_analysis(hp["style"], ap["style"])
                if tactical:
                    enhancements.append(f"鎴樻湳瀵规姉: {tactical.get('key_question','')}")
                    conf_adjust += tactical.get("confidence_adjustment", 0)
            
            # 鐞冨憳鍒嗘瀽
            if hp.get("key_players"):
                enhancements.append(f"{home}鍏抽敭鐞冨憳: {', '.join(hp['key_players'])}")
            if ap.get("key_players"):
                enhancements.append(f"{away}鍏抽敭鐞冨憳: {', '.join(ap['key_players'])}")
            
            # 闃靛浼樺姡鍔?            if ap.get("style") in hp.get("strength_vs", []):
                enhancements.append(f"{home}鎵撴硶鍏嬪埗{away}")
                conf_adjust += 5
            if hp.get("style") in ap.get("strength_vs", []):
                enhancements.append(f"{away}鎵撴硶鍏嬪埗{home}")
                conf_adjust -= 5
        
        return {
            "enhancements": enhancements,
            "confidence_adjustment": conf_adjust,
            "adjusted_confidence": min(100, max(0, base_confidence + conf_adjust))
        }

# 鍏ㄥ眬瀹炰緥
kb = KnowledgeBase()

def enhance_match_analysis(home, away, base_confidence, base_direction):
    """澧炲己姣旇禌鍒嗘瀽 - 渚涘ぇ鍔涚绠楀拰涓撳杈╄璋冪敤"""
    result = kb.enhance_analysis(home, away, base_confidence)
    return {
        "team_analysis": {
            "home": kb.get_team_profile(home),
            "away": kb.get_team_profile(away)
        },
        "tactical_insights": result["enhancements"],
        "confidence_raw": base_confidence,
        "confidence_adjusted": result["adjusted_confidence"],
        "adjustment": result["confidence_adjustment"],
        "direction": base_direction
    }