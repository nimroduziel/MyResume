// Shared Mermaid setup for every page on this site.
//
// Notes for future edits:
//  * securityLevel 'loose' is REQUIRED for `click ... href ...` drill-down links.
//  * We pin theme 'base' with a fixed light palette so diagrams look identical in
//    light and dark mode, sitting on the fixed light .diagram surface. Don't switch
//    to theme:'dark' — the classDef fills in the diagrams assume a light surface.
//  * Avoid `direction` inside a subgraph that has edges crossing its boundary:
//    Mermaid ignores it, which produces sideways, tangled layouts.

mermaid.initialize({
  startOnLoad: true,
  securityLevel: 'loose',
  theme: 'base',
  themeVariables: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    fontSize: '14px',
    background: 'transparent',

    // Dark canvas. Lines are deliberately dimmer than the node borders so the boxes
    // lead and the connections recede — the single biggest readability win.
    primaryColor: '#1a2234',
    primaryTextColor: '#e6edf7',
    primaryBorderColor: '#64748b',
    lineColor: '#5d6b83',
    textColor: '#cbd5e1',
    clusterBkg: '#161f36',
    clusterBorder: '#334155',
    // Must match the .diagram canvas, or every edge label sits in a pale box.
    edgeLabelBackground: '#101728',
    tertiaryColor: '#1a2234',
    tertiaryTextColor: '#e6edf7',

    // sequence-diagram specifics
    actorBkg: '#1c2740',
    actorBorder: '#60a5fa',
    actorTextColor: '#e6edf7',
    actorLineColor: '#475569',
    signalColor: '#93a4bd',
    signalTextColor: '#cbd5e1',
    labelBoxBkgColor: '#1c2740',
    labelBoxBorderColor: '#475569',
    labelTextColor: '#e6edf7',
    loopTextColor: '#cbd5e1',
    noteBkgColor: '#3a2f10',
    noteTextColor: '#fde68a',
    noteBorderColor: '#a16207',
    activationBkgColor: '#243049',
    activationBorderColor: '#64748b',
    sequenceNumberColor: '#0b1120'
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
    nodeSpacing: 50,
    rankSpacing: 72,
    padding: 16
  },
  sequence: {
    useMaxWidth: true,
    diagramMarginX: 12,
    diagramMarginY: 12,
    actorMargin: 46,
    boxTextMargin: 6,
    noteMargin: 10,
    messageMargin: 38,
    mirrorActors: false,   // repeating the actor row at the bottom just adds noise
    wrap: false
  }
});

// --- hover affordance for drill-down nodes -----------------------------------
// A `click X href "..."` node is rendered as <a xlink:href><g>…shape…</g></a>, and
// positionNode() puts the translate() on the <a>. So the hover lift must be applied to
// the inner <g>, never the anchor (that would override its translate() and misplace the
// node). Rather than depend on Mermaid's class strings, tag the inner <g> ourselves and
// let the stylesheet target `.is-drillable`.
(function () {
  function tag() {
    document.querySelectorAll('.diagram svg a').forEach(function (a) {
      var g = a.firstElementChild;
      if (g && g.tagName.toLowerCase() === 'g') g.classList.add('is-drillable');
    });
  }

  function start() {
    tag();
    // Rendering is async, so re-tag as diagrams appear.
    if (window.MutationObserver) {
      var obs = new MutationObserver(tag);
      document.querySelectorAll('.diagram').forEach(function (d) {
        obs.observe(d, { childList: true, subtree: true });
      });
    }
    [150, 500, 1500].forEach(function (t) { setTimeout(tag, t); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
