# -*- coding: utf-8 -*-
"""
娉婃澗鍒嗗竷 + 璐濆彾鏂洿鏂?瀹屾暣瓒崇悆棰勬祴寮曟搸
P(k;位) = (位^k * e^(-位)) / k!
鏀寔: 姣斿垎鐭╅樀銆佹€昏繘鐞冨垎甯冦€佸崐鍏ㄥ満姒傜巼銆佷笅娉ㄦ帹鑽愩€佽祫閲戝垎閰?
"""
import math, json
from team_names import translate

# ==========================================
# 1. 娉婃澗鍒嗗竷鏍稿績
# ==========================================
def poisson(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def poisson_pmf(lam, max_goals=8):
    probs = [poisson(k, lam) for k in range(max_goals + 1)]
    total = sum(probs)
    return [p / total for p in probs]

# ==========================================
# 2. 瀹屾暣姣斿垎姒傜巼鐭╅樀
# ==========================================
def full_score_matrix(lam_home, lam_away, max_goals=8):
    """杩斿洖 (matrix, win_p, draw_p, lose_p, all_scores_list)"""
    h_pmf = poisson_pmf(lam_home, max_goals)
    a_pmf = poisson_pmf(lam_away, max_goals)
    matrix, win_p, draw_p, lose_p = [], 0, 0, 0
    all_scores = []
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            prob = round(h_pmf[i] * a_pmf[j] * 100, 2)
            row.append(prob)
            all_scores.append({"home": i, "away": j, "prob": prob})
            if i > j: win_p += prob / 100
            elif i == j: draw_p += prob / 100
            else: lose_p += prob / 100
        matrix.append(row)
    all_scores.sort(key=lambda x: x["prob"], reverse=True)
    return matrix, round(win_p * 100, 1), round(draw_p * 100, 1), round(lose_p * 100, 1), all_scores

# ==========================================
# 3. 鎬昏繘鐞冩暟鍒嗗竷
# ==========================================
def total_goals_distribution(lam_home, lam_away, max_total=10):
    """P(鎬昏繘鐞?n) = 危_{i=0}^{n} P(涓?i) 脳 P(瀹?n-i)"""
    h_pmf = poisson_pmf(lam_home, max_total)
    a_pmf = poisson_pmf(lam_away, max_total)
    result = {}
    for n in range(max_total + 1):
        prob = 0
        for i in range(n + 1):
            if i < len(h_pmf) and (n - i) < len(a_pmf):
                prob += h_pmf[i] * a_pmf[n - i]
        result[n] = round(prob * 100, 2)
    return result

# ==========================================
# 4. 鍗婂叏鍦烘鐜?
# ==========================================
def half_full_time(lam_home, lam_away, max_goals=5):
    """
    鍗婂叏鍦? 涓婂崐鍦虹敤 位/2 (45鍒嗛挓), 涓嬪崐鍦哄悓鏍?位/2
    缁勫悎鍑?9 绉嶇粨鏋? 鑳滆儨/鑳滃钩/鑳滆礋/骞宠儨/骞冲钩/骞宠礋/璐熻儨/璐熷钩/璐熻礋
    """
    half_lam_h = lam_home / 2
    half_lam_a = lam_away / 2
    h_half = poisson_pmf(half_lam_h, max_goals)
    a_half = poisson_pmf(half_lam_a, max_goals)
    
    # 涓婂崐鍦虹粨鏋滄鐜?
    half_win = half_draw = half_lose = 0
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = h_half[i] * a_half[j]
            if i > j: half_win += prob
            elif i == j: half_draw += prob
            else: half_lose += prob
    
    # 涓嬪崐鍦虹嫭绔嬪悓鍒嗗竷
    sec_win = half_win
    sec_draw = half_draw
    sec_lose = half_lose
    
    # 鍗婂叏鍦?9 绉嶇粍鍚?
    htft = {
        "鑳滆儨": round(half_win * sec_win * 100, 2),
        "鑳滃钩": round(half_win * sec_draw * 100, 2),
        "鑳滆礋": round(half_win * sec_lose * 100, 2),
        "骞宠儨": round(half_draw * sec_win * 100, 2),
        "骞冲钩": round(half_draw * sec_draw * 100, 2),
        "骞宠礋": round(half_draw * sec_lose * 100, 2),
        "璐熻儨": round(half_lose * sec_win * 100, 2),
        "璐熷钩": round(half_lose * sec_draw * 100, 2),
        "璐熻礋": round(half_lose * sec_lose * 100, 2),
    }
    # 鎸夋鐜囨帓搴?
    sorted_htft = sorted(htft.items(), key=lambda x: x[1], reverse=True)
    return htft, sorted_htft

# ==========================================
# 5. 位 浼拌
# ==========================================
TEAM_STRENGTH = {
    "Argentina": 9.2, "Brazil": 9.0, "France": 9.3, "Germany": 8.5,
    "England": 8.8, "Spain": 8.7, "Portugal": 8.3, "Netherlands": 8.0,
    "Italy": 8.2, "Belgium": 7.8, "Croatia": 7.5, "Uruguay": 7.3,
    "Colombia": 7.2, "Morocco": 7.0, "Senegal": 6.5, "Japan": 6.8,
    "South Korea": 6.3, "Iran": 6.0, "Denmark": 7.0, "Mexico": 6.5,
    "United States": 6.8, "Switzerland": 6.5, "Austria": 6.0,
    "Serbia": 6.2, "Poland": 5.8, "Wales": 5.5, "Australia": 5.3,
    "Ecuador": 5.5, "Canada": 5.0, "Czechia": 5.8, "Sweden": 6.0,
    "Turkey": 5.8, "Ukraine": 5.5, "Scotland": 5.3, "Norway": 5.0,
    "Ghana": 5.0, "Cameroon": 5.2, "Nigeria": 5.5,
    "Algeria": 5.2, "Tunisia": 4.8, "South Africa": 4.5,
    "Costa Rica": 4.5, "Panama": 4.0, "Jamaica": 4.2,
    "Paraguay": 5.0, "Chile": 5.5,
    "Qatar": 4.5, "Saudi Arabia": 4.5, "Uzbekistan": 4.0,
    "China": 3.5, "New Zealand": 3.5, "Bosnia-Herzegovina": 4.8,
    "Slovakia": 5.0, "Slovenia": 4.8, "Greece": 5.2, "Hungary": 5.5,
    "Ivory Coast": 5.5, "Mali": 4.5,
}

def estimate_lambda(strength_home, strength_away, home_adv=0.3):
    avg = 1.35
    h = max(0.3, min(3.0, avg * (strength_home / 5.0) + home_adv))
    a = max(0.3, min(3.0, avg * (strength_away / 5.0)))
    return round(h, 2), round(a, 2)

def get_strength(team_name):
    return TEAM_STRENGTH.get(team_name, 5.0)

# ==========================================
# 6. 璐濆彾鏂姩鎬佹洿鏂?
# ==========================================
def bayesian_update(prior_lam, goals, time_ratio):
    if time_ratio <= 0: return prior_lam
    obs_rate = goals / time_ratio
    pw = max(0.2, 1.0 - time_ratio)
    ew = min(3.0, time_ratio * 3 + goals * 0.5)
    return round((pw * prior_lam + ew * obs_rate) / (pw + ew), 2)

# ==========================================
# 7. 涓嬫敞鎺ㄨ崘寮曟搸
# ==========================================
def betting_recommendation(analyses, budget):
    """
    鍩轰簬娉婃澗姒傜巼鍜岄绠楃殑璧勯噾鍒嗛厤鏂规
    绛栫暐: 鍑埄鍏紡鍚彂 - 鎶曟敞閲忎笌姒傜巼浼樺娍鎴愭瘮渚?
    """
    recs = []
    for r in analyses:
        pm = r["pre_match"]
        direction = r["direction"]
        # 鍩虹淇″績
        if direction == "涓昏儨": base_prob = pm["win"] / 100
        elif direction == "瀹㈣儨": base_prob = pm["lose"] / 100
        else: base_prob = pm["draw"] / 100
        
        # 闅愬惈璧旂巼 (鍋囪甯傚満璧旂巼 鈮?1/姒傜巼)
        implied_odds = 1 / base_prob if base_prob > 0 else 100
        # 姒傜巼浼樺娍 = 妯″瀷姒傜巼 - 闅愬惈姒傜巼 (绠€鍖?
        edge = max(0, base_prob - 0.35)  # 鍙湁35%浠ヤ笂鎵嶆湁姝ｆ湡鏈?
        
        # 鍑埄姣斾緥: f = (bp - q) / b, 绠€鍖栫増
        kelly = max(0, (base_prob * (implied_odds - 1) - (1 - base_prob)) / (implied_odds - 1))
        kelly = min(kelly, 0.25)  # 涓婇檺25%
        
        allocation = round(budget * kelly, 2)
        expected_return = round(allocation * (base_prob * implied_odds - 1), 2)
        
        recs.append({
            "match": f"{r['home_team']} vs {r['away_team']}",
            "direction": direction,
            "confidence": r["confidence"],
            "model_prob": round(base_prob * 100, 1),
            "implied_odds": round(implied_odds, 2),
            "kelly_fraction": round(kelly * 100, 1),
            "allocation": allocation,
            "expected_return": expected_return
        })
    
    # 鎸夊垎閰嶆帓搴?& 褰掍竴鍖栨€婚绠?
    recs.sort(key=lambda x: x["allocation"], reverse=True)
    total_alloc = sum(rc["allocation"] for rc in recs)
    
    for rc in recs:
        if total_alloc > 0:
            rc["allocation_pct"] = round(rc["allocation"] / total_alloc * 100, 1)
        else:
            rc["allocation_pct"] = 0
    
    return recs, round(budget - sum(rc["allocation"] for rc in recs), 2)

# ==========================================
# 8. 鍗曞満瀹屾暣鍒嗘瀽
# ==========================================
def analyze_match(home_team, away_team):
    home_cn = translate(home_team)
    away_cn = translate(away_team)
    hs = get_strength(home_team)
    as_ = get_strength(away_team)
    h_lam, a_lam = estimate_lambda(hs, as_)
    
    matrix, win_p, draw_p, lose_p, all_scores = full_score_matrix(h_lam, a_lam)
    total_goals = total_goals_distribution(h_lam, a_lam)
    htft_dict, htft_sorted = half_full_time(h_lam, a_lam)
    
    ms = all_scores[0] if all_scores else {"home":0,"away":0,"prob":0}
    
    direction = "涓昏儨" if win_p > draw_p and win_p > lose_p else ("瀹㈣儨" if lose_p > win_p and lose_p > draw_p else "骞冲眬")
    confidence = round(max(win_p, draw_p, lose_p))
    
    # 鎬昏繘鐞冩帓搴?
    total_goals_sorted = sorted(total_goals.items(), key=lambda x: x[1], reverse=True)
    most_likely_total = total_goals_sorted[0] if total_goals_sorted else (0, 0)
    
    return {
        "home_team": home_cn, "away_team": away_cn,
        "home_team_en": home_team, "away_team_en": away_team,
        "strength": {"home": hs, "away": as_},
        "lambda": {"home": h_lam, "away": a_lam},
        "pre_match": {
            "win": win_p, "draw": draw_p, "lose": lose_p,
            "most_likely_score": f"{ms['home']}-{ms['away']}",
            "most_likely_prob": round(ms["prob"], 1),
            "top_scores": [{"score": f"{s['home']}-{s['away']}", "prob": s["prob"]} for s in all_scores[:10]],
            "all_scores": all_scores,
            "matrix": matrix,
        },
        "total_goals": {
            "distribution": total_goals,
            "sorted": total_goals_sorted,
            "most_likely": most_likely_total[0],
            "most_likely_prob": most_likely_total[1],
            "over_2_5": round(sum(p for n, p in total_goals.items() if n > 2), 1),
            "under_2_5": round(sum(p for n, p in total_goals.items() if n <= 2), 1),
        },
        "half_full_time": {
            "dict": htft_dict,
            "sorted": htft_sorted,
            "most_likely": htft_sorted[0][0] if htft_sorted else "",
            "most_likely_prob": htft_sorted[0][1] if htft_sorted else 0,
        },
        "direction": direction,
        "confidence": confidence,
    }

def analyze_all_matches(matches):
    results = []
    for m in matches:
        r = analyze_match(m["home_team"], m["away_team"])
        r["id"] = m.get("id", 0)
        r["league"] = m.get("league", "")
        r["status"] = m.get("status", "")
        r["utcDate"] = m.get("utcDate", "")
        results.append(r)
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results