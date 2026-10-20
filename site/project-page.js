"use strict";

const PROJECT_PAGES_URL = "./project-config.json";

const root =
  document.querySelector(
    "#projectPageRoot"
  );


function createElement(
  tagName,
  className = "",
  text = ""
) {
  const node =
    document.createElement(
      tagName
    );

  if (className) {
    node.className =
      className;
  }

  if (text !== "") {
    node.textContent =
      text;
  }

  return node;
}


function createLink(
  data,
  className = ""
) {
  const anchor =
    createElement(
      "a",
      className,
      data.label
    );

  anchor.href =
    data.url;

  if (data.external) {
    anchor.target =
      "_blank";

    anchor.rel =
      "noreferrer";
  }

  return anchor;
}


function requireString(
  value,
  field,
  projectId
) {
  if (
    typeof value !== "string" ||
    !value.trim()
  ) {
    throw new Error(
      `${projectId}: ${field} es obligatorio.`
    );
  }
}


function validatePage(page) {
  requireString(
    page.id,
    "id",
    "project-page"
  );

  requireString(
    page.title,
    "title",
    page.id
  );

  requireString(
    page.theme,
    "theme",
    page.id
  );

  if (
    !page.logo?.src ||
    !page.hero ||
    !Array.isArray(
      page.hero.actions
    ) ||
    !Array.isArray(
      page.hero.meta
    ) ||
    !Array.isArray(
      page.features
    ) ||
    !page.release ||
    !page.roadmap ||
    !page.nextRelease
  ) {
    throw new Error(
      `${page.id}: configuración de portal incompleta.`
    );
  }
}


function configureDocument(page) {
  document.title =
    page.documentTitle ||
    `${page.title} · RobDev512`;

  const description =
    document.querySelector(
      'meta[name="description"]'
    );

  if (description) {
    description.content =
      page.metaDescription ||
      page.hero.description;
  }

  document.body.className =
    page.theme;
}


function renderHeader(page) {
  const header =
    createElement(
      "header",
      "site-header"
    );

  const brand =
    createLink(
      {
        label: "RobDev512",
        url: "https://robdev512.github.io/",
        external: false
      },
      "site-brand"
    );

  brand.setAttribute(
    "aria-label",
    "Volver al Hub de RobDev512"
  );

  const dot =
    createElement(
      "span",
      "brand-dot"
    );

  brand.prepend(dot);

  const nav =
    createElement(
      "nav",
      "site-nav"
    );

  nav.setAttribute(
    "aria-label",
    "Navegación principal"
  );

  nav.append(
    createLink(
      {
        label: "Versión",
        url: "#version",
        external: false
      }
    ),
    createLink(
      {
        label: "Roadmap",
        url: "#roadmap-explorer",
        external: false
      }
    )
  );

  if (page.repository) {
    nav.append(
      createLink(
        page.repository
      )
    );
  }

  header.append(
    brand,
    nav
  );

  return header;
}


function renderHero(page) {
  const section =
    createElement(
      "section",
      "hero"
    );

  const copy =
    createElement(
      "div",
      "hero-copy"
    );

  copy.append(
    createElement(
      "span",
      "eyebrow",
      page.eyebrow
    )
  );

  const title =
    createElement(
      "h1"
    );

  const lines =
    page.hero.titleLines?.length
      ? page.hero.titleLines
      : [page.title];

  lines.forEach(
    (line, index) => {
      if (index > 0) {
        title.append(
          document.createElement(
            "br"
          )
        );
      }

      const span =
        createElement(
          "span",
          index === lines.length - 1
            ? "hero-title-accent"
            : "",
          line
        );

      title.append(span);
    }
  );

  const titleRow =
    createElement(
      "div",
      "hero-title-row"
    );

  if (page.hero.titleLogo?.src) {
    const titleLogo =
      document.createElement(
        "img"
      );

    titleLogo.className =
      "hero-title-logo";

    titleLogo.src =
      page.hero.titleLogo.src;

    titleLogo.alt =
      page.hero.titleLogo.alt ||
      "";

    titleRow.append(
      titleLogo
    );
  }

  titleRow.append(
    title
  );

  copy.append(
    titleRow,
    createElement(
      "p",
      "hero-lead",
      page.hero.description
    )
  );

  const actions =
    createElement(
      "div",
      "hero-actions"
    );

  for (
    const action
    of page.hero.actions
  ) {
    const style =
      action.style === "primary"
        ? "btn-primary"
        : "btn-secondary";

    actions.append(
      createLink(
        action,
        `btn ${style}`
      )
    );
  }

  copy.append(actions);

  const meta =
    createElement(
      "div",
      "hero-meta"
    );

  for (
    const item
    of page.hero.meta
  ) {
    const cell =
      document.createElement(
        "div"
      );

    cell.append(
      createElement(
        "strong",
        "",
        item.strong
      ),
      createElement(
        "span",
        "",
        item.small
      )
    );

    meta.append(cell);
  }

  copy.append(meta);

  const visual =
    createElement(
      "div",
      "hero-visual"
    );

  visual.setAttribute(
    "aria-hidden",
    "true"
  );

  visual.append(
    createElement(
      "div",
      "orbit orbit-a"
    ),
    createElement(
      "div",
      "orbit orbit-b"
    ),
    createElement(
      "div",
      "orbit orbit-c"
    )
  );

  const logoWrap =
    createElement(
      "div",
      "hero-logo-wrap"
    );

  const logo =
    document.createElement(
      "img"
    );

  logo.src =
    page.logo.src;

  logo.alt =
    page.logo.alt ||
    "";

  logoWrap.append(logo);

  visual.append(
    logoWrap,
    createElement(
      "span",
      "satellite satellite-a"
    ),
    createElement(
      "span",
      "satellite satellite-b"
    ),
    createElement(
      "span",
      "satellite satellite-c"
    )
  );

  section.append(
    copy,
    visual
  );

  return section;
}


