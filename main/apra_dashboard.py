#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml

ROOT = Path(__file__).resolve().parent
RESULT_ROOT = ROOT / "re_result_6-29_APRA"
HTML_PATH = ROOT / "apra_dashboard.html"

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv(path):
    if not path or not path.exists():
        return [], []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def read_csv_rows(path):
    rows, _ = read_csv(path)
    return rows


def find_file(directory, suffix):
    for f in directory.iterdir():
        if f.name.endswith(suffix):
            return f
    return None


# ---------------------------------------------------------------------------
# Directory-name / param parsing
# ---------------------------------------------------------------------------

def parse_name(directory):
    """Parse directory name:
    {dataset}_{epochs}_{date}_{time}_{method}_fix_True_{mia}_{mia_class}_{noise}_{attack}
    """
    parts = directory.name.split("_")
    idx = 0
    dataset = parts[idx] if len(parts) > idx else ""
    idx += 1
    epochs = parts[idx] if len(parts) > idx else ""
    idx += 1
    # date_time: next 2 parts (e.g. Jun.29, 17.23.12)
    date_part1 = parts[idx] if len(parts) > idx else ""
    idx += 1
    date_part2 = parts[idx] if len(parts) > idx else ""
    idx += 1
    created = f"{date_part1}_{date_part2}"
    method = parts[idx] if len(parts) > idx else ""
    idx += 1
    # skip fix_True
    idx += 1
    idx += 1
    mia = parts[idx] if len(parts) > idx else ""
    idx += 1
    mia_class = parts[idx] if len(parts) > idx else ""
    idx += 1
    noise = parts[idx] if len(parts) > idx else ""
    idx += 1
    attack = "_".join(parts[idx:]) if idx < len(parts) else ""
    return {
        "id": directory.name,
        "dataset": dataset,
        "epochs": epochs,
        "created": created,
        "agg_method": method,
        "attack": attack,
    }


def parse_yaml_params(directory):
    params_path = directory / "params.yaml.txt"
    if not params_path.exists():
        return {}
    try:
        with params_path.open() as f:
            params = yaml.safe_load(f)
        return {
            "num_adversaries": params.get("num_adversaries", 5),
            "num_total_participants": params.get("num_total_participants", 100),
            "num_sampled_participants": params.get("num_sampled_participants", 10),
        }
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# CSV data loaders
# ---------------------------------------------------------------------------

def load_accuracy(directory):
    path = find_file(directory, "_accuracy.csv")
    rows = read_csv_rows(path)
    data = []
    for r in rows:
        epoch_str = r.get("", "0") or "0"
        data.append({
            "epoch": int(float(epoch_str)),
            "main": float(r.get("main", 0) or 0),
            "main_loss": float(r.get("main_loss", 0) or 0),
            "backdoor": float(r.get("backdoor", 0) or 0),
            "backdoor_loss": float(r.get("backdoor_loss", 0) or 0),
            "lr": float(r.get("lr", 0) or 0),
        })
    return data


def load_trajectory(directory):
    path = find_file(directory, "_trajectory.csv")
    rows = read_csv_rows(path)
    data = []
    for r in rows:
        data.append({
            "epoch": int(float(r.get("epoch", 0) or 0)),
            "cosine_similarity": float(r.get("cosine_similarity", 0) or 0),
            "l2_distance": float(r.get("l2_distance", 0) or 0),
            "backdoor": float(r.get("backdoor", 0) or 0),
            "main": float(r.get("main", 0) or 0),
        })
    return data


def load_agg_rounds(directory):
    path = directory / "agg_records" / "agg_rounds.csv"
    rows = read_csv_rows(path)
    parsed = []
    for r in rows:
        parsed.append({
            "epoch": int(float(r.get("epoch", 0) or 0)),
            "method": r.get("method", ""),
            "status": r.get("status", ""),
            "initial_participants": json.loads(r.get("initial_participants", "[]") or "[]"),
            "final_selected": json.loads(r.get("final_selected", "[]") or "[]"),
            "rejected": json.loads(r.get("rejected", "[]") or "[]"),
            "num_initial": int(float(r.get("num_initial", 0) or 0)),
            "num_final": int(float(r.get("num_final", 0) or 0)),
        })
    return parsed


