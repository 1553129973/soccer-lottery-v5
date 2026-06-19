import sys, os, json, math, random, time
from datetime import datetime
from flask import Flask, jsonify, request
app = Flask(__name__)

from hercules import run_prediction
from experts import run_all_experts
from features import get_all_features, PostMatchAnalysis, roi_tracker
from fetcher import fetch_all, start_scheduler
from poisson_bayes import full_score_matrix, total_goals_distribution, poisson_pmf, poisson as poisson_v2
from team_names import translate, TEAM_NAMES
from liuyao_v2 import interpret as liuyao_interpret, generate_hexagram, HEXAGRAMS
from knowledge_loader import kb, enhance_match_analysis
from auto_analyst import analyst
from news_center import get_news_feed, fetch_news
from titan007 import titan
from betting_strategy import play_type_analysis, parlay_combinations, generate_full_betting_plan, when_to_use_which_play
from self_learner import learner
from fusion import fuse_all_matches

def poisson(k, lam):
    if k < 0 or lam <= 0: return 0
    return __import__('math').exp(-lam) * (lam**k) / __import__('math').factorial(k)

MATCHES = None  # Will be loaded from fetcher on startup

def load_matches():
    global MATCHES
    from datetime import datetime as _dt, timedelta as _td
    target_date = (_dt.now() + _td(days=1)).strftime("%Y-%m-%d")
    print("\n[App] 鐩爣鏃ユ湡: " + target_date + " (鏄庡ぉ)")
    print("[App] 姝ｅ湪鑾峰彇瀹炴椂姣旇禌鏁版嵁...")
    
    # Step 1: Try live fetch
    try:
        live = fetch_all(use_cache=False)
        if live:
            for m in live:
                if not m.get("date"):
                    m["date"] = target_date
            live.sort(key=lambda x: x.get("time", "23:59"))
            MATCHES = live[:4]
            print("[App] 浣跨敤瀹炴椂鏁版嵁: " + str(len(MATCHES)) + " 鍦烘瘮璧?(" + target_date + ")")
            for m in MATCHES:
                print("  " + m["time"] + " " + m["home"] + " vs " + m["away"])
            return
    except Exception as e:
        print("[App] 瀹炴椂鎶撳彇澶辫触: " + str(e))
    
    # Step 2: Try cache
    try:
        cache_file = os.path.join(os.path.dirname(__file__), "live_matches.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as _f:
                cached = json.load(_f)
            cached_matches = cached.get("matches", [])
            if cached_matches:
                for m in cached_matches:
                    if not m.get("date"):
                        m["date"] = target_date
                cached_matches.sort(key=lambda x: x.get("time", "23:59"))
                MATCHES = cached_matches[:4]
                print("[App] 浣跨敤缂撳瓨鏁版嵁: " + str(len(MATCHES)) + " 鍦烘瘮璧?(" + target_date + ")")
                return
    except Exception as e:
        print("[App] 缂撳瓨璇诲彇澶辫触: " + str(e))
    
    # Step 3: Hardcoded fallback
    MATCHES = [
        {"home":"鎹峰厠","away":"鍗楅潪","time":"00:00","date":target_date,"lg":"涓栫晫鏉疕缁?,"lh":1.88,"la":1.56,"fh":"2鑳?骞?璐?,"fa":"3鑳?骞?璐?,"h2h":"棣栨浜ら攱","mot":4,"source":"fallback"},
        {"home":"鐟炲＋","away":"娉㈤粦","time":"03:00","date":target_date,"lg":"涓栫晫鏉疓缁?,"lh":2.20,"la":1.20,"fh":"4鑳?骞?璐?,"fa":"1鑳?骞?璐?,"h2h":"鐟炲＋1鑳?骞?,"mot":5,"source":"fallback"},
        {"home":"鍔犳嬁澶?,"away":"鍗″灏?,"time":"06:00","date":target_date,"lg":"涓栫晫鏉疐缁?,"lh":1.65,"la":1.10,"fh":"2鑳?骞?璐?,"fa":"0鑳?骞?璐?,"h2h":"棣栨浜ら攱","mot":4,"source":"fallback"},
        {"home":"澧ㄨタ鍝?,"away":"闊╁浗","time":"09:00","date":target_date,"lg":"涓栫晫鏉疉缁?,"lh":1.72,"la":1.30,"fh":"3鑳?骞?璐?,"fa":"2鑳?骞?璐?,"h2h":"闊╁浗1鑳?骞?,"mot":5,"source":"fallback"},
    ]
    print("[App] 浣跨敤鍏滃簳鏁版嵁: " + str(len(MATCHES)) + " 鍦烘瘮璧?(" + target_date + ")")

EXP = {
    "鎹峰厠":{"t":"涓父鐞冮槦","c":"鍝堣阿鍏?,"g":"H缁?,"f":"FIFA#35","n":"缁嶅垏鍏嬮琛斾笢娆ч搧楠?},
    "鍗楅潪":{"t":"涓嬫父/鏂板啗","c":"甯冪綏鏂?,"g":"H缁?,"f":"FIFA#55","n":"闈炴床鏂板娍鍔?閫熷害鍨嬪弽鍑?},
    "鐟炲＋":{"t":"浜屾。寮洪槦","c":"闆呴噾","g":"G缁?,"f":"FIFA#16","n":"闃插畧缁勭粐涓€娴?澶ц禌缁忛獙涓板瘜"},
    "娉㈤粦":{"t":"涓嬫父/鏂板啗","c":"宸村反闆疯尐","g":"G缁?,"f":"FIFA#60","n":"鍝茬鏃朵唬鍚庨噸寤烘湡"},
    "鍔犳嬁澶?:{"t":"涓父鐞冮槦","c":"椹粈","g":"F缁?,"f":"FIFA#28","n":"2026涓滈亾涓?鎴寸淮鏂?澶у崼鍙屾牳"},
    "鍗″灏?:{"t":"涓嬫父/鏂板啗","c":"妗戝垏鏂?,"g":"F缁?,"f":"FIFA#45","n":"2022涓栫晫鏉粡楠?浜氭床鏉啝鍐?},
    "澧ㄨタ鍝?:{"t":"浜屾。寮洪槦","c":"闃垮悏闆?,"g":"A缁?,"f":"FIFA#15","n":"2026涓滈亾涓?16寮轰笓涓氭埛"},
    "闊╁浗":{"t":"涓父鐞冮槦","c":"鍏嬫灄鏂浖","g":"A缁?,"f":"FIFA#22","n":"瀛欏叴鎱?鏉庡垰浠?蹇€熷弽鍑?},
}

HEX = {
    "111111":("涔句负澶?,"澶у悏路鍒氬仴鏈夊姏",5),"000000":("鍧や负鍦?,"骞崇ǔ路鍘氬痉杞界墿",3),
    "010001":("姘撮浄灞?,"鑹伴毦路涓囦簨寮€澶撮毦",2),"100010":("灞辨按钂?,"鏈﹁儳路褰㈠娍涓嶆槑",2),
    "010111":("姘村ぉ闇€","绛夊緟路鏃舵満鏈埌",2),"111010":("澶╂按璁?,"浜夎路鎴栨湁VAR",2),
    "000111":("鍦板ぉ娉?,"浜ㄩ€毬峰ぉ鍦颁氦娉?,5),"111000":("澶╁湴鍚?,"闂路浜嬩笌鎰胯繚",1),
    "111101":("澶╃伀鍚屼汉","鍚屽績路鍥㈤槦鍗忎綔",4),"101111":("鐏ぉ澶ф湁","涓版敹路澶ц幏鍏ㄨ儨",5),
    "001000":("闆峰湴璞?,"鎰夋偊路杞绘澗鍙栬儨",4),"011001":("娉介浄闅?,"闅忛『路椤哄娍鑰屼负",3),
    "000100":("鍦板北璋?,"璋﹁櫄路浣庤皟鍙栬儨",4),"001110":("闆烽鎭?,"鎭掍箙路绋冲畾鍙戞尌",4),
}

def analyze_poisson(home, away, lh, la, lg, time_str, fh, fa, h2h, mot):
    '''Use poisson_bayes module for full analysis'''
    matrix, win_p, draw_p, lose_p, all_scores = full_score_matrix(lh, la)
    tg_dist = total_goals_distribution(lh, la)
    
    # Convert total goals to list format
    tg = [{"g": str(k), "p": round(v, 2)} for k, v in tg_dist.items() if v > 0.01]
    tg.sort(key=lambda x: -x["p"])
    
    # Half/full time
    hh, ha = lh * 0.44, la * 0.44
    def hp(hl, al):
        m2, w2, d2, l2, _ = full_score_matrix(hl, al, 5)
        t = w2 + d2 + l2
        return {"W": max(0.05, w2/t), "D": max(0.05, d2/t), "L": max(0.05, l2/t)} if t > 0 else {"W": 0.4, "D": 0.3, "L": 0.3}
    half = hp(hh, ha)
    full = hp(lh, la)
    combo = [("鑳滆儨","W","W"),("鑳滃钩","W","D"),("鑳滆礋","W","L"),
             ("骞宠儨","D","W"),("骞冲钩","D","D"),("骞宠礋","D","L"),
             ("璐熻儨","L","W"),("璐熷钩","L","D"),("璐熻礋","L","L")]
    hf = [{"r": n, "p": round(half[hk] * full[fk] * 100, 2)} for n, hk, fk in combo]
    hf.sort(key=lambda x: -x["p"])
    
    # Scores list
    scores = [{"s": f'{s["home"]}-{s["away"]}', "p": s["prob"]} for s in all_scores[:36]]
    
    # Direction
    if win_p > lose_p + 5:
        dire, conf = "涓昏儨", min(85, int(win_p))
    elif lose_p > win_p + 5:
        dire, conf = "瀹㈣儨", min(85, int(lose_p))
    else:
        dire, conf = "骞冲眬", min(85, int(draw_p))
    
    # Handicap
    hcp = f"涓粄-round(min(0.75,(lh-la)*0.4),2)}" if lh > la else "涓?0.25"
    cov = win_p/100 if lh > la else lose_p/100
    
    # Verdict
    if win_p > 60:
        vd = f"銆愯緝绋炽€憑home}瀹炲姏鍗犱紭锛屼富鑳滃ぇ姒傜巼"
    elif win_p > 48:
        vd = f"銆愬€惧悜銆憑home}鐣ュ崰浼橈紝闇€闃插钩灞€"
    elif lose_p > 60:
        vd = f"銆愯緝绋炽€憑away}瀹炲姏鍗犱紭锛屽鑳滄鐜囬珮"
    elif lose_p > 48:
        vd = f"銆愬€惧悜銆憑away}鐣ュ崰浼橈紝瀹㈠満瀛樺彉鏁?
    else:
        vd = "銆愪笉纭畾銆戝弻鏂瑰疄鍔涙帴杩戯紝寤鸿瑙傛湜"
    try:
        from knowledge_loader import enhance_match_analysis
        kb_e = enhance_match_analysis(home, away, conf, dire)
        if kb_e.get("adjustment", 0) != 0:
            adj = kb_e["adjustment"]
            conf = min(100, max(0, conf + adj))
            vd += f"锛岀煡璇嗗簱{adj:+d}%" if adj != 0 else ""
    except:
        pass
    
    # Team info from skill data
    team_tiers = {
        "鑽峰叞": ("浜屾。寮洪槦", "绉戞浖", "FIFA#10", "鑼冩埓鍏嬮琛斿叏鏀诲叏瀹?),
        "鐟炲吀": ("涓父鐞冮槦", "鎵橀┈妫?, "FIFA#27", "鍖楁鍔叉梾"),
        "缇庡浗": ("涓父鐞冮槦(涓滈亾涓?", "璐濆皵鍝堢壒", "FIFA#16", "2026涓滈亾涓?澶氱偣鎻愰€熷帇杩?鏅埄甯屽+缁撮樋,棣栬疆4:1澶ц儨"),
        "婢冲ぇ鍒╀簹": ("涓父鐞冮槦", "闃胯寰?, "FIFA#29", "闃插畧鍙嶅嚮+瀹氫綅鐞?浼婂叞鏄嗚揪閫熷害,棣栬疆璧㈠湡鑰冲叾"),
        "寰峰浗": ("涓€妗ｅ己闃?, "绾虫牸灏旀柉鏇?, "FIFA#3", "涓栫晫鏉?鍐犵帇"),
        "绉戠壒杩摝": ("涓嬫父/鏂板啗", "绂忛浄", "FIFA#50", "闈炴床闆勭嫯"),
        "鍔犳嬁澶?: ("涓父鐞冮槦", "椹粈", "FIFA#28", "2026涓滈亾涓?鎴寸淮鏂?澶у崼鍙屾牳,楂樿妭濂忓啿鍑?杈硅矾濞佽儊澶?),
        "鍗″灏?: ("涓嬫父/鏂板啗", "妗戝垏鏂?, "FIFA#45", "2022涓栫晫鏉粡楠?浜氭床鏉啝鍐?),
        "鑻忔牸鍏?: ("涓父鐞冮槦", "鍏嬫媺鍏?, "FIFA#30", "鐩存帴鍘嬭揩鍨?缃椾集閫?楹﹂噾宸﹁矾,瀹氫綅鐞冨▉鑳佸ぇ,棣栬疆璧㈡捣鍦?),
        "鎽╂礇鍝?: ("涓笂娓哥悆闃?, "闆锋牸鎷夊悏", "FIFA#13", "2022涓栫晫鏉洓寮?鏀诲畧杞崲鎴愮啛,闃夸粈鎷夊か+甯冮樋杩?棣栬疆閫煎钩宸磋タ"),
        "鍘勭摐澶氬皵": ("涓父鐞冮槦", "妗戝垏鏂峰反鏂?, "FIFA#31", "鍗楃編楂樺師涔嬮拱"),
        "搴撴媺绱?: ("涓嬫父/鏂板啗", "甯屼竵鍏?, "FIFA#80", "鍔犲嫆姣斿皬鍥?),
        "宸磋タ": ("涓€妗ｅ己闃?, "澶氶噷鐡﹀皵", "FIFA#2", "5鍐犵帇,瓒崇悆鐜嬪浗"),
        "娴峰湴": ("涓嬫父/鏂板啗", "鐨焹灏?, "FIFA#85", "涓寳缇庢柊鍔垮姏"),
        "澧ㄨタ鍝?: ("浜屾。寮洪槦", "闃垮悏闆?, "FIFA#15", "2026涓滈亾涓?16寮轰笓涓氭埛,鏈夎妭濂忔湁鎶€鏈?涓诲満娴锋嫈浼樺娍"),
        "闊╁浗": ("涓父鐞冮槦", "鍏嬫灄鏂浖", "FIFA#22", "瀛欏叴鎱?鏉庡垰浠?蹇€熷弽鍑?棣栬疆閫嗚浆澹皵楂?浣撹兘鍙楁捣鎷旇€冮獙"),
        "鍦熻€冲叾": ("涓父鐞冮槦", "钂欑壒鎷?, "FIFA#23", "娆ф床榛戦┈"),
        "宸存媺鍦?: ("涓嬫父/鏂板啗", "璋㈡礇鎵?, "FIFA#52", "鍗楃編闃插畧鍙嶅嚮"),
        "绐佸凹鏂?: ("涓父鐞冮槦", "鍗″痉閲?, "FIFA#33", "鍖楅潪鍔叉梾"),
        "鏃ユ湰": ("浜屾。寮洪槦", "妫繚涓€", "FIFA#11", "鎶€鏈祦浜氭床涔嬪厜"),
        "鎹峰厠": ("涓父鐞冮槦", "鍝堣阿鍏?, "FIFA#24", "涓満楂樺害浼樺娍,棣栬疆琚€嗚浆鎬ラ渶鍙嶅脊"),
        "鍗楅潪": ("涓嬫父/鏂板啗", "甯冪綏鏂?, "FIFA#55", "閫熷害鍙嶅嚮鍨?绾緥濂戒换鍔℃槑纭?),
        "鐟炲＋": ("浜屾。寮洪槦", "闆呴噾", "FIFA#19", "鏁翠綋绋冲畾鎬у己,闃垮潕鍚?鎵庡崱鏍稿績,棣栬疆涓㈠垎涓嶅彲鍐嶄繚瀹?),
        "娉㈤粦": ("涓嬫父/鏂板啗", "宸村反闆疯尐", "FIFA#46", "闊ф€у己棣栬疆閫煎钩鍔犳嬁澶?闃插畧瀵嗛泦"),
        "鎸▉": ("浜屾。寮洪槦", "绱㈠皵宸磋偗", "FIFA#18", "鍝堝叞寰?鍘勫痉楂樺弻鏍稿績,鎬昏韩浠风害5浜挎"),
        "浼婃媺鍏?: ("涓嬫父/鏂板啗", "鍗¤惃鏂?, "FIFA#58", "浣庝綅闃插畧鍙嶅嚮,鎬昏韩浠风害0.22浜挎"),
    }
    # Translate team names if they are in English
    home_cn = translate(home) if home else "?"
    away_cn = translate(away) if away else "?"
    he = team_tiers.get(home_cn, team_tiers.get(home, ("涓父鐞冮槦", "?", "FIFA#?", "")))
    ae = team_tiers.get(away_cn, team_tiers.get(away, ("涓父鐞冮槦", "?", "FIFA#?", "")))
    
    # I-Ching
    import random, time
    seed = sum(ord(c) for c in home + away) + int(time.time()) % 100
    rr = random.Random(seed)
    lines = [str(rr.randint(0, 1)) for _ in range(6)]
    code = "".join(lines)
    hex_map = {
        "111111": ("涔句负澶?, "澶у悏路鍒氬仴鏈夊姏", 5), "000000": ("鍧や负鍦?, "骞崇ǔ路鍘氬痉杞界墿", 3),
        "010001": ("姘撮浄灞?, "鑹伴毦路涓囦簨寮€澶撮毦", 2), "100010": ("灞辨按钂?, "鏈﹁儳路褰㈠娍涓嶆槑", 2),
        "000111": ("鍦板ぉ娉?, "浜ㄩ€毬峰ぉ鍦颁氦娉?, 5), "111000": ("澶╁湴鍚?, "闂路浜嬩笌鎰胯繚", 1),
        "111101": ("澶╃伀鍚屼汉", "鍚屽績路鍥㈤槦鍗忎綔", 4), "101111": ("鐏ぉ澶ф湁", "涓版敹路澶ц幏鍏ㄨ儨", 5),
    }
    hx = hex_map.get(code, ("鍙樺崷", "褰㈠娍澶嶆潅", 3))
    
    return {
        "home": home, "away": away, "time": time_str, "lg": lg,
        "hw": round(win_p, 1), "d_": round(draw_p, 1), "aw": round(lose_p, 1),
        "conf": conf, "dire": dire, "verdict": vd,
        "hcp": hcp, "cov": round(cov, 2), "push": 0.1, "fail": round(1 - cov - 0.1, 2),
        "scores": scores, "tg": tg, "hf": hf,
        "hex": {"name": hx[0], "reading": hx[1], "level": hx[2]},
        "hexp": {"t": he[0], "c": he[1], "f": he[2], "n": he[3]},
        "aexp": {"t": ae[0], "c": ae[1], "f": ae[2], "n": ae[3]},
        "ods": {}, "ur": 2 if conf > 55 else (1 if conf > 70 else 3),
        "fh": fh, "fa": fa, "h2h": h2h, "mot": mot,
        "lh": lh, "la": la,
    }

def analyze(m):
    """Wrapper that normalizes analyze_poisson output for gen_plans compatibility"""
    a = analyze_poisson(
        translate(m.get("home", "?")), translate(m.get("away", "?")),
        m.get("lh", 1.5), m.get("la", 1.5),
        m.get("lg", "?"), m.get("time", "?"),
        m.get("fh", "?"), m.get("fa", "?"),
        m.get("h2h", "?"), m.get("mot", 3)
    )
    # Pass through date
    a["date"] = m.get("date", "")
    # Generate form data if missing (live data may not have it)
    if a.get("fh", "?") == "?":
        import random as _rg
        sh = sum(ord(c) for c in a["home"]) % 100
        rg = _rg.Random(sh)
        n = rg.randint(2, 5)
        a["fh"] = f"{n}鑳渰rg.randint(0,3)}骞硔rg.randint(0,3)}璐?
    if a.get("fa", "?") == "?":
        import random as _rg2
        sa = sum(ord(c) for c in a["away"]) % 100
        rg2 = _rg2.Random(sa)
        n2 = rg2.randint(1, 5)
        a["fa"] = f"{n2}鑳渰rg2.randint(0,3)}骞硔rg2.randint(0,3)}璐?
    if a.get("h2h", "?") == "?" or a.get("h2h", "") == "":
        a["h2h"] = "鏆傛棤浜ら攱璁板綍"
    a["source"] = m.get("source", "live")
    # Normalize fields for gen_plans compatibility
    a["ht"] = a["home"]
    a["at"] = a["away"]
    a["tm"] = a.get("time", "?")
    a["cf"] = a.get("conf", 50)
    a["dir"] = a.get("dire", "?")
    a["pm"] = {"w": a.get("hw", 33), "d": a.get("d_", 34), "l": a.get("aw", 33)}
    a["ods"] = {
        "w": round(1/max(a.get("hw",33)/100, 0.01)*0.9, 2),
        "d": round(1/max(a.get("d_",34)/100, 0.01)*0.9, 2),
        "l": round(1/max(a.get("aw",33)/100, 0.01)*0.9, 2)
    }
    a["sm"] = [{"s": s["s"], "p": s["p"], "h": int(s["s"].split("-")[0]), "a": int(s["s"].split("-")[1])} for s in a.get("scores", [])]
    a["lam"] = {"h": a.get("lh", 1.5), "a": a.get("la", 1.5)}
    a["hcp_p"] = {"cov": a.get("cov", 0.5), "push": a.get("push", 0.1), "fail": a.get("fail", 0.4)}
    a["bs"] = min(95, a.get("conf", 50) + 5)
    a["expert"] = {"vd": a.get("verdict",""), "tg": "{} vs {}".format(a.get("hexp",{}).get("t","?"), a.get("aexp",{}).get("t","?")), "xf": "", "rel": "涓?}
    # Upset risk level (1=very safe, 5=high upset risk)
    conf_val = a.get("conf", 50)
    a["ur"] = 1 if conf_val >= 70 else (2 if conf_val >= 55 else (3 if conf_val >= 40 else (4 if conf_val >= 25 else 5)))
    a["source"] = m.get("source", "live")
    a["ly"] = {"nm": a.get("hex",{}).get("name",""), "ip": a.get("hex",{}).get("reading",""), "lk": "猸? * a.get("hex",{}).get("level",3), "sp": "1-1", "sr": "1-1~2-2","tg": "2鐞?, "hf": a.get("dire","?"), "ls": ["鉀?] * 6}
    return a

def gen_plans(matches):
    analyzed=[analyze(m) for m in matches];singles=[]
    for a in analyzed:
        for pn,pk,ok in [("涓昏儨","w","w"),("骞冲眬","d","d"),("瀹㈣儨","l","l")]:
            prob=a["pm"][pk]/100;odds=a["ods"][ok];cf=a["cf"] if pk=="w" else (100-a["cf"] if pk=="l" else 30)
            if prob>0.005:singles.append({"m":f"{a['ht']} vs {a['at']}","pick":pn,"prob":round(prob,3),"odds":odds,"cf":cf,"ur":a["ur"],"md":a})
    singles.sort(key=lambda x:-x["prob"])
    pairs=[]
    for i in range(len(singles)):
        for j in range(i+1,len(singles)):
            if singles[i]["m"]!=singles[j]["m"]:pairs.append({"ms":[singles[i],singles[j]],"prob":round(singles[i]["prob"]*singles[j]["prob"],4),"odds":round(singles[i]["odds"]*singles[j]["odds"],2)})
    pairs.sort(key=lambda x:-x["prob"]);pairs=pairs[:12]
    triples=[]
    for p in pairs[:10]:
        pms=[s["m"] for s in p["ms"]]
        for s in singles:
            if s["m"] not in pms:triples.append({"ms":p["ms"]+[s],"prob":round(p["prob"]*s["prob"],4),"odds":round(p["odds"]*s["odds"],2)})
    triples.sort(key=lambda x:-x["prob"]);triples=triples[:12]
    quads=[]
    for t in triples[:8]:
        tms=[s["m"] for s in t["ms"]]
        for s in singles:
            if s["m"] not in tms:quads.append({"ms":t["ms"]+[s],"prob":round(t["prob"]*s["prob"],4),"odds":round(t["odds"]*s["odds"],2)})
    quads.sort(key=lambda x:-x["prob"]);quads=quads[:8]
    score_p=[];tg_p=[];hf_p=[]
    for a in analyzed:
        for s in a["sm"][:3]:score_p.append({"m":f"{a['ht']} vs {a['at']}","pick":s["s"],"prob":round(s["p"]/100,3),"odds":round(1/max(s["p"]/100,0.01)*0.85,2),"cf":round(s["p"],1)})
        for t in a["tg"][:5]:tg_p.append({"m":f"{a['ht']} vs {a['at']}","pick":f"{t['g']}鐞?,"prob":round(t["p"]/100,3),"odds":round(1/max(t["p"]/100,0.01)*0.85,2),"cf":round(t["p"],1)})
        for h in a["hf"][:3]:hf_p.append({"m":f"{a['ht']} vs {a['at']}","pick":h["r"],"prob":round(h["p"]/100,3),"odds":round(1/max(h["p"]/100,0.01)*0.85,2),"cf":round(h["p"],1)})
    score_p.sort(key=lambda x:-x["prob"]);tg_p.sort(key=lambda x:-x["prob"]);hf_p.sort(key=lambda x:-x["prob"])
    def cls(prob,ur):
        # Distribute across all risk levels
        if prob>0.10 and ur<=2: return "stable"
        if prob>0.05 and ur<=3: return "solid"
        if prob>0.02: return "aggro"
        return "cold"
    plans={"stable":{"name":"绋冲畾绾㈠崟","singles":[],"pairs":[],"triples":[],"quads":[],"mix":[]},"solid":{"name":"绋冲仴鏂规","singles":[],"pairs":[],"triples":[],"quads":[],"mix":[]},"aggro":{"name":"杩涘彇鏂规","singles":[],"pairs":[],"triples":[],"quads":[],"mix":[]},"cold":{"name":"鍗氬喎鏂规","singles":[],"pairs":[],"triples":[],"quads":[],"mix":[]}}
    for s in singles:plans[cls(s["prob"],s["ur"])]["singles"].append(s)
    for p in pairs:
        avg=(p["ms"][0]["ur"]+p["ms"][1]["ur"])/2;plans[cls(p["prob"],avg)]["pairs"].append(p)
    for t in triples:
        avg=sum(m["ur"] for m in t["ms"])/3;plans[cls(t["prob"],avg)]["triples"].append(t)
    for q in quads:
        avg=sum(m["ur"] for m in q["ms"])/4;plans[cls(q["prob"],avg)]["quads"].append(q)
    for rk in plans:
        mp=plans[rk];all_opt=[]
        if mp["singles"]:all_opt.append(("鍗曞叧",mp["singles"][0]["odds"],mp["singles"][0]["prob"]))
        if mp["pairs"]:all_opt.append(("2涓?",mp["pairs"][0]["odds"],mp["pairs"][0]["prob"]))
        if mp["triples"]:all_opt.append(("3涓?",mp["triples"][0]["odds"],mp["triples"][0]["prob"]))
        if mp["quads"]:all_opt.append(("4涓?",mp["quads"][0]["odds"],mp["quads"][0]["prob"]))
        all_opt.sort(key=lambda x:-x[2]);mp["rec"]=f"鎺ㄨ崘{all_opt[0][0]}" if all_opt else "";mp["mix"]=[{"t":o[0],"odds":o[1],"prob":round(o[2]*100,1)} for o in all_opt[:3]]
    return {"singles":singles[:8],"pairs":pairs[:8],"triples":triples[:8],"quads":quads[:6],"plans":{k:{"name":v["name"],"rec":v["rec"],"singles":v["singles"][:3],"pairs":v["pairs"][:3],"triples":v["triples"][:2],"quads":v["quads"][:2],"mix":v["mix"]} for k,v in plans.items()},"score_p":score_p[:12],"tg_p":tg_p[:12],"hf_p":hf_p[:12],"analyzed":analyzed}

# Read the HTML template
TPL = open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'r', encoding='utf-8').read()

@app.route('/diag')
def diag():
    diag_path = os.path.join(os.path.dirname(__file__), 'templates', 'diag.html')
    with open(diag_path, 'r', encoding='utf-8') as _f:
        return _f.read()

@app.route('/')
def index():
    return TPL

@app.route('/api/matches')
def api_m():
    # analyze() now returns correct normalized format directly
    analyzed = [analyze(m) for m in MATCHES]
    match_date = MATCHES[0].get("date", "") if MATCHES else datetime.now().strftime("%Y-%m-%d")
    return jsonify({"matches": analyzed, "date": match_date})

@app.route('/api/plans')
def api_p():
    result = gen_plans(MATCHES)
    result["date"] = MATCHES[0].get("date", "") if MATCHES else datetime.now().strftime("%Y-%m-%d")
    return jsonify(result)

@app.route('/api/multi', methods=['POST'])
def api_multi():
    data = request.get_json(force=True) if request.data else {}
    p = float(data.get("p",100)); tgt = float(data.get("tgt",500)); days = int(data.get("days",7))
    db = round(p/days, 2); plan = []
    for d in range(1, days+1):
        plan.append({"day":d,"budget":db,"bet":round(db*0.4,2),"play":"2涓?" if d<=3 else ("鍗曞叧" if d<=5 else "3涓?"),"note":"绋冲畾绉疮" if d<=3 else ("閫傚害杩涘彇" if d<=5 else "鍐插埡闃舵")})
    return jsonify({"p":p,"tgt":tgt,"days":days,"db":db,"plan":plan})

@app.route('/api/save', methods=['POST'])
def api_save():
    data = request.get_json(force=True) if request.data else {}
    d = os.path.join(os.path.dirname(__file__), 'history')
    os.makedirs(d, exist_ok=True)
    fname = os.path.join(d, f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"ok":True})


@app.route("/api/liuyao")
def api_liuyao():
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if not home or not away:
        if MATCHES and len(MATCHES) > 0:
            home = MATCHES[0].get("home", "?")
            away = MATCHES[0].get("away", "?")
    try:
        result = liuyao_interpret(home, away, datetime.now().strftime("%Y-%m-%d"))
        return jsonify({"home": home, "away": away, "liuyao": result})
    except Exception as e:
        return jsonify({"home": home, "away": away, "error": str(e)})

@app.route("/api/hercules")
def api_hercules():
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    lh = float(request.args.get("lh", 1.5))
    la = float(request.args.get("la", 1.5))
    if not home or not away:
        # Return all matches
        results = []
        for m in MATCHES:
            results.append(run_prediction(m["home"], m["away"], m["lh"], m["la"]))
        return jsonify({"predictions": results})
    result = run_prediction(home, away, lh, la)
    return jsonify(result)



@app.route("/api/experts")
def api_experts():
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    lh = float(request.args.get("lh", 1.5))
    la = float(request.args.get("la", 1.5))
    wp = float(request.args.get("wp", 45))
    dp = float(request.args.get("dp", 25))
    lp = float(request.args.get("lp", 30))
    if not home or not away:
        # Return for first match
        m = MATCHES[0]
        result = run_all_experts(m["home"], m["away"], m["lh"], m["la"], 45, 25, 30)
        return jsonify({"home": m["home"], "away": m["away"], "experts": result})
    result = run_all_experts(home, away, lh, la, wp, dp, lp)
    return jsonify({"home": home, "away": away, "experts": result})



@app.route("/api/features")
def api_features():
    home = request.args.get("home", "鐟炲＋")
    away = request.args.get("away", "娉㈤粦")
    lh = float(request.args.get("lh", 2.2))
    la = float(request.args.get("la", 1.2))
    wp = float(request.args.get("wp", 60))
    dp = float(request.args.get("dp", 20))
    lp = float(request.args.get("lp", 20))
    result = get_all_features(home, away, lh, la, wp, dp, lp)
    return jsonify(result)

@app.route("/api/post_match", methods=["POST"])
def api_post_match():
    data = request.get_json(force=True) if request.data else {}
    home = data.get("home", "")
    away = data.get("away", "")
    pred = data.get("prediction", "0-0")
    actual = data.get("actual", "0-0")
    wp = float(data.get("wp", 45))
    dp = float(data.get("dp", 25))
    lp = float(data.get("lp", 30))
    if not home or not away:
        return jsonify({"error": "need home and away"})
    result = PostMatchAnalysis().analyze(home, away, pred, actual, wp, dp, lp)
    return jsonify(result)

@app.route("/api/roi")
def api_roi():
    return jsonify(roi_tracker.get_stats())

@app.route("/api/roi/add", methods=["POST"])
def api_roi_add():
    data = request.get_json(force=True) if request.data else {}
    record = roi_tracker.add_record(
        data.get("match", ""),
        data.get("prediction", "0-0"),
        data.get("actual", "0-0"),
        float(data.get("odds", 2.0)),
        float(data.get("bet_amount", 10)),
        data.get("bet_type", "鑳滃钩璐?),
    )
    return jsonify(record)


@app.route('/api/refresh')
def api_refresh():
    global MATCHES
    try:
        from fetcher import fetch_all
        live = fetch_all(use_cache=False)
        if live:
            MATCHES = live
            return jsonify({"ok": True, "count": len(live), "source": live[0].get("source", "live") if live else "none"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    return jsonify({"ok": False, "error": "no data"})

@app.route('/api/source')
def api_source():
    return jsonify({
        "matches_count": len(MATCHES) if MATCHES else 0,
        "source": MATCHES[0].get("source", "fallback") if MATCHES else "none",
        "fetched_at": "cache" if os.path.exists(os.path.join(os.path.dirname(__file__), 'live_matches.json')) else "hardcoded"
    })

@app.route("/api/time_analysis")
def api_time_analysis():
    """鏃舵鍒嗘瀽锛氭棭鍦?涓満/鏅氬満鍐烽棬鐜囩粺璁?""
    seg_names = {
        (0, 4): "鏃╁満(00-04)",
        (4, 8): "涓満(04-08)",
        (8, 24): "鏅氬満(08-12)"
    }
    segments = {name: [] for name in seg_names.values()}
    for m in MATCHES:
        t = m.get("time", "23:59")
        hour = int(t.split(":")[0]) if ":" in t else 23
        for (lo, hi), name in seg_names.items():
            if lo <= hour < hi:
                segments[name].append(m)
                break
    
    result = {}
    for seg_name, seg_matches in segments.items():
        if not seg_matches:
            result[seg_name] = {"count": 0, "avg_confidence": 0, "upset_risk": "鏃犳暟鎹?, "matches": [], "high_risk_count": 0}
            continue
        analyzed = [analyze(m) for m in seg_matches]
        avg_conf = sum(a.get("conf", 50) for a in analyzed) / len(analyzed)
        high_risk = sum(1 for a in analyzed if a.get("ur", 3) >= 4)
        upset_risk = "楂? if high_risk > len(analyzed)/2 else ("涓? if high_risk > 0 else "浣?)
        result[seg_name] = {
            "count": len(seg_matches),
            "avg_confidence": round(avg_conf, 1),
            "upset_risk": upset_risk,
            "high_risk_count": high_risk,
            "matches": [{"home": a["home"], "away": a["away"], "time": a["time"], "conf": a["conf"], "ur": a["ur"], "dire": a["dire"]} for a in analyzed]
        }
    return jsonify(result)

@app.route("/api/learn/stats")
def api_learn_stats():
    """Get self-learning statistics"""
    return jsonify(learner.get_stats())

@app.route("/api/learn/review", methods=["POST"])
def api_learn_review():
    """Submit match result for learning"""
    data = request.get_json(force=True) if request.data else {}
    home = data.get("home", "")
    away = data.get("away", "")
    actual_score = data.get("actual_score", "")
    if not home or not away or not actual_score:
        return jsonify({"error": "??home, away, actual_score??"})
    result = learner.review_result(home, away, actual_score)
    return jsonify(result)

@app.route("/api/learn/history")
def api_learn_history():
    """Get prediction history"""
    limit = int(request.args.get("limit", 20))
    history = learner.history[-limit:]
    return jsonify({"history": history, "total": len(learner.history)})

@app.route("/api/fusion")
def api_fusion():
    """??????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if home and away:
        # Single match
        lh = float(request.args.get("lh", 1.5))
        la = float(request.args.get("la", 1.5))
        date_str = request.args.get("date", "")
        if not date_str and MATCHES:
            date_str = MATCHES[0].get("date", "")
        from fusion import fuse_prediction
        result = fuse_prediction(home, away, lh, la, date_str)
        return jsonify(result)
    # All matches
    if not MATCHES:
        return jsonify({"error": "no matches", "results": []})
    results = fuse_all_matches(MATCHES)
    return jsonify({"results": results, "date": MATCHES[0].get("date", "") if MATCHES else ""})

@app.route('/api/news')
def api_news():
    """鏂伴椈涓績"""
    return jsonify(get_news_feed())

@app.route('/api/news/refresh')
def api_news_refresh():
    """鍒锋柊鏂伴椈"""
    items = fetch_news()
    return jsonify({"count": len(items), "items": items})

@app.route('/api/titan007')
def api_titan():
    """titan007瀹屾暣鏁版嵁锛氳禂鐜?鐞冮槦+浜ら攱+绉垎姒?""
    from flask import request
    home = request.args.get('home', '')
    away = request.args.get('away', '')
    if home and away:
        return jsonify(titan.get_full_match_data(home, away))
    return jsonify({
        "odds": titan.fetch_odds(),
        "standings": titan.fetch_standings()
    })

@app.route('/api/titan007/team/<team>')
def api_titan_team(team):
    """鐞冮槦璇︾粏鏁版嵁"""
    return jsonify(titan.fetch_team_stats(team))

@app.route('/api/titan007/h2h')
def api_titan_h2h():
    """鍘嗗彶浜ら攱"""
    home = request.args.get('home', '')
    away = request.args.get('away', '')
    return jsonify(titan.fetch_h2h(home, away) if home and away else {"error": "闇€瑕乭ome鍜宎way鍙傛暟"})

@app.route('/api/titan007/standings')
def api_titan_standings():
    """绉垎姒?""
    group = request.args.get('group', '')
    return jsonify(titan.fetch_standings(group))

@app.route('/api/auto_analysis')
def api_auto():
    """鑷姩鍒嗘瀽甯?""
    analyzed = [analyze(m) for m in MATCHES]
    report = analyst.get_daily_report([{
        "home": a["home"], "away": a["away"],
        "time": a.get("time",""), "lg": a.get("lg",""),
        "hw": a.get("hw",0), "d_": a.get("d_",0), "aw": a.get("aw",0)
    } for a in analyzed])
    return jsonify(report)

@app.route('/api/auto_learn', methods=['POST'])
def api_auto_learn():
    """璧涘悗瀛︿範"""
    data = request.get_json(force=True) if request.data else {}
    result = analyst.learn_from_result(
        data.get("home",""), data.get("away",""),
        data.get("predicted",""), data.get("actual",""),
        data.get("score","0-0")
    )
    return jsonify(result)

# Auto-load on import (for gunicorn on Railway/Render)
load_matches()
start_scheduler(refresh_hour=14)

if __name__ == '__main__':
    print("="*50)
    print("  瓒冲僵鍒嗘瀽鍔╂墜 V5")
    print("  http://127.0.0.1:5000")
    print("="*50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)

