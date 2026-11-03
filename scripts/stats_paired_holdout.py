"""Paired statistics for the five-seed holdout and 20-board multifamily benchmark.
Addresses aiXiv review (v2.0) weakness 4: CIs, paired tests, effect sizes.
Input: figures/multiseed_summary.json. Output: figures/stats_paired_holdout.json
"""
import json, itertools, math, random, statistics as st
d = json.load(open("figures/multiseed_summary.json"))
ps = d["holdout"]["holdout"]["per_seed"]
def paired(a, b, name, B=20000, seed=0):
    diff = [x - y for x, y in zip(a, b)]; n = len(diff)
    m, s = st.mean(diff), st.stdev(diff)
    # exact sign-flip permutation test (two-sided)
    obs = abs(sum(diff)); cnt = tot = 0
    for signs in itertools.product([1, -1], repeat=n):
        tot += 1; cnt += abs(sum(sg * x for sg, x in zip(signs, diff))) >= obs - 1e-15
    rng = random.Random(seed)
    boots = sorted(st.mean(rng.choices(diff, k=n)) for _ in range(B))
    dz = m / s if s else float("inf")
    hedges = dz * (1 - 3 / (4 * (n - 1) - 1))
    tcrit = {4: 2.776, 19: 2.093}.get(n - 1)
    out = dict(comparison=name, n=n, mean_diff=m, sd_diff=s,
               t_ci95=[m - tcrit * s / math.sqrt(n), m + tcrit * s / math.sqrt(n)] if tcrit else None,
               bootstrap_ci95=[boots[int(.025 * B)], boots[int(.975 * B)]],
               exact_signflip_p=cnt / tot, cohen_dz=dz, hedges_gz=hedges,
               wins_a=sum(x > 0 for x in diff))
    return out
res = {"schema": "denoiseopt.stats_paired_holdout.v1", "source": "figures/multiseed_summary.json",
       "results": [paired(ps["ours"], ps["n2n"], "hybrid_vs_n2n_holdout_5seed"),
                   paired(ps["ours"], ps["dual_cosine"], "hybrid_vs_dualcosine_holdout_5seed")]}
mf = d["holdout"]["multifamily"]
deltas = mf["board_mean_deltas"]
res["results"].append(paired(deltas, [0.0] * len(deltas), "hybrid_minus_n2n_multifamily_20boards"))
res["note"] = ("n=5 sign-flip test has minimum attainable p=0.0625; n=20 permutation is exact over 2^20 flips. "
               "Exploratory, not a powered multi-study claim.")
json.dump(res, open("figures/stats_paired_holdout.json", "w"), indent=2)
for r in res["results"]:
    print(r["comparison"], f"d={r['mean_diff']:+.4f} CI95boot={[round(x,4) for x in r['bootstrap_ci95']]} p={r['exact_signflip_p']:.4g} gz={r['hedges_gz']:.2f} wins={r['wins_a']}/{r['n']}")
