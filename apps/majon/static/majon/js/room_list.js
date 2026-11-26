document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#room-search-form");
  const searchInput = document.querySelector("#q");
  const list = document.querySelector("#room-list");
  const pagination = document.querySelector("#room-pagination");
  const status = document.querySelector("#room-list-status");
  const errorContainer = document.querySelector("#room-list-error");
  const totalCount = document.querySelector("#room-total-count");

  let activeController;
  let requestId = 0;
  let currentPage = 1;
  let currentQuery = "";
  let hasSuccessfulData = false;
  let searchTimer;

  const setStatus = (message) => {
    status.textContent = message;
  };

  const setControlsDisabled = (disabled) => {
    form.querySelector("button").disabled = disabled;
    pagination.querySelectorAll("button").forEach((button) => {
      button.disabled = disabled || button.dataset.page === String(currentPage);
    });
  };

  const createRoomCard = (room) => {
    const card = document.createElement("a");
    card.href = room.detail_url;
    card.className = "paper-card group block rounded-2xl p-5 transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md sm:p-6";

    const content = document.createElement("div");
    content.className = "flex items-center justify-between gap-4";
    const details = document.createElement("div");
    details.className = "min-w-0";

    const name = document.createElement("h2");
    name.className = "truncate text-xl font-black group-hover:text-blue-700";
    name.textContent = room.name;
    const code = document.createElement("p");
    code.className = "mt-2 font-mono text-sm font-bold tracking-wider text-stone-500";
    code.textContent = room.code;
    const owner = document.createElement("p");
    owner.className = "mt-2 text-sm text-stone-500";
    owner.textContent = `建立者：${room.owner_display_name}`;
    const arrow = document.createElement("span");
    arrow.className = "shrink-0 text-xl text-stone-400 transition group-hover:translate-x-1 group-hover:text-blue-600";
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "→";

    details.append(name, code, owner);
    content.append(details, arrow);
    card.append(content);
    return card;
  };

  const renderEmpty = () => {
    const empty = document.createElement("div");
    empty.className = "rounded-2xl border border-dashed border-stone-300 bg-white/40 px-6 py-12 text-center";
    const title = document.createElement("p");
    title.className = "font-bold text-stone-700";
    title.textContent = "目前沒有符合條件的房間。";
    const detail = document.createElement("p");
    detail.className = "mt-2 text-sm text-stone-500";
    detail.textContent = "你可以改用其他關鍵字，或建立第一間房間。";
    empty.append(title, detail);
    return empty;
  };

  const pageNumbers = (page, totalPages) => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, index) => index + 1);
    }
    const pages = new Set([1, totalPages, page - 1, page, page + 1]);
    return [...pages]
      .filter((number) => number >= 1 && number <= totalPages)
      .sort((left, right) => left - right);
  };

  const createPageButton = (label, page, disabled, current = false) => {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.page = String(page);
    button.disabled = disabled;
    button.className = "rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-bold text-stone-700 transition hover:border-blue-300 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-50";
    button.textContent = label;
    if (current) {
      button.setAttribute("aria-current", "page");
    }
    button.addEventListener("click", () => loadRooms(page, currentQuery));
    return button;
  };

  const renderPagination = (payload) => {
    pagination.replaceChildren();
    if (payload.total_pages <= 1) {
      return;
    }

    pagination.append(
      createPageButton("上一頁", payload.page - 1, !payload.has_previous),
    );
    let previousNumber = 0;
    pageNumbers(payload.page, payload.total_pages).forEach((number) => {
      if (number - previousNumber > 1) {
        const ellipsis = document.createElement("span");
        ellipsis.className = "px-2 py-2 text-stone-400";
        ellipsis.textContent = "…";
        pagination.append(ellipsis);
      }
      pagination.append(
        createPageButton(String(number), number, number === payload.page, number === payload.page),
      );
      previousNumber = number;
    });
    pagination.append(
      createPageButton("下一頁", payload.page + 1, !payload.has_next),
    );
  };

  const renderError = () => {
    errorContainer.replaceChildren();
    if (!hasSuccessfulData) {
      list.replaceChildren();
    }
    const error = document.createElement("div");
    error.className = "rounded-2xl border border-red-200 bg-red-50 px-6 py-5 text-center";
    const title = document.createElement("p");
    title.className = "font-bold text-red-800";
    title.textContent = "房間載入失敗。";
    const detail = document.createElement("p");
    detail.className = "mt-2 text-sm text-red-700";
    detail.textContent = "請確認網路連線後再試一次。";
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "mt-5 rounded-xl bg-red-700 px-5 py-2 font-bold text-white hover:bg-red-800";
    retry.textContent = "重新載入";
    retry.addEventListener("click", () => loadRooms(currentPage, currentQuery));
    error.append(title, detail, retry);
    errorContainer.append(error);
  };

  const renderRooms = (payload) => {
    errorContainer.replaceChildren();
    list.replaceChildren();
    if (payload.items.length === 0) {
      list.append(renderEmpty());
      setStatus(currentQuery ? `「${currentQuery}」沒有符合條件的房間。` : "目前沒有房間。");
    } else {
      payload.items.forEach((room) => list.append(createRoomCard(room)));
      setStatus(currentQuery ? `「${currentQuery}」的搜尋結果已更新。` : "房間列表已更新。");
    }
    totalCount.textContent = `${payload.total_count} 間房間`;
    renderPagination(payload);
  };

  const loadRooms = async (page = 1, query = searchInput.value.trim()) => {
    requestId += 1;
    const thisRequestId = requestId;
    activeController?.abort();
    activeController = new AbortController();
    currentPage = page;
    currentQuery = query;
    list.setAttribute("aria-busy", "true");
    setControlsDisabled(true);
    setStatus(hasSuccessfulData ? "正在更新房間列表。" : "正在載入房間。");

    const url = new URL(form.action, window.location.origin);
    if (query) {
      url.searchParams.set("q", query);
    }
    url.searchParams.set("page", String(page));

    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal: activeController.signal,
      });
      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }
      const payload = await response.json();
      if (!Array.isArray(payload.items) || typeof payload.total_count !== "number") {
        throw new Error("Invalid room list response");
      }
      if (thisRequestId !== requestId) {
        return;
      }
      currentPage = payload.page;
      hasSuccessfulData = true;
      renderRooms(payload);
    } catch (error) {
      if (error.name === "AbortError" || thisRequestId !== requestId) {
        return;
      }
      setStatus("房間載入失敗，請重新載入。");
      renderError();
    } finally {
      if (thisRequestId === requestId) {
        list.setAttribute("aria-busy", "false");
        setControlsDisabled(false);
      }
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    window.clearTimeout(searchTimer);
    loadRooms(1);
  });

  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => loadRooms(1), 300);
  });

  loadRooms();
});
