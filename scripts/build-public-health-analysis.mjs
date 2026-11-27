import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoDir = path.resolve(scriptDir, "..");
const collectionPath = path.join(repoDir, "questions", "past-exams", "local", "collection.json");
const outputPath = path.join(repoDir, "questions", "analysis", "subjects", "public-health.json");

const collection = JSON.parse(fs.readFileSync(collectionPath, "utf8"));
const targetRows = collection.questions.filter(
  (row) => row.exam >= 24 && row.exam <= 54 && row.subject === "公衆衛生・環境衛生",
);

const knowledgeDefinitions = {
  "PH-K001": {
    label: "結核菌の発見者",
    description: "結核菌を発見した人物を識別する知識。",
    category: "公衆衛生史",
  },
  "PH-K002": {
    label: "コレラ流行様式の疫学的解明",
    description: "コレラの流行様式を地理的・疫学的に解明した人物を識別する知識。",
    category: "公衆衛生史",
  },
  "PH-K003": {
    label: "予防医学の三段階",
    description: "健康増進・予防接種を第1次予防、早期発見・早期治療を第2次予防、リハビリテーションを第3次予防として対応づける知識。",
    category: "予防医学",
  },
  "PH-K004": {
    label: "公的医療保険の仕組み",
    description: "国民皆保険、公的医療保険の公衆衛生上の効果、窓口負担の例外を理解する知識。",
    category: "医療・介護制度",
  },
  "PH-K005": {
    label: "衣服の着用目的と材料特性",
    description: "体温調節・清潔保持・身体保護・作業能率増進と、通気性・吸湿性・抗菌性・耐熱性・伸縮性などを対応づける知識。",
    category: "衣服・住環境",
  },
  "PH-K006": {
    label: "下水の衛生リスクと処理・放流水規制",
    description: "下水に含まれ得る病原微生物等、処理工程、汚泥の再資源化、放流水の法的規制を理解する知識。",
    category: "水・下水",
  },
  "PH-K007": {
    label: "乳児死亡率と母子保健指標",
    description: "乳児死亡率の定義・分母、健康水準の指標としての意味、母子保健統計の水準を理解する知識。",
    category: "母子保健・人口統計",
  },
  "PH-K008": {
    label: "栄養素・無機質・ビタミンの役割",
    description: "タンパク質・炭水化物・脂肪・無機質・ビタミンの主な機能と欠乏症を対応づける知識。",
    category: "栄養",
  },
  "PH-K009": {
    label: "上水道の水質基準と浄水工程",
    description: "水道法の水質基準、取水から配水までの工程、薬品沈殿、残留塩素と消毒の位置づけを理解する知識。",
    category: "水・下水",
  },
  "PH-K010": {
    label: "衛生害虫の発育・媒介・寄生",
    description: "ハエ・蚊・ゴキブリ・シラミ・ダニ等の発育、媒介感染症、寄生やアレルゲンとの関係を理解する知識。",
    category: "衛生害虫",
  },
  "PH-K011": {
    label: "廃棄物の区分・責任・処理",
    description: "一般廃棄物と産業廃棄物の区分、理容所由来廃棄物の扱い、処理責任、委託、焼却・埋立て・再資源化を理解する知識。",
    category: "廃棄物",
  },
  "PH-K012": {
    label: "浄化槽とし尿処理",
    description: "下水道未整備地域の浄化槽、合併処理、設置・保守点検・清掃を規定する制度を理解する知識。",
    category: "水・下水",
  },
  "PH-K013": {
    label: "出生数・出生率・合計特殊出生率",
    description: "出生率の定義、合計特殊出生率の意味、ベビーブームと少子化の統計的傾向を理解する知識。",
    category: "母子保健・人口統計",
  },
  "PH-K014": {
    label: "平均寿命・粗死亡率・死因統計",
    description: "平均寿命の定義、男女差、粗死亡率、主要死因と年次統計の読み取りを理解する知識。",
    category: "母子保健・人口統計",
  },
  "PH-K015": {
    label: "介護保険と在宅福祉",
    description: "介護保険の運営主体・財源・利用者負担と、ホームヘルプ・デイ・訪問看護等の在宅福祉サービスを理解する知識。",
    category: "医療・介護制度",
  },
  "PH-K016": {
    label: "人口高齢化と後期高齢者",
    description: "老年人口の年齢区分、後期高齢者の定義、日本の高齢化の速度と高齢者人口の推移を理解する知識。",
    category: "高齢化・福祉",
  },
  "PH-K017": {
    label: "母子保健事業と妊産婦支援",
    description: "母子健康手帳、妊産婦・乳幼児健診、新生児訪問、母子保健法等に基づく支援の範囲を理解する知識。",
    category: "母子保健・人口統計",
  },
  "PH-K018": {
    label: "喫煙・飲酒の健康影響と対策",
    description: "喫煙・受動喫煙・妊娠中の喫煙・飲酒による健康影響、喫煙率・飲酒量の推移、健康増進法上の対策を理解する知識。",
    category: "健康増進",
  },
  "PH-K019": {
    label: "室内の温熱環境",
    description: "快適性に関わる温度・湿度・気流、冷房病、理容所の温湿度基準を理解する知識。",
    category: "衣服・住環境",
  },
  "PH-K020": {
    label: "環境要因の分類",
    description: "温度等の物理的要因、有毒ガス等の化学的要因、衛生害虫等の生物学的要因、経済等の社会的要因を分類する知識。",
    category: "環境衛生",
  },
  "PH-K021": {
    label: "食中毒の予防と病原体",
    description: "細菌性食中毒の予防三原則、ブドウ球菌、ノロウイルスの発生季節と手指汚染を理解する知識。",
    category: "環境衛生",
  },
  "PH-K022": {
    label: "糖尿病の合併症",
    description: "糖尿病に関連する白内障、心筋梗塞、末梢神経障害、腎機能障害、網膜症、壊疽等を識別する知識。",
    category: "生活習慣病",
  },
  "PH-K023": {
    label: "心の健康・うつ病・自殺統計",
    description: "心の健康と生活の質、うつ病の早期発見・治療、睡眠、休養、ストレス管理、自殺死亡率の推移を理解する知識。",
    category: "心の健康",
  },
  "PH-K024": {
    label: "健康日本21と健康増進",
    description: "健康日本21の生活習慣病予防、健康寿命の延伸、健康格差の縮小、身体活動の目標を理解する知識。",
    category: "健康増進",
  },
  "PH-K025": {
    label: "換気と室内二酸化炭素",
    description: "自然換気・機械換気、在室者や燃焼暖房による二酸化炭素、理容所の室内空気管理を理解する知識。",
    category: "衣服・住環境",
  },
  "PH-K026": {
    label: "虚血性心疾患の危険因子",
    description: "狭心症・心筋梗塞、運動不足・喫煙・ストレス・食生活等の危険因子、患者数や死亡数の傾向を理解する知識。",
    category: "生活習慣病",
  },
  "PH-K027": {
    label: "一酸化炭素の性質と中毒",
    description: "不完全燃焼で発生する無色無臭の一酸化炭素、ヘモグロビンとの結合、健康影響と濃度管理を理解する知識。",
    category: "環境衛生",
  },
  "PH-K028": {
    label: "水の硬度と体内水分",
    description: "カルシウム・マグネシウムによる硬度と石けんの泡立ち、成人の水分出納、脱水の程度を理解する知識。",
    category: "水・下水",
  },
  "PH-K029": {
    label: "生活習慣病と疾病統計",
    description: "がん・脳卒中・心疾患・糖尿病等の生活習慣との関係、死亡率の推移と疾病分類を理解する知識。",
    category: "生活習慣病",
  },
  "PH-K030": {
    label: "国民健康・栄養調査の傾向",
    description: "炭水化物、動物性タンパク質、動物性脂肪、食塩の摂取傾向を統計として読み取る知識。",
    category: "栄養",
  },
  "PH-K031": {
    label: "保健所の役割",
    description: "保健所の第一線機関としての位置づけ、感染症・精神保健・難病・食品衛生・生活衛生・理容所衛生・統計等の業務範囲を理解する知識。",
    category: "地域保健",
  },
  "PH-K032": {
    label: "粗死亡率と年齢調整死亡率",
    description: "粗死亡率の定義、年齢構成が異なる集団比較に年齢調整死亡率を用いること、両者の経年傾向を理解する知識。",
    category: "母子保健・人口統計",
  },
  "PH-K033": {
    label: "がんの死因統計とリスク",
    description: "がんが主要死因第1位であること、部位別死亡率、喫煙・多量飲酒によるリスクを理解する知識。",
    category: "生活習慣病",
  },
  "PH-K034": {
    label: "浮遊粒子状物質と大気環境基準",
    description: "浮遊粒子状物質の粒径、成分と健康影響、PM2.5、大気汚染に係る環境基準を理解する知識。",
    category: "環境衛生",
  },
  "PH-K035": {
    label: "カビ・ダニと室内アレルゲン",
    description: "カビやダニの発育条件、死骸・ふん・黒カビによるアレルギー、害虫駆除薬剤の注意点を理解する知識。",
    category: "環境衛生",
  },
  "PH-K036": {
    label: "アタマジラミの生態と感染",
    description: "毛髪への産卵、幼虫・成虫の吸血、児童集団での発生、頭部接触や共用品による感染を理解する知識。",
    category: "衛生害虫",
  },
  "PH-K037": {
    label: "照明・採光・照度",
    description: "自然光と採光、照度の単位と適正値、局所・全般・直接・間接照明、グレアと眼精疲労を理解する知識。",
    category: "衣服・住環境",
  },
  "PH-K038": {
    label: "高齢者の心身機能と認知症",
    description: "フレイル、骨粗しょう症、ロコモティブシンドローム、アルツハイマー型認知症と脳血管障害の関係を理解する知識。",
    category: "高齢化・福祉",
  },
  "PH-K039": {
    label: "季節と疾病",
    description: "花粉症、熱中症、食中毒、季節性インフルエンザ等の季節変動を理解する知識。",
    category: "環境衛生",
  },
  "PH-K040": {
    label: "空気の組成と空気感染性の汚染",
    description: "空気中の窒素・酸素・二酸化炭素の割合と由来、細菌やウイルス等の浮遊を理解する知識。",
    category: "環境衛生",
  },
};

