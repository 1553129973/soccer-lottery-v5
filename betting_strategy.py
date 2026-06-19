# -*- coding: utf-8 -*-
"""
鏅鸿兘鎶曟敞绛栫暐寮曟搸
- 鑷姩鍒ゆ柇姣忓満鏈€浣崇帺娉?(鑳滃钩璐?姣斿垎/鎬昏繘鐞?鍗婂叏鍦?
- 涓插叧缁勫悎浼樺寲 (2涓?~4涓?)
- 鍑埄鍏紡璧勯噾鍒嗛厤
"""
import math
from itertools import combinations

# ==========================================
# 1. 鐜╂硶閫傞厤搴﹁瘎鍒?
# ==========================================
def play_type_analysis(result):
    """
    鍒嗘瀽姣忓満姣旇禌鏈€閫傚悎鐨勭帺娉?
    杩斿洖姣忕鐜╂硶鐨勮瘎鍒嗗拰鎺ㄨ崘鐞嗙敱
    """
    pm = result["pre_match"]
    tg = result["total_goals"]
    htft = result["half_full_time"]
    
    scores = {}
    
    # --- 鑳滃钩璐熻瘎鍒?---
    # 鏂瑰悜姒傜巼瓒婇珮 + 姒傜巼浼樺娍瓒婂ぇ = 瓒婇€傚悎
    max_prob = max(pm["win"], pm["draw"], pm["lose"])
    min_prob = min(pm["win"], pm["draw"], pm["lose"])
    spread = max_prob - min_prob  # 姒傜巼宸窛
    wdl_score = (max_prob / 100) * 0.5 + (spread / 100) * 0.5
    wdl_score = round(wdl_score * 100)
    
    scores["鑳滃钩璐?] = {
        "score": wdl_score,
        "suitable": wdl_score >= 55,
        "reason": f"鏂瑰悜鏄庣‘锛寋result['direction']}姒傜巼{max_prob}%锛屼笌绗簩閫夐」宸畕spread}%",
        "pick": result["direction"],
        "prob": max_prob,
    }
    
    # --- 姣斿垎鐜╂硶璇勫垎 ---
    # Top姣斿垎姒傜巼瓒婇珮 + Top3瑕嗙洊瓒婇泦涓?= 瓒婇€傚悎
    top_score_prob = pm["top_scores"][0]["prob"]
    top3_coverage = sum(s["prob"] for s in pm["top_scores"][:3])
    score_score = (top_score_prob / 15) * 0.5 + (top3_coverage / 50) * 0.5
    score_score = min(100, round(score_score * 100))
    
    top3_str = ", ".join(f"{s['score']}({s['prob']}%)" for s in pm["top_scores"][:3])
    scores["姣斿垎"] = {
        "score": score_score,
        "suitable": score_score >= 45,
        "reason": f"Top1:{pm['top_scores'][0]['score']}({top_score_prob}%), Top3瑕嗙洊{round(top3_coverage)}%: {top3_str}",
        "pick": pm["top_scores"][0]["score"],
        "prob": top_score_prob,
        "top3": pm["top_scores"][:3],
    }
    
    # --- 鎬昏繘鐞冭瘎鍒?---
    # 鏈€鍙兘杩涚悆姒傜巼瓒婇珮 + 澶у皬鐞冨垎鍖栬秺鏄庢樉 = 瓒婇€傚悎
    top_goal_prob = tg["most_likely_prob"]
    over_under_spread = abs(tg["over_2_5"] - tg["under_2_5"])
    goal_score = (top_goal_prob / 25) * 0.5 + (over_under_spread / 100) * 0.5
    goal_score = min(100, round(goal_score * 100))
    
    over_under_pick = "澶?.5" if tg["over_2_5"] > tg["under_2_5"] else "灏?.5"
    scores["鎬昏繘鐞?] = {
        "score": goal_score,
        "suitable": goal_score >= 45,
        "reason": f"鏈€鍙兘{tg['most_likely']}鐞?{tg['most_likely_prob']}%), {over_under_pick}({max(tg['over_2_5'], tg['under_2_5'])}%)",
        "pick": f"{tg['most_likely']}鐞?,
        "prob": tg["most_likely_prob"],
        "over_under": {"pick": over_under_pick, "prob": max(tg["over_2_5"], tg["under_2_5"])},
    }
    
    # --- 鍗婂叏鍦鸿瘎鍒?---
    # Top鍗婂叏鍦烘鐜囪秺楂樿秺閫傚悎
    top_htft_prob = htft["sorted"][0][1]
    top2_coverage = htft["sorted"][0][1] + htft["sorted"][1][1]
    htft_score = (top_htft_prob / 30) * 0.6 + (top2_coverage / 50) * 0.4
    htft_score = min(100, round(htft_score * 100))
    
    scores["鍗婂叏鍦?] = {
        "score": htft_score,
        "suitable": htft_score >= 40,
        "reason": f"Top:{htft['sorted'][0][0]}({htft['sorted'][0][1]}%), 绗簩:{htft['sorted'][1][0]}({htft['sorted'][1][1]}%)",
        "pick": htft["sorted"][0][0],
        "prob": htft["sorted"][0][1],
        "top2": htft["sorted"][:2],
    }
    
    # 鏈€浣崇帺娉?
    best = max(scores.items(), key=lambda x: x[1]["score"])
    
    return {
        "scores": scores,
        "best_play": best[0],
        "best_score": best[1]["score"],
        "recommendation": f"鎺ㄨ崘銆恵best[0]}銆戠帺娉曪細{best[1]['reason']}",
    }

