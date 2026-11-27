import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const collectionPath = path.join(repo, 'questions', 'past-exams', 'local', 'collection.json');
const htmlRoot = path.join(repo, 'questions', 'past-exams', 'local', 'html', 'questions');
const outputPath = path.join(repo, 'questions', 'analysis', 'subjects', 'anatomy.json');
const current = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));

const manualAnswers = new Map([
  ['r31-q023', [1]],
  ['r36-q022', [4]],
  ['r39-q023', [1, 3]],
]);

const addedDefinitions = {
  'anatomy-k042': {
    label: '血液の成分と全身運搬',
    description: '血漿・血球・凝固因子の区別と、血液が酸素・物質を運搬する役割に関する知識。',
  },
  'anatomy-k043': {
    label: '体組成と体液',
    description: '成人の体重を構成する水分・脂肪・タンパク質・ミネラルの割合に関する知識。',
  },
  'anatomy-k044': {
    label: '自律神経系の総論',
    description: '自律神経系の区分、内分泌系との協調、循環や内臓機能の調節に関する知識。',
  },
  'anatomy-k045': {
    label: '呼吸と酸素運搬',
    description: '肺呼吸・ガス交換、一酸化炭素中毒、ヘモグロビンによる酸素運搬に関する知識。',
  },
  'anatomy-k047': {
    label: '内分泌腺とホルモン',
    description: '内分泌腺と分泌ホルモンの対応、および血糖・代謝・心機能などへの作用に関する知識。',
  },
  'anatomy-k048': {
    label: '泌尿器と尿排泄',
    description: '腎臓・尿管・膀胱・尿道の区分と、尿中への物質排泄に関する知識。',
  },
  'anatomy-k049': {
    label: '脳の左右半球と感覚伝導',
    description: '大脳・小脳などの左右半球、および感覚器から中枢へ情報を伝える神経に関する知識。',
  },
  'anatomy-k050': {
    label: '循環・生理機能の基準と保健',
    description: '血圧・脈拍・呼吸数などの生理機能基準値と、立位・冷却・圧迫などが循環に及ぼす影響に関する知識。',
  },
  'anatomy-k051': {
    label: 'マイボーム腺と涙液膜',
    description: 'マイボーム腺の位置・分泌物と、涙液膜の安定における役割に関する知識。',
  },
  'anatomy-k052': {
    label: '人体の構造・機能の総合確認',
    description: '既存の個別知識項目に分離できない人体の構造・機能の基礎事項。追加回の分析時に細分化候補として扱う。',
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

function sourceId(q) {
  return q.sourceUrl?.split('/').pop() || null;
}

function htmlTruthStatuses(id) {
  if (!id) return null;
  const file = path.join(htmlRoot, `${id}.html`);
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
    const text = normalizeText(html.slice(start, end < 0 ? undefined : end));
    const saysFalse = /誤り|誤った|間違っている|✕/.test(text);
    const saysTrue = /正しい|○|〇/.test(text);
    statuses.push({
      choice,
      truth: saysFalse && !saysTrue ? false : saysTrue && !saysFalse ? true : null,
    });
  }
  return statuses;
}

function inferAnswers(q) {
  if (manualAnswers.has(q.id)) return { answers: manualAnswers.get(q.id), resolution: 'manual.semantic-review' };
  if (Number.isInteger(q.correct) && q.correct >= 1 && q.correct <= 4) {
    return { answers: [q.correct], resolution: 'collection.correct' };
  }

  const statuses = htmlTruthStatuses(sourceId(q));
  const trueChoices = statuses?.filter((item) => item.truth === true).map((item) => item.choice) || [];
  const falseChoices = statuses?.filter((item) => item.truth === false).map((item) => item.choice) || [];
  const negative = /誤って|誤り|ないもの|含まれない|該当しない|正しくない|必要のない/.test(q.question || '');
  const candidates = negative ? falseChoices : trueChoices;
  if (candidates.length === 1) return { answers: candidates, resolution: 'local-html.commentary' };

  const id = sourceId(q);
  if (id) {
    const file = path.join(htmlRoot, `${id}.html`);
    if (fs.existsSync(file)) {
      const text = normalizeText(fs.readFileSync(file, 'utf8'));
      const matches = [...text.matchAll(/正解[^0-9]{0,12}([1-4])/g)].map((match) => Number(match[1]));
      const unique = [...new Set(matches)];
      if (unique.length === 1) return { answers: unique, resolution: 'local-html.answer-text' };
    }
  }
  return { answers: null, resolution: 'unavailable' };
}

function classifyChoice(q, choice) {
  const question = normalizeText(q.question);
  const text = normalizeText(`${q.question} ${choice}`);

  if (/マイボーム腺/.test(text)) return 'anatomy-k051';
  if (/睫毛|まつ毛/.test(text)) return 'anatomy-k038';
  if (/涙液|涙腺|涙点|涙丘/.test(text)) return 'anatomy-k018';
  if (/眼球結膜|眼表|内眼角|瞳孔周辺/.test(text)) return 'anatomy-k040';
  if (/網膜|光を感じ|視覚.*網膜/.test(text)) return 'anatomy-k016';
  if (/虹彩|瞳孔|水晶体|レンズ|毛様体/.test(text)) return 'anatomy-k017';
  if (/耳小骨|蝸牛|音を感じ|聴覚/.test(text)) return 'anatomy-k019';
  if (/半規管|前庭|平衡感覚/.test(text)) return 'anatomy-k020';
  if (/鼓膜|中耳|耳管/.test(text)) return 'anatomy-k021';

  if (/人中|鼻唇溝|口裂|赤唇縁/.test(text)) return 'anatomy-k004';
  if (/鼻尖|鼻翼|外鼻孔|鼻根|鼻背/.test(text)) return 'anatomy-k002';
  if (/正中線|内眼角|眉間|オトガイ|顔部を構成/.test(text)) return 'anatomy-k003';
  if (/顔面|頬骨|眼窩|上唇/.test(text)) return 'anatomy-k001';

  if (/赤色骨髄|黄色骨髄|造血|骨髄/.test(text)) return 'anatomy-k006';
  if (/軟骨|緻密質|骨組織|頭蓋|上顎骨/.test(text)) return 'anatomy-k007';
  if (/関節|滑液|関節包|関節頭/.test(text)) return 'anatomy-k011';

  if (/頚部|頸部|胸鎖乳突筋/.test(text)) return 'anatomy-k010';
  if (/咀嚼筋|咬筋|側頭筋|頭部の表層/.test(text)) return 'anatomy-k009';
  if (/顔面筋|眼輪筋|口輪筋|笑筋|頬筋|前頭筋|鼻筋|えくぼ|唇を|額にしわ|目を/.test(text)) return 'anatomy-k008';
  if (/体性神経|運動神経.*骨格筋|骨格筋/.test(text)) return 'anatomy-k013';
  if (/心筋/.test(text)) return 'anatomy-k036';
  if (/平滑筋/.test(text)) return 'anatomy-k037';

  if (/左右の半球|半球に分かれ/.test(text)) return 'anatomy-k049';
  if (/知覚神経|感覚器.*中枢|遠心性神経/.test(text)) return 'anatomy-k049';
  if (/中枢神経|末梢神経|大脳|小脳|延髄|脳神経/.test(text)) return 'anatomy-k012';
  if (/交感神経/.test(text)) return 'anatomy-k014';
  if (/副交感神経/.test(text)) return 'anatomy-k015';
  if (/自律神経/.test(text)) return 'anatomy-k044';

  if (/血小板|血液凝固|凝固/.test(text)) return 'anatomy-k024';
  if (/赤血球|ヘモグロビン|血色素|酸素を運搬/.test(text)) return 'anatomy-k023';
  if (/リンパ球|免疫/.test(text)) return 'anatomy-k025';
  if (/単球|マクロファージ/.test(text)) return 'anatomy-k026';
  if (/好中球|食作用/.test(text)) return 'anatomy-k027';
  if (/好塩基球|即時型アレルギー/.test(text)) return 'anatomy-k028';
  if (/血漿|白血球|フィブリノゲン|血液に関する|血液.*運び|血液.*物質/.test(text)) return 'anatomy-k042';

  if (/肺循環|肺動脈|肺静脈|右心室.*肺|肺の毛細/.test(text)) return 'anatomy-k029';
  if (/リンパ管|リンパ液/.test(text)) return 'anatomy-k030';
  if (/基準値|呼吸数|脈拍数|最高血圧|最低血圧|循環器系の保健|マッサージ|立位作業|浮腫|静脈瘤|冷水浴|シャンプークロス/.test(text)) return 'anatomy-k050';
  if (/心臓|大動脈|冠状動脈|循環器|門脈|血管|心拍|血圧|脈拍/.test(text)) return 'anatomy-k031';

  if (/横隔膜|呼吸運動/.test(text)) return 'anatomy-k032';
  if (/一酸化炭素|ガス交換|肺呼吸|ヘモグロビン.*酸素|酸素.*結合/.test(text)) return 'anatomy-k045';
  if (/気管|気管支|肺胞|鼻腔から肺|咽頭|喉頭|気道/.test(text)) return 'anatomy-k033';

  if (/小腸.*蠕動/.test(text)) return 'anatomy-k034';
  if (/唾液腺|消化器|消化管|胃腺|塩酸|膵臓|胆嚢|肝臓|消化酵素|アミラーゼ|ペプシン|トリプシン|リパーゼ|小腸|食道|胃|幽門|噴門/.test(text)) return 'anatomy-k035';
  if (/ホルモン|内分泌|インスリン|アドレナリン|甲状腺|副腎|卵巣|サイロキシン|グルカゴン|コルチコイド|オキシトシン|パラトルモン/.test(text)) return 'anatomy-k047';
  if (/泌尿器|膀胱|尿道|尿管|腎臓|尿中|尿素|クレアチニン|排泄/.test(text)) return 'anatomy-k048';
  if (/体重|水分|脂肪|タンパク質|ミネラル/.test(text)) return 'anatomy-k043';
  if (/長さが、男女間|男女間で顕著/.test(text)) return 'anatomy-k048';

  if (/question|^$/.test(question)) return 'anatomy-k052';
  return 'anatomy-k052';
}

const definitions = new Map(current.knowledgeItems.map((item) => [item.knowledgeId, {
  label: item.label,
  description: item.description,
}]));
for (const [id, definition] of Object.entries(addedDefinitions)) {
  if (!definitions.has(id)) definitions.set(id, definition);
}

const allVariants = [...new Map(collection.questions
  .filter((q) => q.exam >= 24 && q.exam <= 54)
  .map((q) => [`${q.exam}-${q.variant}`, { exam: q.exam, variant: q.variant }])).values()];
const candidates = collection.questions
  .filter((q) => q.exam >= 24 && q.exam <= 54 && q.subject === '人体の構造及び機能')
  .sort((a, b) => a.exam - b.exam || String(a.variant).localeCompare(String(b.variant)) || a.number - b.number);
const eligible = candidates.filter((q) => Boolean(q.question && q.question.trim() && q.sourceUrl && Array.isArray(q.choices) && q.choices.length === 4 && q.choices.every((choice) => choice && choice.trim())));
const excluded = candidates.filter((q) => !eligible.includes(q)).map((q) => ({
  id: q.id,
  exam: q.exam,
  variant: q.variant,
  number: q.number,
  reason: 'pdf-only-record-empty',
}));
const existingQuestionKeys = new Set(current.knowledgeItems.flatMap((item) => item.references.map((ref) => `${ref.exam}-${ref.variant}-${ref.number}`)));
const newRecords = eligible.filter((q) => !existingQuestionKeys.has(`${q.exam}-${q.variant}-${q.number}`));

const answerResults = newRecords.map((q) => ({ q, ...inferAnswers(q) }));
const unresolved = answerResults.filter((item) => !item.answers || item.answers.length === 0);

const items = new Map();
for (const [id, definition] of definitions) {
  items.set(id, {
    knowledgeId: id,
    label: definition.label,
    description: definition.description,
    occurrenceCount: 0,
    examCount: 0,
    references: [],
  });
}
for (const item of current.knowledgeItems) {
  const target = items.get(item.knowledgeId);
  for (const ref of item.references) target.references.push({ ...ref });
}
for (const { q, answers } of answerResults) {
  if (!answers) continue;
  for (let index = 0; index < q.choices.length; index += 1) {
    const choice = index + 1;
    const knowledgeId = classifyChoice(q, q.choices[index]);
    const target = items.get(knowledgeId);
    target.references.push({
      exam: q.exam,
      variant: q.variant,
      number: q.number,
      choice,
      polarity: answers.includes(choice) ? 'correct' : 'incorrect',
      sourceUrl: q.sourceUrl,
    });
  }
}

for (const item of items.values()) {
  const seen = new Set();
  item.references = item.references.filter((ref) => {
    const key = `${ref.exam}-${ref.variant}-${ref.number}-${ref.choice}-${ref.sourceUrl}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  item.references.sort((a, b) => a.exam - b.exam || String(a.variant).localeCompare(String(b.variant)) || a.number - b.number || a.choice - b.choice);
  item.occurrenceCount = item.references.length;
  item.examCount = new Set(item.references.map((ref) => `${ref.exam}-${ref.variant}`)).size;
}

const includedVariants = [...new Map(eligible.filter((q) => !unresolved.some((item) => item.q.id === q.id)).map((q) => [`${q.exam}-${q.variant}`, { exam: q.exam, variant: q.variant }])).values()];
const excludedVariants = [...new Map(excluded.map((q) => [`${q.exam}-${q.variant}`, { exam: q.exam, variant: q.variant }])).values()];
const questionNumbersByVariant = {};
for (const q of candidates) {
  const key = `${q.exam}-${q.variant}`;
  questionNumbersByVariant[key] ??= [];
  questionNumbersByVariant[key].push(q.number);
}
for (const key of Object.keys(questionNumbersByVariant)) questionNumbersByVariant[key] = [...new Set(questionNumbersByVariant[key])].sort((a, b) => a - b);

const resolutionCounts = answerResults.reduce((counts, item) => {
  counts[item.resolution] = (counts[item.resolution] || 0) + 1;
  return counts;
}, {});
const answerUnavailable = [
  ...excluded.map((q) => ({ ...q, reason: 'pdf-only-no-answer' })),
  ...unresolved.map(({ q, resolution }) => ({ id: q.id, exam: q.exam, variant: q.variant, number: q.number, reason: resolution })),
];

const output = {
  schemaVersion: current.schemaVersion || '1.0.0',
  subjectSlug: 'anatomy',
  subject: '人体の構造及び機能',
  questionNumberRange: [21, 30],
  method: {
    ...current.method,
    version: 'anatomy-semantic-v2',
    canonicalSource: 'questions/past-exams/local/collection.json',
    integration: '問題文・選択肢の表記一致ではなく、解剖・生理の知識命題を意味分類し、既存の知識IDを優先して同一知識へ統合。',
    polarity: '設問の正答選択肢をcorrect、その他の選択肢をincorrectとする。複数正答問題は正答集合をcorrectとする。',
    rerun: 'node scripts/analyze-subject-anatomy.js',
  },
  coverage: {
    requestedExamRange: [24, 54],
    subject: '人体の構造及び機能',
    questionNumberRange: [21, 30],
    candidateRecordCount: candidates.length,
    structuredRecordCount: eligible.length - unresolved.length,
    excludedPdfOnlyRecordCount: excluded.length,
    excluded,
    answerUnavailable: {
      pdfOnlyRecordCount: excluded.length,
      structuredRecordMissingCollectionCorrectCount: eligible.filter((q) => q.correct == null).length,
      unresolvedStructuredRecordCount: unresolved.length,
      records: answerUnavailable,
    },
    allVariantCount: allVariants.length,
    includedVariantCount: includedVariants.length,
    includedExamVariants: includedVariants.map((x) => `${x.exam}-${x.variant}`),
    excludedExamVariants: excludedVariants.map((x) => `${x.exam}-${x.variant}`),
    questionNumbersByVariant,
    questionCount: eligible.length - unresolved.length,
    choiceReferenceCount: [...items.values()].reduce((total, item) => total + item.references.length, 0),
    knowledgeItemCount: [...items.values()].filter((item) => item.occurrenceCount > 0).length,
    previousCandidateRecordCount: current.coverage?.candidateRecordCount ?? null,
    previousStructuredRecordCount: current.coverage?.structuredRecordCount ?? null,
    addedStructuredRecordCount: newRecords.length - unresolved.length,
    answerResolution: {
      existingAnalysisPreservedQuestionCount: eligible.length - newRecords.length,
      newRecordResolution: resolutionCounts,
    },
    numberingNote: '第27〜40回では人体の構造及び機能がq21〜25で、q26〜30は皮膚科学。科目名を優先して取り込み、皮膚科学のq26〜30は人体分析へ混入させない。',
  },
  knowledgeItems: [...items.values()].filter((item) => item.occurrenceCount > 0),
};

fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  output: path.relative(repo, outputPath),
  allVariants: allVariants.length,
  candidates: candidates.length,
  analyzedQuestions: output.coverage.questionCount,
  refs: output.coverage.choiceReferenceCount,
  excludedPdfOnly: excluded.length,
  unresolvedStructured: unresolved.length,
  addedStructured: output.coverage.addedStructuredRecordCount,
  knowledgeItems: output.knowledgeItems.length,
}, null, 2));

