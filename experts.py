# -*- coding: utf-8 -*-
"""澶у姏绁炵畻 V2 - 鏂板6浣嶄笓椤规姇娉ㄤ笓瀹?""
import math, random, json, os

# ============ 1. 鑳滃钩璐熶笓瀹?============
class WinDrawLossExpert:
    def analyze(self, home, away, lh, la, hw_pct, d_pct, aw_pct):
        """鍩轰簬娉婃澗妯″瀷鐨勮儨骞宠礋娣卞害鍒嗘瀽"""
        # 璁＄畻缃俊鍖洪棿 (浣跨敤姝ｆ€佽繎浼?
        n_sim = 1000
        wins = 0; draws = 0; losses = 0
        
        def poisson(k, lam):
            if k < 0 or lam <= 0: return 0
            return math.exp(-lam) * (lam**k) / math.factorial(k)
        
        for _ in range(n_sim):
            h_goals = sum(1 for _ in range(int(lh * 10)) if random.random() < lh / 10)
            a_goals = sum(1 for _ in range(int(la * 10)) if random.random() < la / 10)
            # Poisson simulation
            hg = 0; ag = 0
            h_cum = 0; a_cum = 0
            for g in range(10):
                h_cum += poisson(g, lh)
                a_cum += poisson(g, la)
            # Simplified: use gaussian around lambda
            hg = max(0, round(random.gauss(lh, math.sqrt(lh))))
            ag = max(0, round(random.gauss(la, math.sqrt(la))))
            if hg > ag: wins += 1
            elif hg == ag: draws += 1
            else: losses += 1
        
        total = wins + draws + losses
        w_prob = wins / total * 100
        d_prob = draws / total * 100
        l_prob = losses / total * 100
        
        # 纭畾鎺ㄨ崘鏂瑰悜
        if w_prob > d_prob and w_prob > l_prob:
            pick = "涓昏儨"
            pick_prob = w_prob
        elif l_prob > w_prob and l_prob > d_prob:
            pick = "瀹㈣儨"
            pick_prob = l_prob
        else:
            pick = "骞冲眬"
            pick_prob = d_prob
            
        # 淇″績璇勭骇
        max_prob = max(w_prob, d_prob, l_prob)
        if max_prob > 55: confidence = "楂?
        elif max_prob > 40: confidence = "涓?
        else: confidence = "浣?
        
        # 璧旂巼寤鸿
        fair_odds_w = round(100 / max(w_prob, 1), 2)
        fair_odds_d = round(100 / max(d_prob, 1), 2)
        fair_odds_l = round(100 / max(l_prob, 1), 2)
        
        return {
            "agent": "鑳滃钩璐熶笓瀹?,
            "icon": "鈿?,
            "home_win": round(w_prob, 1),
            "draw": round(d_prob, 1),
            "away_win": round(l_prob, 1),
            "pick": pick,
            "pick_prob": round(pick_prob, 1),
            "confidence": confidence,
            "fair_odds": {"win": fair_odds_w, "draw": fair_odds_d, "lose": fair_odds_l},
            "key_findings": [
                f"涓昏儨姒傜巼: {w_prob:.1f}% (鍏钩璧旂巼: {fair_odds_w})",
                f"骞冲眬姒傜巼: {d_prob:.1f}% (鍏钩璧旂巼: {fair_odds_d})",
                f"瀹㈣儨姒傜巼: {l_prob:.1f}% (鍏钩璧旂巼: {fair_odds_l})",
                f"鎺ㄨ崘: {pick} (缃俊搴? {confidence})",
            ],
            "verdict": f"鎺ㄨ崘{pick}锛屾鐜噞pick_prob:.1f}%锛岀疆淇″害{confidence}"
        }


# ============ 2. 璁╃悆涓撳 ============
class HandicapExpert:
    def analyze(self, home, away, lh, la):
        """浜氭床璁╃悆鐩樺垎鏋?""
        # 璁＄畻鍏钩璁╃悆
        goal_diff = lh - la
        if goal_diff > 0.8:
            handicap = f"涓婚槦璁﹞round(goal_diff * 0.5, 2)}鐞?
            base_line = -goal_diff * 0.5
        elif goal_diff < -0.8:
            handicap = f"瀹㈤槦璁﹞round(-goal_diff * 0.5, 2)}鐞?
            base_line = -goal_diff * 0.5
        else:
            handicap = "骞虫墜鐩?
            base_line = 0
            
        # 妯℃嫙瑕嗙洊姒傜巼
        n_sim = 1000
        cover = 0; push = 0; fail = 0
        for _ in range(n_sim):
            hg = max(0, round(random.gauss(lh, math.sqrt(max(0.1, lh)))))
            ag = max(0, round(random.gauss(la, math.sqrt(max(0.1, la)))))
            adjusted = hg - ag + base_line
            if adjusted > 0: cover += 1
            elif adjusted == 0: push += 1
            else: fail += 1
            
        total = cover + push + fail
        cover_pct = cover / total * 100
        push_pct = push / total * 100
        fail_pct = fail / total * 100
        
        if cover_pct > fail_pct + 5:
            recommendation = "涓婄洏"
            rec_conf = "涓? if cover_pct > 55 else "浣?
        elif fail_pct > cover_pct + 5:
            recommendation = "涓嬬洏"
            rec_conf = "涓? if fail_pct > 55 else "浣?
        else:
            recommendation = "璧版按椋庨櫓楂橈紝璋ㄦ厧"
            rec_conf = "浣?
            
        return {
            "agent": "璁╃悆涓撳",
            "icon": "馃幆",
            "fair_handicap": handicap,
            "cover_prob": round(cover_pct, 1),
            "push_prob": round(push_pct, 1),
            "fail_prob": round(fail_pct, 1),
            "recommendation": recommendation,
            "rec_confidence": rec_conf,
            "key_findings": [
                f"鍏钩璁╃悆: {handicap}",
                f"涓婄洏姒傜巼: {cover_pct:.1f}% | 璧版按: {push_pct:.1f}% | 涓嬬洏: {fail_pct:.1f}%",
                f"鎺ㄨ崘: {recommendation} (缃俊搴? {rec_conf})",
            ],
            "verdict": f"{handicap} | 鎺ㄨ崘{recommendation}"
        }


