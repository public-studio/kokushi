import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const collectionPath = path.join(repo, 'questions', 'past-exams', 'local', 'collection.json');
const htmlRoot = path.join(repo, 'questions', 'past-exams', 'local', 'html', 'questions');
const outputPath = path.join(repo, 'questions', 'analysis', 'subjects', 'sanitation.json');
const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));

const knowledgeDefinitions = {
  'sanitation.definitions': ['消毒・殺菌・滅菌・防腐・除菌の概念', '病原微生物への作用と、無菌化・腐敗防止・菌の除去を区別する。'],
  'sanitation.thermal': ['乾熱・湿熱・蒸気・煮沸の作用', '湿熱の効率、蒸気と煮沸の所要時間、温度・作用時間、芽胞への効果を統合する。'],
  'sanitation.uv': ['紫外線消毒の適用条件', '表面作用、陰・深部への限界、照射強度・時間、対象物の配置を統合する。'],
  'sanitation.uv-safety-maintenance': ['紫外線の安全性とランプ管理', '目・皮膚・粘膜への障害、プラスチック劣化、ランプ出力低下・交換を統合する。'],
  'sanitation.regulation': ['理容所の器具・布片に対する消毒区分', '血液付着の有無、器具種別、洗浄後消毒、理容師法施行規則の方法を統合する。'],
  'sanitation.chemical-factors': ['化学的消毒の作用条件', '温度・濃度・時間、乾燥状態、対象物に応じた濃度を統合する。'],
  'sanitation.sodium-hypochlorite': ['次亜塩素酸ナトリウムの効力・安全管理', '有機物・日光・酸性薬品・漂白作用・塩素ガス・保存条件を統合する。'],
  'sanitation.alcohol': ['消毒用エタノールの性質と用途', '揮発性・引火性・芽胞への限界・器具表面の清拭・材質への影響を統合する。'],
  'sanitation.surfactants': ['逆性・両性界面活性剤と石けんの関係', '結核菌・ウイルス等への効力、有機物・日光・石けん併用の影響を統合する。'],
  'sanitation.microbial-resistance': ['病原微生物の消毒抵抗性', '芽胞と栄養型、ウイルス、結核菌などの消毒薬に対する抵抗性を統合する。'],
  'sanitation.dilution': ['消毒薬水溶液の希釈計算', '原液濃度・必要濃度・液量から、希釈倍数と必要原液量を求める。'],
  'sanitation.storage-safety': ['消毒薬の保存・取扱い安全', '密栓、冷暗所、酸性薬品との混合禁止、臭気確認や容器の扱いを統合する。'],
  'sanitation.facility-hygiene': ['理容所の継続的衛生管理', '布片の客ごとの交換、器具の客ごとの消毒、消毒設備を統合する。'],
  'sanitation.laboratory-technique': ['消毒薬を扱う基本操作', '臭気の確認方法、メスシリンダーの読み方、ラベルを確認した注ぎ方を統合する。'],
  'sanitation.combination-evaluation': ['複数条件を組み合わせた消毒判断', '複数の消毒条件を同時に評価する選択肢を、各条件の意味に分解して扱う。'],
};

// 本文があるがcollection.jsonで未確定の正答は、キャッシュ済みHTMLの解説または内容照合で補った。
const inferredAnswers = {
  'r41-new-q021': 2, 'r41-new-q022': 1, 'r41-new-q023': 4, 'r41-new-q024': 2, 'r41-new-q025': 3,
  'r42-new-q021': 1, 'r42-new-q022': 3, 'r42-new-q024': 2, 'r42-new-q025': 4,
  'r43-new-q021': 4, 'r43-new-q023': 1, 'r43-new-q024': 2,
  'r44-q021': 4, 'r44-q022': 3, 'r44-q024': 1, 'r44-q025': 2,
  'r46-q022': null, 'r46-q023': 2, 'r46-q024': null,
  'r47-q021': 1,
  'r48-q022': null,
  'r49-q022': 4, 'r49-q023': 3,
  'r51-q021': 3, 'r51-q022': 1, 'r51-q023': 2, 'r51-q024': 2,
  'r53-q021': null, 'r53-q023': null, 'r53-q024': 2,
};

