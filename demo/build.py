"""Build the interactive graph demo from the archived held-out study.

Reads only benchmark 05's immutable round; nothing is recomputed or re-scored.
Usage: python demo/build.py [--out demo/jev-map-graph.html]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks.graphify_compare import graph_node
from benchmarks.toolbelt_study import equal_lexical

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent / "benchmarks/05-heldout-toolbelt/rounds/round-01-live"
REPOSITORIES = ("h11", "pluggy", "boltons")
TEST_DIRS = {"tests", "testing"}


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


def repository(name: str, pairs: list[dict], rankings: list[dict],
               keyword: set[tuple[str, str, str]], summary: dict) -> dict:
    graph = read(ROUND / f"graphify/{name}/graphify-out/graph.json")
    nodes = [node for node in graph["nodes"] if node.get("file_type") != "rationale"]
    index = {node["id"]: position for position, node in enumerate(nodes)}
    out_nodes = [{"label": node["label"], "file": node.get("source_file", ""),
                  "kind": node_kind(node)} for node in nodes]
    edges = [[index[edge["source"]], index[edge["target"]], edge["relation"]]
             for edge in graph["edges"]
             if edge["source"] in index and edge["target"] in index]

    def locate(symbol: str) -> int:
        node_id = graph_node(graph, symbol)
        if node_id is not None:
            return index[node_id]
        # Unmapped symbols get a visible stand-in beside their file's module node.
        path, _, qualified = symbol.partition("::")
        out_nodes.append({"label": qualified, "file": path, "kind": "code", "unmapped": True})
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
        if pair["repository"] != name or not pair["test_eligible"]:
            continue
        key = (name, pair["function"], pair["test"])
        links.append({"f": at(pair["function"]), "t": at(pair["test"]),
                      "score": pair["jev_score"], "jev": pair["jev_accepted"],
                      "keyword": key in keyword, "observed": pair["observed"],
                      "graphify": pair["graphify_link"]})

    targets = []
    for row in rankings:
        if row["repository"] != name:
            continue
        methods = row["methods"]
        before, after = methods["graphify_lexical"], methods["graphify_jev_lexical"]
        targets.append({
            "node": at(row["function"]), "symbol": row["function"],
            "candidates": [{**candidate, "node": at(candidate["test"])}
                           for candidate in row["jev_candidates"]],
            "observed": row["observed_tests"],
            "before": before[0]["test"] if before else None,
            "after": after[0]["test"] if after else None,
            "afterNode": at(after[0]["test"]) if after else None,
            "beforeHit": first_hit(before), "afterHit": first_hit(after),
            "positive": bool(row["observed_tests"]),
        })

    return {"name": name, "nodes": out_nodes, "edges": edges, "links": links,
            "targets": targets, "graphify": summary["graphify"][name]}


def build(out: Path) -> None:
    pairs = read(ROUND / "candidate-pairs.json")
    rankings = read(ROUND / "rankings.json")
    summary = read(ROUND / "summary.json")
    accepted = sum(pair["jev_accepted"] and bool(pair["test_eligible"]) for pair in pairs)
    keyword = equal_lexical(pairs, accepted)
    methods = summary["methods"]
    data = {
        "repositories": [repository(name, pairs, rankings, keyword, summary)
                         for name in REPOSITORIES],
        "pooled": {"edge": summary["edge_filter"],
                   "hitBefore": methods["graphify_lexical"]["hit_at_1_count"],
                   "hitAfter": methods["graphify_jev_lexical"]["hit_at_1_count"],
                   "positive": methods["graphify_lexical"]["positive_targets"],
                   "jevSeconds": summary["provider_wall_seconds_sum"],
                   "jevRequests": summary["provider_requests"]},
    }
    template = (HERE / "template.html").read_text()
    out.write_text(template.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))))
    print(f"wrote {out} ({out.stat().st_size // 1024} KiB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "jev-map-graph.html")
    build(parser.parse_args().out)


if __name__ == "__main__":
    main()
