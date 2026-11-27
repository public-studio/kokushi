import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const collectionPath = `${repo}/questions/past-exams/local/collection.json`;
const htmlRoot = `${repo}/questions/past-exams/local/html/questions`;
const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));

const from = Number(process.argv[2] || 27);
const to = Number(process.argv[3] || 54);

function stripHtml(value) {
  return value
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

function getCommentaryStatuses(id) {
  const file = `${htmlRoot}/${id}.html`;
  if (!fs.existsSync(file)) return null;
  const html = fs.readFileSync(file, 'utf8');
  const statuses = [];
  for (let choice = 1; choice <= 4; choice += 1) {
    const start = html.indexOf(`expound-${choice}`);
    const tail = html.slice(start + 1);
    const next = tail.match(/expound-[1-4]|expound-bottom|class="reference"/);
    const end = next ? start + 1 + next.index : -1;
    const block = start >= 0 ? html.slice(start, end < 0 ? undefined : end) : '';
    const text = stripHtml(block);
    const correct = /正しい|○|〇/.test(text);
    const incorrect = /誤り|誤った|間違っている/.test(text);
    statuses.push({ choice, correct, incorrect, excerpt: text.slice(0, 180) });
  }
  return statuses;
}

function inferCorrect(q, sourceId) {
  if (Number.isInteger(q.correct) && q.correct >= 1 && q.correct <= 4) return q.correct;
  const statuses = sourceId ? getCommentaryStatuses(sourceId) : null;
  const trueChoices = statuses?.filter((item) => item.correct && !item.incorrect).map((item) => item.choice) || [];
  const falseChoices = statuses?.filter((item) => item.incorrect && !item.correct).map((item) => item.choice) || [];
  const negative = /誤って|誤り|該当しない|必要のない|必要がない/.test(q.question || '');
  const statusChoices = negative ? falseChoices : trueChoices;
  if (statusChoices.length === 1) return statusChoices[0];
  if (sourceId) {
    const file = `${htmlRoot}/${sourceId}.html`;
    if (fs.existsSync(file)) {
      const text = stripHtml(fs.readFileSync(file, 'utf8'));
      const match = text.match(/正解[^0-9]{0,12}([1-4])/);
      if (match) return Number(match[1]);
    }
  }
  return null;
}

const questions = collection.questions
  .filter((q) => q.exam >= from && q.exam <= to && q.number >= 1 && q.number <= 10)
  .filter((q) => q.subject.includes('関係法規'))
  .sort((a, b) => a.exam - b.exam || a.variant.localeCompare(b.variant) || a.number - b.number);

for (const q of questions) {
  const sourceId = q.sourceUrl?.split('/').pop();
  const htmlStatuses = sourceId ? getCommentaryStatuses(sourceId) : null;
  console.log(JSON.stringify({
    id: q.id,
    exam: q.exam,
    variant: q.variant,
    number: q.number,
    question: q.question,
    choices: q.choices,
    correct: q.correct,
    inferredCorrect: inferCorrect(q, sourceId),
    sourceUrl: q.sourceUrl,
    extraction: q.extraction,
    htmlStatuses,
  }));
}

