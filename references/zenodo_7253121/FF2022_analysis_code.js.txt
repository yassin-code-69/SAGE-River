// This code is part of the paper 
// Freihardt & Frey (2022): Assessing riverbank erosion in Bangladesh using time series of Sentinel-1 radar imagery in the Google Earth Engine //


//////AUXILIARY FUNCTIONS///////////
//ref for following 3 fct: code from Singha et al (2019)
//Function to convert from dB
function toNatural(img) {
return ee.Image(10.0).pow(img.select(0).divide(10.0));
}

//Function to convert to dB
function toDB(img) {
return ee.Image(img).log10().multiply(10.0);
}

//Applying a Refined Lee Speckle filter as coded in the SNAP 3.0 S1TBX:
//source: https://github.com/senbox-org/s1tbx/blob/master/s1tbx-op-sar-processing/src/main/java/org/esa/s1tbx/sar/gpf/filtering/SpeckleFilters/RefinedLee.java
function RefinedLee(img) {
  // img must be in natural units, i.e. not in dB!
  // Set up 3x3 kernels

  // convert to natural.. do not apply function on dB!
  var myimg = toNatural(img);

  var weights3 = ee.List.repeat(ee.List.repeat(1,3),3);
  var kernel3 = ee.Kernel.fixed(3,3, weights3, 1, 1, false);

  var mean3 = myimg.reduceNeighborhood(ee.Reducer.mean(), kernel3);
  var variance3 = myimg.reduceNeighborhood(ee.Reducer.variance(), kernel3);

  // Use a sample of the 3x3 windows inside a 7x7 windows to determine gradients and directions
  var sample_weights = ee.List([[0,0,0,0,0,0,0], [0,1,0,1,0,1,0],[0,0,0,0,0,0,0], [0,1,0,1,0,1,0], [0,0,0,0,0,0,0], [0,1,0,1,0,1,0],[0,0,0,0,0,0,0]]);

  var sample_kernel = ee.Kernel.fixed(7,7, sample_weights, 3,3, false);

  // Calculate mean and variance for the sampled windows and store as 9 bands
  var sample_mean = mean3.neighborhoodToBands(sample_kernel);
  var sample_var = variance3.neighborhoodToBands(sample_kernel);

  // Determine the 4 gradients for the sampled windows
  var gradients = sample_mean.select(1).subtract(sample_mean.select(7)).abs();
  gradients = gradients.addBands(sample_mean.select(6).subtract(sample_mean.select(2)).abs());
  gradients = gradients.addBands(sample_mean.select(3).subtract(sample_mean.select(5)).abs());
  gradients = gradients.addBands(sample_mean.select(0).subtract(sample_mean.select(8)).abs());

  // And find the maximum gradient amongst gradient bands
  var max_gradient = gradients.reduce(ee.Reducer.max());

  // Create a mask for band pixels that are the maximum gradient
  var gradmask = gradients.eq(max_gradient);

  // duplicate gradmask bands: each gradient represents 2 directions
  gradmask = gradmask.addBands(gradmask);

  // Determine the 8 directions
  var directions = sample_mean.select(1).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(7))).multiply(1);
  directions = directions.addBands(sample_mean.select(6).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(2))).multiply(2));
  directions = directions.addBands(sample_mean.select(3).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(5))).multiply(3));
  directions = directions.addBands(sample_mean.select(0).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(8))).multiply(4));
  // The next 4 are the not() of the previous 4
  directions = directions.addBands(directions.select(0).not().multiply(5));
  directions = directions.addBands(directions.select(1).not().multiply(6));
  directions = directions.addBands(directions.select(2).not().multiply(7));
  directions = directions.addBands(directions.select(3).not().multiply(8));

  // Mask all values that are not 1-8
  directions = directions.updateMask(gradmask);

  // "collapse" the stack into a singe band image (due to masking, each pixel has just one value (1-8) in it's directional band, and is otherwise masked)
  directions = directions.reduce(ee.Reducer.sum());

  var sample_stats = sample_var.divide(sample_mean.multiply(sample_mean));

  // Calculate localNoiseVariance
  var sigmaV = sample_stats.toArray().arraySort().arraySlice(0,0,5).arrayReduce(ee.Reducer.mean(), [0]);

  // Set up the 7*7 kernels for directional statistics
  var rect_weights = ee.List.repeat(ee.List.repeat(0,7),3).cat(ee.List.repeat(ee.List.repeat(1,7),4));

  var diag_weights = ee.List([[1,0,0,0,0,0,0], [1,1,0,0,0,0,0], [1,1,1,0,0,0,0],
  [1,1,1,1,0,0,0], [1,1,1,1,1,0,0], [1,1,1,1,1,1,0], [1,1,1,1,1,1,1]]);

  var rect_kernel = ee.Kernel.fixed(7,7, rect_weights, 3, 3, false);
  var diag_kernel = ee.Kernel.fixed(7,7, diag_weights, 3, 3, false);

  // Create stacks for mean and variance using the original kernels. Mask with relevant direction.
  var dir_mean = myimg.reduceNeighborhood(ee.Reducer.mean(), rect_kernel).updateMask(directions.eq(1));
  var dir_var = myimg.reduceNeighborhood(ee.Reducer.variance(), rect_kernel).updateMask(directions.eq(1));

  dir_mean = dir_mean.addBands(myimg.reduceNeighborhood(ee.Reducer.mean(), diag_kernel).updateMask(directions.eq(2)));
  dir_var = dir_var.addBands(myimg.reduceNeighborhood(ee.Reducer.variance(), diag_kernel).updateMask(directions.eq(2)));

  // and add the bands for rotated kernels
  for (var i=1; i<4; i++) {
  dir_mean = dir_mean.addBands(myimg.reduceNeighborhood(ee.Reducer.mean(), rect_kernel.rotate(i)).updateMask(directions.eq(2*i+1)));
  dir_var = dir_var.addBands(myimg.reduceNeighborhood(ee.Reducer.variance(), rect_kernel.rotate(i)).updateMask(directions.eq(2*i+1)));
  dir_mean = dir_mean.addBands(myimg.reduceNeighborhood(ee.Reducer.mean(), diag_kernel.rotate(i)).updateMask(directions.eq(2*i+2)));
  dir_var = dir_var.addBands(myimg.reduceNeighborhood(ee.Reducer.variance(), diag_kernel.rotate(i)).updateMask(directions.eq(2*i+2)));
  }

  // "collapse" the stack into a single band image (due to masking, each pixel has just one value in it's directional band, and is otherwise masked)
  dir_mean = dir_mean.reduce(ee.Reducer.sum());
  dir_var = dir_var.reduce(ee.Reducer.sum());

  // A finally generate the filtered value
  var varX = dir_var.subtract(dir_mean.multiply(dir_mean).multiply(sigmaV)).divide(sigmaV.add(1.0));

  var b = varX.divide(dir_var);

  var result = dir_mean.add(b.multiply(myimg.subtract(dir_mean)));
  //return(result);
  return(img.select([]).addBands(ee.Image(toDB(result.arrayGet(0))).rename("VV")));
}

