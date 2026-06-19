"""
世界杯新闻中心 - 多源聚合足球新闻
数据源：titan007, 新浪体育, 腾讯体育, 直播吧
"""
import json, os, re
from datetime import datetime
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
NEWS_FILE = os.path.join(DATA_DIR, "news_cache.json")

NEWS_SOURCES = [
    {
        "name": "titan007",
        "url": "https://news.titan007.com/",
        "type": "专业足球数据"
    },
    {
        "name": "新浪体育-世界杯",
        "url": "https://sports.sina.com.cn/global/2026worldcup/",
        "type": "赛事新闻"
    },
    {
        "name": "直播吧",
        "url": "https://www.zhibo8.cc/news/",
        "type": "实时资讯"
    },
    {
        "name": "腾讯体育",
        "url": "https://sports.qq.com/worldcup/",
        "type": "深度分析"
    }
]

def fetch_news():
    """抓取多源新闻"""
    news = []
    for src in NEWS_SOURCES:
        try:
            req = urllib.request.Request(src["url"], headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            })
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract news titles and links
            text = re.sub(r'<[^>]+>', '\n', html)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            for line in lines:
                if len(line) >= 10 and len(line) <= 200:
                    if any(kw in line for kw in ['世界杯','足球','球队','比赛','球员','教练','小组','出线','淘汰','冠军']):
                        news.append({
                            "title": line,
                            "source": src["name"],
                            "type": src["type"],
                            "time": datetime.now().strftime("%H:%M")
                        })
        except Exception as e:
            print(f"[News] {src['name']}: {str(e)[:50]}")
    
    # Cache
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "updated": datetime.now().isoformat(),
            "count": len(news),
            "items": news[:100]
        }, f, ensure_ascii=False, indent=2)
    
    return news[:50]

def get_cached_news():
    """获取缓存的新闻"""
    try:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"items": [], "count": 0}

def get_news_feed():
    """获取新闻订阅（优先缓存，过期则刷新）"""
    cached = get_cached_news()
    if cached.get("items"):
        try:
            updated = datetime.fromisoformat(cached["updated"])
            if (datetime.now() - updated).total_seconds() < 3600:
                return cached
        except:
            pass
    return {"items": fetch_news(), "count": 0, "updated": datetime.now().isoformat()}