def load_agg_stages(directory):
    path = directory / "agg_records" / "agg_stages.csv"
    rows = read_csv_rows(path)
    parsed = []
    for r in rows:
        selected_raw = r.get("selected", "[]") or "[]"
        rejected_raw = r.get("rejected", "[]") or "[]"
        human_raw = r.get("human", "") or ""
        selected = json.loads(selected_raw)
        rejected = json.loads(rejected_raw)
        human = json.loads(human_raw) if human_raw else {}
        parsed.append({
            "epoch": int(float(r.get("epoch", 0) or 0)),
            "method": r.get("method", ""),
            "stage": r.get("stage", ""),
            "selected": selected,
            "rejected": rejected,
            "human": human,
        })
    return parsed


# ---------------------------------------------------------------------------
# Summarisation
# ---------------------------------------------------------------------------

def compute_summary(agg_rounds, num_adversaries):
    total_malicious_sampled = 0
    total_malicious_rejected = 0
    for r in agg_rounds:
        participants = r["initial_participants"]
        rejected = r["rejected"]
        sampled_mal = [pid for pid in participants if pid < num_adversaries]
        rejected_mal = [pid for pid in rejected if pid < num_adversaries]
        total_malicious_sampled += len(sampled_mal)
        total_malicious_rejected += len(rejected_mal)
    return {
        "total_rounds": len(agg_rounds),
        "malicious_sampled": total_malicious_sampled,
        "malicious_rejected": total_malicious_rejected,
        "screening_rate": total_malicious_rejected / total_malicious_sampled
        if total_malicious_sampled
        else 0,
    }


STAGE_LABELS = {
    "apra_mad_filter": "MAD 过滤",
    "apra_hierarchical_cluster": "层次聚类",
    "apra_trust_weighted_clip": "信任加权裁剪",
    "deepsight_ensemble_cluster": "集成聚类",
    "deepsight_final_filter": "最终过滤",
    "rflbat_first_distance_filter": "第一距离过滤",
    "rflbat_cluster_filter": "聚类过滤",
    "rflbat_final_distance_filter": "最终距离过滤",
    "avg": "FedAvg 平均",
    "clip": "裁剪聚合",
    "foolsgold": "FoolsGold",
}


def scan_experiments():
    found = []
    if not RESULT_ROOT.exists():
        return found
    for directory in sorted(RESULT_ROOT.iterdir()):
        if not directory.is_dir():
            continue
        if not (directory / "agg_records" / "agg_stages.csv").exists():
            continue
        meta = parse_name(directory)
        params = parse_yaml_params(directory)
        na = params.get("num_adversaries", 5)
        meta["num_adversaries"] = na
        meta["num_total_participants"] = params.get("num_total_participants", 100)
        acc = load_accuracy(directory)
        meta["final_main_acc"] = acc[-1]["main"] if acc else None
        meta["final_backdoor_acc"] = acc[-1]["backdoor"] if acc else None
        agg_rounds = load_agg_rounds(directory)
        meta["summary"] = compute_summary(agg_rounds, na)
        stages = load_agg_stages(directory)
        stage_names = list(dict.fromkeys(s["stage"] for s in stages))
        meta["stages"] = [
            {"name": s, "label": STAGE_LABELS.get(s, s)} for s in stage_names
        ]
        found.append(meta)
    found.sort(key=lambda x: (x["attack"], x["created"]))
    return found


