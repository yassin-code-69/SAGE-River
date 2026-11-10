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