const plans = new Map();
function add(keys, items, truths) {
  for (const key of Array.isArray(keys) ? keys : [keys]) {
    if (items.length !== 4 || truths.length !== 4) throw new Error(`4択定義不正: ${key}`);
    plans.set(key, { items, truths });
  }
}

// 旧制度の同科目ブロック（問題6〜10）。新制度との意味統合のため同じ知識IDを共有する。
add("27-standard-6", ["PH-K001", "PH-K001", "PH-K001", "PH-K001"], [false, false, true, false]);
add("27-standard-7", ["PH-K003", "PH-K003", "PH-K003", "PH-K003"], [true, false, true, true]);
add("27-standard-8", ["PH-K004", "PH-K004", "PH-K004", "PH-K004"], [true, true, true, false]);
add("27-standard-9", ["PH-K005", "PH-K005", "PH-K005", "PH-K005"], [true, false, false, false]);
add("27-standard-10", ["PH-K006", "PH-K006", "PH-K006", "PH-K006"], [true, false, true, true]);

add("28-standard-6", ["PH-K007", "PH-K007", "PH-K007", "PH-K007"], [true, true, false, true]);
add("28-standard-7", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [true, false, false, false]);
add("28-standard-8", ["PH-K009", "PH-K009", "PH-K009", "PH-K009"], [true, false, true, true]);
add("28-standard-9", ["PH-K010", "PH-K010", "PH-K010", "PH-K010"], [true, true, false, true]);
add("28-standard-10", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, true, true, false]);

