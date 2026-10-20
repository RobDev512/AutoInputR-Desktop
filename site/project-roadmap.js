"use strict";

const ROADMAP_URL = "./ROADMAP.md";

const roadmapGrid =
  document.querySelector("#roadmapGrid");

const roadmapDetail =
  document.querySelector("#roadmapDetail");

const roadmapStatus =
  document.querySelector("#roadmapLoadStatus");

const roadmapFilters =
  [
    ...document.querySelectorAll(
      "[data-roadmap-filter]"
    )
  ];

const roadmapPdfExport =
  document.querySelector(
    "#roadmapPdfExport"
  );

let roadmapItems = [];
let roadmapMarkdown = "";
let roadmapPdfLoaderPromise = null;
let activeRoadmapFilter = "all";
let selectedRoadmapVersion = null;


function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function inlineMarkdown(value = "") {
  let text = escapeHtml(value);

  text = text.replace(
    /`([^`]+)`/g,
    "<code>$1</code>"
  );

  text = text.replace(
    /\*\*([^*]+)\*\*/g,
    "<strong>$1</strong>"
  );

  return text;
}


function normalizeStatus(raw = "") {
  const value =
    raw
      .trim()
      .toLowerCase();

  if (value.includes("aplicada")) {
    return {
      key: "applied",
      label: "Aplicada"
    };
  }

  if (
    value.includes("en desarrollo") ||
    value.includes("desarrollo")
  ) {
    return {
      key: "development",
      label: "En desarrollo"
    };
  }

  if (value.includes("siguiente")) {
    return {
      key: "next",
      label: "Siguiente"
    };
  }

  if (value.includes("pendiente")) {
    return {
      key: "pending",
      label: "Pendiente"
    };
  }

  if (
    value.includes("visión") ||
    value.includes("vision")
  ) {
    return {
      key: "vision",
      label: "Visión"
    };
  }

  return {
    key: "pending",
    label: raw || "Pendiente"
  };
}


function getExcerpt(lines) {
  for (const raw of lines) {
    const line =
      raw.trim();

    if (
      !line ||
      line === "---" ||
      line.startsWith("**Estado:**") ||
      line.startsWith("###") ||
      line.startsWith("-")
    ) {
      continue;
    }

    return line
      .replace(/\*\*/g, "")
      .replace(/`/g, "");
  }

  return "Consulta el detalle de esta versión.";
}


function renderRoadmapBody(lines) {
  const html = [];

  let inList = false;

  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };

  for (const raw of lines) {
    const line =
      raw.trim();

    if (
      !line ||
      line === "---"
    ) {
      closeList();
      continue;
    }

    if (line.startsWith("**Estado:**")) {
      continue;
    }

    if (line.startsWith("### ")) {
      closeList();

      html.push(
        `<h4>${inlineMarkdown(line.slice(4))}</h4>`
      );

      continue;
    }

    if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }

      html.push(
        `<li>${inlineMarkdown(line.slice(2))}</li>`
      );

      continue;
    }

    closeList();

    html.push(
      `<p>${inlineMarkdown(line)}</p>`
    );
  }

  closeList();

  return html.join("");
}


function parseRoadmap(markdown) {
  const lines =
    markdown
      .replace(/\r/g, "")
      .split("\n");

  const items = [];

  let current = null;

  const headingPattern =
    /^##\s+(v\d+(?:\.\d+){1,3})\s+—\s+(.+)$/;

  for (const rawLine of lines) {
    const match =
      rawLine.match(headingPattern);

    if (match) {
      if (current) {
        items.push(current);
      }

      current = {
        version: match[1],
        title: match[2].trim(),
        statusRaw: "",
        lines: []
      };

      continue;
    }

    if (!current) {
      continue;
    }

    const statusMatch =
      rawLine
        .trim()
        .match(
          /^\*\*Estado:\*\*\s*(.+)$/
        );

    if (statusMatch) {
      current.statusRaw =
        statusMatch[1].trim();
    }

    current.lines.push(rawLine);
  }

  if (current) {
    items.push(current);
  }

  return items.map(
    (item) => ({
      ...item,

      status:
        normalizeStatus(
          item.statusRaw
        ),

      excerpt:
        getExcerpt(
          item.lines
        )
    })
  );
}


function matchesRoadmapFilter(item) {
  return (
    activeRoadmapFilter === "all" ||
    item.status.key === activeRoadmapFilter
  );
}


function roadmapStatusClass(status) {
  return `roadmap-status-${status}`;
}


