# -*- coding: utf-8 -*-
"""澶у姏绁炵畻 V3 - 鐞冮槦瀵规瘮 + 涓撳杈╄ + 璧涘悗鍒嗘瀽 + AI鍥炴姤鐜?""
import math, random, json, os
from datetime import datetime

# ============ 鐞冮槦瀹屾暣鏁版嵁 ============
FULL_TEAM_DATA = {
    "鎹峰厠": {
        "attack": 6, "defense": 6, "pace": 5, "press": 7, "poss": 4,
        "fifa": 35, "form": "2鑳?骞?璐?, "trend": "绋冲畾",
        "strengths": ["韬綋瀵规姉寮?, "瀹氫綅鐞冨▉鑳佸ぇ", "闃插畧绾緥濂?],
        "weaknesses": ["鎶€鏈粏鑵诲害涓嶈冻", "鍒涢€犲姏鏈夐檺", "閫熷害鍋忔參"],
        "key_player": "缁嶅垏鍏?, "coach": "鍝堣阿鍏?, "formation": "4-2-3-1",
    },
    "鍗楅潪": {
        "attack": 5, "defense": 5, "pace": 8, "press": 5, "poss": 4,
        "fifa": 55, "form": "3鑳?骞?璐?, "trend": "涓婂崌",
        "strengths": ["閫熷害绐佺牬", "鍙嶅嚮鐘€鍒?, "浣撹兘鍏呮矝"],
        "weaknesses": ["闃插畧缁勭粐寮?, "缁忛獙涓嶈冻", "瀵规姉椤剁骇闃熷悆鍔?],
        "key_player": "鍓嶉攱鏍稿績", "coach": "甯冪綏鏂?, "formation": "4-3-3",
    },
    "鐟炲＋": {
        "attack": 7, "defense": 8, "pace": 6, "press": 6, "poss": 5,
        "fifa": 16, "form": "4鑳?骞?璐?, "trend": "鏋佷匠",
        "strengths": ["闃插畧缁勭粐椤剁骇", "鍙嶅嚮鏁堢巼楂?, "澶ц禌缁忛獙涓板瘜"],
        "weaknesses": ["鍒涢€犳€т竴鑸?, "瀵规憜澶у反鐞冮槦鍔炴硶涓嶅"],
        "key_player": "鎵庡崱", "coach": "闆呴噾", "formation": "3-5-2",
    },
    "娉㈤粦": {
        "attack": 4, "defense": 4, "pace": 5, "press": 4, "poss": 4,
        "fifa": 60, "form": "1鑳?骞?璐?, "trend": "浣庤糠",
        "strengths": ["鏂楀織椤藉己", "闃插畧鍙嶅嚮鍩虹"],
        "weaknesses": ["鏁翠綋瀹炲姏寮?, "鏍稿績鑰佸寲", "杩涙敾鎵嬫鍗曚竴"],
        "key_player": "闃熼暱", "coach": "宸村反闆疯尐", "formation": "4-4-2",
    },
    "鍔犳嬁澶?: {
        "attack": 7, "defense": 5, "pace": 9, "press": 7, "poss": 5,
        "fifa": 28, "form": "2鑳?骞?璐?, "trend": "绋冲畾",
        "strengths": ["閫熷害鏋佸揩", "杈硅矾鐖嗙牬", "涓滈亾涓绘皵鍔?],
        "weaknesses": ["闃插畧缁勭粐宸?, "缁忛獙涓嶈冻", "棰嗗厛鏃舵帶鍒跺姏寮?],
        "key_player": "鎴寸淮鏂?, "coach": "椹粈", "formation": "4-3-3",
    },
    "鍗″灏?: {
        "attack": 5, "defense": 4, "pace": 5, "press": 5, "poss": 6,
        "fifa": 45, "form": "0鑳?骞?璐?, "trend": "浣庤糠",
        "strengths": ["鎶€鏈紶鎺?, "涓诲満缁忛獙", "褰掑寲鐞冨憳"],
        "weaknesses": ["韬綋瀵规姉寮?, "杩涚悆鑳藉姏宸?, "淇″績涓嶈冻"],
        "key_player": "闃块噷", "coach": "妗戝垏鏂?, "formation": "4-2-3-1",
    },
    "澧ㄨタ鍝?: {
        "attack": 7, "defense": 6, "pace": 7, "press": 7, "poss": 6,
        "fifa": 15, "form": "3鑳?骞?璐?, "trend": "鑹ソ",
        "strengths": ["鎶€鏈粏鑵?, "涓诲満浼樺娍", "澶ц禌缁忛獙涓板瘜"],
        "weaknesses": ["瀹㈠満琛ㄧ幇涓嶇ǔ", "棰嗗厛鏃朵繚瀹?],
        "key_player": "娲涜惃璇?, "coach": "闃垮悏闆?, "formation": "4-3-3",
    },
    "闊╁浗": {
        "attack": 7, "defense": 5, "pace": 8, "press": 7, "poss": 5,
        "fifa": 22, "form": "2鑳?骞?璐?, "trend": "绋冲畾",
        "strengths": ["蹇€熷弽鍑?, "瀛欏叴鎲嬩釜浜鸿兘鍔?, "鏂楀織椤藉己"],
        "weaknesses": ["闃插畧涓嶇ǔ瀹?, "瀛欏叴鎲嬩緷璧栫棁", "瀵规姉娆ф床闃熶綋鏍煎樊璺?],
        "key_player": "瀛欏叴鎲?, "coach": "鍏嬫灄鏂浖", "formation": "4-4-2",
    },
}


# ============ 1. 鐞冮槦瀵规瘮寮曟搸 ============
class TeamComparison:
    def compare(self, home, away):
        ht = FULL_TEAM_DATA.get(home, {})
        at = FULL_TEAM_DATA.get(away, {})
        if not ht or not at:
            return {"error": "鐞冮槦鏁版嵁涓嶈冻"}
        
        # 闆疯揪鍥炬暟鎹?(0-10)
        categories = ["attack", "defense", "pace", "press", "poss"]
        labels_cn = ["杩涙敾", "闃插畧", "閫熷害", "鍘嬭揩", "鎺х悆"]
        
        radar = []
        for cat, label in zip(categories, labels_cn):
            radar.append({
                "category": label,
                "home": ht.get(cat, 5),
                "away": at.get(cat, 5),
            })
        
        # 缁煎悎璇勫垎
        h_overall = sum(ht.get(c, 5) for c in categories) / len(categories)
        a_overall = sum(at.get(c, 5) for c in categories) / len(categories)
        
        # 浼樺姡鍔垮姣?
        h_edges = []
        a_edges = []
        for cat, label in zip(categories, labels_cn):
            diff = ht.get(cat, 5) - at.get(cat, 5)
            if diff >= 2:
                h_edges.append(f"{label}: 涓婚槦鏄庢樉鍗犱紭 (+{diff})")
            elif diff <= -2:
                a_edges.append(f"{label}: 瀹㈤槦鏄庢樉鍗犱紭 (+{-diff})")
        
        # 鍏抽敭瀵瑰喅
        matchups = []
        if ht.get("pace", 5) > 7 and at.get("defense", 5) < 6:
            matchups.append("涓婚槦閫熷害鍙兘鎾曠牬瀹㈤槦闃茬嚎")
        if at.get("pace", 5) > 7 and ht.get("defense", 5) < 6:
            matchups.append("瀹㈤槦閫熷害鏄富闃熼槻绾跨殑鏈€澶у▉鑳?)
        if abs(ht.get("poss", 5) - at.get("poss", 5)) <= 1:
            matchups.append("涓満鎺х悆鏉冧簤澶哄皢鏄叧閿?)
        if ht.get("press", 5) > at.get("press", 5) + 1:
            matchups.append("涓婚槦楂樺帇閫兼姠鍙兘閫犳垚瀹㈤槦澶辫")
        
        return {
            "home": home, "away": away,
            "radar": radar,
            "home_overall": round(h_overall, 1),
            "away_overall": round(a_overall, 1),
            "home_strengths": ht.get("strengths", []),
            "home_weaknesses": ht.get("weaknesses", []),
            "away_strengths": at.get("strengths", []),
            "away_weaknesses": at.get("weaknesses", []),
            "home_edges": h_edges,
            "away_edges": a_edges,
            "key_matchups": matchups,
            "home_info": {"fifa": ht.get("fifa"), "form": ht.get("form"), "trend": ht.get("trend"), 
                         "coach": ht.get("coach"), "key_player": ht.get("key_player"), "formation": ht.get("formation")},
            "away_info": {"fifa": at.get("fifa"), "form": at.get("form"), "trend": at.get("trend"),
                         "coach": at.get("coach"), "key_player": at.get("key_player"), "formation": at.get("formation")},
        }


# ============ 2. 涓撳杈╄寮曟搸 ============
class ExpertDebate:
    def debate(self, home, away, lh, la, win_pct, draw_pct, away_pct):
        """妯℃嫙涓撳鍥㈣京璁猴細閫夎儨/閫夊钩/閫夎礋鐨勪笓瀹跺悇鑷檲杩扮悊鐢?""
        ht = FULL_TEAM_DATA.get(home, {})
        at = FULL_TEAM_DATA.get(away, {})
        
        win_camp = []
        draw_camp = []
        lose_camp = []
        
        # 鏁版嵁鍒嗘瀽鍛樿瑙?
        if win_pct > draw_pct and win_pct > away_pct:
            win_camp.append({
                "expert": "鏁版嵁鍒嗘瀽鍛?, "icon": "馃搳",
                "argument": f"涓婚槦杩戞湡{ht.get('trend','')}锛岄鏈熻繘鐞冧紭鍔挎槑鏄撅紝鏁版嵁闈㈡敮鎸佷富鑳?,
                "confidence": round(win_pct, 1),
            })
        elif away_pct > win_pct and away_pct > draw_pct:
            lose_camp.append({
                "expert": "鏁版嵁鍒嗘瀽鍛?, "icon": "馃搳",
                "argument": f"瀹㈤槦鏁版嵁闈㈠崰浼橈紝杩戞湡鐘舵€亄at.get('trend','')}锛屽鑳滄鐜囨洿楂?,
                "confidence": round(away_pct, 1),
            })
        else:
            draw_camp.append({
                "expert": "鏁版嵁鍒嗘瀽鍛?, "icon": "馃搳",
                "argument": "鍙屾柟鏁版嵁鎺ヨ繎锛屽钩灞€鏄渶鍚堢悊鐨勭粨鏋?,
                "confidence": round(draw_pct, 1),
            })
        
        # 鎴樻湳鍒嗘瀽鍛樿瑙?
        h_pace = ht.get("pace", 5); a_def = at.get("defense", 5)
        a_pace = at.get("pace", 5); h_def = ht.get("defense", 5)
        
        if h_pace > a_def + 1:
            win_camp.append({
                "expert": "鎴樻湳鍒嗘瀽鍛?, "icon": "馃幆",
                "argument": f"涓婚槦閫熷害({h_pace})鍙啿鐮村闃熼槻绾?{a_def})锛屾垬鏈厠鍒舵槑鏄?,
                "confidence": min(85, 50 + (h_pace - a_def) * 10),
            })
        elif a_pace > h_def + 1:
            lose_camp.append({
                "expert": "鎴樻湳鍒嗘瀽鍛?, "icon": "馃幆",
                "argument": f"瀹㈤槦閫熷害({a_pace})鏄富闃熼槻绾?{h_def})鐨勫櫓姊?,
                "confidence": min(85, 50 + (a_pace - h_def) * 10),
            })
        else:
            draw_camp.append({
                "expert": "鎴樻湳鍒嗘瀽鍛?, "icon": "馃幆",
                "argument": "鍙屾柟椋庢牸浜掔浉鍒剁害锛屾垬鏈潰闅惧垎楂樹笅",
                "confidence": 50,
            })
        
        # 闃靛鍒嗘瀽鍛樿瑙?
        h_score = ht.get("attack", 5) + ht.get("defense", 5)
        a_score = at.get("attack", 5) + at.get("defense", 5)
        
        if h_score > a_score + 3:
            win_camp.append({
                "expert": "闃靛鍒嗘瀽鍛?, "icon": "馃彞",
                "argument": f"涓婚槦闃靛瀹炲姏鏄庢樉鏇村己(FIFA#{ht.get('fifa','?')} vs #{at.get('fifa','?')})",
                "confidence": min(80, 50 + (h_score - a_score) * 5),
            })
        elif a_score > h_score + 3:
            lose_camp.append({
                "expert": "闃靛鍒嗘瀽鍛?, "icon": "馃彞",
                "argument": f"瀹㈤槦闃靛瀹炲姏鏇村己(FIFA#{at.get('fifa','?')} vs #{ht.get('fifa','?')})",
                "confidence": min(80, 50 + (a_score - h_score) * 5),
            })
        else:
            draw_camp.append({
                "expert": "闃靛鍒嗘瀽鍛?, "icon": "馃彞",
                "argument": "鍙屾柟闃靛瀹炲姏鎺ヨ繎锛岄樀瀹归潰闅惧垎浼徊",
                "confidence": 40,
            })
        
        # 鍙嶆柟瀹＄鍛?- 鎬绘槸鎸戞垬涓绘祦瑙傜偣
        if len(win_camp) > len(lose_camp):
            lose_camp.append({
                "expert": "鍙嶆柟瀹＄鍛?, "icon": "馃攳",
                "argument": f"璀︽儠杩囧害鐪嬪ソ涓婚槦锛歿ht.get('weaknesses',['鏈煡'])[0]}鍙兘鏄獊鐮村彛锛屽闃焮at.get('strengths',['鏈煡'])[0]}涓嶅蹇借",
                "confidence": 30,
            })
        elif len(lose_camp) > len(win_camp):
            win_camp.append({
                "expert": "鍙嶆柟瀹＄鍛?, "icon": "馃攳",
                "argument": f"璀︽儠杩囧害鐪嬪ソ瀹㈤槦锛氬鍦轰綔鎴?{at.get('weaknesses',['鏈煡'])[0]}锛屼富闃熶富鍦轰紭鍔挎湭琚厖鍒嗛噸瑙?,
                "confidence": 30,
            })
        
        # 姹囨€?
        total = len(win_camp) + len(draw_camp) + len(lose_camp)
        win_ratio = round(len(win_camp) / total * 100) if total > 0 else 0
        draw_ratio = round(len(draw_camp) / total * 100) if total > 0 else 0
        lose_ratio = round(len(lose_camp) / total * 100) if total > 0 else 0
        
        # 鍒ゅ畾缁撴灉
        if len(win_camp) > len(draw_camp) and len(win_camp) > len(lose_camp):
            verdict = f"涓撳鍥㈠€惧悜涓昏儨 ({len(win_camp)}绁?vs {len(lose_camp)}绁?"
        elif len(lose_camp) > len(win_camp) and len(lose_camp) > len(draw_camp):
            verdict = f"涓撳鍥㈠€惧悜瀹㈣儨 ({len(lose_camp)}绁?vs {len(win_camp)}绁?"
        else:
            verdict = f"涓撳鍥㈠垎姝ц緝澶э紝骞冲眬鍙兘鎬т笉瀹瑰拷瑙?
        
        return {
            "win_camp": win_camp,
            "draw_camp": draw_camp,
            "lose_camp": lose_camp,
            "vote_ratio": {"win": win_ratio, "draw": draw_ratio, "lose": lose_ratio},
            "verdict": verdict,
            "total_experts": total,
        }


