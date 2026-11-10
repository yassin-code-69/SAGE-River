"""Erosion decision rules: published baseline and SAGE-River components (A = agreement, G = confidence gating).

Inputs (all in dB, speckle-filtered exactly like the baseline, NaN = no data):
  pre_comp : 2-D pre-monsoon composite (temporal mean of filtered dB scenes, F&F rule)
  post     : 3-D stack (k, H, W) of filtered post-monsoon scenes for the chosen subset
Thresholds:
  T_pre, T_post : vegetation vs sand/water thresholds (dB). Pixel is "vegetation" if value > T.
Outputs: int8 map, 1 erosion / 0 non-erosion / -1 uncertain / -2 no data.

Three-valued (Kleene) logic is used for gating so that a pixel is only abstained when the decision
really depends on an uncertain input:
  erosion  = VEG_pre AND SAND_post
  decided non-erosion if either term is confidently FALSE; decided erosion if both confidently TRUE.
"""
import numpy as np

NODATA = -2


def _tri(values, T, delta, below_is_true):
    """Return +1 (confidently true), 0 (confidently false), -1 (uncertain) for the predicate value<T (or >T)."""
    out = np.full(values.shape, -1, dtype=np.int8)
    if below_is_true:
        out[values < T - delta] = 1
        out[values > T + delta] = 0
    else:
        out[values > T + delta] = 1
        out[values < T - delta] = 0
    if delta == 0:  # exact equality: treat as not-below / not-above (strict F&F inequalities)
        eq = values == T
        out[eq] = 0
    return out


def _kleene_and(a, b):
    out = np.full(a.shape, -1, dtype=np.int8)
    out[(a == 0) | (b == 0)] = 0
    out[(a == 1) & (b == 1)] = 1
    return out


def baseline(pre_comp, post, T_pre, T_post):
    """Freihardt & Frey rule: pre composite > T_pre AND mean(post dB) < T_post (no abstention)."""
    post_comp = np.nanmean(post, axis=0) if post.shape[0] > 1 else post[0]
    out = ((pre_comp > T_pre) & (post_comp < T_post)).astype(np.int8)
    out[np.isnan(pre_comp) | np.isnan(post_comp)] = NODATA
    return out


def gated(pre_comp, post, T_pre, T_post, delta):
    """Baseline composite rule with a +/- delta dB abstention band on both pre and post composites."""
    post_comp = np.nanmean(post, axis=0) if post.shape[0] > 1 else post[0]
    veg = _tri(pre_comp, T_pre, delta, below_is_true=False)
    sand = _tri(post_comp, T_post, delta, below_is_true=True)
    out = _kleene_and(veg, sand)
    out[np.isnan(pre_comp) | np.isnan(post_comp)] = NODATA
    return out


def agreement(pre_comp, post, T_pre, T_post, m, delta=0.0):
    """m-of-k temporal agreement on per-scene sand/water votes, optionally with a per-scene margin delta.

    Per scene: vote SAND if value < T_post - delta, NOT-SAND if value > T_post + delta, else UNSURE.
    Post term = TRUE if #SAND >= m; FALSE if #SAND + #UNSURE < m (m can no longer be reached); else UNCERTAIN.
    With delta = 0 there are no UNSURE votes, so the rule reduces to a plain m-of-k vote.
    A scene with no data at a pixel counts as UNSURE (conservative, never as a vote for erosion).
    """
    k = post.shape[0]
    if not 1 <= m <= k:
        raise ValueError("m must be in 1..k")
    sand = np.zeros(post.shape[1:], dtype=np.int16)
    notsand = np.zeros(post.shape[1:], dtype=np.int16)
    for s in range(k):
        v = post[s]
        sand += (v < T_post - delta)
        notsand += (v > T_post + delta) if delta > 0 else (v >= T_post)
    unsure = k - sand - notsand
    post_term = np.full(sand.shape, -1, dtype=np.int8)
    post_term[sand >= m] = 1
    post_term[(sand + unsure) < m] = 0
    veg = _tri(pre_comp, T_pre, delta, below_is_true=False)
    out = _kleene_and(veg, post_term)
    allnan = np.all(np.isnan(post), axis=0)
    out[np.isnan(pre_comp) | allnan] = NODATA
    if delta == 0:
        # without a margin nothing is uncertain except no-data scenes; keep -1 where a scene was missing
        pass
    return out


def majority_m(k):
    return k // 2 + 1


def _selftest():
    pre = np.array([[-10.0, -10.0, -16.0, -13.0]])
    post = np.array([[[-15.0, -11.0, -15.0, -15.0]],
                     [[-15.0, -15.0, -15.0, -15.0]],
                     [[-11.0, -11.0, -15.0, -15.0]]])
    b = baseline(pre, post, -13.2, -12.7)
    # means: -13.67, -12.33, -15, -15 ; pre veg: T,T,F,T(-13.0 > -13.2)
    assert b.tolist() == [[1, 0, 0, 1]], b
    a = agreement(pre, post, -13.2, -12.7, m=3)  # unanimous: only pixel 4 has 3/3 sand votes
    assert a.tolist() == [[0, 0, 0, 1]], a
    a2 = agreement(pre, post, -13.2, -12.7, m=2)
    assert a2.tolist() == [[1, 0, 0, 1]], a2
    g = gated(pre, post, -13.2, -12.7, delta=0.5)
    # pixel 2: post mean -12.33 lies inside [-13.2, -12.2] -> UNCERTAIN
    # pixel 4: pre -13.0 within 0.5 of -13.2 -> uncertain veg; post -15 confidently sand -> UNCERTAIN
    assert g.tolist() == [[1, -1, 0, -1]], g
    ag = agreement(pre, post, -13.2, -12.7, m=2, delta=0.5)
    # pixel 1: votes -15(S) -15(S) -11(N) -> 2 sand >= 2 -> sand; pre veg -> erosion
    assert ag.tolist() == [[1, 0, 0, -1]], ag
    print("sage_methods self-test passed")


if __name__ == "__main__":
    _selftest()
