// =====================================================================================
// 05 — Independent Sentinel-2 reference (COPERNICUS/S2_SR_HARMONIZED + Cloud Score+)
// Optical sensor reference, NOT field ground truth. Mirrors python/reference_validation.py:
//   VEG: NDVI >= 0.30 ; WATER: MNDWI >= 0 ; SAND: NDVI < 0.20 & MNDWI < 0 ; else ambiguous
//   reference erosion = VEG(Feb-Mar Y) AND WATER|SAND(Feb-Mar Y+1)
// (channel-connectivity and outer-bank strip are applied in Python on the exported layers)
// =====================================================================================
var YEAR = 2025;
var Y = YEARS[YEAR];
var CS_THRESHOLD = 0.60;
function s2Composite(start, end) {
  var cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');
  var col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(AOI).filterDate(start, end)
    .linkCollection(cs, ['cs_cdf'])
    .map(function (img) {
      var s = img.select(['B2', 'B3', 'B4', 'B8', 'B11']).divide(10000);
      var ndvi = s.normalizedDifference(['B8', 'B4']).rename('ndvi');
      var mndwi = s.normalizedDifference(['B3', 'B11']).rename('mndwi');
      return s.addBands([ndvi, mndwi]).updateMask(img.select('cs_cdf').gte(CS_THRESHOLD));
    });
  print('S2 images ' + start + '..' + end, col.size());
  return col.median().addBands(col.select('ndvi').count().rename('nobs'));
}
function classify(c) {
  var water = c.select('mndwi').gte(0);
  var veg = c.select('ndvi').gte(0.30).and(water.not());
  var sand = c.select('ndvi').lt(0.20).and(water.not());
  return ee.Image(3).where(sand, 2).where(water, 1).where(veg, 0).where(c.select('nobs').lt(3), 3).rename('cls');
}
var pre = s2Composite(Y.s2pre[0], Y.s2pre[1]);
var post = s2Composite(Y.s2post[0], Y.s2post[1]);
var cpre = classify(pre), cpost = classify(post);
var refErosion = cpre.eq(0).and(cpost.eq(1).or(cpost.eq(2)));

Map.centerObject(AOI, 12);
Map.addLayer(pre.clip(AOI), {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.25}, 'S2 pre (Feb-Mar ' + YEAR + ')');
Map.addLayer(post.clip(AOI), {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.25}, 'S2 post (Feb-Mar ' + (YEAR + 1) + ')');
Map.addLayer(refErosion.selfMask().clip(AOI), {palette: ['00e5ff']}, 'reference erosion candidates');
Export.image.toDrive({image: cpre.addBands(cpost.rename('cls_post')).toByte().clip(AOI),
  description: 's2_reference_classes_' + YEAR, region: AOI, scale: 10, crs: 'EPSG:32645', maxPixels: 1e10});
