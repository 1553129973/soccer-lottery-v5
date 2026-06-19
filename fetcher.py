# -*- coding: utf-8 -*-
"""瀹炴椂鏁版嵁鎶撳彇妯″潡 - 璧涚▼ + 璧旂巼"""
import json, os, time, math, random, re
from datetime import datetime, timedelta
import threading
import urllib.request

# Try to import requests - fall back to urllib if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(DATA_DIR, "live_data.json")
MATCHES_FILE = os.path.join(DATA_DIR, "live_matches.json")

# ============ HTTP Helper ============
def http_get(url, headers=None, timeout=10):
    """HTTP GET with fallback"""
    # Disable any system proxy for direct connections
    import os
    for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy','REQUESTS_CA_BUNDLE']:
        os.environ.pop(k, None)
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.sporttery.cn/",
    }
    if headers:
        default_headers.update(headers)
    
    if HAS_REQUESTS:
        try:
            resp = requests.get(url, headers=default_headers, timeout=timeout, proxies={'http':None,'https':None})
            resp.encoding = 'utf-8'
            return resp.text
        except Exception as e:
            print(f"  [requests error] {e}")
            return None
    else:
        try:
            req = urllib.request.Request(url, headers=default_headers)
            with urllib.request.urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            print(f"  [urllib error] {e}")
            return None