add("29-standard-6", ["PH-K002", "PH-K002", "PH-K002", "PH-K002"], [false, true, false, false]);
add("29-standard-7", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, true, true, false]);
add("29-standard-8", ["PH-K003", "PH-K003", "PH-K003", "PH-K003"], [false, true, true, true]);
add("29-standard-9", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, true, true, false]);
add("29-standard-10", ["PH-K012", "PH-K012", "PH-K012", "PH-K012"], [true, true, false, true]);

add("30-standard-6", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [false, true, true, true]);
add("30-standard-7", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [false, true, false, false]);
add("30-standard-8", ["PH-K015", "PH-K015", "PH-K015", "PH-K015"], [false, false, false, true]);
add("30-standard-9", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [false, false, true, false]);
add("30-standard-10", ["PH-K009", "PH-K009", "PH-K009", "PH-K009"], [false, true, false, false]);

add("31-standard-6", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, false, false, false]);
add("31-standard-7", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [false, true, false, false]);
add("31-standard-8", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [false, false, true, false]);
add("31-standard-9", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, true, true, false]);
add("31-standard-10", ["PH-K006", "PH-K006", "PH-K006", "PH-K006"], [false, false, true, false]);

add("32-standard-6", ["PH-K017", "PH-K017", "PH-K017", "PH-K017"], [false, true, true, true]);
add("32-standard-7", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [true, true, false, true]);
add("32-standard-8", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [false, true, true, true]);
add("32-standard-9", ["PH-K021", "PH-K021", "PH-K021", "PH-K021"], [true, true, false, true]);
add("32-standard-10", ["PH-K006", "PH-K006", "PH-K006", "PH-K006"], [true, true, true, false]);

