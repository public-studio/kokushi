import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const collectionPath = path.join(repo, 'questions', 'past-exams', 'local', 'collection.json');
const htmlRoot = path.join(repo, 'questions', 'past-exams', 'local', 'html', 'questions');
const outputPath = path.join(repo, 'questions', 'analysis', 'subjects', 'law.json');
const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));

const manualAnswers = new Map([
  ['r36-q002', 1],
  ['r48-q005', 1],
  ['r48-q008', 3],
  ['r49-q001', 2],
  ['r49-q004', 4],
  ['r49-q005', 3],
  ['r49-q009', 3],
  ['r51-q001', 4],
  ['r53-q001', 2],
]);

const definitions = {
  'law.legal-framework-purpose': {
    label: '理容師法の目的・法体系',
    description: '理容師法が公衆衛生、業務の適正化、資格・免許をどう定めるか、および法律・政令・省令・条例の役割を区別する知識。',
  },
  'law.exam-and-qualification': {
    label: '試験・受験資格・資格付与',
    description: '理容師試験の実施主体、指定試験機関、養成施設、必要な知識・技能、受験資格と資格付与に関する知識。',
  },
  'law.license-registry': {
    label: '免許登録・名簿訂正・免許証手続',
    description: '理容師名簿の登録事項、氏名・本籍などの変更、訂正期限、再交付、返納・提出先に関する知識。',
  },
  'law.license-sanctions': {
    label: '免許拒否・取消し・業務停止',
    description: '無免許営業、精神機能の障害、伝染性疾病、衛生違反、業務停止違反などに対する免許・行政処分の区別に関する知識。',
  },
  'law.outside-place-work': {
    label: '理容所以外での業務と出張理容',
    description: '理容所以外での業務禁止と、疾病、婚礼、条例などに基づく出張理容の例外に関する知識。',
  },
  'law.opening-notification': {
    label: '理容所の開設・変更・承継届',
    description: '理容所の開設届、変更届、相続等による地位の承継、従業者情報、移動理容、理美容所の重複開設に関する知識。',
  },
  'law.facility-confirmation': {
    label: '構造設備の検査・使用確認',
    description: '営業開始前の構造設備の検査・確認と、確認前に施設を使用してはならないことに関する知識。',
  },
  'law.managing-barber': {
    label: '管理理容師',
    description: '常時2人以上の理容師が従事する場合の設置義務、資格要件、講習、兼務および届出事項に関する知識。',
  },
  'law.hygiene-measures': {
    label: '衛生措置・施設衛生基準',
    description: '器具・布片の消毒、清潔保持、採光・照明・換気、床・洗い場など理容業務と理容所に必要な衛生措置に関する知識。',
  },
  'law.inspection-and-closure': {
    label: '立入検査・理容所閉鎖命令',
    description: '環境衛生監視員の立入検査、検査の拒否・妨害・忌避、理容所の閉鎖命令に関する知識。',
  },
  'law.penalties': {
    label: '理容師法上の罰則',
    description: '無免許営業、無届、検査確認前の使用、衛生措置違反、立入検査妨害などに適用される罰金等の知識。',
  },
  'law.public-health-center': {
    label: '保健所・地域保健の役割',
    description: '地域保健法、保健所、市町村保健センター、環境衛生監視員の設置と公衆衛生行政上の役割に関する知識。',
  },
  'law.living-hygiene-business': {
    label: '生活衛生関係営業の制度',
    description: '生活衛生関係営業法、振興指針、振興計画、標準営業約款、生活衛生同業組合・指導センターに関する知識。',
  },
  'law.labor-standards': {
    label: '労働基準法・労働条件',
    description: '労働基準法の適用、労働契約、労働条件の明示、賃金、労働時間、休憩、年次有給休暇に関する知識。',
  },
  'law.employment-insurance': {
    label: '雇用保険',
    description: '雇用保険の適用、保険料負担、基本手当、高年齢求職者給付金、育児休業給付に関する知識。',
  },
  'law.workers-compensation': {
    label: '労災保険',
    description: '労働者災害補償保険の適用範囲、国籍・年齢等の扱い、業務災害・通勤災害に関する知識。',
  },
  'law.health-insurance': {
    label: '健康保険・国民健康保険',
    description: '医療保険の保険者、被保険者、保険料負担、給付・自己負担、産前産後・育児休業中の保険料免除に関する知識。',
  },
  'law.national-pension': {
    label: '国民年金・基礎年金',
    description: '国民年金の被保険者、保険料、免除、老齢・障害・遺族基礎年金、付加年金に関する知識。',
  },
  'law.long-term-care-insurance': {
    label: '介護保険',
    description: '介護保険の保険者、被保険者、介護給付・予防給付・市町村特別給付、利用者負担に関する知識。',
  },
  'law.accounting': {
    label: '会計・財務諸表',
    description: '損益計算書と貸借対照表の役割、利益、資産・負債、流動負債・固定負債に関する知識。',
  },
  'law.general-management': {
    label: '運営管理の個別事項',
    description: '関係法規・制度及び運営管理に含まれる上記分類に直接該当しない個別知識。追加回の分析時に再確認する候補。',
  },
};

