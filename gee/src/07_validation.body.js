// =====================================================================================
// 07 — Validation in GEE (cross-check of python/metrics.py): confusion counts of an erosion
// map against the Sentinel-2 reference inside an evaluation polygon.
// The definitive metrics are computed in Python on the exported 10 m arrays (same grid);
// this script lets judges/team reproduce counts interactively.
// =====================================================================================
var YEAR = 2025, K = 8;
var Y = YEARS[YEAR];
var pre = mosaicByDay(s1VVasc(AOI, Y.pre[0], Y.pre[1])).map(filterCircle7).mean();
var post = ee.ImageCollection(mosaicByDay(s1VVasc(AOI, Y.post[0], Y.post[1])).sort('system:time_start').toList(K))
  .map(filterCircle7).mean();
var pred = pre.gt(T_6MO).and(post.lt(T_1MO));
function s2(start, end) {
  var cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(AOI).filterDate(start, end)
    .linkCollection(cs, ['cs_cdf']).map(function (i) { return i.updateMask(i.select('cs_cdf').gte(0.6)).divide(10000); }).median();
}
var a = s2(Y.s2pre[0], Y.s2pre[1]), b = s2(Y.s2post[0], Y.s2post[1]);
var vegA = a.normalizedDifference(['B8', 'B4']).gte(0.30).and(a.normalizedDifference(['B3', 'B11']).lt(0));
var lowB = b.normalizedDifference(['B3', 'B11']).gte(0).or(b.normalizedDifference(['B8', 'B4']).lt(0.20));
var ref = vegA.and(lowB);
var cm = pred.multiply(2).add(ref).rename('c');   // 0 TN, 1 FN, 2 FP, 3 TP
print('confusion histogram (0 TN, 1 FN, 2 FP, 3 TP)',
  cm.reduceRegion({reducer: ee.Reducer.frequencyHistogram(), geometry: AOI, scale: 10, maxPixels: 1e10}));