# ============ 3. 璧涘悗鍒嗘瀽寮曟搸 ============
class PostMatchAnalysis:
    def analyze(self, home, away, pred_score, actual_score, pred_win_pct, pred_draw_pct, pred_away_pct):
        """瀵规瘮棰勬祴 vs 瀹為檯璧涙灉鐨勫鐩樺垎鏋?""
        try:
            pred_h, pred_a = map(int, pred_score.split("-"))
            actual_h, actual_a = map(int, actual_score.split("-"))
        except:
            return {"error": "姣斿垎鏍煎紡閿欒"}
        
        # 棰勬祴鍑嗙‘鎬?
        pred_result = "涓昏儨" if pred_h > pred_a else ("骞冲眬" if pred_h == pred_a else "瀹㈣儨")
        actual_result = "涓昏儨" if actual_h > actual_a else ("骞冲眬" if actual_h == actual_a else "瀹㈣儨")
        
        correct_result = pred_result == actual_result
        exact_score = pred_h == actual_h and pred_a == actual_a
        goal_diff_ok = abs((pred_h - pred_a) - (actual_h - actual_a)) <= 1
        
        # 璇勫垎
        score = 0
        if exact_score: score = 100
        elif correct_result and goal_diff_ok: score = 75
        elif correct_result: score = 60
        elif goal_diff_ok: score = 30
        else: score = 10
        
        # 鍒嗘瀽鍋忕鍘熷洜
        deviation_analysis = []
        if pred_h != actual_h:
            diff = actual_h - pred_h
            if diff > 0:
                deviation_analysis.append(f"涓婚槦瀹為檯杩涚悆({actual_h})瓒呭嚭棰勬湡({pred_h})锛岃繘鏀荤琛ㄧ幇鍑轰箮鎰忔枡")
            else:
                deviation_analysis.append(f"涓婚槦瀹為檯杩涚悆({actual_h})浣庝簬棰勬湡({pred_h})锛岃繘鏀荤鏈揪棰勬湡")
        if pred_a != actual_a:
            diff = actual_a - pred_a
            if diff > 0:
                deviation_analysis.append(f"瀹㈤槦瀹為檯杩涚悆({actual_a})瓒呭嚭棰勬湡({pred_a})锛岄槻瀹堥娴嬪亸涔愯")
            else:
                deviation_analysis.append(f"瀹㈤槦瀹為檯杩涚悆({actual_a})浣庝簬棰勬湡({pred_a})锛岄槻瀹堟瘮棰勬湡濂?)
        
        if correct_result:
            deviation_analysis.append("鏂瑰悜鍒ゆ柇姝ｇ‘锛屼絾鍏蜂綋姣斿垎鏈夊亸宸?)
        else:
            deviation_analysis.append(f"鏂瑰悜鍒ゆ柇閿欒锛氶娴媨pred_result}锛屽疄闄厈actual_result}")
        
        # 瀛︿範鐐?
        learnings = []
        if not correct_result:
            learnings.append("闇€閲嶆柊璇勪及涓ら槦瀹炲姏宸窛鐨勬潈閲?)
            if actual_result == "骞冲眬":
                learnings.append("骞冲眬姒傜巼鍙兘琚綆浼帮紝闇€鎻愰珮骞冲眬妯″瀷鐨勬晱鎰熷害")
            if abs(actual_h - actual_a) <= 1:
                learnings.append("姣斿垎鎺ヨ繎鐨勬瘮璧涢娴嬮毦搴﹂珮锛岄渶鏇村鍏虫敞涓村満鍥犵礌")
        
        return {
            "home": home, "away": away,
            "predicted": pred_score,
            "actual": actual_score,
            "pred_result": pred_result,
            "actual_result": actual_result,
            "correct_result": correct_result,
            "exact_score": exact_score,
            "accuracy_score": score,
            "deviation_analysis": deviation_analysis,
            "learnings": learnings,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }


# ============ 4. AI鎶曟敞鍥炴姤鐜囪拷韪?============
class ROITracker:
    def __init__(self):
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history", "roi_history.json")
        self.load_history()
    
    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        except:
            self.records = []
    
    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_record(self, match, prediction, actual, odds, bet_amount, bet_type):
        """璁板綍涓€娆℃姇娉?""
        # Handle pending bets (actual="pending" or empty)
        if not actual or actual == "pending":
            record = {
                "match": match,
                "prediction": prediction,
                "actual": None,
                "odds": odds,
                "bet_amount": bet_amount,
                "bet_type": bet_type,
                "won": None,
                "profit": 0,
                "pending": True,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
            self.records.append(record)
            self.save_history()
            return record
        
        pred_h, pred_a = map(int, prediction.split("-"))
        actual_h, actual_a = map(int, actual.split("-"))
        pred_result = "win" if pred_h > pred_a else ("draw" if pred_h == pred_a else "lose")
        actual_result = "win" if actual_h > actual_a else ("draw" if actual_h == actual_a else "lose")
        
        won = pred_result == actual_result
        profit = bet_amount * odds - bet_amount if won else -bet_amount
        
        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match": match,
            "prediction": prediction,
            "actual": actual,
            "bet_type": bet_type,
            "odds": odds,
            "bet_amount": bet_amount,
            "won": won,
            "profit": round(profit, 2),
        }
        self.records.append(record)
        self.save_history()
        return record
    
    def get_stats(self):
        """璁＄畻AI鎶曟敞缁熻"""
        if not self.records:
            return {"total_bets": 0, "message": "鏆傛棤鎶曟敞璁板綍"}
        
        completed = [r for r in self.records if not r.get("pending")]
        pending = [r for r in self.records if r.get("pending")]
        total = len(self.records)
        wins = sum(1 for r in completed if r.get("won"))
        total_bet = sum(r["bet_amount"] for r in self.records)
        total_profit = sum(r["profit"] for r in completed)
        
        win_rate = round(wins / total * 100, 1) if total > 0 else 0
        roi = round(total_profit / total_bet * 100, 1) if total_bet > 0 else 0
        
        # 鎸夌帺娉曞垎绫?
        by_type = {}
        for r in self.records:
            bt = r["bet_type"]
            if bt not in by_type:
                by_type[bt] = {"total": 0, "wins": 0, "profit": 0, "bet": 0}
            by_type[bt]["total"] += 1
            by_type[bt]["wins"] += 1 if r["won"] else 0
            by_type[bt]["profit"] += r["profit"]
            by_type[bt]["bet"] += r["bet_amount"]
        
        for bt in by_type:
            by_type[bt]["win_rate"] = round(by_type[bt]["wins"] / by_type[bt]["total"] * 100, 1)
            by_type[bt]["roi"] = round(by_type[bt]["profit"] / by_type[bt]["bet"] * 100, 1) if by_type[bt]["bet"] > 0 else 0
        
        # 鏈€杩戣秼鍔?
        recent = self.records[-10:]
        recent_wins = sum(1 for r in recent if r["won"])
        recent_roi = round(sum(r["profit"] for r in recent) / sum(r["bet_amount"] for r in recent) * 100, 1) if sum(r["bet_amount"] for r in recent) > 0 else 0
        
        return {
            "total_bets": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": win_rate,
            "total_bet": round(total_bet, 2),
            "total_profit": round(total_profit, 2),
            "roi": roi,
            "by_type": by_type,
            "recent_10": {"bets": len(recent), "wins": recent_wins, "roi": recent_roi},
            "records": self.records[-20:],
        }


# ============ 宸ュ叿鍑芥暟 ============
roi_tracker = ROITracker()

def get_all_features(home, away, lh, la, win_pct, draw_pct, away_pct):
    """鑾峰彇鍏ㄩ儴4涓柊鍔熻兘鐨勫垎鏋愮粨鏋?""
    results = {}
    
    # 1. 鐞冮槦瀵规瘮
    try:
        results["team_comparison"] = TeamComparison().compare(home, away)
    except Exception as e:
        results["team_comparison"] = {"error": str(e)}
    
    # 2. 涓撳杈╄
    try:
        results["expert_debate"] = ExpertDebate().debate(home, away, lh, la, win_pct, draw_pct, away_pct)
    except Exception as e:
        results["expert_debate"] = {"error": str(e)}
    
    # 3. ROI缁熻
    try:
        results["roi_stats"] = roi_tracker.get_stats()
    except Exception as e:
        results["roi_stats"] = {"error": str(e)}
    
    return results