function normalizeText(value) {
  return String(value || '')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .normalize('NFKC')
    .replace(/[ \t\r\n]+/g, ' ')
    .trim();
}

function htmlChoiceStatuses(sourceId) {
  if (!sourceId) return null;
  const file = path.join(htmlRoot, `${sourceId}.html`);
  if (!fs.existsSync(file)) return null;
  const html = fs.readFileSync(file, 'utf8');
  const statuses = [];
  for (let choice = 1; choice <= 4; choice += 1) {
    const start = html.indexOf(`expound-${choice}`);
    if (start < 0) {
      statuses.push({ choice, truth: null });
      continue;
    }
    const tail = html.slice(start + 1);
    const next = tail.match(/expound-[1-4]|expound-bottom|class="reference"/);
    const end = next ? start + 1 + next.index : -1;
    const block = html.slice(start, end < 0 ? undefined : end);
    const text = normalizeText(block);
    const saysFalse = /誤り|誤った|間違っている|✕/.test(text);
    const saysTrue = /正しい|○|〇/.test(text);
    statuses.push({ choice, truth: saysFalse && !saysTrue ? false : saysTrue && !saysFalse ? true : null });
  }
  return statuses;
}

function inferAnswer(q) {
  if (Number.isInteger(q.correct) && q.correct >= 1 && q.correct <= 4) return { answer: q.correct, resolution: 'collection.correct' };
  if (manualAnswers.has(q.id)) return { answer: manualAnswers.get(q.id), resolution: 'manual.semantic-review' };
  const sourceId = q.sourceUrl?.split('/').pop();
  const statuses = htmlChoiceStatuses(sourceId);
  const truthChoices = statuses?.filter((item) => item.truth === true).map((item) => item.choice) || [];
  const falseChoices = statuses?.filter((item) => item.truth === false).map((item) => item.choice) || [];
  const negative = /誤って|誤り|該当しない|必要のない|必要がない/.test(q.question || '');
  const candidates = negative ? falseChoices : truthChoices;
  if (candidates.length === 1) return { answer: candidates[0], resolution: 'local-html.commentary' };
  if (sourceId) {
    const file = path.join(htmlRoot, `${sourceId}.html`);
    if (fs.existsSync(file)) {
      const text = normalizeText(fs.readFileSync(file, 'utf8'));
      const match = text.match(/正解[^0-9]{0,12}([1-4])/);
      if (match) return { answer: Number(match[1]), resolution: 'local-html.answer-text' };
    }
  }
  return { answer: null, resolution: 'unavailable' };
}

function isNegativeQuestion(question) {
  return /誤って|誤り|該当しない|必要のない|必要がない/.test(question || '');
}

