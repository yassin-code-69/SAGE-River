"""Evaluate the pre-registered SAGE-River v2 success criteria (docs/sage_river_v2_design.md §8) for every evaluation.

(a) at a 20 % review budget, prioritized review recovers more reference erosion than the random-review mean AND lies
    outside (above) the 5-95 % random band;
(b) HIGH-CONFIDENCE false erosion is not higher than v1's (A+G) false erosion.
Also reports v2 vs random review of v1 UNCERTAIN at the same effort, and the no-review full-area F1 vs the tuned baseline.
Output: outputs/tables/v2_preregistered_criteria.csv
"""
import pandas as pd

import config as C

EVALS = [
    ("Kurigram 2025", "EXPLORATORY", C.ROOT / "outputs" / "tables", "gee", 2025),
    ("Sirajganj 2025 (local calibration)", "INDEPENDENT (pre-registered primary)", C.ROOT / "outputs" / "reaches" / "sirajganj" / "tables", "gee", 2025),
    ("Sirajganj 2024 (Kurigram parameters)", "INDEPENDENT TRANSFER (addendum)", C.ROOT / "outputs" / "reaches" / "sirajganj" / "tables", "gee_transferK", 2024),
    ("Sirajganj 2025 (Kurigram parameters)", "INDEPENDENT TRANSFER (addendum)", C.ROOT / "outputs" / "reaches" / "sirajganj" / "tables", "gee_transferK", 2025),
]


def main():
    rows = []
    for name, role, t, tag, year in EVALS:
        s = pd.read_csv(t / f"v2_review_summary_{tag}.csv")
        A = pd.read_csv(t / f"experiment_A_summary_{tag}.csv")
        for k in (2, 3, 6, 8):
            d = s[(s.year == year) & (s.k == k) & (s.budget_frac == 0.2)].set_index("strategy")
            d0 = s[(s.year == year) & (s.k == k) & (s.budget_frac == 0.0)].set_index("strategy")
            a = A[(A.year == year) & (A.k == k)].set_index("method")
            if d.empty or "AG_agree+gate" not in a.index:
                continue
            pri, rmean, r95 = d.loc["v2_prioritized", "recovered_ha"], d.loc["v2_random_mean", "recovered_ha"], d.loc["v2_random_p95", "recovered_ha"]
            hc_false = d.loc["v2_prioritized", "hc_false_ha"]
            v1_false = a.loc["AG_agree+gate", "false_erosion_ha_mean"]
            rows.append({"evaluation": name, "role": role, "year": year, "k": k,
                         "reference_erosion_ha": d.loc["v2_prioritized", "reference_erosion_ha"],
                         "erosion_in_REVIEW_ha": d.loc["v2_prioritized", "review_erosion_ha"],
                         "REVIEW_area_ha": d.loc["v2_prioritized", "review_area_ha"],
                         "effort_20pct_ha": d.loc["v2_prioritized", "review_effort_ha"],
                         "recovered_prioritized_ha": pri, "recovered_random_mean_ha": rmean, "random_p95_ha": r95,
                         "recovered_v1_uncertain_random_ha": d.loc["v1_uncertain_random_mean", "recovered_ha"],
                         "crit_a_met": bool(pri > rmean and pri > r95),
                         "hc_false_ha": hc_false, "v1_false_ha": v1_false, "crit_b_met": bool(hc_false <= v1_false + 1e-9),
                         "f1_v2_no_review": d0.loc["v2_prioritized", "f1_full_area"],
                         "f1_v2_20pct_prioritized": d.loc["v2_prioritized", "f1_full_area"],
                         "f1_v2_20pct_random": d.loc["v2_random_mean", "f1_full_area"],
                         "f1_v1_uncertain_as_nonerosion": a.loc["AG_agree+gate", "f1_abst_nonero_mean"],
                         "f1_tuned_baseline": a.loc["BASE_F1tuned", "f1_mean"],
                         "f1_published_baseline": a.loc["BASE_published", "f1_mean"]})
    df = pd.DataFrame(rows)
    df["both_met"] = df.crit_a_met & df.crit_b_met
    df.to_csv(C.ROOT / "outputs" / "tables" / "v2_preregistered_criteria.csv", index=False)
    pd.set_option("display.width", 250)
    print(df[["evaluation", "k", "recovered_prioritized_ha", "recovered_random_mean_ha", "random_p95_ha", "recovered_v1_uncertain_random_ha",
              "crit_a_met", "hc_false_ha", "v1_false_ha", "crit_b_met", "f1_v2_no_review", "f1_v2_20pct_prioritized", "f1_tuned_baseline"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
