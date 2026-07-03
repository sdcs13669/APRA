#!/usr/bin/env python3
"""
Convert REAL APRA trace data from agg_records/ into the CSV formats
expected by the replay page.

Reads ALL APRA experiments from the result directory and generates
per-dataset per-attack trace files.

Outputs:
  - public/data/apra_client_trace_{dataset}_{attack}.csv
  - public/data/apra_round_summary_{dataset}_{attack}.csv
  - public/data/apra_client_trace.csv  (default: first APRA experiment)
  - public/data/apra_round_summary.csv (default: first APRA experiment)
"""

import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR.parent / "main" / "re_result_6-29_APRA"
PUBLIC_DATA = BASE_DIR / "public" / "data"

ATTACK_MAP = {
    "a3fl": "a3fl",
    "sin-adv_DOBA": "doba",
    "sin-adv": "doba",
    "neurotoxin": "neurotoxin",
    "modelreplace": "modelreplace",
    "modelreplace_2": "modelreplace",
    "modelreplace_5": "modelreplace",
    "reba": "reba",
}

DATASETS = ["cifar10", "cifar100"]


def find_apra_dirs():
    """Find ALL APRA experiment directories with their dataset and attack types."""
    results = []
    for d in sorted(RESULT_DIR.iterdir()):
        if not d.is_dir() or "_apra_" not in d.name:
            continue

        # Determine dataset
        dataset = None
        for ds in DATASETS:
            if d.name.startswith(ds + "_"):
                dataset = ds
                break
        if dataset is None:
            continue

        # Determine attack from dir name
        parts = d.name.split("_")
        attack = None
        # Find attack after defense marker
        dm_idx = None
        for i, p in enumerate(parts):
            if p == "apra":
                dm_idx = i
                break
        if dm_idx is not None:
            after_def = parts[dm_idx + 1:]
            remaining = "_".join(after_def)
            for key in sorted(ATTACK_MAP.keys(), key=len, reverse=True):
                if key in remaining:
                    attack = ATTACK_MAP[key]
                    break

        if attack:
            results.append((d, dataset, attack))
    return results


def load_csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def parse_json(val, default=None):
    if not val or val.strip() == "":
        return default if default is not None else []
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def json_arr(arr):
    return json.dumps(arr)


