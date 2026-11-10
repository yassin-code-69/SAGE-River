// =====================================================================================
// 03 — SAR preprocessing check: paper-described vs released-code speckle filter.
// Shows one post-monsoon scene with (a) no filter, (b) square 7x7 boxcar (paper text),
// (c) circle radius 7 (released code), and prints the incidence-angle range over the AOI.
// =====================================================================================
var Y = YEARS[2025];
var col = mosaicByDay(s1VVasc(AOI, Y.post[0], Y.post[1])).sort('system:time_start');
var first = ee.Image(col.first());
print('first post-monsoon scene', first.get('date'));
var raw = ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(AOI)
  .filterDate(Y.post[0], Y.post[1]).filter(ee.Filter.eq('relativeOrbitNumber_start', REL_ORBIT)).first();
print('incidence angle over AOI (deg)', raw.select('angle').reduceRegion({reducer: ee.Reducer.minMax(), geometry: AOI, scale: 100}));
Map.centerObject(AOI, 12);
Map.addLayer(first.clip(AOI), {min: -22, max: -4}, 'VV unfiltered');
Map.addLayer(filterSquare7(first).clip(AOI), {min: -22, max: -4}, 'VV square 7x7 (paper text)');
Map.addLayer(filterCircle7(first).clip(AOI), {min: -22, max: -4}, 'VV circle r=7 (released code)');
