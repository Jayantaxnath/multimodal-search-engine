const API_BASE = "https://jayanta2025-first-space.hf.space";
const IMAGE_BASE = "https://huggingface.co/datasets/jayanta2025/flickr31k-images/resolve/main/";
const BATCH_SIZE = 4;

const textInput = document.getElementById("textInput");
const attachBtn = document.getElementById("attachBtn");
const imageInput = document.getElementById("imageInput");
const imageChip = document.getElementById("imageChip");
const imageChipThumb = document.getElementById("imageChipThumb");
const removeImage = document.getElementById("removeImage");
const searchBtn = document.getElementById("searchBtn");
const alphaRow = document.getElementById("alphaRow");
const alphaSlider = document.getElementById("alphaSlider");
const alphaVal = document.getElementById("alphaVal");
const statusLine = document.getElementById("statusLine");
const resultsEl = document.getElementById("results");
const sentinel = document.getElementById("sentinel");

let attachedFile = null;
let allResults = [];
let shownCount = 0;
let observer = null;

// ---------- Attach image ----------
attachBtn.addEventListener("click", () => imageInput.click());

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) return;
  attachedFile = file;
  imageChipThumb.src = URL.createObjectURL(file);
  imageChip.hidden = false;
  alphaRow.hidden = false;
});

removeImage.addEventListener("click", () => {
  attachedFile = null;
  imageInput.value = "";
  imageChip.hidden = true;
  alphaRow.hidden = true;
});

alphaSlider.addEventListener("input", () => {
  alphaVal.textContent = Number(alphaSlider.value).toFixed(2);
});

textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch();
});
searchBtn.addEventListener("click", runSearch);

// ---------- Search ----------
async function runSearch() {
  const query = textInput.value.trim();

  if (!query && !attachedFile) {
    setStatus("Type a description or attach an image to search.", true);
    return;
  }

  setStatus("Searching…");
  searchBtn.disabled = true;
  showSkeleton();
  teardownObserver();

  try {
    const data = attachedFile
      ? await searchByImage(attachedFile, query)
      : await searchByText(query);

    allResults = data.results || [];
    shownCount = 0;
    resultsEl.innerHTML = "";

    if (allResults.length === 0) {
      resultsEl.innerHTML = `<div class="empty-state">No matches found. Try a different query.</div>`;
      setStatus("0 results.");
    } else {
      setStatus(`${allResults.length} results — showing top ${Math.min(BATCH_SIZE, allResults.length)}.`);
      revealNextBatch();
    }
  } catch (err) {
    resultsEl.innerHTML = "";
    setStatus(`Something went wrong: ${err.message}`, true);
  } finally {
    searchBtn.disabled = false;
  }
}

async function searchByText(query) {
  const res = await fetch(`${API_BASE}/search/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function searchByImage(file, query) {
  const form = new FormData();
  form.append("file", file);

  const params = new URLSearchParams();
  if (query) {
    params.set("query", query);
    params.set("alpha", alphaSlider.value);
  }

  const res = await fetch(`${API_BASE}/search/image?${params.toString()}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// ---------- Rendering ----------
function revealNextBatch() {
  const next = allResults.slice(shownCount, shownCount + BATCH_SIZE);
  next.forEach((r) => resultsEl.appendChild(buildCard(r)));
  shownCount += next.length;

  if (shownCount < allResults.length) {
    observeSentinel();
  } else {
    teardownObserver();
  }
}

function buildCard(result) {
  const card = document.createElement("div");
  card.className = "card";

  const imgWrap = document.createElement("div");
  imgWrap.className = "card-img-wrap";
  const img = document.createElement("img");
  img.loading = "lazy";
  img.src = IMAGE_BASE + encodeURI(result.image_url);
  img.alt = result.captions?.[0] || "Result image";
  imgWrap.appendChild(img);

  const body = document.createElement("div");
  body.className = "card-body";

  const score = document.createElement("span");
  score.className = "card-score";
  score.textContent = `score ${Number(result.score).toFixed(3)}`;

  const caption = document.createElement("p");
  caption.className = "card-caption";
  caption.textContent = result.captions?.[0] || "";

  body.append(score, caption);

  if (result.captions && result.captions.length > 1) {
    const moreBtn = document.createElement("button");
    moreBtn.className = "card-more";
    moreBtn.textContent = `+${result.captions.length - 1} more caption${result.captions.length > 2 ? "s" : ""}`;

    const list = document.createElement("ul");
    list.className = "card-caption-list";
    list.hidden = true;
    result.captions.slice(1).forEach((c) => {
      const li = document.createElement("li");
      li.textContent = c;
      list.appendChild(li);
    });

    moreBtn.addEventListener("click", () => {
      list.hidden = !list.hidden;
      moreBtn.textContent = list.hidden
        ? `+${result.captions.length - 1} more caption${result.captions.length > 2 ? "s" : ""}`
        : "hide captions";
    });

    body.append(moreBtn, list);
  }

  card.appendChild(imgWrap);
  card.appendChild(body);
  return card;
}

function showSkeleton() {
  resultsEl.innerHTML = "";
  for (let i = 0; i < BATCH_SIZE; i++) {
    const card = document.createElement("div");
    card.className = "card skeleton";
    card.innerHTML = `
      <div class="card-img-wrap"></div>
      <div class="card-body">
        <div class="skeleton-line w40"></div>
        <div class="skeleton-line w90"></div>
        <div class="skeleton-line w60"></div>
      </div>`;
    resultsEl.appendChild(card);
  }
}

function observeSentinel() {
  teardownObserver();
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) revealNextBatch();
  }, { rootMargin: "200px" });
  observer.observe(sentinel);
}

function teardownObserver() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
}

function setStatus(msg, isError = false) {
  statusLine.textContent = msg;
  statusLine.classList.toggle("error", isError);
}
