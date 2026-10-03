# Interactive graph demo

A replay of the [popular-repository study](../benchmarks/07-popular-repos/FINDINGS.md)
(Flask, FastAPI, langchain-core, yt-dlp, Graphify) and the
[held-out toolbelt study](../benchmarks/05-heldout-toolbelt/FINDINGS.md) (h11, Pluggy,
Boltons), drawn on Graphify's own code graph for each repository. Every link, score,
and verdict comes from the archived `round-01-live` rounds. Nothing is re-run, and
animation timing is not provider latency.

```sh
PYTHONPATH=src:. python demo/build.py        # writes demo/jev-map-graph.html
python -m http.server -d demo 8765           # or open the file directly
```

The page is self-contained apart from loading d3 from jsDelivr and Overpass from Google Fonts.

It is drawn like an engineering sheet. Jev's added links are dashed pencil, a test that
ran the function inks the link blue, and one that didn't gets a red strike. Blue and
red are the only hues, checked for colour-blind separation in both themes. The key
shows only the entries for what's on screen in the current step.

| Key | Action |
| --- | --- |
| Space, ←/→, 1–8, or Next | Step through the walkthrough |
| Repository menu, or `[` / `]` | Switch repository |
| Click a node | Candidate tests, Jev scores, test-run results, first suggestion |
| Scroll / drag | Zoom and pan; function labels appear when zoomed in |
| F / C / R | Reframe the graph / hide the key and hints / replay the step |
| D | Switch between paper and dark (or open with `?theme=dark`) |

Steps, written for someone seeing jev-map for the first time:

1. What jev-map does and why test links are hard to find.
2. Graphify's map of the repository.
3. A close-up of one function, its three candidate tests, and Jev's score for each.
   The example is the first sampled function where Jev both added and rejected a
   candidate, shown with its recorded outcome.
4. All of Jev's added links across the repository.
5. Running the tests confirms or refutes them, including how many real links Jev left out.
6. The same number of links picked by keyword score alone.
7. Whether the first suggested test changed (97 to 105 of 134 in study 05, 97 to 100
   of 191 in study 07).
8. The agent study where the hint changed nothing (23/24 both ways).

Keep the last step in any recording that shows the others.