var bufferPoly = function(feature) {
  return feature.buffer(20);   // substitute in your value of Z here
};

// Smooth output image by filtering speckle (https://earth.esa.int/documents/653194/656796/Speckle_Filtering.pdf)
// Define boxcar filters of different sizes
var boxcar1by1 = ee.Kernel.circle({ //dummy filter for "unfiltered" mode below
  radius: 1,
  units: 'pixels',
  normalize: true
});

var meanFilter1by1 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar1by1);
  return toDB(image);
};

var boxcar3by3 = ee.Kernel.circle({
  radius: 3,
  units: 'pixels',
  normalize: true
});

var meanFilter3by3 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar3by3);
  return toDB(image);
};

var boxcar5by5 = ee.Kernel.circle({
  radius: 5,
  units: 'pixels',
  normalize: true
});

var meanFilter5by5 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar5by5);
  return toDB(image);
};

var boxcar7by7 = ee.Kernel.circle({
  radius: 7,
  units: 'pixels',
  normalize: true
});

var meanFilter7by7 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar7by7);
  return toDB(image);
};

var boxcar11by11= ee.Kernel.circle({
  radius: 11,
  units: 'pixels',
  normalize: true
});

var meanFilter11by11 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar11by11);
  return toDB(image);
};

var boxcar25by25 = ee.Kernel.circle({
  radius: 25,
  units: 'pixels',
  normalize: true
});

var meanFilter25by25 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar25by25);
  return toDB(image);
};

var boxcar50by50 = ee.Kernel.circle({
  radius: 50,
  units: 'pixels',
  normalize: true
});

var meanFilter50by50 = function(image){
  image = toNatural(image);
  image = image.convolve(boxcar50by50);
  return toDB(image);
};


//////////////MAIN PART//////////////////////

// Load Sentinel-1 C-band SAR Ground Range collection
var S1 = ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(assessment_site)
        .filter(ee.Filter.eq('instrumentMode', 'IW'))
        .filterMetadata('resolution_meters', 'equals', 10)
        ;
//print(S1, 'Complete S1 Collection')

// Create functions that will mask out the Sentinel-1 images beyond 30 to 45 degrees.
var maskGTAng30 = function(image){
  var angle = image.select(['angle'])
  var maskedAngle = angle.gt(30)
  return image.updateMask(maskedAngle);
};
var S1 = S1.map(maskGTAng30);

var maskLTAng45 = function(image){
  var angle = image.select(['angle'])
  var maskedAngle = angle.lt(45)
  return image.updateMask(maskedAngle);
};
var S1 = S1.map(maskLTAng45);

// Create image collections for different polarizations
var imgVV_VH = S1.filterMetadata('transmitterReceiverPolarisation', 'equals', ['VV', 'VH']);
var imgVV = S1.select('VV');
var imgVH = imgVV_VH.select('VH');

// Filter by pass type
//var imgVV_VH_ASC = imgVV_VH.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'));
var imgVV_ASC = imgVV.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'));
//var imgVH_ASC = imgVH.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'));

//var imgVV_VH_DESC = imgVV_VH.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'));
var imgVV_DESC = imgVV.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'));
//var imgVH_DESC = imgVH.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'));

//Load Sentinel-2 images for assessment of classification and erosion detection (code from https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2)

/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2clouds(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}

// Map the function over one month of data and take the median.
// Load Sentinel-2 TOA reflectance data.
var S2_0118 = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2018-01-01', '2018-02-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

var S2_1118 = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2018-11-01', '2018-12-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

var S2_0119 = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2019-01-01', '2019-02-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

var S2_1119 = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2019-11-01', '2019-12-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

var S2_0120 = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2020-01-01', '2020-02-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

//define visualization parameters
var rgbVis = {
  min: 0.0,
  max: 0.3,
  bands: ['B4', 'B3', 'B2'],
};

// Define feature collections for land cover types "water", "sand", "trees", "fields"
var river_regions = ee.FeatureCollection([
  ee.Feature(river1, {label: 'Site 1'}),
  ee.Feature(river2, {label: 'Site 2'}),
  ee.Feature(river3, {label: 'Site 3'}),
  ee.Feature(river4, {label: 'Site 4'}),
  ee.Feature(river5, {label: 'Site 5'}),
  ee.Feature(river6, {label: 'Site 6'}),
  ee.Feature(river7, {label: 'Site 7'}),
  ee.Feature(river8, {label: 'Site 8'}),
  ee.Feature(river9, {label: 'Site 9'}),
  ee.Feature(river10, {label: 'Site 10'})
]);

var sand_regions = ee.FeatureCollection([
  ee.Feature(sand1, {label: 'Sand 1'}),
  ee.Feature(sand2, {label: 'Sand 2'}),
  ee.Feature(sand3, {label: 'Sand 3'}),
  ee.Feature(sand4, {label: 'Sand 4'}),
  ee.Feature(sand5, {label: 'Sand 5'}),
  ee.Feature(sand6, {label: 'Sand 6'}),
  ee.Feature(sand7, {label: 'Sand 7'}),
  ee.Feature(sand8, {label: 'Sand 8'}),
  ee.Feature(sand9, {label: 'Sand 9'}),
  ee.Feature(sand10, {label: 'Sand 10'})
]);

var tree_regions = ee.FeatureCollection([
  ee.Feature(trees1, {label: 'Trees 1'}),
  ee.Feature(trees2, {label: 'Trees 2'}),
  ee.Feature(trees3, {label: 'Trees 3'}),
  ee.Feature(trees4, {label: 'Trees 4'}),
  ee.Feature(trees5, {label: 'Trees 5'}),
  ee.Feature(trees6, {label: 'Trees 6'}),
  ee.Feature(trees7, {label: 'Trees 7'}),
  ee.Feature(trees8, {label: 'Trees 8'}),
  ee.Feature(trees9, {label: 'Trees 9'}),
  ee.Feature(trees10, {label: 'Trees 10'})
]);

var field_regions = ee.FeatureCollection([
  ee.Feature(field1, {label: 'Field 1'}),
  ee.Feature(field2, {label: 'Field 2'}),
  ee.Feature(field3, {label: 'Field 3'}),
  ee.Feature(field4, {label: 'Field 4'}),
  ee.Feature(field5, {label: 'Field 5'}),
  ee.Feature(field6, {label: 'Field 6'}),
  ee.Feature(field7, {label: 'Field 7'}),
  ee.Feature(field8, {label: 'Field 8'}),
  ee.Feature(field9, {label: 'Field 9'}),
  ee.Feature(field10, {label: 'Field 10'})
]);

////////////////////
///// 1. Create monthly time series charts for illustration purposes - code adapted from Singha et al (2019)
////////////////////

//create number sequence for 12 months
var monList = ee.List.sequence(1,12,1);
var monList_2020 = ee.List.sequence(1,4,1);