add("33-standard-6", ["PH-K003", "PH-K003", "PH-K003", "PH-K003"], [true, false, true, true]);
add("33-standard-7", ["PH-K022", "PH-K022", "PH-K022", "PH-K022"], [true, true, false, true]);
add("33-standard-8", ["PH-K023", "PH-K023", "PH-K023", "PH-K023"], [true, true, true, false]);
add("33-standard-9", ["PH-K025", "PH-K025", "PH-K025", "PH-K025"], [false, true, false, false]);
add("33-standard-10", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [false, false, false, true]);

add("34-standard-6", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, false, false, true]);
add("34-standard-7", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [false, true, false, false]);
add("34-standard-8", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [true, true, false, true]);
add("34-standard-9", ["PH-K009", "PH-K009", "PH-K009", "PH-K009"], [false, true, true, false]);
add("34-standard-10", ["PH-K010", "PH-K010", "PH-K010", "PH-K010"], [false, true, true, true]);

add("35-standard-6", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, true, false, false]);
add("35-standard-7", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [false, false, true, false]);
add("35-standard-8", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [false, true, true, true]);
add("35-standard-9", ["PH-K025", "PH-K025", "PH-K025", "PH-K025"], [true, false, true, true]);
add("35-standard-10", ["PH-K028", "PH-K028", "PH-K028", "PH-K028"], [true, true, false, true]);

add("36-standard-6", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, false, true, true]);
add("36-standard-7", ["PH-K004", "PH-K004", "PH-K015", "PH-K015"], [true, false, false, false]);
add("36-standard-8", ["PH-K008", "PH-K008", "PH-K008", "PH-K008"], [true, true, true, false]);
add("36-standard-9", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, true, false, true]);
add("36-standard-10", ["PH-K010", "PH-K010", "PH-K010", "PH-K010"], [false, true, true, true]);

add("37-standard-6", ["PH-K031", "PH-K031", "PH-K031", "PH-K031"], [true, false, false, false]);
add("37-standard-7", ["PH-K007", "PH-K007", "PH-K007", "PH-K007"], [false, false, true, false]);
add("37-standard-8", ["PH-K026", "PH-K026", "PH-K026", "PH-K026"], [true, true, false, true]);
add("37-standard-9", ["PH-K027", "PH-K027", "PH-K027", "PH-K027"], [true, true, false, true]);
add("37-standard-10", ["PH-K028", "PH-K028", "PH-K028", "PH-K028"], [true, false, true, true]);

add("38-standard-6", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, false, false, true]);
add("38-standard-7", ["PH-K024", "PH-K024", "PH-K024", "PH-K024"], [false, true, false, false]);
add("38-standard-8", ["PH-K030", "PH-K030", "PH-K030", "PH-K030"], [false, true, true, true]);
add("38-standard-9", ["PH-K028", "PH-K028", "PH-K028", "PH-K028"], [false, true, true, true]);
add("38-standard-10", ["PH-K010", "PH-K010", "PH-K010", "PH-K010"], [true, true, true, false]);

add("39-standard-6", ["PH-K003", "PH-K003", "PH-K003", "PH-K003"], [true, false, false, false]);
add("39-standard-7", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, true, true, false]);
add("39-standard-8", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, false, true, false]);
add("39-standard-9", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [false, true, true, true]);
add("39-standard-10", ["PH-K036", "PH-K036", "PH-K036", "PH-K036"], [true, false, true, true]);

