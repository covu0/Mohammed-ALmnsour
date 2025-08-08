const form = document.getElementById('qa-form');
const questionEl = document.getElementById('question');
const jurisdictionEl = document.getElementById('jurisdiction');
const topicEl = document.getElementById('topic');
const modeEl = document.getElementById('mode');
const loadingEl = document.getElementById('loading');
const resultEl = document.getElementById('result');
const answerEl = document.getElementById('answer');
const disclaimerEl = document.getElementById('disclaimer');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = questionEl.value.trim();
  const jurisdiction = jurisdictionEl.value.trim();
  const topic = topicEl.value.trim();
  const mode = modeEl.value;

  if (!question) {
    alert('Please enter a question.');
    return;
  }

  loadingEl.hidden = false;
  resultEl.hidden = true;

  try {
    const res = await fetch('/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, jurisdiction, topic, mode })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Request failed');
    }
    const data = await res.json();
    disclaimerEl.textContent = data.disclaimer || '';
    answerEl.textContent = data.answer || '';
    resultEl.hidden = false;
  } catch (err) {
    alert('Something went wrong: ' + (err?.message || err));
  } finally {
    loadingEl.hidden = true;
  }
});