//create functions that return the average of all images taken in a certain month
function monthlyComposite_2017(month) {
  var year = 2017
  var start = ee.Date.fromYMD(year,month,1)
  var end = start.advance(1,"month")
  var first = imgVV_ASC.filterDate(start,end).first()
  var S1 = imgVV_ASC.filterDate(start,end).mean().copyProperties(first, ['system:time_start'])
  return S1
}

function monthlyComposite_2018(month) {
  var year = 2018
  var start = ee.Date.fromYMD(year,month,1)
  var end = start.advance(1,"month")
  var first = imgVV_ASC.filterDate(start,end).first()
  var S1 = imgVV_ASC.filterDate(start,end).mean().copyProperties(first, ['system:time_start'])
  return S1
}

function monthlyComposite_2019(month) {
  var year = 2019
  var start = ee.Date.fromYMD(year,month,1)
  var end = start.advance(1,"month")
  var first = imgVV_ASC.filterDate(start,end).first()
  var S1 = imgVV_ASC.filterDate(start,end).mean().copyProperties(first, ['system:time_start'])
  return S1
}

function monthlyComposite_2020(month) {
  var year = 2020
  var start = ee.Date.fromYMD(year,month,1)
  var end = start.advance(1,"month")
  var first = imgVV_ASC.filterDate(start,end).first()
  var S1 = imgVV_ASC.filterDate(start,end).mean().copyProperties(first, ['system:time_start'])
  return S1
}

//calculate average images for all months from 2017 to 2020
var monthlyColl_2017 = ee.ImageCollection(monList.map(monthlyComposite_2017));
var monthlyColl_2018 = ee.ImageCollection(monList.map(monthlyComposite_2018));
var monthlyColl_2019 = ee.ImageCollection(monList.map(monthlyComposite_2019));
var monthlyColl_2020 = ee.ImageCollection(monList_2020.map(monthlyComposite_2020));

//merge all monthly images into one image collection
var monthlyColl_2018to20 = monthlyColl_2018.merge(monthlyColl_2019).merge(monthlyColl_2020);

// Define FeatureCollection of different land cover types
var different_regions = ee.FeatureCollection([
  ee.Feature(settlement1, {label: 'Settlement'}),
  ee.Feature(trees1, {label: 'Trees'}),
  ee.Feature(field1, {label: 'Field 1'}),
  ee.Feature(field_temporarily_flooded1, {label: 'Field 2 (seasonally flooded)'}),
  ee.Feature(eroded_2018N, {label: 'Field 3 (eroded in 2018)'}),
  ee.Feature(sand2, {label: 'Sand'}),
  ee.Feature(river1, {label: 'River'})
]);

// Select data for 2018 to 2020 and create time series charts.
var TimeSeries_different_regions_monthly = ui.Chart.image.seriesByRegion(
    monthlyColl_2018to20, different_regions, ee.Reducer.mean(), null, 10, null, 'label')
        .setChartType('LineChart')
        .setOptions({
          title: 'Mean monthly backscatter of different landcover types, 01-2018 to 04-2020',
          vAxis: {title: 'Backscatter coefficient [dB]', viewWindowMode:'explicit', viewWindow: {min: -30.5, max: 7.5}},
          lineWidth: 1,
          pointSize: 4,
          series: {
            0: {color: '000000'}, // settlement
            1: {color: 'ff4912'}, // trees
            2: {color: '12ff35'}, // field
            3: {color: 'fb12ff'}, // flooded field
            4: {color: '09632c'}, // eroded field
            5: {color: 'fcba03'}, // sand
            6: {color: '0000FF'}, // river
}});

// Print time-series charts at different locations/land cover types
//print(TimeSeries_different_regions_monthly);

////////////////////
///// 2. Analyze influence of sampling duration and filter size on recorded backscatter values for four land cover classes
////////////////////

//use dry season 2018-19; for 10 sites of water, sand, trees, respectively

//define different durations of the dry season 18-19 (starting Nov 1st)
var drySeason2018_19_2we = ee.Filter.date('2018-11-01', '2018-11-15');
var drySeason2018_19_1mo = ee.Filter.date('2018-11-01', '2018-12-01');
var drySeason2018_19_2mo = ee.Filter.date('2018-11-01', '2019-01-01');
var drySeason2018_19_3mo = ee.Filter.date('2018-11-01', '2019-02-01');
var drySeason2018_19_4mo = ee.Filter.date('2018-11-01', '2019-03-01');
var drySeason2018_19_5mo = ee.Filter.date('2018-11-01', '2019-04-01');
var drySeason2018_19_6mo = ee.Filter.date('2018-11-01', '2019-05-01');
var drySeason2018_19_7mo = ee.Filter.date('2018-11-01', '2019-06-01');

//filter for the respective images
var images_dry2018_19_2we = imgVV_ASC.filter(drySeason2018_19_2we).map(RefinedLee);
var images_dry2018_19_1mo = imgVV_ASC.filter(drySeason2018_19_1mo).map(RefinedLee);
var images_dry2018_19_2mo = imgVV_ASC.filter(drySeason2018_19_2mo).map(RefinedLee);
var images_dry2018_19_3mo = imgVV_ASC.filter(drySeason2018_19_3mo).map(RefinedLee);
var images_dry2018_19_4mo = imgVV_ASC.filter(drySeason2018_19_4mo).map(RefinedLee);
var images_dry2018_19_5mo = imgVV_ASC.filter(drySeason2018_19_5mo).map(RefinedLee);
var images_dry2018_19_6mo = imgVV_ASC.filter(drySeason2018_19_6mo).map(RefinedLee);
var images_dry2018_19_7mo = imgVV_ASC.filter(drySeason2018_19_7mo).map(RefinedLee);

//reduce to the mean of each image collection
var mean_2we = images_dry2018_19_2we.mean();
var mean_1mo = images_dry2018_19_1mo.mean();
var mean_2mo = images_dry2018_19_2mo.mean();
var mean_3mo = images_dry2018_19_3mo.mean();
var mean_4mo = images_dry2018_19_4mo.mean();
var mean_5mo = images_dry2018_19_5mo.mean();
var mean_6mo = images_dry2018_19_6mo.mean();
var mean_7mo = images_dry2018_19_7mo.mean();

//a. River sites
// Add mean reducer output to the Features in the collection, for all 8 dry season durations.
var river_mean_2we = mean_2we.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_1mo = mean_1mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_2mo = mean_2mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_3mo = mean_3mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_4mo = mean_4mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_5mo = mean_5mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_6mo = mean_6mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var river_mean_7mo = mean_7mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

