# Benchmarks

Each study has its own folder. The four main studies, 03, 05, 06 and 07, each have a `PROTOCOL.md`, written and frozen before any results came in, and a `FINDINGS.md` with the results. The raw data lives under `rounds/`. Archived rounds are never rewritten, and a new run goes in a new round.

| Study | What it asks | Start here |
| --- | --- | --- |
| 01, mapping smoke test | Does the wiring work, end to end, on a tiny example repo? | [README](01-mapping-smoke/README.md) |
| 02, indexing pilot | Can the mapper parse a real public repository? | [README](02-repository-index/README.md) |
| 03, multi-repo relationships | When Jev says a test runs a function, is it right? | [Findings](03-multi-repo-relationships/FINDINGS.md) |
| 04, Graphify and keyword baselines | How do Jev's links compare with Graphify's call graph and a keyword ranker? An exploratory look back at study 03's sample. | [README](04-product-baselines/README.md) |
| 05, held-out toolbelt | On new functions, does Jev beat keyword search, and does the first suggested test improve? | [Findings](05-heldout-toolbelt/FINDINGS.md) |
| 06, agent navigation | Does a coding agent find the right test more often with Jev's hints? | [Findings](06-agent-navigation/FINDINGS.md) |
| 07, popular repos | Does study 05 hold up on Flask, FastAPI, langchain-core, yt-dlp and Graphify? | [Findings](07-popular-repos/FINDINGS.md) |

Wherever a study scores Jev or an agent, it checks the answers against real test runs. The tests run under a tracer, a tool that records every function each test calls. Jev never sees those results.
