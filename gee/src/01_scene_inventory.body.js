// =====================================================================================
// 01 — Sentinel-1 scene inventory over the AOI (2014-10 .. 2026-11), all orbits.
// Prints counts and a chart; exports a CSV of every GRD product to Google Drive.
// =====================================================================================
var all = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(AOI).filterDate('2014-10-01', '2026-11-11')
  .filter(ee.Filter.eq('instrumentMode', 'IW'));

var table = all.map(function (img) {
  return ee.Feature(null, {
    product_id: img.get('system:index'),
    date: ee.Date(img.get('system:time_start')).format('YYYY-MM-dd'),
    time_utc: ee.Date(img.get('system:time_start')).format('YYYY-MM-dd HH:mm:ss'),
    platform: img.get('platform_number'),
    pass: img.get('orbitProperties_pass'),
    rel_orbit: img.get('relativeOrbitNumber_start'),
    pols: ee.List(img.get('transmitterReceiverPolarisation')).join('+'),
    resolution_m: img.get('resolution_meters')
  });
});
print('GRD products over AOI:', all.size());
print('Platforms:', all.aggregate_histogram('platform_number'));
print('Relative orbits:', all.aggregate_histogram('relativeOrbitNumber_start'));
print('Passes:', all.aggregate_histogram('orbitProperties_pass'));

// acquisitions per year for the experiment orbit
var years = ee.List.sequence(2014, 2026);
var perYear = ee.FeatureCollection(years.map(function (y) {
  var c = all.filter(ee.Filter.calendarRange(y, y, 'year'));
  return ee.Feature(null, {
    year: y,
    R114_ASC: c.filter(ee.Filter.eq('relativeOrbitNumber_start', 114)).aggregate_count_distinct('system:time_start'),
    R150_DSC: c.filter(ee.Filter.eq('relativeOrbitNumber_start', 150)).aggregate_count_distinct('system:time_start')
  });
}));
print(ui.Chart.feature.byFeature(perYear, 'year', ['R114_ASC', 'R150_DSC'])
  .setChartType('ColumnChart').setOptions({title: 'Sentinel-1 IW products per year over AOI'}));

Export.table.toDrive({collection: table, description: 'sage_river_s1_inventory', fileFormat: 'CSV'});