function classifyChoice(q, choice) {
  const t = normalizeText(`${q.question} ${choice}`);
  const question = normalizeText(q.question);

  if (/損益計算書|貸借対照表|流動負債|固定負債|資産|負債|利益.*収益|収益.*費用/.test(t)) return 'law.accounting';
  if (/国民年金|老齢基礎年金|障害基礎年金|遺族基礎年金|第1号被保険者|付加保険料|付加年金/.test(t)) return 'law.national-pension';
  if (/介護保険|介護給付|予防給付|市町村特別給付|第2号被保険者/.test(t)) return 'law.long-term-care-insurance';
  if (/雇用保険|基本手当|育児休業給付|高年齢求職者給付/.test(t)) return 'law.employment-insurance';
  if (/労働者災害補償|労災|通勤途上|業務災害/.test(t)) return 'law.workers-compensation';
  if (/健康保険|国民健康保険|医療保険|保険料.*被保険者負担|自己負担割合|社会保険.*保険料/.test(t)) return 'law.health-insurance';
  if (/労働基準法|労働条件|労働契約|雇用契約|賃金|労働時間|休憩時間|年次有給|最低基準/.test(t)) return 'law.labor-standards';
  if (/生活衛生関係営業|振興指針|振興計画|標準営業約款|生活衛生同業組合|営業指導センター|理容料金の統一|適正化規程/.test(t)) return 'law.living-hygiene-business';
  if (/保健所|地域保健法|市町村保健センター/.test(t)) return 'law.public-health-center';
  if (/管理理容師/.test(t)) return 'law.managing-barber';
  if (/理容所以外|出張理容|婚礼.*儀式|疾病.*理容所に来る|移動理容/.test(t)) return 'law.outside-place-work';
  if (/罰金|罰則|30万円以下|処せられる/.test(t)) return 'law.penalties';
  if (/立入検査|閉鎖命令|閉鎖処分|理容所の閉鎖/.test(t)) return 'law.inspection-and-closure';
  if (/理容師名簿|本籍地|本籍|登録番号|氏名を変更|住所を変更|再交付|免許証.*返納|免許証.*提出|30日以内/.test(t)) return 'law.license-registry';
  if (/免許取消|免許を取り消|業務停止|再免許|無免許|免許が与えられない|伝染性の疾病|精神の機能/.test(t)) return 'law.license-sanctions';
  if (/構造設備|検査.*確認|確認を受けた後|使用してはならない/.test(t)) return 'law.facility-confirmation';
  if (/開設届|開設の届出|届出事項|開設者の地位|相続|承継|重複開設|理容所を開設|開設者/.test(t)) return 'law.opening-notification';
  if (/器具|消毒|採光|照明|換気|床|腰板|洗い場|清潔|衛生上必要な措置|布片/.test(t)) return 'law.hygiene-measures';
  if (/試験|受験資格|養成施設|知識・技能|資格を定め|資格を与え/.test(t)) return 'law.exam-and-qualification';
  if (/法律|政令|省令|条例|法令|目的|公衆衛生の向上|業務が適正/.test(question + t)) return 'law.legal-framework-purpose';
  return 'law.general-management';
}

function examVariantKey(q) {
  return `${q.exam}-${q.variant}`;
}

const allTargetRecords = collection.questions
  .filter((q) => q.exam >= 24 && q.exam <= 54 && q.number >= 1 && q.number <= 10)
  .sort((a, b) => a.exam - b.exam || String(a.variant).localeCompare(String(b.variant)) || a.number - b.number);
const subjectRecords = allTargetRecords.filter((q) => String(q.subject || '').includes('関係法規'));
const eligible = subjectRecords.filter((q) => {
  return Boolean(q.question && q.question.trim() && Array.isArray(q.choices) && q.choices.length === 4 && q.choices.every((choice) => choice && choice.trim()) && q.sourceUrl);
});
const excludedSubjectRecords = subjectRecords.filter((q) => !eligible.includes(q));

const answerResults = eligible.map((q) => ({ q, ...inferAnswer(q) }));
const answerUnavailable = answerResults.filter((item) => item.answer === null);
const analyzed = answerResults.filter((item) => item.answer !== null);

const items = new Map(Object.entries(definitions).map(([id, value]) => [id, {
  knowledgeId: id,
  label: value.label,
  description: value.description,
  occurrenceCount: 0,
  examCount: 0,
  references: [],
}]));

for (const { q, answer } of analyzed) {
  const negative = isNegativeQuestion(q.question);
  for (let index = 0; index < q.choices.length; index += 1) {
    const choiceNumber = index + 1;
    const knowledgeId = classifyChoice(q, q.choices[index]);
    const item = items.get(knowledgeId);
    const polarity = (negative ? choiceNumber !== answer : choiceNumber === answer) ? 'correct' : 'incorrect';
    item.occurrenceCount += 1;
    item.references.push({
      exam: q.exam,
      variant: q.variant,
      number: q.number,
      choice: choiceNumber,
      polarity,
      sourceUrl: q.sourceUrl,
    });
  }
}

