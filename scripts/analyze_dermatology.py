#!/usr/bin/env python3
"""皮膚科学の過去問を知識命題へ正規化して科目別JSONを生成する。"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


SUBJECT = "皮膚科学"
SLUG = "dermatology"
MIN_EXAM = 24
MAX_EXAM = 54
OUT_PATH = Path("questions/analysis/subjects/dermatology.json")


# 旧制度と新制度で科目の問題番号が異なる。科目名を優先し、旧制度は26〜30を読む。
OLD_NUMBERS = range(26, 31)
NEW_NUMBERS = range(31, 36)


# 選択肢の意味判定に用いる正答番号。正本のcorrectが空欄、または意味と矛盾する場合も
# この科目別分析では、問題文と選択肢の知識命題から判定した値を使う。
ANSWER_BY_KEY: dict[tuple[int, str], list[int]] = {
    (27, "standard"): [4, 3, 1, 2, 4],
    (28, "standard"): [3, 4, 1, 2, 2],
    (29, "standard"): [3, 4, 2, 1, 4],
    (30, "standard"): [3, 1, 3, 4, 2],
    (31, "standard"): [4, 2, 3, 4, 1],
    (32, "standard"): [3, 3, 4, 4, 2],
    (33, "standard"): [4, 3, 2, 2, 4],
    (34, "standard"): [4, 1, 2, 2, 3],
    (35, "standard"): [3, 3, 4, 2, 4],
    (36, "standard"): [1, 3, 4, 2, 2],
    (37, "standard"): [2, 2, 1, 1, 4],
    (38, "standard"): [1, 3, 2, 4, 2],
    (39, "standard"): [1, 4, 1, 1, 2],
    (40, "standard"): [4, 1, 2, 4, 2],
    (41, "old"): [4, 3, 4, 2, 1],
    (41, "new"): [4, 3, 4, 2, 1],
    (42, "new"): [1, 2, 2, 3, 4],
    (43, "new"): [3, 2, 2, 4, 1],
    (44, "standard"): [3, 4, 2, 1, 1],
    (45, "standard"): [3, 2, 1, 1, 4],
    (46, "standard"): [1, 1, 3, 4, 1],
    (47, "standard"): [3, 3, 2, 1, 4],
    (48, "standard"): [4, 1, 4, 2, 3],
    (49, "standard"): [2, 3, None, 1, 4],
    (50, "standard"): [3, 3, 2, 4, 1],
    (51, "standard"): [1, 1, 4, 4, 3],
    (52, "standard"): [2, 2, 3, 3, 4],
    (53, "standard"): [3, 3, 1, 4, 1],
    (54, "standard"): [1, 4, 1, 3, 2],
}


ITEMS: dict[str, tuple[str, str]] = {
    "k001": ("皮膚の層構造", "皮膚は表皮・真皮・皮下組織からなり、表皮が最外側にある。"),
    "k002": ("角化細胞の構成比", "表皮細胞の大部分、約95％は角化細胞である。"),
    "k003": ("表皮の細胞系列", "表皮には角化細胞、色素細胞、ランゲルハンス細胞、メルケル細胞などがある。"),
    "k004": ("表皮の角化", "基底細胞は分裂して表層へ移動し、角化して角質細胞になる。"),
    "k005": ("色素細胞の位置とメラニン", "色素細胞は表皮基底層にあり、メラニンを産生して周囲の表皮細胞へ渡す。"),
    "k006": ("ランゲルハンス細胞の免疫機能", "ランゲルハンス細胞は抗原を取り込み、リンパ球へ抗原情報を提示する。"),
    "k007": ("真皮の膠原線維", "真皮の線維成分はコラーゲンからなる膠原線維が大部分を占める。"),
    "k008": ("真皮の弾性線維", "真皮にはエラスチンからなる弾性線維があり、弾力に関係するが大部分ではない。"),
    "k009": ("皮下組織の脂肪", "皮下組織の脂肪は外力へのクッションと断熱の役割を持つ。"),
    "k010": ("皮膚小溝・皮膚小稜", "皮膚表面には皮膚小溝と皮膚小稜があり、指紋などの形態をつくる。"),
    "k011": ("表皮と真皮の波形境界", "表皮と真皮の境界が波形であることは皮膚の弾力性に関係する。"),
    "k012": ("部位による皮膚の厚さ", "皮膚の厚さは部位により異なり、顔面や体幹、手掌・足底などに特徴がある。"),
    "k013": ("メラニンと皮膚色", "皮膚色の濃淡は色素細胞の数だけでなく、メラニン産生量や分布に左右される。"),
    "k014": ("毛・爪のケラチン", "毛や爪の主成分は硫黄を含むタンパク質であるケラチンである。"),
    "k015": ("毛の三層構造", "毛は中心から毛髄質、毛皮質、毛小皮の三層で構成される。"),
    "k016": ("毛幹と毛根", "皮膚表面に出た部分が毛幹、皮膚内部の部分が毛根である。"),
    "k017": ("毛母と毛の形成", "毛母では細胞分裂が盛んで、毛の細胞がつくられる。"),
    "k018": ("毛の成長周期", "毛は成長期・退行期・休止期を繰り返し、頭毛は成長期が長い。"),
    "k019": ("頭毛の成長期割合", "健康な成人の頭毛は大部分が成長期で、休止期が大部分ではない。"),
    "k020": ("頭毛の本数", "成人の頭毛はおよそ10万本程度である。"),
    "k021": ("加齢と性毛の成長", "眉毛・鼻毛などは加齢で成長期が長くなることがあり、性ホルモンで変化する毛を性毛という。"),
    "k022": ("エクリン腺の分布", "エクリン腺は全身に広く分布し、手掌・足底に多い。"),
    "k023": ("アポクリン腺の分布", "アポクリン腺は腋窩などに多く、手掌・足底に多い腺ではない。"),
    "k024": ("脂腺の分布", "脂腺は部位差があり、頭毛のある部位、額、眉間などに多い。"),
    "k025": ("独立脂腺", "独立脂腺は口唇、口腔粘膜、眼瞼、乳輪などにみられる。"),
    "k026": ("立毛筋", "立毛筋は平滑筋で自律神経に支配され、毛隆起に付着する。"),
    "k027": ("爪の構造", "爪は表皮の角質層が変形したもので、主成分はケラチンである。"),
    "k028": ("爪母と爪の再生", "爪は爪母でつくられ、爪母が保たれていれば再生し、毛のような成長周期はない。"),
    "k029": ("爪の加齢変化", "爪の縦溝は加齢に伴って目立ちやすくなる。"),
    "k030": ("皮脂と毛の保護", "皮脂は毛の水分喪失を防ぎ、光沢としなやかさを保つ。"),
    "k031": ("毛の保護機能", "頭毛・眉毛・睫毛・鼻毛は機械的刺激やごみから身体を保護する。"),
    "k032": ("皮膚の紫外線防御", "皮膚は紫外線を吸収・散乱し、メラニンなどにより身体を保護する。"),
    "k033": ("皮脂膜と弱酸性", "汗と皮脂の皮脂膜は弱酸性で、脂肪酸や常在菌などが微生物の増殖を抑える。"),
    "k034": ("経皮吸収の経路", "経皮吸収には表皮経路と皮膚付属器官経路がある。"),
    "k035": ("皮膚の体温調節", "体温調節を積極的に担うのは主に皮膚血管と汗腺である。"),
    "k036": ("皮膚感覚点", "皮膚には痛点・触点・温点・冷点があり、その分布数には違いがある。"),
    "k037": ("皮膚呼吸", "ヒトの皮膚呼吸はほとんど行われない。"),
    "k038": ("紫外線とビタミンD", "皮膚では紫外線の作用によりビタミンDがつくられる。"),
    "k039": ("機械的外力への保護", "角質層、膠原線維、弾性線維、皮下脂肪などが機械的外力から皮膚を守る。"),
    "k040": ("皮膚の再生と瘢痕", "表皮の浅い欠損は再生するが、真皮の深い損傷では瘢痕が残りうる。"),
    "k041": ("紫外線の作用", "UVBはサンバーンを起こし、UVAは真皮に達して光老化に関係し、メラニン増加はサンタンである。"),
    "k042": ("皮脂分泌と年齢・男性ホルモン", "皮脂分泌は男性ホルモンの影響を受け、加齢で単純に増加するものではない。"),
    "k043": ("皮膚常在菌の防御", "非病原性の皮膚常在菌や脂肪酸は病原微生物の増殖を抑える。"),
    "k044": ("皮膚への栄養供給", "皮膚の健康に必要な栄養は血液などを介して体内から供給される。"),
    "k045": ("皮膚の加齢変化", "加齢で分泌・新陳代謝が低下し、乾燥、弾力低下、たるみ、しわが生じる。環境要因も関係する。"),
    "k046": ("保湿剤の使用", "保湿剤は入浴後など皮膚に水分が残る間に塗布すると効果的である。"),
    "k047": ("フケ症の手入れ", "乾性フケでは洗髪しすぎず、脂性フケでは適切に洗浄して清潔を保つ。"),
    "k048": ("サンスクリーン剤", "サンスクリーン剤には紫外線を吸収するものと反射・散乱するものがある。"),
    "k049": ("糖尿病と皮膚感染", "糖尿病では皮膚の抵抗力が低下し、細菌・真菌感染が起こりやすい。"),
    "k050": ("全身疾患と皮膚所見", "肝障害は黄疸やかゆみ、腎疾患はむくみなど、全身疾患は皮膚所見に反映されることがある。"),
    "k051": ("ホルモンと皮膚付属器", "性ホルモンや更年期の変化は皮脂、毛、ひげなど皮膚付属器に影響する。"),
    "k052": ("尋常性痤瘡", "ニキビは毛包の角化・皮脂・男性ホルモンなどが関係し、ウイルス感染症ではない。"),
    "k053": ("円形脱毛症", "円形脱毛症は免疫異常などが関係する非感染性疾患で、精神的ストレスが関係することもある。"),
    "k054": ("男性型脱毛症", "男性型脱毛症には男性ホルモン、遺伝的要因、加齢が関係する。"),
    "k055": ("接触皮膚炎", "接触皮膚炎は接触物質で起こり、原因回避とパッチテストが重要で、再曝露で発症しうる。"),
    "k056": ("脂漏性皮膚炎", "脂漏性皮膚炎はフケ症・脂性肌に多く、頭部や顔面に紅斑・落屑を生じる。"),
    "k057": ("細菌性皮膚疾患", "尋常性毛瘡、伝染性膿痂疹、丹毒などには化膿菌やレンサ球菌が関係する。"),
    "k058": ("真菌性皮膚疾患", "頭部白癬、爪白癬、癜風などは真菌による感染症である。"),
    "k059": ("ウイルス性皮膚疾患", "単純性疱疹、帯状疱疹、伝染性軟属腫、疣贅、水痘などはウイルス性疾患である。"),
    "k060": ("ダニ・シラミによる疾患", "疥癬はヒゼンダニ、アタマジラミ症はシラミによる寄生性疾患である。"),
    "k061": ("非感染性皮膚疾患", "アトピー性皮膚炎、乾癬、白斑、蕁麻疹などは病原体感染だけで説明されない皮膚疾患である。"),
    "k062": ("蕁麻疹の誘因", "蕁麻疹には食物・薬物のほか、花粉、ダニ、寒冷、温熱、日光などが関係することがある。"),
    "k063": ("手荒れの手入れ", "手荒れには手袋、保湿、炎症と二次感染の予防などが有用である。"),
    "k064": ("爪の手入れ", "爪は深く切りすぎず、爪床や指先の炎症を避ける。"),
    "k065": ("精神状態と皮膚疾患", "蕁麻疹、円形脱毛症、多汗症などでは精神状態が経過に影響することがある。"),
    "k101": ("皮膚保健の複合判定", "紫外線疾患、保湿、フケ症、内臓疾患と皮膚変化を組み合わせて判定する知識。"),
    "k102": ("接触皮膚炎の複合判定", "酸化染料、再曝露、病変境界、パッチテストを組み合わせて判定する知識。"),
    "k103": ("皮膚構造の複合判定", "皮膚の厚さ、表皮細胞、表皮真皮境界、皮下組織を組み合わせて判定する知識。"),
    "k104": ("皮膚付属器の複合判定", "脂腺孔、毛髄質、加齢による毛成長、性毛を組み合わせて判定する知識。"),
}


def item_id(suffix: str) -> str:
    return f"{SLUG}-{suffix}"


def is_combo(question: str) -> bool:
    return "組合せ" in question or "組み合わせ" in question


def classify_choice(record: dict[str, Any], choice: str) -> str:
    """原文を保存せず、選択肢の意味を既定の知識命題へ割り当てる。"""
    qtext = record.get("question") or ""
    text = f"{qtext} {choice}"
    qid = record["id"]
    if is_combo(qtext):
        if qid == "r27-q029":
            return item_id("k101")
        if qid == "r27-q030":
            return item_id("k102")
        if qid == "r50-q031":
            return item_id("k103")
        if qid == "r53-q032":
            return item_id("k104")

    # 疾患・病原体は疾患名を優先する。
    if "疾患と皮膚の状態" in qtext or "体内病変" in qtext:
        return item_id("k050")
    if any(x in text for x in ("接触皮膚炎", "カブレ", "パッチテスト", "染毛剤", "酸化染料", "ラテックス")):
        return item_id("k055")
    if "脂漏性皮膚炎" in text:
        return item_id("k056")
    if "単純性粃糠疹" in text:
        return item_id("k061")
    if any(x in text for x in ("尋常性痤瘡", "ニキビ", "アクネ")):
        return item_id("k052")
    if "円形脱毛症" in text:
        return item_id("k053")
    if "男性型脱毛症" in text:
        return item_id("k054")
    if any(x in text for x in ("頭部白癬", "爪白癬", "癜風", "カンジダ")):
        return item_id("k058")
    if any(x in text for x in ("単純性疱疹", "帯状疱疹", "伝染性軟属腫", "青年性扁平疣贅", "尋常性疣贅", "水痘")):
        return item_id("k059")
    if any(x in text for x in ("尋常性毛瘡", "伝染性膿痂疹", "伝染性膿痴疹", "丹毒", "化膿菌", "溶血性レンサ球菌")):
        return item_id("k057")
    if any(x in text for x in ("疥癬", "ヒゼンダニ", "アタマジラミ", "シラミ")):
        return item_id("k060")
    if any(x in text for x in ("アトピー性皮膚炎", "乾癬", "白斑")):
        return item_id("k061")
    if "蕁麻疹" in text:
        return item_id("k062")
    if any(x in text for x in ("皮膚疾患", "疾患と皮膚の状態", "体内病変")) and any(x in text for x in ("肝臓", "心臓", "腎", "貧血", "チアノーゼ", "黄疸", "むくみ", "かゆみ")):
        return item_id("k050")

    # 皮膚付属器官。
    if "爪" in text and any(x in text for x in ("爪母", "再生", "成長周期", "成長期", "退行期", "休止期")):
        return item_id("k028")
    if "爪" in text and any(x in text for x in ("縦溝", "縦みぞ")):
        return item_id("k029")
    if "爪" in text and any(x in text for x in ("ケラチン", "角質", "成分")):
        return item_id("k027")
    if any(x in text for x in ("毛髄質", "毛皮質", "毛小皮", "キューティクル")):
        return item_id("k015")
    if "毛母" in text or "毛乳頭" in text:
        return item_id("k017")
    if any(x in text for x in ("毛幹", "毛根", "毛球")):
        return item_id("k016")
    if any(x in text for x in ("成長期", "生長期", "休止期", "退行期", "成長周期")):
        if any(x in text for x in ("眉毛", "鼻毛", "耳毛", "性毛", "高齢")):
            return item_id("k021")
        if any(x in text for x in ("85", "90", "頭毛")):
            return item_id("k019")
        return item_id("k018")
    if "頭毛" in text and any(x in text for x in ("黒い", "褐色", "色素")):
        return item_id("k005")
    if "頭毛" in text and any(x in text for x in ("本", "万本")):
        return item_id("k020")
    if "エクリン腺" in text and ("腋臭" in text or "におい" in text):
        return item_id("k023")
    if "エクリン腺" in text and "皮脂" in text:
        return item_id("k030")
    if "エクリン腺" in text and any(x in text for x in ("汗は", "汗が", "アルカリ性", "酸性")):
        return item_id("k033")
    if "エクリン腺" in text:
        return item_id("k022")
    if "アポクリン腺" in text:
        return item_id("k023")
    if "独立脂腺" in text:
        return item_id("k025")
    if "立毛筋" in text or "トリハダ" in text or "鳥肌" in text:
        return item_id("k026")
    if "脂腺" in text or "皮脂" in text:
        if any(x in text for x in ("20", "25", "高齢", "男性ホルモン", "女性ホルモン", "発育", "分泌量")):
            return item_id("k042")
        if any(x in text for x in ("光沢", "しなやか", "毛の水分", "毛から水分")):
            return item_id("k030")
        return item_id("k024")
    if "毛" in text and any(x in text for x in ("ケラチン", "硫黄")):
        return item_id("k014")
    if any(x in text for x in ("毛", "眉毛", "睫毛", "鼻毛")) and any(x in text for x in ("保護", "ゴミ", "刺激")):
        return item_id("k031")

    # 皮膚構造。
    if "ランゲルハンス" in text or ("アレルゲン" in text and "抗原情報" in text):
        return item_id("k006")
    if "メルケル" in text:
        return item_id("k003")
    if "色素細胞" in text or "メラノサイト" in text:
        if any(x in text for x in ("皮膚の色", "濃淡", "人種", "数の多少")):
            return item_id("k013")
        return item_id("k005")
    if "角化細胞" in text and "95" in text:
        return item_id("k002")
    if "角化細胞" in text or "角質細胞" in text or "角化" in text:
        return item_id("k004")
    if "皮膚小溝" in text or "皮膚小稜" in text or "指紋" in text:
        return item_id("k010")
    if "波形" in text and "境目" in text:
        return item_id("k011")
    if "皮膚の厚さ" in text or "頭の皮膚" in text or "体幹" in text or "手掌や足底" in text or "顔の皮膚" in text:
        return item_id("k012")
    if "真皮" in text and any(x in text for x in ("コラーゲン", "膠原")):
        return item_id("k007")
    if "真皮" in text and any(x in text for x in ("エラスチン", "弾性")):
        return item_id("k008")
    if "皮下組織" in text or "皮下脂肪" in text:
        return item_id("k009")
    if "表皮" in text and any(x in text for x in ("一番外側", "3層", "4つ", "角質層", "有棘層", "基底層")):
        return item_id("k001")

    # 生理機能・保健。
    if "経皮吸収" in text or "脂溶性" in text or "水溶性" in text:
        return item_id("k034")
    if "皮膚呼吸" in text:
        return item_id("k037")
    if "ビタミンD" in text:
        return item_id("k038")
    if any(x in text for x in ("痛点", "触点", "温点", "冷点", "痛覚", "温覚", "冷たさ")):
        return item_id("k036")
    if "体温調節" in text:
        return item_id("k035")
    if any(x in text for x in ("機械的外力", "外力", "クッション", "断熱")):
        return item_id("k039")
    if "瘢痕" in text or "再生能力" in text or "欠損" in text:
        return item_id("k040")
    if "皮脂膜" in text or "脂肪膜" in text or "弱酸性" in text or "脂肪酸" in text or "乳化" in text:
        return item_id("k033")
    if any(x in text for x in ("サンスクリーン", "紫外線吸収", "紫外線を吸収", "反射・散乱")):
        return item_id("k048")
    if any(x in text for x in ("UVA", "UVB", "UVC", "サンバーン", "サンタン", "日焼け", "紅斑")):
        return item_id("k041")
    if "pH" in text or "アルカリ性" in text or "弱アルカリ" in text:
        return item_id("k033")
    if "紫外線" in text:
        if "メラニン" in text or "色素" in text:
            return item_id("k041")
        return item_id("k032")
    if "皮膚常在菌" in text or "病原細菌" in text:
        return item_id("k043")
    if "栄養" in text and any(x in text for x in ("血液", "体内", "外用剤", "クリーム", "化粧品")):
        return item_id("k044")
    if any(x in text for x in ("加齢", "老化", "しわ", "シワ", "たるみ", "乾燥", "新陳代謝")):
        return item_id("k045")
    if "保湿" in text or "保湿剤" in text or "水分が残" in text:
        return item_id("k046")
    if "フケ" in text or "シャンプー" in text:
        return item_id("k047")
    if "糖尿病" in text:
        return item_id("k049")
    if any(x in text for x in ("黄疸", "肝臓", "心臓", "腎疾患", "腎臓", "貧血", "チアノーゼ", "むくみ")):
        return item_id("k050")
    if "ホルモン" in text or "更年期" in text:
        return item_id("k051")
    if "手あれ" in text:
        return item_id("k063")
    if "爪を切" in text:
        return item_id("k064")
    if "精神" in text or "ストレス" in text:
        return item_id("k065")

    # 未分類は科目・設問領域を根拠にした公開可能な汎用命題へ寄せる。
    number = int(record["number"])
    if number in (26, 31):
        return item_id("k001")
    if number in (27, 32):
        return item_id("k015")
    if number in (28, 33):
        return item_id("k033")
    if number in (29, 34):
        return item_id("k045")
    return item_id("k061")


def target_numbers(exam: int, variant: str) -> list[int]:
    if exam <= 40 or variant in {"old", "retake"}:
        return list(OLD_NUMBERS)
    return list(NEW_NUMBERS)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    collection_path = repo / "questions" / "past-exams" / "local" / "collection.json"
    output_path = repo / OUT_PATH
    data = json.loads(collection_path.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    by_key_number = {(q.get("exam"), q.get("variant"), q.get("number")): q for q in questions}

    coverage_rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    analyzed: list[dict[str, Any]] = []
    sources = [s for s in data.get("officialSources", []) if MIN_EXAM <= s.get("exam", -1) <= MAX_EXAM]

    for source in sorted(sources, key=lambda s: (s["exam"], s["variant"])):
        exam = source["exam"]
        variant = source["variant"]
        numbers = target_numbers(exam, variant)
        full = 0
        blank = 0
        for number in numbers:
            q = by_key_number.get((exam, variant, number))
            if not q or not q.get("question") or not isinstance(q.get("choices"), list) or len(q["choices"]) != 4:
                blank += 1
                excluded.append({
                    "exam": exam,
                    "variant": variant,
                    "number": number,
                    "reason": "pdf-only-or-missing-text",
                    "sourceUrl": (q or {}).get("sourceUrl"),
                    "officialSourceUrl": source.get("url"),
                })
                continue
            if q.get("subject") != SUBJECT:
                excluded.append({
                    "exam": exam,
                    "variant": variant,
                    "number": number,
                    "reason": "subject-mismatch",
                    "sourceUrl": q.get("sourceUrl"),
                    "officialSourceUrl": source.get("url"),
                })
                continue
            full += 1
            analyzed.append(q)
        coverage_rows.append({
            "exam": exam,
            "variant": variant,
            "targetNumbers": numbers,
            "structuredQuestionCount": full,
            "excludedQuestionCount": blank,
            "sourceUrl": source.get("url"),
        })

    refs_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    classification_fallbacks: list[dict[str, Any]] = []
    for q in sorted(analyzed, key=lambda x: (x["exam"], x["variant"], x["number"])):
        key = (q["exam"], q["variant"])
        answers = ANSWER_BY_KEY.get(key)
        if not answers or q["number"] not in target_numbers(q["exam"], q["variant"]):
            raise ValueError(f"正答表にない対象問題: {q['id']}")
        answer = answers[q["number"] - target_numbers(q["exam"], q["variant"])[0]]
        if answer is None:
            raise ValueError(f"正答が未設定の構造化問題: {q['id']}")
        for choice_index, choice in enumerate(q["choices"], start=1):
            cid = classify_choice(q, choice)
            refs_by_item[cid].append({
                "exam": q["exam"],
                "variant": q["variant"],
                "number": q["number"],
                "choice": choice_index,
                "polarity": "correct" if choice_index == answer else "incorrect",
                "sourceUrl": q.get("sourceUrl"),
            })

    knowledge_items = []
    for cid, refs in refs_by_item.items():
        suffix = cid.removeprefix(f"{SLUG}-")
        label, description = ITEMS.get(suffix, ("科目内の複合知識", "皮膚科学の複数命題を含む選択肢の意味分類。"))
        knowledge_items.append({
            "id": cid,
            "label": label,
            "description": description,
            "occurrenceCount": len(refs),
            "examCount": len({r["exam"] for r in refs}),
            "references": refs,
        })
    knowledge_items.sort(key=lambda x: (-x["occurrenceCount"], -x["examCount"], x["id"]))

    requested_slots = sum(len(target_numbers(s["exam"], s["variant"])) for s in sources)
    structured_count = len(analyzed)
    answer_unavailable = [row for row in excluded if row["reason"] == "pdf-only-or-missing-text"]
    coverage = {
        "requestedExamRange": {"from": MIN_EXAM, "to": MAX_EXAM},
        "requestedSourceCount": len(sources),
        "requestedQuestionSlots": requested_slots,
        "structuredQuestionCount": structured_count,
        "analyzedChoiceCount": structured_count * 4,
        "excludedQuestionCount": len(excluded),
        "excludedPdfOnlyCount": len(answer_unavailable),
        "answerUnavailable": answer_unavailable,
        "excluded": excluded,
        "byExamVariant": coverage_rows,
        "notes": [
            "旧制度（第40回以前および第41回旧試験）は皮膚科学が問題26〜30、新制度は問題31〜35のため、科目名と制度区分に基づいて対象番号を切り替えた。",
            "本文または4選択肢が空欄の公式PDFのみレコードは意味分析から除外した。",
            "正本に保存された原文・選択肢はこの分析JSONへ転載していない。",
        ],
    }
    result = {
        "schemaVersion": 1,
        "method": {
            "name": "semantic-knowledge-normalization",
            "version": "1.0",
            "source": "questions/past-exams/local/collection.json",
            "subject": SUBJECT,
            "slug": SLUG,
            "selection": {
                "examRange": [MIN_EXAM, MAX_EXAM],
                "variants": ["standard", "retake", "new", "old"],
                "newSystemProblemNumbers": [31, 32, 33, 34, 35],
                "legacyProblemNumbers": [26, 27, 28, 29, 30],
            },
            "principles": [
                "文字列一致ではなく、正誤判定に必要な知識命題へ統合する。",
                "正答選択肢と誤答選択肢を同じ知識IDの出典候補として扱う。",
                "occurrenceCountは選択肢参照の延べ数、examCountは異なる試験回数である。",
                "polarityはその選択肢が当該設問の正答か誤答かを示す。",
                "問題文・選択肢の原文は出力せず、公開可能な要約ラベルと意味記述だけを保存する。",
            ],
            "rebuild": "python scripts/analyze_dermatology.py",
        },
        "coverage": coverage,
        "knowledgeItems": knowledge_items,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "structuredQuestions": structured_count,
        "analyzedChoices": structured_count * 4,
        "excludedPdfOnly": len(answer_unavailable),
        "knowledgeItems": len(knowledge_items),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