# ============ 3. 鎬昏繘鐞冧笓瀹?============
class TotalGoalsExpert:
    def analyze(self, home, away, lh, la):
        """鎬昏繘鐞冩暟鍒嗘瀽 (澶у皬鐞?"""
        def poisson(k, lam):
            if k < 0 or lam <= 0: return 0
            return math.exp(-lam) * (lam**k) / math.factorial(k)
            
        total_lambda = lh + la
        tg_probs = {}
        for n in range(10):
            prob = sum(poisson(h, lh) * poisson(n-h, la) for h in range(min(n, 8)+1) if 0 <= n-h <= 8)
            tg_probs[n] = round(prob * 100, 1)
            
        # 澶у皬鐞冨垎鏋?(2.5鐞冪嚎)
        under_2_5 = sum(tg_probs.get(n, 0) for n in range(3))
        over_2_5 = 100 - under_2_5
        
        # 鏈€浣虫€昏繘鐞冩帹鑽?
        best_goals = max(tg_probs, key=tg_probs.get)
        best_prob = tg_probs[best_goals]
        
        # 澶у皬鐞冩帹鑽?
        if over_2_5 > 55:
            ou_pick = "澶х悆(>2.5)"
            ou_conf = "涓? if over_2_5 > 60 else "浣?
        elif under_2_5 > 55:
            ou_pick = "灏忕悆(<2.5)"
            ou_conf = "涓? if under_2_5 > 60 else "浣?
        else:
            ou_pick = "澶х悆/灏忕悆姒傜巼鎺ヨ繎"
            ou_conf = "浣?
            
        return {
            "agent": "鎬昏繘鐞冧笓瀹?,
            "icon": "鈿?,
            "expected_goals": round(total_lambda, 2),
            "best_goals": best_goals,
            "best_goals_prob": best_prob,
            "over_2_5": round(over_2_5, 1),
            "under_2_5": round(under_2_5, 1),
            "ou_pick": ou_pick,
            "ou_confidence": ou_conf,
            "goal_probs": {str(k): v for k, v in sorted(tg_probs.items())[:8]},
            "key_findings": [
                f"棰勬湡鎬昏繘鐞? {total_lambda:.2f}鐞?,
                f"鏈€鍙兘鎬昏繘鐞? {best_goals}鐞?({best_prob:.1f}%)",
                f"澶х悆(>2.5): {over_2_5:.1f}% | 灏忕悆(<2.5): {under_2_5:.1f}%",
                f"鎺ㄨ崘: {ou_pick} (缃俊搴? {ou_conf})",
            ],
            "verdict": f"棰勬湡{total_lambda:.1f}鐞?| {ou_pick}"
        }


