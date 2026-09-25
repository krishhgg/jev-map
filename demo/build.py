"""Build the interactive graph demo from archived benchmark rounds.

Reads immutable rounds only; nothing is recomputed or re-scored. Benchmark 07
(popular repositories) is included when its live round exists.
Usage: python demo/build.py [--out demo/jev-map-graph.html] [--benchmarks DIR]
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from benchmarks.graphify_compare import graph_node
from benchmarks.toolbelt_study import equal_lexical

HERE = Path(__file__).resolve().parent
STUDIES = (
    {"key": "popular", "number": "07", "round": "07-popular-repos/rounds/round-01-live",
     "repositories": ("flask", "fastapi", "langchain", "yt-dlp", "graphify"),
     "labels": {"langchain": "langchain-core", "yt-dlp": "yt-dlp"}},
    {"key": "original", "number": "05", "round": "05-heldout-toolbelt/rounds/round-01-live",
     "repositories": ("h11", "pluggy", "boltons"), "labels": {}},
)
TEST_DIRS = {"tests", "testing", "test"}
MAX_NODES = 2500


def read(path: Path):
    return json.loads(path.read_text())


def is_test_file(path: str) -> bool:
    parts = path.split("/")
    return bool(TEST_DIRS & set(parts[:-1])) or parts[-1].startswith("test_")


def node_kind(node: dict) -> str:
    if is_test_file(node.get("source_file", "")):
        return "test"
    return "code" if node.get("_callable") else "module"


def first_hit(suggestions: list[dict]) -> bool:
    return bool(suggestions and suggestions[0]["observed"])


def focus(graph: dict, nodes: list[dict], anchors: set[str]) -> list[dict]:
    """For large graphs, keep the anchors' files and graph neighbourhood."""
    if len(nodes) <= MAX_NODES:
        return nodes
    by_id = {node["id"]: node for node in nodes}
    files = {by_id[node_id].get("source_file") for node_id in anchors if node_id in by_id}
    keep = {node["id"] for node in nodes if node.get("source_file") in files and not node.get("_callable")}
    keep |= anchors
    neighbours: dict[str, set[str]] = {}
    for edge in graph["edges"]:
        neighbours.setdefault(edge["source"], set()).add(edge["target"])
        neighbours.setdefault(edge["target"], set()).add(edge["source"])
    queue = deque(sorted(anchors))
    while queue and len(keep) < MAX_NODES:
        for peer in sorted(neighbours.get(queue.popleft(), ())):
            if peer in by_id and peer not in keep and len(keep) < MAX_NODES:
                keep.add(peer)
                queue.append(peer)
    return [node for node in nodes if node["id"] in keep]