function renderFeatureStrip(page) {
  const section =
    createElement(
      "section",
      "feature-strip"
    );

  section.setAttribute(
    "aria-label",
    "Características principales"
  );

  page.features
    .slice(0, 4)
    .forEach(
      (feature, index) => {
        const article =
          document.createElement(
            "article"
          );

        article.append(
          createElement(
            "span",
            "feature-number",
            String(
              index + 1
            ).padStart(2, "0")
          ),
          createElement(
            "h2",
            "",
            feature.title
          ),
          createElement(
            "p",
            "",
            feature.text
          )
        );

        section.append(article);
      }
    );

  return section;
}


function renderRelease(page) {
  const section =
    createElement(
      "section",
      "section-grid"
    );

  section.id =
    "version";

  const heading =
    createElement(
      "div",
      "section-heading"
    );

  heading.append(
    createElement(
      "span",
      "section-kicker",
      page.release.kicker
    ),
    createElement(
      "h2",
      "",
      page.release.version
    ),
    createElement(
      "p",
      "",
      page.release.summary
    )
  );

  const card =
    createElement(
      "div",
      "release-card"
    );

  card.append(
    createElement(
      "span",
      "status-pill",
      page.release.status
    ),
    createElement(
      "h3",
      "",
      page.release.title
    )
  );

  const list =
    document.createElement(
      "ul"
    );

  for (
    const item
    of page.release.items
  ) {
    list.append(
      createElement(
        "li",
        "",
        item
      )
    );
  }

  card.append(list);

  if (page.release.link) {
    card.append(
      createLink(
        page.release.link,
        "text-link"
      )
    );
  }

  section.append(
    heading,
    card
  );

  return section;
}


function renderRoadmap(page) {
  const section =
    createElement(
      "section",
      "roadmap-section"
    );

  section.id =
    "roadmap-explorer";

  const heading =
    createElement(
      "div",
      "section-heading roadmap-heading"
    );

  heading.append(
    createElement(
      "span",
      "section-kicker",
      page.roadmap.kicker
    ),
    createElement(
      "h2",
      "",
      page.roadmap.title
    ),
    createElement(
      "p",
      "",
      page.roadmap.description
    )
  );

  const toolbar =
    createElement(
      "div",
      "roadmap-toolbar"
    );

  toolbar.setAttribute(
    "aria-label",
    "Filtros del roadmap"
  );

  const filters = [
    ["all", "Todas"],
    ["applied", "Aplicadas"],
    ["development", "En desarrollo"],
    ["next", "Siguiente"],
    ["pending", "Pendientes"],
    ["vision", "Visión"]
  ];

  filters.forEach(
    ([value, label], index) => {
      const button =
        createElement(
          "button",
          `roadmap-filter${
            index === 0
              ? " active"
              : ""
          }`,
          label
        );

      button.type =
        "button";

      button.dataset.roadmapFilter =
        value;

      button.setAttribute(
        "aria-pressed",
        String(
          index === 0
        )
      );

      toolbar.append(button);
    }
  );

  const exportButton =
    createElement(
      "button",
      "roadmap-filter roadmap-export-button",
      "Exportar PDF"
    );

  exportButton.type =
    "button";

  exportButton.id =
    "roadmapPdfExport";

  exportButton.title =
    "Descargar una copia PDF del roadmap";

  toolbar.append(
    exportButton
  );


  const status =
    createElement(
      "p",
      "roadmap-load-status",
      "Preparando roadmap…"
    );

  status.id =
    "roadmapLoadStatus";

  const grid =
    createElement(
      "div",
      "roadmap-live-grid"
    );

  grid.id =
    "roadmapGrid";

  const detail =
    createElement(
      "article",
      "roadmap-detail"
    );

  detail.id =
    "roadmapDetail";

  detail.hidden =
    true;

  section.append(
    heading,
    toolbar,
    status,
    grid,
    detail
  );

  return section;
}


