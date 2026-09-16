const tg = window.Telegram?.WebApp;
if (tg) { tg.ready(); tg.expand(); }

const API = ""; // тот же хост, что и сам Web App

/* ---------- Tabs ---------- */
const tabs = document.querySelectorAll(".tab");
const underline = document.getElementById("tabUnderline");

function positionUnderline(tabEl) {
  underline.style.left = tabEl.offsetLeft + "px";
  underline.style.width = tabEl.offsetWidth + "px";
}

function activateTab(name) {
  tabs.forEach(t => t.classList.toggle("is-active", t.dataset.tab === name));
  document.querySelectorAll(".screen").forEach(s => s.classList.toggle("is-active", s.id === name));
  positionUnderline([...tabs].find(t => t.dataset.tab === name));
}

tabs.forEach(t => t.addEventListener("click", () => activateTab(t.dataset.tab)));
window.addEventListener("load", () => positionUnderline(document.querySelector(".tab.is-active")));

/* ---------- Tarot subtabs ---------- */
const subtabs = document.querySelectorAll(".subtab");
subtabs.forEach(t => t.addEventListener("click", () => {
  subtabs.forEach(s => s.classList.toggle("is-active", s === t));
  document.querySelectorAll(".subscreen").forEach(s =>
    s.classList.toggle("is-active", s.id === `${t.dataset.subtab}Screen`));
}));

/* ---------- Shared card renderer ---------- */
function renderCard(container, c, i) {
  const card = document.createElement("div");
  card.className = "tarot-card";
  card.innerHTML = `
    <div class="tarot-card-position">${c.position}</div>
    <div class="tarot-card-inner">
      <div class="tarot-card-face tarot-card-back"><span class="draw-button-glyph tarot-card-back-glyph">✦</span></div>
      <div class="tarot-card-face tarot-card-front">
        <div class="tarot-card-emoji">${c.emoji}</div>
        <div class="tarot-card-name">${c.card}</div>
        ${c.reversed ? '<span class="tarot-card-reversed-tag">перевёрнута</span>' : ""}
        <div class="tarot-card-meaning">${c.meaning}</div>
      </div>
    </div>`;
  container.appendChild(card);
  setTimeout(() => {
    card.classList.add("is-flipped");
    tg?.HapticFeedback?.impactOccurred("medium");
  }, 250 + i * 220);
}

/* ---------- Daily card ---------- */
const dailyButton = document.getElementById("dailyButton");
const dailyCardRow = document.getElementById("dailyCardRow");

dailyButton.addEventListener("click", async () => {
  dailyButton.disabled = true;
  dailyCardRow.innerHTML = "";
  tg?.HapticFeedback?.impactOccurred("light");
  try {
    const res = await fetch(`${API}/api/tarot/draw?spread=one_card`);
    const data = await res.json();
    data.cards.forEach((c, i) => renderCard(dailyCardRow, c, i));
  } catch (err) {
    dailyCardRow.innerHTML = `<p class="lede">Не удалось вытянуть карту. Попробуй ещё раз.</p>`;
  } finally {
    dailyButton.disabled = false;
  }
});

/* ---------- Question + spread ---------- */
const spreadPicker = document.getElementById("spreadPicker");
const drawButton = document.getElementById("drawButton");
const cardsRow = document.getElementById("cardsRow");
const questionInput = document.getElementById("questionInput");
const deckBadge = document.getElementById("deckBadge");
const aiInterpretation = document.getElementById("aiInterpretation");
let currentSpread = "three_cards";

const EXAMPLE_QUESTIONS = [
  "Почему я не могу отпустить эти отношения?",
  "Стоит ли мне менять работу прямо сейчас?",
  "Что мешает мне двигаться дальше?",
  "Получится ли у нас с ним/с ней?",
  "Куда лучше вложить силы в ближайшее время?",
  "Почему я снова чувствую тревогу без причины?",
  "Что мне нужно понять про себя сейчас?",
  "Стоит ли доверять этому человеку?",
  "Что я упускаю в этой ситуации?",
  "Как мне перестать бояться начинать заново?",
];

function setRandomPlaceholder() {
  const q = EXAMPLE_QUESTIONS[Math.floor(Math.random() * EXAMPLE_QUESTIONS.length)];
  questionInput.placeholder = `Например: ${q}`;
}

setRandomPlaceholder();

spreadPicker.addEventListener("click", e => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  spreadPicker.querySelectorAll(".chip").forEach(c => c.classList.remove("is-active"));
  chip.classList.add("is-active");
  currentSpread = chip.dataset.spread;
});

