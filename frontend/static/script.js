(function () {
  "use strict";

  /* ============================================================
     Theme toggle — defaults to system preference, no storage
     ============================================================ */

  var root = document.documentElement;
  var themeToggle = document.getElementById("theme-toggle");
  var prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    themeToggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    themeToggle.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light theme" : "Switch to dark theme"
    );
  }

  applyTheme(prefersDark.matches ? "dark" : "light");

  themeToggle.addEventListener("click", function () {
    var current = root.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
  });

  /* ============================================================
     Elements
     ============================================================ */

  var form = document.getElementById("search-form");
  var submitBtn = document.getElementById("submit-btn");
  var btnLabel = submitBtn.querySelector(".btn-label");
  var btnSpinner = submitBtn.querySelector(".btn-spinner");
  var formError = document.getElementById("form-error");

  var statsPlaceholder = document.getElementById("stats-placeholder");
  var statsBody = document.getElementById("stats-body");
  var strategyBadge = document.getElementById("strategy-badge");
  var selectivityValue = document.getElementById("selectivity-value");
  var meter = document.getElementById("meter");
  var meterFill = document.getElementById("meter-fill");
  var meterNote = document.getElementById("meter-note");
  var embedTimeEl = document.getElementById("embed-time");
  var queryTimeEl = document.getElementById("query-time");
  var totalTimeEl = document.getElementById("total-time");

  var emptyState = document.getElementById("empty-state");
  var emptyHeading = document.getElementById("empty-heading");
  var emptyMessage = document.getElementById("empty-message");
  var resultsList = document.getElementById("results-list");

  /* ============================================================
     Helpers
     ============================================================ */

  function escapeHTML(value) {
    var div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
  }

  function formatMs(value) {
    if (typeof value !== "number") return "—";
    return value.toFixed(1) + " ms";
  }

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnSpinner.hidden = !isLoading;
    btnLabel.textContent = isLoading ? "Searching…" : "Run search";
  }

  function showFormError(message) {
    formError.textContent = message;
    formError.hidden = false;
  }

  function clearFormError() {
    formError.hidden = true;
    formError.textContent = "";
  }

  function showEmptyState(heading, message) {
    emptyHeading.textContent = heading;
    emptyMessage.textContent = message;
    emptyState.hidden = false;
    resultsList.hidden = true;
    resultsList.innerHTML = "";
  }

  /* ============================================================
     Rendering
     ============================================================ */

  function renderStats(data) {
    statsPlaceholder.hidden = true;
    statsBody.hidden = false;

    var isFilterFirst = data.strategy === "filter-first";

    strategyBadge.textContent = isFilterFirst ? "Filter-first" : "Vector-first";
    strategyBadge.className = "strategy-badge " + (isFilterFirst ? "filter-first" : "vector-first");

    meterFill.style.background = isFilterFirst
      ? "var(--accent-filter)"
      : "var(--accent-vector)";

    if (typeof data.selectivity === "number" && data.matched_rows !== null && data.matched_rows !== undefined) {
      meter.hidden = false;
      var pct = Math.max(0, Math.min(1, data.selectivity)) * 100;
      selectivityValue.textContent = (pct).toFixed(2) + "% selective";
      // Slight delay so the width transition is visible on repeated searches.
      requestAnimationFrame(function () {
        meterFill.style.width = pct + "%";
      });
      meterNote.textContent =
        data.matched_rows.toLocaleString() +
        " of " +
        data.total_rows.toLocaleString() +
        " rows matched the category filter.";
    } else {
      meter.hidden = false;
      selectivityValue.textContent = "no filter applied";
      meterFill.style.width = "0%";
      meterNote.textContent =
        "No category filter applied — the planner ranked all " +
        (data.total_rows ? data.total_rows.toLocaleString() : "") +
        " rows by vector similarity.";
    }

    embedTimeEl.textContent = formatMs(data.embed_time_ms);
    queryTimeEl.textContent = formatMs(data.query_time_ms);
    totalTimeEl.textContent = formatMs(data.total_time_ms);
  }

  function renderResults(results) {
    resultsList.innerHTML = "";

    if (!results || results.length === 0) {
      showEmptyState("No matches", "Try a broader category or different search terms.");
      return;
    }

    emptyState.hidden = true;
    resultsList.hidden = false;

    results.forEach(function (result) {
      var similarityPct = Math.max(0, Math.min(1, result.similarity)) * 100;

      var li = document.createElement("li");
      li.className = "result-card";
      li.innerHTML =
        '<div class="result-top">' +
        '<span class="result-category">' + escapeHTML(result.category || "uncategorized") + "</span>" +
        '<span class="result-similarity">' + result.similarity.toFixed(4) + "</span>" +
        "</div>" +
        '<p class="result-text">' + escapeHTML(result.text) + "</p>" +
        '<div class="similarity-bar-track">' +
        '<div class="similarity-bar-fill" style="width:0%"></div>' +
        "</div>";

      resultsList.appendChild(li);

      var fill = li.querySelector(".similarity-bar-fill");
      requestAnimationFrame(function () {
        fill.style.width = similarityPct + "%";
      });
    });
  }

  /* ============================================================
     Search submit
     ============================================================ */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearFormError();

    var query = document.getElementById("query").value.trim();
    var category = document.getElementById("category").value;
    var topK = parseInt(document.getElementById("top_k").value, 10);

    if (!query) {
      showFormError("Enter a query to search.");
      return;
    }

    setLoading(true);

    fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        category: category,
        top_k: topK
      })
    })
      .then(function (response) {
        if (!response.ok) {
          return response
            .json()
            .catch(function () {
              return null;
            })
            .then(function (body) {
              var message =
                (body && (body.error || body.message)) ||
                "The server returned an error (status " + response.status + ").";
              throw new Error(message);
            });
        }
        return response.json();
      })
      .then(function (data) {
        renderStats(data);
        renderResults(data.results);
      })
      .catch(function (err) {
        showFormError(
          err && err.message
            ? err.message
            : "Couldn't reach the search API. Check that the server is running."
        );
      })
      .finally(function () {
        setLoading(false);
      });
  });
})();