function renderNextRelease(page) {
  const section =
    createElement(
      "section",
      "next-release"
    );

  const heading =
    document.createElement(
      "div"
    );

  heading.append(
    createElement(
      "span",
      "section-kicker",
      page.nextRelease.kicker
    ),
    createElement(
      "h2",
      "",
      page.nextRelease.title
    )
  );

  section.append(
    heading,
    createElement(
      "p",
      "",
      page.nextRelease.text
    )
  );

  return section;
}


function renderFooter(page) {
  const footer =
    document.createElement(
      "footer"
    );

  footer.append(
    createElement(
      "span",
      "",
      page.footer.left
    )
  );

  if (page.footer.right) {
    footer.append(
      createLink(
        page.footer.right
      )
    );
  }

  return footer;
}


function enablePortalMotion() {
  const reduceMotion =
    window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

  const revealTargets =
    document.querySelectorAll(
      [
        ".hero-copy",
        ".hero-visual",
        ".feature-strip article",
        ".section-grid > *",
        ".roadmap-heading",
        ".roadmap-toolbar",
        ".roadmap-load-status",
        ".next-release",
        "footer"
      ].join(",")
    );

  if (reduceMotion) {
    revealTargets.forEach(
      (target) => {
        target.classList.add(
          "reveal-visible"
        );
      }
    );
  }
  else {
    const observer =
      new IntersectionObserver(
        (entries) => {
          entries.forEach(
            (entry) => {
              if (
                !entry.isIntersecting
              ) {
                return;
              }

              entry.target.classList.add(
                "reveal-visible"
              );

              observer.unobserve(
                entry.target
              );
            }
          );
        },
        {
          threshold: 0.12,
          rootMargin:
            "0px 0px -28px 0px"
        }
      );

    revealTargets.forEach(
      (target, index) => {
        target.classList.add(
          "reveal-ready"
        );

        target.style.setProperty(
          "--reveal-delay",
          `${Math.min(
            index * 35,
            210
          )}ms`
        );

        observer.observe(
          target
        );
      }
    );
  }

  document
    .querySelectorAll(
      ".release-card, .next-release, .feature-strip article"
    )
    .forEach(
      (target) => {
        target.addEventListener(
          "pointermove",
          (event) => {
            const rect =
              target.getBoundingClientRect();

            target.style.setProperty(
              "--pointer-x",
              `${event.clientX - rect.left}px`
            );

            target.style.setProperty(
              "--pointer-y",
              `${event.clientY - rect.top}px`
            );

            target.classList.add(
              "pointer-active"
            );
          }
        );

        target.addEventListener(
          "pointerleave",
          () => {
            target.classList.remove(
              "pointer-active"
            );
          }
        );
      }
    );
}




/* =========================================================
   FINAL MOTION LAYER
   ========================================================= */

function installScrollProgress() {
  if (
    document.querySelector(
      ".scroll-progress"
    )
  ) {
    return;
  }

  const progress =
    createElement(
      "div",
      "scroll-progress"
    );

  progress.setAttribute(
    "aria-hidden",
    "true"
  );

  document.body.append(
    progress
  );

  const update = () => {
    const maxScroll =
      document.documentElement.scrollHeight -
      window.innerHeight;

    const ratio =
      maxScroll > 0
        ? Math.min(
            1,
            Math.max(
              0,
              window.scrollY /
              maxScroll
            )
          )
        : 0;

    progress.style.transform =
      `scaleX(${ratio})`;
  };

  update();

  window.addEventListener(
    "scroll",
    update,
    {
      passive: true
    }
  );

  window.addEventListener(
    "resize",
    update
  );
}


function installRippleFeedback() {
  if (
    document.body.dataset.rippleReady ===
    "true"
  ) {
    return;
  }

  document.body.dataset.rippleReady =
    "true";

  document.addEventListener(
    "pointerdown",
    (event) => {
      const target =
        event.target.closest(
          [
            ".btn",
            ".site-nav a",
            ".roadmap-filter",
            ".roadmap-detail-close",
            ".text-link",
            "footer a"
          ].join(",")
        );

      if (!target) {
        return;
      }

      const rect =
        target.getBoundingClientRect();

      const size =
        Math.max(
          rect.width,
          rect.height
        ) * 1.7;

      const ripple =
        createElement(
          "span",
          "ui-ripple"
        );

      ripple.style.width =
        `${size}px`;

      ripple.style.height =
        `${size}px`;

      ripple.style.left =
        `${event.clientX -
        rect.left -
        size / 2}px`;

      ripple.style.top =
        `${event.clientY -
        rect.top -
        size / 2}px`;

      target.append(ripple);

      window.setTimeout(
        () => {
          ripple.remove();
        },
        620
      );
    }
  );
}


