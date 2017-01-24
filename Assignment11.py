# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:02:33 2017

@author: Koen Veenenbos & Tim Jak
"""

# Importing modules
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
import numpy as np
import os, subprocess
import urllib
import tarfile, sys
import matplotlib.pyplot as plt

#Download and untar the data
def DownloadUntarFile (Inputurl, NameFile):
    url = Inputurl
    urllib.urlretrieve (url, NameFile)
    tar = tarfile.open(NameFile)
    tar.extractall()
    tar.close()

DownloadUntarFile("https://dl.dropbox.com/s/zb7nrla6fqi1mq4/LC81980242014260-SC20150123044700.tar.gz", "LC8data.tar")

# Define bands
band4 = './LC81980242014260LGN00_sr_band4.tif'
band5 = './LC81980242014260LGN00_sr_band5.tif'

# Open bands
dsband4 = gdal.Open(band4, GA_ReadOnly)
dsband5 = gdal.Open(band5, GA_ReadOnly)

# Read data from the bands into an array
band4_Arr = dsband4.GetRasterBand(1).ReadAsArray(0,0,dsband4.RasterXSize, dsband4.RasterYSize)
band5_Arr = dsband5.GetRasterBand(1).ReadAsArray(0,0,dsband5.RasterXSize, dsband5.RasterYSize)

# Set data type 
band4_Arr=band4_Arr.astype(np.float32)
band5_Arr=band5_Arr.astype(np.float32)

# Create a mask
mask = np.greater(band5_Arr + band4_Arr,0)

# Set an ignore value for values that cannot represent NDWI values and create NDWI
with np.errstate(invalid='ignore'):
        ndwi = np.choose(mask,(-99,(band4_Arr - band5_Arr) / (band4_Arr + band5_Arr)))

# Check data if it contains correct values
print 'NDVI min and max values', ndwi.min(), ndwi.max()

# Check the real minimum value
print ndwi[ndwi>-99].min()

# Write the result to disk
driver = gdal.GetDriverByName('GTiff')
outDataSet = driver.Create('./ndwi.tif', dsband4.RasterXSize, dsband4.RasterYSize, 1, GDT_Float32)
outBand = outDataSet.GetRasterBand(1)
outBand.WriteArray(ndwi,0,0)
outBand.SetNoDataValue(-99)

# Set the projection and extent information of the dataset
outDataSet.SetProjection(dsband4.GetProjection())
outDataSet.SetGeoTransform(dsband4.GetGeoTransform())

# Save or Flush the data
outBand.FlushCache()
outDataSet.FlushCache()

# Reproject the file
bash = "gdalwarp -t_srs EPSG:4326 ./ndwi.tif ./ndwi_latlon.tif"
ndwi_latlon = subprocess.Popen(bash, shell = True)

ndwiLatLon = gdal.Open("./ndwi_latlon.tif")
ndwiPlot = ndwiLatLon.ReadAsArray(0, 0, ndwiLatLon.RasterXSize, ndwiLatLon.RasterYSize)
plt.imshow(ndwiPlot, interpolation = "nearest", vmin=0, cmap=plt.cm.gist_earth)
plt.show()