// Add std reducer output to the Features in the collection, for all 8 dry season durations
var river_std_2we = mean_2we.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_1mo = mean_1mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_2mo = mean_2mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_3mo = mean_3mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_4mo = mean_4mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_5mo = mean_5mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_6mo = mean_6mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var river_std_7mo = mean_7mo.reduceRegions({
  collection: river_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

//b. Sand sites
//mean
var sand_mean_2we = mean_2we.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_1mo = mean_1mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_2mo = mean_2mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_3mo = mean_3mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_4mo = mean_4mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_5mo = mean_5mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_6mo = mean_6mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var sand_mean_7mo = mean_7mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

//Standard deviation
var sand_std_2we = mean_2we.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_1mo = mean_1mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_2mo = mean_2mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_3mo = mean_3mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_4mo = mean_4mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_5mo = mean_5mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_6mo = mean_6mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var sand_std_7mo = mean_7mo.reduceRegions({
  collection: sand_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

//c. Tree sites
//mean
var tree_mean_2we = mean_2we.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_1mo = mean_1mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_2mo = mean_2mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_3mo = mean_3mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_4mo = mean_4mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_5mo = mean_5mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_6mo = mean_6mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var tree_mean_7mo = mean_7mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

//Standard deviation
var tree_std_2we = mean_2we.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_1mo = mean_1mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_2mo = mean_2mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_3mo = mean_3mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_4mo = mean_4mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_5mo = mean_5mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_6mo = mean_6mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var tree_std_7mo = mean_7mo.reduceRegions({
  collection: tree_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

//d. Field sites
//mean
var field_mean_2we = mean_2we.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_1mo = mean_1mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_2mo = mean_2mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_3mo = mean_3mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_4mo = mean_4mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_5mo = mean_5mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_6mo = mean_6mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

var field_mean_7mo = mean_7mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.mean(),
  scale: 10
});

//Standard deviation
var field_std_2we = mean_2we.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_1mo = mean_1mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_2mo = mean_2mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_3mo = mean_3mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_4mo = mean_4mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_5mo = mean_5mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_6mo = mean_6mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

var field_std_7mo = mean_7mo.reduceRegions({
  collection: field_regions,
  reducer: ee.Reducer.stdDev(),
  scale: 10
});

//merge the results from all eight sampling durations into one variable
var river_means = river_mean_2we.merge(river_mean_1mo.merge(river_mean_2mo.merge(river_mean_3mo.merge(river_mean_4mo.merge(river_mean_5mo.merge(river_mean_6mo.merge(river_mean_7mo)))))));
var river_std = river_std_2we.merge(river_std_1mo.merge(river_std_2mo.merge(river_std_3mo.merge(river_std_4mo.merge(river_std_5mo.merge(river_std_6mo.merge(river_std_7mo)))))));

var sand_means = sand_mean_2we.merge(sand_mean_1mo.merge(sand_mean_2mo.merge(sand_mean_3mo.merge(sand_mean_4mo.merge(sand_mean_5mo.merge(sand_mean_6mo.merge(sand_mean_7mo)))))));
var sand_std = sand_std_2we.merge(sand_std_1mo.merge(sand_std_2mo.merge(sand_std_3mo.merge(sand_std_4mo.merge(sand_std_5mo.merge(sand_std_6mo.merge(sand_std_7mo)))))));

var tree_means = tree_mean_2we.merge(tree_mean_1mo.merge(tree_mean_2mo.merge(tree_mean_3mo.merge(tree_mean_4mo.merge(tree_mean_5mo.merge(tree_mean_6mo.merge(tree_mean_7mo)))))));
var tree_std = tree_std_2we.merge(tree_std_1mo.merge(tree_std_2mo.merge(tree_std_3mo.merge(tree_std_4mo.merge(tree_std_5mo.merge(tree_std_6mo.merge(tree_std_7mo)))))));

var field_means = field_mean_2we.merge(field_mean_1mo.merge(field_mean_2mo.merge(field_mean_3mo.merge(field_mean_4mo.merge(field_mean_5mo.merge(field_mean_6mo.merge(field_mean_7mo)))))));
var field_std = field_std_2we.merge(field_std_1mo.merge(field_std_2mo.merge(field_std_3mo.merge(field_std_4mo.merge(field_std_5mo.merge(field_std_6mo.merge(field_std_7mo)))))));

//export the FeatureCollections.
//Export.table.toDrive({
  //collection: river_means,
  //description: 'river_means',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: river_std,
  //description: 'river_std',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: sand_means,
  //description: 'sand_means',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: sand_std,
  //description: 'sand_std',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: tree_means,
  //description: 'tree_means',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: tree_std,
  //description: 'tree_std',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: field_means,
  //description: 'field_means',
  //fileFormat: 'CSV'
//});

//Export.table.toDrive({
  //collection: field_std,
  //description: 'field_std',
  //fileFormat: 'CSV'
//});

////////////////////
///// 3. Classification dry season 2019/20, using different filters and sampling durations
////////////////////

/// define filter and sampling duration and corresponding thresholds - uncomment only one configuration

//Var. 1: 3x3 boxcar filter, 1 month sampling duration
//var duration = ee.Filter.date('2019-11-01', '2019-12-01');
//var filter_classification = meanFilter3by3;

//var THRESHOLD_WATER = -21.5;
//var THRESHOLD_SAND = -12.8;
//var THRESHOLD_FIELDS = -8.3;
//var THRESHOLD_TREES = -2;

//Var. 2: 25x25 boxcar filter, 2 weeks sampling duration
//var duration = ee.Filter.date('2019-11-01', '2019-11-15');
//var filter_classification = meanFilter25by25;

//var THRESHOLD_WATER = -20.4;
//var THRESHOLD_SAND = -12.7;
//var THRESHOLD_FIELDS = -7.4;
//var THRESHOLD_TREES = -2;

//Var. 3: unfiltered, 6 months sampling duration
var duration = ee.Filter.date('2019-11-01', '2020-05-01');
var filter_classification = meanFilter1by1;

var THRESHOLD_WATER = -20.6;
var THRESHOLD_SAND = -13.2;
var THRESHOLD_FIELDS = -9.3;
var THRESHOLD_TREES = -2;

//filter for the respective images, smoothen with respective filter and reduce to the mean of the image collection
var image_classification = imgVV_ASC.filter(duration).map(filter_classification).mean();

//classify
var water2020 = image_classification.lt(THRESHOLD_WATER);
var sand2020 = image_classification.gt(THRESHOLD_WATER).and(image_classification.lt(THRESHOLD_SAND));
var fields2020 = image_classification.gt(THRESHOLD_SAND).and(image_classification.lt(THRESHOLD_FIELDS));
var trees2020 = image_classification.gt(THRESHOLD_FIELDS).and(image_classification.lt(THRESHOLD_TREES));

//mask
var water2020_masked = water2020.mask(water2020.eq(1));
var sand2020_masked = sand2020.mask(sand2020.eq(1));
var fields2020_masked = fields2020.mask(fields2020.eq(1));
var trees2020_masked = trees2020.mask(trees2020.eq(1));

//Map classfication of (mean of) November 2019 images and Sentinel-2 image
//Map.addLayer(S2_1119.median(), rgbVis, 'Sentinel-2 Nov 2019');
//Map.addLayer(water2020_masked, {min: 0, max: 1, palette: ['1368ff']}, 'Water dry season 2019-20 Blue', true, 0.4);
//Map.addLayer(sand2020_masked, {min: 0, max: 1, palette: ['f7d47c']}, 'Sand dry season 2019-20 Sand', true, 0.4);
//Map.addLayer(fields2020_masked, {min: 0, max: 1, palette: ['39a81c']}, 'Fields dry season 2019-20 Light green', true, 0.4);
//Map.addLayer(trees2020_masked, {min: 0, max: 1, palette: ['1f5c0f']}, 'Trees dry season 2019-20 Dark green', true, 0.4);

///// Exporting images
var sen2_1119_exp = S2_1119.median().visualize({bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.3});
var water2020_exp = water2020_masked.visualize({min: 0, max: 1, palette: ['1368ff'], opacity: 0.2});
var sand2020_exp = sand2020_masked.visualize({min: 0, max: 1, palette: ['f7d47c'], opacity: 0.2});
var fields2020_exp = fields2020_masked.visualize({min: 0, max: 1, palette: ['39a81c'], opacity: 0.2});
var trees2020_exp = trees2020_masked.visualize({min: 0, max: 1, palette: ['1f5c0f'], opacity: 0.2});

var S2_base = sen2_1119_exp;
var S2_w = ee.ImageCollection([sen2_1119_exp, water2020_exp]).mosaic();
var S2_s = ee.ImageCollection([sen2_1119_exp, sand2020_exp]).mosaic();
var S2_f = ee.ImageCollection([sen2_1119_exp, fields2020_exp]).mosaic();
var S2_t = ee.ImageCollection([sen2_1119_exp, trees2020_exp]).mosaic();
var S2_all = ee.ImageCollection([sen2_1119_exp, water2020_exp, sand2020_exp, fields2020_exp, trees2020_exp]).mosaic();

//Export.image.toDrive({
  //image: S2_base,
  //description: 'S2_base',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

//Export.image.toDrive({
  //image: S2_w,
  //description: 'S2_w',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

//Export.image.toDrive({
  //image: S2_s,
  //description: 'S2_s',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

//Export.image.toDrive({
  //image: S2_f,
  //description: 'S2_f',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

//Export.image.toDrive({
  //image: S2_t,
  //description: 'S2_t',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

//Export.image.toDrive({
  //image: S2_all,
  //description: 'S2_all',
  //scale: 10,
  //region: JL02,
  //crs: 'EPSG:3106'
//});

////////////////////
///// 4. Settlement detection
////////////////////

//define thresholds for persistent scatterers (0.25 taken from Ferretti et al (2001); -2 and 0.65 from van Leijen (2014))
var THRESHOLD_PS_COV = 0.4;
var THRESHOLD_PS_SIGMA = -4;
var THRESHOLD_PS_FRACTION = 0.65;

//define dry season durations (November-May)
var duration_sett2014_15 = ee.Filter.date('2014-11-01', '2015-05-01');
var duration_sett2015_16 = ee.Filter.date('2015-11-01', '2016-05-01');
var duration_sett2016_17 = ee.Filter.date('2016-11-01', '2017-05-01');
var duration_sett2017_18 = ee.Filter.date('2017-11-01', '2018-05-01');
var duration_sett2018_19 = ee.Filter.date('2018-11-01', '2019-05-01');
var duration_sett2019_20 = ee.Filter.date('2019-11-01', '2020-05-01');

//calculate pixel-wise covariance of amplitude values over whole dry season, both for ASC and DESC
var dry2014_15_ASC = imgVV_ASC.filter(duration_sett2014_15).map(toNatural);
var dry2015_16_ASC = imgVV_ASC.filter(duration_sett2015_16).map(toNatural);
var dry2016_17_ASC = imgVV_ASC.filter(duration_sett2016_17).map(toNatural);
var dry2017_18_ASC = imgVV_ASC.filter(duration_sett2017_18).map(toNatural);
var dry2018_19_ASC = imgVV_ASC.filter(duration_sett2018_19).map(toNatural);
var dry2019_20_ASC = imgVV_ASC.filter(duration_sett2019_20).map(toNatural);

var CoV_dry2014_15_ASC = dry2014_15_ASC.reduce(ee.Reducer.stdDev()).divide(dry2014_15_ASC.mean());
var CoV_dry2015_16_ASC = dry2015_16_ASC.reduce(ee.Reducer.stdDev()).divide(dry2015_16_ASC.mean());
var CoV_dry2016_17_ASC = dry2016_17_ASC.reduce(ee.Reducer.stdDev()).divide(dry2016_17_ASC.mean());
var CoV_dry2017_18_ASC = dry2017_18_ASC.reduce(ee.Reducer.stdDev()).divide(dry2017_18_ASC.mean());
var CoV_dry2018_19_ASC = dry2018_19_ASC.reduce(ee.Reducer.stdDev()).divide(dry2018_19_ASC.mean());
var CoV_dry2019_20_ASC = dry2019_20_ASC.reduce(ee.Reducer.stdDev()).divide(dry2019_20_ASC.mean());

var dry2014_15_DESC = imgVV_DESC.filter(duration_sett2014_15).map(toNatural);
var dry2015_16_DESC = imgVV_DESC.filter(duration_sett2015_16).map(toNatural);
var dry2016_17_DESC = imgVV_DESC.filter(duration_sett2016_17).map(toNatural);
var dry2017_18_DESC = imgVV_DESC.filter(duration_sett2017_18).map(toNatural);
var dry2018_19_DESC = imgVV_DESC.filter(duration_sett2018_19).map(toNatural);
var dry2019_20_DESC = imgVV_DESC.filter(duration_sett2019_20).map(toNatural);

var CoV_dry2014_15_DESC = dry2014_15_DESC.reduce(ee.Reducer.stdDev()).divide(dry2014_15_DESC.mean());
var CoV_dry2015_16_DESC = dry2015_16_DESC.reduce(ee.Reducer.stdDev()).divide(dry2015_16_DESC.mean());
var CoV_dry2016_17_DESC = dry2016_17_DESC.reduce(ee.Reducer.stdDev()).divide(dry2016_17_DESC.mean());
var CoV_dry2017_18_DESC = dry2017_18_DESC.reduce(ee.Reducer.stdDev()).divide(dry2017_18_DESC.mean());
var CoV_dry2018_19_DESC = dry2018_19_DESC.reduce(ee.Reducer.stdDev()).divide(dry2018_19_DESC.mean());
var CoV_dry2019_20_DESC = dry2019_20_DESC.reduce(ee.Reducer.stdDev()).divide(dry2019_20_DESC.mean());

//perform amplitude thresholding

// Use imageCollection.iterate() to make a collection of cumulative values above threshold over time.
// The initial value for iterate() is a list of images already processed. The first image in the list is just 0, with the time0 timestamp.
var first = ee.List([ee.Image(0)]);

// This is a function to pass to Iterate(). As threshold images are computed, add them to the list.
var accumulate = function(image, list) {
  // Get the latest cumulative image from the end of the list with get(-1).
  var previous = ee.Image(ee.List(list).get(-1));
  // Add the current thresholded image to make a new cumulative image and return the list with the cumulative image inserted..
  var added = image.gt(THRESHOLD_PS_SIGMA).add(previous);
  return ee.List(list).add(added);
};

// Create an ImageCollection of cumulative anomaly images by iterating. Since the return type of iterate is unknown, it needs to be cast to a List.
var cum2014_15_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2014_15).iterate(accumulate, first)));
var cum2015_16_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2015_16).iterate(accumulate, first)));
var cum2016_17_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2016_17).iterate(accumulate, first)));
var cum2017_18_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2017_18).iterate(accumulate, first)));
var cum2018_19_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2018_19).iterate(accumulate, first)));
var cum2019_20_ASC = ee.ImageCollection(ee.List(imgVV_ASC.filter(duration_sett2019_20).iterate(accumulate, first)));

