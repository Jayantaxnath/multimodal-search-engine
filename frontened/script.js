const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_TOP_K = 8;
const DEFAULT_COMBINED_ALPHA = 0.3; // Image weight
const IMAGE_BASE = "../data/Flickr8k dataset/Images/";
const SEARCH_SUGGESTIONS = [
    "few dogs swimming in lake",
    "two young children playing soccer in a grassy field",
    "couple walking barefoot along the beach at sunset",
    "little girl in a pink dress dancing on a sidewalk",
    "a black and white cat lounging near a sunny window",
    "a hiker climbing a steep rocky mountain trail",
    "group of friends laughing together at an outdoor picnic",
    "a skateboarder performing a trick in an urban skate park",
    "a man in a blue shirt cooking on a backyard grill",
    "a runner crossing the finish line during a marathon",
    "child flying a colorful kite on a windy day"
];

let selectedImageFile = null;
let selectedImagePreviewUrl = null;

function triggerUpload() {
    document.getElementById("imageInput").click();
}

function triggerUploadTop() {
    document.getElementById("imageInput2").click();
}

// Add event listeners when page loads
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("imageInput").addEventListener("change", handleImageUpload);
    document.getElementById("imageInput2").addEventListener("change", handleImageUpload);
    document.getElementById("removeSearchPreview").addEventListener("click", clearSelectedImage);
    document.getElementById("removeTopSearchPreview").addEventListener("click", clearSelectedImage);
    document.getElementById("searchInput").addEventListener("keydown", handleEnterKey);
    document.getElementById("topSearchInput").addEventListener("keydown", handleEnterKey);
    document.getElementById("searchInput").addEventListener("input", handleTypedQuery);
    document.getElementById("topSearchInput").addEventListener("input", handleTypedQuery);

    setupSuggestionDropdown("searchInput", "homeSuggestions");
    setupSuggestionDropdown("topSearchInput", "topSuggestions");

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".search-container")) {
            closeSuggestionDropdowns();
        }
    });
});

function setupSuggestionDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    if (!input) {
        return;
    }

    const container = input.closest(".search-container");
    if (!container) {
        return;
    }

    let dropdown = document.getElementById(dropdownId);
    if (!dropdown) {
        dropdown = document.createElement("div");
        dropdown.id = dropdownId;
        dropdown.className = "search-suggestions";
        container.appendChild(dropdown);
    }

    const render = () => renderSuggestions(input, dropdown, input.value);

    input.addEventListener("focus", render);
    input.addEventListener("click", render);
    input.addEventListener("input", render);
}

function renderSuggestions(input, dropdown, query) {
    const typed = (query || "").trim().toLowerCase();
    const suggestions = SEARCH_SUGGESTIONS.filter((item) => {
        if (!typed) {
            return true;
        }
        return item.toLowerCase().includes(typed);
    }).slice(0, 6);

    if (suggestions.length === 0) {
        dropdown.style.display = "none";
        dropdown.innerHTML = "";
        return;
    }

    dropdown.innerHTML = suggestions
        .map((item) => `<button type="button" class="suggestion-item">${escapeHtml(item)}</button>`)
        .join("");
    dropdown.style.display = "block";

    const buttons = dropdown.querySelectorAll(".suggestion-item");
    buttons.forEach((button, index) => {
        const pickedValue = suggestions[index];
        button.addEventListener("mousedown", function (event) {
            event.preventDefault();
            setBothSearchValues(pickedValue);
            closeSuggestionDropdowns();
        });
    });
}

function setBothSearchValues(value) {
    document.getElementById("searchInput").value = value;
    document.getElementById("topSearchInput").value = value;
}

function closeSuggestionDropdowns() {
    document.querySelectorAll(".search-suggestions").forEach((dropdown) => {
        dropdown.style.display = "none";
    });
}

function handleEnterKey(event) {
    if (event.key === "Enter") {
        closeSuggestionDropdowns();
        search();
    }
}

function handleTypedQuery(event) {
    const typedValue = event.target.value;
    if (event.target.id === "searchInput") {
        document.getElementById("topSearchInput").value = typedValue;
    } else {
        document.getElementById("searchInput").value = typedValue;
    }
}

function setSearchPreview(previewUrl) {
    const preview1 = document.getElementById("searchPreview");
    const preview2 = document.getElementById("topSearchPreview");
    const container1 = preview1 ? preview1.closest(".search-container") : null;
    const container2 = preview2 ? preview2.closest(".search-container") : null;

    if (!preview1 || !preview2) {
        return;
    }

    if (previewUrl) {
        preview1.src = previewUrl;
        preview2.src = previewUrl;
        preview1.style.display = "block";
        preview2.style.display = "block";
        if (container1) {
            container1.classList.add("has-preview");
        }
        if (container2) {
            container2.classList.add("has-preview");
        }
    } else {
        preview1.removeAttribute("src");
        preview2.removeAttribute("src");
        preview1.style.display = "none";
        preview2.style.display = "none";
        if (container1) {
            container1.classList.remove("has-preview");
        }
        if (container2) {
            container2.classList.remove("has-preview");
        }
    }
}