function prepareRoadmapCardMotion(
  button,
  index
) {
  button.style.setProperty(
    "--roadmap-index",
    String(index)
  );

  button.classList.add(
    "roadmap-enter"
  );

  button.addEventListener(
    "pointermove",
    (event) => {
      const rect =
        button.getBoundingClientRect();

      button.style.setProperty(
        "--roadmap-pointer-x",
        `${event.clientX - rect.left}px`
      );

      button.style.setProperty(
        "--roadmap-pointer-y",
        `${event.clientY - rect.top}px`
      );

      button.classList.add(
        "roadmap-pointer-active"
      );
    }
  );

  button.addEventListener(
    "pointerleave",
    () => {
      button.classList.remove(
        "roadmap-pointer-active"
      );
    }
  );
}


function renderRoadmapGrid() {
  const visible =
    roadmapItems.filter(
      matchesRoadmapFilter
    );

  roadmapGrid.innerHTML =
    visible
      .map(
        (item) => `
          <button
            class="
              roadmap-live-card
              ${
                selectedRoadmapVersion === item.version
                  ? "selected"
                  : ""
              }
            "
            type="button"
            data-roadmap-version="${escapeHtml(item.version)}"
          >

            <div class="roadmap-live-card-top">

              <span class="roadmap-live-version">
                ${escapeHtml(item.version)}
              </span>

              <span
                class="
                  roadmap-status
                  ${roadmapStatusClass(item.status.key)}
                "
              >
                ${escapeHtml(item.status.label)}
              </span>

            </div>

            <h3>
              ${escapeHtml(item.title)}
            </h3>

            <p>
              ${escapeHtml(item.excerpt)}
            </p>

            <span class="roadmap-open">
              Ver detalle →
            </span>

          </button>
        `
      )
      .join("");

  if (!visible.length) {
    roadmapGrid.innerHTML = `
      <div class="roadmap-empty">
        No hay versiones que coincidan con este filtro.
      </div>
    `;

    return;
  }

  roadmapGrid
    .querySelectorAll(
      "[data-roadmap-version]"
    )
    .forEach(
      (button, index) => {
        prepareRoadmapCardMotion(
          button,
          index
        );

        button.addEventListener(
          "click",
          () => {
            showRoadmapDetail(
              button.dataset.roadmapVersion
            );
          }
        );
      }
    );
}


function showRoadmapDetail(version) {
  const item =
    roadmapItems.find(
      (candidate) =>
        candidate.version === version
    );

  if (!item) {
    return;
  }

  selectedRoadmapVersion =
    version;

  renderRoadmapGrid();

  roadmapDetail.hidden =
    false;

  roadmapDetail.innerHTML = `

    <div class="roadmap-detail-header">

      <div>

        <span class="roadmap-live-version">
          ${escapeHtml(item.version)}
        </span>

        <h3>
          ${escapeHtml(item.title)}
        </h3>

      </div>

      <span
        class="
          roadmap-status
          ${roadmapStatusClass(item.status.key)}
        "
      >
        ${escapeHtml(item.status.label)}
      </span>

    </div>

    <p class="roadmap-detail-summary">
      ${escapeHtml(item.excerpt)}
    </p>

    <div class="roadmap-detail-body">
      ${renderRoadmapBody(item.lines)}
    </div>

    <button
      class="roadmap-detail-close"
      id="roadmapDetailClose"
      type="button"
    >
      Cerrar detalle
    </button>

  `;

  document
    .querySelector(
      "#roadmapDetailClose"
    )
    ?.addEventListener(
      "click",
      () => {
        selectedRoadmapVersion =
          null;

        roadmapDetail.hidden =
          true;

        roadmapDetail.classList.remove(
          "roadmap-detail-enter"
        );

        roadmapDetail.innerHTML =
          "";

        renderRoadmapGrid();
      }
    );

  roadmapDetail.classList.remove(
    "roadmap-detail-enter"
  );

  requestAnimationFrame(
    () => {
      roadmapDetail.classList.add(
        "roadmap-detail-enter"
      );
    }
  );

  roadmapDetail.scrollIntoView({
    behavior: "smooth",
    block: "nearest"
  });
}




function ensureRoadmapPdfExporter() {
  if (window.RoadmapPdf) {
    return Promise.resolve(
      window.RoadmapPdf
    );
  }

  if (roadmapPdfLoaderPromise) {
    return roadmapPdfLoaderPromise;
  }

  roadmapPdfLoaderPromise =
    new Promise(
      (resolve, reject) => {
        const script =
          document.createElement(
            "script"
          );

        script.src =
          "./roadmap-pdf.js";

        script.onload =
          () => {
            if (window.RoadmapPdf) {
              resolve(
                window.RoadmapPdf
              );
              return;
            }

            reject(
              new Error(
                "El exportador PDF no se inicializó."
              )
            );
          };

        script.onerror =
          () => {
            reject(
              new Error(
                "No se pudo cargar roadmap-pdf.js."
              )
            );
          };

        document.head.append(
          script
        );
      }
    );

  return roadmapPdfLoaderPromise;
}


