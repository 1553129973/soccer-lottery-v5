import re, json, sys, os
from datetime import datetime, timedelta

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
    HAS_REQUESTS = True
except:
    import urllib.request
    HAS_REQUESTS = False

def http_get_gbk(url, timeout=10):
    """HTTP GET with GBK encoding (for 500.com)"""
    if HAS_REQUESTS:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        resp.encoding = 'gbk'
        return resp.text
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('gbk', errors='replace')

def http_get_utf8(url, timeout=10):
    """HTTP GET with UTF-8 encoding"""
    if HAS_REQUESTS:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        resp.encoding = 'utf-8'
        return resp.text
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')

import os
for k in ["HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy"]:
    os.environ.pop(k, None)

def fetch_500_matches():
    """浠?00褰╃エ缃戞姄鍙栨瘮璧涙暟鎹?""
    print("[500.com] 寮€濮嬫姄鍙栨瘮璧涙暟鎹?..")
    
    # Step 1: Get odds.500.com main page to find match IDs
    html = http_get_utf8("https://odds.500.com")
    if not html:
        print("[500.com] 鏃犳硶璁块棶odds.500.com")
        return None
    
    # Extract ouzhiList (娆ц禂鍒楄〃) - contains match IDs with odds
    ouzhi_match = re.search(r'var\s+ouzhiList\s*=\s*(\{[^}]+\})', html)
    match_ids = []
    if ouzhi_match:
        try:
            ouzhi = json.loads(ouzhi_match.group(1))
            match_ids = list(ouzhi.keys())
            print(f"[500.com] 鎵惧埌 {len(match_ids)} 涓瘮璧汭D: {match_ids[:10]}...")
        except Exception as e:
            print(f"[500.com] 瑙ｆ瀽ouzhiList澶辫触: {e}")
    
    if not match_ids:
        print("[500.com] 鏈壘鍒版瘮璧汭D")
        return None
    
    # Step 2: Fetch each match page for details
    matches = []
    for mid in match_ids[:10]:  # Limit to 10 matches
        try:
            url = f"https://odds.500.com/fenxi/ouzhi-{mid}.shtml"
            page = http_get_gbk(url)
            if not page:
                continue
            
            # Extract match info from title/page
            title_match = re.search(r'<title>([^<]+)</title>', page)
            title = title_match.group(1) if title_match else ""
            
            # Parse "澧ㄨタ鍝S闊╁浗(2026涓栫晫鏉?-鐧惧娆ц禂-500褰╃エ缃?
            vs_match = re.search(r'([\u4e00-\u9fff]+)\s*VS\s*([\u4e00-\u9fff]+)', title)
            if not vs_match:
                continue
            
            home = vs_match.group(1)
            away = vs_match.group(2)
            
            # Extract league/tournament
            lg_match = re.search(r'\(([^)]+)\)', title)
            league = lg_match.group(1) if lg_match else "鏈煡"
            
            # Extract match time
            time_match = re.search(r'(\d{2}:\d{2})', page)
            match_time = time_match.group(1) if time_match else "00:00"
            
            # Extract odds from ouzhiList
            odds_data = {}
            if ouzhi_match:
                try:
                    ouzhi = json.loads(ouzhi_match.group(1))
                    if mid in ouzhi:
                        mid_data = ouzhi[mid]
                        # Get initial odds (first company)
                        if "2" in mid_data and mid_data["2"]:
                            first_odds = mid_data["2"][0]
                            # [home_win, draw, away_win, home_pct, draw_pct, away_pct, return_rate, ...]
                            if len(first_odds) >= 7:
                                odds_data = {
                                    "home_odds": float(first_odds[0]),
                                    "draw_odds": float(first_odds[1]),
                                    "away_odds": float(first_odds[2]),
                                    "home_prob": float(first_odds[3]),
                                    "draw_prob": float(first_odds[4]),
                                    "away_prob": float(first_odds[5]),
                                }
                except:
                    pass
            
            # Calculate lambda from odds
            ho = odds_data.get("home_odds", 2.0)
            ao = odds_data.get("away_odds", 3.0)
            lh = round(3.0 / max(ho, 1.01), 2)
            la = round(3.0 / max(ao, 1.01), 2)
            
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
                "odds": odds_data
            })
            print(f"[500.com] {match_time} {home} vs {away} [{league}] lh={lh} la={la}")
            
        except Exception as e:
            print(f"[500.com] 鎶撳彇姣旇禌{mid}澶辫触: {e}")
            continue
    
    print(f"[500.com] 鎴愬姛鎶撳彇 {len(matches)} 鍦烘瘮璧?)
    return matches if matches else None

if __name__ == '__main__':
    print("=" * 50)
    print("  500.com Fetcher Test")
    print("=" * 50)
    matches = fetch_500_matches()
    if matches:
        print(f"\n鍏辨姄鍙?{len(matches)} 鍦烘瘮璧?")
        for m in matches:
            print(f"  {m['time']} {m['home']} vs {m['away']} [{m['lg']}] odds={m.get('odds',{})}")