def process_apra_experiment(apra_dir, attack):
    """Process one APRA experiment and return (client_trace_rows, round_summary_rows)."""
    params_path = apra_dir / "params.yaml.txt"
    na = 5
    if params_path.exists():
        try:
            with open(params_path) as f:
                params = yaml.safe_load(f)
        except Exception:
            with open(params_path) as f:
                params = yaml.full_load(f)
        if params:
            na = params.get("num_adversaries", 5)

    rounds_path = apra_dir / "agg_records" / "agg_rounds.csv"
    stages_path = apra_dir / "agg_records" / "agg_stages.csv"
    if not rounds_path.exists() or not stages_path.exists():
        return [], []

    rounds = load_csv_rows(rounds_path)
    stages = load_csv_rows(stages_path)

    stages_by_epoch = defaultdict(dict)
    for s in stages:
        epoch = int(float(s.get("epoch", 0)))
        stage_name = s.get("stage", "")
        sel = parse_json(s.get("selected", "[]"), [])
        rej = parse_json(s.get("rejected", "[]"), [])
        human = parse_json(s.get("human", ""), {})
        stages_by_epoch[epoch][stage_name] = {
            "selected": sel, "rejected": rej, "human": human,
        }

    round_summary_rows = []
    client_trace_rows = []

    for r in rounds:
        epoch = int(float(r.get("epoch", 0)))
        participants = parse_json(r.get("initial_participants", "[]"), [])
        final_sel = parse_json(r.get("final_selected", "[]"), [])
        rejected = parse_json(r.get("rejected", "[]"), [])
        num_sampled = len(participants)

        epoch_stages = stages_by_epoch.get(epoch, {})
        mad_stage = epoch_stages.get("apra_mad_filter", {})
        cluster_stage = epoch_stages.get("apra_hierarchical_cluster", {})
        clip_stage = epoch_stages.get("apra_trust_weighted_clip", {})

        mad_sel = mad_stage.get("selected", [])
        mad_rej = mad_stage.get("rejected", [])
        mad_hu = mad_stage.get("human", {})

        cluster_sel = cluster_stage.get("selected", [])
        cluster_rej = cluster_stage.get("rejected", [])
        cluster_hu = cluster_stage.get("human", {})

        clip_hu = clip_stage.get("human", {})

        sampled_benign = [pid for pid in participants if pid >= na]
        sampled_malicious = [pid for pid in participants if pid < na]

        mad_effective_pass = [pid for pid in mad_sel if pid in cluster_sel]
        mad_effective_reject = [pid for pid in mad_sel if pid not in cluster_sel]

        cluster_effective_pass = [pid for pid in cluster_sel if pid in final_sel]
        cluster_effective_reject = [pid for pid in cluster_sel if pid not in final_sel]

        final_sel_benign = [pid for pid in final_sel if pid >= na]
        final_sel_malicious = [pid for pid in final_sel if pid < na]
        final_rej_benign = [pid for pid in rejected if pid >= na]
        final_rej_malicious = [pid for pid in rejected if pid < na]

        round_summary_rows.append({
            "epoch": epoch, "num_sampled": num_sampled, "num_adversaries": na,
            "sampled_ids": json_arr(participants),
            "sampled_benign_ids": json_arr(sampled_benign),
            "sampled_malicious_ids": json_arr(sampled_malicious),
            "mad_median_norm": mad_hu.get("median_norm"),
            "mad_mad": mad_hu.get("mad"),
            "mad_k": mad_hu.get("k"),
            "mad_safety_keep_used": int(mad_hu.get("safety_keep_used", False)),
            "mad_fallback_used": int(mad_hu.get("fallback_used", False)),
            "mad_pass_ids": json_arr(mad_sel),
            "mad_reject_ids": json_arr(mad_rej),
            "mad_effective_pass_ids": json_arr(mad_effective_pass),
            "mad_effective_reject_ids": json_arr(mad_effective_reject),
            "mad_pass_benign_ids": json_arr([pid for pid in mad_sel if pid >= na]),
            "mad_pass_malicious_ids": json_arr([pid for pid in mad_sel if pid < na]),
            "mad_reject_benign_ids": json_arr([pid for pid in mad_rej if pid >= na]),
            "mad_reject_malicious_ids": json_arr([pid for pid in mad_rej if pid < na]),
            "cluster_best_k": cluster_hu.get("best_k"),
            "cluster_best_score": cluster_hu.get("best_score"),
            "cluster_scores": json.dumps(cluster_hu.get("cluster_scores", {})),
            "cluster_selected_cluster": cluster_hu.get("selected_cluster"),
            "cluster_fallback_used": int(cluster_hu.get("fallback_used", False)),
            "cluster_pass_ids": json_arr(cluster_sel),
            "cluster_reject_ids": json_arr(cluster_rej),
            "cluster_effective_pass_ids": json_arr(cluster_effective_pass),
            "cluster_effective_reject_ids": json_arr(cluster_effective_reject),
            "cluster_pass_benign_ids": json_arr([pid for pid in cluster_sel if pid >= na]),
            "cluster_pass_malicious_ids": json_arr([pid for pid in cluster_sel if pid < na]),
            "cluster_reject_benign_ids": json_arr([pid for pid in cluster_rej if pid >= na]),
            "cluster_reject_malicious_ids": json_arr([pid for pid in cluster_rej if pid < na]),
            "final_selected_ids": json_arr(final_sel),
            "final_rejected_ids": json_arr(rejected),
            "final_selected_benign_ids": json_arr(final_sel_benign),
            "final_selected_malicious_ids": json_arr(final_sel_malicious),
            "final_rejected_benign_ids": json_arr(final_rej_benign),
            "final_rejected_malicious_ids": json_arr(final_rej_malicious),
            "final_selected_benign_count": len(final_sel_benign),
            "final_selected_malicious_count": len(final_sel_malicious),
            "final_rejected_benign_count": len(final_rej_benign),
            "final_rejected_malicious_count": len(final_rej_malicious),
        })

        # ---- Client trace rows ----
        all_client_ids = set(participants)
        for stg in [mad_sel, mad_rej, cluster_sel, cluster_rej]:
            all_client_ids.update(stg)

        trust_weights = clip_hu.get("trust_weights", {})
        base_clip = clip_hu.get("base_clip", 1.0)
        cluster_scores_dict = cluster_hu.get("cluster_scores", {})
        selected_cluster = cluster_hu.get("selected_cluster", 0)

        for cid in sorted(all_client_ids):
            is_adv = 1 if cid < na else 0
            in_sample = cid in participants

            mad_pass = 1 if cid in mad_sel else 0
            mad_eff = 1 if cid in mad_effective_pass else 0
            cluster_pass = 1 if cid in cluster_sel else 0
            cluster_eff = 1 if cid in cluster_effective_pass else 0
            final_sel_flag = 1 if cid in final_sel else 0

            if not in_sample:
                cluster_label = -1
            elif cluster_pass:
                cluster_label = selected_cluster
            else:
                other_labels = [int(k) for k in cluster_scores_dict.keys() if int(k) != selected_cluster]
                cluster_label = other_labels[0] if other_labels else -1

            tw = trust_weights.get(str(cid), 0.0)
            clip_factor = base_clip if tw > 0 else 0.0

            client_trace_rows.append({
                "epoch": epoch, "client_id": cid,
                "role": "adversary" if is_adv else "benign",
                "is_adversary": is_adv, "update_norm": 0, "mad_z_score": 0,
                "mad_pass": mad_pass, "mad_effective_pass": mad_eff,
                "cluster_label": cluster_label, "selected_cluster": selected_cluster,
                "cluster_pass": cluster_pass, "cluster_effective_pass": cluster_eff,
                "final_selected": final_sel_flag,
                "trust_weight": round(tw, 6) if isinstance(tw, (int, float)) else 0,
                "clip_factor": round(clip_factor, 6),
                "update_norm_before_clip": 0, "update_norm_after_clip": 0,
                "feature_norm": 0, "feature_0": 0, "feature_1": 0, "feature_2": 0,
            })

    return client_trace_rows, round_summary_rows