async function exportRoadmapPdf() {
  if (
    !roadmapPdfExport ||
    !roadmapMarkdown
  ) {
    return;
  }

  const originalText =
    roadmapPdfExport.textContent;

  roadmapPdfExport.disabled =
    true;

  roadmapPdfExport.textContent =
    "Generando PDF…";

  try {
    const exporter =
      await ensureRoadmapPdfExporter();

    const projectTitle =
      document.querySelector(
        ".hero h1"
      )
      ?.textContent
      ?.replace(/\s+/g, " ")
      ?.trim() ||
      document.title
        .split("·")[0]
        .trim();

    exporter.downloadMarkdown({
      markdown:
        roadmapMarkdown,
      title:
        projectTitle,
      subtitle:
        "Roadmap del proyecto",
      source:
        ROADMAP_URL,
      filename:
        `${projectTitle}-Roadmap.pdf`
    });

    roadmapPdfExport.textContent =
      "PDF descargado";

    window.setTimeout(
      () => {
        roadmapPdfExport.textContent =
          originalText;

        roadmapPdfExport.disabled =
          false;
      },
      1200
    );
  }
  catch (error) {
    console.error(
      "No se pudo exportar el roadmap a PDF:",
      error
    );

    roadmapPdfExport.textContent =
      "Error al exportar";

    window.setTimeout(
      () => {
        roadmapPdfExport.textContent =
          originalText;

        roadmapPdfExport.disabled =
          false;
      },
      1500
    );
  }
}


async function loadRoadmap() {
  roadmapStatus.textContent =
    "Cargando roadmap…";

  try {
    const response =
      await fetch(
        ROADMAP_URL,
        {
          cache: "no-store"
        }
      );

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status}`
      );
    }

    const markdown =
      await response.text();

    roadmapMarkdown =
      markdown;

    roadmapItems =
      parseRoadmap(markdown);

    if (!roadmapItems.length) {
      throw new Error(
        "No se encontraron versiones en ROADMAP.md"
      );
    }

    roadmapStatus.textContent =
      `${roadmapItems.length} versiones cargadas desde ROADMAP.md. Selecciona una para ver su detalle.`;

    renderRoadmapGrid();

    if (
      roadmapPdfExport &&
      roadmapPdfExport.dataset.bound !== "true"
    ) {
      roadmapPdfExport.dataset.bound =
        "true";

      roadmapPdfExport.addEventListener(
        "click",
        exportRoadmapPdf
      );
    }
  }
  catch (error) {
    console.error(
      "No se pudo cargar el roadmap:",
      error
    );

    roadmapStatus.innerHTML = `
      No se pudo cargar el roadmap dinámico.
      <a
        href="${ROADMAP_URL}"
        target="_blank"
        rel="noreferrer"
      >
        Abrir ROADMAP.md
      </a>
    `;

    roadmapGrid.innerHTML =
      "";
  }
}


roadmapFilters.forEach(
  (button) => {
    button.addEventListener(
      "click",
      () => {
        activeRoadmapFilter =
          button.dataset.roadmapFilter;

        selectedRoadmapVersion =
          null;

        roadmapDetail.hidden =
          true;

        roadmapDetail.innerHTML =
          "";

        roadmapFilters.forEach(
          (candidate) => {
            const active =
              candidate === button;

            candidate.classList.toggle(
              "active",
              active
            );

            candidate.setAttribute(
              "aria-pressed",
              String(active)
            );
          }
        );

        const reduceMotion =
          window.matchMedia(
            "(prefers-reduced-motion: reduce)"
          ).matches;

        if (reduceMotion) {
          renderRoadmapGrid();
          return;
        }

        roadmapGrid.classList.add(
          "roadmap-grid-leaving"
        );

        window.setTimeout(
          () => {
            renderRoadmapGrid();

            roadmapGrid.classList.remove(
              "roadmap-grid-leaving"
            );

            roadmapGrid.classList.add(
              "roadmap-grid-entering"
            );

            window.setTimeout(
              () => {
                roadmapGrid.classList.remove(
                  "roadmap-grid-entering"
                );
              },
              260
            );
          },
          130
        );
      }
    );
  }
);


loadRoadmap();
