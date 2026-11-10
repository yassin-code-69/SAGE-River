"""Print and save a compact digest of the real results (used to write poster/findings.json by hand).

Usage: python results_digest.py --source pc  -> outputs/reports/results_digest_<tag>.md
"""
import argparse
import json

import pandas as pd

import config as C


def main(tag):
    A = pd.read_csv(C.TABLES / f"experiment_A_summary_{tag}.csv")
    B = pd.read_csv(C.TABLES / f"experiment_B_chronological_{tag}.csv")
    sel = json.loads((C.TABLES / f"selected_parameters_{tag}.json").read_text())
    cal = pd.read_csv(C.TABLES / f"calibration_thresholds_2024_{tag}.csv")
    L = [f"# Results digest ({tag})", "", "## Frozen parameters (2024)", "```", json.dumps(sel, indent=1), "```", "",
         "## Calibration table", cal.to_markdown(index=False), ""]
    cols = ["method", "k", "n_subsets", "precision_mean", "recall_mean", "f1_mean", "f1_sd", "f1_min", "f1_max", "iou_mean",
            "coverage_mean", "false_erosion_ha_mean", "missed_erosion_ha_mean", "abstained_erosion_ha_mean", "recall_all_pixels_mean",
            "reference_erosion_ha"]
    for y in (2024, 2025):
        d = A[A.year == y][cols].sort_values(["k", "method"])
        L += [f"## Experiment A — {y} ({'validation, in-sample' if y == 2024 else 'TEST, frozen'})", d.round(3).to_markdown(index=False), ""]
        base = d[d.method == "BASE_calibrated"].set_index("k")
        rows = []
        for m in d.method.unique():
            if m == "BASE_calibrated":
                continue
            dm = d[d.method == m].set_index("k")
            for k in dm.index:
                if k in base.index:
                    rows.append({"method": m, "k": k, "dP": dm.precision_mean[k] - base.precision_mean[k],
                                 "dR": dm.recall_mean[k] - base.recall_mean[k], "dF1": dm.f1_mean[k] - base.f1_mean[k],
                                 "dIoU": dm.iou_mean[k] - base.iou_mean[k], "dFalse_ha": dm.false_erosion_ha_mean[k] - base.false_erosion_ha_mean[k],
                                 "dMissed_ha": dm.missed_erosion_ha_mean[k] - base.missed_erosion_ha_mean[k], "coverage": dm.coverage_mean[k]})
        L += [f"### Difference vs BASE_calibrated ({y})", pd.DataFrame(rows).round(3).to_markdown(index=False), ""]
    bcols = ["year", "reference", "map_available_date", "method", "k", "precision", "recall", "f1", "iou", "coverage",
             "false_erosion_ha", "missed_erosion_ha", "abstained_erosion_ha", "reference_erosion_ha"]
    L += ["## Experiment B — chronological", B[bcols].round(3).to_markdown(index=False)]
    out = C.REPORTS / f"results_digest_{tag}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pc")
    main(ap.parse_args().tag)
