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
