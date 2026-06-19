# -*- coding: utf-8 -*-
"""澶氭簮铻嶅悎寮曟搸 - 娉婃澗+澶у姏绁炵畻+涓撳+鍏埢"""
import math, json, os

WEIGHTS = {"poisson": 40, "hercules": 25, "experts": 20, "liuyao": 15}

def fuse_prediction(home, away, lh, la, date_str):
    from poisson_bayes import full_score_matrix
    from hercules import run_prediction
    from experts import run_all_experts
    from liuyao_v2 import interpret
    
    # 1. Poisson
    try:
        matrix, wp, dp, lp, scores = full_score_matrix(lh, la)
        poisson_dir = "W" if wp > max(dp, lp) else ("L" if lp > max(wp, dp) else "D")
        poisson_conf = max(wp, dp, lp)
    except:
        wp = dp = lp = 33; poisson_dir = "D"; poisson_conf = 40

    # 2. Hercules
    try:
        h = run_prediction(home, away, lh, la)
        pred = h.get("prediction", {})
        h_score = pred.get("final_score", "?")
        h_consensus = pred.get("consensus", "?")
        agents = pred.get("agents_detail", [])
        wv = sum(1 for a in agents if "涓? in str(a.get("verdict","")) or "home" in str(a.get("verdict","")).lower())
        lv = sum(1 for a in agents if "瀹? in str(a.get("verdict","")) or "away" in str(a.get("verdict","")).lower())
        dv = len(agents) - wv - lv
        t = max(len(agents), 1)
        h_wp = round(wv/t*100,1); h_dp = round(dv/t*100,1); h_lp = round(lv/t*100,1)
        hercules_dir = "W" if h_wp > max(h_dp, h_lp) else ("L" if h_lp > max(h_wp, h_dp) else "D")
        hercules_conf = max(h_wp, h_dp, h_lp)
    except:
        h_wp, h_dp, h_lp = wp, dp, lp
        hercules_dir = poisson_dir; hercules_conf = poisson_conf
        h_score = "?"; h_consensus = "?"

    # 3. Experts
    try:
        e = run_all_experts(home, away, lh, la, wp, dp, lp)
        wdl = e.get("win_draw_loss", {})
        e_wp = wdl.get("home_win", wp); e_dp = wdl.get("draw", dp); e_lp = wdl.get("away_win", lp)
        e_pick = wdl.get("pick", "?"); e_conf = wdl.get("confidence", 50)
        experts_dir = "W" if "涓? in str(e_pick) else ("L" if "瀹? in str(e_pick) else "D")
        experts_conf = max(e_wp, e_dp, e_lp)
    except:
        e_wp, e_dp, e_lp = wp, dp, lp
        experts_dir = poisson_dir; experts_conf = poisson_conf; e_pick = "?"

    # 4. Liuyao
    try:
        ly = interpret(home, away, date_str)
        ly_dir_text = ly.get("direction", "?")
        ly_auspice = ly.get("main_auspice", "?")
        ly_name = ly.get("main_name", "?")
        if "涓? in ly_dir_text or "鑳? in ly_dir_text:
            ly_dir = "W"; ly_wp, ly_dp, ly_lp = 55, 25, 20
        elif "瀹? in ly_dir_text or "璐? in ly_dir_text:
            ly_dir = "L"; ly_wp, ly_dp, ly_lp = 20, 25, 55
        else:
            ly_dir = "D"; ly_wp, ly_dp, ly_lp = 30, 40, 30
        ly_conf = 65 if "澶у悏" in ly_auspice else (55 if "鍚? in ly_auspice else (35 if "鍑? in ly_auspice else 45))
    except:
        ly_wp, ly_dp, ly_lp = wp, dp, lp
        ly_dir = poisson_dir; ly_conf = 45; ly_name = "?"; ly_auspice = "?"

    # FUSION
    w = WEIGHTS; tw = sum(w.values())
    fused_wp = round((wp*w["poisson"] + h_wp*w["hercules"] + e_wp*w["experts"] + ly_wp*w["liuyao"])/tw, 1)
    fused_dp = round((dp*w["poisson"] + h_dp*w["hercules"] + e_dp*w["experts"] + ly_dp*w["liuyao"])/tw, 1)
    fused_lp = round((lp*w["poisson"] + h_lp*w["hercules"] + e_lp*w["experts"] + ly_lp*w["liuyao"])/tw, 1)
    
    total = fused_wp + fused_dp + fused_lp
    if total > 0:
        fused_wp = round(fused_wp/total*100, 1)
        fused_dp = round(fused_dp/total*100, 1)
        fused_lp = round(fused_lp/total*100, 1)
    
    if fused_wp > max(fused_dp, fused_lp):
        fused_dir = "W"; fused_label = "涓昏儨"
    elif fused_lp > max(fused_wp, fused_dp):
        fused_dir = "L"; fused_label = "瀹㈣儨"
    else:
        fused_dir = "D"; fused_label = "骞冲眬"
    
    dirs = [poisson_dir, hercules_dir, experts_dir, ly_dir]
    agree_count = max(dirs.count(d) for d in set(dirs))
    agreement_pct = round(agree_count/4*100)
    if agree_count == 4:
        agreement = "楂樺害涓€鑷?
    elif agree_count >= 3:
        agreement = "澶氭暟涓€鑷?
    elif agree_count == 2:
        agreement = "鍒嗘"
    else:
        agreement = "楂樺害鍒嗘"
    
    confidences = [poisson_conf, hercules_conf, experts_conf, ly_conf]
    avg_conf = round(sum(confidences)/len(confidences), 1)
    risk = "浣? if avg_conf >= 65 else ("涓? if avg_conf >= 45 else "楂?)
    
    return {
        "home": home, "away": away,
        "win": fused_wp, "draw": fused_dp, "lose": fused_lp,
        "direction": fused_label, "dir_code": fused_dir,
        "confidence": avg_conf, "risk": risk,
        "agreement": agreement, "agreement_pct": agreement_pct,
        "sources": {
            "poisson": {"name": "娉婃澗璐濆彾鏂?, "weight": w["poisson"], "win": wp, "draw": dp, "lose": lp, "direction": "涓昏儨" if poisson_dir=="W" else ("瀹㈣儨" if poisson_dir=="L" else "骞冲眬"), "confidence": round(poisson_conf, 1)},
            "hercules": {"name": "澶у姏绁炵畻", "weight": w["hercules"], "win": h_wp, "draw": h_dp, "lose": h_lp, "direction": "涓昏儨" if hercules_dir=="W" else ("瀹㈣儨" if hercules_dir=="L" else "骞冲眬"), "confidence": round(hercules_conf, 1), "consensus": h_consensus, "score": h_score},
            "experts": {"name": "涓撳绯荤粺", "weight": w["experts"], "win": e_wp, "draw": e_dp, "lose": e_lp, "direction": "涓昏儨" if experts_dir=="W" else ("瀹㈣儨" if experts_dir=="L" else "骞冲眬"), "confidence": round(experts_conf, 1), "pick": e_pick},
            "liuyao": {"name": "鍏埢", "weight": w["liuyao"], "win": ly_wp, "draw": ly_dp, "lose": ly_lp, "direction": "涓昏儨" if ly_dir=="W" else ("瀹㈣儨" if ly_dir=="L" else "骞冲眬"), "confidence": round(ly_conf, 1), "hexagram": ly_name, "auspice": ly_auspice}
        },
        "recommended_play": _recommend(fused_wp, fused_dp, fused_lp, avg_conf)
    }

def _recommend(wp, dp, lp, conf):
    max_p = max(wp, dp, lp)
    spread = max_p - min(wp, dp, lp)
    if max_p >= 55 and spread >= 20:
        return {"play": "鑳滃钩璐?, "reason": f"鏂瑰悜鏄庣‘锛屾鐜囧樊{spread:.0f}%", "confidence": "楂? if conf >= 60 else "涓?}
    elif max_p >= 45 and spread >= 10:
        return {"play": "鎬昏繘鐞?, "reason": "鏈夊€惧悜浣嗘湁鍙樻暟锛屾€昏繘鐞冮檷浣庨闄?, "confidence": "涓?}
    elif spread < 15:
        return {"play": "鍗婂叏鍦?, "reason": "鍙屾柟鎺ヨ繎锛屽崐鍏ㄥ満鏇寸伒娲?, "confidence": "涓?}
    else:
        return {"play": "鑳滃钩璐?, "reason": "缁煎悎鍒嗘瀽寤鸿鑳滃钩璐?, "confidence": "浣?}

def fuse_all_matches(matches):
    results = []
    for m in matches:
        try:
            r = fuse_prediction(m.get("home","?"), m.get("away","?"), m.get("lh",1.5), m.get("la",1.5), m.get("date",""))
            r["time"] = m.get("time","")
            r["lg"] = m.get("lg","")
            results.append(r)
        except Exception as e:
            results.append({"error": str(e), "home": m.get("home"), "away": m.get("away")})
    return results