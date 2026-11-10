// =====================================================================================
// 06 — SAGE-River decision rules (A = m-of-k agreement, G = confidence gating)
// Output classes: 1 erosion, 0 non-erosion, 2 UNCERTAIN (abstained). Parameters must be the
// values frozen on the 2024 validation year (outputs/tables/selected_parameters_*.json).
// Three-valued logic: erosion = VEG_pre AND SAND_post; decided only when the result does not
// depend on a value inside the +/- DELTA band.
// =====================================================================================
var YEAR = 2025, K = 3, M = 2, DELTA = 1.0;
var T_PRE = T_6MO, T_SCENE = T_1MO;     // replace with calibrated values

var Y = YEARS[YEAR];
var pre = mosaicByDay(s1VVasc(AOI, Y.pre[0], Y.pre[1])).map(filterCircle7).mean();
var postK = ee.ImageCollection(mosaicByDay(s1VVasc(AOI, Y.post[0], Y.post[1]))
  .sort('system:time_start').toList(K)).map(filterCircle7);

// per-scene votes
var nSand = postK.map(function (i) { return i.lt(T_SCENE - DELTA); }).sum();
var nNot = postK.map(function (i) { return i.gt(T_SCENE + DELTA); }).sum();
var nUnsure = ee.Image(K).subtract(nSand).subtract(nNot);
var postTrue = nSand.gte(M);
var postFalse = nSand.add(nUnsure).lt(M);
var preTrue = pre.gt(T_PRE + DELTA);
var preFalse = pre.lt(T_PRE - DELTA);

var erosion = preTrue.and(postTrue);
var nonErosion = preFalse.or(postFalse);
var out = ee.Image(2).where(nonErosion, 0).where(erosion, 1).rename('sage');

Map.centerObject(AOI, 12);
Map.addLayer(out.clip(AOI), {min: 0, max: 2, palette: ['ffffff', 'ff4d00', '9e9e9e']}, 'SAGE-River (white non / orange erosion / grey uncertain)');
Export.image.toDrive({image: out.toByte().clip(AOI), description: 'sage_' + YEAR + '_k' + K + '_m' + M + '_d' + DELTA,
  region: AOI, scale: 10, crs: 'EPSG:32645', maxPixels: 1e10});
