"""
自动分析师 - 每天自动学习分析比赛
1. 赛前：自动搜集信息 + 调用知识库生成分析
2. 赛后：对比预测vs结果，自动修正权重
"""
import json, os, re, time
from datetime import datetime, timedelta
import urllib.request
import urllib.error

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
KB_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
LEARN_FILE = os.path.join(DATA_DIR, "self_learned.json")

class AutoAnalyst:
    def __init__(self):
        self.kb = self._load_json(KB_FILE, {"videos": [], "tactical_patterns": {}, "team_profiles": {}})
        self.learned = self._load_json(LEARN_FILE, {"history": [], "patterns_discovered": [], "accuracy": {}})
        self.search_sources = [
            "https://www.google.com/search?q={home}+vs+{away}+足球+赛前分析+2026",
            "https://www.bing.com/search?q={home}+{away}+football+preview+2026",
        ]
    
    def _load_json(self, path, default):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    
    def _save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def search_match_info(self, home, away):
        """搜索引擎搜索比赛相关信息（文字提取）"""
        results = []
        for url_template in self.search_sources:
            url = url_template.format(home=urllib.request.quote(home), away=urllib.request.quote(away))
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                })
                resp = urllib.request.urlopen(req, timeout=10)
                html = resp.read().decode('utf-8', errors='ignore')
                
                # Extract text snippets
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text)
                
                # Find Chinese text blocks
                cn_blocks = re.findall(r'[\u4e00-\u9fff]{20,200}', text)
                for block in cn_blocks:
                    if any(kw in block for kw in ['球队','比赛','进攻','防守','阵容','战术','球员','主场','客场','世界杯']):
                        if block not in results:
                            results.append(block)
            except Exception as e:
                pass
        
        return results[:10]  # Top 10 relevant snippets
    
    def analyze_match(self, home, away, home_style=None, away_style=None):
        """自动分析一场比赛"""
        hp = self.kb["team_profiles"].get(home, {})
        ap = self.kb["team_profiles"].get(away, {})
        
        # Determine styles from KB or infer
        h_style = home_style or hp.get("style", "未知")
        a_style = away_style or ap.get("style", "未知")
        
        # Try to search for real-time info
        print(f"[AutoAnalyst] 搜索 {home} vs {away} 信息...")
        snippets = self.search_match_info(home, away)
        if snippets:
            print(f"[AutoAnalyst] 找到 {len(snippets)} 条相关信息")
        
        # Generate analysis from knowledge base patterns
        analysis = self._generate_tactical_analysis(home, away, h_style, a_style, hp, ap)
        analysis["web_snippets"] = snippets[:5]
        analysis["generated_at"] = datetime.now().isoformat()
        
        # Save to self-learned history
        self.learned.setdefault("analyses", []).append({
            "home": home, "away": away,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "analysis": analysis
        })
        self.learned["analyses"] = self.learned["analyses"][-50:]  # Keep last 50
        self._save_json(LEARN_FILE, self.learned)
        
        return analysis
    
    def _generate_tactical_analysis(self, home, away, h_style, a_style, hp, ap):
        """基于知识库模式生成战术分析"""
        analysis = {
            "home": {"name": home, "style": h_style, "profile": hp},
            "away": {"name": away, "style": a_style, "profile": ap},
            "tactical_matchup": "",
            "key_factors": [],
            "prediction": "",
            "confidence_note": ""
        }
        
        # 1. 战术风格对抗
        matchup_key = f"{h_style}_vs_{a_style}"
        tactical = self.kb["tactical_patterns"].get(matchup_key, {})
        if tactical:
            analysis["tactical_matchup"] = tactical.get("description", "")
            analysis["key_factors"].append(tactical.get("key_question", ""))
        
        # 2. 第二轮调整法则
        round2 = self.kb["tactical_patterns"].get("第二轮_vs_第一轮", {})
        if round2:
            analysis["key_factors"].append(round2.get("key_principle", ""))
        
        # 3. 球队关键球员
        if hp.get("key_players"):
            analysis["key_factors"].append(f"{home}关键球员: {', '.join(hp['key_players'])}")
        if ap.get("key_players"):
            analysis["key_factors"].append(f"{away}关键球员: {', '.join(ap['key_players'])}")
        
        # 4. 球队近况
        if hp.get("note"):
            analysis["key_factors"].append(f"{home}: {hp['note']}")
        if ap.get("note"):
            analysis["key_factors"].append(f"{away}: {ap['note']}")
        
        # 5. 优劣势分析
        if ap.get("style") in hp.get("strength_vs", []):
            analysis["key_factors"].append(f"{home}打法克制{away}")
        if hp.get("style") in ap.get("strength_vs", []):
            analysis["key_factors"].append(f"{away}打法克制{home}")
        
        # 6. 生成预测
        if tactical:
            outcome = tactical.get("typical_outcome", "")
            if outcome:
                analysis["prediction"] = outcome
            analysis["confidence_note"] = tactical.get("note", "")
        
        return analysis
    
    def learn_from_result(self, home, away, predicted, actual, score):
        """赛后学习：对比预测vs实际结果"""
        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match": f"{home} vs {away}",
            "predicted": predicted,
            "actual": actual,
            "score": score,
            "correct": predicted == actual
        }
        
        self.learned["history"].append(record)
        
        # Update accuracy tracking
        key = f"{home}_vs_{away}" if not record["correct"] else None
        if key:
            self.learned.setdefault("corrections", {})[key] = {
                "predicted": predicted, "actual": actual,
                "lesson": f"预测{predicted}但实际{actual}，需要重新评估"
            }
        
        # Calculate overall accuracy
        total = len(self.learned["history"])
        correct = sum(1 for h in self.learned["history"] if h["correct"])
        self.learned["accuracy"] = {
            "total": total,
            "correct": correct,
            "rate": round(correct / total * 100, 1) if total > 0 else 0
        }
        
        # Discover new patterns from corrections
        if not record["correct"]:
            self._discover_pattern(home, away, hp=self.kb["team_profiles"].get(home, {}),
                                   ap=self.kb["team_profiles"].get(away, {}), 
                                   predicted=predicted, actual=actual)
        
        self._save_json(LEARN_FILE, self.learned)
        print(f"[AutoAnalyst] 学习完毕 - 准确率: {self.learned['accuracy']['rate']}% ({correct}/{total})")
        
        return record
    
    def _discover_pattern(self, home, away, hp, ap, predicted, actual):
        """从预测错误中发现新模式"""
        h_style = hp.get("style", "")
        a_style = ap.get("style", "")
        
        if h_style and a_style:
            pattern_key = f"{h_style}_vs_{a_style}_修正"
            existing = self.learned.get("patterns_discovered", [])
            
            discovery = {
                "pattern": pattern_key,
                "match": f"{home} vs {away}",
                "finding": f"{h_style}面对{a_style}时，预测{predicted}但实际{actual}",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            if discovery not in existing:
                existing.append(discovery)
                self.learned["patterns_discovered"] = existing
                print(f"[AutoAnalyst] 发现新模式: {pattern_key}")
    
    def get_daily_report(self, matches):
        """生成每日分析报告"""
        analyses = []
        for m in matches:
            home = m.get("home", "")
            away = m.get("away", "")
            if home and away:
                result = self.analyze_match(home, away)
                result["match_data"] = m
                analyses.append(result)
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "analyses": analyses,
            "knowledge_base_stats": {
                "videos_learned": len(self.kb.get("videos", [])),
                "teams_known": len(self.kb.get("team_profiles", {})),
                "patterns": len(self.kb.get("tactical_patterns", {})),
                "accuracy": self.learned.get("accuracy", {})
            }
        }

# 全局实例
analyst = AutoAnalyst()