var cum2014_15_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2014_15).iterate(accumulate, first)));
var cum2015_16_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2015_16).iterate(accumulate, first)));
var cum2016_17_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2016_17).iterate(accumulate, first)));
var cum2017_18_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2017_18).iterate(accumulate, first)));
var cum2018_19_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2018_19).iterate(accumulate, first)));
var cum2019_20_DESC = ee.ImageCollection(ee.List(imgVV_DESC.filter(duration_sett2019_20).iterate(accumulate, first)));

// Cast image collection to a list and select last image corresponding to the cumulative values above the threshold over the whole dry season
//var last_cum2019_20 = ee.Image(cum2019_20.toList(cum2019_20.size()).get(ee.Number.expression("size-1", {'size': cum2019_20.size()}))).aside(print,'last');
var last_cum2014_15_ASC = ee.Image(cum2014_15_ASC.toList(cum2014_15_ASC.size()).get(-1));
var last_cum2015_16_ASC = ee.Image(cum2015_16_ASC.toList(cum2015_16_ASC.size()).get(-1));
var last_cum2016_17_ASC = ee.Image(cum2016_17_ASC.toList(cum2016_17_ASC.size()).get(-1));
var last_cum2017_18_ASC = ee.Image(cum2017_18_ASC.toList(cum2017_18_ASC.size()).get(-1));
var last_cum2018_19_ASC = ee.Image(cum2018_19_ASC.toList(cum2018_19_ASC.size()).get(-1));
var last_cum2019_20_ASC = ee.Image(cum2019_20_ASC.toList(cum2019_20_ASC.size()).get(-1));