# ============ Sporttery.cn API ============
def fetch_sporttery_matches(date_str=None):
    """浠庝腑鍥界珵褰╃綉鎶撳彇姣旇禌鏁版嵁"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"[Fetcher] 鎶撳彇绔炲僵缃戞暟鎹? {date_str}")
    
    # sporttery.cn internal API for match list
    # Try multiple known endpoints
    urls = [
        f"https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry?matchBeginDate={date_str}&matchEndDate={date_str}&leagueId=&pageSize=100&pageNo=1&isFix=0&matchPage=1",
        f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchHeadV1.qry?matchBeginDate={date_str}&matchEndDate={date_str}&leagueId=&pageSize=100&pageNo=1",
        f"https://webapi.sporttery.cn/gateway/jc/football/getMatchCalculatorV1.qry?matchBeginDate={date_str}&matchEndDate={date_str}&leagueId=&pageSize=100&pageNo=1",
    ]
    
    for url in urls:
        text = http_get(url, timeout=15)
        if text:
            try:
                data = json.loads(text)
                if data.get("success") or data.get("errorCode") == "0" or "value" in data:
                    print(f"  [OK] sporttery.cn 杩斿洖鏁版嵁")
                    return parse_sporttery_data(data, date_str)
            except json.JSONDecodeError:
                continue
        print(f"  [fail] {url[:80]}...")
    
    print("  [WARN] sporttery.cn API 鍏ㄩ儴澶辫触")
    return None

def parse_sporttery_data(data, date_str):
    """瑙ｆ瀽sporttery.cn杩斿洖鐨勬瘮璧涙暟鎹?""
    matches = []
    value = data.get("value", data)
    
    if isinstance(value, dict):
        items = value.get("matchResultList", value.get("matchList", value.get("list", [])))
    elif isinstance(value, list):
        items = value
    else:
        items = []
    
    if not items:
        print("  [WARN] 鏈壘鍒版瘮璧涘垪琛?)
        return None
    
    for item in items:
        try:
            home = item.get("homeTeam", item.get("homeTeamName", item.get("home", "")))
            away = item.get("awayTeam", item.get("awayTeamName", item.get("away", "")))
            if not home or not away:
                continue
            
            match_time = item.get("matchTime", item.get("matchDate", ""))
            # Extract time portion
            if " " in match_time:
                match_time = match_time.split(" ")[1][:5]
            elif len(match_time) > 5:
                match_time = match_time[-8:-3] if len(match_time) >= 8 else match_time[:5]
            if not match_time or match_time == "00:00":
                match_time = item.get("matchNum", "00:00")
                if len(match_time) > 5:
                    match_time = match_time[:5]
            
            league = item.get("leagueName", item.get("leagueAbbName", item.get("tournament", "")))
            
            # Odds (spf = 鑳滃钩璐?
            spf = item.get("spf", item.get("had", item.get("odds", {})))
            if isinstance(spf, dict):
                lh = float(spf.get("h", spf.get("home", spf.get("w", 1.8))))
                la_odds = float(spf.get("a", spf.get("away", spf.get("l", 1.5))))
            else:
                lh, la_odds = 1.8, 1.5
            
            # Convert odds to lambda (approximate goal expectation)
            # Higher odds = weaker team
            lh_lambda = round(2.0 / max(lh, 1.01), 2) if lh > 0 else 1.5
            la_lambda = round(2.0 / max(la_odds, 1.01), 2) if la_odds > 0 else 1.2
            
            # Form info (if available)
            fh = item.get("homeForm", item.get("homeRecent", ""))
            fa = item.get("awayForm", item.get("awayRecent", ""))
            h2h = item.get("h2h", item.get("historyMatch", ""))
            
            matches.append({
                "home": home,
                "away": away,
                "time": match_time,
                "lg": league or "涓栫晫鏉?,
                "lh": lh_lambda,
                "la": la_lambda,
                "fh": fh or "?",
                "fa": fa or "?",
                "h2h": h2h or "?",
                "mot": 4,
                "source": "sporttery.cn",
                "raw_odds": {"home": lh, "away": la_odds}
            })
        except Exception as e:
            print(f"  [skip] parse error: {e}")
            continue
    
    print(f"  [OK] 瑙ｆ瀽鍒?{len(matches)} 鍦烘瘮璧?)
    return matches if matches else None

# ============ 500.com 璧旂巼鎶撳彇 ============
def fetch_500_odds():
    """浠?00褰╃エ缃戞姄鍙栬禂鐜?""
    print("[Fetcher] 鎶撳彇500.com璧旂巼...")
    
    # 500.com API
    url = "https://odds.500.com/fenxi/ouzhi-1228391.shtml"
    text = http_get(url, timeout=10)
    if text and len(text) > 1000:
        print(f"  [OK] 500.com 杩斿洖 {len(text)} 瀛楄妭")
        # Parse odds from HTML (simplified)
        return parse_500_odds(text)
    
    # Try alternative endpoints
    alt_urls = [
        "https://live.500.com/detail.php?fid=1228391",
        "https://www.500.com/",
    ]
    for url in alt_urls:
        text = http_get(url, timeout=10)
        if text:
            print(f"  [OK] 500.com 澶囬€?{len(text)} 瀛楄妭")
            break
    
    print("  [WARN] 500.com 鏃犳暟鎹?)
    return None

def parse_500_odds(html):
    """瑙ｆ瀽500.com鐨勮禂鐜嘓TML"""
    # Simplified parser - extract odds using regex
    import re
    odds_data = {}
    
    # Try to find JSON data embedded in HTML
    json_match = re.search(r'var\s+data\s*=\s*({.+?});', html)
    if json_match:
        try:
            odds_data = json.loads(json_match.group(1))
        except:
            pass
    
    # Try table-based odds extraction
    odds_pattern = re.findall(r'<td[^>]*>(\d+\.\d+)</td>', html)
    if odds_pattern:
        odds_data["raw_odds"] = [float(o) for o in odds_pattern[:30]]
    
    return odds_data if odds_data else None

# ============ FIFA World Cup 2026 Schedule (Fallback) ============
def get_worldcup_schedule():
    """2026涓栫晫鏉皬缁勮禌璧涚▼锛堢‖缂栫爜鍏滃簳锛?""
    # Generate next 7 days of default matches based on known schedule
    today = datetime.now()
    schedules = {
        "2026-06-20": [
            ("鎹峰厠", "鍗楅潪", "00:00", "涓栫晫鏉疕缁?, 1.88, 1.56),
            ("鐟炲＋", "娉㈤粦", "03:00", "涓栫晫鏉疓缁?, 2.20, 1.20),
            ("鍔犳嬁澶?, "鍗″灏?, "06:00", "涓栫晫鏉疐缁?, 1.65, 1.10),
            ("澧ㄨタ鍝?, "闊╁浗", "09:00", "涓栫晫鏉疉缁?, 1.72, 1.30),
        ],
        "2026-06-21": [
            ("鑻辨牸鍏?, "浼婃湕", "00:00", "涓栫晫鏉疊缁?, 2.50, 1.10),
            ("闃挎牴寤?, "娌欑壒", "03:00", "涓栫晫鏉疌缁?, 2.80, 1.05),
            ("娉曞浗", "绉橀瞾", "06:00", "涓栫晫鏉疍缁?, 2.20, 1.15),
            ("宸磋タ", "濉炲皵缁翠簹", "09:00", "涓栫晫鏉疎缁?, 2.50, 1.10),
        ],
        "2026-06-22": [
            ("寰峰浗", "鏃ユ湰", "00:00", "涓栫晫鏉疎缁?, 1.95, 1.45),
            ("瑗跨彮鐗?, "鍝ユ柉杈鹃粠鍔?, "03:00", "涓栫晫鏉疐缁?, 2.30, 1.15),
            ("钁¤悇鐗?, "鍔犵撼", "06:00", "涓栫晫鏉疕缁?, 2.10, 1.30),
            ("鑽峰叞", "濉炲唴鍔犲皵", "09:00", "涓栫晫鏉疉缁?, 1.85, 1.50),
        ],
    }
    
    date_str = today.strftime("%Y-%m-%d")
    if date_str in schedules:
        return [
            {"home": h, "away": a, "time": t, "lg": lg, "lh": lh, "la": la, "fh": "?", "fa": "?", "h2h": "?", "mot": 4, "source": "schedule"}
            for h, a, t, lg, lh, la in schedules[date_str]
        ]
    return None

# ============ Main Fetcher ============

# ============ 500.com Live Fetcher ============
def fetch_500_live():
    """浠?00褰╃エ缃戝疄鏃舵姄鍙栨瘮璧?璧旂巼"""
    print("[Fetcher] 鎶撳彇500.com瀹炴椂鏁版嵁...")
    try:
        req = urllib.request.Request("https://odds.500.com", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        start = html.find("var ouzhiList = ")
        if start < 0:
            print("  [WARN] ouzhiList not found")
            return None
        start += len("var ouzhiList = ")
        end = html.find(";", start)
        ouzhi = json.loads(html[start:end])
        match_ids = list(ouzhi.keys())
        print(f"  [OK] Found {len(match_ids)} match IDs")
        
        matches = []
        for mid in match_ids[:12]:
            try:
                url = f"https://odds.500.com/fenxi/ouzhi-{mid}.shtml"
                req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    page = resp2.read().decode("gbk", errors="replace")
                title_m = re.search(r"<title>([^<]+)</title>", page)
                if not title_m: continue
                title = title_m.group(1)
                vs_m = re.search(r"([\u4e00-\u9fff]+)\s*VS\s*([\u4e00-\u9fff]+)", title)
                if not vs_m: continue
                home, away = vs_m.group(1), vs_m.group(2)
                lg_m = re.search(r"\(([^)]+)\)", title)
                league = lg_m.group(1) if lg_m else "2026涓栫晫鏉?
                time_m = re.search(r"(\d{2}:\d{2})", page)
                match_time = time_m.group(1) if time_m else "00:00"
                
                odds = ouzhi.get(mid, {}).get("2", [[2.0, 3.0, 3.0]])[0]
                lh = round(3.0 / max(float(odds[0]), 1.01), 2)
                la = round(3.0 / max(float(odds[2]), 1.01), 2)
                
                matches.append({
                    "home": home, "away": away, "time": match_time, "lg": league,
                    "lh": lh, "la": la, "fh": "?", "fa": "?", "h2h": "?", "mot": 4,
                    "source": "500.com",
                    "odds": {"home": float(odds[0]), "draw": float(odds[1]), "away": float(odds[2]),
                             "h_prob": float(odds[3]), "d_prob": float(odds[4]), "a_prob": float(odds[5])}
                })
                print(f"    {match_time} {home} vs {away} [{league}]")
            except Exception:
                continue
        print(f"  [OK] Got {len(matches)} matches from 500.com")
        return matches if matches else None
    except Exception as e:
        print(f"  [FAIL] 500.com: {e}")
        return None


# ============ 500.com Date-Specific Fetch ============
def fetch_500_by_date(date_str):
    """浠?live.500.com 鎸夋棩鏈熸姄鍙栨瘮璧?""
    import re
    print(f"[500.com] 鎶撳彇 {date_str} 姣旇禌...")
    
    url = f"https://live.500.com/?e={date_str}"
    html = http_get(url, timeout=15)
    if not html:
        print("[500.com] 鏃犳硶璁块棶 live.500.com")
        return None
    
    # 500.com uses GBK encoding - need to re-fetch with proper encoding
    try:
        import urllib.request as _ur
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with _ur.urlopen(req, timeout=15) as _resp:
            html = _resp.read().decode("gbk", errors="replace")
    except Exception as _e:
        print(f"[500.com] GBK retry failed: {_e}")
    
    matches = []
    
    # Parse match rows - look for team names with time patterns
    # Pattern: time, home team, away team, league
    # The page has <tr> elements with match data
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        # Check if this row has a time pattern (HH:MM)
        time_match = re.search(r'(\d{2}:\d{2})', row)
        if not time_match:
            continue
        
        match_time = time_match.group(1)
        
        # Find all Chinese text chunks (potential team names)
        text_chunks = re.findall(r'>([涓€-榭縘{2,6}(?:\s*[涓€-榭縘{2,6})?)<', row)
        # Also look for text in <a> tags
        a_texts = re.findall(r'<a[^>]*>([涓€-榭縘{2,6})</a>', row)
        
        all_teams = text_chunks + a_texts
        
        # Filter out common non-team text
        skip_words = ['涓栫晫鏉?, '鎺ㄨ崘', '缃《', '鑱旇禌', '鏃堕棿', '涓婚槦', '瀹㈤槦', '鍦烘', '璧涗簨', '杞', 
                      '鐘舵€?, '姣斿垎', '鍗婂満', '鐩存挱', '鍒嗘瀽', '涓€鐞?, '鍙椾竴鐞?, '鍗婄悆', '鍙楀崐鐞?,
                      '鐞冨崐', '鍙楃悆鍗?, '骞虫墜', '鍗虫椂鎸囨暟', '鍒濈洏鎸囨暟', '鑳屾櫙鐨偆', '鎻愮ず绐?,
                      '杩涚悆澹?, '鏃犲０', '榛樿', '缁忓吀', '鍠囧彮', '鍝ㄥ瓙', '鍙疯', '楦熼福',
                      '姝ｄ笂鏂?, '姝ｄ笅鏂?, '姝ｅ乏鏂?, '姝ｅ彸鏂?, '宸︿笂鏂?, '鍙充笂鏂?, '宸︿笅鏂?, '鍙充笅鏂?,
                      '閰风偒绱?, '娴锋磱钃?, '澶╃┖钃?, '鑽夊湴缁?, '鑳滆礋濂栭噾', '璁╃悆濂栭噾', '骞冲潎娆ц禂',
                      '鑳滆礋', '璁╃悆', '杩涚悆', '姣斿垎', '鍗婂叏', '鑺秴', '鐟炲吀瓒?, '鎸秴',
                      '涓ょ悆', '涓ょ悆鍗?, '鍙椾袱鐞?, '鍙椾袱鐞冨崐', '鐞冨崐涓ょ悆', '鍙楃悆鍗婁袱鐞?,
                      '涓€鐞冪悆鍗?, '鍙椾竴鐞冪悆鍗?, '鍗婄悆涓€鐞?, '鍙楀崐鐞冧竴鐞?, '骞虫墜鍗婄悆', '鍙楀钩鎵嬪崐鐞?]
        
        teams = [t.strip() for t in all_teams if t.strip() not in skip_words and len(t.strip()) >= 2]
        
        if len(teams) >= 2:
            home = teams[0]
            away = teams[1]
            
            # Try to find league
            league_match = re.search(r'<a[^>]*>([涓€-榭縘{2,4}(?:瓒厊鏉瘄鑱旇禌|鐢瞸涔檤閿璧?)</a>', row)
            league = league_match.group(1) if league_match else "涓栫晫鏉?
            
            # Extract actual match date from page (format: MM-DD)
            date_in_row = re.search(r'(\d{2}-\d{2})', row)
            match_date = date_str
            if date_in_row:
                month_day = date_in_row.group(1)
                # Determine year: if month is 01-06 and current month is 12, use next year
                from datetime import datetime as _dt2
                yr = _dt2.now().year
                if int(month_day[:2]) < _dt2.now().month - 6:
                    yr += 1
                match_date = str(yr) + "-" + month_day
            
            # Get lambda from handicap info in the row
            lh, la = 1.8, 1.2
            # Extract handicap text
            hcp_match = re.search(r'鐞僛/涓€-榭縘*', row)
            # Look for handicap patterns like 鍗婄悆/涓€鐞? 涓€鐞? etc.
            handicap_map = {
                '骞虫墜': (1.2, 1.2),
                '骞虫墜/鍗婄悆': (1.4, 1.05),
                '鍗婄悆': (1.6, 0.9),
                '鍗婄悆/涓€鐞?: (1.9, 0.8),
                '涓€鐞?: (2.2, 0.7),
                '涓€鐞?鐞冨崐': (2.5, 0.55),
                '鐞冨崐': (2.8, 0.45),
                '鐞冨崐/涓ょ悆': (3.0, 0.35),
                '涓ょ悆': (3.2, 0.3),
                '涓ょ悆/涓ょ悆鍗?: (3.4, 0.25),
                '涓ょ悆鍗?: (3.6, 0.2),
                '鍙楀钩鎵?鍗婄悆': (1.05, 1.4),
                '鍙楀崐鐞?: (0.9, 1.6),
                '鍙楀崐鐞?涓€鐞?: (0.8, 1.9),
                '鍙椾竴鐞?: (0.7, 2.2),
                '鍙椾竴鐞?鐞冨崐': (0.55, 2.5),
                '鍙楃悆鍗?: (0.45, 2.8),
            }
            
            # Check if home has (-N) or (+N)
            home_hcp = re.search(r'\(-(\d+)\)', row)
            away_hcp = re.search(r'\(\+(\d+)\)', row)
            
            # Sort by length descending to match longest/most specific handicap first
            sorted_hcps = sorted(handicap_map.items(), key=lambda x: -len(x[0]))
            for hcp_text, (hl, al) in sorted_hcps:
                if hcp_text in row:
                    lh, la = hl, al
                    break
            
            # Fallback lambda from team strength if no handicap matched
            if lh == 1.8 and la == 1.2:
                # Estimate from team names using built-in knowledge
                strong_teams = ['宸磋タ','寰峰浗','鑽峰叞','娉曞浗','瑗跨彮鐗?,'鑻辨牸鍏?,'闃挎牴寤?,'鎰忓ぇ鍒?,'钁¤悇鐗?,'鏃ユ湰','澧ㄨタ鍝?,'涔屾媺鍦?,'鍏嬬綏鍦颁簹']
                medium_teams = ['缇庡浗','鐟炲＋','涓归害','鍝ヤ鸡姣斾簹','鐟炲吀','闊╁浗','鎽╂礇鍝?,'鍦熻€冲叾','鍔犳嬁澶?,'鑻忔牸鍏?,'鍘勭摐澶氬皵']
                weak_teams = ['婢冲ぇ鍒╀簹','鍗楅潪','娉㈤粦','鍗″灏?,'娴峰湴','搴撴媺绱?,'宸存媺鍦?,'绐佸凹鏂?,'绉戠壒杩摝','娌欑壒','绉橀瞾']
                
                h_str = 1.0
                if home in strong_teams: h_str = 1.8
                elif home in medium_teams: h_str = 1.4
                elif home in weak_teams: h_str = 1.0
                
                a_str = 1.0
                if away in strong_teams: a_str = 1.8
                elif away in medium_teams: a_str = 1.4
                elif away in weak_teams: a_str = 1.0
                
                # Adjust lambda based on relative strength
                ratio = h_str / max(a_str, 0.5)
                lh = round(1.8 * ratio, 2)
                la = round(1.8 / max(ratio, 0.5), 2)
                lh = max(0.3, min(3.5, lh))
                la = max(0.2, min(3.5, la))

            # Avoid duplicates
            if not any(m["home"] == home and m["away"] == away for m in matches):
                matches.append({
                    "home": home,
                    "away": away,
                    "time": match_time,
                    "lg": league,
                    "lh": lh,
                    "la": la,
                    "fh": "?",
                    "fa": "?",
                    "h2h": "?",
                    "mot": 4,
                    "source": "500.com",
                    "date": match_date
                })
                print(f"  {match_time} {home} vs {away} [{league}] lh={lh} la={la}")
    
    if matches:
        matches.sort(key=lambda x: x.get("time", "23:59"))
        print(f"[500.com] 鎴愬姛鎶撳彇 {len(matches)} 鍦烘瘮璧?({date_str})")
        return matches
    else:
        print("[500.com] 鏈壘鍒版瘮璧涙暟鎹?)
        return None



# ============ Football-Data.org API Fetcher ============
FOOTBALL_API_KEY = "250064f72c9b4e2a962eb0b2f00caaf1"

def fetch_football_data(target_date_str):
    """浠?football-data.org 鎶撳彇瀹樻柟姣旇禌鏁版嵁"""
    from datetime import datetime as _dt2, timedelta as _td2
    
    print(f"[football-data.org] 鎶撳彇 {target_date_str} 姣旇禌...")
    
    # Need to query 2 date ranges to catch all Beijing-time matches
    target = _dt2.strptime(target_date_str, "%Y-%m-%d")
    day_before = (target - _td2(days=1)).strftime("%Y-%m-%d")
    day_after = (target + _td2(days=1)).strftime("%Y-%m-%d")
    
    all_matches = []
    target_mmdd = target.strftime("%m-%d")
    
    for date_from, date_to in [(day_before, target_date_str), (target_date_str, day_after)]:
        try:
            url = f"https://api.football-data.org/v4/matches?dateFrom={date_from}&dateTo={date_to}"
            req = urllib.request.Request(url, headers={"X-Auth-Token": FOOTBALL_API_KEY})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            
            for m in data.get("matches", []):
                utc = m.get("utcDate", "")
                if utc:
                    dt_utc = _dt2.fromisoformat(utc.replace("Z", "+00:00"))
                    bj = dt_utc + _td2(hours=8)
                    if bj.strftime("%m-%d") == target_mmdd:
                        ht = m["homeTeam"]["name"]
                        at = m["awayTeam"]["name"]
                        grp = m.get("group", "")
                        comp = m.get("competition", {}).get("name", "涓栫晫鏉?)
                        odds = m.get("odds", {})
                        
                        # Convert odds to lambda
                        lh, la = 1.8, 1.2
                        if odds.get("homeWin") and odds.get("awayWin"):
                            try:
                                ho = float(odds["homeWin"])
                                ao = float(odds["awayWin"])
                                lh = round(3.0 / max(ho, 1.01), 2)
                                la = round(3.0 / max(ao, 1.01), 2)
                            except:
                                pass
                        
                        all_matches.append({
                            "home": ht,
                            "away": at,
                            "time": bj.strftime("%H:%M"),
                            "date": target_date_str,
                            "lg": f"{comp} {grp}",
                            "lh": lh,
                            "la": la,
                            "fh": "?",
                            "fa": "?",
                            "h2h": "?",
                            "mot": 4,
                            "source": "football-data.org"
                        })
        except Exception as e:
            print(f"  [football-data.org] {date_from}: {e}")
    
    if all_matches:
        all_matches.sort(key=lambda x: x.get("time", "23:59"))
        print(f"[football-data.org] 鎶撳彇 {len(all_matches)} 鍦烘瘮璧?)
        for m in all_matches:
            print(f"  {m['time']} {m['home']} vs {m['away']} [{m['lg']}]")
    else:
        print("[football-data.org] 鏈壘鍒版瘮璧?)
    
    # Enrich with 500.com handicap data if odds are missing
    if all_matches:
        try:
            enrich_date = _dt2.now().strftime("%Y-%m-%d")
            hcp_matches = fetch_500_by_date(enrich_date)
            if hcp_matches:
                for m in all_matches:
                    if m.get("lh") == 1.8 and m.get("la") == 1.2:  # Default values
                        # Find matching match in 500.com data
                        for hm in hcp_matches:
                            # Fuzzy match team names
                            h1 = m["home"].lower().replace(" ","")
                            h2 = hm["home"].lower().replace(" ","")
                            a1 = m["away"].lower().replace(" ","")
                            a2 = hm["away"].lower().replace(" ","")
                            if (h1 in h2 or h2 in h1) and (a1 in a2 or a2 in a1):
                                m["lh"] = hm.get("lh", 1.8)
                                m["la"] = hm.get("la", 1.2)
                                print(f"  [merge] {m['home']} vs {m['away']}: using 500.com lh={m['lh']} la={m['la']}")
                                break
        except Exception as e:
            print(f"  [merge] enrichment failed: {e}")
    
    return all_matches if all_matches else None


def fetch_all(use_cache=True):
    """鎶撳彇鍏ㄩ儴鏁版嵁锛屼紭鍏堜娇鐢ㄥ疄鏃舵暟鎹?""
    # Try cache first
    if use_cache and os.path.exists(MATCHES_FILE):
        try:
            with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            cache_time = datetime.fromisoformat(cached.get("fetched_at", "2000-01-01"))
            if (datetime.now() - cache_time).total_seconds() < 3600:  # 1 hour cache
                print(f"[Fetcher] 浣跨敤缂撳瓨 ({cache_time.strftime('%H:%M')})")
                return cached.get("matches", [])
        except:
            pass
    
    matches = None
    from datetime import datetime as _dt, timedelta as _td
    today_str = _dt.now().strftime("%Y-%m-%d")
    target_date = (_dt.now() + _td(days=1)).strftime("%Y-%m-%d")
    
    # 1. Try 500.com (Chinese names + handicaps) - primary
    all_matches = fetch_500_by_date(today_str)
    if all_matches:
        target_mmdd = target_date[5:]
        matches = [m for m in all_matches if m.get("date","") == target_date or target_mmdd in m.get("date","")]
        if matches:
            print(f"[Fetcher] 500.com 绛涢€夊嚭 {len(matches)} 鍦?{target_date} 鐨勬瘮璧?)
        else:
            print(f"[Fetcher] 500.com 鏈壘鍒?{target_date} 鐨勬瘮璧?)
            matches = None
    
    # 2. Fallback to football-data.org
    if not matches:
        api_matches = fetch_football_data(target_date)
        if api_matches:
            matches = api_matches
            print(f"[Fetcher] 浣跨敤 football-data.org: {len(matches)} 鍦?)
    
    # 2. Fallback to sporttery.cn
    if not matches:
        for attempt in range(2):
            date_str = (datetime.now() + timedelta(days=attempt)).strftime("%Y-%m-%d")
            matches = fetch_sporttery_matches(date_str)
            if matches:
                break
    
    # 3. Fallback to schedule
    if not matches:
        print("[Fetcher] 浣跨敤涓栫晫鏉禌绋嬪厹搴?)
        matches = get_worldcup_schedule()
    
    # 3. Hard fallback
    if not matches:
        print("[Fetcher] 浣跨敤纭紪鐮佸厹搴曟暟鎹?)
        matches = [
            {"home":"鎹峰厠","away":"鍗楅潪","time":"00:00","lg":"涓栫晫鏉疕缁?,"lh":1.88,"la":1.56,"fh":"2鑳?骞?璐?,"fa":"3鑳?骞?璐?,"h2h":"棣栨浜ら攱","mot":4,"source":"fallback"},
            {"home":"鐟炲＋","away":"娉㈤粦","time":"03:00","lg":"涓栫晫鏉疓缁?,"lh":2.20,"la":1.20,"fh":"4鑳?骞?璐?,"fa":"1鑳?骞?璐?,"h2h":"鐟炲＋1鑳?骞?,"mot":5,"source":"fallback"},
            {"home":"鍔犳嬁澶?,"away":"鍗″灏?,"time":"06:00","lg":"涓栫晫鏉疐缁?,"lh":1.65,"la":1.10,"fh":"2鑳?骞?璐?,"fa":"0鑳?骞?璐?,"h2h":"棣栨浜ら攱","mot":4,"source":"fallback"},
            {"home":"澧ㄨタ鍝?,"away":"闊╁浗","time":"09:00","lg":"涓栫晫鏉疉缁?,"lh":1.72,"la":1.30,"fh":"3鑳?骞?璐?,"fa":"2鑳?骞?璐?,"h2h":"闊╁浗1鑳?骞?,"mot":5,"source":"fallback"},
        ]
    
    # Save cache
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(MATCHES_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "fetched_at": datetime.now().isoformat(),
                "matches": matches,
                "count": len(matches)
            }, f, ensure_ascii=False, indent=2)
        print(f"[Fetcher] 宸茬紦瀛?{len(matches)} 鍦烘瘮璧?)
    except Exception as e:
        print(f"[Fetcher] 缂撳瓨鍐欏叆澶辫触: {e}")
    
    return matches

# ============ Daily Scheduler ============
_scheduler_running = False

def start_scheduler(refresh_hour=14):
    """鍚姩姣忔棩瀹氭椂鍒锋柊锛堝悗鍙扮嚎绋嬶級"""
    global _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True
    
    def schedule_loop():
        print(f"[Scheduler] 姣忔棩 {refresh_hour}:00 鑷姩鍒锋柊宸插惎鍔?)
        while True:
            now = datetime.now()
            # Calculate seconds until next refresh
            target = now.replace(hour=refresh_hour, minute=0, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            wait_seconds = (target - now).total_seconds()
            print(f"[Scheduler] 涓嬫鍒锋柊: {target.strftime('%Y-%m-%d %H:%M')} ({wait_seconds/3600:.1f}h)")
            time.sleep(min(wait_seconds, 3600 * 3))  # Check every 3 hours max
            
            # Refresh when it's time
            now = datetime.now()
            if now.hour == refresh_hour and now.minute < 5:
                print(f"[Scheduler] 鈴?寮€濮嬫瘡鏃ュ埛鏂?..")
                try:
                    matches = fetch_all(use_cache=False)
                    print(f"[Scheduler] 鉁?鍒锋柊瀹屾垚: {len(matches)} 鍦烘瘮璧?)
                except Exception as e:
                    print(f"[Scheduler] 鉂?鍒锋柊澶辫触: {e}")
    
    t = threading.Thread(target=schedule_loop, daemon=True)
    t.start()
    print(f"[Scheduler] 鍚庡彴绾跨▼宸插惎鍔?)

# ============ Quick Test ============
if __name__ == '__main__':
    print("=" * 50)
    print("  鏁版嵁鎶撳彇娴嬭瘯")
    print("=" * 50)
    matches = fetch_all(use_cache=False)
    print(f"\n缁撴灉: {len(matches)} 鍦烘瘮璧?)
    for m in matches[:8]:
        print(f"  {m['time']} {m['home']} vs {m['away']} [{m['lg']}] src={m.get('source','?')}")