# ============ 4. 姣斿垎涓撳 ============
class CorrectScoreExpert:
    def analyze(self, home, away, lh, la):
        """姝ｇ‘姣斿垎鍒嗘瀽"""
        def poisson(k, lam):
            if k < 0 or lam <= 0: return 0
            return math.exp(-lam) * (lam**k) / math.factorial(k)
            
        score_probs = []
        for h in range(7):
            for a in range(7):
                prob = poisson(h, lh) * poisson(a, la) * 100
                if prob > 0.01:
                    score_probs.append({"score": f"{h}-{a}", "prob": round(prob, 2)})
                    
        score_probs.sort(key=lambda x: -x["prob"])
        top_scores = score_probs[:5]
        
        # 鏈€甯歌姣斿垎鍖洪棿
        h_most = max(range(5), key=lambda x: poisson(x, lh))
        a_most = max(range(5), key=lambda x: poisson(x, la))
        
        # 姣斿垎鐜╂硶寤鸿
        if top_scores[0]["prob"] > 15:
            score_confidence = "杈冮珮"
        elif top_scores[0]["prob"] > 8:
            score_confidence = "涓瓑"
        else:
            score_confidence = "杈冧綆(姣斿垎鐜╂硶椋庨櫓楂?"
            
        return {
            "agent": "姣斿垎涓撳",
            "icon": "馃幆",
            "top_scores": top_scores,
            "most_likely_range": f"{max(0, h_most-1)}-{max(0, a_most-1)} 鑷?{h_most+1}-{a_most+1}",
            "score_confidence": score_confidence,
            "key_findings": [
                f"鏈€鍙兘姣斿垎: {top_scores[0]['score']} ({top_scores[0]['prob']:.1f}%)" if top_scores else "",
                f"绗簩姣斿垎: {top_scores[1]['score']} ({top_scores[1]['prob']:.1f}%)" if len(top_scores) > 1 else "",
                f"姣斿垎鍖洪棿: {max(0, h_most-1)}-{max(0, a_most-1)} 鑷?{h_most+1}-{a_most+1}",
                f"姣斿垎鐜╂硶缃俊搴? {score_confidence}",
            ],
            "verdict": f"鏈€鍙兘 {top_scores[0]['score']} ({top_scores[0]['prob']:.1f}%)" if top_scores else "鏁版嵁涓嶈冻"
        }


