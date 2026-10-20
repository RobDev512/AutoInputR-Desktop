"use strict";

(function roadmapPdfFactory(global) {

  const PAGE_WIDTH = 595.28;
  const PAGE_HEIGHT = 841.89;

  const MARGIN = 42;
  const CONTENT_WIDTH =
    PAGE_WIDTH - MARGIN * 2;

  const DARK = [0.035, 0.060, 0.090];
  const PANEL = [0.060, 0.090, 0.130];
  const PANEL_2 = [0.078, 0.115, 0.160];
  const TEXT = [0.93, 0.96, 1.00];
  const MUTED = [0.60, 0.67, 0.75];
  const LINE = [0.16, 0.20, 0.25];
  const GREEN = [0.39, 0.88, 0.64];
  const BLUE = [0.32, 0.76, 0.96];
  const AMBER = [1.00, 0.68, 0.27];
  const PURPLE = [0.68, 0.59, 0.98];


  function cleanText(value = "") {
    return String(value)
      .replace(/\u00a0/g, " ")
      .replace(/[–—]/g, "-")
      .replace(/→/g, "->")
      .replace(/←/g, "<-")
      .replace(/•/g, "-")
      .replace(/\t/g, "    ")
      .replace(/\s+/g, " ")
      .trim();
  }


  function stripInlineMarkdown(value = "") {
    return cleanText(value)
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/\*([^*]+)\*/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
  }


  function safeFilename(value = "roadmap.pdf") {
    let name =
      cleanText(value)
        .replace(/[<>:"/\\|?*]+/g, "-")
        .replace(/\s+/g, "-");

    if (!name.toLowerCase().endsWith(".pdf")) {
      name += ".pdf";
    }

    return name;
  }


  function datedFilename(filename) {
    const safe =
      safeFilename(filename);

    const date =
      new Date()
        .toISOString()
        .slice(0, 10);

    return safe.replace(
      /\.pdf$/i,
      `-${date}.pdf`
    );
  }


  function parseRoadmap(markdown) {
    const lines =
      String(markdown)
        .replace(/\r/g, "")
        .split("\n");

    const items = [];
    const intro = [];
    let current = null;
    let group = null;

    const phaseHeading =
      /^#{1,3}\s+(Fase\s+\d+(?:\.\d+)?\s*[-—]\s*.+)$/i;

    const versionHeading =
      /^#{1,3}\s+(v\d+(?:\.\d+){1,3}\s*[-—]\s*.+)$/i;

    const genericRoadmapTitle =
      /^#\s+ROADMAP\b/i;


    function pushCurrent() {
      if (!current) {
        return;
      }

      if (group) {
        current.groups.push(group);
        group = null;
      }

      items.push(current);
      current = null;
    }


    for (const raw of lines) {
      const rawLine =
        raw.replace(/\s+$/g, "");

      const line =
        rawLine.trim();

      if (!line) {
        continue;
      }

      if (genericRoadmapTitle.test(line)) {
        continue;
      }

      const headingMatch =
        line.match(phaseHeading) ||
        line.match(versionHeading);

      if (headingMatch) {
        pushCurrent();

        const heading =
          stripInlineMarkdown(
            headingMatch[1]
          );

        let label = heading;
        let title = heading;

        const split =
          heading.match(
            /^(.+?)\s*-\s*(.+)$/
          );

        if (split) {
          label =
            split[1].trim();

          title =
            split[2].trim();
        }

        current = {
          label,
          title,
          status: "",
          paragraphs: [],
          fields: [],
          groups: [],
          quotes: []
        };

        group = null;
        continue;
      }

      const subHeading =
        line.match(
          /^#{1,4}\s+(.+)$/
        );

      if (subHeading && current) {
        if (group) {
          current.groups.push(group);
        }

        group = {
          title:
            stripInlineMarkdown(
              subHeading[1]
            ),
          items: [],
          paragraphs: []
        };

        continue;
      }

      const field =
        line.match(
          /^\*\*([^*]+):\*\*\s*(.*)$/
        );

      if (field) {
        const label =
          stripInlineMarkdown(
            field[1]
          );

        const value =
          stripInlineMarkdown(
            field[2]
          );

        if (current) {
          current.fields.push({
            label,
            value
          });

          if (
            label
              .toLowerCase()
              .includes("estado")
          ) {
            current.status = value;
          }
        }
        else {
          intro.push(
            `${label}: ${value}`
          );
        }

        continue;
      }

      if (/^---+$/.test(line)) {
        continue;
      }

      if (line.startsWith(">")) {
        const text =
          stripInlineMarkdown(
            line.replace(
              /^>\s*/,
              ""
            )
          );

        if (current) {
          current.quotes.push(text);
        }
        else {
          intro.push(text);
        }

        continue;
      }

      const bullet =
        line.match(
          /^[-*]\s+(.+)$/
        );

      if (bullet) {
        const text =
          stripInlineMarkdown(
            bullet[1]
          );

        if (current) {
          if (!group) {
            group = {
              title: "Puntos clave",
              items: [],
              paragraphs: []
            };
          }

          group.items.push(text);
        }
        else {
          intro.push(text);
        }

        continue;
      }

      const paragraph =
        stripInlineMarkdown(line);

      const indentedContinuation =
        /^\s{2,}/.test(rawLine);

      if (
        current &&
        group &&
        indentedContinuation &&
        group.items.length
      ) {
        const lastIndex =
          group.items.length - 1;

        group.items[lastIndex] =
          `${group.items[lastIndex]} ${paragraph}`;

        continue;
      }

      if (current) {
        if (group) {
          group.paragraphs.push(
            paragraph
          );
        }
        else {
          current.paragraphs.push(
            paragraph
          );
        }
      }
      else {
        intro.push(paragraph);
      }
    }

    pushCurrent();

    return {
      intro,
      items
    };
  }


  function roadmapItemsToMarkdown(items, title) {
    const lines = [
      `# ROADMAP - ${title}`,
      ""
    ];

    for (const item of items) {
      const codename =
        item.codename
          ? ` - ${item.codename}`
          : "";

      lines.push(
        `## ${item.version}${codename} - ${item.title || ""}`
      );

      if (item.preRelease) {
        lines.push(
          `**Pre-release:** ${item.preRelease}`
        );
      }

      if (
        item.statusLabel ||
        item.status
      ) {
        lines.push(
          `**Estado:** ${
            item.statusLabel ||
            item.status
          }`
        );
      }

      if (item.summary) {
        lines.push(
          "",
          item.summary
        );
      }

      const groups = [
        ["Implementado", item.implemented],
        ["En desarrollo", item.inProgress],
        ["Pendiente", item.pending],
        ["Detalle", item.details]
      ];

      for (
        const [heading, values]
        of groups
      ) {
        if (
          !Array.isArray(values) ||
          !values.length
        ) {
          continue;
        }

        lines.push(
          "",
          `### ${heading}`
        );

        for (const value of values) {
          lines.push(
            `- ${value}`
          );
        }
      }

      lines.push(
        "",
        "---",
        ""
      );
    }

    return lines.join("\n");
  }


  function extractArrayLiteral(
    source,
    variableName = "roadmapItems"
  ) {
    const marker =
      `const ${variableName}`;

    const markerIndex =
      source.indexOf(marker);

    if (markerIndex < 0) {
      throw new Error(
        `No se encontró ${variableName} en el script.`
      );
    }

    const openIndex =
      source.indexOf(
        "[",
        markerIndex
      );

    if (openIndex < 0) {
      throw new Error(
        `No se encontró el arreglo ${variableName}.`
      );
    }

    let depth = 0;
    let quote = null;
    let escaped = false;

    for (
      let index = openIndex;
      index < source.length;
      index += 1
    ) {
      const char =
        source[index];

      if (quote) {
        if (escaped) {
          escaped = false;
          continue;
        }

        if (char === "\\") {
          escaped = true;
          continue;
        }

        if (char === quote) {
          quote = null;
        }

        continue;
      }

      if (
        char === '"' ||
        char === "'" ||
        char === "`"
      ) {
        quote = char;
        continue;
      }

      if (char === "[") {
        depth += 1;
      }
      else if (char === "]") {
        depth -= 1;

        if (depth === 0) {
          return source.slice(
            openIndex,
            index + 1
          );
        }
      }
    }

    throw new Error(
      `No se pudo cerrar el arreglo ${variableName}.`
    );
  }


  function parseRoadmapScript(
    source,
    variableName = "roadmapItems"
  ) {
    const literal =
      extractArrayLiteral(
        source,
        variableName
      );

    const values =
      Function(
        `"use strict"; return (${literal});`
      )();

    if (!Array.isArray(values)) {
      throw new Error(
        "El roadmap embebido no produjo un arreglo."
      );
    }

    return values;
  }


  function themeForTitle(title = "") {
    const value =
      cleanText(title)
        .toLowerCase();

    if (value.includes("orbishot")) {
      return {
        accent: [1.00, 0.48, 0.00],
        accentSoft: [1.00, 0.70, 0.28],
        alt: [0.25, 0.82, 1.00]
      };
    }

    if (value.includes("labnotes")) {
      return {
        accent: [0.34, 0.67, 1.00],
        accentSoft: [0.57, 0.79, 1.00],
        alt: [0.58, 0.93, 1.00]
      };
    }

    if (value.includes("convertidor")) {
      return {
        accent: [0.50, 0.40, 1.00],
        accentSoft: [0.72, 0.66, 1.00],
        alt: [0.31, 0.82, 1.00]
      };
    }

    if (value.includes("tecnet")) {
      return {
        accent: [0.18, 0.83, 0.63],
        accentSoft: [0.52, 0.90, 0.79],
        alt: [0.37, 0.70, 1.00]
      };
    }

    return {
      accent: [0.21, 0.77, 0.94],
      accentSoft: [0.52, 0.88, 1.00],
      alt: [1.00, 0.60, 0.24]
    };
  }


  function statusKind(status = "") {
    const value =
      cleanText(status)
        .toLowerCase();

    if (
      value.includes("complet") ||
      value.includes("aplicad") ||
      value.includes("publicad") ||
      value.includes("estable")
    ) {
      return "done";
    }

    if (
      value.includes("desarrollo") ||
      value.includes("parcial") ||
      value.includes("current") ||
      value.includes("actual")
    ) {
      return "progress";
    }

    if (
      value.includes("siguiente") ||
      value.includes("próxima") ||
      value.includes("proxima") ||
      value.includes("pendiente") ||
      value.includes("planead")
    ) {
      return "planned";
    }

    if (
      value.includes("visión") ||
      value.includes("vision") ||
      value.includes("largo plazo")
    ) {
      return "future";
    }

    return "neutral";
  }


  function statusColor(kind) {
    switch (kind) {
      case "done":
        return GREEN;
      case "progress":
        return BLUE;
      case "planned":
        return AMBER;
      case "future":
        return PURPLE;
      default:
        return MUTED;
    }
  }


  function encodeWinAnsi(value) {
    const replacements =
      new Map([
        [0x20ac, 0x80],
        [0x201a, 0x82],
        [0x0192, 0x83],
        [0x201e, 0x84],
        [0x2026, 0x85],
        [0x2020, 0x86],
        [0x2021, 0x87],
        [0x02c6, 0x88],
        [0x2030, 0x89],
        [0x0160, 0x8a],
        [0x2039, 0x8b],
        [0x0152, 0x8c],
        [0x017d, 0x8e],
        [0x2018, 0x91],
        [0x2019, 0x92],
        [0x201c, 0x93],
        [0x201d, 0x94],
        [0x2022, 0x95],
        [0x2013, 0x96],
        [0x2014, 0x97],
        [0x02dc, 0x98],
        [0x2122, 0x99],
        [0x0161, 0x9a],
        [0x203a, 0x9b],
        [0x0153, 0x9c],
        [0x017e, 0x9e],
        [0x0178, 0x9f]
      ]);

    const bytes = [];

    for (const char of value) {
      const code =
        char.codePointAt(0);

      if (code <= 0xff) {
        bytes.push(code);
      }
      else if (
        replacements.has(code)
      ) {
        bytes.push(
          replacements.get(code)
        );
      }
      else {
        bytes.push(0x3f);
      }
    }

    return new Uint8Array(bytes);
  }


  function ascii(value) {
    return new TextEncoder()
      .encode(value);
  }


  function concatBytes(chunks) {
    const length =
      chunks.reduce(
        (total, chunk) =>
          total + chunk.length,
        0
      );

    const output =
      new Uint8Array(length);

    let offset = 0;

    for (const chunk of chunks) {
      output.set(
        chunk,
        offset
      );

      offset +=
        chunk.length;
    }

    return output;
  }


  function escapePdfText(value) {
    return cleanText(value)
      .replace(/\\/g, "\\\\")
      .replace(/\(/g, "\\(")
      .replace(/\)/g, "\\)");
  }


  function rgb(color) {
    return color
      .map((value) =>
        Number(value)
          .toFixed(3)
      )
      .join(" ");
  }


  function drawText({
    text,
    x,
    y,
    size,
    bold = false,
    color = TEXT
  }) {
    const prefix =
      [
        "BT\n",
        `${rgb(color)} rg\n`,
        `/${bold ? "F2" : "F1"} ${size} Tf\n`,
        `1 0 0 1 ${x.toFixed(2)} ${y.toFixed(2)} Tm\n`,
        "("
      ].join("");

    const suffix =
      ") Tj\nET\n";

    return concatBytes([
      ascii(prefix),
      encodeWinAnsi(
        escapePdfText(text)
      ),
      ascii(suffix)
    ]);
  }


  function rect({
    x,
    y,
    width,
    height,
    fill,
    stroke = null,
    strokeWidth = 1
  }) {
    const commands = [];

    if (fill) {
      commands.push(
        `${rgb(fill)} rg`
      );
    }

    if (stroke) {
      commands.push(
        `${rgb(stroke)} RG`,
        `${strokeWidth} w`
      );
    }

    commands.push(
      `${x.toFixed(2)} ${y.toFixed(2)} ${width.toFixed(2)} ${height.toFixed(2)} re`
    );

    if (fill && stroke) {
      commands.push("B");
    }
    else if (fill) {
      commands.push("f");
    }
    else if (stroke) {
      commands.push("S");
    }

    return ascii(
      commands.join("\n") +
      "\n"
    );
  }


  function roundedRect({
    x,
    y,
    width,
    height,
    radius = 12,
    fill,
    stroke = null,
    strokeWidth = 1
  }) {
    const k = 0.5522847498;
    const r =
      Math.min(
        radius,
        width / 2,
        height / 2
      );

    const c =
      r * k;

    const path = [
      `${(x + r).toFixed(2)} ${y.toFixed(2)} m`,
      `${(x + width - r).toFixed(2)} ${y.toFixed(2)} l`,
      `${(x + width - r + c).toFixed(2)} ${y.toFixed(2)} ${(x + width).toFixed(2)} ${(y + r - c).toFixed(2)} ${(x + width).toFixed(2)} ${(y + r).toFixed(2)} c`,
      `${(x + width).toFixed(2)} ${(y + height - r).toFixed(2)} l`,
      `${(x + width).toFixed(2)} ${(y + height - r + c).toFixed(2)} ${(x + width - r + c).toFixed(2)} ${(y + height).toFixed(2)} ${(x + width - r).toFixed(2)} ${(y + height).toFixed(2)} c`,
      `${(x + r).toFixed(2)} ${(y + height).toFixed(2)} l`,
      `${(x + r - c).toFixed(2)} ${(y + height).toFixed(2)} ${x.toFixed(2)} ${(y + height - r + c).toFixed(2)} ${x.toFixed(2)} ${(y + height - r).toFixed(2)} c`,
      `${x.toFixed(2)} ${(y + r).toFixed(2)} l`,
      `${x.toFixed(2)} ${(y + r - c).toFixed(2)} ${(x + r - c).toFixed(2)} ${y.toFixed(2)} ${(x + r).toFixed(2)} ${y.toFixed(2)} c`,
      "h"
    ];

    const commands = [];

    if (fill) {
      commands.push(
        `${rgb(fill)} rg`
      );
    }

    if (stroke) {
      commands.push(
        `${rgb(stroke)} RG`,
        `${strokeWidth} w`
      );
    }

    commands.push(
      path.join("\n")
    );

    if (fill && stroke) {
      commands.push("B");
    }
    else if (fill) {
      commands.push("f");
    }
    else {
      commands.push("S");
    }

    return ascii(
      commands.join("\n") +
      "\n"
    );
  }


  function circle({
    x,
    y,
    radius,
    stroke,
    strokeWidth = 1
  }) {
    const k =
      0.5522847498;

    const c =
      radius * k;

    const path = [
      `${(x + radius).toFixed(2)} ${y.toFixed(2)} m`,
      `${(x + radius).toFixed(2)} ${(y + c).toFixed(2)} ${(x + c).toFixed(2)} ${(y + radius).toFixed(2)} ${x.toFixed(2)} ${(y + radius).toFixed(2)} c`,
      `${(x - c).toFixed(2)} ${(y + radius).toFixed(2)} ${(x - radius).toFixed(2)} ${(y + c).toFixed(2)} ${(x - radius).toFixed(2)} ${y.toFixed(2)} c`,
      `${(x - radius).toFixed(2)} ${(y - c).toFixed(2)} ${(x - c).toFixed(2)} ${(y - radius).toFixed(2)} ${x.toFixed(2)} ${(y - radius).toFixed(2)} c`,
      `${(x + c).toFixed(2)} ${(y - radius).toFixed(2)} ${(x + radius).toFixed(2)} ${(y - c).toFixed(2)} ${(x + radius).toFixed(2)} ${y.toFixed(2)} c`,
      "S"
    ];

    return ascii(
      [
        `${rgb(stroke)} RG`,
        `${strokeWidth} w`,
        ...path
      ].join("\n") +
      "\n"
    );
  }


  function line({
    x1,
    y1,
    x2,
    y2,
    color = LINE,
    width = 1
  }) {
    return ascii(
      [
        `${rgb(color)} RG`,
        `${width} w`,
        `${x1.toFixed(2)} ${y1.toFixed(2)} m`,
        `${x2.toFixed(2)} ${y2.toFixed(2)} l`,
        "S"
      ].join("\n") +
      "\n"
    );
  }


  function fitTextSize(
    text,
    maxWidth,
    preferredSize,
    minSize = 5.8,
    bold = false
  ) {
    let size =
      preferredSize;

    while (
      size > minSize &&
      measureWidth(
        text,
        size,
        bold
      ) > maxWidth
    ) {
      size -= 0.25;
    }

    return Math.max(
      minSize,
      size
    );
  }


  function compactHeaderMetrics(
    item,
    width
  ) {
    const labelWidth =
      Math.max(
        54,
        Math.min(
          width * 0.42,
          measureWidth(
            item.label,
            7.7,
            true
          ) + 20
        )
      );

    const status =
      item.status ||
      "Sin estado";

    const desiredStatusWidth =
      measureWidth(
        status,
        6.6,
        true
      ) + 18;

    const statusWidth =
      Math.max(
        58,
        Math.min(
          width * 0.60,
          desiredStatusWidth
        )
      );

    const inline =
      labelWidth +
      statusWidth +
      18 <=
      width - 26;

    return {
      labelWidth,
      statusWidth,
      inline,
      headerHeight:
        inline
          ? 46
          : 72
    };
  }


  function measureWidth(
    text,
    size,
    bold = false
  ) {
    return (
      cleanText(text).length *
      size *
      (
        bold
          ? 0.55
          : 0.50
      )
    );
  }


  function wrapText(
    text,
    maxWidth,
    size,
    bold = false
  ) {
    const cleaned =
      cleanText(text);

    if (!cleaned) {
      return [];
    }

    const words =
      cleaned.split(/\s+/);

    const lines = [];
    let current = "";

    for (const word of words) {
      const candidate =
        current
          ? `${current} ${word}`
          : word;

      if (
        measureWidth(
          candidate,
          size,
          bold
        ) <= maxWidth
      ) {
        current =
          candidate;
      }
      else {
        if (current) {
          lines.push(current);
        }

        current = word;
      }
    }

    if (current) {
      lines.push(current);
    }

    return lines;
  }


  function drawParagraph({
    commands,
    text,
    x,
    y,
    width,
    size = 10,
    lineHeight = 14,
    color = MUTED,
    bold = false
  }) {
    const lines =
      wrapText(
        text,
        width,
        size,
        bold
      );

    for (const lineText of lines) {
      commands.push(
        drawText({
          text: lineText,
          x,
          y,
          size,
          bold,
          color
        })
      );

      y -= lineHeight;
    }

    return y;
  }


  function drawBulletList({
    commands,
    items,
    x,
    y,
    width,
    size = 9.4,
    lineHeight = 13,
    color = TEXT,
    maxItems = null
  }) {
    const values =
      maxItems
        ? items.slice(
            0,
            maxItems
          )
        : items;

    for (const item of values) {
      const lines =
        wrapText(
          item,
          width - 16,
          size
        );

      commands.push(
        drawText({
          text: "-",
          x,
          y,
          size,
          bold: true,
          color
        })
      );

      let localY = y;

      for (
        let index = 0;
        index < lines.length;
        index += 1
      ) {
        commands.push(
          drawText({
            text: lines[index],
            x: x + 13,
            y: localY,
            size,
            color
          })
        );

        localY -=
          lineHeight;
      }

      y =
        localY - 3;
    }

    return y;
  }


  function pageBackground(
    commands,
    theme,
    pageNumber
  ) {
    commands.push(
      rect({
        x: 0,
        y: 0,
        width:
          PAGE_WIDTH,
        height:
          PAGE_HEIGHT,
        fill: DARK
      })
    );

    commands.push(
      circle({
        x:
          PAGE_WIDTH - 20,
        y:
          PAGE_HEIGHT - 45,
        radius: 90,
        stroke:
          theme.accent,
        strokeWidth: 0.7
      }),
      circle({
        x:
          PAGE_WIDTH - 20,
        y:
          PAGE_HEIGHT - 45,
        radius: 125,
        stroke:
          theme.alt,
        strokeWidth: 0.45
      }),
      line({
        x1: MARGIN,
        y1: 36,
        x2:
          PAGE_WIDTH -
          MARGIN,
        y2: 36,
        color: LINE,
        width: 0.6
      }),
      drawText({
        text:
          "RobDev512 · Roadmap",
        x: MARGIN,
        y: 21,
        size: 7.7,
        color: MUTED
      }),
      drawText({
        text:
          `Página ${pageNumber}`,
        x:
          PAGE_WIDTH -
          MARGIN -
          44,
        y: 21,
        size: 7.7,
        color: MUTED
      })
    );
  }


  function headerForContentPage(
    commands,
    theme,
    title,
    pageNumber
  ) {
    pageBackground(
      commands,
      theme,
      pageNumber
    );

    commands.push(
      drawText({
        text: title,
        x: MARGIN,
        y:
          PAGE_HEIGHT - 58,
        size: 9,
        bold: true,
        color:
          theme.accentSoft
      }),
      drawText({
        text:
          "ROADMAP · RESPALDO VISUAL",
        x:
          PAGE_WIDTH -
          MARGIN -
          132,
        y:
          PAGE_HEIGHT - 58,
        size: 7.2,
        bold: true,
        color: MUTED
      }),
      line({
        x1: MARGIN,
        y1:
          PAGE_HEIGHT - 72,
        x2:
          PAGE_WIDTH -
          MARGIN,
        y2:
          PAGE_HEIGHT - 72,
        color: LINE,
        width: .7
      })
    );

    return (
      PAGE_HEIGHT - 94
    );
  }


  function coverPage({
    title,
    subtitle,
    source,
    intro,
    items,
    theme,
    generatedAt
  }) {
    const commands = [];

    pageBackground(
      commands,
      theme,
      1
    );

    commands.push(
      roundedRect({
        x: MARGIN,
        y:
          PAGE_HEIGHT -
          123,
        width: 174,
        height: 27,
        radius: 13,
        fill: PANEL_2,
        stroke:
          theme.accent,
        strokeWidth: .9
      }),
      drawText({
        text:
          "RESPALDO VISUAL DEL ROADMAP",
        x:
          MARGIN + 14,
        y:
          PAGE_HEIGHT -
          113,
        size: 8.4,
        bold: true,
        color:
          theme.accentSoft
      })
    );

    let y =
      PAGE_HEIGHT - 184;

    y =
      drawParagraph({
        commands,
        text: title,
        x: MARGIN,
        y,
        width: 430,
        size: 33,
        lineHeight: 37,
        color: TEXT,
        bold: true
      });

    y -= 5;

    const introText =
      subtitle ||
      intro
        .slice(0, 2)
        .join(" ") ||
      "Roadmap del proyecto";

    y =
      drawParagraph({
        commands,
        text:
          introText,
        x: MARGIN,
        y,
        width: 430,
        size: 11.3,
        lineHeight: 16.5,
        color: MUTED
      });

    const counters = {
      total:
        items.length,
      done: 0,
      progress: 0,
      planned: 0,
      future: 0
    };

    for (const item of items) {
      const kind =
        statusKind(
          item.status
        );

      if (
        Object.prototype
          .hasOwnProperty
          .call(
            counters,
            kind
          )
      ) {
        counters[kind] += 1;
      }
    }

    const stats = [
      [
        String(
          counters.total
        ),
        "VERSIONES / FASES",
        theme.accent
      ],
      [
        String(
          counters.done
        ),
        "COMPLETADAS",
        GREEN
      ],
      [
        String(
          counters.progress
        ),
        "EN DESARROLLO",
        BLUE
      ],
      [
        String(
          counters.planned +
          counters.future
        ),
        "FUTURAS",
        PURPLE
      ]
    ];

    const gap = 10;
    const statWidth =
      (
        CONTENT_WIDTH -
        gap * 3
      ) / 4;

    let statX =
      MARGIN;

    for (
      const [
        value,
        label,
        color
      ]
      of stats
    ) {
      commands.push(
        roundedRect({
          x: statX,
          y: 424,
          width:
            statWidth,
          height: 86,
          radius: 14,
          fill: PANEL,
          stroke: LINE,
          strokeWidth: .75
        }),
        drawText({
          text: value,
          x:
            statX + 13,
          y: 470,
          size: 23,
          bold: true,
          color
        }),
        drawText({
          text: label,
          x:
            statX + 13,
          y: 445,
          size: 7.3,
          bold: true,
          color: MUTED
        })
      );

      statX +=
        statWidth + gap;
    }

    commands.push(
      roundedRect({
        x: MARGIN,
        y: 250,
        width:
          CONTENT_WIDTH,
        height: 138,
        radius: 18,
        fill: PANEL,
        stroke: LINE,
        strokeWidth: .75
      }),
      drawText({
        text:
          "METADATOS DEL RESPALDO",
        x:
          MARGIN + 17,
        y: 366,
        size: 8.5,
        bold: true,
        color:
          theme.accentSoft
      }),
      drawText({
        text:
          "GENERADO",
        x:
          MARGIN + 17,
        y: 337,
        size: 7.2,
        bold: true,
        color: MUTED
      }),
      drawText({
        text:
          generatedAt,
        x:
          MARGIN + 17,
        y: 320,
        size: 9.4,
        color: TEXT
      }),
      drawText({
        text:
          "FUENTE",
        x:
          MARGIN + 17,
        y: 292,
        size: 7.2,
        bold: true,
        color: MUTED
      })
    );

    drawParagraph({
      commands,
      text:
        source ||
        "Roadmap interno del proyecto",
      x:
        MARGIN + 17,
      y: 275,
      width:
        CONTENT_WIDTH - 34,
      size: 8.5,
      lineHeight: 12,
      color: TEXT
    });

    commands.push(
      roundedRect({
        x: MARGIN,
        y: 135,
        width:
          CONTENT_WIDTH,
        height: 78,
        radius: 16,
        fill: PANEL_2,
        stroke:
          theme.accent,
        strokeWidth: .7
      }),
      drawText({
        text:
          "SNAPSHOT",
        x:
          MARGIN + 16,
        y: 188,
        size: 7.7,
        bold: true,
        color:
          theme.accentSoft
      }),
      drawText({
        text:
          "Este PDF conserva una fotografía visual del roadmap.",
        x:
          MARGIN + 16,
        y: 166,
        size: 9.3,
        color: TEXT
      }),
      drawText({
        text:
          "La fuente de verdad continúa siendo el roadmap original.",
        x:
          MARGIN + 16,
        y: 149,
        size: 9.3,
        color: MUTED
      })
    );

    return concatBytes(
      commands
    );
  }


  function estimateCardHeight(
    item,
    width
  ) {
    const header =
      compactHeaderMetrics(
        item,
        width
      );

    let height =
      header.headerHeight + 24;

    height +=
      wrapText(
        item.title,
        width - 28,
        14.2,
        true
      ).length * 17;

    const summary =
      item.paragraphs.join(
        " "
      );

    if (summary) {
      height += 7;

      height +=
        Math.min(
          3,
          wrapText(
            summary,
            width - 28,
            8.6
          ).length
        ) * 11.5;
    }

    const fields =
      item.fields.filter(
        (field) =>
          !field.label
            .toLowerCase()
            .includes("estado")
      );

    for (
      const field
      of fields.slice(0, 2)
    ) {
      height += 14;

      height +=
        Math.min(
          2,
          wrapText(
            field.value,
            width - 28,
            8
          ).length
        ) * 10.5;

      height += 4;
    }

    for (const group of item.groups) {
      height += 15;

      if (
        group.paragraphs.length
      ) {
        height +=
          Math.min(
            2,
            wrapText(
              group.paragraphs.join(" "),
              width - 28,
              7.8
            ).length
          ) * 10;
      }

      for (
        const bullet
        of group.items
      ) {
        const lines =
          Math.max(
            1,
            wrapText(
              bullet,
              width - 43,
              7.9
            ).length
          );

        height +=
          lines * 10.2 + 2;
      }

      height += 3;
    }

    return Math.max(
      112,
      height + 20
    );
  }


  function drawCompactCard({
    commands,
    item,
    theme,
    x,
    topY,
    width,
    height
  }) {
    const kind =
      statusKind(
        item.status
      );

    const statusTint =
      statusColor(kind);

    const bottomY =
      topY - height;

    commands.push(
      roundedRect({
        x,
        y: bottomY,
        width,
        height,
        radius: 14,
        fill: PANEL,
        stroke:
          [
            (
              LINE[0] +
              theme.accent[0]
            ) / 2,
            (
              LINE[1] +
              theme.accent[1]
            ) / 2,
            (
              LINE[2] +
              theme.accent[2]
            ) / 2
          ],
        strokeWidth: .7
      })
    );

    const metrics =
      compactHeaderMetrics(
        item,
        width
      );

    commands.push(
      roundedRect({
        x:
          x + 13,
        y:
          topY - 34,
        width:
          metrics.labelWidth,
        height: 22,
        radius: 11,
        fill: PANEL_2,
        stroke:
          theme.accent,
        strokeWidth: .65
      })
    );

    const labelFont =
      fitTextSize(
        item.label,
        metrics.labelWidth - 18,
        7.7,
        5.8,
        true
      );

    commands.push(
      drawText({
        text:
          item.label,
        x:
          x + 22,
        y:
          topY - 26,
        size:
          labelFont,
        bold: true,
        color:
          theme.accentSoft
      })
    );

    const status =
      item.status ||
      "Sin estado";

    const statusY =
      metrics.inline
        ? topY - 34
        : topY - 60;

    const statusX =
      metrics.inline
        ? (
            x +
            width -
            metrics.statusWidth -
            13
          )
        : (
            x +
            13
          );

    commands.push(
      roundedRect({
        x:
          statusX,
        y:
          statusY,
        width:
          metrics.statusWidth,
        height: 22,
        radius: 11,
        fill: PANEL_2,
        stroke:
          statusTint,
        strokeWidth: .65
      })
    );

    const statusFont =
      fitTextSize(
        status,
        metrics.statusWidth - 16,
        6.6,
        5.0,
        true
      );

    commands.push(
      drawText({
        text:
          status,
        x:
          statusX + 8,
        y:
          statusY + 8,
        size:
          statusFont,
        bold: true,
        color:
          statusTint
      })
    );

    let y =
      topY -
      metrics.headerHeight -
      12;

    y =
      drawParagraph({
        commands,
        text:
          item.title,
        x:
          x + 14,
        y,
        width:
          width - 28,
        size: 14.2,
        lineHeight: 17,
        color: TEXT,
        bold: true
      });

    const summary =
      item.paragraphs.join(
        " "
      );

    if (summary) {
      y -= 3;

      const summaryLines =
        wrapText(
          summary,
          width - 28,
          8.6
        ).slice(0, 3);

      for (const lineText of summaryLines) {
        if (
          y <
          bottomY + 24
        ) {
          break;
        }

        commands.push(
          drawText({
            text:
              lineText,
            x:
              x + 14,
            y,
            size: 8.6,
            color: MUTED
          })
        );

        y -= 11.5;
      }

      y -= 5;
    }

    const fields =
      item.fields.filter(
        (field) =>
          !field.label
            .toLowerCase()
            .includes("estado")
      );

    for (
      const field
      of fields.slice(0, 2)
    ) {
      if (
        y <
        bottomY + 35
      ) {
        break;
      }

      commands.push(
        drawText({
          text:
            `${field.label.toUpperCase()}:`,
          x:
            x + 14,
          y,
          size: 6.8,
          bold: true,
          color:
            theme.accentSoft
        })
      );

      y -= 10;

      const fieldLines =
        wrapText(
          field.value,
          width - 28,
          8
        ).slice(0, 2);

      for (
        const lineText
        of fieldLines
      ) {
        if (
          y <
          bottomY + 24
        ) {
          break;
        }

        commands.push(
          drawText({
            text:
              lineText,
            x:
              x + 14,
            y,
            size: 8,
            color: TEXT
          })
        );

        y -= 10.5;
      }

      y -= 4;
    }

    for (
      const group
      of item.groups
    ) {
      if (
        y <
        bottomY + 38
      ) {
        break;
      }

      commands.push(
        drawText({
          text:
            group.title
              .toUpperCase(),
          x:
            x + 14,
          y,
          size: 7,
          bold: true,
          color:
            theme.accentSoft
        })
      );

      y -= 12;

      if (
        group.paragraphs.length
      ) {
        const paragraphLines =
          wrapText(
            group.paragraphs.join(" "),
            width - 28,
            7.8
          ).slice(0, 2);

        for (
          const lineText
          of paragraphLines
        ) {
          if (
            y <
            bottomY + 24
          ) {
            break;
          }

          commands.push(
            drawText({
              text:
                lineText,
              x:
                x + 14,
              y,
              size: 7.8,
              color: MUTED
            })
          );

          y -= 10;
        }
      }

      for (
        const bullet
        of group.items
      ) {
        const bulletLines =
          wrapText(
            bullet,
            width - 43,
            7.9
          );

        const required =
          bulletLines.length *
          10.2 + 2;

        if (
          y - required <
          bottomY + 20
        ) {
          break;
        }

        commands.push(
          drawText({
            text: "-",
            x:
              x + 14,
            y,
            size: 7.9,
            bold: true,
            color:
              theme.accentSoft
          })
        );

        let localY = y;

        for (
          const lineText
          of bulletLines
        ) {
          commands.push(
            drawText({
              text:
                lineText,
              x:
                x + 25,
              y:
                localY,
              size: 7.9,
              color: TEXT
            })
          );

          localY -= 10.2;
        }

        y =
          localY - 2;
      }

      y -= 3;
    }

    return bottomY;
  }


  function fullWidthDetailPages({
    title,
    item,
    theme,
    startPageNumber
  }) {
    const pages = [];

    let pageNumber =
      startPageNumber;

    let commands = [];

    let y =
      headerForContentPage(
        commands,
        theme,
        title,
        pageNumber
      );

    const kind =
      statusKind(
        item.status
      );

    const statusTint =
      statusColor(kind);

    commands.push(
      roundedRect({
        x: MARGIN,
        y:
          y - 28,
        width: 84,
        height: 24,
        radius: 12,
        fill: PANEL_2,
        stroke:
          theme.accent,
        strokeWidth: .7
      }),
      drawText({
        text:
          item.label,
        x:
          MARGIN + 12,
        y:
          y - 19,
        size: 8,
        bold: true,
        color:
          theme.accentSoft
      })
    );

    const status =
      item.status ||
      "Sin estado";

    const statusWidth =
      Math.max(
        80,
        Math.min(
          230,
          measureWidth(
            status,
            7.2,
            true
          ) + 22
        )
      );

    commands.push(
      roundedRect({
        x:
          PAGE_WIDTH -
          MARGIN -
          statusWidth,
        y:
          y - 28,
        width:
          statusWidth,
        height: 24,
        radius: 12,
        fill: PANEL_2,
        stroke:
          statusTint,
        strokeWidth: .7
      }),
      drawText({
        text: status,
        x:
          PAGE_WIDTH -
          MARGIN -
          statusWidth +
          11,
        y:
          y - 19,
        size:
          fitTextSize(
            status,
            statusWidth - 18,
            7.2,
            5.4,
            true
          ),
        bold: true,
        color:
          statusTint
      })
    );

    y -= 53;

    y =
      drawParagraph({
        commands,
        text:
          item.title,
        x: MARGIN,
        y,
        width:
          CONTENT_WIDTH,
        size: 23,
        lineHeight: 27,
        color: TEXT,
        bold: true
      });

    const summary =
      item.paragraphs.join(" ");

    if (summary) {
      y -= 3;

      y =
        drawParagraph({
          commands,
          text: summary,
          x: MARGIN,
          y,
          width:
            CONTENT_WIDTH,
          size: 10,
          lineHeight: 14.5,
          color: MUTED
        });

      y -= 8;
    }

    for (const group of item.groups) {
      const groupParagraph =
        group.paragraphs.join(" ");

      const estimatedLines =
        (
          groupParagraph
            ? wrapText(
                groupParagraph,
                CONTENT_WIDTH -
                30,
                9
              ).length
            : 0
        ) +
        group.items.reduce(
          (sum, bullet) =>
            sum +
            Math.max(
              1,
              wrapText(
                bullet,
                CONTENT_WIDTH -
                46,
                8.8
              ).length
            ),
          0
        );

      const boxHeight =
        Math.max(
          74,
          45 +
          estimatedLines *
          12.6
        );

      if (
        y -
        boxHeight <
        72
      ) {
        pages.push(
          concatBytes(
            commands
          )
        );

        pageNumber += 1;
        commands = [];

        y =
          headerForContentPage(
            commands,
            theme,
            title,
            pageNumber
          );

        commands.push(
          drawText({
            text:
              `${item.label} · continuación`,
            x: MARGIN,
            y,
            size: 17,
            bold: true,
            color: TEXT
          })
        );

        y -= 28;
      }

      const bottom =
        y -
        boxHeight;

      commands.push(
        roundedRect({
          x: MARGIN,
          y:
            bottom,
          width:
            CONTENT_WIDTH,
          height:
            boxHeight,
          radius: 14,
          fill: PANEL,
          stroke: LINE,
          strokeWidth: .7
        }),
        drawText({
          text:
            group.title
              .toUpperCase(),
          x:
            MARGIN + 15,
          y:
            y - 22,
          size: 8,
          bold: true,
          color:
            theme.accentSoft
        })
      );

      let localY =
        y - 42;

      if (groupParagraph) {
        localY =
          drawParagraph({
            commands,
            text:
              groupParagraph,
            x:
              MARGIN + 15,
            y:
              localY,
            width:
              CONTENT_WIDTH -
              30,
            size: 9,
            lineHeight: 12.7,
            color: MUTED
          });

        localY -= 4;
      }

      drawBulletList({
        commands,
        items:
          group.items,
        x:
          MARGIN + 15,
        y:
          localY,
        width:
          CONTENT_WIDTH -
          30,
        size: 8.7,
        lineHeight: 12.2,
        color: TEXT
      });

      y =
        bottom - 13;
    }

    pages.push(
      concatBytes(
        commands
      )
    );

    return pages;
  }


  function compactContentPages({
    title,
    items,
    theme,
    startPageNumber
  }) {
    const pages = [];

    const gap = 10;

    const twoColumnWidth =
      (
        CONTENT_WIDTH -
        gap
      ) / 2;

    const fullWidth =
      CONTENT_WIDTH;

    let pageNumber =
      startPageNumber;

    let commands = [];

    let pageTop =
      headerForContentPage(
        commands,
        theme,
        title,
        pageNumber
      );

    let columnY = [
      pageTop,
      pageTop
    ];

    let pageHasContent =
      false;


    const startFreshPage = () => {
      commands = [];

      pageTop =
        headerForContentPage(
          commands,
          theme,
          title,
          pageNumber
        );

      columnY = [
        pageTop,
        pageTop
      ];

      pageHasContent =
        false;
    };


    const flushPage = () => {
      if (!pageHasContent) {
        return;
      }

      pages.push(
        concatBytes(
          commands
        )
      );

      pageNumber += 1;

      startFreshPage();
    };


    let index = 0;

    while (
      index <
      items.length
    ) {
      const item =
        items[index];

      const compactHeight =
        estimateCardHeight(
          item,
          twoColumnWidth
        );

      const wideHeight =
        estimateCardHeight(
          item,
          fullWidth
        );

      const needsDetailedPage =
        wideHeight > 390 ||
        item.groups.length > 5;

      if (needsDetailedPage) {
        flushPage();

        const detailPages =
          fullWidthDetailPages({
            title,
            item,
            theme,
            startPageNumber:
              pageNumber
          });

        pages.push(
          ...detailPages
        );

        pageNumber +=
          detailPages.length;

        startFreshPage();

        index += 1;
        continue;
      }

      /*
       * Si una página está vacía y una tarjeta compacta viene
       * inmediatamente antes de una tarjeta ancha, usamos el
       * ancho completo para la primera. Esto evita dejar media
       * página vacía sólo por respetar dos columnas.
       */
      if (
        !pageHasContent &&
        compactHeight <= 330 &&
        wideHeight <= 300 &&
        index + 1 <
        items.length
      ) {
        const next =
          items[
            index + 1
          ];

        const nextCompactHeight =
          estimateCardHeight(
            next,
            twoColumnWidth
          );

        const nextWideHeight =
          estimateCardHeight(
            next,
            fullWidth
          );

        const nextIsWide =
          nextCompactHeight > 330 &&
          nextWideHeight <= 390 &&
          next.groups.length <= 5;

        const bothFit =
          pageTop -
          wideHeight -
          gap -
          nextWideHeight >=
          58;

        if (
          nextIsWide &&
          bothFit
        ) {
          const firstBottom =
            drawCompactCard({
              commands,
              item,
              theme,
              x: MARGIN,
              topY:
                pageTop,
              width:
                fullWidth,
              height:
                wideHeight
            });

          columnY = [
            firstBottom - gap,
            firstBottom - gap
          ];

          pageHasContent =
            true;

          index += 1;
          continue;
        }
      }

      if (
        compactHeight <=
        330
      ) {
        let column =
          columnY[0] >=
          columnY[1]
            ? 0
            : 1;

        const other =
          column === 0
            ? 1
            : 0;

        if (
          columnY[column] -
          compactHeight <
          58
        ) {
          if (
            columnY[other] -
            compactHeight >=
            58
          ) {
            column = other;
          }
          else {
            flushPage();
            column = 0;
          }
        }

        const x =
          MARGIN +
          column *
          (
            twoColumnWidth +
            gap
          );

        const bottom =
          drawCompactCard({
            commands,
            item,
            theme,
            x,
            topY:
              columnY[column],
            width:
              twoColumnWidth,
            height:
              compactHeight
          });

        columnY[column] =
          bottom - gap;

        pageHasContent =
          true;

        index += 1;
        continue;
      }

      let topY =
        Math.min(
          columnY[0],
          columnY[1]
        );

      if (
        topY -
        wideHeight <
        58
      ) {
        flushPage();

        topY =
          pageTop;
      }

      const bottom =
        drawCompactCard({
          commands,
          item,
          theme,
          x: MARGIN,
          topY,
          width:
            fullWidth,
          height:
            wideHeight
        });

      columnY = [
        bottom - gap,
        bottom - gap
      ];

      pageHasContent =
        true;

      index += 1;
    }

    flushPage();

    return pages;
  }


  function buildMarkdownPdf({
    markdown,
    title = "Roadmap",
    subtitle = "",
    source = ""
  }) {
    const parsed =
      parseRoadmap(
        markdown
      );

    const theme =
      themeForTitle(
        title
      );

    const generatedAt =
      new Date()
        .toLocaleString(
          "es-MX"
        );

    const streams = [
      coverPage({
        title,
        subtitle,
        source,
        intro:
          parsed.intro,
        items:
          parsed.items,
        theme,
        generatedAt
      })
    ];

    streams.push(
      ...compactContentPages({
        title,
        items:
          parsed.items,
        theme,
        startPageNumber: 2
      })
    );

    return buildPdfDocument(
      streams
    );
  }


  function buildPdfDocument(
    streams
  ) {
    const pageCount =
      streams.length;

    const objects =
      new Map();

    const pageObjectNumbers =
      [];

    for (
      let index = 0;
      index < pageCount;
      index += 1
    ) {
      pageObjectNumbers.push(
        5 + index * 2
      );
    }

    objects.set(
      1,
      ascii(
        "<< /Type /Catalog /Pages 2 0 R >>"
      )
    );

    objects.set(
      2,
      ascii(
        `<< /Type /Pages /Count ${pageCount} /Kids [${pageObjectNumbers.map((number) => `${number} 0 R`).join(" ")}] >>`
      )
    );

    objects.set(
      3,
      ascii(
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
      )
    );

    objects.set(
      4,
      ascii(
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
      )
    );

    streams.forEach(
      (stream, index) => {
        const pageNumber =
          5 + index * 2;

        const contentNumber =
          pageNumber + 1;

        objects.set(
          pageNumber,
          ascii(
            [
              "<<",
              "/Type /Page",
              "/Parent 2 0 R",
              `/MediaBox [0 0 ${PAGE_WIDTH} ${PAGE_HEIGHT}]`,
              "/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >>",
              `/Contents ${contentNumber} 0 R`,
              ">>"
            ].join(" ")
          )
        );

        objects.set(
          contentNumber,
          concatBytes([
            ascii(
              `<< /Length ${stream.length} >>\nstream\n`
            ),
            stream,
            ascii(
              "\nendstream"
            )
          ])
        );
      }
    );

    const maxObject =
      4 +
      pageCount * 2;

    const chunks = [
      ascii(
        "%PDF-1.4\n%\n"
      )
    ];

    const offsets =
      new Array(
        maxObject + 1
      ).fill(0);

    let currentLength =
      chunks[0].length;

    for (
      let number = 1;
      number <= maxObject;
      number += 1
    ) {
      const object =
        objects.get(number);

      offsets[number] =
        currentLength;

      const header =
        ascii(
          `${number} 0 obj\n`
        );

      const footer =
        ascii(
          "\nendobj\n"
        );

      chunks.push(
        header,
        object,
        footer
      );

      currentLength +=
        header.length +
        object.length +
        footer.length;
    }

    const xrefOffset =
      currentLength;

    const xrefLines = [
      "xref",
      `0 ${maxObject + 1}`,
      "0000000000 65535 f "
    ];

    for (
      let number = 1;
      number <= maxObject;
      number += 1
    ) {
      xrefLines.push(
        `${String(offsets[number]).padStart(10, "0")} 00000 n `
      );
    }

    chunks.push(
      ascii(
        [
          ...xrefLines,
          "trailer",
          `<< /Size ${maxObject + 1} /Root 1 0 R >>`,
          "startxref",
          String(xrefOffset),
          "%%EOF",
          ""
        ].join("\n")
      )
    );

    return concatBytes(
      chunks
    );
  }


  function downloadBytes(
    bytes,
    filename
  ) {
    if (
      typeof document ===
      "undefined"
    ) {
      throw new Error(
        "La descarga directa requiere un navegador."
      );
    }

    const blob =
      new Blob(
        [bytes],
        {
          type:
            "application/pdf"
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const anchor =
      document.createElement(
        "a"
      );

    anchor.href = url;
    anchor.download =
      datedFilename(
        filename
      );

    document.body.append(
      anchor
    );

    anchor.click();
    anchor.remove();

    window.setTimeout(
      () => {
        URL.revokeObjectURL(
          url
        );
      },
      1200
    );
  }


  function downloadMarkdown(options) {
    const bytes =
      buildMarkdownPdf(
        options
      );

    downloadBytes(
      bytes,
      options.filename ||
      `${options.title || "Roadmap"}-Roadmap.pdf`
    );

    return bytes;
  }


  async function fetchText(url) {
    const response =
      await fetch(
        url,
        {
          cache:
            "no-store"
        }
      );

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status} al cargar ${url}`
      );
    }

    return response.text();
  }


  async function downloadFromSource(config) {
    const source =
      config.source ||
      config.url;

    if (
      config.type ===
      "script-array"
    ) {
      const script =
        await fetchText(
          config.url
        );

      const items =
        parseRoadmapScript(
          script,
          config.variableName ||
          "roadmapItems"
        );

      const markdown =
        roadmapItemsToMarkdown(
          items,
          config.title ||
          "Roadmap"
        );

      return downloadMarkdown({
        markdown,
        title:
          config.title ||
          "Roadmap",
        subtitle:
          config.subtitle ||
          "",
        source,
        filename:
          config.filename ||
          "Roadmap.pdf"
      });
    }

    const markdown =
      await fetchText(
        config.url
      );

    return downloadMarkdown({
      markdown,
      title:
        config.title ||
        "Roadmap",
      subtitle:
        config.subtitle ||
        "",
      source,
      filename:
        config.filename ||
        "Roadmap.pdf"
    });
  }


  global.RoadmapPdf = {
    buildMarkdownPdf,
    downloadMarkdown,
    downloadFromSource,
    parseRoadmap,
    parseRoadmapScript,
    roadmapItemsToMarkdown
  };

})(
  typeof window !== "undefined"
    ? window
    : globalThis
);
