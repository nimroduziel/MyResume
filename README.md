# Platform Architecture

Interactive architecture documentation for a self-hosted, on-premises LLM platform —
OpenShift for the application and control plane, dedicated GPU VMs on a separate, segmented
network for all inference and vector search.

**→ [View the diagrams](https://nimroduziel.github.io/AI-Architecture/)**

The site is a "bird view" you can descend into: the overview shows the whole platform, and
every component on it links to a page with that area's detail.

| Page | Covers |
| ---- | ------ |
| [Overview](index.html) | The platform at a glance, legend, redundancy posture, namespace inventory, permitted flows |
| [Walkthroughs](flows.html) | Step-by-step sequences for the three ways work enters the platform |
| [Inference](inference.html) | LiteLLM gateway + 9 GPU VMs running vLLM |
| [Data](data.html) | Two pgpool Postgres clusters, Qdrant, S3 object store, Redis caches |
| [Observability](observability.html) | Prometheus / OpenTelemetry / Alertmanager, and the external Grafana |
| [MCP](mcp.html) | Confluence, Jira and GitLab tool servers |

Diagrams are [Mermaid](https://mermaid.js.org/), rendered client-side. See `CLAUDE.md` for
the full written architecture description and editing conventions.

> Generalized reference architecture. Component counts, model choices and topology are
> illustrative of the design pattern rather than a description of any live deployment.