CLIENT_FIELDS = [
    "epoch", "client_id", "role", "is_adversary", "update_norm",
    "mad_z_score", "mad_pass", "mad_effective_pass",
    "cluster_label", "selected_cluster", "cluster_pass", "cluster_effective_pass",
    "final_selected", "trust_weight", "clip_factor",
    "update_norm_before_clip", "update_norm_after_clip",
    "feature_norm", "feature_0", "feature_1", "feature_2",
]
ROUND_FIELDS = [
    "epoch", "num_sampled", "num_adversaries",
    "sampled_ids", "sampled_benign_ids", "sampled_malicious_ids",
    "mad_median_norm", "mad_mad", "mad_k",
    "mad_safety_keep_used", "mad_fallback_used",
    "mad_pass_ids", "mad_reject_ids",
    "mad_effective_pass_ids", "mad_effective_reject_ids",
    "mad_pass_benign_ids", "mad_pass_malicious_ids",
    "mad_reject_benign_ids", "mad_reject_malicious_ids",
    "cluster_best_k", "cluster_best_score", "cluster_scores",
    "cluster_selected_cluster", "cluster_fallback_used",
    "cluster_pass_ids", "cluster_reject_ids",
    "cluster_effective_pass_ids", "cluster_effective_reject_ids",
    "cluster_pass_benign_ids", "cluster_pass_malicious_ids",
    "cluster_reject_benign_ids", "cluster_reject_malicious_ids",
    "final_selected_ids", "final_rejected_ids",
    "final_selected_benign_ids", "final_selected_malicious_ids",
    "final_rejected_benign_ids", "final_rejected_malicious_ids",
    "final_selected_benign_count", "final_selected_malicious_count",
    "final_rejected_benign_count", "final_rejected_malicious_count",
]


def main():
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

    apra_dirs = find_apra_dirs()
    if not apra_dirs:
        print("ERROR: No APRA experiments found in", RESULT_DIR)
        return

    first_dataset = None
    first_attack = None

    for apra_dir, dataset, attack in apra_dirs:
        print(f"Processing APRA {dataset}/{attack}: {apra_dir.name}")
        client_rows, round_rows = process_apra_experiment(apra_dir, attack)

        if not client_rows and not round_rows:
            print(f"  SKIP (no agg_records data)")
            continue

        # Per-dataset per-attack files
        ct_file = PUBLIC_DATA / f"apra_client_trace_{dataset}_{attack}.csv"
        rs_file = PUBLIC_DATA / f"apra_round_summary_{dataset}_{attack}.csv"
        with open(ct_file, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CLIENT_FIELDS)
            w.writeheader(); w.writerows(client_rows)
        with open(rs_file, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=ROUND_FIELDS)
            w.writeheader(); w.writerows(round_rows)
        print(f"  -> {ct_file.name} ({len(client_rows)} rows)")
        print(f"  -> {rs_file.name} ({len(round_rows)} rows)")

        # Keep first experiment as default
        if first_dataset is None:
            first_dataset = dataset
            first_attack = attack
            shutil.copy2(ct_file, PUBLIC_DATA / "apra_client_trace.csv")
            shutil.copy2(rs_file, PUBLIC_DATA / "apra_round_summary.csv")

        # Also keep per-attack files for backward compatibility
        ct_legacy = PUBLIC_DATA / f"apra_client_trace_{attack}.csv"
        rs_legacy = PUBLIC_DATA / f"apra_round_summary_{attack}.csv"
        shutil.copy2(ct_file, ct_legacy)
        shutil.copy2(rs_file, rs_legacy)

    print(f"\nDone — {len(apra_dirs)} APRA experiments processed.")
    print(f"Default trace files (dataset={first_dataset}, attack={first_attack})")


if __name__ == "__main__":
    main()