for (const item of items.values()) {
  item.references.sort((a, b) => a.exam - b.exam || String(a.variant).localeCompare(String(b.variant)) || a.number - b.number || a.choice - b.choice);
  item.examCount = new Set(item.references.map((ref) => `${ref.exam}-${ref.variant}`)).size;
}

const targetVariants = [...new Map(allTargetRecords.map((q) => [examVariantKey(q), { exam: q.exam, variant: q.variant }])).values()];
const analyzedVariants = [...new Map(analyzed.map(({ q }) => [examVariantKey(q), { exam: q.exam, variant: q.variant }])).values()];
const excluded = excludedSubjectRecords.map((q) => ({
  id: q.id,
  exam: q.exam,
  variant: q.variant,
  number: q.number,
  reason: q.extraction?.text === 'official-pdf-image-only' || !q.question ? 'pdf-only-record-empty' : 'missing-required-fields',
}));
const outOfScope = allTargetRecords.filter((q) => !subjectRecords.includes(q)).map((q) => ({
  id: q.id,
  exam: q.exam,
  variant: q.variant,
  number: q.number,
  reason: 'outside-law-subject',
}));
const pdfOnlyUnavailable = excluded
  .filter((record) => record.reason === 'pdf-only-record-empty')
  .map((record) => ({ ...record, reason: 'pdf-only-no-answer' }));
const answerUnavailableRecords = [
  ...pdfOnlyUnavailable,
  ...answerUnavailable.map(({ q, resolution }) => ({
    id: q.id,
    exam: q.exam,
    variant: q.variant,
    number: q.number,
    reason: resolution === 'unavailable' ? 'answer-not-resolved' : resolution,
  })),
];

const output = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  subject: {
    slug: 'law',
    name: '関係法規・制度及び運営管理',
    questionRange: { from: 1, to: 10 },
    knowledgeIdPrefix: 'law.',
  },
  method: {
    version: 'law-semantic-v1',
    canonicalSource: 'questions/past-exams/local/collection.json',
    sourcePriority: ['collection.correct', 'local HTML commentary', 'manual semantic review of local records'],
    principles: [
      '問題文の表記一致ではなく、法令上の役割・義務・期限・処分・制度目的を知識命題として統合した。',
      '正答選択肢と誤答選択肢の双方を、選択肢が表す知識命題の出典として参照化した。',
      'polarity は選択肢の命題が正しいかどうかを表し、設問の正答位置そのものを表さない。',
      'examCount は exam と variant の組合せを異なる試験回区分として数え、41回以降の新旧区分を分離した。',
      '本文・選択肢が空欄のPDF-onlyレコードは意味分析から除外し、原文は分析JSONへ転載しない。',
    ],
    rerun: 'node scripts/analyze-subject-law.js',
  },
  coverage: {
    requestedExamRange: { from: 24, to: 54 },
    requestedQuestionRange: { from: 1, to: 10 },
    targetVariantCount: targetVariants.length,
    scannedQuestionRecords: allTargetRecords.length,
    subjectMatchedRecords: subjectRecords.length,
    analyzedQuestionRecords: analyzed.length,
    analyzedChoiceReferences: analyzed.length * 4,
    analyzedVariantCount: analyzedVariants.length,
    excludedCount: excluded.length + outOfScope.length,
    excludedSubjectCount: excluded.length,
    excludedOutOfScopeCount: outOfScope.length,
    excluded,
    outOfScope,
    answerUnavailableCount: answerUnavailableRecords.length,
    answerUnavailable: answerUnavailableRecords,
    targetVariants,
    analyzedVariants,
    answerResolutionCounts: analyzed.reduce((counts, item) => {
      counts[item.resolution] = (counts[item.resolution] || 0) + 1;
      return counts;
    }, {}),
  },
  knowledgeItems: [...items.values()].filter((item) => item.occurrenceCount > 0),
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  output: path.relative(repo, outputPath),
  scanned: allTargetRecords.length,
  subjectMatched: subjectRecords.length,
  analyzed: analyzed.length,
  choiceReferences: analyzed.length * 4,
  excluded: excluded.length + outOfScope.length,
  answerUnavailable: answerUnavailableRecords.length,
  knowledgeItems: output.knowledgeItems.length,
}, null, 2));