const unavailableIds = new Set(Object.entries(inferredAnswers).filter(([, answer]) => answer === null).map(([id]) => id));

function answerFor(q) {
  if (Number.isInteger(q.correct) && q.correct >= 1 && q.correct <= 4) return q.correct;
  if (Object.prototype.hasOwnProperty.call(inferredAnswers, q.id)) return inferredAnswers[q.id];
  const sourceId = q.sourceUrl?.split('/').pop();
  if (!sourceId) return null;
  const file = path.join(htmlRoot, `${sourceId}.html`);
  if (!fs.existsSync(file)) return null;
  const html = fs.readFileSync(file, 'utf8')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .normalize('NFKC');
  const matches = [...html.matchAll(/(?:正解|答え)\s*(?:は|：|:)\s*([1-4])(?=\s*(?:です|。|$))/g)].map((match) => Number(match[1]));
  const unique = [...new Set(matches)];
  return unique.length === 1 ? unique[0] : null;
}

function classify(q, choice) {
  const text = `${q.question ?? ''} ${choice}`;
  const ids = new Set();
  const add = (id) => ids.add(id);

  if (/殺菌|滅菌|消毒|防腐|除菌|無菌|感染力/.test(text)) add('sanitation.definitions');
  if (/乾熱|湿熱|蒸気|煮沸|沸騰|タオル蒸し器|熱変性/.test(text)) add('sanitation.thermal');
  if (/紫外線|殺菌灯|253\.7|85マイクロワット/.test(text)) add('sanitation.uv');
  if (/目や皮膚|粘膜|陰|深部|プラスチック|重なり|劣化|出力|交換|発光/.test(text)) add('sanitation.uv-safety-maintenance');
  if (/理容師法|施行規則|血液|器具|かみそり|はさみ|くし|ブラシ|クリッパー|布片|タオル|洗浄/.test(text)) add('sanitation.regulation');
  if (/温度|濃度|時間|湿度|殺菌効果|作用時間|乾燥/.test(text)) add('sanitation.chemical-factors');
  if (/次亜塩素酸|漂白|塩素ガス|有機物|冷暗所|日光|酸性/.test(text)) add('sanitation.sodium-hypochlorite');
  if (/エタノール|揮発|引火|芽胞|ゴム|消毒用/.test(text)) add('sanitation.alcohol');
  if (/逆性石けん|両性界面活性剤|陽イオン|普通の石けん|中性洗剤/.test(text)) add('sanitation.surfactants');
  if (/芽胞|栄養型|ウイルス|結核菌|ノロウイルス/.test(text)) add('sanitation.microbial-resistance');
  if (/希釈|％|mL|倍|水溶液|濃度/.test(text)) add('sanitation.dilution');
  if (/保存|密栓|臭い|臭気|火気|容器/.test(text)) add('sanitation.storage-safety');
  if (/客一人|取りかえ|設備/.test(text)) add('sanitation.facility-hygiene');
  if (/嗅ぐ|あおぎ|メスシリンダー|液面|ラベルの反対側/.test(text)) add('sanitation.laboratory-technique');
  if (/aとb|bとc|cとd|aとd|A：|B：|C：|D：/.test(choice)) add('sanitation.combination-evaluation');
  if (ids.size === 0) add('sanitation.combination-evaluation');
  return [...ids];
}

const selected = collection.questions
  .filter((q) => q.exam >= 24 && q.exam <= 54)
  .filter((q) => q.subject === '衛生管理技術' && q.number >= 16 && q.number <= 25)
  .sort((a, b) => a.exam - b.exam || a.variant.localeCompare(b.variant) || a.number - b.number);

const excluded = selected
  .filter((q) => !q.question || !Array.isArray(q.choices) || q.choices.length !== 4)
  .map((q) => ({
    exam: q.exam,
    variant: q.variant,
    number: q.number,
    reason: '本文・選択肢が空のPDF画像のみで、意味分析から除外',
    sourceUrl: q.sourceUrl,
    officialSourceUrl: q.officialSourceUrl,
  }));