# ============ 5. 鍗婂叏鍦轰笓瀹?============
class HalfFullExpert:
    def analyze(self, home, away, lh, la):
        """鍗婂叏鍦虹帺娉曞垎鏋?""
        # 鍗婂満lambda绾︿负鍏ㄥ満鐨?4%
        h_lambda_half = lh * 0.44
        a_lambda_half = la * 0.44
        
        def half_result(hl, al):
            hw = 0; d = 0; aw = 0
            def poisson(k, lam):
                if k < 0 or lam <= 0: return 0
                return math.exp(-lam) * (lam**k) / math.factorial(k)
            for h in range(5):
                for a in range(5):
                    p = poisson(h, hl) * poisson(a, al)
                    if h > a: hw += p
                    elif h == a: d += p
                    else: aw += p
            total = hw + d + aw
            return {"鑳?: hw/total*100 if total > 0 else 33, "骞?: d/total*100 if total > 0 else 34, "璐?: aw/total*100 if total > 0 else 33}
        
        half_p = half_result(h_lambda_half, a_lambda_half)
        full_p = half_result(lh, la)
        
        combos = [
            ("鑳滆儨", "鑳?, "鑳?), ("鑳滃钩", "鑳?, "骞?), ("鑳滆礋", "鑳?, "璐?),
            ("骞宠儨", "骞?, "鑳?), ("骞冲钩", "骞?, "骞?), ("骞宠礋", "骞?, "璐?),
            ("璐熻儨", "璐?, "鑳?), ("璐熷钩", "璐?, "骞?), ("璐熻礋", "璐?, "璐?),
        ]
        
        results = []
        for name, hk, fk in combos:
            prob = half_p[hk] * full_p[fk] / 100
            results.append({"result": name, "prob": round(prob, 1)})
        
        results.sort(key=lambda x: -x["prob"])
        top_3 = results[:3]
        
        # 鍒ゆ柇閫傚悎鍗婂叏鍦虹帺娉曞悧
        if top_3[0]["prob"] > 25:
            hf_suitable = "闈炲父閫傚悎"
        elif top_3[0]["prob"] > 15:
            hf_suitable = "閫傚悎"
        else:
            hf_suitable = "鍙樻暟杈冨ぇ锛岃皑鎱?
            
        return {
            "agent": "鍗婂叏鍦轰笓瀹?,
            "icon": "馃攧",
            "top_combos": top_3,
            "all_combos": results,
            "suitability": hf_suitable,
            "key_findings": [
                f"鏈€鍙兘鍗婂叏鍦? {top_3[0]['result']} ({top_3[0]['prob']:.1f}%)",
                f"绗簩: {top_3[1]['result']} ({top_3[1]['prob']:.1f}%)",
                f"绗笁: {top_3[2]['result']} ({top_3[2]['prob']:.1f}%)",
                f"鍗婂叏鍦虹帺娉曢€傚悎搴? {hf_suitable}",
            ],
            "verdict": f"鎺ㄨ崘 {top_3[0]['result']} ({top_3[0]['prob']:.1f}%) | {hf_suitable}"
        }


# ============ 6. 璧勯噾鍒嗛厤涓撳 ============
class BankrollExpert:
    def analyze(self, home, away, lh, la, win_pct, draw_pct, away_pct):
        """鍩轰簬鍑埄鍏紡鐨勮祫閲戝垎閰嶅缓璁?""
        def poisson(k, lam):
            if k < 0 or lam <= 0: return 0
            return math.exp(-lam) * (lam**k) / math.factorial(k)
        
        # 璁＄畻鍚勭帺娉曠殑鏈€浼樿禂鐜囧拰姒傜巼
        # 鑳滃钩璐?
        spf_odds = {
            "涓昏儨": round(100 / max(win_pct, 1), 2),
            "骞冲眬": round(100 / max(draw_pct, 1), 2),
            "瀹㈣儨": round(100 / max(away_pct, 1), 2),
        }
        spf_probs = {"涓昏儨": win_pct/100, "骞冲眬": draw_pct/100, "瀹㈣儨": away_pct/100}
        
        # 鍑埄鍏紡: f = (bp - q) / b = p - q/b
        # 绠€鍖栫増锛氬嚡鍒╂瘮渚?= 姒傜巼 - (1-姒傜巼)/(璧旂巼-1)
        kelly_bets = []
        for bet_name in ["涓昏儨", "骞冲眬", "瀹㈣儨"]:
            p = spf_probs[bet_name]
            b = spf_odds[bet_name] - 1  # 鍑€璧旂巼
            if b > 0:
                kelly = (p * b - (1 - p)) / b
                kelly = max(0, kelly)  # 璐熸暟涓嶆姇
            else:
                kelly = 0
            if kelly > 0.001:
                kelly_bets.append({"play": "鑳滃钩璐?, "pick": bet_name, "prob": round(p*100, 1), "odds": spf_odds[bet_name], "kelly": round(kelly*100, 1)})
        
        kelly_bets.sort(key=lambda x: -x["kelly"])
        
        # 璧勯噾鍒嗛厤鏂规
        # 淇濆畧: 鍑埄/4, 绋冲仴: 鍑埄/2, 杩涘彇: 鍑埄
        allocation_plan = {
            "conservative": {"name": "淇濆畧鏂规", "ratio": 0.25, "desc": "姣忔鎶曟敞鏈噾鐨?/4鍑埄姣斾緥锛岄€傚悎闀挎湡绋冲畾"},
            "moderate": {"name": "绋冲仴鏂规", "ratio": 0.5, "desc": "姣忔鎶曟敞鏈噾鐨?/2鍑埄姣斾緥锛屽钩琛￠闄╂敹鐩?},
            "aggressive": {"name": "杩涘彇鏂规", "ratio": 1.0, "desc": "鍏ㄥ嚡鍒╂瘮渚嬶紝楂樻敹鐩婁絾娉㈠姩澶?},
        }
        
        # 涓插叧寤鸿
        combo_advice = []
        if len(kelly_bets) >= 4:
            combo_advice.append("鍙€冭檻2涓?缁勫悎楂樻鐜囬€夐」")
        if len(kelly_bets) >= 3:
            combo_advice.append("3涓?寤鸿浠呯敤浜庡ū涔愶紝椋庨櫓鏋侀珮")
        combo_advice.append("鍗曞叧鎶曟敞涓烘渶绋冲畾鏂瑰紡")
        
        # 浠撲綅绠＄悊
        if kelly_bets and kelly_bets[0]["kelly"] > 5:
            position = "鍙€傚綋鍔犲ぇ浠撲綅"
        elif kelly_bets and kelly_bets[0]["kelly"] > 2:
            position = "姝ｅ父浠撲綅"
        else:
            position = "杞讳粨鎴栬鏈?
            
        return {
            "agent": "璧勯噾鍒嗛厤涓撳",
            "icon": "馃挵",
            "kelly_bets": kelly_bets[:5],
            "allocation_plan": allocation_plan,
            "position_advice": position,
            "combo_advice": combo_advice,
            "key_findings": [
                f"鏈€浣冲嚡鍒╂姇娉? {kelly_bets[0]['play']}-{kelly_bets[0]['pick']} (鍑埄{kelly_bets[0]['kelly']:.1f}%)" if kelly_bets else "鏃犳槑鏄炬鏈熸湜鎶曟敞",
                f"浠撲綅寤鸿: {position}",
                f"淇濆畧姣忔鎶曟敞: {kelly_bets[0]['kelly']*0.25:.1f}%鏈噾" if kelly_bets else "",
            ] + combo_advice,
            "verdict": f"{position} | 鎺ㄨ崘{'鑳滃钩璐? if kelly_bets else '瑙傛湜'}" + (f"-{kelly_bets[0]['pick']}" if kelly_bets else "")
        }


# ============ 鏁村悎鍒皉un_prediction ============
def run_all_experts(home, away, lh, la, win_pct, draw_pct, away_pct):
    """杩愯鍏ㄩ儴11浣嶄笓瀹?""
    experts = {}
    
    # 鍘熸湁5浣?(浠巋ercules涓绘ā鍧楄皟鐢?
    # 鏂板6浣嶄笓椤逛笓瀹?
    try:
        experts["win_draw_loss"] = WinDrawLossExpert().analyze(home, away, lh, la, win_pct, draw_pct, away_pct)
    except Exception as e:
        experts["win_draw_loss"] = {"error": str(e)}
        
    try:
        experts["handicap"] = HandicapExpert().analyze(home, away, lh, la)
    except Exception as e:
        experts["handicap"] = {"error": str(e)}
        
    try:
        experts["total_goals"] = TotalGoalsExpert().analyze(home, away, lh, la)
    except Exception as e:
        experts["total_goals"] = {"error": str(e)}
        
    try:
        experts["correct_score"] = CorrectScoreExpert().analyze(home, away, lh, la)
    except Exception as e:
        experts["correct_score"] = {"error": str(e)}
        
    try:
        experts["half_full"] = HalfFullExpert().analyze(home, away, lh, la)
    except Exception as e:
        experts["half_full"] = {"error": str(e)}
        
    try:
        experts["bankroll"] = BankrollExpert().analyze(home, away, lh, la, win_pct, draw_pct, away_pct)
    except Exception as e:
        experts["bankroll"] = {"error": str(e)}
        
    return experts
