// =====================================================================================
// SAGE-River — common header (paste at the top of every script, or keep in a GEE repo
// and load with require()). Google Earth Engine Code Editor (JavaScript).
//
// Baseline = Freihardt & Frey (2023, NHESS 23:751-770, doi:10.5194/nhess-23-751-2023),
// released code Zenodo doi:10.5281/zenodo.7253121 (CC-BY-4.0). Functions below replicate
// that code: VV, ascending, angle 30-45 deg per-pixel mask, toNatural -> circle(r=7) mean
// -> toDB, temporal mean in dB, thresholds -13.2 dB (6-month) / -12.7 dB (1-month).
// =====================================================================================

// ---- Study area (written by python/select_aoi.py; see data/aoi/aoi.geojson) ----
var AOI = ee.Geometry.Rectangle(/*AOI_BBOX*/[89.62892, 25.61311, 89.89019, 25.72624]/*END_AOI_BBOX*/);
var REL_ORBIT = 114;            // ascending relative orbit over the AOI (verified in inventory)

// ---- Temporal design: validation monsoon 2024, test monsoon 2025 ----
var YEARS = {
  2024: {pre: ['2023-11-01', '2024-05-01'], post: ['2024-11-01', '2025-02-01'],
         s2pre: ['2024-02-01', '2024-04-01'], s2post: ['2025-02-01', '2025-04-01']},
  2025: {pre: ['2024-11-01', '2025-05-01'], post: ['2025-11-01', '2026-02-01'],
         s2pre: ['2025-02-01', '2025-04-01'], s2post: ['2026-02-01', '2026-04-01']}
};
var T_6MO = -13.2, T_1MO = -12.7;  // published thresholds (paper Sect. 2.5; code l.1203/1208)

// ---- Freihardt & Frey helpers (code lines 7-15, 158-167, 210-243) ----
function toNatural(img) { return ee.Image(10.0).pow(img.select(0).divide(10.0)); }
function toDB(img) { return ee.Image(img).log10().multiply(10.0); }
var CIRCLE7 = ee.Kernel.circle({radius: 7, units: 'pixels', normalize: true});   // released code
var SQUARE7 = ee.Kernel.square({radius: 3, units: 'pixels', normalize: true});   // paper text "7x7 boxcar"
function filterCircle7(img) { return toDB(toNatural(img).convolve(CIRCLE7)).rename('VV')
                              .copyProperties(img, ['system:time_start']); }
function filterSquare7(img) { return toDB(toNatural(img).convolve(SQUARE7)).rename('VV')
                              .copyProperties(img, ['system:time_start']); }
function angleMask(img) {
  var a = img.select('angle');
  return img.updateMask(a.gt(30)).updateMask(a.lt(45));
}
function s1VVasc(region, start, end) {
  return ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(region)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('resolution_meters', 10))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    .filter(ee.Filter.eq('relativeOrbitNumber_start', REL_ORBIT))
    .filterDate(start, end)
    .map(angleMask)
    .select('VV');
}
// Mosaic GRD slices that belong to the same pass/day so each acquisition counts once.
function mosaicByDay(col) {
  var days = ee.List(col.aggregate_array('system:time_start'))
    .map(function (t) { return ee.Date(t).format('YYYY-MM-dd'); }).distinct();
  return ee.ImageCollection(days.map(function (d) {
    var d0 = ee.Date.parse('YYYY-MM-dd', d);
    return col.filterDate(d0, d0.advance(1, 'day')).mosaic()
      .set('system:time_start', d0.millis()).set('date', d);
  }));
}

// =====================================================================================
// 04 — Baseline erosion mapping (Freihardt & Frey 2023 released-code configuration)
// pre composite  : temporal mean of filtered VV-ASC images, Nov(Y-1)-Apr(Y)  -> > T_6MO = vegetation
// post composite : temporal mean of the first k filtered images after 1 Nov(Y) -> < T_post = sand/water
// erosion        : pre > T_pre AND post < T_post   (code lines 1222-1226)
// =====================================================================================
var YEAR = 2025;          // 2024 = validation, 2025 = test
var K = 8;                // number of post-monsoon scenes (1, 2, 3, 6, 8)
var T_PRE = T_6MO;        // published; replace with the 2024-calibrated value from selected_parameters_*.json
var T_POST = T_1MO;       // published short-window value; replace with calibrated T_post(k)

var Y = YEARS[YEAR];
var pre = mosaicByDay(s1VVasc(AOI, Y.pre[0], Y.pre[1])).map(filterCircle7).mean();
var postCol = mosaicByDay(s1VVasc(AOI, Y.post[0], Y.post[1])).sort('system:time_start');
print('post-monsoon pool dates', postCol.aggregate_array('date'));
var postK = ee.ImageCollection(postCol.toList(K)).map(filterCircle7);
var post = postK.mean();

var vegPre = pre.gt(T_PRE);
var sandPost = post.lt(T_POST);
var eroded = vegPre.and(sandPost).selfMask();

Map.centerObject(AOI, 12);
Map.addLayer(pre.clip(AOI), {min: -22, max: -4}, 'pre composite VV (dB)');
Map.addLayer(post.clip(AOI), {min: -22, max: -4}, 'post composite VV (dB), k=' + K);
Map.addLayer(eroded.clip(AOI), {palette: ['ff4d00']}, 'baseline erosion');
print('baseline eroded area (ha):', eroded.multiply(ee.Image.pixelArea()).divide(1e4)
  .reduceRegion({reducer: ee.Reducer.sum(), geometry: AOI, scale: 10, maxPixels: 1e10}));

Export.image.toDrive({image: eroded.unmask(0).toByte().clip(AOI), description: 'baseline_erosion_' + YEAR + '_k' + K,
  region: AOI, scale: 10, crs: 'EPSG:32645', maxPixels: 1e10});