drawButton.addEventListener("click", async () => {
  drawButton.disabled = true;
  cardsRow.innerHTML = "";
  deckBadge.hidden = true;
  aiInterpretation.hidden = true;
  tg?.HapticFeedback?.impactOccurred("light");
  try {
    const q = encodeURIComponent(questionInput.value.trim());
    const res = await fetch(`${API}/api/tarot/draw?spread=${currentSpread}&question=${q}`);
    const data = await res.json();
    deckBadge.hidden = false;
    deckBadge.textContent = `✦ ${data.deck}`;
    data.cards.forEach((c, i) => renderCard(cardsRow, c, i));

    const revealDelay = 250 + data.cards.length * 220 + 400;
    setTimeout(() => {
      if (data.interpretation) {
        aiInterpretation.hidden = false;
        aiInterpretation.innerHTML = `
          ${data.question ? `<p class="ai-interpretation-question">«${data.question}»</p>` : ""}
          <p class="ai-interpretation-text">${data.interpretation}</p>`;
        tg?.HapticFeedback?.notificationOccurred("success");
      }
    }, revealDelay);
  } catch (err) {
    cardsRow.innerHTML = `<p class="lede">Не удалось получить расклад. Проверь соединение и попробуй снова.</p>`;
  } finally {
    drawButton.disabled = false;
    setRandomPlaceholder();
  }
});

/* ---------- Matrix ---------- */
const dateForm = document.getElementById("dateForm");
const matrixWrap = document.getElementById("matrixWrap");
const octagramEl = document.getElementById("octagram");
const pointDetail = document.getElementById("pointDetail");

const ANGLES = { A: 0, B: 90, C: 180, D: 270, E: 45, F: 135, G: 225, H: 315 };
const CENTER = 160, RADIUS = 118;

function pointXY(angleDeg) {
  const rad = (angleDeg - 90) * Math.PI / 180; // 0° = верх
  return { x: CENTER + RADIUS * Math.cos(rad), y: CENTER + RADIUS * Math.sin(rad) };
}

function buildOctagram(points) {
  const outer = ["A", "B", "C", "D"].map(c => pointXY(ANGLES[c]));
  const inner = ["E", "F", "G", "H"].map(c => pointXY(ANGLES[c]));
  const pathFrom = pts => `M ${pts[0].x} ${pts[0].y} L ${pts[1].x} ${pts[1].y} L ${pts[2].x} ${pts[2].y} L ${pts[3].x} ${pts[3].y} Z`;

  let svg = "";
  svg += `<path class="octagram-line" d="${pathFrom(outer)}" />`;
  svg += `<path class="octagram-line" d="${pathFrom(inner)}" style="animation-delay:.15s" />`;

  points.forEach(p => {
    const { x, y } = pointXY(ANGLES[p.code]);
    svg += `<g class="octagram-point" data-code="${p.code}" transform="translate(${x},${y})">
      <circle r="20"></circle>
      <text dy="1">${p.number}</text>
    </g>`;
  });

  octagramEl.innerHTML = svg;

  octagramEl.querySelectorAll(".octagram-point").forEach(el => {
    el.addEventListener("click", () => {
      octagramEl.querySelectorAll(".octagram-point").forEach(p => p.classList.remove("is-active"));
      el.classList.add("is-active");
      const p = points.find(pt => pt.code === el.dataset.code);
      showPointDetail(p);
      tg?.HapticFeedback?.selectionChanged();
    });
  });
}

function showPointDetail(p) {
  pointDetail.innerHTML = `
    <p class="point-detail-title">${p.emoji} ${p.code} · ${p.label}</p>
    <p class="point-detail-source">Складывается из: ${p.source} → аркан №${p.number} «${p.name}»</p>
    <p class="point-detail-meaning">${p.meaning}</p>`;
}

dateForm.addEventListener("submit", async e => {
  e.preventDefault();
  const day = +document.getElementById("day").value;
  const month = +document.getElementById("month").value;
  const year = +document.getElementById("year").value;

  try {
    const res = await fetch(`${API}/api/matrix/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ day, month, year }),
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    matrixWrap.hidden = false;
    buildOctagram(data.points);
    pointDetail.innerHTML = `<p class="point-detail-hint">Коснись точки на схеме, чтобы прочитать её значение.</p>`;
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch {
    matrixWrap.hidden = false;
    pointDetail.innerHTML = `<p class="point-detail-hint">Проверь дату рождения — что-то пошло не так.</p>`;
  }
});
