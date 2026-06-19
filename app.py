# -*- coding: utf-8 -*-
"""足球分析助手 - 完整后端"""
import sys, os, json, math, random, threading, time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request


from hercules import run_prediction
from experts import run_all_experts
from features import get_all_features, PostMatchAnalysis, roi_tracker
from liuyao_v2 import interpret as liuyao_interpret, generate_hexagram
from knowledge_loader import kb, enhance_match_analysis
from auto_analyst import analyst
from news_center import get_news_feed, fetch_news
from titan007 import titan
from fusion import fuse_all_matches
from self_learner import learner
from betting_strategy import generate_full_betting_plan
# 赔率抓取 & 历史追踪
try:
    from odds_scraper import get_cached_odds, get_live_odds
    ODDS_AVAILABLE = True
except ImportError:
    ODDS_AVAILABLE = False

try:
    from history_tracker import record_prediction, update_actual_result, get_stats, get_recent_predictions
    HISTORY_AVAILABLE = True
except ImportError:
    HISTORY_AVAILABLE = False

# 自学习引擎
try:
    from self_learner import load_weights, save_weights, review_and_learn, get_learning_status, apply_expert_to_lambda
    LEARNER_AVAILABLE = True
except ImportError:
    LEARNER_AVAILABLE = False
    def load_weights(): return {}
    def apply_expert_to_lambda(lh, la, ht, at): return lh, la


app = Flask(__name__)

# ==================== 球队中文名映射 ====================
TEAM_NAMES_CN = {
    "Switzerland": "瑞士", "Bosnia-Herzegovina": "波黑", "USA": "美国", "Australia": "澳大利亚",
    "Czech Republic": "捷克", "South Africa": "南非", "Uzbekistan": "乌兹别克斯坦", "Colombia": "哥伦比亚",
    "Canada": "加拿大", "Qatar": "卡塔尔", "Mexico": "墨西哥", "South Korea": "韩国",
    "Scotland": "苏格兰", "Morocco": "摩洛哥", "Argentina": "阿根廷", "Brazil": "巴西",
    "Germany": "德国", "France": "法国", "England": "英格兰", "Spain": "西班牙",
    "Italy": "意大利", "Netherlands": "荷兰", "Portugal": "葡萄牙", "Belgium": "比利时",
    "Croatia": "克罗地亚", "Japan": "日本", "Iran": "伊朗", "Saudi Arabia": "沙特阿拉伯",
    "Denmark": "丹麦", "Sweden": "瑞典", "Norway": "挪威", "Poland": "波兰",
    "Austria": "奥地利", "Turkey": "土耳其", "Greece": "希腊", "Serbia": "塞尔维亚",
    "Ukraine": "乌克兰", "Wales": "威尔士", "Ireland": "爱尔兰", "Chile": "智利",
    "Uruguay": "乌拉圭", "Peru": "秘鲁", "Ecuador": "厄瓜多尔", "Paraguay": "巴拉圭",
    "Nigeria": "尼日利亚", "Egypt": "埃及", "Ghana": "加纳", "Cameroon": "喀麦隆",
    "Senegal": "塞内加尔", "Ivory Coast": "科特迪瓦", "Algeria": "阿尔及利亚", "Tunisia": "突尼斯",
}

# ==================== Poisson分布计算 ====================
# -*- coding: utf-8 -*-
# 2026世界杯专家分析数据库
# 标注：★=较稳判断  ◆=娱乐推演  ⚠=资料不足/不确定

