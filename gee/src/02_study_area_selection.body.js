// =====================================================================================
// 02 — Study-area selection aid: Sentinel-2 Feb-Mar 2025 vs Feb-Mar 2026 true colour and
// NDVI-loss layer over the candidate Jamuna boxes (Kurigram, Bogura-Gaibandha, Sirajganj).
// =====================================================================================
var boxes = {
  kurigram: ee.Geometry.Rectangle([89.55, 25.30, 89.95, 25.85]),
  bogura_gaibandha: ee.Geometry.Rectangle([89.50, 24.75, 89.85, 25.30]),
  sirajganj: ee.Geometry.Rectangle([89.55, 24.10, 89.95, 24.75])
};
function comp(start, end, region) {
  var cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(start, end)
    .linkCollection(cs, ['cs_cdf'])
    .map(function (i) { return i.updateMask(i.select('cs_cdf').gte(0.6)).divide(10000); }).median();
}
Object.keys(boxes).forEach(function (k) {
  var r = boxes[k];
  var a = comp('2025-02-01', '2025-04-01', r), b = comp('2026-02-01', '2026-04-01', r);
  var loss = a.normalizedDifference(['B8', 'B4']).gt(0.35).and(b.normalizedDifference(['B8', 'B4']).lt(0.15));
  Map.addLayer(a.clip(r), {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.25}, k + ' S2 Feb-Mar 2025', false);
  Map.addLayer(b.clip(r), {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.25}, k + ' S2 Feb-Mar 2026', false);
  Map.addLayer(loss.selfMask().clip(r), {palette: ['ff0000']}, k + ' NDVI loss 2025 monsoon', true);
});
Map.addLayer(AOI, {color: 'yellow'}, 'selected AOI');
Map.centerObject(AOI, 11);
