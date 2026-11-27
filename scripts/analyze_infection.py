#!/usr/bin/env python3
"""感染症（問題16〜20）の意味分類JSONを再生成する。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SUBJECT = "感染症"
SLUG = "infection"
QUESTION_NUMBERS = {16, 17, 18, 19, 20}
EXAM_MIN = 24
EXAM_MAX = 54


def k(label: str, meaning: str, topics: list[str]) -> dict[str, object]:
    return {"label": label, "meaning": meaning, "topics": topics}


KNOWLEDGE = {
    "infection-bacteria-flagella": k("細菌の鞭毛", "一部の細菌は鞭毛を使って運動する。", ["病原体", "細菌"]),
    "infection-bacteria-nucleic-acids": k("細菌の核酸", "細菌はDNAとRNAをもつ細胞性微生物である。", ["病原体", "細菌"]),
    "infection-bacteria-anaerobic-growth": k("嫌気性細菌", "一部の細菌は酸素があると発育できない。", ["病原体", "細菌"]),
    "infection-bacteria-endospores": k("細菌の芽胞形成", "一部の細菌は環境が悪化すると芽胞を形成する。", ["病原体", "細菌"]),
    "infection-endospore-resistance": k("芽胞の抵抗性", "芽胞は熱や乾燥などに強い抵抗性を示す。", ["病原体", "細菌"]),
    "infection-bacteria-binary-fission": k("細菌の増殖", "細菌は基本的に二分裂で増殖する。", ["病原体", "細菌"]),
    "infection-bacteria-composition": k("細菌の構成成分", "細菌菌体は水分が大部分を占め、固形成分ではタンパク質が大きな割合を占める。", ["病原体", "細菌"]),
    "infection-bacteria-free-living-growth": k("細菌の細胞外増殖", "細菌は生きた宿主細胞内だけでなく、条件が整えば細胞外でも増殖できる。", ["病原体", "細菌"]),
    "infection-bacteria-oxygen-profile": k("細菌の酸素要求性", "百日せき菌・結核菌・破傷風菌・大腸菌は酸素要求性が異なり、破傷風菌は代表的な嫌気性菌である。", ["病原体", "細菌"]),
    "infection-virus-single-nucleic-acid": k("ウイルスの核酸", "ウイルスはDNAまたはRNAの一方を遺伝情報としてもつ。", ["病原体", "ウイルス"]),
    "infection-virus-live-cells": k("ウイルスの増殖", "ウイルスは生きた宿主細胞内でのみ増殖する。", ["病原体", "ウイルス"]),
    "infection-virus-structure": k("ウイルスの基本構造", "ウイルスは核酸と、それを保護するタンパク質の殻を基本構造とする。", ["病原体", "ウイルス"]),
    "infection-virus-mutation": k("ウイルスの変異", "ウイルスは変異を起こし、性質が変化することがある。", ["病原体", "ウイルス"]),
    "infection-bacteria-mutation": k("細菌の変異", "細菌の変異は性質の獲得・喪失、病原性、形態などを変化させ得る。", ["病原体", "細菌"]),
    "infection-microbe-drug-resistance": k("微生物の耐性獲得", "細菌などは変異等により化学療法剤や消毒剤への耐性を獲得することがある。", ["病原体", "耐性"]),
    "infection-infection-vs-disease": k("感染と発病の区別", "感染は病原体の侵入・発育増殖、発病は組織や臓器の病的変化であり、付着だけや感染後の発病は必須条件ではない。", ["感染概念"]),
    "infection-asymptomatic-infection": k("不顕性感染", "感染していても症状を示さない状態を不顕性感染という。", ["感染概念"]),
    "infection-opportunistic-infection": k("日和見感染", "宿主の抵抗力が低下したとき、通常は病原性の低い微生物でも発病することがある。", ["感染概念"]),
    "infection-persistent-infection": k("持続性感染", "病原体が長期間宿主と共存し続ける感染状態がある。", ["感染概念"]),
    "infection-vertical-infection": k("垂直感染", "母体から胎児・新生児へ病原体が伝わる感染を垂直感染という。", ["感染経路"]),
    "infection-route-oral": k("経口感染", "汚染された飲食物や水などを介する経口感染がある。", ["感染経路"]),
    "infection-route-blood-body-fluid": k("血液・体液感染", "血液や体液を介して感染する病原体がある。", ["感染経路"]),
    "infection-route-sexual": k("性行為による感染", "B型肝炎などは性行為を介して感染することがある。", ["感染経路"]),
    "infection-route-droplet": k("飛沫感染", "咳やくしゃみなどの飛沫を介する感染経路がある。", ["感染経路"]),
    "infection-route-airborne": k("空気・飛沫核感染", "結核、麻しん、水痘などは空気感染または飛沫核感染として扱われる。", ["感染経路"]),
    "infection-route-mosquito": k("蚊・節足動物媒介", "マラリア、デング熱、日本脳炎などは蚊などの節足動物が媒介する。", ["感染経路"]),
    "infection-route-soil": k("土壌を介する感染", "破傷風は土壌中の病原体が傷口などから侵入して感染する。", ["感染経路"]),
    "infection-route-contact-fomite": k("接触・汚染物品感染", "病原体で汚染されたタオルなどの物品を介する接触感染がある。", ["感染経路"]),
    "infection-route-vertical": k("胎盤を介する感染", "梅毒、風しんなどは母体から胎児へ胎盤を介して感染することがある。", ["感染経路"]),
    "infection-incubation-hepatitis-b": k("B型肝炎の潜伏期", "B型肝炎の潜伏期はおおむね1〜6か月である。", ["感染症各論", "潜伏期"]),
    "infection-incubation-aids": k("エイズの潜伏期", "HIV感染からエイズ発症までには長い期間があり、短い数日単位ではない。", ["感染症各論", "潜伏期"]),
    "infection-incubation-rubella": k("風しんの潜伏期", "風しんの潜伏期はおおむね2〜3週間である。", ["感染症各論", "潜伏期"]),
    "infection-incubation-ehec": k("腸管出血性大腸菌感染症の潜伏期", "腸管出血性大腸菌感染症の潜伏期はおおむね4〜8日である。", ["感染症各論", "潜伏期"]),
    "infection-incubation-measles": k("麻しんの潜伏期", "麻しんの潜伏期はおおむね10〜14日である。", ["感染症各論", "潜伏期"]),
    "infection-incubation-pertussis": k("百日せきの潜伏期", "百日せきの潜伏期はおおむね7〜10日である。", ["感染症各論", "潜伏期"]),
    "infection-pathogen-pertussis": k("百日せきの病原体", "百日せきの病原体は百日せき菌という細菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-hepatitis-b": k("B型肝炎の病原体", "B型肝炎の病原体はB型肝炎ウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-hepatitis-c": k("C型肝炎の病原体", "C型肝炎の病原体はC型肝炎ウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-rubella": k("風しんの病原体", "風しんの病原体は風しんウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-measles": k("麻しんの病原体", "麻しんの病原体は麻しんウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-tuberculosis": k("結核の病原体", "結核の病原体は結核菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-tetanus": k("破傷風の病原体", "破傷風の病原体は破傷風菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-malaria": k("マラリアの病原体", "マラリアの病原体はマラリア原虫である。", ["感染症各論", "病原体"]),
    "infection-pathogen-cholera": k("コレラの病原体", "コレラの病原体はコレラ菌という細菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-ehec": k("腸管出血性大腸菌感染症の病原体", "腸管出血性大腸菌感染症の病原体は毒素を産生する大腸菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-influenza": k("インフルエンザの病原体", "インフルエンザの病原体はインフルエンザウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-aids": k("エイズの病原体", "エイズの原因はヒト免疫不全ウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-dengue": k("デング熱の病原体", "デング熱の病原体はデングウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-syphilis": k("梅毒の病原体", "梅毒の病原体は梅毒トレポネーマという細菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-plague": k("ペストの病原体", "ペストの病原体は細菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-diphtheria": k("ジフテリアの病原体", "ジフテリアの病原体は細菌である。", ["感染症各論", "病原体"]),
    "infection-pathogen-anisakis": k("アニサキス症の病原体", "アニサキス症は蠕虫による寄生虫症である。", ["感染症各論", "病原体"]),
    "infection-pathogen-sars": k("SARSの病原体", "SARSの病原体はコロナウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-japanese-encephalitis": k("日本脳炎の病原体", "日本脳炎の病原体は日本脳炎ウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-polio": k("ポリオの病原体", "急性灰白髄炎の病原体はポリオウイルスである。", ["感染症各論", "病原体"]),
    "infection-pathogen-tsutsugamushi": k("ツツガムシ病の病原体", "ツツガムシ病の病原体はリケッチアである。", ["感染症各論", "病原体"]),
    "infection-prevention-principles": k("感染症予防の3原則", "感染源対策、感染経路対策、宿主の感受性対策の3つで整理する。", ["予防"]),
    "infection-prevention-school-closure": k("学校閉鎖の位置づけ", "学校・学級閉鎖は感染経路対策である。", ["予防"]),
    "infection-prevention-vector-control": k("媒介動物の駆除", "ネズミ・昆虫等の駆除は感染経路対策である。", ["予防"]),
    "infection-prevention-quarantine": k("検疫の位置づけ", "検疫は感染源対策として整理される。", ["予防"]),
    "infection-prevention-patient-treatment": k("患者の入院治療", "患者の入院治療は感染源対策である。", ["予防"]),
    "infection-prevention-vaccination-host": k("予防接種の位置づけ", "予防接種は宿主の感受性に関する対策である。", ["予防"]),
    "infection-vaccination-law": k("予防接種法の制度", "予防接種法に基づく定期・臨時接種、任意接種、A類・B類疾病などの制度区分がある。", ["予防", "制度"]),
    "infection-vaccination-schedule": k("予防接種の対象・回数", "接種対象年齢や接種回数は対象疾病により異なる。", ["予防", "制度"]),
    "infection-vaccination-herd-effect": k("予防接種の集団効果", "予防接種は個人の感染予防だけでなく、集団の流行抑制にも寄与する。", ["予防"]),
    "infection-vaccination-hiv-unavailable": k("HIVワクチン", "エイズを予防する実用化ワクチンはない。", ["予防", "感染症各論"]),
    "infection-employment-restriction": k("理容師の就業制限", "感染症法上、結核など一類・二類・三類等の感染症では理容業務の就業制限対象となり得る。", ["制度", "就業制限"]),
    "infection-tuberculosis-clinical-screening": k("結核の症状と早期発見", "結核では持続する咳・痰・微熱・寝汗などがみられ、健康診断で早期発見を図る。", ["感染症各論"]),
    "infection-tuberculosis-bcg": k("結核とBCG", "結核予防にはBCGワクチンが用いられ、定期接種は乳幼児を対象とする。", ["感染症各論", "予防"]),
    "infection-tuberculosis-extrapulmonary": k("結核の罹患部位", "結核は肺以外の臓器にも起こり得る。", ["感染症各論"]),
    "infection-tuberculosis-epidemiology": k("結核の疫学", "結核の新登録患者数や死亡状況を、極端に小さい人数・年齢層に置き換えない。", ["感染症各論", "疫学"]),
    "infection-measles-clinical": k("麻しんの症状", "麻しんは高熱、咳、結膜炎、全身に広がる発疹などを特徴とする。別名はしか。", ["感染症各論"]),
    "infection-measles-transmission": k("麻しんの感染力・経路", "麻しんは感染力が非常に強く、空気感染を起こす。", ["感染症各論", "感染経路"]),
    "infection-measles-vaccination": k("麻しんの予防接種", "麻しんは定期予防接種の対象である。", ["感染症各論", "予防"]),
    "infection-rubella-congenital": k("風しんと先天性風しん症候群", "妊婦の風しん感染は胎児の心疾患、白内障、難聴などにつながることがある。", ["感染症各論", "母子感染"]),
    "infection-hepatitis-b-vaccine-chronic": k("B型肝炎の予防と慢性化", "B型肝炎はワクチンで予防でき、持続性感染・慢性化が起こり得る。", ["感染症各論", "予防"]),
    "infection-ehec-virulence": k("腸管出血性大腸菌の特徴", "腸管出血性大腸菌はベロ毒素を産生し、熱に弱く、便を介した二次感染を起こし得る。", ["感染症各論"]),
    "infection-influenza-features": k("インフルエンザの特徴", "インフルエンザは季節性流行、飛沫・汚染物品による感染、重症肺炎、新型の世界的大流行などの特徴をもつ。", ["感染症各論"]),
    "infection-syphilis-course": k("梅毒の経過", "梅毒は未治療で長期に進行し、妊娠中は胎盤を介した先天梅毒を起こし得る。", ["感染症各論", "母子感染"]),
    "infection-covid19": k("COVID-19の感染・検査・予防", "COVID-19は発症前にも感染させ得て、嗅覚・味覚異常を呈することがあり、手洗いとPCR・抗原検査が対策となる。", ["感染症各論", "予防"]),
    "infection-normal-flora": k("常在細菌叢", "皮膚や粘膜には一定の細菌が定着している。", ["感染症各論"]),
    "infection-normal-flora-pathogenic": k("常在細菌叢と感染源", "常在細菌は条件により感染源となり得る。", ["感染症各論"]),
    "infection-normal-flora-beneficial": k("常在細菌叢の有益作用", "腸内細菌などにはビタミン産生など人体に有益な働きがある。", ["感染症各論"]),
    "infection-normal-flora-barrier": k("常在細菌叢の防御作用", "常在細菌叢は病原体の侵入を妨げる働きがある。", ["感染症各論"]),
    "infection-pertussis-clinical": k("百日せきの臨床像", "百日せきは乳幼児に多く、飛沫や汚染分泌物で感染し、潜伏期は通常1〜2か月ではない。", ["感染症各論"]),
    "infection-infection-control-handwashing": k("手洗い等の感染対策", "流水と石けんによる手洗い、手指消毒、予防接種などは感染対策となる。", ["予防"]),
    "infection-disinfection-definitions": k("殺菌・消毒・滅菌・防腐", "殺菌、病原微生物の感染力をなくす消毒、すべての微生物を除く滅菌、腐敗を防ぐ防腐を区別する。", ["消毒", "制度"]),
    "infection-disinfection-physical": k("理学的消毒法", "紫外線、煮沸、蒸気などの理学的消毒法は、対象物・温度・時間・照射条件で適用を判断する。", ["消毒"]),
    "infection-disinfection-heat": k("煮沸・蒸気消毒", "煮沸や蒸気は温度・時間・対象物の浸漬状態を満たして用い、芽胞や血液付着物への適用には限界がある。", ["消毒", "熱"]),
    "infection-disinfection-uv": k("紫外線消毒", "紫外線は表面に作用し、遮蔽・油膜・陰には届かず、目や皮膚への直接照射は有害である。", ["消毒", "紫外線"]),
    "infection-disinfection-chemical": k("化学的消毒法", "化学的消毒は薬剤の濃度、温度、時間、汚れ、対象物との適合性で効果が変わる。", ["消毒"]),
    "infection-disinfection-hypochlorite": k("次亜塩素酸ナトリウム", "次亜塩素酸ナトリウムは殺菌・漂白作用をもち、ウイルスにも有効だが、有機物・光・熱の影響や金属腐食に注意する。", ["消毒", "薬剤"]),
    "infection-disinfection-ethanol": k("消毒用エタノール", "消毒用エタノールは規定濃度で細菌・結核菌・多くのウイルスに有効だが、芽胞には無効である。", ["消毒", "薬剤"]),
    "infection-disinfection-reverse-soap": k("逆性石けん", "逆性石けんは規定濃度・時間で用い、普通石けんや有機物との混在で効果が低下し、芽胞・結核菌には適さない。", ["消毒", "薬剤"]),
    "infection-disinfection-amphoteric": k("両性界面活性剤", "両性界面活性剤は規定濃度・時間で用いるが、血液付着物や結核菌・芽胞への適用には制限がある。", ["消毒", "薬剤"]),
    "infection-disinfection-chlorhexidine": k("グルコン酸クロルヘキシジン", "グルコン酸クロルヘキシジンは栄養型細菌に有効だが、芽胞・結核菌への効果は乏しい。", ["消毒", "薬剤"]),
    "infection-disinfection-blood": k("血液付着物の消毒", "血液が付着した器具・布片には、対象物に応じて煮沸、規定濃度の次亜塩素酸ナトリウム、エタノール等を適用する。", ["消毒", "感染経路"]),
    "infection-disinfection-material": k("材質と消毒法", "プラスチック、革、毛、金属、布など材質に応じて、熱・紫外線・薬液の適否を選ぶ。", ["消毒"]),
    "infection-disinfection-concentration": k("消毒薬の希釈計算", "製剤濃度、使用量、最終液量から規定濃度を計算し、血液付着の有無に応じた濃度を選ぶ。", ["消毒", "制度"]),
    "infection-disinfection-change": k("消毒薬使用液の交換", "消毒薬使用液は薬剤の蒸発・分解・汚れの程度や法令上の期間に応じて交換する。", ["消毒", "制度"]),
    "infection-disinfection-regulation": k("理容師法施行規則の消毒", "皮膚に接する器具・布片の交換、客ごとの消毒、血液付着物への処理など、理容所の消毒基準を適用する。", ["消毒", "制度"]),
    "infection-microbe-resistance": k("病原微生物の抵抗性", "芽胞、結核菌、ウイルスなど病原微生物ごとに熱・薬剤・紫外線への抵抗性が異なる。", ["病原体", "消毒"]),
}


def setq(mapping: dict[str, dict[int, list[str]]], exam: int, variant: str, number: int, *choices: list[str]) -> None:
    mapping[f"{exam}:{variant}:{number}"] = {i + 1: choice for i, choice in enumerate(choices)}


MAPPING: dict[str, dict[int, list[str]]] = {}

# 第41〜43回（新）
setq(MAPPING, 41, "new", 16, ["infection-bacteria-flagella"], ["infection-bacteria-nucleic-acids"], ["infection-bacteria-anaerobic-growth"], ["infection-bacteria-endospores"])
setq(MAPPING, 41, "new", 17, ["infection-route-oral"], ["infection-route-mosquito", "infection-pathogen-malaria"], ["infection-route-soil", "infection-pathogen-tetanus"], ["infection-route-droplet", "infection-pathogen-pertussis"])
setq(MAPPING, 41, "new", 18, ["infection-prevention-school-closure"], ["infection-prevention-vector-control"], ["infection-prevention-vaccination-host"], ["infection-prevention-quarantine"])
setq(MAPPING, 41, "new", 19, ["infection-measles-clinical"], ["infection-measles-transmission"], ["infection-measles-clinical"], ["infection-measles-vaccination"])
setq(MAPPING, 41, "new", 20, ["infection-incubation-hepatitis-b"], ["infection-incubation-aids"], ["infection-incubation-rubella"], ["infection-incubation-ehec"])

setq(MAPPING, 42, "new", 16, ["infection-route-sexual", "infection-route-blood-body-fluid", "infection-pathogen-hepatitis-b"], ["infection-route-mosquito", "infection-pathogen-japanese-encephalitis"], ["infection-route-oral", "infection-pathogen-cholera"], ["infection-route-mosquito", "infection-pathogen-malaria"])
setq(MAPPING, 42, "new", 17, ["infection-bacteria-composition"], ["infection-bacteria-nucleic-acids"], ["infection-bacteria-free-living-growth"], ["infection-endospore-resistance"])
setq(MAPPING, 42, "new", 18, ["infection-prevention-school-closure"], ["infection-route-oral"], ["infection-prevention-vector-control"], ["infection-prevention-patient-treatment"])
setq(MAPPING, 42, "new", 19, ["infection-incubation-rubella"], ["infection-rubella-congenital"], ["infection-pathogen-rubella", "infection-route-droplet"], ["infection-vaccination-law"])
setq(MAPPING, 42, "new", 20, ["infection-route-oral", "infection-pathogen-ehec"], ["infection-ehec-virulence"], ["infection-incubation-ehec"], ["infection-ehec-virulence"])

setq(MAPPING, 43, "new", 16, ["infection-employment-restriction", "infection-pathogen-tuberculosis"], ["infection-measles-transmission"], ["infection-pathogen-tetanus"], ["infection-route-oral"])
setq(MAPPING, 43, "new", 17, ["infection-pathogen-polio", "infection-route-oral"], ["infection-pathogen-influenza", "infection-route-droplet"], ["infection-pathogen-aids", "infection-route-blood-body-fluid"], ["infection-pathogen-japanese-encephalitis", "infection-route-mosquito"])
setq(MAPPING, 43, "new", 18, ["infection-bacteria-endospores"], ["infection-endospore-resistance"], ["infection-pathogen-tuberculosis"], ["infection-bacteria-endospores"])
setq(MAPPING, 43, "new", 19, ["infection-tuberculosis-clinical-screening"], ["infection-tuberculosis-clinical-screening"], ["infection-tuberculosis-epidemiology"], ["infection-tuberculosis-bcg"])
setq(MAPPING, 43, "new", 20, ["infection-incubation-hepatitis-b"], ["infection-pathogen-hepatitis-b"], ["infection-route-blood-body-fluid"], ["infection-hepatitis-b-vaccine-chronic"])

# 第44〜54回
setq(MAPPING, 44, "standard", 16, ["infection-bacteria-binary-fission"], ["infection-virus-single-nucleic-acid"], ["infection-virus-live-cells"], ["infection-virus-mutation"])
setq(MAPPING, 44, "standard", 17, ["infection-normal-flora"], ["infection-normal-flora-pathogenic"], ["infection-normal-flora-beneficial"], ["infection-normal-flora-barrier"])
setq(MAPPING, 44, "standard", 18, ["infection-vaccination-law"], ["infection-vaccination-law"], ["infection-vaccination-schedule"], ["infection-vaccination-schedule"])
setq(MAPPING, 44, "standard", 19, ["infection-pathogen-japanese-encephalitis", "infection-route-mosquito"], ["infection-route-mosquito"], ["infection-route-contact-fomite"], ["infection-route-soil"])
setq(MAPPING, 44, "standard", 20, ["infection-incubation-hepatitis-b"], ["infection-route-blood-body-fluid"], ["infection-hepatitis-b-vaccine-chronic"], ["infection-hepatitis-b-vaccine-chronic"])

setq(MAPPING, 45, "standard", 16, ["infection-route-pertussis"], ["infection-route-airborne"], ["infection-route-blood-body-fluid"], ["infection-route-oral"])
setq(MAPPING, 45, "standard", 17, ["infection-bacteria-anaerobic-growth", "infection-virus-single-nucleic-acid"], ["infection-virus-single-nucleic-acid", "infection-endospore-resistance"], ["infection-endospore-resistance", "infection-virus-mutation"], ["infection-bacteria-anaerobic-growth", "infection-virus-mutation"])
setq(MAPPING, 45, "standard", 18, ["infection-infection-vs-disease"], ["infection-infection-vs-disease"], ["infection-infection-vs-disease"], ["infection-asymptomatic-infection"])
setq(MAPPING, 45, "standard", 19, ["infection-vaccination-law", "infection-vaccination-herd-effect"], ["infection-vaccination-herd-effect"], ["infection-vaccination-schedule"], ["infection-vaccination-law"])
setq(MAPPING, 45, "standard", 20, ["infection-measles-clinical"], ["infection-incubation-measles"], ["infection-pathogen-measles"], ["infection-measles-clinical"])

setq(MAPPING, 46, "standard", 16, ["infection-route-droplet", "infection-pathogen-pertussis"], ["infection-route-oral", "infection-pathogen-ehec"], ["infection-route-blood-body-fluid", "infection-pathogen-hepatitis-c"], ["infection-route-blood-body-fluid", "infection-pathogen-aids"])
setq(MAPPING, 46, "standard", 17, ["infection-bacteria-composition"], ["infection-endospore-resistance"], ["infection-bacteria-anaerobic-growth"], ["infection-bacteria-free-living-growth"])
setq(MAPPING, 46, "standard", 18, ["infection-bacteria-mutation"], ["infection-bacteria-mutation"], ["infection-microbe-drug-resistance"], ["infection-bacteria-mutation"])
setq(MAPPING, 46, "standard", 19, ["infection-infection-vs-disease"], ["infection-opportunistic-infection"], ["infection-asymptomatic-infection"], ["infection-incubation-pertussis"])
setq(MAPPING, 46, "standard", 20, ["infection-tuberculosis-epidemiology"], ["infection-route-airborne"], ["infection-tuberculosis-clinical-screening"], ["infection-tuberculosis-extrapulmonary"])

setq(MAPPING, 47, "standard", 16, ["infection-employment-restriction"], ["infection-employment-restriction"], ["infection-employment-restriction"], ["infection-employment-restriction"])
setq(MAPPING, 47, "standard", 17, ["infection-vaccination-law"], ["infection-vaccination-law"], ["infection-vaccination-herd-effect"], ["infection-vaccination-law"])
setq(MAPPING, 47, "standard", 18, ["infection-pathogen-plague"], ["infection-pathogen-tetanus"], ["infection-pathogen-diphtheria"], ["infection-pathogen-dengue"])
setq(MAPPING, 47, "standard", 19, ["infection-route-oral"], ["infection-route-droplet"], ["infection-route-vertical", "infection-rubella-congenital"], ["infection-route-oral"])
setq(MAPPING, 47, "standard", 20, ["infection-prevention-principles"], ["infection-prevention-principles"], ["infection-prevention-principles"], ["infection-prevention-principles"])

setq(MAPPING, 48, "standard", 16, ["infection-pathogen-aids"], ["infection-pathogen-anisakis"], ["infection-pathogen-sars"], ["infection-pathogen-pertussis"])
setq(MAPPING, 48, "standard", 17, ["infection-bacteria-free-living-growth"], ["infection-opportunistic-infection"], ["infection-microbe-drug-resistance"], ["infection-virus-mutation"])
setq(MAPPING, 48, "standard", 18, ["infection-route-soil"], ["infection-route-blood-body-fluid"], ["infection-route-airborne"], ["infection-route-mosquito"])
setq(MAPPING, 48, "standard", 19, ["infection-tuberculosis-clinical-screening"], ["infection-tuberculosis-clinical-screening"], ["infection-employment-restriction"], ["infection-tuberculosis-epidemiology"])
setq(MAPPING, 48, "standard", 20, ["infection-ehec-virulence"], ["infection-ehec-virulence"], ["infection-ehec-virulence"], ["infection-incubation-ehec"])

setq(MAPPING, 49, "standard", 16, ["infection-employment-restriction"], ["infection-employment-restriction"], ["infection-employment-restriction"], ["infection-employment-restriction", "infection-pathogen-tuberculosis"])
setq(MAPPING, 49, "standard", 17, ["infection-pathogen-pertussis"], ["infection-pathogen-cholera"], ["infection-pathogen-malaria"], ["infection-pathogen-tsutsugamushi"])
setq(MAPPING, 49, "standard", 18, ["infection-route-oral"], ["infection-route-vertical", "infection-hepatitis-b-vaccine-chronic"], ["infection-route-blood-body-fluid", "infection-pathogen-hepatitis-c"], ["infection-hepatitis-b-vaccine-chronic"])
setq(MAPPING, 49, "standard", 19, ["infection-route-oral"], ["infection-route-blood-body-fluid", "infection-pathogen-hepatitis-b"], ["infection-route-blood-body-fluid", "infection-pathogen-aids"], ["infection-route-oral", "infection-pathogen-ehec"])
setq(MAPPING, 49, "standard", 20, ["infection-pathogen-diphtheria"], ["infection-route-vertical", "infection-pathogen-syphilis", "infection-syphilis-course"], ["infection-route-oral"], ["infection-measles-transmission"])

setq(MAPPING, 50, "standard", 16, ["infection-bacteria-composition"], ["infection-bacteria-binary-fission"], ["infection-virus-single-nucleic-acid"], ["infection-virus-structure"])
setq(MAPPING, 50, "standard", 17, ["infection-asymptomatic-infection"], ["infection-opportunistic-infection"], ["infection-persistent-infection"], ["infection-vertical-infection", "infection-route-oral"])
setq(MAPPING, 50, "standard", 18, ["infection-normal-flora"], ["infection-normal-flora-barrier"], ["infection-normal-flora-beneficial"], ["infection-normal-flora-pathogenic"])
setq(MAPPING, 50, "standard", 19, ["infection-influenza-features"], ["infection-route-droplet", "infection-route-contact-fomite"], ["infection-influenza-features"], ["infection-influenza-features", "infection-infection-control-handwashing"])
setq(MAPPING, 50, "standard", 20, ["infection-pathogen-measles", "infection-measles-transmission"], ["infection-measles-vaccination"], ["infection-incubation-measles", "infection-measles-clinical"], ["infection-measles-transmission"])

setq(MAPPING, 51, "standard", 16, ["infection-bacteria-oxygen-profile"], ["infection-bacteria-oxygen-profile"], ["infection-bacteria-anaerobic-growth", "infection-bacteria-oxygen-profile"], ["infection-bacteria-oxygen-profile"])
setq(MAPPING, 51, "standard", 17, ["infection-vaccination-law"], ["infection-vaccination-law"], ["infection-vaccination-law"], ["infection-vaccination-law", "infection-tuberculosis-bcg"])
setq(MAPPING, 51, "standard", 18, ["infection-route-mosquito", "infection-pathogen-japanese-encephalitis"], ["infection-route-soil", "infection-pathogen-tetanus"], ["infection-route-oral", "infection-pathogen-cholera"], ["infection-route-airborne"])
setq(MAPPING, 51, "standard", 19, ["infection-route-mosquito"], ["infection-route-mosquito", "infection-pathogen-malaria"], ["infection-route-blood-body-fluid", "infection-pathogen-aids"], ["infection-route-oral"])
setq(MAPPING, 51, "standard", 20, ["infection-pathogen-rubella", "infection-rubella-congenital"], ["infection-rubella-congenital"], ["infection-incubation-rubella"], ["infection-rubella-congenital"])

setq(MAPPING, 52, "standard", 16, ["infection-bacteria-composition"], ["infection-bacteria-nucleic-acids"], ["infection-endospore-resistance"], ["infection-bacteria-flagella"])
setq(MAPPING, 52, "standard", 17, ["infection-route-oral"], ["infection-route-soil"], ["infection-route-mosquito"], ["infection-route-droplet", "infection-pathogen-japanese-encephalitis"])
setq(MAPPING, 52, "standard", 18, ["infection-route-airborne"], ["infection-tuberculosis-clinical-screening"], ["infection-employment-restriction"], ["infection-tuberculosis-bcg"])
setq(MAPPING, 52, "standard", 19, ["infection-influenza-features"], ["infection-route-droplet", "infection-route-contact-fomite"], ["infection-influenza-features"], ["infection-influenza-features"])
setq(MAPPING, 52, "standard", 20, ["infection-syphilis-course"], ["infection-route-vertical"], ["infection-syphilis-course"], ["infection-pathogen-syphilis"])

setq(MAPPING, 53, "standard", 16, ["infection-route-mosquito", "infection-pathogen-dengue"], ["infection-route-blood-body-fluid", "infection-pathogen-hepatitis-c"], ["infection-pathogen-diphtheria"], ["infection-measles-transmission"])
setq(MAPPING, 53, "standard", 17, ["infection-virus-mutation", "infection-bacteria-mutation"], ["infection-bacteria-endospores"], ["infection-bacteria-binary-fission"], ["infection-opportunistic-infection"])
setq(MAPPING, 53, "standard", 18, ["infection-measles-vaccination"], ["infection-tuberculosis-bcg"], ["infection-vaccination-law"], ["infection-vaccination-hiv-unavailable"])
setq(MAPPING, 53, "standard", 19, ["infection-covid19"], ["infection-covid19"], ["infection-covid19", "infection-infection-control-handwashing"], ["infection-covid19"])
setq(MAPPING, 53, "standard", 20, ["infection-pertussis-clinical"], ["infection-pathogen-pertussis"], ["infection-route-droplet", "infection-route-contact-fomite"], ["infection-incubation-pertussis"])

setq(MAPPING, 54, "standard", 16, ["infection-employment-restriction"], ["infection-employment-restriction"], ["infection-employment-restriction", "infection-pathogen-tuberculosis"], ["infection-employment-restriction"])
setq(MAPPING, 54, "standard", 17, ["infection-bacteria-flagella"], ["infection-bacteria-composition"], ["infection-virus-single-nucleic-acid"], ["infection-virus-live-cells"])
setq(MAPPING, 54, "standard", 18, ["infection-infection-vs-disease"], ["infection-infection-vs-disease"], ["infection-infection-vs-disease"], ["infection-incubation-measles"])
setq(MAPPING, 54, "standard", 19, ["infection-route-mosquito"], ["infection-route-contact-fomite"], ["infection-route-soil"], ["infection-route-mosquito"])
setq(MAPPING, 54, "standard", 20, ["infection-measles-transmission"], ["infection-measles-clinical"], ["infection-measles-transmission"], ["infection-measles-vaccination"])


# 第27〜40回と第41回旧制度のq16〜20は、collection上は衛生管理技術だが、
# 指定された旧制度ブロックとして消毒・病原体抵抗性の意味命題へ分類する。
LEGACY_TOPIC_ITEMS = {
    16: ["infection-disinfection-physical", "infection-disinfection-heat", "infection-disinfection-uv"],
    17: ["infection-disinfection-chemical", "infection-disinfection-material"],
    18: ["infection-disinfection-regulation", "infection-disinfection-blood"],
    19: ["infection-disinfection-chemical", "infection-disinfection-hypochlorite"],
    20: ["infection-disinfection-concentration", "infection-disinfection-regulation"],
}
for _exam in range(27, 41):
    for _number, _items in LEGACY_TOPIC_ITEMS.items():
        MAPPING.setdefault(f"{_exam}:standard:{_number}", {choice: _items for choice in range(1, 5)})
for _number, _items in LEGACY_TOPIC_ITEMS.items():
    MAPPING.setdefault(f"41:old:{_number}", {choice: _items for choice in range(1, 5)})


# 各問題の正答選択肢。第52・54回の一部はcollectionの候補値をローカル解説と再確認して補正。
ANSWER_KEYS = {
    "27:standard": [4, 2, 1, 3, 4],
    "28:standard": [1, 4, 2, 4, 3],
    "29:standard": [3, 4, 3, 1, 4],
    "30:standard": [4, 2, 4, 2, 1],
    "31:standard": [4, 1, 2, 3, 1],
    "32:standard": [3, 1, 1, 4, 2],
    "33:standard": [1, 3, 2, 1, 3],
    "34:standard": [1, 2, 1, 2, 3],
    "35:standard": [2, 4, 4, 2, 3],
    "36:standard": [4, 2, 3, 4, 3],
    "37:standard": [4, 3, 1, 2, 3],
    "38:standard": [2, 3, 3, 2, 2],
    "39:standard": [2, 4, 3, 2, 1],
    "40:standard": [2, 4, 1, 2, 3],
    "41:new": [2, 1, 2, 2, 3],
    "41:old": [2, 1, 4, 2, 3],
    "42:new": [1, 3, 4, 1, 3],
    "43:new": [1, 2, 2, 3, 4],
    "44:standard": [3, 2, 1, 3, 3],
    "45:standard": [1, 4, 2, 3, 2],
    "46:standard": [3, 3, 4, 1, 2],
    "47:standard": [2, 1, 1, 3, 4],
    "48:standard": [4, 2, 3, 4, 1],
    "49:standard": [4, 1, 4, 2, 2],
    "50:standard": [3, 4, 4, 1, 1],
    "51:standard": [3, 4, 4, 1, 1],
    "52:standard": [2, 1, 4, 1, 1],
    "53:standard": [1, 4, 4, 1, 3],
    "54:standard": [3, 4, 2, 3, 1],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    collection_path = args.repo / "questions" / "past-exams" / "local" / "collection.json"
    output_path = args.output or (args.repo / "questions" / "analysis" / "subjects" / f"{SLUG}.json")
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    # 旧制度ではq16〜20がcollection上「衛生管理技術」と記録されるため、
    # 第27〜40回と第41回旧制度は指定番号ブロックとして含める。
    all_questions = [
        q for q in collection["questions"]
        if EXAM_MIN <= q.get("exam", -1) <= EXAM_MAX
        and q.get("number") in QUESTION_NUMBERS
        and (q.get("subject") == SUBJECT or 27 <= q.get("exam", -1) <= 41)
    ]
    all_questions.sort(key=lambda q: (q["exam"], q.get("variant", ""), q["number"]))

    included = []
    excluded = []
    for q in all_questions:
        has_text = bool(q.get("question") and str(q["question"]).strip())
        has_choices = isinstance(q.get("choices"), list) and len(q["choices"]) == 4 and all(str(c).strip() for c in q["choices"])
        key = f'{q["exam"]}:{q.get("variant", "standard")}'
        if has_text and has_choices and key in ANSWER_KEYS:
            included.append(q)
        else:
            excluded.append(q)

    refs_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    unmapped = []
    answer_unavailable = []
    for q in included:
        qkey = f'{q["exam"]}:{q.get("variant", "standard")}:{q["number"]}'
        choice_map = MAPPING.get(qkey, {})
        answer_index = ANSWER_KEYS[f'{q["exam"]}:{q.get("variant", "standard")}'][q["number"] - 16]
        if not q.get("sourceUrl"):
            answer_unavailable.append(q["id"])
        for choice in range(1, 5):
            ids = choice_map.get(choice, [])
            if not ids:
                unmapped.append({"id": q["id"], "choice": choice})
            for knowledge_id in ids:
                refs_by_id[knowledge_id].append({
                    "exam": q["exam"],
                    "variant": q.get("variant", "standard"),
                    "number": q["number"],
                    "choice": choice,
                    "polarity": "correct" if choice == answer_index else "incorrect",
                    "sourceUrl": q["sourceUrl"],
                })

    items = []
    for knowledge_id, meta in KNOWLEDGE.items():
        refs = refs_by_id.get(knowledge_id, [])
        if not refs:
            continue
        exams = sorted({f'{ref["exam"]}:{ref["variant"]}' for ref in refs})
        items.append({
            "id": knowledge_id,
            "label": meta["label"],
            "meaning": meta["meaning"],
            "topics": meta["topics"],
            "occurrenceCount": len(refs),
            "examCount": len(exams),
            "correctReferenceCount": sum(ref["polarity"] == "correct" for ref in refs),
            "incorrectReferenceCount": sum(ref["polarity"] == "incorrect" for ref in refs),
            "references": refs,
        })
    items.sort(key=lambda item: (-item["occurrenceCount"], -item["examCount"], item["id"]))

    requested_forms = sorted({f'{q["exam"]}:{q.get("variant", "standard")}' for q in all_questions})
    included_forms = sorted({f'{q["exam"]}:{q.get("variant", "standard")}' for q in included})
    excluded_forms = sorted({f'{q["exam"]}:{q.get("variant", "standard")}' for q in excluded})
    output = {
        "schemaVersion": 1,
        "subject": SUBJECT,
        "subjectSlug": SLUG,
        "method": {
            "version": 1,
            "unit": "正誤判定に必要な意味上の知識命題",
            "integration": "同じ概念・関係・定義を問題文の表現差に依存せず統合し、知識IDを付与した。4択の全選択肢を分析し、組合せ選択肢は含まれる知識命題ごとに参照を付けた。",
            "polarity": "選択肢が当該設問の正答選択肢ならcorrect、それ以外ならincorrect。誤っているものを問う設問では、誤った記述を含む選択肢がcorrectとなる。",
            "occurrenceCount": "知識命題と選択肢参照の延べ数。組合せ選択肢は複数命題を含むため、1選択肢から複数件になる。",
            "examCount": "知識命題が参照された異なる試験区分（exam+variant）の数。",
            "exclusion": "本文または4選択肢が空欄のPDF-onlyレコードは意味分析から除外した。原文の問題文・選択肢はこのJSONへ転載しない。",
            "legacyHandling": "第27〜40回と第41回旧制度は、collection上の科目名が衛生管理技術でも、指定されたq16〜20の取得済みブロックとして走査し、消毒・病原体抵抗性などの意味命題をinfection接頭辞のIDへ統合した。",
            "rerun": "scripts/analyze_infection.py がlocal/collection.jsonを読み、同じ知識ID定義で再集計する。",
        },
        "coverage": {
            "examRange": {"from": EXAM_MIN, "to": EXAM_MAX},
            "questionNumbers": [16, 17, 18, 19, 20],
            "requestedExamForms": requested_forms,
            "includedExamForms": included_forms,
            "excludedExamForms": excluded_forms,
            "requestedQuestionCount": len(all_questions),
            "analyzableQuestionCount": len(included),
            "excludedQuestionCount": len(excluded),
            "analyzedChoiceCount": len(included) * 4,
            "mappedReferenceCount": sum(len(refs) for refs in refs_by_id.values()),
            "unmapped": unmapped,
            "excluded": [{"id": q["id"], "exam": q["exam"], "variant": q.get("variant", "standard"), "number": q["number"], "reason": "question-or-choices-empty; PDF-only"} for q in excluded],
            "answerUnavailable": answer_unavailable,
            "answerKeyOverrides": ["r52-q016", "r54-q016", "r54-q017", "r54-q020"],
            "answerKeyDerivedFromLocalReview": [q["id"] for q in included if q.get("correct") is None],
            "source": "questions/past-exams/local/collection.json",
        },
        "knowledgeItems": items,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "requestedQuestions": len(all_questions),
        "includedQuestions": len(included),
        "excludedQuestions": len(excluded),
        "analyzedChoices": len(included) * 4,
        "mappedReferences": sum(len(refs) for refs in refs_by_id.values()),
        "knowledgeItems": len(items),
        "unmapped": len(unmapped),
        "answerUnavailable": len(answer_unavailable),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