def load_experiment(exp_id):
    directory = RESULT_ROOT / exp_id
    if not directory.exists():
        return None
    meta = parse_name(directory)
    params = parse_yaml_params(directory)
    na = params.get("num_adversaries", 5)
    meta["num_adversaries"] = na
    meta["num_total_participants"] = params.get("num_total_participants", 100)
    acc = load_accuracy(directory)
    traj = load_trajectory(directory)
    agg_rounds = load_agg_rounds(directory)
    stages = load_agg_stages(directory)
    stage_names = list(dict.fromkeys(s["stage"] for s in stages))
    meta["stages"] = [
        {"name": s, "label": STAGE_LABELS.get(s, s)} for s in stage_names
    ]
    meta["summary"] = compute_summary(agg_rounds, na)
    meta["final_main_acc"] = acc[-1]["main"] if acc else None
    meta["final_backdoor_acc"] = acc[-1]["backdoor"] if acc else None
    meta["total_rounds"] = len(agg_rounds)
    return {
        "meta": meta,
        "accuracy": acc,
        "trajectory": traj,
        "num_adversaries": na,
    }


def load_trace(exp_id, page, page_size):
    directory = RESULT_ROOT / exp_id
    if not directory.exists():
        return None
    params = parse_yaml_params(directory)
    na = params.get("num_adversaries", 5)
    agg_rounds = load_agg_rounds(directory)
    agg_stages = load_agg_stages(directory)

    # Group stages by epoch
    stages_by_epoch = defaultdict(list)
    for s in agg_stages:
        epoch = s["epoch"]
        stages_by_epoch[epoch].append({
            "name": s["stage"],
            "label": STAGE_LABELS.get(s["stage"], s["stage"]),
            "selected": s["selected"],
            "rejected": s["rejected"],
            "human": s["human"],
        })

    # Build merged rows
    merged = []
    for r in agg_rounds:
        epoch = r["epoch"]
        stgs = stages_by_epoch.get(epoch, [])
        enriched_stages = []
        for stg in stgs:
            sel = stg["selected"]
            rej = stg["rejected"]
            enriched_stages.append({
                **stg,
                "selected_count": len(sel),
                "rejected_count": len(rej),
                "selected_malicious": [pid for pid in sel if pid < na],
                "rejected_malicious": [pid for pid in rej if pid < na],
            })
        all_participants = r["initial_participants"]
        merged.append({
            "epoch": epoch,
            "method": r["method"],
            "status": r["status"],
            "num_initial": r["num_initial"],
            "num_final": r["num_final"],
            "initial_participants": all_participants,
            "final_selected": r["final_selected"],
            "rejected": r["rejected"],
            "stages": enriched_stages,
            "malicious_in_sample": [pid for pid in all_participants if pid < na],
            "malicious_rejected": [pid for pid in r["rejected"] if pid < na],
            "malicious_selected": [pid for pid in r["final_selected"] if pid < na],
        })
    total_rows = len(merged)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "page": page,
        "page_size": page_size,
        "total_rows": total_rows,
        "total_pages": total_pages,
        "num_adversaries": na,
        "rows": merged[start:end],
    }


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def send_html(self):
        data = HTML_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/":
            self.send_html()
        elif parsed.path == "/api/experiments":
            self.send_json({"experiments": scan_experiments()})
        elif parsed.path == "/api/experiment":
            exp_id = qs.get("id", [""])[0]
            data = load_experiment(exp_id)
            if data is None:
                self.send_json({"error": "not found"}, 404)
            else:
                self.send_json(data)
        elif parsed.path == "/api/trace":
            exp_id = qs.get("id", [""])[0]
            page = max(1, int(qs.get("page", ["1"])[0]))
            page_size = min(100, max(1, int(qs.get("page_size", ["10"])[0])))
            data = load_trace(exp_id, page, page_size)
            if data is None:
                self.send_json({"error": "not found"}, 404)
            else:
                self.send_json(data)
        else:
            self.send_json({"error": "not found"}, 404)


def main():
    parser = argparse.ArgumentParser(description="APRA Round Audit Dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8925, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"APRA dashboard: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
