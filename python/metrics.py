"""Evaluation metrics for (possibly abstaining) binary erosion maps against a reference.

Conventions
-----------
pred : int8 array, 1 = erosion, 0 = non-erosion, -1 = UNCERTAIN (abstained); any other value / NaN = no data
ref  : int8 array, 1 = reference erosion, 0 = reference non-erosion, -1 = reference uncertain (excluded)
eval_mask : bool array, pixels inside the evaluation domain (outer-bank corridor, valid data)

Pixel area for 10 m pixels = 100 m^2 = 0.01 ha.

Metrics on DECIDED pixels (pred in {0,1}) follow standard definitions. Abstentions are never silently
dropped: coverage, uncertain fraction and the reference-erosion area that fell into abstention are reported,
plus an "all-pixel" recall where abstained reference-erosion counts as missed.
"""
import numpy as np

PIXEL_HA = 0.01


def evaluate(pred, ref, eval_mask, pixel_ha=PIXEL_HA):
    m = eval_mask & np.isin(ref, (0, 1)) & np.isin(pred, (-1, 0, 1))
    p = pred[m]
    r = ref[m]
    n_eval = int(m.sum())
    decided = p >= 0
    tp = int(np.sum((p == 1) & (r == 1)))
    fp = int(np.sum((p == 1) & (r == 0)))
    fn = int(np.sum((p == 0) & (r == 1)))
    tn = int(np.sum((p == 0) & (r == 0)))
    abst_pos = int(np.sum((p == -1) & (r == 1)))
    abst_neg = int(np.sum((p == -1) & (r == 0)))
    n_dec = int(decided.sum())
    prec = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    rec = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    f1 = 2 * prec * rec / (prec + rec) if (tp + fp) > 0 and (tp + fn) > 0 and (prec + rec) > 0 else np.nan
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else np.nan
    ref_pos = tp + fn + abst_pos
    rec_all = tp / ref_pos if ref_pos > 0 else np.nan  # abstained reference erosion counted as missed
    return {
        "n_eval_px": n_eval,
        "n_decided_px": n_dec,
        "coverage": n_dec / n_eval if n_eval else np.nan,
        "uncertain_pct": 100.0 * (n_eval - n_dec) / n_eval if n_eval else np.nan,
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "abstained_ref_erosion_px": abst_pos, "abstained_ref_nonerosion_px": abst_neg,
        "precision": prec, "recall": rec, "f1": f1, "iou": iou,
        "recall_all_pixels": rec_all,
        "false_erosion_ha": fp * pixel_ha,
        "missed_erosion_ha": fn * pixel_ha,
        "abstained_erosion_ha": abst_pos * pixel_ha,
        "predicted_erosion_ha": (tp + fp) * pixel_ha,
        "reference_erosion_ha": ref_pos * pixel_ha,
    }


def _selftest():
    ref = np.array([1, 1, 1, 0, 0, 0, 0, -1], dtype=np.int8)
    pred = np.array([1, 0, -1, 1, 0, 0, -1, 1], dtype=np.int8)
    mask = np.ones_like(ref, dtype=bool)
    r = evaluate(pred, ref, mask)
    assert r["n_eval_px"] == 7 and r["n_decided_px"] == 5
    assert (r["TP"], r["FP"], r["FN"], r["TN"]) == (1, 1, 1, 2)
    assert abs(r["precision"] - 0.5) < 1e-9 and abs(r["recall"] - 0.5) < 1e-9
    assert abs(r["iou"] - 1 / 3) < 1e-9 and abs(r["recall_all_pixels"] - 1 / 3) < 1e-9
    assert abs(r["coverage"] - 5 / 7) < 1e-9
    print("metrics self-test passed")


if __name__ == "__main__":
    _selftest()