def repository(study: dict, round_dir: Path, name: str, pairs: list[dict], rankings: list[dict],
               keyword: set[tuple[str, str, str]], summary: dict) -> dict:
    graph = read(round_dir / f"graphify/{name}/graphify-out/graph.json")
    pairs = [pair for pair in pairs if pair["repository"] == name]
    rankings = [row for row in rankings if row["repository"] == name]
    symbols = {pair["function"] for pair in pairs} | {pair["test"] for pair in pairs}
    symbols |= {row["function"] for row in rankings}
    symbols |= {row["methods"]["graphify_jev_lexical"][0]["test"] for row in rankings
                if row["methods"]["graphify_jev_lexical"]}
    anchors = {node_id for symbol in symbols if (node_id := graph_node(graph, symbol))}
    all_nodes = [node for node in graph["nodes"] if node.get("file_type") != "rationale"]
    nodes = focus(graph, all_nodes, anchors)
    index = {node["id"]: position for position, node in enumerate(nodes)}
    out_nodes = [{"label": node["label"], "file": node.get("source_file", ""),
                  "kind": node_kind(node)} for node in nodes]
    edges = [[index[edge["source"]], index[edge["target"]], edge["relation"]]
             for edge in graph["edges"]
             if edge["source"] in index and edge["target"] in index]

    def locate(symbol: str) -> int:
        node_id = graph_node(graph, symbol)
        if node_id is not None and node_id in index:
            return index[node_id]
        # Unmapped symbols get a visible stand-in beside their file's module node.
        path, _, qualified = symbol.partition("::")
        out_nodes.append({"label": qualified, "file": path, "kind": "test" if is_test_file(path) else "code",
                          "unmapped": node_id is None})
        module = next((position for position, node in enumerate(nodes)
                       if node.get("source_file") == path and not node.get("_callable")), None)
        if module is not None:
            edges.append([len(out_nodes) - 1, module, "contains"])
        return len(out_nodes) - 1

    located: dict[str, int] = {}

    def at(symbol: str) -> int:
        if symbol not in located:
            located[symbol] = locate(symbol)
        return located[symbol]

    links = []
    for pair in pairs:
        if not pair["test_eligible"]:
            continue
        links.append({"f": at(pair["function"]), "t": at(pair["test"]),
                      "score": pair["jev_score"], "jev": pair["jev_accepted"],
                      "keyword": (name, pair["function"], pair["test"]) in keyword,
                      "observed": pair["observed"], "graphify": pair["graphify_link"]})

    targets = []
    for row in rankings:
        before, after = row["methods"]["graphify_lexical"], row["methods"]["graphify_jev_lexical"]
        targets.append({
            "node": at(row["function"]), "symbol": row["function"],
            "candidates": [{**candidate, "node": at(candidate["test"])}
                           for candidate in row["jev_candidates"] if candidate["score"] is not None],
            "observed": row["observed_tests"],
            "before": before[0]["test"] if before else None,
            "after": after[0]["test"] if after else None,
            "afterNode": at(after[0]["test"]) if after else None,
            "beforeHit": first_hit(before), "afterHit": first_hit(after),
            "positive": bool(row["observed_tests"]),
        })

    return {"name": study["labels"].get(name, name), "study": study["key"], "nodes": out_nodes,
            "edges": edges, "links": links, "targets": targets,
            "graphify": summary["graphify"][name], "shownNodes": len(nodes), "totalNodes": len(all_nodes)}


def study_data(study: dict, benchmarks: Path) -> tuple[dict, list[dict]] | None:
    round_dir = benchmarks / study["round"]
    if not (round_dir / "summary.json").is_file():
        return None
    pairs = read(round_dir / "candidate-pairs.json")
    rankings = read(round_dir / "rankings.json")
    summary = read(round_dir / "summary.json")
    accepted = sum(pair["jev_accepted"] and bool(pair["test_eligible"]) for pair in pairs)
    keyword = equal_lexical(pairs, accepted)
    methods = summary["methods"]
    pooled = {"number": study["number"], "repoCount": len(study["repositories"]),
              "targets": summary["targets"], "edge": summary["edge_filter"],
              "hitBefore": methods["graphify_lexical"]["hit_at_1_count"],
              "hitAfter": methods["graphify_jev_lexical"]["hit_at_1_count"],
              "positive": methods["graphify_lexical"]["positive_targets"],
              "jevSeconds": summary["provider_wall_seconds_sum"],
              "jevRequests": summary["provider_requests"],
              "primaryGate": summary["primary"]["frozen_gate_supported"],
              "edgeGate": summary["edge_filter"]["frozen_gate_supported"]}
    repos = [repository(study, round_dir, name, pairs, rankings, keyword, summary)
             for name in study["repositories"]]
    return pooled, repos


def build(out: Path, benchmarks: Path) -> None:
    studies, repositories = {}, []
    for study in STUDIES:
        loaded = study_data(study, benchmarks)
        if loaded is not None:
            studies[study["key"]], repos = loaded
            repositories += repos
    data = {"studies": studies, "repositories": repositories}
    template = (HERE / "template.html").read_text()
    out.write_text(template.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))))
    print(f"wrote {out} ({out.stat().st_size // 1024} KiB): "
          + ", ".join(f"{repo['name']} {repo['shownNodes']}/{repo['totalNodes']} nodes" for repo in repositories))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "jev-map-graph.html")
    parser.add_argument("--benchmarks", type=Path, default=HERE.parent / "benchmarks")
    args = parser.parse_args()
    build(args.out, args.benchmarks)


if __name__ == "__main__":
    main()
