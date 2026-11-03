"""Paired statistics for the matched 5k outer-loop bake-off (n=3 search seeds).
Input: figures/multiseed_summary.json search.approaches per-seed values.
Output: figures/stats_meta_approach_5k.json
"""
import json, itertools, random, statistics as st

d = json.load(open("figures/multiseed_summary.json"))
approaches = d["search"]["approaches"]
search_seeds = [1902771841, 2026072701, 2026072702]


def paired(a, b, name, B=20000, seed=1):
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    m, s = st.mean(diff), st.stdev(diff) if n > 1 else 0.0
    obs = abs(sum(diff))
    cnt = tot = 0
    for signs in itertools.product([1, -1], repeat=n):
        tot += 1
        cnt += abs(sum(sg * x for sg, x in zip(signs, diff))) >= obs - 1e-15
    rng = random.Random(seed)
    boots = sorted(st.mean(rng.choices(diff, k=n)) for _ in range(B))
    dz = m / s if s else float("inf")
    hedges = dz * (1 - 3 / (4 * (n - 1) - 1)) if n > 1 else float("inf")
    tcrit = {2: 4.303, 19: 2.093}.get(n - 1)
    return {
        "comparison": name,
        "n": n,
        "search_seeds": search_seeds,
        "mean_diff_hybrid_minus_other": m,
        "sd_diff": s,
        "t_ci95": [m - tcrit * s / (n**0.5), m + tcrit * s / (n**0.5)] if tcrit else None,
        "bootstrap_ci95_mean_diff": [boots[int(0.025 * B)], boots[int(0.975 * B)]],
        "exact_signflip_p_two_sided": cnt / tot,
        "cohen_dz": dz,
        "hedges_gz": hedges,
        "hybrid_wins": sum(x > 0 for x in diff),
    }


hyb = approaches["hybrid_lstm"]["values"]
results = []
order = sorted(
    approaches.items(),
    key=lambda kv: (-kv[1]["mean"], kv[0]),
)
second_key = order[1][0] if len(order) > 1 else None
for key, meta in approaches.items():
    if key == "hybrid_lstm":
        continue
    results.append(paired(hyb, meta["values"], f"hybrid_vs_{key}"))
if second_key:
    results.append(paired(hyb, approaches[second_key]["values"], f"hybrid_vs_runner_up_{second_key}"))

out = {
    "schema": "denoiseopt.stats_meta_approach_5k.v1",
    "source": "figures/multiseed_summary.json",
    "metric": "champion R_blend after matched 5k search per approach",
    "rank_by_mean": [k for k, _ in order],
    "results": results,
    "note": (
        "n=3 exact sign-flip two-sided test has minimum attainable p=0.25 when all three "
        "paired deltas share sign. Use for descriptive selection support only, not ANOVA superiority."
    ),
}
json.dump(out, open("figures/stats_meta_approach_5k.json", "w"), indent=2)
for r in results:
    print(
        r["comparison"],
        f"d={r['mean_diff_hybrid_minus_other']:+.4f}",
        f"CIboot={[round(x,4) for x in r['bootstrap_ci95_mean_diff']]}",
        f"p={r['exact_signflip_p_two_sided']:.4g}",
        f"wins={r['hybrid_wins']}/{r['n']}",
    )