var last_cum2014_15_DESC = ee.Image(cum2014_15_DESC.toList(cum2014_15_DESC.size()).get(-1));
var last_cum2015_16_DESC = ee.Image(cum2015_16_DESC.toList(cum2015_16_DESC.size()).get(-1));
var last_cum2016_17_DESC = ee.Image(cum2016_17_DESC.toList(cum2016_17_DESC.size()).get(-1));
var last_cum2017_18_DESC = ee.Image(cum2017_18_DESC.toList(cum2017_18_DESC.size()).get(-1));
var last_cum2018_19_DESC = ee.Image(cum2018_19_DESC.toList(cum2018_19_DESC.size()).get(-1));
var last_cum2019_20_DESC = ee.Image(cum2019_20_DESC.toList(cum2019_20_DESC.size()).get(-1));

//select PS candidates: smaller than CoV threshold AND in 65% of all images larger than sigma_0 threshold (-2 dB)
//(use size-1 since the first element of cum2019_20 is the zero-image)
var PS_dry2014_15_ASC = CoV_dry2014_15_ASC.lt(THRESHOLD_PS_COV).and(last_cum2014_15_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2014_15_ASC.size()})));
var PS_dry2015_16_ASC = CoV_dry2015_16_ASC.lt(THRESHOLD_PS_COV).and(last_cum2015_16_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2015_16_ASC.size()})));
var PS_dry2016_17_ASC = CoV_dry2016_17_ASC.lt(THRESHOLD_PS_COV).and(last_cum2016_17_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2016_17_ASC.size()})));
var PS_dry2017_18_ASC = CoV_dry2017_18_ASC.lt(THRESHOLD_PS_COV).and(last_cum2017_18_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2017_18_ASC.size()})));
var PS_dry2018_19_ASC = CoV_dry2018_19_ASC.lt(THRESHOLD_PS_COV).and(last_cum2018_19_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2018_19_ASC.size()})));
var PS_dry2019_20_ASC = CoV_dry2019_20_ASC.lt(THRESHOLD_PS_COV).and(last_cum2019_20_ASC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2019_20_ASC.size()})));

var PS_dry2014_15_DESC = CoV_dry2014_15_DESC.lt(THRESHOLD_PS_COV).and(last_cum2014_15_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2014_15_DESC.size()})));
var PS_dry2015_16_DESC = CoV_dry2015_16_DESC.lt(THRESHOLD_PS_COV).and(last_cum2015_16_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2015_16_DESC.size()})));
var PS_dry2016_17_DESC = CoV_dry2016_17_DESC.lt(THRESHOLD_PS_COV).and(last_cum2016_17_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2016_17_DESC.size()})));
var PS_dry2017_18_DESC = CoV_dry2017_18_DESC.lt(THRESHOLD_PS_COV).and(last_cum2017_18_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2017_18_DESC.size()})));
var PS_dry2018_19_DESC = CoV_dry2018_19_DESC.lt(THRESHOLD_PS_COV).and(last_cum2018_19_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2018_19_DESC.size()})));
var PS_dry2019_20_DESC = CoV_dry2019_20_DESC.lt(THRESHOLD_PS_COV).and(last_cum2019_20_DESC.gt(ee.Number.expression("threshold * (size-1)", {'threshold': THRESHOLD_PS_FRACTION, 'size': cum2019_20_DESC.size()})));

//combine ASC and DESC
var PS_dry2014_15 = PS_dry2014_15_ASC.or(PS_dry2014_15_DESC);
var PS_dry2015_16 = PS_dry2015_16_ASC.or(PS_dry2015_16_DESC);
var PS_dry2016_17 = PS_dry2016_17_ASC.or(PS_dry2016_17_DESC);
var PS_dry2017_18 = PS_dry2017_18_ASC.or(PS_dry2017_18_DESC);
var PS_dry2018_19 = PS_dry2018_19_ASC.or(PS_dry2018_19_DESC);
var PS_dry2019_20 = PS_dry2019_20_ASC.or(PS_dry2019_20_DESC);

var PS_dry2014_15_masked = PS_dry2014_15.mask(PS_dry2014_15.eq(1));
var PS_dry2015_16_masked = PS_dry2015_16.mask(PS_dry2015_16.eq(1));
var PS_dry2016_17_masked = PS_dry2016_17.mask(PS_dry2016_17.eq(1));
var PS_dry2017_18_masked = PS_dry2017_18.mask(PS_dry2017_18.eq(1));
var PS_dry2018_19_masked = PS_dry2018_19.mask(PS_dry2018_19.eq(1));
var PS_dry2019_20_masked = PS_dry2019_20.mask(PS_dry2019_20.eq(1));