add("40-standard-6", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [true, true, false, true]);
add("40-standard-7", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, false, false, true]);
add("40-standard-8", ["PH-K039", "PH-K039", "PH-K039", "PH-K039"], [true, false, false, false]);
add("40-standard-9", ["PH-K040", "PH-K040", "PH-K040", "PH-K040"], [false, true, true, true]);
add("40-standard-10", ["PH-K009", "PH-K009", "PH-K006", "PH-K006"], [true, false, true, true]);

for (const [newKey, oldKey] of [
  ["41-new-11", "41-old-6"],
  ["41-new-12", "41-old-7"],
  ["41-new-13", "41-old-8"],
  ["41-new-14", "41-old-9"],
  ["41-new-15", "41-old-10"],
]) {
  const sourcePlan = {
    "41-new-11": ["PH-K017", [true, true, true, false]],
    "41-new-12": ["PH-K014", [true, false, false, false]],
    "41-new-13": ["PH-K029", [true, true, false, true]],
    "41-new-14": ["PH-K019", [true, false, true, true]],
    "41-new-15": ["PH-K005", [false, true, true, true]],
  }[newKey];
  add([newKey, oldKey], Array(4).fill(sourcePlan[0]), sourcePlan[1]);
}

add("42-new-11", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, true, false, true]);
add("42-new-12", ["PH-K022", "PH-K022", "PH-K022", "PH-K022"], [false, true, true, true]);
add("42-new-13", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [true, false, true, true]);
add("42-new-14", ["PH-K020", "PH-K020", "PH-K020", "PH-K020"], [true, false, false, false]);
add("42-new-15", ["PH-K009", "PH-K009", "PH-K009", "PH-K009"], [true, true, false, true]);

add("43-new-11", ["PH-K031", "PH-K031", "PH-K031", "PH-K031"], [false, false, true, false]);
add("43-new-12", ["PH-K013", "PH-K013", "PH-K013", "PH-K013"], [true, false, false, false]);
add("43-new-13", ["PH-K024", "PH-K024", "PH-K024", "PH-K024"], [true, true, false, true]);
add("43-new-14", ["PH-K019", "PH-K019", "PH-K019", "PH-K019"], [true, true, true, false]);
add("43-new-15", ["PH-K025", "PH-K025", "PH-K025", "PH-K025"], [false, true, false, false]);

add("44-standard-11", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [true, false, true, true]);
add("44-standard-12", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [false, false, false, true]);
add("44-standard-13", ["PH-K023", "PH-K023", "PH-K023", "PH-K023"], [true, true, true, false]);
add("44-standard-14", ["PH-K035", "PH-K035", "PH-K035", "PH-K035"], [true, true, false, true]);
add("44-standard-15", ["PH-K034", "PH-K034", "PH-K034", "PH-K034"], [false, true, true, true]);

add("45-standard-11", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [false, false, false, true]);
add("45-standard-12", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [false, false, true, false]);
add("45-standard-13", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [true, false, true, true]);
add("45-standard-14", ["PH-K019", "PH-K019", "PH-K019", "PH-K019"], [false, false, false, true]);
add("45-standard-15", ["PH-K036", "PH-K036", "PH-K036", "PH-K036"], [false, true, true, true]);

add("46-standard-11", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [true, false, false, false]);
add("46-standard-12", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [false, true, false, false]);
add("46-standard-13", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [false, false, true, false]);
add("46-standard-14", ["PH-K027", "PH-K027", "PH-K027", "PH-K027"], [true, false, true, true]);
add("46-standard-15", ["PH-K037", "PH-K037", "PH-K037", "PH-K037"], [true, false, true, true]);

add("47-standard-11", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [false, false, false, true]);
add("47-standard-12", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [true, false, true, true]);
add("47-standard-13", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [false, false, true, false]);
add("47-standard-14", ["PH-K035", "PH-K035", "PH-K035", "PH-K035"], [false, true, true, true]);
add("47-standard-15", ["PH-K012", "PH-K012", "PH-K012", "PH-K012"], [true, true, true, false]);