const analyzable = selected.filter((q) => !excluded.some((item) => item.exam === q.exam && item.variant === q.variant && item.number === q.number));
const answerUnavailable = analyzable
  .filter((q) => answerFor(q) === null)
  .map((q) => ({
    exam: q.exam,
    variant: q.variant,
    number: q.number,
    reason: '正答をcollection.jsonまたはキャッシュ済みHTMLから一意に確定できないため、極性付き参照を生成しない',
    sourceUrl: q.sourceUrl,
    officialSourceUrl: q.officialSourceUrl,
  }));

const itemRefs = new Map(Object.keys(knowledgeDefinitions).map((id) => [id, []]));
for (const q of analyzable) {
  const answer = answerFor(q);
  if (answer === null) continue;
  q.choices.forEach((choice, index) => {
    const polarity = index + 1 === answer ? 'correct' : 'incorrect';
    for (const knowledgeId of classify(q, choice)) {
      itemRefs.get(knowledgeId).push({
        exam: q.exam,
        variant: q.variant,
        number: q.number,
        choice: index + 1,
        polarity,
        sourceUrl: q.sourceUrl,
      });
    }
  });
}

const knowledgeItems = Object.entries(knowledgeDefinitions)
  .map(([id, [label, description]]) => {
    const references = itemRefs.get(id);
    return {
      id,
      label,
      description,
      occurrenceCount: references.length,
      examCount: new Set(references.map((ref) => ref.exam)).size,
      references,
    };
  })
  .filter((item) => item.references.length > 0)
  .sort((a, b) => b.occurrenceCount - a.occurrenceCount || a.id.localeCompare(b.id));

const targetExamVariants = [...new Set(selected.map((q) => `${q.exam}-${q.variant}`))];
const examVariants = [...new Set(analyzable.map((q) => `${q.exam}-${q.variant}`))];
const output = {
  schemaVersion: 1,
  slug: 'sanitation',
  subject: '衛生管理技術',
  method: {
    version: '2026-11-27.2',
    summary: '本文と4択を読み、正誤判定に必要な知識命題を意味単位へ統合した。文字列一致ではなく、消毒法・対象物・作用条件・薬剤特性・希釈計算などの概念群で分類した。第41回新制度以降の問題番号21〜25に加え、旧制度の同一科目番号16〜20も科目名で拾う。',
    sourceOfTruth: 'questions/past-exams/local/collection.json',
    originalTextPolicy: '問題文・選択肢の原文は転載せず、公開可能な要約ラベル・意味記述と参照メタデータだけを保存する。',
    polarity: '正答選択肢をcorrect、その他の選択肢をincorrectとする。正答未確定の問題はanswerUnavailableへ分離する。',
    counts: 'occurrenceCountは知識項目に紐づく選択肢参照の延べ数、examCountはvariantをまたいで異なるexam番号の数。',
  },
  coverage: {
    examFrom: 24,
    examTo: 54,
    requestedNumbers: [21, 22, 23, 24, 25],
    legacyNumbersIncluded: [16, 17, 18, 19, 20],
    selectedRecordCount: selected.length,
    analyzableQuestionCount: analyzable.length,
    analyzedQuestionCount: analyzable.length - answerUnavailable.length,
    analyzedChoiceCount: (analyzable.length - answerUnavailable.length) * 4,
    examVariantCount: targetExamVariants.length,
    analyzedExamVariantCount: examVariants.length,
    targetExamVariants,
    examVariants,
    excludedCount: excluded.length,
    excluded,
    answerUnavailableCount: answerUnavailable.length,
    answerUnavailable,
    note: '旧制度では衛生管理技術が問題16〜20に配置されるため、科目名が一致する旧番号も走査。第24〜26回、第31回再試験、第42・43回旧制度は本文・選択肢がPDF画像のみのため除外。',
  },
  knowledgeItems,
};

fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ outputPath, selected: selected.length, excluded: excluded.length, answerUnavailable: answerUnavailable.length, analyzed: output.coverage.analyzedQuestionCount, knowledgeItems: knowledgeItems.length }, null, 2));