//Alternative for locations at the intersection of two SAR imaging patches: apply amplitude threshold to mean of all images instead of to the individual images:
//var PS_dry2019_20_alt = CoV_dry2019_20.lt(THRESHOLD_PS_COV).and(imgVV_ASC.filter(duration_sett2019_20).mean().gt(THRESHOLD_PS_SIGMA));
//var PS_dry2019_20_alt_masked = PS_dry2019_20_alt.mask(PS_dry2019_20_alt.eq(1));

//Map.centerObject(settl_export, 17);
//Map.addLayer(PS_dry2019_20_alt_masked, {min: 0, max: 1, palette: ['f7d47c']}, 'PS candidates Alternative dry season 2019-20 Sand', true);
//Map.addLayer(PS_dry2017_18_masked, {min: 0, max: 1, palette: ['960505']}, 'PS candidates dry season 2017-18 Wine Red', true);
//Map.addLayer(PS_dry2018_19_masked, {min: 0, max: 1, palette: ['1368ff']}, 'PS candidates dry season 2018-19 Blue', true);
//Map.addLayer(PS_dry2019_20_masked, {min: 0, max: 1, palette: ['f79d00']}, 'PS candidates dry season 2019-20 Orange', true);

////////////////////
///// 6. Detect eroded sites
////////////////////

/// for land cover classification: define filter, sampling duration and corresponding thresholds

//for years 2014-2018: 6 months sampling duration
var duration2014 = ee.Filter.date('2014-11-01', '2015-05-01');
var duration2015 = ee.Filter.date('2015-11-01', '2016-05-01');
var duration2016 = ee.Filter.date('2016-11-01', '2017-05-01');
var duration2017 = ee.Filter.date('2017-11-01', '2018-05-01');
var duration2018 = ee.Filter.date('2018-11-01', '2019-05-01');

var THRESHOLD_SAND_6mo = -13.2;

//for year 2019: 1 month sampling duration
var duration2019 = ee.Filter.date('2019-11-01', '2019-12-01');

var THRESHOLD_SAND_1mo = -12.7;

//define filter: 7x7 boxcar
var filter = meanFilter7by7;

//filter for the respective images, smooth with respective filter and reduce to the mean of the image collection
var image2014 = imgVV_ASC.filter(duration2014).map(filter).mean();
var image2015 = imgVV_ASC.filter(duration2015).map(filter).mean();
var image2016 = imgVV_ASC.filter(duration2016).map(filter).mean();
var image2017 = imgVV_ASC.filter(duration2017).map(filter).mean();
var image2018 = imgVV_ASC.filter(duration2018).map(filter).mean();
var image2019 = imgVV_ASC.filter(duration2019).map(filter).mean();

//detect eroded non-sand pixels (fields or trees) for each year: greater than sand-fields threshold before the monsoon, and smaller after
var eroded_land_2015 = image2014.gt(THRESHOLD_SAND_6mo).and(image2015.lt(THRESHOLD_SAND_6mo));
var eroded_land_2016 = image2015.gt(THRESHOLD_SAND_6mo).and(image2016.lt(THRESHOLD_SAND_6mo));
var eroded_land_2017 = image2016.gt(THRESHOLD_SAND_6mo).and(image2017.lt(THRESHOLD_SAND_6mo));
var eroded_land_2018 = image2017.gt(THRESHOLD_SAND_6mo).and(image2018.lt(THRESHOLD_SAND_6mo));
var eroded_land_2019 = image2018.gt(THRESHOLD_SAND_6mo).and(image2019.lt(THRESHOLD_SAND_1mo));

//mask eroded pixels
var eroded_land_2015_masked = eroded_land_2015.mask(eroded_land_2015.eq(1));
var eroded_land_2016_masked = eroded_land_2016.mask(eroded_land_2016.eq(1));
var eroded_land_2017_masked = eroded_land_2017.mask(eroded_land_2017.eq(1));
var eroded_land_2018_masked = eroded_land_2018.mask(eroded_land_2018.eq(1));
var eroded_land_2019_masked = eroded_land_2019.mask(eroded_land_2019.eq(1));

//map
Map.centerObject(JR04, 14);

//Map optical Sentinel-2 images for optical assessment
//Map.addLayer(S2_0118.median(), rgbVis, 'Sentinel-2 Nov 2018');
//Map.addLayer(S2_0119.median(), rgbVis, 'Sentinel-2 Jan 2019');
Map.addLayer(S2_1119.median(), rgbVis, 'Sentinel-2 Nov 2019');
//Map.addLayer(S2_0120.median(), rgbVis, 'Sentinel-2 Jan 2020');

//Map.addLayer(eroded_land_2015_masked, {min: 0, max: 1, palette: ['944c1f']}, 'Non-Sand eroded in 2015 monsoon (Dark brown)', true);
//Map.addLayer(eroded_land_2016_masked, {min: 0, max: 1, palette: ['ab541d']}, 'Non-Sand eroded in 2016 monsoon', true);
//Map.addLayer(eroded_land_2017_masked, {min: 0, max: 1, palette: ['c45a16']}, 'Non-Sand eroded in 2017 monsoon', true);
//Map.addLayer(eroded_land_2018_masked, {min: 0, max: 1, palette: ['c95002']}, 'Non-Sand eroded in 2018 monsoon', true);
Map.addLayer(eroded_land_2019_masked, {min: 0, max: 1, palette: ['ff6200']}, 'Non-Sand eroded in 2019 monsoon (Light brown)', true);

/// eroded settlements

//find eroded PS
var PS_eroded2015 = PS_dry2014_15.and(image2015.lt(THRESHOLD_SAND_6mo));
var PS_eroded2016 = PS_dry2015_16.and(image2016.lt(THRESHOLD_SAND_6mo));
var PS_eroded2017 = PS_dry2016_17.and(image2017.lt(THRESHOLD_SAND_6mo));
var PS_eroded2018 = PS_dry2017_18.and(image2018.lt(THRESHOLD_SAND_6mo));
var PS_eroded2019 = PS_dry2018_19.and(image2019.lt(THRESHOLD_SAND_1mo));

//mask eroded pixels
var PS_eroded2015_masked = PS_eroded2015.mask(PS_eroded2015.eq(1));
var PS_eroded2016_masked = PS_eroded2016.mask(PS_eroded2016.eq(1));
var PS_eroded2017_masked = PS_eroded2017.mask(PS_eroded2017.eq(1));
var PS_eroded2018_masked = PS_eroded2018.mask(PS_eroded2018.eq(1));
var PS_eroded2019_masked = PS_eroded2019.mask(PS_eroded2019.eq(1));

//map
//Map.addLayer(PS_eroded2015_masked, {min: 0, max: 1, palette: ['1061e3']}, 'Settlement eroded in 2015 monsoon', true);
//Map.addLayer(PS_eroded2016_masked, {min: 0, max: 1, palette: ['1061e3']}, 'Settlement eroded in 2016 monsoon', true);
//Map.addLayer(PS_eroded2017_masked, {min: 0, max: 1, palette: ['1061e3']}, 'Settlement eroded in 2017 monsoon', true);
//Map.addLayer(PS_eroded2018_masked, {min: 0, max: 1, palette: ['1061e3']}, 'Settlement eroded in 2018 monsoon', true);
Map.addLayer(PS_eroded2019_masked, {min: 0, max: 1, palette: ['1061e3']}, 'Settlement eroded in 2019 monsoon', true);