EXPERT_DB = {
    "阿根廷": {"tier": "世界顶级", "fifa_zone": "FIFA#1", "group": "C", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯C组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "阿根廷国家男子足球队绰号\\"},
    "法国": {"tier": "世界顶级", "fifa_zone": "FIFA#2", "group": "D", "coach": "迪迪埃·德尚 (Didier Deschamps)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯D组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "法国国家男子足球队绰号\\\"高卢雄鸡\\\"，是目前世界足坛当之无愧的顶级豪强与夺冠大热门。\\n\\n在功勋主帅迪迪埃&middot;德尚的率领下，球队将顶级的个人天赋与极其务实的大赛战术完美融合，其技术风格可以高度概括为\\\"攻守均衡、稳守反击、闪电快攻\\\"。\\n\\n法国队的战术核心在于极高的容错率和针对性，不盲目追求华丽的传控，而是将比赛节奏牢牢掌握在自己手中。德尚为球队打造了极其成熟的杯赛打法。防守时，球队会保持紧凑的阵型，通过高强度的前场逼抢切断对手出球；断球后，则能瞬间由守转攻，利用前场球员惊人"},
    "西班牙": {"tier": "世界顶级", "fifa_zone": "FIFA#3", "group": "G", "coach": "塞尔吉奥.德拉富恩特 (Luis de la Fuente)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯G组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "西班牙国家男子足球队&zwnj;，绰号\\\"斗牛士军团\\\"，是国际足坛最具统治力的球队之一，现世界排名第一，隶属于西班牙皇家足球协会，现任主教练为&zwnj;路易斯&middot;德拉富恩特&zwnj;。\\n\\n西班牙在夺得 2008 年欧洲足球锦标赛之前，长时期无法在国际大赛上取得显赫的战绩，唯有个别球员能够达到世界顶级水平，但整体实力并不算突出。此前西班牙具代表性的荣誉仅有 1964 年的欧洲国家杯冠军及其次是 1992 年巴塞罗那奥运会足球赛冠军；而在世界杯的以往最佳成绩仅为 1950 年世"},
    "英格兰": {"tier": "世界顶级", "fifa_zone": "FIFA#4", "group": "F", "coach": "托马斯.图赫尔 (Thomas Tuchel)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯F组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "英格兰国家男子足球队，因其队徽上的三只狮子而被誉为\\\"三狮军团\\\"，是欧洲乃至世界足坛的传统豪强。他们带着自1966年本土夺冠后长达60年的等待，以夺冠大热的身份出征2026年美加墨世界杯。\\n\\n作为现代足球的发源地，英格兰队拥有辉煌的历史和深厚的足球底蕴。1966年，在本土举办的世界杯上，捧起了队史唯一一座大力神杯。\\n\\n在2026年世界杯欧洲区预选赛中，英格兰队展现了无与伦比的统治力。他们在K组以8战全胜、进23球且0失球的完美战绩，提前两轮锁定小组头名，成为欧洲区首支晋级决赛圈的球队，"},
    "巴西": {"tier": "世界顶级", "fifa_zone": "FIFA#5", "group": "B", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯B组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "巴西国家男子足球队，绰号\\"},
    "葡萄牙": {"tier": "欧洲一线", "fifa_zone": "FIFA#6", "group": "H", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯H组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "葡萄牙国家男子足球队绰号\\"},
    "荷兰": {"tier": "欧洲一线", "fifa_zone": "FIFA#7", "group": "E", "coach": "罗纳德.科曼 (Ronald Koeman)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯E组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "荷兰国家男子足球队，绰号 \\\"橙衣军团\\\"，是世界足坛的传统豪门，FIFA 排名第 7 位，以华丽的全攻全守足球闻名，却因三次世界杯亚军（1974、1978、2010）被称为 \\\"无冕之王\\\"。2026 年美加墨世界杯，荷兰队以欧洲区预选赛 G 组不败战绩晋级，队史第 12 次踏上世界杯舞台。\\n\\n在世界杯的历史长河中，荷兰队曾三次闯入决赛，却都遗憾地与冠军失之交臂。1974年，他们以华丽的足球征服世界，却在决赛中不敌西德；1978年，他们再次倒在决赛舞台，负于阿根廷；2010年，由斯内德和罗"},
    "比利时": {"tier": "欧洲一线", "fifa_zone": "FIFA#8", "group": "H", "coach": "鲁迪.加西亚 (Rudi Garcia)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯H组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "比利时国家男子足球队绰号\\\"欧洲红魔\\\"，是世界足坛一支底蕴深厚且正处于新老交替关键期的欧洲劲旅。在现任主帅鲁迪&middot;加西亚的带领下，球队告别了过去单纯依赖球星个人能力的模式，全面转向\\\"快速攻防转换、边路爆破、稳固防守\\\"的现代高效战术体系。\\n\\n自从 2018 年俄罗斯世界杯夺得季军、创下队史最佳战绩后，比利时国家男子足球队随着黄金一代逐渐淡出，实力开始出现下滑，2022 年卡塔尔世界杯小组赛出局、2024 年欧洲杯止步十六强，昔日世界第一的统治力不复当年。\\n\\n但近几年来，比"},
    "德国": {"tier": "欧洲一线", "fifa_zone": "FIFA#9", "group": "E", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯E组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "德国国家男子足球队绰号\\"},
    "乌拉圭": {"tier": "欧洲一线", "fifa_zone": "FIFA#11", "group": "F", "coach": "马塞洛.贝尔萨 (Marcelo Bielsa)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯F组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "乌拉圭国家男子足球队，绰号\\\"天蓝军团\\\"，由乌拉圭足球协会管辖，是世界足坛历史底蕴最深厚的传统豪门之一。球队曾于 1930 年首届世界杯、1950 年 \\\"马拉卡纳奇迹\\\" 两度登顶世界之巅，更早于 1924、1928 年蝉联奥运会足球金牌，以铁血防守、顽强斗志和高效反击闻名足坛，更是美洲杯 15 次夺冠的历史王者之一。\\n\\n在 2022 卡塔尔世界杯后，球队完成新老交替，阵容实力与活力大幅提升。乌拉圭足球的灵魂在于其奉行的\\\"加拉精神\\\"（Garra Charr&uacute;a），代表着"},
    "克罗地亚": {"tier": "欧洲一线", "fifa_zone": "FIFA#12", "group": "G", "coach": "奎罗兹 (Carlos Manuel Queiroz)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯G组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "克罗地亚国家男子足球队，因其标志性的红白格子球衣而被誉为\\\"格子军团\\\"，是世界足坛一支以顽强意志和坚韧精神著称的劲旅。\\n\\n1990年代克罗地亚独立，克罗地亚国家队也正式成立。自加入国际足联以来，在世界杯赛场上书写了属于自己的传奇。尽管全国人口不足四百万，但他们多次在世界最高舞台上取得远超体量的优异成绩。由于之前南斯拉夫出产了大量优秀球星，故克罗地亚一立国亦继承了很多出色猛将。在其国家独立后，克罗地亚在世界杯和欧锦赛上的成绩可圈可点。\\n\\n在2026年世界杯欧洲区预选赛中，克罗地亚队表现强"},
    "哥伦比亚": {"tier": "二档强队", "fifa_zone": "FIFA#13", "group": "J", "coach": "内斯托·洛伦佐 (Nestor Lorenzo)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯J组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "哥伦比亚国家男子足球队绰号\\\"南美神鹰\\\"，是南美足坛一支技术华丽、球风奔放的劲旅。\\n\\n在现任主帅内斯托尔&middot;洛伦索的调教下，球队将南美足球传统的灵巧技术与欧洲足球的战术纪律完美结合，其技术风格可以高度概括为\\\"双核驱动、快速转换、边路爆破\\\"。\\n\\n阿根廷籍主帅洛伦索师从名帅佩克尔曼，自2022年接手球队后，为哥伦比亚队打造了极具现代感的战术体系。球队不再单纯依赖个人天赋，而是极度强调战术纪律和整体防守的紧凑性。在由守转攻时，哥伦比亚队能迅速通过简洁的传递发动反击，力求在对手"},
    "摩洛哥": {"tier": "二档强队", "fifa_zone": "FIFA#14", "group": "E", "coach": "穆罕默德.瓦赫比 (Mohamed Ouahbi)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯E组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "摩洛哥国家男子足球队，绰号\\\"亚特拉斯雄狮\\\"，&zwnj;&zwnj; 作为非洲足球的杰出代表，该队近年来凭借一系列突破性成就，已从国际足坛的黑马蜕变为一支不可忽视的稳定强队。&zwnj;&zwnj;\\n\\n摩洛哥足球历史悠久，其国家队在1928年进行了首场比赛。&zwnj;&zwnj; 该队创造了多项非洲足球纪录：1970年成为首支直接晋级世界杯决赛圈的非洲球队，1986年成为首支获得世界杯小组头名的非洲球队。&zwnj;&zwnj; 在非洲国家杯赛场，摩洛哥于1976年夺冠，并在2004年"},
    "日本": {"tier": "二档强队", "fifa_zone": "FIFA#15", "group": "D", "coach": "森保一 (Hajime Moriyasu)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯D组", "host_factor": 0, "confidence": "高", "dark_horse": "中", "expert_note": "日本国家男子足球队绰号\\\"蓝武士\\\"，是亚洲足坛当之无愧的绝对霸主，也是目前世界足坛一支不容小觑的准一流强队。在现任主帅森保一的带领下，球队不仅稳居亚洲第一，更在FIFA的世界排名中高居世界第18位。\\n\\n日本自 1998 年首进世界杯后从未缺席，2022 年卡塔尔世界杯击败德国、西班牙创历史晋级十六强。2026 年预选赛以7 胜 0 平 1 负提前三轮锁定资格，成为全球最早晋级的球队之一，展现了高效的竞赛体系。\\n\\n森保一为球队打造了类似曼城的现代足球体系。球队不仅保留了细腻的地面传控和快"},
    "墨西哥": {"tier": "二档强队", "fifa_zone": "FIFA#16", "group": "A", "coach": "哈维尔.阿吉雷 (Javier Aguirre)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯A组", "host_factor": 12, "confidence": "中", "dark_horse": "中", "expert_note": "墨西哥国家男子足球队（绰号\\\"三色军团\\\"，El Tri）是中北美及加勒比海地区的绝对霸主，也是世界足坛公认的传统劲旅。球队以灵动华丽的脚下技术、极具侵略性的前场压迫以及在国际大赛中极高的稳定性著称，始终扮演着\\\"强队杀手\\\"的角色。\\n\\n球队历史荣光璀璨，是世界杯舞台上最活跃的力量之一：自1930年首届世界杯至今已18次杀入决赛圈。历史上曾两次举办世界杯（1970年、1986年），均闯入八强，铸就了队史巅峰。此外，墨西哥队在地区赛事中统治力惊人，曾15次夺得中北美及加勒比海金杯赛（含前身）冠"},
    "美国": {"tier": "二档强队", "fifa_zone": "FIFA#17", "group": "J", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯J组", "host_factor": 12, "confidence": "中", "dark_horse": "中", "expert_note": "美国国家男子足球队，绰号\\"},
    "瑞士": {"tier": "二档强队", "fifa_zone": "FIFA#18", "group": "I", "coach": "卡洛.安切洛蒂 (Carlo Ancelotti)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯I组", "host_factor": 0, "confidence": "中", "dark_horse": "中", "expert_note": "　　瑞士国家男子足球队（绰号\\\"十字军团\\\"，Rossocrociati）是欧洲足坛公认的\\\"顶级强队敲门砖\\\"与\\\"战术执行力天花板\\\"。球队以极致的防守组织、严密的战术纪律以及极其稳定的心理素质著称，在世界大赛中多次扮演\\\"豪强终结者\\\"的角色。\\n　　\\n球队历史荣光璀璨，是国际足坛极具韧性的中坚力量：自1934年首次参赛以来，已累计13次杀入决赛圈。历史上曾三次闯入世界杯八强（1934年、1938年及1954年），虽然在现代世界杯中多次止步16强，但他们在2020年欧洲杯中点球淘汰卫冕冠"},
    "塞内加尔": {"tier": "二档强队", "fifa_zone": "FIFA#19", "group": "F", "coach": "帕佩·蒂亚乌 (Pape Thiaw)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯F组", "host_factor": 0, "confidence": "中", "dark_horse": "中", "expert_note": "塞内加尔国家男子足球队绰号 \\\"特兰加雄狮\\\"，是非洲足坛最具实力和影响力的球队之一，长期稳居非洲足联排名前列。球队成立于 1960 年，1964 年正式加入国际足联和非洲足联，以身体强壮、防守稳固、反击犀利著称，打法硬朗且极具冲击力，是世界杯和非洲杯的常客。\\n\\n2002 年韩日世界杯是塞内加尔的成名之战，首次参赛便在揭幕战爆冷击败卫冕冠军法国，一路闯入八强，创造队史最佳世界杯战绩，震惊世界足坛。此后球队经历起伏，2018 年俄罗斯世界杯重返决赛圈，2022 年卡塔尔世界杯再度晋级十六强，展"},
    "韩国": {"tier": "二档强队", "fifa_zone": "FIFA#20", "group": "C", "coach": "洪明甫 (Hong Myung-Bo)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯C组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "韩国国家男子足球队绰号\\\"太极虎\\\"，是亚洲足坛当之无愧的传统霸主。球队最大的亮点是已经连续11次杀入世界杯决赛圈，创造了亚洲纪录，并在2002年本土世界杯上历史性地夺得殿军（第四名），至今仍是亚洲球队在世界杯上的最佳战绩。\\n\\n本届世界杯被外界视为韩国足球\\\"黄金一代\\\"的最后一舞，以队长孙兴慜为首的核心阵容将迎来谢幕战，球队的目标是再次从小组赛突围，寻求淘汰赛的突破。\\n\\n韩国队全队总身价高达约2.1亿欧元。在战术上，洪明甫通常采用 4-2-3-1 或 3-4-3 阵型，球队不再单纯依赖"},
    "伊朗": {"tier": "二档强队", "fifa_zone": "FIFA#21", "group": "B", "coach": "阿米尔·加莱诺埃 (Amir Ghalenoei)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯B组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "伊朗国家男子足球队是亚洲足坛的传统豪强，由伊朗足球协会管理。球队成立于1920年，绰号\\\"波斯铁骑\\\"，主场设在可容纳超过10万人的阿萨迪体育场。\\n\\n伊朗队是亚洲足球史上唯一实现亚洲杯三连冠（1968年、1972年、1976年）的球队，底蕴深厚。球队历史上共6次晋级世界杯决赛圈（1978年、1998年、2006年、2014年、2018年、2022年），2026 年美加墨世界杯将是伊朗第7次踏上世界杯赛场。在世界杯赛场上，曾取得过3场胜利，分别是1998年击败美国、2018年绝杀摩洛哥，以及2"},
    "埃及": {"tier": "二档强队", "fifa_zone": "FIFA#24", "group": "G", "coach": "霍萨姆·哈桑 (Hossam Hassan)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯G组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "埃及国家男子足球队&zwnj;，绰号\\\"法老军团\\\"，成立于1921年，由埃及足球协会管辖。球队在非洲杯赛场战绩辉煌，共&zwnj;7次夺冠&zwnj;，是该项赛事历史上最成功的队伍。埃及是非洲足球的开创者，是第一支参加世界杯的非洲国家，早在 1934 年便登上世界杯舞台，成为非洲足球的代表。此后埃及分别在 1990 年、2018 年再度晋级世界杯决赛圈，2026 年美加墨世界杯将是埃及第四次踏上世界杯赛场。\\n\\n在功勋主帅侯赛姆&middot;哈桑的带领下，球队将战术纪律与球星个人天赋完美融"},
    "科特迪瓦": {"tier": "二档强队", "fifa_zone": "FIFA#25", "group": "J", "coach": "埃默塞.法埃 (Emerse Fae)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯J组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "科特迪瓦国家男子足球队，绰号\\\"非洲大象\\\"，是非洲足坛的传统劲旅。是非洲足坛传统豪强，FIFA 排名第 34 位。2026 年美加墨世界杯是其队史第 4 次晋级决赛圈，这支西非劲旅以其强悍的身体素质、出色的个人技术和充满激情的比赛风格而闻名于世。时隔 12 年重返世界杯舞台，目标打破 \\\"黄金一代\\\" 从未小组出线的魔咒。\\n\\n科特迪瓦此前曾在2006、2010、2014年连续三届参加世界杯，但均止步小组赛，其中德罗巴、亚亚&middot;图雷领衔的\\\"黄金一代\\\"曾在2006年3-2击败塞"},
    "突尼斯": {"tier": "中游球队", "fifa_zone": "FIFA#26", "group": "L", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯L组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "突尼斯队，人们会先想起他们身上的一个标签：\\"},
    "加拿大": {"tier": "中游球队", "fifa_zone": "FIFA#27", "group": "A", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯A组", "host_factor": 12, "confidence": "中", "dark_horse": "高", "expert_note": "加拿大国家男子足球队,绰号\\"},
    "奥地利": {"tier": "中游球队", "fifa_zone": "FIFA#28", "group": "K", "coach": "罗伯托.马丁内斯 (Roberto Martinez Gutierrez)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯K组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "奥地利国家男子足球队由奥地利足球协会管理，球队成立于1904年，绰号\\\"条顿军团\\\"。这是一支欧洲足坛的传统劲旅，在经历了长达28年的沉寂后，他们终于在2025年强势突围，重返世界杯舞台。\\n\\n奥地利队历史上共7次晋级世界杯决赛圈。他们在1954年瑞士世界杯上大放异彩，一路杀入半决赛，最终获得季军，这也是球队在世界杯历史上的最佳战绩。此外，他们还在1934年世界杯获得殿军，并在1978年和1982年两度闯入八强。在经历了自1998年后的漫长低谷期后，奥地利队在2025年的世预赛欧洲区中表现强势"},
    "苏格兰": {"tier": "中游球队", "fifa_zone": "FIFA#29", "group": "M", "coach": "波波维奇 (Anthony Popovic)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯M组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "苏格兰国家男子足球队，绰号\\\"格子军团\\\"，是现代足球运动的发源地代表之一，承载着世界上最古老的国际足球底蕴。球队以极其坚韧的集体防守、充满激情的对抗意志以及极具爆发力的边路推进著称，在赛场上始终保持着昂扬的斗志。\\n\\n球队历史荣光璀璨，作为国际足球历史的开创者之一：苏格兰与英格兰在1872年进行了世界足球史上第一场正式国际比赛。历史上，苏格兰队曾8次杀入世界杯决赛圈，尤其在20世纪70至80年代曾连续五届入围，涌现了肯尼&middot;达格利什、丹尼斯&middot;劳等殿堂级巨星。虽然此后"},
    "土耳其": {"tier": "中游球队", "fifa_zone": "FIFA#30", "group": "I", "coach": "尤利安.纳格尔斯曼 (Julian Nagelsmann)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯I组", "host_factor": 0, "confidence": "中", "dark_horse": "高", "expert_note": "土耳其国家男子足球队绰号\\\"星月弯刀军团\\\"，成立于1923年。由于地跨欧亚，球队在1962年选择\\\"脱亚入欧\\\"加入欧足联，这一战略决策极大地提升了其足球竞技水平。目前，球队由意大利籍主帅文森佐&middot;蒙特拉执掌，国际足联世界排名第22位。\\n\\n2026年世预赛附加赛中，土耳其队凭借阿克蒂尔克奥卢的制胜球1-0力克科索沃，时隔24年重返世界杯决赛圈，这也是队史第3次晋级。谈到世界杯，就不得不提土耳其足球的巅峰&mdash;&mdash;2002年韩日世界杯。在主帅居内什的率领下，拥有"},
    "巴拉圭": {"tier": "中游球队", "fifa_zone": "FIFA#32", "group": "M", "coach": "古斯塔沃·阿尔法罗 (Gustavo Alfaro)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯M组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "巴拉圭国家男子足球队成立于1906年，绰号\\\"红白军团\\\"，以坚韧的防守和顽强的球风在南美足坛独树一帜 。球队目前由阿根廷籍主帅古斯塔沃&middot;阿尔法罗执掌，国际足联世界排名第40位 。\\n\\n2026年世预赛南美区，巴拉圭队凭借坚固的防守（17轮仅失10球）成功突围，以南美区第六名（28 分）晋级，期间1-0 巴西、2-1 阿根廷，时隔16年重返世界杯决赛圈，这也是队史第9次晋级正赛 。\\n\\n球队在阿根廷籍主帅古斯塔沃&middot;阿尔法罗的调教下，风格极其鲜明，可以概括为\\\"防守"},
    "南非": {"tier": "中游球队", "fifa_zone": "FIFA#33", "group": "I", "coach": "雨果.布鲁斯 (Hugo Broos)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯I组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "南非国家男子足球队绰号\\\"巴法纳&middot;巴法纳\\\"，在恩古尼语中意为\\\"小伙子们\\\"，是非洲足坛的一支传统劲旅。球队最大的亮点是时隔16年重返世界杯正赛，并将在本届世界杯的揭幕战中再次对阵东道主墨西哥。\\n\\n 南非队在2026年世界杯非洲区预选赛中表现极其顽强。尽管中途因违规使用停赛球员被扣除3分，但他们依然在小组末轮3-0击败卢旺达，力压尼日利亚以小组第一的身份出线，打破了长达16年的世界杯荒。\\n 南非队全队总身价仅约4115万欧元，是A组中身价最低的球队，整体实力相对处于劣势。不"},
    "加纳": {"tier": "中游球队", "fifa_zone": "FIFA#34", "group": "L", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯L组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "<font face=\\"},
    "挪威": {"tier": "中游球队", "fifa_zone": "FIFA#36", "group": "B", "coach": "莱昂内尔·斯卡罗尼 (Lionel Sebastian Scaloni)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯B组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "挪威国家男子足球队是欧洲足坛颇具特色的球队，绰号\\\"北欧海盗\\\"，虽未跻身传统世界豪门之列，但凭借强悍的身体对抗、简洁高效的战术打法以及世界级球星加持，始终是国际大赛不可忽视的力量，队史曾迎来黄金时代，如今再度坐拥天赋爆表的核心阵容，重回世界足坛主流视野。\\n\\n挪威足球早年在国际大赛中鲜有亮眼表现，整体实力长期处于欧洲中游，未曾染指世界杯、欧洲杯等顶级赛事桂冠，也未在洲际大赛中取得过显赫战绩，更多是作为陪跑者参与角逐，仅依靠个别球员的个人能力撑起门面，团队战斗力与体系化打法尚未形成。此前挪威具"},
    "瑞典": {"tier": "中游球队", "fifa_zone": "FIFA#37", "group": "K", "coach": "埃尔韦·勒纳尔 (Herve Renard)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯K组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "瑞典国家男子足球队，素有\\\"北欧海盗\\\"之称，是国际足坛一支历史悠久且战绩斐然的劲旅。球队成立于1904年，截至2026年，已第13次晋级世界杯决赛圈，FIFA 排名第38位，是国际足联的创始成员之一，其主场设在斯德哥尔摩奥林匹克体育场。瑞典足球以其传统的北欧力量型打法为基础，近年来融入了更多技术元素，形成了坚韧、团结且富有冲击力的\\\"新北欧风格\\\"。\\n\\n瑞典队在世界杯历史上有着不容小觑的成绩单。其最佳战绩是在1958年作为东道主时一路杀入决赛，最终惜败于拥有贝利的巴西队，荣获亚军。此外，他"},
    "捷克": {"tier": "中游球队", "fifa_zone": "FIFA#38", "group": "M", "coach": "雨果.布鲁斯 (Hugo Broos)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯M组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "捷克国家男子足球队是欧洲足坛的传统劲旅，因其强悍的球风也被称为\\\"东欧铁骑\\\"。球队前身为曾两夺世界杯亚军（1934年、1962年）和一次欧洲杯冠军（1976年）的捷克斯洛伐克国家队。1993年捷克独立后，球队继承了其足球底蕴，并在1996年欧洲杯上以\\\"黄金一代\\\"为核心首次参赛便斩获亚军。\\n捷克队近期最受关注的动态是时隔20年重返世界杯正赛。在2026年4月的世预赛欧洲区附加赛决赛中，捷克队总比分5-3击败丹麦，成功拿到了通往美加墨世界杯的门票。\\n捷克队通常以3-4-2-1或3-5-2作"},
    "波黑": {"tier": "中游球队", "fifa_zone": "FIFA#39", "group": "L", "coach": "毛里西奥.波切蒂诺 (Mauricio Pochettino Trosero)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯L组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "波斯尼亚和黑塞哥维那国家男子足球队（绰号\\\"龙之队\\\"，Zmajevi）是欧洲巴尔干半岛足球力量的杰出代表，承载着战后国家重建的荣耀与希望。球队以浓郁的东欧技术流风格、出色的身体对抗以及极具爆发力的反击著称，长期处于欧洲二流梯队的顶尖水平\\n\\n球队历史荣光璀璨，虽建队时间较晚但起点极高：自1995年加入FIFA以来，波黑足球迅速崛起。2014年巴西世界杯是其历史性的巅峰，球队首次杀入决赛圈并在小组赛中取得胜绩。此后，波黑队虽多次在附加赛中遗憾出局，但始终保持着极高的竞技水准，曾在2013年创下"},
    "卡塔尔": {"tier": "中游球队", "fifa_zone": "FIFA#40", "group": "J", "coach": "胡伦.洛佩特吉 (Julen Lopetegui)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯J组", "host_factor": 0, "confidence": "低", "dark_horse": "高", "expert_note": "卡塔尔国家男子足球队，绰号\\\"酒红色军团\\\"，由卡塔尔足球协会管理，球队成立于1960年。\\n这是一支依靠金元投入和长期青训规划迅速崛起的亚洲新贵。作为两届亚洲杯卫冕冠军，卡塔尔队在亚洲足坛极具统治力，并已历史性地首次通过预选赛晋级世界杯，即将踏上2026年美加墨世界杯的舞台。\\n卡塔尔队近年来在亚洲赛场表现强势，先后在2019年和2024年两度夺得亚洲杯冠军，成功实现卫冕，稳居亚洲足球第一梯队。继2022年以东道主身份首次亮相后，卡塔尔队在2026年世界杯亚洲区预选赛中表现优异，通过附加赛击败"},
    "阿尔及利亚": {"tier": "下游/新军", "fifa_zone": "FIFA#41", "group": "K", "coach": "弗拉基米尔·佩特科维奇 (Vladimir Petkovic)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯K组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "阿尔及利亚国家男子足球队由阿尔及利亚足球协会管理，球队成立于1962年，绰号\\\"沙漠之狐\\\"。\\n\\n这是一支非洲足坛的传统劲旅，球风彪悍且充满激情。在经历了12年的等待后，他们成功重返世界杯舞台，是一支拥有极强搅局能力的球队。\\n阿尔及利亚队历史上曾两次捧起非洲国家杯冠军奖杯，分别是在1990年本土举办的赛事，以及2019年。球队历史上共4次晋级世界杯决赛圈（1982年、1986年、2010年、2014年），在2014年巴西世界杯上，阿尔及利亚队表现惊艳，历史性地闯入16强。虽然在加时赛中1-"},
    "伊拉克": {"tier": "下游/新军", "fifa_zone": "FIFA#42", "group": "H", "coach": "格拉汉姆·阿诺德 (Graham Arnold)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯H组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "伊拉克国家男子足球队&zwnj;，绰号\\\"&zwnj;美索不达米亚雄狮&zwnj;\\\"，由伊拉克足球协会管理，自1948年起代表伊拉克参加国际赛事，是西亚地区具有悠久历史的国家队之一。\\n\\n伊拉克队于&zwnj;1950年加入国际足联&zwnj;，1970年成为亚足联成员，2000年加入西亚足球联合会。球队最辉煌的成就是在&zwnj;2007年亚洲杯&zwnj;上&zwnj;奇迹夺冠&zwnj;，当时在不被看好的情况下，一路杀入决赛并击败沙特，首次捧起亚洲杯，成为国家团结的象征。\\n\\n尽管在"},
    "约旦": {"tier": "下游/新军", "fifa_zone": "FIFA#43", "group": "G", "coach": "N/A", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯G组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "<font face=\\"},
    "乌兹别克斯坦": {"tier": "下游/新军", "fifa_zone": "FIFA#45", "group": "E", "coach": "法比奥.卡纳瓦罗 (Fabio Cannavaro)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯E组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "乌兹别克斯坦国家男子足球队由乌兹别克斯坦足球协会管理，球队绰号\\\"中亚狼\\\"。\\n\\n这是一支近年来在亚洲足坛迅速崛起的硬核力量。凭借着对青训体系数十年如一日的深耕，乌兹别克斯坦足球在2026年迎来了井喷式的爆发，不仅各年龄段青年队屡创佳绩，成年国家队更是历史性地首次登上了世界杯的舞台。\\n\\n近年来，乌兹别克斯坦各级国字号队伍全面爆发。他们不仅夺得了U23亚洲杯冠军（2018年）、U20亚洲杯冠军（2023年）和U17亚洲杯冠军（2024年），更在2024年历史性地首次闯入奥运会男足决赛圈，实"},
    "巴拿马": {"tier": "下游/新军", "fifa_zone": "FIFA#46", "group": "C", "coach": "托马斯·克里斯蒂安森 (Thomas Christiansen)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯C组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "巴拿马国家男子足球队，绰号\\\"运河工兵\\\"，正以昂扬的姿态第二次踏上世界杯的征程。这支来自中美洲的球队以其硬朗的球风、严明的纪律和强大的团队凝聚力而闻名。\\n\\n在2026年世界杯中北美及加勒比海地区预选赛中，巴拿马队表现极为出色。他们以小组头名的身份，力压诸多对手，强势锁定一张直通世界杯的门票。这标志着他们连续第二届闯入世界杯决赛圈，完成了历史性的突破。\\n\\n球队由丹麦籍主教练托马斯&middot;克里斯蒂安森掌舵。他将北欧足球严谨的战术体系与中美洲球员狂野不羁的激情相结合，打造出了一支纪律"},
    "新西兰": {"tier": "下游/新军", "fifa_zone": "FIFA#47", "group": "A", "coach": "达伦·巴泽利 (Darren Bazeley)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯A组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "新西兰国家男子足球队（昵称 &quot;全白队&quot;）由新西兰足球协会管辖，是大洋洲足坛的绝对霸主。球队曾于 1982 年、2010 年两度晋级世界杯决赛圈，2010 年南非世界杯更以三场平局（含 1-1 逼平意大利）保持不败，创下队史世界杯最佳战绩。但此后连续两届世预赛（2018、2022）均在洲际附加赛失利，与正赛失之交臂。\\n\\n由本土教练达伦&middot;巴泽利执掌教鞭。他自2023年接手国家队以来，迅速完成了球队的新老交替，打造了一支纪律严明的铁军。新西兰足球稳步复苏，阵容新老"},
    "库拉索": {"tier": "下游/新军", "fifa_zone": "FIFA#48", "group": "A", "coach": "迪克.艾德沃卡特 (Dick Nicolaas Advocaat)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯A组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "库拉索国家男子足球队，绰号\\\"蓝色浪潮\\\"，是2026年美加墨世界杯最具传奇色彩的新军，FIFA 排名第82位。这个位于加勒比海南部、与上海面积相当的荷兰王国自治国，人口仅约15.6万，国土面积444平方公里，在2025年11月力压牙买加等强敌成功突围，成为世界杯历史上人口最少、国土面积最小的参赛球队。\\n\\n这是库拉索队史首次晋级世界杯正赛。球队的前身是荷属安的列斯代表队，2010年荷属安的列斯解体后，库拉索于2011年成立足协并加入国际足联，正式以独立身份征战国际赛事 。早期他们只是中北美及"},
    "海地": {"tier": "下游/新军", "fifa_zone": "FIFA#50", "group": "B", "coach": "塞巴斯蒂安·米格内 (Sebastien Migne)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯B组", "host_factor": 0, "confidence": "低", "dark_horse": "中", "expert_note": "海地国家男子足球队，绰号\\\"红蓝军团\\\"，是加勒比地区极具爆发力与战斗精神的足球力量，承载着这个岛国在困境中永不言弃的国家意志。球队以出众的身体素质、极其纯粹的个人突击能力以及极具压迫性的乱战打法著称，在北美赛场常能凭借其不可预测的进攻爆发力给强队制造麻烦。\\n\\n球队历史荣光璀璨，曾在20世纪70年代书写过加勒比足球的辉煌：海地队历史上最伟大的时刻是在1973年夺得中北美及加勒比锦标赛冠军，并借此成功杀入1974年世界杯决赛圈，成为历史上继古巴之后第二支进入世界杯的加勒比球队。在那届杯赛中，他"},
    "沙特阿拉伯": {"tier": "下游/新军", "fifa_zone": "FIFA#51", "group": "F", "coach": "乔治·多尼斯 (Georgios Donis)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯F组", "host_factor": 0, "confidence": "低", "dark_horse": "低", "expert_note": "沙特阿拉伯国家男子足球队&zwnj;，绰号\\\"绿隼\\\"，由沙特阿拉伯足球联合会管理，是亚洲足坛的传统强队之一，现FIFA世界排名第&zwnj;61位&zwnj;。沙特队是亚洲杯历史上最成功的球队之一，曾&zwnj;三次夺冠&zwnj;（&zwnj;1984年、1988年、1996年&zwnj;），是首支实现亚洲杯两连冠的队伍。自1984年首次参赛以来，沙特&zwnj;从未缺席任何一届亚洲杯正赛&zwnj;，展现了极强的稳定性。\\n\\n沙特的足球运动员身体素质与南美、非洲球员相近，他们灵活快速、柔"},
    "厄瓜多尔": {"tier": "下游/新军", "fifa_zone": "FIFA#52", "group": "H", "coach": "塞巴斯蒂安贝卡 (Sebastian Beccacece)", "style": "待补充", "weakness": "待补充", "qual_path": "2026世界杯H组", "host_factor": 0, "confidence": "低", "dark_horse": "低", "expert_note": "厄瓜多尔国家男子足球队以其顽强的防守和独特的\\\"高原主场\\\"优势闻名，绰号\\\"高原杀手\\\" 。目前世界排名第23位，是南美足坛近年崛起的新锐力量，以钢铁防线与高效反击为核心风格。在2026年世界杯南美区预选赛中，球队展现了惊人的韧性，即便被扣除3分开局，最终仍以29分的高分力压巴西、乌拉圭等传统豪强，以南美区第二名的身份强势晋级 。\\n\\n这是厄瓜多尔队史第6次参加世界杯正赛。球队曾在2006年德国世界杯上创造历史，小组赛力压波兰和哥斯达黎加，历史性地首次闯入16强 。在美洲杯赛场上，他们也曾在"},
}
def get_expert_analysis(home_team, away_team, home_win_pct, draw_pct, away_win_pct, upset_risk, motivation):
    """基于专家数据库(piaosuo)生成专业赛事分析"""
    h = EXPERT_DB.get(home_team, {})
    a = EXPERT_DB.get(away_team, {})
    
    if not h or not a:
        partial_h = bool(h)
        partial_a = bool(a)
        if not partial_h and not partial_a:
            return {"summary": "球队数据不足，分析基于纯数学模型。", "confidence_level": "资料不足", "tier_gap": "", "home_coach": "", "away_coach": "", "home_group": "", "away_group": ""}
        elif not partial_h:
            h = {"tier": "未知", "coach": "未知", "group": "?", "style": "", "weakness": "", "confidence": "低", "dark_horse": "?", "host_factor": 0, "expert_note": ""}
        else:
            a = {"tier": "未知", "coach": "未知", "group": "?", "style": "", "weakness": "", "confidence": "低", "dark_horse": "?", "host_factor": 0, "expert_note": ""}
    
    host_bonus = h.get("host_factor", 0)
    tier_scores = {"世界顶级": 10, "欧洲一线": 8, "二档强队": 6, "中游球队": 4, "下游/新军": 2, "未知": 3}
    h_score = tier_scores.get(h.get("tier", "未知"), 3)
    a_score = tier_scores.get(a.get("tier", "未知"), 3)
    
    if h.get("confidence") == "高" and a.get("confidence") == "高":
        reliability = "较高-双方数据充分(piaosuo数据库)"
    elif h.get("confidence") == "低" or a.get("confidence") == "低":
        reliability = "较低-至少一方数据不足"
    else:
        reliability = "中等-基于piaosuo数据库"
    
    host_note = ""
    if host_bonus > 0:
        host_note = f"{home_team}作为2026世界杯东道主，享有显著主场优势(+{host_bonus}%加成)。"
    
    key_matchup = ""
    h_style = str(h.get("style", ""))
    a_style = str(a.get("style", ""))
    if h_style and a_style:
        if "身体" in h_style and "速度" in a_style:
            key_matchup = "关键对位：主队身体优势 vs 客队速度反击"
        elif "技术" in h_style and "身体" in a_style:
            key_matchup = "关键对位：主队技术控制 vs 客队身体对抗"
        elif "防守" in h_style and "进攻" not in str(h.get("weakness","")):
            key_matchup = "关键对位：主队稳固防守 vs 客队攻坚能力"
        else:
            key_matchup = "关键对位：双方风格差异明显，临场战术决定胜负"
    
    h_kp = h.get("key_players", [])
    a_kp = a.get("key_players", [])
    if isinstance(h_kp, list) and len(h_kp) > 0:
        h_players = "、".join(h_kp[:2])
    else:
        h_players = h.get("coach", "数据不足")
    if isinstance(a_kp, list) and len(a_kp) > 0:
        a_players = "、".join(a_kp[:2])
    else:
        a_players = a.get("coach", "数据不足")
    key_players_note = f"主队主帅：{h_players}；客队主帅：{a_players}"
    
    x_factors = []
    if h.get("dark_horse") in ("中", "高"):
        x_factors.append(f"{home_team}有黑马潜质")
    if a.get("dark_horse") in ("中", "高"):
        x_factors.append(f"{away_team}有黑马潜质")
    if upset_risk >= 2:
        x_factors.append("存在冷门风险")
    if motivation >= 4:
        x_factors.append("双方战意充足，比赛强度高")
    
    if home_win_pct >= 65:
        verdict = f"较稳判断：{home_team}实力+数据双重支持，主胜是大概率事件。"
    elif home_win_pct >= 50:
        verdict = f"倾向判断：{home_team}略占优但优势有限，需防平局。"
    elif away_win_pct >= 65:
        verdict = f"较稳判断：{away_team}实力占优，客胜概率高。"
    elif away_win_pct >= 50:
        verdict = f"倾向判断：{away_team}略占优但客场作战存在变数。"
    else:
        verdict = "不确定：双方实力接近，任何结果都可能发生，建议观望。"
    if upset_risk >= 3:
        verdict += " 冷门风险高，建议谨慎重注。"
    
    return {
        "summary": h.get('expert_note','') + ' | ' + a.get('expert_note',''),
        "host_note": host_note, "tier_gap": f"{home_team}({h.get('tier','?')}) vs {away_team}({a.get('tier','?')})",
        "key_matchup": key_matchup, "key_players": key_players_note,
        "x_factors": "；".join(x_factors) if x_factors else "无明显X因素",
        "reliability": reliability, "verdict": verdict,
        "home_style": h.get("style", ""), "away_style": a.get("style", ""),
        "home_weakness": h.get("weakness", ""), "away_weakness": a.get("weakness", ""),
        "home_pre_qual": h.get("qual_path", ""), "away_pre_qual": a.get("qual_path", ""),
        "home_host_bonus": host_bonus,
        "home_coach": h.get("coach", ""), "away_coach": a.get("coach", ""),
        "home_group": h.get("group", ""), "away_group": a.get("group", ""),
        "home_fifa": h.get("fifa_zone", ""), "away_fifa": a.get("fifa_zone", ""),
    }

def poisson_pmf(k, lam):
    if k < 0 or lam <= 0:
        return 0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def poisson_cdf(k, lam):
    return sum(poisson_pmf(i, lam) for i in range(k + 1))

def compute_score_matrix(lam_home, lam_away, max_goals=7):
    matrix = {}
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_pmf(h, lam_home) * poisson_pmf(a, lam_away)
            matrix[f"{h}-{a}"] = prob
    return matrix

def compute_total_goals(lam_home, lam_away, max_goals=7):
    tg = {}
    max_total = max_goals * 2
    for n in range(max_total + 1):
        prob = 0
        for h in range(min(n, max_goals) + 1):
            a = n - h
            if 0 <= a <= max_goals:
                prob += poisson_pmf(h, lam_home) * poisson_pmf(a, lam_away)
        tg[n] = prob
    return tg

def compute_half_full(lam_home, lam_away):
    half_lam_h = lam_home * 0.44
    half_lam_a = lam_away * 0.44
    full_lam_h = lam_home * 0.56
    full_lam_a = lam_away * 0.56

    h_home_win = 1 - poisson_cdf(0, half_lam_h) * (1 - poisson_cdf(1, half_lam_a)) - sum(poisson_pmf(i, half_lam_h) * poisson_pmf(i, half_lam_a) for i in range(6))
    h_draw = sum(poisson_pmf(i, half_lam_h) * poisson_pmf(i, half_lam_a) for i in range(6))
    h_away_win = 1 - h_home_win - h_draw

    f_home_win = 1 - poisson_cdf(0, full_lam_h + half_lam_h) * (1 - poisson_cdf(1, full_lam_a + half_lam_a)) - sum(poisson_pmf(i, full_lam_h + half_lam_h) * poisson_pmf(i, full_lam_a + half_lam_a) for i in range(7))
    f_draw = sum(poisson_pmf(i, full_lam_h + half_lam_h) * poisson_pmf(i, full_lam_a + half_lam_a) for i in range(7))
    f_away_win = 1 - f_home_win - f_draw

    half_p = {"胜": max(0.25, min(0.60, h_home_win)), "平": max(0.15, min(0.45, h_draw)), "负": max(0.15, min(0.55, h_away_win))}
    full_p = {"胜": max(0.2, min(0.65, f_home_win)), "平": max(0.1, min(0.40, f_draw)), "负": max(0.15, min(0.60, f_away_win))}

    total_h = sum(half_p.values())
    total_f = sum(full_p.values())
    half_p = {k: v / total_h for k, v in half_p.items()}
    full_p = {k: v / total_f for k, v in full_p.items()}

    combinations = [
        ("胜胜", half_p["胜"] * full_p["胜"]),
        ("胜平", half_p["胜"] * full_p["平"]),
        ("胜负", half_p["胜"] * full_p["负"]),
        ("平胜", half_p["平"] * full_p["胜"]),
        ("平平", half_p["平"] * full_p["平"]),
        ("平负", half_p["平"] * full_p["负"]),
        ("负胜", half_p["负"] * full_p["胜"]),
        ("负平", half_p["负"] * full_p["平"]),
        ("负负", half_p["负"] * full_p["负"]),
    ]
    total = sum(p for _, p in combinations)
    return [(name, p / total) for name, p in combinations]

# ==================== 六爻预测 ====================
HEXAGRAM_NAMES = {
    "111111": "乾为天", "000000": "坤为地", "010001": "水雷屯", "100010": "山水蒙",
    "010111": "水天需", "111010": "天水讼", "000010": "地水师", "010000": "水地比",
    "110111": "风天小畜", "111011": "天泽履", "000111": "地天泰", "111000": "天地否",
    "111101": "天火同人", "101111": "火天大有", "000100": "地山谦", "001000": "雷地豫",
    "011001": "泽雷随", "100110": "山风蛊", "000011": "地泽临", "110000": "风地观",
    "101001": "火雷噬嗑", "100101": "山火贲", "100000": "山地剥", "000001": "地雷复",
    "111001": "天雷无妄", "100111": "山天大畜", "100001": "山雷颐", "011110": "泽风大过",
    "010010": "坎为水", "101101": "离为火", "011100": "泽山咸", "001110": "雷风恒",
    "111100": "天山遁", "001111": "雷天大壮", "101000": "火地晋", "000101": "地火明夷",
    "110101": "风火家人", "101011": "火泽睽", "010100": "水山蹇", "001010": "雷水解",
    "100011": "山泽损", "110001": "风雷益", "011111": "泽天夬", "111110": "天风姤",
    "000110": "地风升",
    "001001": "震为雷",
    "001011": "雷泽归妹",
    "001100": "雷山小过",
    "001101": "雷火丰",
    "010011": "水泽节",
    "010101": "水火既济",
    "010110": "水风井",
    "011000": "泽地萃",
    "011010": "泽水困",
    "011011": "兑为泽",
    "011101": "泽火革",
    "100100": "艮为山",
    "101010": "火水未济",
    "101100": "火山旅",
    "101110": "火风鼎",
    "110010": "风水涣",
    "110011": "风泽中孚",
    "110100": "风山渐",
    "110110": "巽为风",
}

HEXAGRAM_INTERP = {
    "乾为天": "大吉 · 刚健有力 · 主队气势如虹",
    "坤为地": "平稳 · 厚德载物 · 防守稳固",
    "水雷屯": "艰难 · 万事开头难 · 可能有冷门",
    "山水蒙": "朦胧 · 形势不明 · 需谨慎观望",
    "水天需": "等待 · 时机未到 · 不宜重注",
    "天水讼": "争议 · 可能有VAR介入 · 谨慎",
    "地水师": "统帅 · 客场有纪律 · 防守反击",
    "水地比": "亲附 · 主场优势明显",
    "风天小畜": "积蓄 · 小胜格局 · 小球倾向",
    "天泽履": "履险 · 实力接近 · 可能平局",
    "地天泰": "通泰 · 强队可期 · 大球倾向",
    "天地否": "闭塞 · 强队受阻 · 爆冷风险",
    "天火同人": "同心 · 团队协作好 · 整体发挥",
    "火天大有": "丰收 · 实力碾压 · 大胜可期",
    "地山谦": "谦逊 · 低调取胜 · 小胜格局",
    "雷地豫": "愉悦 · 状态良好 · 主导比赛",
    "泽雷随": "随和 · 顺其自然 · 正路赛果",
    "山风蛊": "腐败 · 内部问题 · 可能意外",
    "地泽临": "临近 · 状态上升 · 值得关注",
    "风地观": "观察 · 形势待定 · 不宜重注",
    "火雷噬嗑": "咬合 · 激烈对抗 · 可能有红牌",
    "山火贲": "装饰 · 表面华丽 · 实力虚高",
    "山地剥": "剥落 · 核心缺阵 · 实力下降",
    "地雷复": "回复 · 反弹可期 · 复苏信号",
    "天雷无妄": "无妄 · 意外难免 · 小注为宜",
    "山天大畜": "大畜 · 攻防俱佳 · 零封可能",
    "山雷颐": "颐养 · 稳健发挥 · 正路赛果",
    "泽风大过": "大过 · 超出预期 · 可能大比分",
    "坎为水": "坎险 · 防守大战 · 小球倾向",
    "离为火": "明亮 · 进攻足球 · 大球倾向",
    "泽山咸": "感应 · 配合默契 · 团队制胜",
    "雷风恒": "恒久 · 稳定发挥 · 强队可信",
    "天山遁": "退避 · 客场保守 · 小比分",
    "雷天大壮": "强壮 · 碾压之势 · 大胜可期",
    "火地晋": "前进 · 状态上升 · 值得看好",
    "地火明夷": "受伤 · 核心缺阵 · 实力受损",
    "风火家人": "和睦 · 主场氛围好 · 主场优势",
    "火泽睽": "分歧 · 盘口分歧 · 谨慎投注",
    "水山蹇": "艰难 · 客战不利 · 客场难胜",
    "雷水解": "解放 · 反弹可期 · 回暖信号",
    "山泽损": "损失 · 有伤停影响 · 实力打折",
    "风雷益": "增益 · 状态回升 · 值得关注",
    "泽天夬": "决断 · 强队可信 · 正路赛果",
    "天风姤": "邂逅 · 冷门潜伏 · 需防意外",
    "地风升": "上升 · 状态渐入佳境 · 值得关注",
    "震为雷": "震动 · 场上变数多 · 防意外",
    "雷泽归妹": "归妹 · 配合生疏 · 需谨慎",
    "雷山小过": "小过 · 略有偏差 · 小球倾向",
    "雷火丰": "丰满 · 进攻盛宴 · 大球可期",
    "水泽节": "节制 · 节奏缓慢 · 小球格局",
    "水火既济": "既济 · 圆满收官 · 正路赛果",
    "水风井": "井卦 · 稳定发挥 · 中规中矩",
    "泽地萃": "聚集 · 强队可信 · 正路赛果",
    "泽水困": "困境 · 强队遇阻 · 防冷门",
    "兑为泽": "喜悦 · 状态放松 · 主场优势",
    "泽火革": "变革 · 战术调整 · 变数大",
    "艮为山": "静止 · 防守稳固 · 小比分",
    "火水未济": "未济 · 功亏一篑 · 需防逆转",
    "火山旅": "旅途 · 客战不利 · 客场难胜",
    "火风鼎": "鼎新 · 状态更新 · 回暖信号",
    "风水涣": "涣散 · 军心不稳 · 意外可能",
    "风泽中孚": "诚信 · 稳定发挥 · 正路可期",
    "风山渐": "渐进 · 逐步走强 · 值得看好",
    "巽为风": "柔顺 · 以柔克刚 · 技术制胜",
}

def generate_liuyao(match_name, home_team="", away_team=""):
    lines = []
    for i in range(6):
        coin = [random.randint(0, 1) for _ in range(3)]
        heads = sum(coin)
        if heads == 3:
            lines.append("1")
        elif heads == 2:
            lines.append("1")
        elif heads == 1:
            lines.append("0")
        else:
            lines.append("0")
    code = "".join(reversed(lines))
    name = HEXAGRAM_NAMES.get(code, f"卦{code}")
    interp = HEXAGRAM_INTERP.get(name, "卦象平和 · 正路为主")
    
    yaos = ["━━━" if l == "1" else "━ ━" for l in reversed(lines)]
    yao_labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    
    yang_count = code.count("1")
    yin_count = code.count("0")
    yang_ratio = yang_count / 6.0

    if yang_ratio >= 0.67:
        wdl_pred = f"卦象刚健，{home_team or '主队'}气势占优，看好主胜"
        wdl_dir = "主胜"
    elif yang_ratio <= 0.33:
        wdl_pred = f"卦象柔顺，{away_team or '客队'}暗藏杀机，倾向客胜"
        wdl_dir = "客胜"
    else:
        wdl_pred = "阴阳平衡，双方势均力敌，平局概率较高"
        wdl_dir = "平局"

    pred_home_goals = max(0, min(5, round(yang_count * 0.6 + random.uniform(-0.5, 0.5))))
    pred_away_goals = max(0, min(4, round(yin_count * 0.55 + random.uniform(-0.5, 0.5))))
    score_pred = f"{pred_home_goals}-{pred_away_goals}"
    score_range = f"{max(0,pred_home_goals-1)}-{pred_away_goals} 至 {min(5,pred_home_goals+1)}-{min(4,pred_away_goals+1)}"

    total_goals = pred_home_goals + pred_away_goals
    if total_goals <= 1:
        tg_pred = f"{total_goals}球（小球格局，防守为主）"
    elif total_goals <= 3:
        tg_pred = f"{total_goals}球（中等进球数）"
    else:
        tg_pred = f"{total_goals}球（大球倾向，进攻激烈）"

    half_home = max(0, round(pred_home_goals * 0.45))
    half_away = max(0, round(pred_away_goals * 0.4))
    if half_home > half_away:
        half_result = "胜"
    elif half_home < half_away:
        half_result = "负"
    else:
        half_result = "平"

    if wdl_dir == "主胜":
        hf_pred = "胜胜" if half_result == "胜" else ("平胜" if half_result == "平" else "负胜（逆转取胜）")
    elif wdl_dir == "客胜":
        hf_pred = "负负" if half_result == "负" else ("平负" if half_result == "平" else "胜负（被逆转）")
    else:
        hf_pred = "平平（全场胶着）"

    if "大吉" in interp or "通泰" in interp or "丰收" in interp or "强壮" in interp:
        luck = "大吉 ⭐⭐⭐⭐⭐"
    elif "平稳" in interp or "积蓄" in interp or "亲附" in interp:
        luck = "吉 ⭐⭐⭐⭐"
    elif "艰难" in interp or "闭塞" in interp or "争议" in interp:
        luck = "凶 ⭐⭐"
    elif "朦胧" in interp or "等待" in interp or "腐败" in interp or "剥落" in interp:
        luck = "大凶 ⭐"
    else:
        luck = "中平 ⭐⭐⭐"

    return {
        "name": name, "code": code, "interpretation": interp, "luck": luck,
        "yaos": yaos, "yao_labels": yao_labels, "lines": list(reversed(lines)),
        "wdl_pred": wdl_pred, "wdl_dir": wdl_dir,
        "score_pred": score_pred, "score_range": score_range,
        "tg_pred": tg_pred, "hf_pred": hf_pred,
    }

# ==================== 主数据生成 ====================
def generate_matches():
    # ??14:00??????????
    tomorrow = datetime.now() + timedelta(days=1)
    match_date = tomorrow.strftime("%Y-%m-%d")

    # ?????????(UTC+8) - 6.19??
    matches_data = [
        {"home": "捷克", "away": "南非", "league": "世界杯预选赛附加赛", "time": "00:00", "lam_h": 1.72, "lam_a": 1.48, "strength_h": 6.5, "strength_a": 5.5, "motivation": 4, "form": "近5场2胜2平1负 进7失5", "h2h": "首次交锋，捷克主场"},
        {"home": "瑞士", "away": "波黑", "league": "世界杯预选赛欧洲区", "time": "03:00", "lam_h": 2.06, "lam_a": 1.30, "strength_h": 7.5, "strength_a": 5.0, "motivation": 4, "form": "近5场3胜1平1负 进9失3", "h2h": "历史交锋瑞士占优(3胜1平)"},
        {"home": "加拿大", "away": "卡塔尔", "league": "世界杯预选赛", "time": "06:00", "lam_h": 1.58, "lam_a": 1.42, "strength_h": 6.0, "strength_a": 5.0, "motivation": 3, "form": "近5场2胜2平1负 进5失4", "h2h": "实力接近，主场略优"},
        {"home": "墨西哥", "away": "韩国", "league": "世界杯预选赛", "time": "09:00", "lam_h": 1.80, "lam_a": 1.55, "strength_h": 6.5, "strength_a": 6.0, "motivation": 4, "form": "近5场2胜2平1负 进6失4", "h2h": "墨西哥主场强势(近10场8胜)"},
    ]
    matches_data.sort(key=lambda x: x["time"])

    results = []
    for m in matches_data:
        prior_h = m["lam_h"]
        prior_a = m["lam_a"]

        wins = m["form"].count("胜")
        losses = m["form"].count("负")
        form_factor_h = 1.0 + (wins - losses) * 0.08

        lam_h_adj = prior_h * 0.40 + (prior_h * form_factor_h) * 0.60
        lam_a_adj = prior_a * 0.45 + (prior_a * (1.0 + (3 - wins + losses) * 0.06)) * 0.55

        # ????
        lam_h_adj *= 1.08
        lam_a_adj *= 0.96

        # ????
        mot_factor_h = 0.85 + m["motivation"] * 0.04
        lam_h_adj *= mot_factor_h

        # H2H??
        if "占优" in m["h2h"]:
            lam_h_adj *= 1.05
            lam_a_adj *= 0.95

        # ??????2026?????????
        host_bonus_pct = 0
        if m["home"] in ("???", "???"):
            host_bonus_pct = 12
            lam_h_adj *= 1.12
            lam_a_adj *= 0.94
        if m["away"] in ("???", "???"):
            host_bonus_pct = -12
            lam_a_adj *= 1.12
            lam_h_adj *= 0.94

        score_matrix = compute_score_matrix(lam_h_adj, lam_a_adj)
        total_goals = compute_total_goals(lam_h_adj, lam_a_adj)
        half_full = compute_half_full(lam_h_adj, lam_a_adj)

        home_win = sum(v for k, v in score_matrix.items() if int(k.split("-")[0]) > int(k.split("-")[1]))
        draw = sum(v for k, v in score_matrix.items() if int(k.split("-")[0]) == int(k.split("-")[1]))
        away_win = sum(v for k, v in score_matrix.items() if int(k.split("-")[0]) < int(k.split("-")[1]))
        total = home_win + draw + away_win
        home_win_pct = round(home_win / total * 100, 1)
        draw_pct = round(draw / total * 100, 1)
        away_win_pct = round(away_win / total * 100, 1)

        max_dir = max(("主胜", home_win_pct), ("平局", draw_pct), ("客胜", away_win_pct), key=lambda x: x[1])
        direction = max_dir[0]
        confidence = min(95, max(30, max_dir[1] * 0.7 + m["motivation"] * 8))
        confidence = round(confidence)

        prob_margin = abs(home_win_pct - away_win_pct)
        strength_diff = abs(m["strength_h"] - m["strength_a"])
        if prob_margin < 8 or (m["motivation"] <= 2 and direction == "主胜"):
            upset_risk = 3
            hot_level = "低"
        elif prob_margin < 15 or strength_diff < 1.5:
            upset_risk = 2
            hot_level = "中"
        else:
            upset_risk = 1
            hot_level = "高"

        sorted_scores = sorted([{"score": k, "prob": round(v * 100, 2)} for k, v in score_matrix.items() if v > 0.001], key=lambda x: x["prob"], reverse=True)[:12]
        sorted_goals = sorted([{"goals": k, "prob": round(v * 100, 2)} for k, v in total_goals.items() if v > 0.001], key=lambda x: x["prob"], reverse=True)[:10]
        sorted_hf = sorted([{"result": name, "prob": round(p * 100, 2)} for name, p in half_full], key=lambda x: x["prob"], reverse=True)

        battle_score = round(m["motivation"] / 5 * 100)
        odds_score = round(home_win_pct * 0.4 + (100 - home_win_pct) * 0.1)
        form_score = round(70 if "胜" in m["form"] else 50)
        composite_score = round(battle_score * 0.40 + odds_score * 0.35 + form_score * 0.25)

        lam_diff = m["lam_h"] - m["lam_a"]
        base_handicap = round(lam_diff * 4) / 4
        if base_handicap > 0:
            handicap_label = f"??{abs(base_handicap):.2f}"
            handicap_num = -base_handicap
        elif base_handicap < 0:
            handicap_label = f"??{abs(base_handicap):.2f}"
            handicap_num = -base_handicap
        else:
            handicap_label = "平手"
            handicap_num = 0
        adj_home = m["lam_h"] + handicap_num
        h_cover = 0
        for k in range(8):
            for j in range(k + (1 if handicap_num < 0 else 0), 8):
                if j >= 0:
                    h_cover += poisson_pmf(k, adj_home) * poisson_pmf(j, m["lam_a"])
        h_push = sum(poisson_pmf(k, adj_home) * poisson_pmf(k + max(0, int(handicap_num)), m["lam_a"]) for k in range(7))
        total_h = h_cover + h_push
        h_fail = max(0, 1 - total_h)
        total_h2 = h_cover + h_push + h_fail
        handicap_probs = {"cover": round(h_cover/total_h2, 2) if total_h2 > 0 else 0.5, "push": round(h_push/total_h2, 2) if total_h2 > 0 else 0.1, "fail": round(h_fail/total_h2, 2) if total_h2 > 0 else 0.4}

        liuyao = generate_liuyao(f"{m['home']} vs {m['away']}", m['home'], m['away'])

        # ????
        expert = get_expert_analysis(m["home"], m["away"], home_win_pct, draw_pct, away_win_pct, upset_risk, m["motivation"])

        match_result = {
            "home_team": m["home"], "away_team": m["away"],
            "league": m["league"], "time": m["time"] + " (北京时间)",
            "date": match_date, "direction": direction, "confidence": confidence,
            "hot_level": hot_level, "upset_risk": upset_risk,
            "handicap": handicap_label,
            "handicap_probs": handicap_probs,
            "pre_match": {"win": home_win_pct, "draw": draw_pct, "lose": away_win_pct, "top_scores": sorted_scores[:3]},
            "lambda": {"home": round(lam_h_adj, 2), "away": round(lam_a_adj, 2)},
            "lambda_prior": {"home": prior_h, "away": prior_a},
            "bayesian": {"prior_weight": 0.40, "likelihood_weight": 0.60, "form_factor": round(form_factor_h, 2)},
            "strength": {"home": m["strength_h"], "away": m["strength_a"]},
            "motivation": m["motivation"], "form": m["form"], "h2h": m["h2h"],
            "score_matrix": sorted_scores, "total_goals": sorted_goals, "half_full": sorted_hf,
            "composite_score": composite_score, "battle_score": battle_score,
            "odds_score": odds_score, "form_score": form_score, "liuyao": liuyao,
            "expert_analysis": expert,
        }
        results.append(match_result)

        # 记录预测到历史追踪
    if HISTORY_AVAILABLE:
        for r in results:
            try:
                record_prediction(match_date, r["home_team"], r["away_team"], r["direction"], r["confidence"])
            except:
                pass
    
    # 尝试获取实时赔率
    odds_data = None
    if ODDS_AVAILABLE:
        try:
            odds_data = get_cached_odds(max_age=600)
        except:
            pass
    
    return {"date": match_date, "matches": results, "odds": odds_data}

def generate_picks(matches):
    picks = []
    for m in matches:
        pm = m["pre_match"]
        wdl = [("主胜", pm["win"]), ("平局", pm["draw"]), ("客胜", pm["lose"])]
        best_wdl = max(wdl, key=lambda x: x[1])
        picks.append({"m": f"{m['home_team']} vs {m['away_team']}", "play": "胜平负", "pick": best_wdl[0], "prob": round(best_wdl[1]/100, 4), "odds": round(1.0/(best_wdl[1]/100*0.92), 2), "dir": m["direction"], "conf": m["confidence"], "upset": m["upset_risk"], "details": [{"pick": p[0], "prob": round(p[1],1), "odds": round(1.0/(p[1]/100*0.92), 2)} for p in wdl]})

        score_details = [{"score": s["score"], "prob": s["prob"], "odds": round(1.0/(s["prob"]/100*0.92*0.85),2)} for s in m["score_matrix"][:12]]
        best_score = m["score_matrix"][0]
        picks.append({"m": f"{m['home_team']} vs {m['away_team']}", "play": "比分", "pick": best_score["score"], "prob": round(best_score["prob"]/100,4), "odds": round(1.0/(best_score["prob"]/100*0.92*0.85),2), "dir": m["direction"], "conf": m["confidence"], "upset": m["upset_risk"], "details": score_details})

        goal_details = [{"goals": f"{g['goals']}球", "prob": g["prob"], "odds": round(1.0/(g["prob"]/100*0.92*0.88),2)} for g in m["total_goals"]]
        best_goal = m["total_goals"][0]
        picks.append({"m": f"{m['home_team']} vs {m['away_team']}", "play": "总进球", "pick": f"{best_goal['goals']}球", "prob": round(best_goal["prob"]/100,4), "odds": round(1.0/(best_goal["prob"]/100*0.92*0.88),2), "dir": m["direction"], "conf": m["confidence"], "upset": m["upset_risk"], "details": goal_details})

        hf_details = [{"result": h["result"], "prob": h["prob"], "odds": round(1.0/(h["prob"]/100*0.92*0.82),2)} for h in m["half_full"]]
        best_hf = m["half_full"][0]
        picks.append({"m": f"{m['home_team']} vs {m['away_team']}", "play": "半全场", "pick": best_hf["result"], "prob": round(best_hf["prob"]/100,4), "odds": round(1.0/(best_hf["prob"]/100*0.92*0.82),2), "dir": m["direction"], "conf": m["confidence"], "upset": m["upset_risk"], "details": hf_details})
    return picks


def generate_mixed_parlays(picks, matches, n=3):
    """生成混合串关：2关+3关组合"""
    result = {"2+3混合": []}
    single_picks = [p for p in picks if p.get("conf", 0) >= 45]
    if len(single_picks) < 3:
        return result
    
    # 选2关+3关组合
    for i in range(min(3, len(single_picks)-2)):
        for j in range(i+1, min(6, len(single_picks)-1)):
            for k in range(j+1, min(8, len(single_picks))):
                combo_3 = [single_picks[i], single_picks[j], single_picks[k]]
                prob_3 = combo_3[0]["prob"] * combo_3[1]["prob"] * combo_3[2]["prob"]
                odds_3 = combo_3[0]["odds"] * combo_3[1]["odds"] * combo_3[2]["odds"]
                result["2+3混合"].append({
                    "type": "3串1",
                    "desc": f"{combo_3[0]['m']} + {combo_3[1]['m']} + {combo_3[2]['m']}",
                    "prob": prob_3,
                    "odds": round(odds_3, 2),
                    "picks": [p["pick"] for p in combo_3],
                })
                if len(result["2+3混合"]) >= 4:
                    break
            if len(result["2+3混合"]) >= 4:
                break
        if len(result["2+3混合"]) >= 4:
            break
    
    return result


def generate_parlays(picks, n, min_count=1):
    from itertools import combinations as comb
    wdl = [p for p in picks if p["play"] == "胜平负"]
    if len(wdl) < n:
        return []
    results = []
    for combo in comb(wdl, n):
        prob = 1.0
        odds = 1.0
        descs = [c["pick"] for c in combo]
        for c in combo:
            prob *= c["prob"]
            odds *= c["odds"]
        results.append({"ms": [{"m": c["m"], "pick": c["pick"], "prob": c["prob"], "odds": c["odds"]} for c in combo], "prob": round(prob, 6), "odds": round(odds, 2), "desc": " | ".join(descs)})
    results.sort(key=lambda x: x["prob"] * x["odds"], reverse=True)
    return results[:min(10, len(results))]

# ==================== 数据缓存 ====================
_cached_data = None
_cache_time = None
_cache_lock = threading.Lock()

def get_cached_data():
    global _cached_data, _cache_time
    now = datetime.now()
    with _cache_lock:
        if _cached_data is None or _cache_time is None or (now - _cache_time).total_seconds() > 1800:
            matches_data = generate_matches()
            picks_data = generate_picks(matches_data["matches"])
            parlays_data = {}
            for n in [1, 2, 3, 4]:
                parlays_data[f"{n}串1"] = generate_parlays(picks_data, n)
            _cached_data = {"matches": matches_data["matches"], "picks": picks_data, "parlays": parlays_data, "mixed_parlays": generate_mixed_parlays(picks_data, matches_data["matches"]), "date": matches_data["date"], "odds": matches_data.get("odds")}
            _cache_time = now
    return dict(_cached_data)

def daily_refresh_thread():
    while True:
        time.sleep(60)
        now = datetime.now()
        if now.hour == 14 and now.minute == 0:
            # Regenerate standalone HTML with fresh data
            try:
                import json as _json
                mdata = generate_matches()
                pdata = generate_picks(mdata["matches"])
                pldata = {}
                for _n in [1,2,3,4]:
                    pldata[f"{_n}x1"] = generate_parlays(pdata, _n)
                full = {"matches": mdata["matches"], "picks": pdata, "parlays": pldata, "date": mdata["date"]}
                rpath = os.path.join(os.path.dirname(__file__), "standalone.html")
                if os.path.exists(rpath):
                    with open(rpath, "r", encoding="utf-8") as _f:
                        _html = _f.read()
                    _new_data = "var EMBEDDED_DATA = " + _json.dumps(full, ensure_ascii=False) + ";"
                    import re as _re
                    _html = _re.sub(r"var EMBEDDED_DATA = \{[\s\S]*?\};", _new_data, _html)
                    with open(rpath, "w", encoding="utf-8") as _f:
                        _f.write(_html)
            except:
                pass
            with _cache_lock:
                global _cached_data, _cache_time
                _cached_data = None
                _cache_time = None
            get_cached_data()

# ==================== Flask Routes ====================
@app.route("/")
def index():
    import os as _os
    report_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "standalone.html")
    if _os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        # Fallback: try relative to CWD
        alt_path = "standalone.html"
        if _os.path.exists(alt_path):
            with open(alt_path, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            html = "<html><body><h1>Report not found</h1><p>Path: "+report_path+"</p></body></html>"
    from flask import Response
    resp = Response(html, status=200, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # Explicitly set correct Content-Length
    return resp
@app.route("/api/matches")
def api_matches():
    data = get_cached_data()
    return jsonify({"matches": data["matches"], "date": data["date"]})

@app.route("/api/picks")
def api_picks():
    data = get_cached_data()
    return jsonify({"picks": data["picks"], "matches": data["matches"], "date": data["date"]})

@app.route("/api/full")
def api_full():
    data = get_cached_data()
    return jsonify(data)


# ==================== 赔率API ====================
@app.route("/api/odds")
def api_odds():
    """获取实时赔率"""
    if not ODDS_AVAILABLE:
        return jsonify({"error": "赔率模块不可用", "status": "unavailable"})
    odds = get_cached_odds()
    return jsonify(odds or {"status": "fetching", "message": "正在获取赔率数据..."})

# ==================== 历史追踪API ====================
@app.route("/api/history/stats")
def api_history_stats():
    """获取预测准确率统计"""
    if not HISTORY_AVAILABLE:
        return jsonify({"error": "历史模块不可用"})
    return jsonify(get_stats())

@app.route("/api/history/recent")
def api_history_recent():
    """获取最近预测记录"""
    if not HISTORY_AVAILABLE:
        return jsonify([])
    n = request.args.get('n', 10, type=int)
    return jsonify(get_recent_predictions(n))

@app.route("/api/history/record", methods=["POST"])
def api_record_result():
    """记录实际比赛结果"""
    if not HISTORY_AVAILABLE:
        return jsonify({"error": "历史模块不可用"})
    data = request.get_json() or {}
    home = data.get("home", "")
    away = data.get("away", "")
    result = data.get("result", "")
    if home and away and result:
        updated = update_actual_result(home, away, result)
        return jsonify({"updated": updated, "stats": get_stats()})
    return jsonify({"error": "参数不完整"})



# ==================== 自学习API ====================
@app.route("/api/learn/review")
def api_learn_review():
    """触发复盘学习"""
    if not LEARNER_AVAILABLE:
        return jsonify({"error": "自学习模块不可用"})
    result = review_and_learn()
    return jsonify(result)

@app.route("/api/learn/status")
def api_learn_status():
    """获取学习状态"""
    if not LEARNER_AVAILABLE:
        return jsonify({"error": "自学习模块不可用", "weights": {"prior_weight": 0.40, "likelihood_weight": 0.60}})
    return jsonify(get_learning_status())



# ========== V5 Additional Routes ==========

@app.route("/api/hercules")
def api_hercules():
    """??????????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    lh = float(request.args.get("lh", 1.5))
    la = float(request.args.get("la", 1.5))
    if not home or not away:
        return jsonify({"error": "??home?away??"})
    result = run_prediction(home, away, lh, la)
    return jsonify(result)

@app.route("/api/experts")
def api_experts():
    """??????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    lh = float(request.args.get("lh", 1.5))
    la = float(request.args.get("la", 1.5))
    if not home or not away:
        return jsonify({"error": "??home?away??"})
    result = run_all_experts(home, away, lh, la)
    return jsonify(result)

@app.route("/api/features")
def api_features():
    """??????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if not home or not away:
        return jsonify({"error": "??home?away??"})
    result = get_all_features(home, away)
    return jsonify(result)

@app.route("/api/liuyao")
def api_liuyao():
    """????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if not home or not away:
        return jsonify({"error": "??home?away??"})
    result = generate_hexagram(home, away)
    return jsonify(result)

@app.route("/api/fusion")
def api_fusion():
    """????"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    lh = float(request.args.get("lh", 1.5))
    la = float(request.args.get("la", 1.5))
    if home and away:
        from fusion import fuse_prediction
        result = fuse_prediction(home, away, lh, la)
        return jsonify(result)
    return jsonify({"error": "??home?away??"})

@app.route("/api/news")
def api_news():
    """????"""
    return jsonify(get_news_feed())

@app.route("/api/news/refresh")
def api_news_refresh():
    """????"""
    items = fetch_news()
    return jsonify({"count": len(items), "items": items})

@app.route("/api/titan007")
def api_titan():
    """Titan007??"""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if home and away:
        return jsonify(titan.get_full_match_data(home, away))
    return jsonify({"odds": titan.fetch_odds(), "standings": titan.fetch_standings()})

@app.route("/api/roi")
def api_roi():
    """???/????"""
    stats = roi_tracker.get_stats()
    return jsonify(stats)

@app.route("/api/roi/place", methods=["POST"])
def api_roi_place():
    """AI????"""
    data = request.get_json(force=True) if request.data else {}
    result = roi_tracker.place_bet(data)
    return jsonify(result)

@app.route("/api/betting/plan")
def api_betting_plan():
    """??????"""
    budget = float(request.args.get("budget", 100))
    risk = request.args.get("risk", "stable")
    result = generate_full_betting_plan(budget, risk)
    return jsonify(result)

@app.route("/api/auto_analysis")
def api_auto_analysis():
    """??????"""
    result = analyst.get_daily_report()
    return jsonify(result)

@app.route("/api/learn/history")
def api_learn_history():
    """?????"""
    limit = int(request.args.get("limit", 20))
    history = learner.history[-limit:]
    return jsonify({"history": history, "total": len(learner.history)})

@app.route("/api/learn/stats")
def api_learn_stats():
    """?????"""
    return jsonify(learner.get_stats())

# Auto-load data on import (for gunicorn)
get_cached_data()
refresh_thread = threading.Thread(target=daily_refresh_thread, daemon=True)
refresh_thread.start()

if __name__ == "__main__":
    print("⚽ 足彩分析助手已启动: http://127.0.0.1:5000")
    print("📅 每日14:00自动刷新次日赛程（北京时间）")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

