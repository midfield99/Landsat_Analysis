#I should change the classes so that create image creates an image from 3 inputted bands.
import numpy as np
import pdb
import time
from osgeo import gdal, ogr

class landsat8Scene:
	def __init__(self, dir, id):
		self.rootDir = dir
		self.scene_id = id
		
		self.proj = None
		self.geoTrans = None
		self.col = None
		self.row = None
		self.driver = None
		
		self.landsatBands = {'1':("_B1","Coastal Aerosol"), '2':("_B2","Blue"), '3':("_B3","Green"), \
			'4':("_B4","Red"), '5':("_B5","NIR"), '6':("_B6","SWIR 1"), '7':("_B7","SWIR 2"), \
			'8':("_B8","Panchromatic"), '9':("_B9","Cirrus"), '10':("_B10","TIRS 1"), '11':("_B11","TIRS 2")}
	
	#Each band in the landsat 8 data sets is its own image,
	# so each image is checked to make sure it was created with the same settings.
	def checkBand(self, proj, geoTrans, col, row):
		if self.proj == None: self.proj = proj
		if self.geoTrans == None: self.geoTrans = geoTrans
		if self.col == None: self.col = col
		if self.row == None: self.row = row
		
		if self.proj != proj:
			print "Unexpected Error. The bands have multiple projections."
		if self.geoTrans != geoTrans:
			print "Unexpected Error. The bands have multiple GeoTransforms."
		if self.col != col:
			print "Unexpected Error. The bands have different widths."
		if self.row != row:
			print "Unexpected Error. The bands have different heights."
	
	def getRGB(self):
		self.redBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['4'][0] + ".TIF")
		self.greenBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['3'][0] + ".TIF")
		self.blueBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['2'][0] + ".TIF")
		
	def getCIR(self):
		self.redBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['5'][0] + ".TIF")
		self.greenBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['4'][0] + ".TIF")
		self.blueBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['3'][0] + ".TIF")
	
	#Used in testing the NDVI image.
	def getTestNDVI(self):
		self.redBand = self.openRaster(self.rootDir + self.scene_id + "_NIRtest.TIF")
		self.redBand = np.multiply(np.add(self.redBand, np.float32(1.0)), np.float32(65535/4.0)).astype('uint16')
		self.greenBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['4'][0] + ".TIF")
		self.blueBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['3'][0] + ".TIF")
	
	#Uses raster operations to get the NDVI values
	def getNDVI(self):
		
		self.NIR = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['5'][0] + ".TIF").clip(0).astype('float16')
		self.redBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['4'][0] + ".TIF").clip(0).astype('float16')
		self.greenBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['4'][0] + ".TIF")
		self.blueBand = self.openRaster(self.rootDir + self.scene_id + self.landsatBands['3'][0] + ".TIF")
		
		#type float32 causes memory issues, and float16 is too small for adding two arrays together without overflows.
		self.NIR = np.divide(self.NIR, 2.0)
		self.redBand = np.divide(self.redBand, 2.0)
		
		#NDVI ranges from 0 to 1,
		#NDVI = (NIR - VIR)/(NIR + VIR)
		NDVIs = np.subtract(self.NIR, self.redBand)

		NDVIa = np.add(self.NIR, self.redBand)

		self.redBand = np.divide(NDVIs, NDVIa)
		#Please note createImage, the array is of type int16, so the range needs to go from (-1, 1) to (0, 65535)
		#I ran into some memory issues calculating the NDVI, so I compensated that by using a couple multiplications, instead of one.
		#self.redBand = np.add(np.multiply(self.redBand, 4096), 4096).astype('uint16')
		self.redBand += 1
		self.redBand = np.multiply(self.redBand, 4096).astype('uint16')
		self.redBand *= 8
		#self.redBand = np.multiply(self.redBand, 8)

	def createImage(self, outputPath):
		#Initializes the output image.
		outputImage = gdal.GetDriverByName("GTiff").Create(outputPath, self.col, self.row, 3, gdal.GDT_UInt16)
		
		#Creates metadata.
		outputImage.SetProjection(self.proj)
		outputImage.SetGeoTransform(self.geoTrans)
		
		#print outputImage.isValid()
		
		#Writes the bands to the raser.
		bandList = [(1, self.redBand), (2, self.greenBand), (3, self.blueBand)]
		for b in bandList:
			band = outputImage.GetRasterBand(b[0])
			band.WriteArray(b[1])
			del band
			
		#Closes the image.
		outputImage = None
	
	def openRaster(self, filePath):
		try: 
			#pdb.set_trace()
			raster = gdal.Open(filePath)

			self.checkBand(raster.GetProjection(), raster.GetGeoTransform(), raster.RasterXSize, raster.RasterYSize)

			return raster.ReadAsArray()
			
		except:
			print "There was an error opening the file: " + str(filePath)

