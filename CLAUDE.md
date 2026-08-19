# CLAUDE.md

Context for Claude Code when working in this repository.

> **Sanitization rule — read before editing any page.** This is a **public** repository, so the
> site is written as a *generalized reference architecture*, not a description of a live
> deployment. Do **not** reintroduce: port numbers, VLAN/subnet/host/address specifics, security
> posture ("no proxy in the path"), or per-component failure blast radius ("single pod — all
> metrics stop"). Redundancy gaps may be described as roadmap items in general terms, never as
> an enumerated list of what breaks when. Every page carries a `.disclaimer` note stating the
> counts are illustrative.

## What this repository is

A **GitHub Pages site** (`nimroduziel/AI-Architecture`, branch `main`, served from root) whose
purpose is to **document and publish the architecture of a self-hosted enterprise LLM
platform** as an interactive set of Mermaid diagrams.

The site is intentionally structured as a **"bird view" overview that viewers can drill into**:
`index.html` shows the whole platform at a glance, and boxes marked `↗` are clickable
links into a dedicated page with the detail for that area. Viewers can also enter at any
detail page directly.

This repo holds **documentation only** — no application code, no Helm charts, no
infrastructure-as-code. The systems described below live elsewhere.

### Site layout

| File | Purpose |
| ---- | ------- |
| `index.html` | Bird-view overview, stat tiles, legend, resilience table, namespace inventory, cross-network flow table |
| `flows.html` | Three sequence-diagram walkthroughs: RAG chat, Claude Code, n8n automation |
| `inference.html` | LiteLLM gateway + the external GPU/vLLM model fleet |
| `data.html` | Postgres/pgpool clusters, Qdrant vector DB, S3 object storage, Redis caches |
| `observability.html` | Prometheus / OpenTelemetry / Alertmanager flows |
| `mcp.html` | MCP servers and their two client surfaces |
| `assets/style.css` | Shared styling for all pages |
| `assets/diagram.js` | Shared Mermaid config — the single place render settings live |
| `tools/apply-palette.py` | Single source of truth for diagram `classDef` colours; rewrites them across all pages |
| `.nojekyll` | Disables Jekyll so the HTML is served verbatim |
| `_config.yml` | Leftover Jekyll scaffold; inert while `.nojekyll` is present |

### Conventions for editing this site

- Diagrams are **Mermaid**, rendered client-side from the jsDelivr CDN (`mermaid@10`).
- `flows.html` uses **`sequenceDiagram`**, not `flowchart` — the flowchart layout rules below
  do not apply to it, and the layout checker skips it.
- All render config lives in **`assets/diagram.js`** — one shared file, no per-page
  `mermaid.initialize()`. Every page loads the CDN script then `assets/diagram.js`.
- `securityLevel: 'loose'` is required — **click/href drill-down links do not work
  without it.** Don't remove it.
- Drill-down is implemented with Mermaid `click <nodeId> href "page.html" "tooltip"` lines.
- A local project skill is installed at `.claude/skills/mermaid/` (from
  [WH-2099/mermaid-skill](https://github.com/WH-2099/mermaid-skill), MIT). It carries syntax
  references for 38 diagram types — see `references/architecture.md`, `references/c4.md`,
  and `references/flowchart.md` when authoring or fixing diagrams.

### Layout rules — these were learned the hard way

1. **Never put `direction` inside a subgraph that has edges crossing its boundary.**
   Mermaid *silently ignores* it, and the result is a sideways, tangled layout. This was the
   single biggest cause of the first version looking bad.
2. **Prefer tree shapes.** A graph with `edges ≈ nodes − 1` lays out with zero crossings.
   Where a real fan-out existed (LiteLLM → the whole model VM fleet), an intermediate
   grouping node per model family turns the fan into a tree without losing information.
3. **Push detail into prose and tables, not more edges.** Secondary relationships
   (Prometheus scrape targets, Qdrant master↔worker replication, namespace-internal traffic)
   are stated in text and captioned under the diagram rather than drawn, which keeps the
   primary path legible.
4. **Every diagram is `flowchart TB`** — top-to-bottom throughout the site, by request.
   The risk with TB is horizontal blowout, so:
5. **Use invisible links (`~~~`) to stack siblings into columns.** `A ~~~ B` forces B onto the
   next rank without drawing an edge. This is what keeps TB diagrams narrow: the Inference
   fleet went from 8 VMs in one row (~1480px) to three columns (~555px), and the OpenShift
   page turned 15 workloads-in-a-row into 6 namespace columns. Keep the widest rank at
   roughly 6 nodes / ~1100px so the diagram fits without horizontal scrolling.
6. **Dotted edges (`-.->`) for observation, solid for request traffic.** Monitoring's scrape
   edges touch everything, so they need to read as a different kind of relationship.
7. **Tiers only stack if their ranks do not overlap.** A subgraph is drawn as its own
   horizontal band only when *every* node in it ranks strictly below every node of the tier
   above. If ranks overlap, Mermaid renders the two boxes **side by side**, which is what made
   the bird view look broken. The usual culprit is a node with **no incoming edge** (it ranks 0
   and drags its tier up to the users' level). Fix with an invisible link from the tier above —
   these `~~~` links are load-bearing, not decoration; deleting one breaks the tiering.
8. **Only make a node clickable if a page is actually about it.** No dead-end or
   approximate links. The affordance is a **hover lift + glow**, styled in `assets/style.css`,
   not a glyph in the label. Keep the legend table on the bird view in sync.
   **Gotcha:** Mermaid renders `click X href "..."` as
   `<a xlink:href><g class="node ... clickable">`, and `positionNode()` puts the
   `translate()` on the **`<a>`**. So a CSS `transform` is only safe on the inner `<g>` —
   putting one on the anchor overrides its `translate()` and moves the node to the wrong
   place. The hover rules deliberately target `.diagram a > g.node`.
9. **Diagrams render on a fixed DARK canvas** (`.diagram` background `#101728`, in both
   colour schemes). Every `classDef` is a muted dark fill + luminous border + light text, so
   making the surface light would render every node unreadable. Two things must stay in sync
   with the canvas colour: `edgeLabelBackground` in `assets/diagram.js` (otherwise edge labels
   sit in pale boxes) and the `@media print` rule (which forces the canvas to print, or the
   light text prints onto white). Do not hand-edit `classDef` lines — edit
   `tools/apply-palette.py` and re-run it, so all 8 diagrams stay consistent.
   Design notes behind the palette: node borders are brighter than `lineColor` on purpose so
   boxes lead and connectors recede; only LiteLLM gets a full-strength accent (amber); and
   per-VM leaf nodes are deliberately dim so the family nodes read first.
10. Keep `<b>`/`<small>`/`<br/>` markup inside **quoted** labels — unquoted labels containing
   `<`, `>`, `&` or `|` break the parser.

Validation: extract each `<pre class="mermaid">` block, then check (a) structure — balanced
subgraphs, click targets resolving to declared nodes, link targets existing on disk, no nested
`direction`; and (b) layout — compute longest-path ranks to get each subgraph's rank span, and
fail if sibling tiers overlap or any rank exceeds ~4 nodes. The layout check is the one that
catches "renders side by side" and "too wide" before they reach the browser. A real Mermaid
*parse* needs a browser or Node ≥18 — the system Node here is v10.

---

## The architecture being documented

An on-premises, air-gapped-style LLM platform: OpenShift runs the application and control
plane, while all model inference and vector search runs on dedicated GPU VMs on a separate,
segmented network.

### Network topology

Two segmented networks, with only specific service-to-service flows permitted between them:

- **the cluster network** — the OpenShift cluster.
- **the segregated network** — the GPU VM fleet, the Qdrant VMs, and both Postgres/pgpool clusters.

Flows permitted across the boundary:
- LiteLLM (the cluster network) → vLLM containers (the segregated network) on its API port
- OpenWebUI (the cluster network) → Qdrant via HAProxy (the segregated network) 
- OpenWebUI / LiteLLM / n8n → pgpool, for relational state
- Prometheus (the cluster network) → all vLLM instances (the segregated network) for scraping

### OpenShift cluster — namespaces

Everything below is deployed via **Helm charts**.

| Namespace | Workloads |
| --------- | --------- |
| **OpenWebUI** | OpenWebUI — 3 pods · Redis cluster — 6 pods |
| **LiteLLM** | LiteLLM — 5 pods · Redis cluster — 6 pods |
| **Monitoring** | Prometheus — 1 pod · Alertmanager — 1 pod · OpenTelemetry Collector — 1 pod |
| **MCPs** | Confluence MCP — 1 pod · Jira MCP — 1 pod · GitLab MCP — 1 pod |
| **N8n** | 2 master pods · 3 worker pods (worker + runner) |
| **Support** | Static docs, 1 pod each: LiteLLM docs, OpenWebUI docs, n8n docs |

### GPU / model fleet (the segregated network)

Every GPU VM runs **vLLM inside a Docker container, listening on its API port**. Chat model
containers use **tensor parallelism — one model instance sharded across 2 GPUs**, not two
independent replicas. Every Gemma container additionally runs **LMCache** for KV-cache reuse.

| VMs | GPUs per VM | Containers per VM | Serves |
| --- | ----------- | ----------------- | ------ |
| 4 | 2 × L40 | 1 | Qwen3.6-35B-A3B, FP8 quantized (tensor parallel over 2 GPUs) |
| 2 | 2 × L40 | 1 | gemma-4-26B-A4B, FP8 quantized + LMCache (tensor parallel over 2 GPUs) |
| 1 | 2 × A100 | 1 | gemma-4-26B-A4B, FP8 quantized + LMCache (tensor parallel over 2 GPUs) |
| 1 | 4 × L4 | 2 | gemma-4-26B-A4B, FP8 quantized + LMCache — two containers, each tensor parallel over its own 2 GPUs |
| 1 | 2 × L4 | 2 | llama-embed-nemotron-8b (1 GPU) + llama-nemotron-rerank-1b-v2 (1 GPU) — 1 model per GPU here |

**9 model VMs, 20 GPUs, 11 vLLM containers total.** Two VMs break the one-container-per-VM
pattern: the 4 × L4 VM runs two Gemma containers side by side (tensor parallel over 2 GPUs
each), and the retrieval VM runs two distinct models, one pinned per GPU with no tensor
parallelism.

The same FP8 Gemma checkpoint is served on every Gemma host. L40 and L4 are Ada-generation and
execute FP8 natively; the A100 pair is Ampere with no FP8 tensor cores, so the runtime
upconverts there — same weights, different arithmetic.

Model names are the real upstream releases: `Qwen3.6-35B-A3B`, `google/gemma-4-26B-A4B`,
`nvidia/llama-embed-nemotron-8b`, `nvidia/llama-nemotron-rerank-1b-v2`. There is no Gemma 4
27B — the published sizes are E2B, E4B, 12B, 26B-A4B and 31B.

### Postgres (the segregated network) — two separate pgpool clusters

Relational state lives on the segregated network, not in the cluster. Clients always connect through
**pgpool**, never directly to a Postgres node.

| Cluster | Layout | Databases |
| ------- | ------ | --------- |
| **Platform** | 3 VMs, each running **both pgpool and Postgres** — 1 primary + 2 streaming replicas | One DB for **OpenWebUI**, a separate DB for **LiteLLM** |
| **n8n** | Its own pgpool-fronted Postgres cluster, also on the segregated network | n8n's DB |

The two clusters are entirely independent — n8n does not share the platform's Postgres.

### Vector database (the segregated network)

- **2 VMs, each 2 × T4** running a **Qdrant cluster** — one master, one worker.
- The T4s are used for **Qdrant's GPU-accelerated indexing**.
- **HAProxy** fronts the cluster and load-balances across the instances.
- OpenWebUI connects through HAProxy and uses Qdrant as its vector DB (RAG).

### Object storage

An **on-prem S3-compatible object store** (MinIO-style). OpenWebUI connects to it for
**user document uploads**.

### How the pieces connect

- **All models → LiteLLM.** Every vLLM endpoint is registered in the **LiteLLM config**;
  LiteLLM is the single gateway in front of the whole fleet.
- **OpenWebUI → LiteLLM** via an **API key**.
- **OpenWebUI → Qdrant** (through HAProxy) for vector search.
- **OpenWebUI → S3** for document uploads.
- **Claude Code → LiteLLM.** Claude Code is fully supported on the network. Users
  **self-serve their own API keys in LiteLLM** and point Claude Code at it. These requests
  are served by the **local self-hosted models** — not the real Anthropic API.
- **MCP servers are called by both OpenWebUI and Claude Code.** Both surfaces are
  configured as MCP clients against the same three servers.
- Redis clusters back OpenWebUI and LiteLLM independently (6 pods each) for
  caching/coordination across their replicas.
- **OpenWebUI and LiteLLM → the platform Postgres cluster** via pgpool, each with
  its own database. **n8n → its own separate pgpool cluster**, also on the segregated network.

### Observability

- **OpenTelemetry Collector** exists specifically to **ingest OpenWebUI's metrics and
  translate them into a Prometheus-friendly format**.
- **Prometheus scrapes everything**: LiteLLM, OpenWebUI (via OTel), and all vLLM instances
  across the network boundary.
- **Alertmanager** consumes Prometheus and **alerts when something goes down**.
- **Grafana** is a **central, shared instance that this platform does not deploy or manage.**
  What belongs to the platform is the **set of dashboards built inside it** for OpenWebUI,
  LiteLLM and the vLLM fleet. It is wired as a **Prometheus datasource** — Grafana queries
  Prometheus on dashboard load; nothing is pushed to it. Drawn with a **dashed border**
  everywhere, which is this site's convention for "exists already, not ours".

---

## Unconfirmed details

Some specifics were never pinned down and are intentionally described loosely on the site
(exact node counts for the secondary database cluster, where the shared dashboards instance
runs, where the load balancer is hosted). Keep them loose — do not add precision here that the
public site should not carry.
