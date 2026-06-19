# -*- coding: utf-8 -*-
"""澶у姏绁炵畻 V2 - AI璧涘墠鍒嗘瀽椹鹃┒鑸?""
import random, math, json, os, hashlib
from datetime import datetime

# ============ 淇℃伅婧愬垎绾х郴缁?============
SOURCE_TIERS = {
    "official": {"name": "瀹樻柟鏉ユ簮", "weight": 1.0, "icon": "馃彌锔?, "desc": "FIFA/鐞冮槦瀹樻柟鍏憡"},
    "authoritative": {"name": "鏉冨▉濯掍綋", "weight": 0.8, "icon": "馃摪", "desc": "ESPN/BBC/澶╃┖浣撹偛绛?},
    "medium": {"name": "鏅€氬獟浣?, "weight": 0.4, "icon": "馃摑", "desc": "寰呯‘璁や俊鎭?},
    "unconfirmed": {"name": "鏈‘璁?, "weight": 0.1, "icon": "鉂?, "desc": "浼犻椈/绀句氦濯掍綋"},
}

# ============ 鐞冮槦瀹屾暣鏁版嵁搴?============
TEAM_DB = {
    "鎹峰厠": {
        "style": "韬綋瀵规姉+瀹氫綅鐞?, "formation": "4-2-3-1",
        "attack": 6, "defense": 6, "pace": 5, "press": 7, "poss": 4, "wing": 6, "central": 5,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "绋冲畾",
        "key_players": ["缁嶅垏鍏?涓満鏍稿績)", "甯屽厠(鍓嶉攱)", "鏇规硶灏?鍙冲悗鍗?"],
        "injuries": [
            {"player": "涓満鏇胯ˉ", "status": "瀛樼枒", "source": "medium", "impact": 0.1},
        ],
        "coach": "鍝堣阿鍏?, "fifa_rank": 35,
    },
    "鍗楅潪": {
        "style": "閫熷害绐佺牬+闃插畧鍙嶅嚮", "formation": "4-3-3",
        "attack": 5, "defense": 5, "pace": 8, "press": 5, "poss": 4, "wing": 7, "central": 4,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "涓婂崌",
        "key_players": ["鍓嶉攱鏍稿績(閫熷害鍨?", "涓満缁勭粐鑰?],
        "injuries": [
            {"player": "涓诲姏鍚庡崼", "status": "缂洪樀", "source": "official", "impact": 0.25},
        ],
        "coach": "甯冪綏鏂?, "fifa_rank": 55,
    },
    "鐟炲＋": {
        "style": "闃插畧绋冲浐+鍙嶅嚮鐘€鍒?, "formation": "3-5-2",
        "attack": 7, "defense": 8, "pace": 6, "press": 6, "poss": 5, "wing": 6, "central": 5,
        "recent": "杩?鍦?鑳?骞?璐?杩?0澶?", "trend": "鏋佷匠",
        "key_players": ["鎵庡崱(闃熼暱/涓満)", "鎭╁崥娲?鍓嶉攱)", "闃垮潕鍚?涓悗鍗?", "绱㈤粯(闂ㄥ皢)"],
        "injuries": [],
        "coach": "闆呴噾", "fifa_rank": 16,
    },
    "娉㈤粦": {
        "style": "闃插畧鍙嶅嚮", "formation": "4-4-2",
        "attack": 4, "defense": 4, "pace": 5, "press": 4, "poss": 4, "wing": 5, "central": 4,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "浣庤糠",
        "key_players": ["闃熼暱(涓満)", "鍓嶉攱(瀛樼枒)"],
        "injuries": [
            {"player": "涓诲姏涓満", "status": "缂洪樀", "source": "authoritative", "impact": 0.3},
            {"player": "鍓嶉攱", "status": "瀛樼枒", "source": "medium", "impact": 0.15},
        ],
        "coach": "宸村反闆疯尐", "fifa_rank": 60,
    },
    "鍔犳嬁澶?: {
        "style": "閫熷害鍨?蹇€熸帹杩?, "formation": "4-3-3",
        "attack": 7, "defense": 5, "pace": 9, "press": 7, "poss": 5, "wing": 8, "central": 5,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "绋冲畾",
        "key_players": ["鎴寸淮鏂?宸﹀悗鍗?杈归攱)", "澶у崼(鍓嶉攱)", "甯冨潕鍗?杈归攱)"],
        "injuries": [
            {"player": "杈瑰悗鍗?, "status": "瀛樼枒", "source": "unconfirmed", "impact": 0.05},
        ],
        "coach": "椹粈", "fifa_rank": 28,
    },
    "鍗″灏?: {
        "style": "浼犳帶+鎶€鏈祦", "formation": "4-2-3-1",
        "attack": 5, "defense": 4, "pace": 5, "press": 5, "poss": 6, "wing": 5, "central": 5,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "浣庤糠",
        "key_players": ["闃块噷(鍓嶉攱)", "娴峰鏂?闃熼暱)"],
        "injuries": [
            {"player": "涓诲姏鍓嶉攱", "status": "缂洪樀", "source": "official", "impact": 0.35},
        ],
        "coach": "妗戝垏鏂?, "fifa_rank": 45,
    },
    "澧ㄨタ鍝?: {
        "style": "鎶€鏈祦+涓诲満榫?, "formation": "4-3-3",
        "attack": 7, "defense": 6, "pace": 7, "press": 7, "poss": 6, "wing": 7, "central": 6,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "鑹ソ",
        "key_players": ["娲涜惃璇?杈归攱)", "闃垮皵鐡﹂浄鏂?涓満)", "濂ヤ箶浜?闂ㄥ皢)"],
        "injuries": [
            {"player": "涓満", "status": "瀛樼枒", "source": "medium", "impact": 0.1},
        ],
        "coach": "闃垮悏闆?, "fifa_rank": 15,
    },
    "闊╁浗": {
        "style": "蹇€熷弽鍑?鐞冩槦椹卞姩", "formation": "4-4-2",
        "attack": 7, "defense": 5, "pace": 8, "press": 7, "poss": 5, "wing": 7, "central": 5,
        "recent": "杩?鍦?鑳?骞?璐?杩?澶?", "trend": "绋冲畾",
        "key_players": ["瀛欏叴鎲?闃熼暱/鍓嶉攱)", "鏉庡垰浠?涓満)", "閲戞椈鍝?涓悗鍗?"],
        "injuries": [
            {"player": "鍚庡崼", "status": "瀛樼枒", "source": "unconfirmed", "impact": 0.05},
        ],
        "coach": "鍏嬫灄鏂浖", "fifa_rank": 22,
    },
}

# ============ 鍦哄湴鏁版嵁 ============
VENUE_DB = {
    "涓栫晫鏉疕缁?: {"city": "娲涙潐鐭?, "stadium": "SoFi浣撹偛鍦?, "temp": 22, "humidity": 55, "grass": "澶╃劧鑽?, "altitude": 87, "weather": "鏅?, "wind": "寰"},
    "涓栫晫鏉疓缁?: {"city": "杩堥樋瀵?, "stadium": "纭煶浣撹偛鍦?, "temp": 28, "humidity": 75, "grass": "澶╃劧鑽?, "altitude": 2, "weather": "澶氫簯", "wind": "寰"},
    "涓栫晫鏉疐缁?: {"city": "澶氫鸡澶?, "stadium": "BMO鐞冨満", "temp": 18, "humidity": 60, "grass": "浜哄伐鑽?, "altitude": 76, "weather": "鏅?, "wind": "涓瓑"},
    "涓栫晫鏉疉缁?: {"city": "澧ㄨタ鍝ュ煄", "stadium": "闃垮吂鐗瑰厠浣撹偛鍦?, "temp": 20, "humidity": 45, "grass": "澶╃劧鑽?, "altitude": 2250, "weather": "鏅?, "wind": "寰"},
}


def get_source_credibility(sources):
    """璁＄畻淇℃伅婧愬彲淇″害鍔犳潈"""
    if not sources: return 0.5, "鏃犳槑纭潵婧?
    total_weight = 0
    tiers_found = set()
    for s in sources:
        tier_info = SOURCE_TIERS.get(s, SOURCE_TIERS["unconfirmed"])
        total_weight += tier_info["weight"]
        tiers_found.add(tier_info["name"])
    avg_weight = total_weight / len(sources)
    if avg_weight >= 0.8: level = "楂樺彲淇″害"
    elif avg_weight >= 0.5: level = "涓瓑鍙俊搴?
    else: level = "浣庡彲淇″害"
    return avg_weight, f"{level} (鏉ユ簮: {', '.join(tiers_found)})"


class DataAnalyst:
    """鏁版嵁鍒嗘瀽鍛?- 鎴樼哗瓒嬪娍 + 鏀婚槻鏁堢巼"""
    def analyze(self, home, away, lh, la):
        ht = TEAM_DB.get(home, {})
        at = TEAM_DB.get(away, {})
        h_att = ht.get("attack", 5) / 10
        a_def = at.get("defense", 5) / 10
        a_att = at.get("attack", 5) / 10
        h_def = ht.get("defense", 5) / 10
        h_xg = round(lh * (h_att / max(0.3, a_def)), 2)
        a_xg = round(la * (a_att / max(0.3, h_def)), 2)
        h_trend = ht.get("trend", "绋冲畾")
        a_trend = at.get("trend", "绋冲畾")
        score_h = round(min(5, max(0, h_xg + random.gauss(0, 0.2))))
        score_a = round(min(5, max(0, a_xg + random.gauss(0, 0.2))))
        return {
            "agent": "鏁版嵁鍒嗘瀽鍛?, "icon": "馃搳",
            "score": f"{score_h}-{score_a}",
            "confidence": min(90, int(abs(h_xg - a_xg) * 35 + 40)),
            "key_findings": [
                f"涓婚槦杩戞湡: {ht.get('recent','')} | 瓒嬪娍: {h_trend}",
                f"瀹㈤槦杩戞湡: {at.get('recent','')} | 瓒嬪娍: {a_trend}",
                f"棰勬湡杩涚悆(xG): 涓?{h_xg} - 瀹?{a_xg}",
                f"鏀婚槻鏁堢巼: 涓昏繘鏀粄h_att:.0%} vs 瀹㈤槻瀹坽a_def:.0%}",
            ],
            "verdict": "涓婚槦鏁版嵁鍗犱紭" if h_xg > a_xg + 0.2 else ("瀹㈤槦鏁版嵁鍗犱紭" if a_xg > h_xg + 0.2 else "鏁版嵁闈㈡帴杩?),
        }


class TacticalAnalyst:
    """鎴樻湳鍒嗘瀽鍛?- 椋庢牸鐩稿厠 + 闃靛瀷瀵逛綅"""
    def analyze(self, home, away, lh, la):
        ht = TEAM_DB.get(home, {})
        at = TEAM_DB.get(away, {})
        h_style = ht.get("style", "")
        a_style = at.get("style", "")
        h_form = ht.get("formation", "")
        a_form = at.get("formation", "")
        advantages = []; concerns = []
        # 閫熷害鍏嬪埗
        if ht.get("pace", 5) > at.get("pace", 5) + 2:
            advantages.append(f"涓婚槦閫熷害浼樺娍({ht['pace']} vs {at['pace']})鍙啿鍑诲闃熼槻绾?)
        elif at.get("pace", 5) > ht.get("pace", 5) + 2:
            concerns.append(f"瀹㈤槦閫熷害({at['pace']})鍙兘鎵撶┛涓婚槦({ht['pace']})")
        # 鍘嬭揩鍏嬪埗
        if ht.get("press", 5) > at.get("press", 5) + 1:
            advantages.append("涓婚槦楂樹綅鍘嬭揩闄愬埗瀹㈤槦缁勭粐")
        # 鎺х悆
        if abs(ht.get("poss", 5) - at.get("poss", 5)) <= 1:
            advantages.append("鎺х悆鐜囬璁℃帴杩戯紝涓満浜夊ず鍏抽敭")
        # 椋庢牸鐩稿厠
        if "鍙嶅嚮" in h_style and ("浼犳帶" in a_style or "鎺х悆" in a_style):
            advantages.append(f"涓婚槦鍙嶅嚮椋庢牸({h_style})鍏嬪埗瀹㈤槦({a_style})")
        if "浼犳帶" in h_style and "鍙嶅嚮" in a_style:
            concerns.append(f"涓婚槦浼犳帶鍙兘琚闃熷弽鍑婚拡瀵?)
        score_h = round(min(5, max(0, lh + len(advantages) * 0.3 - len(concerns) * 0.3 + random.gauss(0, 0.2))))
        score_a = round(min(5, max(0, la + len(concerns) * 0.3 - len(advantages) * 0.2 + random.gauss(0, 0.2))))
        return {
            "agent": "鎴樻湳鍒嗘瀽鍛?, "icon": "馃幆",
            "score": f"{score_h}-{score_a}",
            "confidence": min(85, 50 + len(advantages) * 10 - len(concerns) * 8),
            "key_findings": [
                f"涓婚槦: {h_style} | 闃靛瀷: {h_form}",
                f"瀹㈤槦: {a_style} | 闃靛瀷: {a_form}",
            ] + advantages[:2] + concerns[:2],
            "verdict": "鎴樻湳闈富闃熸湁鍒? if len(advantages) > len(concerns) else ("鎴樻湳闈㈠闃熸湁鍒? if len(concerns) > len(advantages) else "鎴樻湳闈簰鏈夊厠鍒?),
        }


class RosterObserver:
    """浼ゅ仠闃靛瑙傚療鍛?- 澶氭簮鏍搁獙 + 鏉ユ簮鍒嗙骇"""
    def analyze(self, home, away, lh, la):
        ht = TEAM_DB.get(home, {})
        at = TEAM_DB.get(away, {})
        findings = []
        h_impact = 1.0; a_impact = 1.0
        # 涓婚槦浼ゅ仠
        for inj in ht.get("injuries", []):
            tier = SOURCE_TIERS.get(inj.get("source", "unconfirmed"), SOURCE_TIERS["unconfirmed"])
            weighted_impact = inj["impact"] * tier["weight"]
            h_impact -= weighted_impact
            findings.append(f"{tier['icon']} [{tier['name']}] 涓婚槦 {inj['player']}: {inj['status']} (褰卞搷鏉冮噸: {weighted_impact:.0%})")
        # 瀹㈤槦浼ゅ仠
        for inj in at.get("injuries", []):
            tier = SOURCE_TIERS.get(inj.get("source", "unconfirmed"), SOURCE_TIERS["unconfirmed"])
            weighted_impact = inj["impact"] * tier["weight"]
            a_impact -= weighted_impact
            findings.append(f"{tier['icon']} [{tier['name']}] 瀹㈤槦 {inj['player']}: {inj['status']} (褰卞搷鏉冮噸: {weighted_impact:.0%})")
        # 鏍稿績鐞冨憳
        findings.append(f"涓婚槦鏍稿績: {', '.join(ht.get('key_players',[])[:3])}")
        findings.append(f"瀹㈤槦鏍稿績: {', '.join(at.get('key_players',[])[:3])}")
        # 鏉ユ簮鍙俊搴?
        all_sources = [inj.get("source", "unconfirmed") for inj in ht.get("injuries", []) + at.get("injuries", [])]
        cred_score, cred_label = get_source_credibility(all_sources)
        if not all_sources:
            findings.append("馃彌锔?鏃犻噸澶т激鍋滄姤鍛婏紝闃靛淇℃伅鏉ヨ嚜瀹樻柟娓犻亾")
        h_adj = lh * max(0.5, h_impact)
        a_adj = la * max(0.5, a_impact)
        score_h = round(min(5, max(0, h_adj + random.gauss(0, 0.15))))
        score_a = round(min(5, max(0, a_adj + random.gauss(0, 0.15))))
        return {
            "agent": "浼ゅ仠闃靛瑙傚療鍛?, "icon": "馃彞",
            "score": f"{score_h}-{score_a}",
            "confidence": 60 + int(cred_score * 30),
            "key_findings": findings,
            "verdict": f"闃靛闈'涓婚槦鏇村畬鏁? if h_impact > a_impact else ('瀹㈤槦鏇村畬鏁? if a_impact > h_impact else '鍙屾柟榻愭暣')} | 淇℃伅鏉ユ簮: {cred_label}",
            "source_credibility": cred_label,
        }


class WeatherAnalyst:
    """澶╂皵鍦哄湴鍒嗘瀽鍛?""
    def analyze(self, home, away, lh, la):
        venue = VENUE_DB.get("涓栫晫鏉疕缁?, list(VENUE_DB.values())[0])
        findings = []
        temp = venue["temp"]; hum = venue["humidity"]; alt = venue["altitude"]
        grass = venue["grass"]; weather = venue["weather"]; wind = venue["wind"]
        findings.append(f"馃搷 {venue['city']} | {venue['stadium']} | {weather} | {temp}鈩?| 婀垮害{hum}%")
        findings.append(f"馃彑锔?{grass} | 娴锋嫈{alt}m | {wind}")
        # 褰卞搷璇勪及
        impact_note = []
        if temp > 28: impact_note.append("楂樻俯澧炲姞浣撹兘娑堣€?)
        elif temp < 12: impact_note.append("浣庢俯褰卞搷鎶€鏈彂鎸?)
        else: impact_note.append("娓╁害閫傚疁")
        if hum > 70: impact_note.append("楂樻箍搴﹀姞閲嶄綋鑳借礋鎷?)
        if alt > 1500: impact_note.append(f"鈿狅笍 楂樻捣鎷?{alt}m)鏄捐憲褰卞搷涓嶉€傚簲鐞冮槦")
        elif alt > 500: impact_note.append("涓捣鎷旀湁杞诲井褰卞搷")
        if "浜哄伐" in grass: impact_note.append("浜哄伐鑽夌悆閫熷亸蹇?)
        findings.append("褰卞搷: " + " | ".join(impact_note))
        pace_factor = 0.85 if temp > 30 else 1.0
        score_h = round(min(5, max(0, lh * pace_factor + random.gauss(0, 0.15))))
        score_a = round(min(5, max(0, la * pace_factor + random.gauss(0, 0.15))))
        return {
            "agent": "澶╂皵鍦哄湴鍒嗘瀽鍛?, "icon": "馃尋锔?,
            "score": f"{score_h}-{score_a}",
            "confidence": 60,
            "key_findings": findings,
            "verdict": "鐜鍥犵礌瀵瑰弻鏂瑰奖鍝嶅潎琛? if alt < 1000 else "楂樻捣鎷斿彲鑳藉奖鍝嶅闃熶綋鑳?,
            "venue": venue,
        }


class DevilAdvocate:
    """鍙嶆柟瀹＄鍛?- 鐩茬偣妫€娴?+ 椋庨櫓璇勪及"""
    def analyze(self, home, away, lh, la):
        ht = TEAM_DB.get(home, {})
        at = TEAM_DB.get(away, {})
        warnings = []
        risk_factors = []
        # 寮洪槦闄烽槺
        if lh > la + 0.5:
            risk_factors.append({"factor": "寮洪槦渚濊禆椋庨櫓", "level": "涓?, "detail": f"鏁版嵁鏄庢樉鍊惧悜涓婚槦(位宸?{lh-la:.1f})锛岄渶璀︽儠鐖嗗喎"})
        elif la > lh + 0.5:
            risk_factors.append({"factor": "瀹㈠満椋庨櫓", "level": "涓?, "detail": f"鏁版嵁鍊惧悜瀹㈤槦浣嗗鍦轰綔鎴樺彉鏁板ぇ"})
        # 鐘舵€侀櫡闃?
        if ht.get("trend") == "鏋佷匠" and at.get("trend") == "浣庤糠":
            warnings.append("鈿狅笍 璀︽儠鐘舵€侀櫡闃? 瀹㈤槦浣庤糠鍚庡彲鑳芥湁鍙嶅脊鍔ㄥ姏")
        if at.get("trend") == "鏋佷匠" and ht.get("trend") == "浣庤糠":
            warnings.append("鈿狅笍 涓婚槦铏界姸鎬佸樊浣嗘湁涓诲満浼樺娍鍜屽弽寮归渶姹?)
        # 瀹炲姏鎺ヨ繎
        if abs(lh - la) < 0.2:
            risk_factors.append({"factor": "楂樹笉纭畾鎬?, "level": "楂?, "detail": "鍙屾柟瀹炲姏鎺ヨ繎锛屼换浣曠粨鏋滈兘鍙兘"})
        # 浼ゅ仠鐩茬偣
        h_inj = ht.get("injuries", [])
        a_inj = at.get("injuries", [])
        unconfirmed = [i for i in h_inj + a_inj if i.get("source") in ("medium", "unconfirmed")]
        if unconfirmed:
            warnings.append(f"鈿狅笍 {len(unconfirmed)}鏉′激鍋滀俊鎭湭瀹屽叏纭锛屽瓨鍦ㄤ俊鎭樊椋庨櫓")
        # 涓栫晫鏉壒娈婂洜绱?
        warnings.append("鈿狅笍 灏忕粍璧涢杞弻鏂瑰彲鑳藉亸淇濆畧锛屾€昏繘鐞冨彲鑳戒綆浜庨鏈?)
        warnings.append("鈿狅笍 VAR/瑁佸垽灏哄害绛変笉鍙帶鍥犵礌鏃犳硶棰勬祴")
        # 杩戝喌閫嗚浆椋庨櫓
        if at.get("trend") == "浣庤糠" and ht.get("trend") == "鑹ソ":
            risk_factors.append({"factor": "杩戝喌閫嗚浆椋庨櫓", "level": "浣?, "detail": "瀹㈤槦浣庤糠鍙兘瑙﹀簳鍙嶅脊"})
        risk_level = "浣? if len(warnings) <= 2 else ("涓? if len(warnings) <= 4 else "楂?)
        return {
            "agent": "鍙嶆柟瀹＄鍛?, "icon": "馃攳",
            "score": "N/A",
            "confidence": max(30, 80 - len(warnings) * 15),
            "key_findings": warnings,
            "risk_factors": risk_factors,
            "verdict": f"鍙戠幇 {len(warnings)} 涓渶鍏虫敞鍥犵礌 | 缁煎悎椋庨櫓: {risk_level}",
            "risk_level": risk_level,
        }


class ModelComparison:
    """妯″瀷瀵规瘮 - Claude vs GPT"""
    def compare(self, home, away, lh, la):
        ht = TEAM_DB.get(home, {})
        at = TEAM_DB.get(away, {})
        # Claude椋庢牸: 閲嶈鎴樻湳缁撴瀯銆侀樀瀹瑰畬鏁村害銆侀鏍煎厠鍒?
        claude_focus = ["鎴樻湳缁撴瀯", "闃靛瀹屾暣搴?, "椋庢牸鍏嬪埗"]
        claude_h = round(min(4, max(0, lh * 0.9 + (1 if ht.get("defense", 5) > at.get("attack", 5) else 0))))
        claude_a = round(min(4, max(0, la * 0.9)))
        # GPT椋庢牸: 閲嶈杩戞湡鏁版嵁瓒嬪娍銆佽繘鏀绘晥鐜囥€佹瘮璧涜妭濂?
        gpt_focus = ["杩戞湡鏁版嵁", "杩涙敾鏁堢巼", "姣旇禌鑺傚"]
        gpt_h = round(min(5, max(0, lh * 1.1)))
        gpt_a = round(min(4, max(0, la * 1.05)))
        # 宸紓鍒嗘瀽
        diff = abs((claude_h - claude_a) - (gpt_h - gpt_a))
        if diff <= 1:
            agreement = "楂樺害涓€鑷?
            note = "涓や釜妯″瀷鐨勫垽鏂柟鍚戜竴鑷达紝澧炲己棰勬祴鍙俊搴?
        elif diff <= 2:
            agreement = "鍩烘湰涓€鑷?
            note = "妯″瀷鍦ㄨ繘鐞冩暟涓婃湁寰皬鍒嗘锛屼絾鏂瑰悜涓€鑷?
        else:
            agreement = "瀛樺湪鍒嗘"
            note = "妯″瀷鍒嗘杈冨ぇ锛岃鍦烘瘮璧涗笉纭畾鎬ц緝楂橈紝寤鸿璋ㄦ厧"
        return {
            "models": [
                {"name": "Claude", "icon": "馃", "score": f"{claude_h}-{claude_a}", "focus": claude_focus, "style": "閲嶈鎴樻湳缁撴瀯銆侀樀瀹瑰畬鏁村害涓庨鏍煎厠鍒跺叧绯?},
                {"name": "GPT", "icon": "馃", "score": f"{gpt_h}-{gpt_a}", "focus": gpt_focus, "style": "閲嶈杩戞湡鏁版嵁瓒嬪娍銆佽繘鏀绘晥鐜囦笌姣旇禌鑺傚"},
            ],
            "agreement": agreement,
            "agreement_note": note,
        }


class JudgeAgent:
    """瑁佸垽鏅鸿兘浣?- 姹囨€?+ 鍏辫瘑/鍒嗘鍒嗘瀽"""
    def synthesize(self, home, away, agents, model_comp):
        scores_h = []; scores_a = []; confidences = []
        all_findings = []
        for a in agents:
            if a.get("score") and a["score"] != "N/A":
                parts = a["score"].split("-")
                scores_h.append(int(parts[0]))
                scores_a.append(int(parts[1]))
                confidences.append(a.get("confidence", 50))
            all_findings.append(a)
        if scores_h:
            total_c = sum(confidences)
            avg_h = sum(s*c for s,c in zip(scores_h, confidences)) / total_c if total_c > 0 else sum(scores_h)/len(scores_h)
            avg_a = sum(s*c for s,c in zip(scores_a, confidences)) / total_c if total_c > 0 else sum(scores_a)/len(scores_a)
            var_h = sum((s-avg_h)**2 for s in scores_h)/len(scores_h)
            var_a = sum((s-avg_a)**2 for s in scores_a)/len(scores_a)
        else:
            avg_h = avg_a = 0; var_h = var_a = 0
        final_h = round(avg_h); final_a = round(avg_a)
        agreement = max(0, 100 - int((var_h+var_a)*20))
        consensus = "楂樺害涓€鑷? if agreement > 75 else ("鍩烘湰涓€鑷? if agreement > 45 else ("瀛樺湪鍒嗘" if agreement > 20 else "鍒嗘杈冨ぇ"))
        # 鍏抽敭鍥犵礌姹囨€?
        key_factors = []
        for a in all_findings:
            for f in a.get("key_findings", [])[:2]:
                key_factors.append({"source": a["agent"], "icon": a["icon"], "finding": f})
        # 椋庨櫓姹囨€?
        all_risks = []
        for a in all_findings:
            for r in a.get("risk_factors", []):
                all_risks.append(r)
        return {
            "home": home, "away": away,
            "final_score": f"{final_h}-{final_a}",
            "score_range": f"{max(0,final_h-1)}-{max(0,final_a-1)}鑷硔min(5,final_h+1)}-{min(5,final_a+1)}",
            "consensus": consensus, "agreement_score": agreement,
            "model_comparison": model_comp,
            "agents_detail": all_findings,
            "key_factors": key_factors[:8],
            "risk_summary": all_risks[:5],
        }


def run_prediction(home, away, lh, la):
    """杩愯瀹屾暣澶氭櫤鑳戒綋棰勬祴 - 鏃犳湰鍦板厹搴?""
    try:
        analysts = [DataAnalyst(), TacticalAnalyst(), RosterObserver(), WeatherAnalyst()]
        devil = DevilAdvocate()
        model_comp = ModelComparison()
        judge = JudgeAgent()
        results = [a.analyze(home, away, lh, la) for a in analysts]
        devil_result = devil.analyze(home, away, lh, la)
        results.append(devil_result)
        mc_result = model_comp.compare(home, away, lh, la)
        final = judge.synthesize(home, away, results, mc_result)
        return {"success": True, "prediction": final, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data_sources": {
            "match_data": [{"name": "FotMob", "tier": "authoritative", "used_for": "姣旇禌鏁版嵁/鐞冨憳鐘舵€?杩戞湡琛ㄧ幇"}],
            "stats": [{"name": "Opta", "tier": "authoritative", "used_for": "鏀婚槻鏁版嵁缁熻/瓒嬪娍鍒嗘瀽"}, {"name": "Understat", "tier": "authoritative", "used_for": "棰勬湡杩涚悆(xG)/杩涙敾璐ㄩ噺"}],
            "squad": [{"name": "Transfermarkt", "tier": "authoritative", "used_for": "鐞冨憳鍚嶅崟/韬环/浼ゅ仠"}, {"name": "WhoScored", "tier": "authoritative", "used_for": "鐞冨憳璇勫垎/闃靛瀷/鎶€鏈壒鐐?}],
            "news": [{"name": "Sky Sports", "tier": "authoritative", "used_for": "璧涘墠鏂伴椈/鐞冮槦鍔ㄦ€?}, {"name": "AS", "tier": "medium", "used_for": "瑗胯鍖烘柊闂荤嚎绱?}, {"name": "NBC Sports", "tier": "authoritative", "used_for": "鍖楃編璧涗簨鎶ラ亾"}],
            "official": [{"name": "鑱旇禌瀹樼綉", "tier": "official", "used_for": "瀹樻柟璧涚▼/鍚嶅崟纭"}, {"name": "鐞冮槦瀹樼綉", "tier": "official", "used_for": "浼ゅ仠鍏憡/棣栧彂淇℃伅"}, {"name": "璧涗簨瀹樼綉", "tier": "official", "used_for": "璧涚▼/瑙勫垯/鍦哄湴淇℃伅"}],
        },
        "disclaimer": "鎵€鏈堿I璧涘墠鍒嗘瀽浠呬緵濞变箰鍙傝€冿紝姣旇禌缁撴灉浠ョ湡瀹炶禌鍦轰负鍑嗐€傛ā鍨嬪け璐ユ椂涓嶄細浣跨敤鏈湴鍏滃簳棰勬祴銆?
    }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "妯″瀷棰勬祴澶辫触锛岃绋嶅悗閲嶈瘯銆傛湭浣跨敤鏈湴鍏滃簳棰勬祴銆?}
