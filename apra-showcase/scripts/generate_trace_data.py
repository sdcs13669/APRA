#!/usr/bin/env python3
"""
Generate synthetic APRA trace data for the replay page and dashboard charts.

Outputs:
  - public/data/apra_client_trace.csv   (~7000 rows, 10 clients x 700 rounds)
  - public/data/apra_round_summary.csv  (~700 rows)
"""

import csv
import json
import math
import random

from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DATA = BASE_DIR / "public" / "data"
PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
TOTAL_CLIENTS = 100
SAMPLE_SIZE = 10
NUM_ADVERSARIES = 5  # IDs 0..4
TOTAL_ROUNDS = 700
POISON_EPOCHS = 350  # first 350 rounds have adversary attacks

K_INIT = 5.0
K_DECAY = 0.1

ADV_IDS = set(range(NUM_ADVERSARIES))
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def decaying_k(epoch: int) -> float:
    return max(2.0, K_INIT * math.exp(-K_DECAY * epoch))


def median(values):
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return float(s[n // 2])
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def mad(values):
    med = median(values)
    abs_devs = [abs(v - med) for v in values]
    m = median(abs_devs)
    return m * 1.4826 if m > 0 else 1e-9


def json_arr(ints):
    return json.dumps(ints)


def soft_mad_pass(z_score, k):
    """Probabilistic MAD pass that models small-sample noise.

    For a strict threshold this would be (abs(z) <= k).  We soften it so
    that at the boundary there is a realistic chance of both outcomes,
    which is what happens when MAD is estimated from only 10 samples.
    """
    # Effective threshold with ~15% random fluctuation
    k_eff = k * random.uniform(0.85, 1.15)
    return 1 if abs(z_score) <= k_eff else 0


# ---------------------------------------------------------------------------
# Generate data
# ---------------------------------------------------------------------------

client_trace_rows = []
round_summary_rows = []

for epoch in range(1, TOTAL_ROUNDS + 1):
    is_attack_epoch = epoch <= POISON_EPOCHS

    # 1. Sample 10 clients
    sampled_ids = sorted(random.sample(range(TOTAL_CLIENTS), SAMPLE_SIZE))

    # Adversarial IDs are only considered "malicious" during poison epochs
    adversarial_in_sample = [
        cid for cid in sampled_ids if cid in ADV_IDS and is_attack_epoch
    ]
    benign_in_sample = [
        cid for cid in sampled_ids if cid not in adversarial_in_sample
    ]
    num_adv_behavioral = len(adversarial_in_sample)

    # 2. Build per-client data
    clients = []
    for cid in sampled_ids:
        is_adv = cid in ADV_IDS and is_attack_epoch

        if is_adv:
            # ~40% of adversaries keep norms moderately high to simulate
            # stealthy attacks that partially evade detection
            if random.random() < 0.40:
                update_norm = random.uniform(1.5, 2.5)
            else:
                update_norm = random.uniform(2.5, 4.5)
            trust_weight = random.uniform(0.01, 0.05)
            clip_factor = random.uniform(0.2, 0.4)
        else:
            # Benign (or post-attack adversary): normal update range
            update_norm = random.uniform(0.3, 1.8)
            trust_weight = random.uniform(0.10, 0.15)
            clip_factor = random.uniform(0.8, 1.0)

        update_before = update_norm
        update_after = update_norm * clip_factor
        feature_norm = random.uniform(0.1, 0.5)
        f0 = random.uniform(-0.5, 0.5)
        f1 = random.uniform(-0.5, 0.5)
        f2 = random.uniform(-0.5, 0.5)

        clients.append({
            "client_id": cid,
            "is_adversary": int(is_adv),
            "update_norm": round(update_norm, 6),
            "update_norm_before_clip": round(update_before, 6),
            "update_norm_after_clip": round(update_after, 6),
            "trust_weight": round(trust_weight, 6),
            "clip_factor": round(clip_factor, 6),
            "feature_norm": round(feature_norm, 6),
            "feature_0": round(f0, 6),
            "feature_1": round(f1, 6),
            "feature_2": round(f2, 6),
        })

    norms = [c["update_norm"] for c in clients]
    med_norm = median(norms)
    mad_val = mad(norms)
    k = decaying_k(epoch)

    # 3. MAD z-scores
    for c in clients:
        c["mad_z_score"] = round(
            (c["update_norm"] - med_norm) / mad_val, 6
        ) if mad_val > 0 else 0.0

    # 4. MAD pass / reject (soft threshold with noise)
    mad_pass_ids = []
    mad_reject_ids = []
    for c in clients:
        c["mad_pass"] = soft_mad_pass(c["mad_z_score"], k)
        if c["mad_pass"]:
            mad_pass_ids.append(c["client_id"])
        else:
            mad_reject_ids.append(c["client_id"])

    # Safety-keep: if too few pass, force-keep the best ones
    min_keep = max(2, SAMPLE_SIZE // 2)
    mad_safety_keep = False
    if len(mad_pass_ids) < min_keep:
        mad_safety_keep = True
        sorted_clients = sorted(clients, key=lambda x: abs(x["mad_z_score"]))
        kept = set(c["client_id"] for c in sorted_clients[:min_keep])
        mad_pass_ids = [cid for cid in sampled_ids if cid in kept]
        mad_reject_ids = [cid for cid in sampled_ids if cid not in kept]
        for c in clients:
            c["mad_pass"] = 1 if c["client_id"] in kept else 0

    # MAD effective pass (stricter)
    mad_effective_pass_ids = []
    mad_effective_reject_ids = []
    for c in clients:
        if c["mad_pass"] == 1 and abs(c["mad_z_score"]) <= k * 0.8:
            c["mad_effective_pass"] = 1
            mad_effective_pass_ids.append(c["client_id"])
        else:
            c["mad_effective_pass"] = 0
            if c["mad_pass"] == 1:
                mad_effective_reject_ids.append(c["client_id"])

    mad_pass_benign = [
        cid for cid in mad_pass_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    mad_pass_malicious = [
        cid for cid in mad_pass_ids if cid in ADV_IDS and is_attack_epoch
    ]
    mad_reject_benign = [
        cid for cid in mad_reject_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    mad_reject_malicious = [
        cid for cid in mad_reject_ids if cid in ADV_IDS and is_attack_epoch
    ]

    # 5. Hierarchical clustering simulation
    cluster_labels = {}
    for c in clients:
        if c["is_adversary"]:
            # 55% chance the adversary is separated into a minority cluster
            if random.random() < 0.55:
                label = random.choice([1, 2])
            else:
                label = 0  # blends in with the benign cluster
        else:
            label = 0
        cluster_labels[c["client_id"]] = label
        c["cluster_label"] = label

    # The largest cluster is chosen as the "good" cluster
    cluster_counts = {}
    for c in clients:
        lbl = cluster_labels[c["client_id"]]
        cluster_counts[lbl] = cluster_counts.get(lbl, 0) + 1
    selected_cluster = max(cluster_counts, key=cluster_counts.get)

    # Cluster scores (silhouette-like)
    cluster_scores = {
        str(k): round(random.uniform(0.3, 0.9), 4)
        for k in cluster_counts
    }
    cluster_best_k = len(cluster_counts)
    cluster_best_score = max(cluster_scores.values())

    cluster_pass_ids = []
    cluster_reject_ids = []
    cluster_effective_pass_ids = []
    cluster_effective_reject_ids = []

    for c in clients:
        c["selected_cluster"] = selected_cluster
        in_selected = 1 if cluster_labels[c["client_id"]] == selected_cluster else 0
        c["cluster_pass"] = in_selected
        if in_selected:
            cluster_pass_ids.append(c["client_id"])
        else:
            cluster_reject_ids.append(c["client_id"])
        if in_selected and random.random() < 0.9:
            c["cluster_effective_pass"] = 1
            cluster_effective_pass_ids.append(c["client_id"])
        else:
            c["cluster_effective_pass"] = 0
            if in_selected:
                cluster_effective_reject_ids.append(c["client_id"])

    cluster_fallback = random.random() < 0.05

    cluster_pass_benign = [
        cid for cid in cluster_pass_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    cluster_pass_malicious = [
        cid for cid in cluster_pass_ids if cid in ADV_IDS and is_attack_epoch
    ]
    cluster_reject_benign = [
        cid for cid in cluster_reject_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    cluster_reject_malicious = [
        cid for cid in cluster_reject_ids if cid in ADV_IDS and is_attack_epoch
    ]

    # 6. Final selection: intersection of MAD pass and cluster pass
    final_selected_ids = sorted(set(mad_pass_ids) & set(cluster_pass_ids))
    final_rejected_ids = sorted(set(sampled_ids) - set(final_selected_ids))

    for c in clients:
        c["final_selected"] = 1 if c["client_id"] in final_selected_ids else 0

    final_selected_benign = [
        cid for cid in final_selected_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    final_selected_malicious = [
        cid for cid in final_selected_ids if cid in ADV_IDS and is_attack_epoch
    ]
    final_rejected_benign = [
        cid for cid in final_rejected_ids
        if not (cid in ADV_IDS and is_attack_epoch)
    ]
    final_rejected_malicious = [
        cid for cid in final_rejected_ids if cid in ADV_IDS and is_attack_epoch
    ]

    # 7. Write round summary
    round_summary_rows.append({
        "epoch": epoch,
        "num_sampled": len(sampled_ids),
        "num_adversaries": num_adv_behavioral,
        "sampled_ids": json_arr(sampled_ids),
        "sampled_benign_ids": json_arr(benign_in_sample),
        "sampled_malicious_ids": json_arr(adversarial_in_sample),
        "mad_median_norm": round(med_norm, 6),
        "mad_mad": round(mad_val, 6),
        "mad_k": round(k, 6),
        "mad_safety_keep_used": int(mad_safety_keep),
        "mad_fallback_used": 0,
        "mad_pass_ids": json_arr(mad_pass_ids),
        "mad_reject_ids": json_arr(mad_reject_ids),
        "mad_effective_pass_ids": json_arr(mad_effective_pass_ids),
        "mad_effective_reject_ids": json_arr(mad_effective_reject_ids),
        "mad_pass_benign_ids": json_arr(mad_pass_benign),
        "mad_pass_malicious_ids": json_arr(mad_pass_malicious),
        "mad_reject_benign_ids": json_arr(mad_reject_benign),
        "mad_reject_malicious_ids": json_arr(mad_reject_malicious),
        "cluster_best_k": cluster_best_k,
        "cluster_best_score": cluster_best_score,
        "cluster_scores": json.dumps(cluster_scores),
        "cluster_selected_cluster": selected_cluster,
        "cluster_fallback_used": int(cluster_fallback),
        "cluster_pass_ids": json_arr(cluster_pass_ids),
        "cluster_reject_ids": json_arr(cluster_reject_ids),
        "cluster_effective_pass_ids": json_arr(cluster_effective_pass_ids),
        "cluster_effective_reject_ids": json_arr(cluster_effective_reject_ids),
        "cluster_pass_benign_ids": json_arr(cluster_pass_benign),
        "cluster_pass_malicious_ids": json_arr(cluster_pass_malicious),
        "cluster_reject_benign_ids": json_arr(cluster_reject_benign),
        "cluster_reject_malicious_ids": json_arr(cluster_reject_malicious),
        "final_selected_ids": json_arr(final_selected_ids),
        "final_rejected_ids": json_arr(final_rejected_ids),
        "final_selected_benign_ids": json_arr(final_selected_benign),
        "final_selected_malicious_ids": json_arr(final_selected_malicious),
        "final_rejected_benign_ids": json_arr(final_rejected_benign),
        "final_rejected_malicious_ids": json_arr(final_rejected_malicious),
        "final_selected_benign_count": len(final_selected_benign),
        "final_selected_malicious_count": len(final_selected_malicious),
        "final_rejected_benign_count": len(final_rejected_benign),
        "final_rejected_malicious_count": len(final_rejected_malicious),
    })

    # 8. Write per-client trace rows
    for c in clients:
        client_trace_rows.append({
            "epoch": epoch,
            "client_id": c["client_id"],
            "role": "adversary" if c["is_adversary"] else "benign",
            "is_adversary": c["is_adversary"],
            "update_norm": c["update_norm"],
            "mad_z_score": c["mad_z_score"],
            "mad_pass": c["mad_pass"],
            "mad_effective_pass": c["mad_effective_pass"],
            "cluster_label": c["cluster_label"],
            "selected_cluster": c["selected_cluster"],
            "cluster_pass": c["cluster_pass"],
            "cluster_effective_pass": c["cluster_effective_pass"],
            "final_selected": c["final_selected"],
            "trust_weight": c["trust_weight"],
            "clip_factor": c["clip_factor"],
            "update_norm_before_clip": c["update_norm_before_clip"],
            "update_norm_after_clip": c["update_norm_after_clip"],
            "feature_norm": c["feature_norm"],
            "feature_0": c["feature_0"],
            "feature_1": c["feature_1"],
            "feature_2": c["feature_2"],
        })

# ---------------------------------------------------------------------------
# Write CSVs
# ---------------------------------------------------------------------------

CLIENT_TRACE_FILE = PUBLIC_DATA / "apra_client_trace.csv"
ROUND_SUMMARY_FILE = PUBLIC_DATA / "apra_round_summary.csv"

client_fields = [
    "epoch", "client_id", "role", "is_adversary", "update_norm",
    "mad_z_score", "mad_pass", "mad_effective_pass",
    "cluster_label", "selected_cluster", "cluster_pass", "cluster_effective_pass",
    "final_selected", "trust_weight", "clip_factor",
    "update_norm_before_clip", "update_norm_after_clip",
    "feature_norm", "feature_0", "feature_1", "feature_2",
]

round_fields = [
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

with open(CLIENT_TRACE_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=client_fields)
    writer.writeheader()
    writer.writerows(client_trace_rows)

with open(ROUND_SUMMARY_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=round_fields)
    writer.writeheader()
    writer.writerows(round_summary_rows)

print(f"Wrote {len(client_trace_rows)} rows -> {CLIENT_TRACE_FILE}")
print(f"Wrote {len(round_summary_rows)} rows -> {ROUND_SUMMARY_FILE}")
print("Done.")