///// Exporting images
var S2_0118 = S2_0118.median().visualize({bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.3});
var S2_0119 = S2_0119.median().visualize({bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.3});
var S2_1119 = S2_1119.median().visualize({bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.3});
var S2_0120 = S2_0120.median().visualize({bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.3});

var eroded_15 = eroded_land_2015_masked.visualize({min: 0, max: 1, palette: ['944c1f'], opacity: 0.8});
var eroded_16 = eroded_land_2016_masked.visualize({min: 0, max: 1, palette: ['ab541d'], opacity: 0.8});
var eroded_17 = eroded_land_2017_masked.visualize({min: 0, max: 1, palette: ['c45a16'], opacity: 0.8});
var eroded_18 = eroded_land_2018_masked.visualize({min: 0, max: 1, palette: ['e05f0d'], opacity: 0.8});
var eroded_19 = eroded_land_2019_masked.visualize({min: 0, max: 1, palette: ['ff6200'], opacity: 0.3});

var PS_15 = PS_eroded2015_masked.visualize({min: 0, max: 1, palette: ['1061e3']});
var PS_16 = PS_eroded2016_masked.visualize({min: 0, max: 1, palette: ['1061e3']});
var PS_17 = PS_eroded2017_masked.visualize({min: 0, max: 1, palette: ['1061e3']});
var PS_18 = PS_eroded2018_masked.visualize({min: 0, max: 1, palette: ['1061e3']});
var PS_19 = PS_eroded2019_masked.visualize({min: 0, max: 1, palette: ['ff0000']});

var mosaic = ee.ImageCollection([S2_1119, eroded_19, PS_19]).mosaic();
//var mosaic = ee.ImageCollection([S2_0120, eroded_15, eroded_16, eroded_17, eroded_18, eroded_19, PS_15, PS_16, PS_17, PS_18, PS_19]).mosaic();

Export.image.toDrive({
  image: mosaic,
  description: 'eroded_S2_19_Nov',
  scale: 10,
  region: JR04,
  crs: 'EPSG:3106'
});

////////////////////
///// 7. Accuracy assessment using Sentinel-2 imagery
////////////////////

// Load Sentinel-2 TOA reflectance data.
var S2_assessment = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate('2021-03-01', '2021-04-01')
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

// Select Red and NIR bands and calculate monthly median of NDVI
var s2 = S2_assessment.select(['B4','B8'], ['R','N']);

function addNdvi(img) {
  var nd = img.normalizedDifference(['N', 'R']);
  return img.addBands(nd.rename('NDVI'));
}

var ndvi = s2.map(addNdvi);

var S2_for_class = ndvi.select('NDVI').median();

// Define threshold between water/sand and vegetated land and classify the two land cover classes "water/sand" and "vegetated"
var THRESHOLD_ndvi_sand_veg = 0.1;

var water_sand_ndvi = S2_for_class.lt(THRESHOLD_ndvi_sand_veg);
var veg_ndvi = S2_for_class.gt(THRESHOLD_ndvi_sand_veg);

var water_sand_ndvi_masked = water_sand_ndvi.mask(water_sand_ndvi.eq(1));
var veg_ndvi_masked = veg_ndvi.mask(veg_ndvi.eq(1));

// Create SAR-based classification
//Var. 1: 3x3 boxcar filter, 1 month sampling duration
var filter_classification = meanFilter3by3;
var duration = ee.Filter.date('2021-03-01', '2021-04-01');

//filter for the respective images, smooth with respective filter and reduce to the mean of the image collection
var image_classification = imgVV_ASC.filter(duration).map(filter_classification).mean();

//classify
var THRESHOLD_SAND = -12.8;
var water_sand2020 = image_classification.lt(THRESHOLD_SAND);
var vegetation2020 = image_classification.gt(THRESHOLD_SAND);

//mask
var water_sand2020_masked = water_sand2020.mask(water_sand2020.eq(1));
var vegetation2020_masked = vegetation2020.mask(vegetation2020.eq(1));

//compare SAR-based to S2-based classification
var water_sand_identical = water_sand_ndvi_masked.eq(1).and(water_sand2020_masked.eq(1));
var vegetation_identical = veg_ndvi_masked.eq(1).and(vegetation2020_masked.eq(1));
var vegetation_false_pos = water_sand_ndvi_masked.eq(1).and(vegetation2020_masked.eq(1));
var vegetation_false_neg = veg_ndvi_masked.eq(1).and(water_sand2020_masked.eq(1));

//Map.addLayer(water_sand_identical, {min: 0, max: 1, palette: ['0000FF'], opacity: 0.8}, 'Water/sand identical (blue)', true);
//Map.addLayer(vegetation_identical, {min: 0, max: 1, palette: ['32a846'], opacity: 0.8}, 'Vegetation identical (green)', true);
//Map.addLayer(vegetation_false_pos, {min: 0, max: 1, palette: ['a88c32'], opacity: 0.8}, 'Vegetation false pos (sand)', true);
//Map.addLayer(vegetation_false_neg, {min: 0, max: 1, palette: ['944c1f'], opacity: 0.8}, 'Vegetation false neg (brown)', true);

var area_water_sand_identical = ee.Number(water_sand_identical.multiply(ee.Image.pixelArea()).divide(1e6).reduceRegion({reducer:ee.Reducer.sum(), geometry:assessment_site, scale:1, maxPixels: 1e9, bestEffort:true}));
var area_vegetation_identical = ee.Number(vegetation_identical.multiply(ee.Image.pixelArea()).divide(1e6).reduceRegion({reducer:ee.Reducer.sum(), geometry:assessment_site, scale:1, maxPixels: 1e9, bestEffort:true}));
var area_vegetation_false_pos = ee.Number(vegetation_false_pos.multiply(ee.Image.pixelArea()).divide(1e6).reduceRegion({reducer:ee.Reducer.sum(), geometry:assessment_site, scale:1, maxPixels: 1e9, bestEffort:true}));
var area_vegetation_false_neg = ee.Number(vegetation_false_neg.multiply(ee.Image.pixelArea()).divide(1e6).reduceRegion({reducer:ee.Reducer.sum(), geometry:assessment_site, scale:1, maxPixels: 1e9, bestEffort:true}));

var features_all = [
  ee.Feature(null, area_water_sand_identical),
  ee.Feature(null, area_vegetation_identical),
  ee.Feature(null, area_vegetation_false_pos),
  ee.Feature(null, area_vegetation_false_neg)
];

// Create a FeatureCollection from the list and print it.
var all_areas = ee.FeatureCollection(features_all);

Export.table.toDrive({
  collection: all_areas,
  description: 'identical_areas_V3_1mo_0321',
  fileFormat: 'CSV'
});
