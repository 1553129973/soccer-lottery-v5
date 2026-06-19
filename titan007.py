"""
titan007 完整数据源 - 赔率/赛程/球队数据/历史交锋/积分榜
"""
import json, os, re
from datetime import datetime
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class Titan007:
    def __init__(self):
        self.base = "https://www.titan007.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.titan007.com/'
        }
    
    def fetch_odds(self, match_id=None):
        """赔率数据：胜平负/让球/大小球"""
        odds = {}
        try:
            url = f"{self.base}/odds/WorldCup2026/" if not match_id else f"{self.base}/odds/{match_id}"
            req = urllib.request.Request(url, headers=self.headers)
            resp = urllib.request.urlopen(req, timeout=15)
            html = resp.read().decode('gbk', errors='ignore')
            
            # Parse odds tables
            companies = ['澳门', '香港', '威廉希尔', 'bet365', '立博']
            for comp in companies:
                pattern = f'{comp}.*?(\d+\.\d+).*?(\d+\.\d+).*?(\d+\.\d+)'
                m = re.search(pattern, html)
                if m:
                    odds[comp] = {"win": float(m.group(1)), "draw": float(m.group(2)), "lose": float(m.group(3))}
            
            # Asian handicap
            hcap = re.findall(r'([\u4e00-\u9fff]+).*?([-+]?\d+\.?\d*).*?(\d+\.\d+).*?(\d+\.\d+)', html)
            if hcap:
                odds["asian_handicap"] = [{"team": h[0], "line": float(h[1]), "home_odds": float(h[2]), "away_odds": float(h[3])} for h in hcap[:5]]
            
            # Over/Under
            ou = re.findall(r'([大小])\s*球.*?(\d+\.?\d*).*?(\d+\.\d+).*?(\d+\.\d+)', html)
            if ou:
                odds["over_under"] = [{"type": o[0], "line": float(o[1]), "over": float(o[2]), "under": float(o[3])} for o in ou[:5]]
            
        except Exception as e:
            print(f"[titan007] 赔率: {str(e)[:60]}")
        return odds
    
    def fetch_team_stats(self, team_name):
        """球队数据：近期战绩/进球/失球/控球率"""
        stats = {"team": team_name, "recent": [], "avg_goals": 0, "avg_conceded": 0}
        try:
            # Try team page
            encoded = urllib.request.quote(team_name.encode('gbk'))
            url = f"{self.base}/team/{encoded}/"
            req = urllib.request.Request(url, headers=self.headers)
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode('gbk', errors='ignore')
            
            # Recent form
            results = re.findall(r'([\u4e00-\u9fff]+)\s+(\d+)-(\d+)\s+([\u4e00-\u9fff]+)', html)
            for r in results[:10]:
                stats["recent"].append({"opponent": r[0], "gf": int(r[1]), "ga": int(r[2]), "vs": r[3]})
            
            # Goal averages
            goals = re.findall(r'场均进球.*?(\d+\.?\d*)', html)
            if goals: stats["avg_goals"] = float(goals[0])
            conceded = re.findall(r'场均失球.*?(\d+\.?\d*)', html)
            if conceded: stats["avg_conceded"] = float(conceded[0])
            
        except Exception as e:
            print(f"[titan007] 球队数据 {team_name}: {str(e)[:40]}")
        return stats
    
    def fetch_h2h(self, home, away):
        """历史交锋记录"""
        h2h = {"matches": [], "summary": ""}
        try:
            url = f"{self.base}/compare/{urllib.request.quote(home.encode('gbk'))}_vs_{urllib.request.quote(away.encode('gbk'))}/"
            req = urllib.request.Request(url, headers=self.headers)
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode('gbk', errors='ignore')
            
            # Parse match history
            matches = re.findall(r'(\d{4}-\d{2}-\d{2}).*?(\d+)-(\d+)', html)
            for m in matches[:20]:
                h2h["matches"].append({"date": m[0], "score": f"{m[1]}-{m[2]}"})
            
            if h2h["matches"]:
                hwins = sum(1 for m in h2h["matches"] if int(m["score"].split('-')[0]) > int(m["score"].split('-')[1]))
                awins = sum(1 for m in h2h["matches"] if int(m["score"].split('-')[0]) < int(m["score"].split('-')[1]))
                draws = len(h2h["matches"]) - hwins - awins
                h2h["summary"] = f"{home}胜{hwins}场, {away}胜{awins}场, 平{draws}场"
            
        except Exception as e:
            print(f"[titan007] 交锋 {home}vs{away}: {str(e)[:40]}")
        return h2h
    
    def fetch_standings(self, group=None):
        """积分榜"""
        standings = []
        try:
            url = f"{self.base}/standings/WorldCup2026/"
            if group: url += f"?group={group}"
            req = urllib.request.Request(url, headers=self.headers)
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode('gbk', errors='ignore')
            
            # Parse standings table
            teams = re.findall(r'([\u4e00-\u9fff]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)[-:](\d+)\s+(\d+)', html)
            for t in teams[:32]:
                standings.append({
                    "team": t[0], "played": int(t[1]), "won": int(t[2]),
                    "drawn": int(t[3]), "lost": int(t[4]),
                    "gf": int(t[5]), "ga": int(t[6]), "pts": int(t[7])
                })
        except Exception as e:
            print(f"[titan007] 积分榜: {str(e)[:40]}")
        return standings
    
    def get_full_match_data(self, home, away):
        """获取一场比赛的完整数据包"""
        return {
            "odds": self.fetch_odds(),
            "home_stats": self.fetch_team_stats(home),
            "away_stats": self.fetch_team_stats(away),
            "h2h": self.fetch_h2h(home, away),
            "fetched_at": datetime.now().isoformat()
        }

titan = Titan007()