add("48-standard-11", ["PH-K031", "PH-K031", "PH-K031", "PH-K031"], [true, true, true, false]);
add("48-standard-12", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [true, true, false, true]);
add("48-standard-13", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [false, true, true, true]);
add("48-standard-14", ["PH-K039", "PH-K039", "PH-K039", "PH-K039"], [true, true, false, true]);
add("48-standard-15", ["PH-K027", "PH-K027", "PH-K027", "PH-K027"], [false, true, false, false]);

add("49-standard-11", ["PH-K017", "PH-K017", "PH-K017", "PH-K017"], [true, true, false, true]);
add("49-standard-12", ["PH-K024", "PH-K024", "PH-K024", "PH-K024"], [true, false, true, true]);
add("49-standard-13", ["PH-K022", "PH-K022", "PH-K022", "PH-K022"], [false, true, true, true]);
add("49-standard-14", ["PH-K037", "PH-K037", "PH-K037", "PH-K037"], [true, false, true, true]);
add("49-standard-15", ["PH-K036", "PH-K036", "PH-K036", "PH-K036"], [false, true, true, true]);

add("50-standard-11", ["PH-K031", "PH-K031", "PH-K031", "PH-K031"], [false, true, true, true]);
add("50-standard-12", ["PH-K013", "PH-K013", "PH-K032", "PH-K032"], [true, true, false, true]);
add("50-standard-13", ["PH-K033", "PH-K033", "PH-K033", "PH-K033"], [false, true, false, false]);
add("50-standard-14", ["PH-K006", "PH-K006", "PH-K006", "PH-K006"], [true, true, false, true]);
add("50-standard-15", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, true, false, true]);

add("51-standard-11", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [true, false, false, false]);
add("51-standard-12", ["PH-K029", "PH-K029", "PH-K029", "PH-K029"], [true, false, true, true]);
add("51-standard-13", ["PH-K023", "PH-K023", "PH-K023", "PH-K023"], [true, true, true, false]);
add("51-standard-14", ["PH-K034", "PH-K034", "PH-K034", "PH-K034"], [true, true, false, true]);
add("51-standard-15", ["PH-K025", "PH-K025", "PH-K025", "PH-K025"], [true, true, true, false]);

add("52-standard-11", ["PH-K031", "PH-K031", "PH-K031", "PH-K031"], [true, false, false, false]);
add("52-standard-12", ["PH-K032", "PH-K032", "PH-K032", "PH-K032"], [false, true, false, false]);
add("52-standard-13", ["PH-K033", "PH-K033", "PH-K033", "PH-K033"], [true, false, true, true]);
add("52-standard-14", ["PH-K034", "PH-K034", "PH-K034", "PH-K034"], [true, false, false, false]);
add("52-standard-15", ["PH-K019", "PH-K019", "PH-K019", "PH-K019"], [true, true, true, false]);

add("53-standard-11", ["PH-K018", "PH-K018", "PH-K018", "PH-K018"], [false, false, true, false]);
add("53-standard-12", ["PH-K016", "PH-K016", "PH-K016", "PH-K016"], [true, false, true, true]);
add("53-standard-13", ["PH-K038", "PH-K038", "PH-K038", "PH-K038"], [true, false, true, true]);
add("53-standard-14", ["PH-K027", "PH-K027", "PH-K027", "PH-K027"], [true, true, false, true]);
add("53-standard-15", ["PH-K006", "PH-K006", "PH-K006", "PH-K006"], [true, true, true, false]);

add("54-standard-11", ["PH-K014", "PH-K014", "PH-K014", "PH-K014"], [true, false, false, false]);
add("54-standard-12", ["PH-K022", "PH-K022", "PH-K022", "PH-K022"], [true, false, true, true]);
add("54-standard-13", ["PH-K038", "PH-K038", "PH-K038", "PH-K038"], [true, true, false, true]);
add("54-standard-14", ["PH-K037", "PH-K037", "PH-K037", "PH-K037"], [true, true, true, false]);
add("54-standard-15", ["PH-K011", "PH-K011", "PH-K011", "PH-K011"], [true, false, true, true]);

// 本文と4択が存在するレコードだけを分析対象とする。
const usableRows = targetRows.filter(
  (row) => String(row.question ?? "").trim().length > 0 && Array.isArray(row.choices) && row.choices.length === 4,
);
const excludedRows = targetRows.filter((row) => !usableRows.includes(row));