# ==========================================
# 2. 涓插叧缁勫悎寮曟搸
# ==========================================
def parlay_combinations(analyses, max_parlay=4):
    """
    鐢熸垚涓插叧鎺ㄨ崘
    绛栫暐: 閫夐珮淇″績鍦烘缁勫悎锛岃绠楃粍鍚堟鐜囧拰鏈熸湜鍥炴姤
    """
    # 绛涢€夐€傚悎涓插叧鐨勫満娆?(淇″績 >= 50%)
    candidates = [a for a in analyses if a["confidence"] >= 45]
    if len(candidates) < 2:
        return {}
    
    parlays = {}
    for size in range(2, min(max_parlay + 1, len(candidates) + 1)):
        combos = []
        for combo in combinations(candidates, size):
            # 璁＄畻涓插叧缁勫悎姒傜巼
            combined_prob = 1.0
            total_confidence = 0
            match_names = []
            picks = []
            for r in combo:
                pm = r["pre_match"]
                if r["direction"] == "涓昏儨":
                    prob = pm["win"] / 100
                elif r["direction"] == "瀹㈣儨":
                    prob = pm["lose"] / 100
                else:
                    prob = pm["draw"] / 100
                combined_prob *= prob
                total_confidence += r["confidence"]
                match_names.append(f"{r['home_team']}vs{r['away_team']}({r['direction']})")
                picks.append(r["direction"])
            
            avg_confidence = total_confidence / size
            # 鏈熸湜璧旂巼 (鍋囪鍗曞満璧旂巼 鈮?1/姒傜巼 * 0.9 搴勫鎶芥按)
            implied_odds = 1 / combined_prob * (0.9 ** size)
            
            combos.append({
                "matches": match_names,
                "picks": picks,
                "combined_prob": round(combined_prob * 100, 1),
                "avg_confidence": round(avg_confidence),
                "implied_odds": round(implied_odds, 2),
                "expected_value": round(combined_prob * implied_odds - 1, 3),
            })
        
        # 鎺掑簭: 鎸夋湡鏈涘€?脳 姒傜巼
        combos.sort(key=lambda x: x["combined_prob"] * x["implied_odds"], reverse=True)
        parlays[f"{size}涓?"] = combos[:3]  # Top 3
    
    return parlays

