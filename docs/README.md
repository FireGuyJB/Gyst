# Gyst docs

Everything about *what* we're building, *why*, and *how*, kept next to the code
so it stays in sync. If code and docs disagree, that's a bug: fix one of them
in the same PR.

| Folder | What goes here | When you touch it |
|---|---|---|
| [`product/`](product/) | Vision and requirements: what Gyst does and for whom | When product behavior changes |
| [`architecture/`](architecture/) | How the layers fit together (frontend → API → database) | When you add a layer, service, or change how they connect |
| [`decisions/`](decisions/) | ADRs: one short file per significant technical decision and *why* | When you choose a library, pattern, or trade-off worth remembering |
| [`features/`](features/) | One folder per feature, with its spec | Before building any feature (see the workflow) |
| [`guides/`](guides/) | How-tos: setup, daily workflow | When a command or process changes |
| [`specs/`](specs/) | Design docs for larger efforts (e.g. repo foundations) | During brainstorming/design |
| [`plans/`](plans/) | Step-by-step implementation plans that come from a spec | Before implementation starts |

**New here?** Read in this order:
1. [product/vision.md](product/vision.md)
2. [architecture/overview.md](architecture/overview.md)
3. [guides/getting-started.md](guides/getting-started.md)
4. [features/README.md](features/README.md) (how we build things)