function clearSelectedImage() {
    selectedImageFile = null;
    if (selectedImagePreviewUrl) {
        URL.revokeObjectURL(selectedImagePreviewUrl);
        selectedImagePreviewUrl = null;
    }
    document.getElementById("imageInput").value = "";
    document.getElementById("imageInput2").value = "";
    setSearchPreview(null);
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        clearSelectedImage();
        selectedImageFile = file;
        selectedImagePreviewUrl = URL.createObjectURL(file);
        setSearchPreview(selectedImagePreviewUrl);
    }
}

async function search() {
    const searchInput = document.getElementById("searchInput");
    const topSearchInput = document.getElementById("topSearchInput");
    const homeVisible = document.getElementById("home").style.display !== "none";
    const query = (homeVisible ? searchInput.value : topSearchInput.value || searchInput.value || "").trim();

    if (!query && !selectedImageFile) {
        return;
    }

    document.getElementById("home").style.display = "none";
    document.getElementById("resultsPage").style.display = "block";
    document.getElementById("topSearchInput").value = query;

    await showResults(query, selectedImageFile);
}

async function fetchTextResults(query) {
    const response = await fetch(`${API_BASE_URL}/search/text`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query, top_k: DEFAULT_TOP_K })
    });

    if (!response.ok) {
        throw new Error(`Text search failed: ${response.status}`);
    }

    return response.json();
}

async function fetchImageResults(file, query) {
    const formData = new FormData();
    formData.append("file", file);

    const params = new URLSearchParams({ top_k: String(DEFAULT_TOP_K) });
    if (query && query.trim().length > 0) {
        params.set("query", query.trim());
        params.set("alpha", String(DEFAULT_COMBINED_ALPHA));
    }

    const response = await fetch(`${API_BASE_URL}/search/image?${params.toString()}`, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Image search failed: ${response.status}`);
    }

    return response.json();
}

function getAllCaptions(item) {
    if (!item || !Array.isArray(item.captions) || item.captions.length === 0) {
        return [];
    }

    return item.captions
        .map((caption) => {
            if (typeof caption === "string") {
                return caption;
            }
            return caption && caption.text ? caption.text : "";
        })
        .filter((caption) => caption);
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function resolveImageUrl(imageUrl) {
    if (!imageUrl) {
        return "";
    }

    const fileName = imageUrl.replaceAll("\\", "/").split("/").pop();
    if (!fileName) {
        return "";
    }

    return `${IMAGE_BASE}${fileName}`;
}

async function showResults(query, imageFile) {
    const mixedDiv = document.getElementById("mixedResults");
    mixedDiv.innerHTML = "<p>Loading results...</p>";

    try {
        const payload = imageFile ? await fetchImageResults(imageFile, query) : await fetchTextResults(query);
        const results = payload.results || [];

        if (results.length === 0) {
            mixedDiv.innerHTML = "<p>No results found.</p>";
            return;
        }

        mixedDiv.innerHTML = "";

        results.forEach((result) => {
            const imageUrl = resolveImageUrl(result.image_url || "");
            const captions = getAllCaptions(result);
            const captionsHtml = captions.length > 0
                ? captions.map((caption) => `<div class="result-snippet">${escapeHtml(caption)}</div>`).join("")
                : `<div class="result-snippet">No caption available</div>`;
            const scoreValue = typeof result.score === "number" ? result.score : null;
            const score = scoreValue !== null ? scoreValue.toFixed(4) : "N/A";
            const searchMethod = imageFile
                ? (query ? "Combined similarity" : "similarity search")
                : (scoreValue !== null && scoreValue > 1 ? "BM25" : "Cosine Similarity");

            mixedDiv.innerHTML += `
                <div class="image-result-item">
                    <div class="image-container">
                        <img src="${escapeHtml(imageUrl)}" alt="Search result image">
                        <div class="image-info">
                            <div class="image-title">Similarity score: ${escapeHtml(score)}</div>
                            <div class="captions-scroll">${captionsHtml}</div>
                            <!-- <div class="image-url">${escapeHtml(imageUrl)}</div> -->
                            <div class="result-snippet">Method: ${escapeHtml(searchMethod)}</div>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        mixedDiv.innerHTML = `<p>Could not load results. ${escapeHtml(error.message)}</p>`;
    }
}