# ==========================================
# 3. 瀹屾暣涓嬫敞鏂规鐢熸垚
# ==========================================
def generate_full_betting_plan(analyses, budget):
    """
    鐢熸垚瀹屾暣鎶曟敞鏂规
    杩斿洖: { single_bets, parlays, summary }
    """
    plan = {
        "budget": budget,
        "single_bets": [],
        "parlays": {},
        "summary": {},
    }
    
    # --- 鍗曞満鎺ㄨ崘 ---
    for r in analyses:
        play = play_type_analysis(r)
        best = play["best_play"]
        best_info = play["scores"][best]
        
        # 鍑埄璁＄畻鍗曞満鎶曟敞
        prob = best_info["prob"] / 100
        if prob > 0.35:
            implied_odds = 1 / prob * 0.9
            kelly = max(0, (prob * (implied_odds - 1) - (1 - prob)) / (implied_odds - 1))
            kelly = min(kelly, 0.15)  # 鍗曞満涓婇檺15%
        else:
            kelly = 0
        
        allocation = round(budget * kelly, 2)
        
        plan["single_bets"].append({
            "match": f"{r['home_team']} vs {r['away_team']}",
            "confidence": r["confidence"],
            "best_play": best,
            "best_score": play["best_score"],
            "pick": best_info["pick"],
            "pick_prob": best_info["prob"],
            "reason": best_info["reason"],
            "kelly_pct": round(kelly * 100, 1),
            "allocation": allocation,
            "all_plays": {k: {"score": v["score"], "suitable": v["suitable"]} for k, v in play["scores"].items()},
        })
    
    # --- 涓插叧鎺ㄨ崘 ---
    parlays = parlay_combinations(analyses)
    
    # 鍒嗛厤涓插叧棰勭畻 (鎬婚绠楃殑30%)
    parlay_budget = round(budget * 0.3, 2)
    parlay_plan = {}
    total_weight = 0
    
    for size_name, combos in parlays.items():
        for combo in combos:
            weight = combo["combined_prob"] / 100 * combo["implied_odds"]
            combo["weight"] = weight
            total_weight += weight
    
    for size_name, combos in parlays.items():
        parlay_plan[size_name] = []
        for combo in combos:
            if total_weight > 0:
                alloc = round(parlay_budget * combo["weight"] / total_weight, 2)
            else:
                alloc = 0
            combo["allocation"] = alloc
            parlay_plan[size_name].append(combo)
    
    plan["parlays"] = parlay_plan
    plan["parlay_budget"] = parlay_budget
    
    # --- 姹囨€?---
    single_total = sum(b["allocation"] for b in plan["single_bets"])
    parlay_total = sum(c["allocation"] for combos in parlay_plan.values() for c in combos)
    
    # 鍊嶆暟寤鸿: 鏍规嵁棰勭畻绾у埆
    if budget <= 10:
        multiplier = 1
        multiplier_note = "灏忛棰勭畻锛屽缓璁?鍊嶆姇娉?
    elif budget <= 50:
        multiplier = max(1, budget // 20)
        multiplier_note = f"寤鸿{multiplier}鍊嶆姇娉紝鍒嗘暎椋庨櫓"
    elif budget <= 200:
        multiplier = max(2, budget // 30)
        multiplier_note = f"寤鸿{multiplier}鍊嶆姇娉紝鍗曞叧涓轰富+灏忎覆涓鸿緟"
    else:
        multiplier = max(3, budget // 50)
        multiplier_note = f"寤鸿{multiplier}鍊嶆姇娉紝鍗曞叧+涓插叧鍧囪　閰嶇疆"
    
    plan["summary"] = {
        "single_total": single_total,
        "parlay_total": parlay_total,
        "total_allocated": single_total + parlay_total,
        "remaining": round(budget - single_total - parlay_total, 2),
        "multiplier": multiplier,
        "multiplier_note": multiplier_note,
        "strategy": generate_strategy_text(plan, multiplier),
    }
    
    return plan

def generate_strategy_text(plan, multiplier):
    """鐢熸垚绛栫暐璇存槑鏂囧瓧"""
    lines = []
    lines.append(f"馃搵 鎬婚绠?{plan['budget']}鍏?脳 {multiplier}鍊?= 瀹為檯鎶曟敞 {plan['budget'] * multiplier}鍏?)
    lines.append(f"馃挵 鍗曞叧鍒嗛厤: {plan['summary']['single_total']}鍏?({round(plan['summary']['single_total']/plan['budget']*100)}%)")
    lines.append(f"馃敆 涓插叧鍒嗛厤: {plan['summary']['parlay_total']}鍏?({round(plan['summary']['parlay_total']/plan['budget']*100)}%)")
    lines.append(f"馃洝锔?淇濈暀: {plan['summary']['remaining']}鍏?)
    
    # 鍗曞叧绛栫暐
    active_singles = [b for b in plan["single_bets"] if b["allocation"] >= 2]
    if active_singles:
        lines.append(f"\n鉁?鍗曞叧鎶曟敞 ({len(active_singles)}鍦?:")
        for b in active_singles:
            lines.append(f"  {b['match']}: {b['best_play']}鈫抺b['pick']} | {b['allocation']}鍏?)
    
    # 涓插叧绛栫暐
    for size_name, combos in plan["parlays"].items():
        active_combos = [c for c in combos if c["allocation"] >= 2]
        if active_combos:
            lines.append(f"\n馃敆 {size_name}:")
            for c in active_combos:
                lines.append(f"  {' + '.join(c['matches'])} | 缁煎悎姒傜巼{c['combined_prob']}% | {c['allocation']}鍏?)
    
    return "\n".join(lines)

# ==========================================
# 4. 鍚勭帺娉曢€傜敤鏃舵満鍒嗘瀽
# ==========================================
def when_to_use_which_play(analyses):
    """
    鍩轰簬浠婃棩鎵€鏈夊満娆★紝鍒嗘瀽浠€涔堟椂鍊欓€傚悎浠€涔堢帺娉?
    """
    all_scores = {"鑳滃钩璐?: [], "姣斿垎": [], "鎬昏繘鐞?: [], "鍗婂叏鍦?: []}
    
    for r in analyses:
        play = play_type_analysis(r)
        for play_name, info in play["scores"].items():
            all_scores[play_name].append({
                "match": f"{r['home_team']}vs{r['away_team']}",
                "score": info["score"],
                "suitable": info["suitable"],
            })
    
    # 姣忕被鐜╂硶鐨勫钩鍧囧垎
    advice = {}
    for play_name, items in all_scores.items():
        avg = sum(i["score"] for i in items) / len(items) if items else 0
        suitable_count = sum(1 for i in items if i["suitable"])
        
        if play_name == "鑳滃钩璐?:
            condition = "鏂瑰悜姒傜巼浼樺娍 > 20%鏃舵渶浣炽€備粖鏃? + ("閫傚悎澶氬満" if suitable_count >= len(items)//2 else "闇€绮鹃€?)
            typical = "璧旂巼1.5-2.5锛岀ǔ瀹氭€ф渶楂橈紝閫傚悎鍋氫覆鍏冲熀纭€"
        elif play_name == "姣斿垎":
            condition = "Top姣斿垎姒傜巼 > 10%鏃惰€冭檻銆備粖鏃? + ("鏈夐泦涓瘮鍒? if suitable_count > 0 else "姣斿垎杈冨垎鏁?)
            typical = "璧旂巼6-50鍊嶏紝楂樺洖鎶ヤ絾浣庡懡涓紝閫傚悎灏忛鍗氬喎"
        elif play_name == "鎬昏繘鐞?:
            condition = "鏈€鍙兘杩涚悆姒傜巼 > 18%鏃惰緝浼樸€備粖鏃? + ("杩涚悆鍒嗗竷闆嗕腑" if suitable_count > 0 else "杩涚悆鍒嗗竷鍧囧寑")
            typical = "璧旂巼1.8-4鍊嶏紝涓瓑椋庨櫓锛屽ぇ灏忕悆鍒ゆ柇杈呭姪"
        elif play_name == "鍗婂叏鍦?:
            condition = "Top鍗婂叏鍦烘鐜?> 20%鏃舵渶浼樸€備粖鏃? + ("鍗婂叏鍦洪泦涓? if suitable_count > 0 else "鍗婂叏鍦哄垎鏁?)
            typical = "璧旂巼3-15鍊嶏紝闇€鐞冮槦椋庢牸鏀寔锛堟參鐑?鎶㈠紑灞€鍨嬶級"
        
        advice[play_name] = {
            "avg_score": round(avg),
            "suitable_matches": suitable_count,
            "condition": condition,
            "typical_odds": typical,
        }
    
    return advice