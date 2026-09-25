# Interactive graph demo

A replay of the [held-out toolbelt study](../benchmarks/05-heldout-toolbelt/FINDINGS.md)
drawn on Graphify's own code graph for h11, Pluggy, and Boltons. Every link,
score, and verdict comes from the archived `round-01-live`; nothing is re-run and
animation timing is not provider latency.

```sh
PYTHONPATH=src:. python demo/build.py        # writes demo/jev-map-graph.html
python -m http.server -d demo 8765           # or open the file directly
```

The page is self-contained apart from loading d3 from jsDelivr and Overpass from Google Fonts.

It is drawn like an engineering sheet: Jev's proposals are pencilled in, a test that
ran the function inks the link blue, and one that didn't gets a red strike. Blue and
red are the only hues, checked for colour-blind separation in both themes.

| Key | Action |
| --- | --- |
| Space, ←/→, 1–6, or Next sheet | Step through the story |
| `[` / `]` | Switch repository |
| Click a node | Candidate tests, Jev scores, execution verdicts, first suggestion |
| Scroll / drag | Zoom and pan; function labels appear when zoomed in |
| F / C / R | Fit the graph / hide the key and hints / replay the step |
| D | Switch between paper and dark (or open with `?theme=dark`) |

Steps: Graphify's map → Jev adds test links → running the tests confirms or
refutes them → the same budget from a keyword ranker → the first suggested test
improving from 97 to 105 of 134 → the agent study where the hint changed nothing
(23/24 both ways). Keep the last step in any recording that shows the others.
