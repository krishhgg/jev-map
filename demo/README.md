# Interactive graph demo

Live at **[jev-map.vercel.app](https://jev-map.vercel.app)**.

The demo replays two studies on Graphify's own code graph for each repository. They are the [popular-repository study](../benchmarks/07-popular-repos/FINDINGS.md), on Flask, FastAPI, langchain-core, yt-dlp and Graphify, and the [held-out toolbelt study](../benchmarks/05-heldout-toolbelt/FINDINGS.md), on h11, Pluggy and Boltons. Every link, score and result comes from the archived `round-01-live` rounds. Nothing is re-run, and the animation timing isn't Jev's real latency.

## Build it

```sh
PYTHONPATH=src:. python demo/build.py                     # writes demo/jev-map-graph.html
python -m http.server -d demo 8765                        # or open the file directly
```

To publish it, pass the public address with `--site-url` and write the page into the folder you deploy:

```sh
PYTHONPATH=src:. python demo/build.py --out /path/to/site/index.html --site-url https://jev-map.vercel.app
```

`--site-url` adds the link-preview tags and copies `demo/preview.png` next to the page. The page is one self-contained file, apart from loading d3 from jsDelivr and the Overpass font from Google Fonts.

## What's on screen

The page looks like a sheet of engineering paper. A link Jev added is a dashed line. It turns solid blue when the test ran the function, and gets a red cross when it didn't. Blue and red are the only colors, and they were checked to stay distinct for colorblind viewers in both the light and dark themes. The key only lists what's on screen in the current step. On a phone, the story sits at the top, the controls at the bottom, and the key is hidden.

| Key | What it does |
| --- | --- |
| Space, ← and →, 1 to 8, or Next | Move through the steps |
| The repository menu, or `[` and `]` | Switch repository |
| Click a circle | Show its candidate tests, Jev's scores, the test-run results and the first suggestion |
| Scroll or drag | Zoom and pan. Function names appear when you zoom in. |
| F, C or R | Reframe the graph, hide the key and hints, or replay the step |
| D | Switch between light and dark, or open the page with `?theme=dark` |

## The eight steps

1. What jev-map does, and why test links are hard to find.
2. Graphify's map of the repository.
3. A close-up of one function, its three candidate tests, and Jev's score for each. The example is the first sampled function where Jev both added and rejected a candidate, shown with its recorded result.
4. All of Jev's links across the repository.
5. The test runs that confirm or refute them, and how many real links Jev left out.
6. The same number of links picked by keyword search alone.
7. Whether the first suggested test got better. It went from 97 to 105 of 134 in study 05, and from 97 to 100 of 191 in study 07.
8. The agent study where the hints changed nothing, at 23 of 24 both ways.

Keep the last step in any recording that shows the others.
