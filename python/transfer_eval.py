"""Transfer evaluation (pre-registered addendum, docs/sage_river_v2_design.md §9).

All parameters frozen on KURIGRAM 2024 (v1: thresholds, m, delta; v2: D_review, ranking model) are applied unchanged
to another reach (SAGE_REACH, e.g. sirajganj) for 2024 and 2025. No data of the target reach influence any choice.
Usage:  SAGE_REACH=sirajganj python transfer_eval.py
Outputs (target reach tables): experiment_A_summary_gee_transferK.csv, experiment_B_chronological_gee_transferK.csv,
         v2_review_summary_gee_transferK.csv, v2_review_simulation_gee_transferK.csv, v2_hc_only_metrics_gee_transferK.csv
"""
import itertools
import json

import numpy as np
import pandas as pd

import config as C
import experiment_runner as E
import sage_v2 as V
from metrics import evaluate

TAG = "gee"
SRC_TABLES = C.ROOT / "outputs" / "tables"  # Kurigram (development reach)


def main():
    assert C.REACH != "kurigram", "transfer evaluation must target another reach"
    sel = json.loads((SRC_TABLES / f"selected_parameters_{TAG}.json").read_text())
    cal = json.loads((SRC_TABLES / f"v2_calibration_{TAG}.json").read_text())
    T, params = sel["thresholds"], sel["params_by_k"]
    rng = np.random.default_rng(C.RANDOM_SEED)
    allA, allB, sim_rows, hc_rows = [], [], [], []
    for year in (2024, 2025):
        Dfull = E.load(TAG, year)
        D = E.domain_view(Dfull)
        allA.append(E.experiment_A(D, T, params, year, TAG + "_transferK"))
        allB.append(E.experiment_B(D, T, params, year, TAG + "_transferK"))
        pre, ref, dom = Dfull["pre_comp"], Dfull["ref"], Dfull["domain"]
        geom = V.sar_geometry(pre, T["T_pre"])
        K = Dfull["post"].shape[0]
        sets = [("A", c) for k in C.K_LIST if k <= K for c in itertools.combinations(range(K), k)] + \
               [("B", tuple(range(k))) for k in C.K_CHRONO if k <= K]
        for exp, comb in sets:
            cls, ev = V.v2_classes(pre, Dfull["post"][list(comb)], sel, geom, dom, cal["D_review_m"])
            meta = {"year": year, "tag": TAG + "_transferK", "experiment": exp, "k": len(comb), "subset": "-".join(map(str, comb)),
                    "dates": ";".join(Dfull["dates"][i] for i in comb), "role": "INDEPENDENT TRANSFER (Kurigram-2024 parameters)"}
            for r in V.simulate(cls, ev, ref, dom, cal, rng):
                r.update(meta); sim_rows.append(r)
            e = evaluate(V.v2_pred_map(cls), ref, dom)
            e.update(meta); e.update({"method": "SAGE_v2_HC_only"})
            hc_rows.append(e)
    A = pd.concat(allA); B = pd.concat(allB)
    A.to_csv(C.TABLES / f"experiment_A_all_subsets_{TAG}_transferK.csv", index=False)
    E.summarise(A).to_csv(C.TABLES / f"experiment_A_summary_{TAG}_transferK.csv", index=False)
    E.add_derived(B).to_csv(C.TABLES / f"experiment_B_chronological_{TAG}_transferK.csv", index=False)
    sim = pd.DataFrame(sim_rows)
    sim.to_csv(C.TABLES / f"v2_review_simulation_{TAG}_transferK.csv", index=False)
    pd.DataFrame(hc_rows).to_csv(C.TABLES / f"v2_hc_only_metrics_{TAG}_transferK.csv", index=False)
    summ = sim[sim.experiment == "A"].groupby(["year", "role", "k", "budget_frac", "strategy"]).agg(
        n_subsets=("recovered_ha", "size"), review_effort_ha=("review_effort_ha", "mean"), recovered_ha=("recovered_ha", "mean"),
        missed_ha=("missed_ha", "mean"), hc_false_ha=("hc_false_ha", "mean"), f1_full_area=("f1_full_area", "mean"),
        recall_full_area=("recall_full_area", "mean"), coverage_auto=("coverage_auto", "mean"),
        review_area_ha=("review_area_ha", "mean"), review_erosion_ha=("review_erosion_ha", "mean"),
        stable_erosion_ha=("stable_erosion_ha", "mean"), reference_erosion_ha=("reference_erosion_ha", "first")).reset_index()
    summ.to_csv(C.TABLES / f"v2_review_summary_{TAG}_transferK.csv", index=False)
    print("transfer evaluation written for", C.REACH)


if __name__ == "__main__":
    main()