function installHeroParallax() {
  const hero =
    document.querySelector(
      ".hero"
    );

  const visual =
    document.querySelector(
      ".hero-visual"
    );

  if (
    !hero ||
    !visual ||
    window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches
  ) {
    return;
  }

  const reset = () => {
    visual.style.setProperty(
      "--parallax-logo-x",
      "0px"
    );

    visual.style.setProperty(
      "--parallax-logo-y",
      "0px"
    );

    visual.style.setProperty(
      "--parallax-orbit-x",
      "0px"
    );

    visual.style.setProperty(
      "--parallax-orbit-y",
      "0px"
    );

    visual.style.setProperty(
      "--parallax-satellite-x",
      "0px"
    );

    visual.style.setProperty(
      "--parallax-satellite-y",
      "0px"
    );
  };

  hero.addEventListener(
    "pointermove",
    (event) => {
      const rect =
        hero.getBoundingClientRect();

      const x =
        (
          event.clientX -
          rect.left
        ) /
        rect.width -
        .5;

      const y =
        (
          event.clientY -
          rect.top
        ) /
        rect.height -
        .5;

      visual.style.setProperty(
        "--parallax-logo-x",
        `${x * 16}px`
      );

      visual.style.setProperty(
        "--parallax-logo-y",
        `${y * 12}px`
      );

      visual.style.setProperty(
        "--parallax-orbit-x",
        `${x * -9}px`
      );

      visual.style.setProperty(
        "--parallax-orbit-y",
        `${y * -7}px`
      );

      visual.style.setProperty(
        "--parallax-satellite-x",
        `${x * 22}px`
      );

      visual.style.setProperty(
        "--parallax-satellite-y",
        `${y * 16}px`
      );
    }
  );

  hero.addEventListener(
    "pointerleave",
    reset
  );

  reset();
}


function installFinalMotionLayer() {
  installScrollProgress();
  installRippleFeedback();
  installHeroParallax();
}


function loadRoadmapModule() {
  const script =
    document.createElement(
      "script"
    );

  script.src =
    "./project-roadmap.js";

  script.defer =
    true;

  document.body.append(
    script
  );
}


function renderPage(page) {
  configureDocument(page);

  const shell =
    createElement(
      "div",
      "page-shell"
    );

  shell.append(
    renderHeader(page)
  );

  const main =
    document.createElement(
      "main"
    );

  main.append(
    renderHero(page),
    renderFeatureStrip(page),
    renderRelease(page),
    renderRoadmap(page),
    renderNextRelease(page)
  );

  shell.append(
    main,
    renderFooter(page)
  );

  root.replaceChildren(
    shell
  );

  loadRoadmapModule();

  requestAnimationFrame(
    () => {
      enablePortalMotion();
      installFinalMotionLayer();
    }
  );
}


function renderError(message) {
  const shell =
    createElement(
      "div",
      "page-shell"
    );

  const section =
    createElement(
      "section",
      "page-error"
    );

  section.append(
    createElement(
      "span",
      "section-kicker",
      "Página de proyecto"
    ),
    createElement(
      "h1",
      "",
      "No se pudo cargar el proyecto"
    ),
    createElement(
      "p",
      "",
      message
    ),
    createLink(
      {
        label: "Volver al Hub",
        url: "https://robdev512.github.io/",
        external: false
      },
      "btn btn-secondary"
    )
  );

  shell.append(section);

  root.replaceChildren(
    shell
  );
}


async function loadPage() {
  if (!root) {
    throw new Error(
      "No existe #projectPageRoot."
    );
  }

  const projectId =
    document.body.dataset.projectId;

  requireString(
    projectId,
    "data-project-id",
    "page"
  );

  const response =
    await fetch(
      PROJECT_PAGES_URL,
      {
        cache: "no-store"
      }
    );

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status} al cargar ${PROJECT_PAGES_URL}`
    );
  }

  const catalog =
    await response.json();

  if (
    catalog.schemaVersion !== 2 ||
    !Array.isArray(
      catalog.pages
    )
  ) {
    throw new Error(
      "project-pages.json no tiene un formato compatible."
    );
  }

  const page =
    catalog.pages.find(
      (candidate) =>
        candidate.id ===
        projectId
    );

  if (!page) {
    throw new Error(
      `No existe configuración para "${projectId}".`
    );
  }

  validatePage(page);
  renderPage(page);
}


loadPage().catch(
  (error) => {
    console.error(
      "No se pudo cargar la página del proyecto:",
      error
    );

    renderError(
      error.message
    );
  }
);