const counts = new Map();
for (const row of usableRows) {
  const key = `${row.exam}-${row.variant}-${row.number}`;
  const plan = plans.get(key);
  if (!plan) throw new Error(`意味分類定義がありません: ${key}`);
  for (const id of plan.items) {
    if (!knowledgeDefinitions[id]) throw new Error(`知識定義がありません: ${id}`);
  }
  for (let index = 0; index < 4; index += 1) {
    const id = plan.items[index];
    const entry = counts.get(id) ?? { occurrenceCount: 0, exams: new Set(), references: [] };
    entry.occurrenceCount += 1;
    entry.exams.add(row.exam);
    entry.references.push({
      exam: row.exam,
      variant: row.variant,
      number: row.number,
      choice: index + 1,
      polarity: plan.truths[index] ? "correct" : "incorrect",
      sourceUrl: row.sourceUrl,
    });
    counts.set(id, entry);
  }
}

const excluded = excludedRows.map((row) => ({
  exam: row.exam,
  variant: row.variant,
  number: row.number,
  reason: "PDF-only: question text and/or choices are empty in local canonical collection",
  sourceUrl: row.sourceUrl,
  officialSourceUrl: row.officialSourceUrl,
}));

const output = {
  schemaVersion: 1,
  slug: "public-health",
  subject: "公衆衛生・環境衛生",
  generatedAt: new Date().toISOString(),
  method: {
    analysisUnit: "正誤判定に必要な意味上の知識命題。文字列一致ではなく、同じ命題を同一のPH-K###へ統合。",
    optionHandling: "4択の正答・誤答をすべて参照化。polarityは選択肢に含まれる知識命題の正誤であり、設問で選ぶべき番号そのものではない。",
    counting: "occurrenceCountは知識命題に紐づく選択肢参照の延べ数、examCountはexam番号の異なる数。41回new/oldは同一examとしてexamCountを1回と数える。",
    sourceHandling: "原文の問題文・選択肢は転載せず、公開可能な要約ラベル・意味記述と出典URLだけを保存。",
    exclusionRule: "本文または選択肢が空欄のPDF-onlyレコードは意味分析から除外し、coverage.excludedとcoverage.answerUnavailableに記録。",
    legacyHandling: "旧制度で同科目が問題6〜10に配置されるレコードは、問題番号11〜15の新制度ブロックと意味統合するため分析対象に含めた。",
    reproducibility: "scripts/build-public-health-analysis.mjsがlocal/collection.jsonを読み、同じ知識定義・参照生成規則で再集計する。",
  },
  coverage: {
    requestedExamRange: { from: 24, to: 54 },
    requestedModernProblemNumbers: [11, 12, 13, 14, 15],
    legacyEquivalentProblemNumbers: [6, 7, 8, 9, 10],
    scannedCollectionQuestionCount: collection.questions.filter((row) => row.exam >= 24 && row.exam <= 54).length,
    subjectRecordCount: targetRows.length,
    analyzedRecordCount: usableRows.length,
    analyzedChoiceCount: usableRows.length * 4,
    excludedCount: excluded.length,
    excluded,
    answerUnavailable: excluded.map((row) => ({
      exam: row.exam,
      variant: row.variant,
      number: row.number,
      reason: "正答判定に使える本文・選択肢がlocal/collection.jsonにないため、意味分析対象外",
      officialSourceUrl: row.officialSourceUrl,
    })),
    analyzedExamVariants: [...new Set(usableRows.map((row) => `${row.exam}-${row.variant}`))].sort(),
    analyzedExamNumbers: [...new Set(usableRows.map((row) => row.exam))].sort((a, b) => a - b),
  },
  knowledgeItems: [...counts.entries()]
    .map(([knowledgeId, entry]) => ({
      knowledgeId,
      ...knowledgeDefinitions[knowledgeId],
      occurrenceCount: entry.occurrenceCount,
      examCount: entry.exams.size,
      references: entry.references,
    }))
    .sort((a, b) => b.occurrenceCount - a.occurrenceCount || a.knowledgeId.localeCompare(b.knowledgeId)),
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({
  outputPath,
  subjectRecordCount: targetRows.length,
  analyzedRecordCount: usableRows.length,
  analyzedChoiceCount: usableRows.length * 4,
  excludedCount: excluded.length,
  knowledgeItemCount: output.knowledgeItems.length,
}, null, 2));

