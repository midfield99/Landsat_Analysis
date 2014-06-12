from optparse import OptionParser
import landsatProcessing as satProc
#Sample command:
#landsatProcCommandLine.py --imageType=NDVI --directory=D:/Downloads/LC80260312014143LGN00.tar/LC80260312014143LGN00/ --id=LC80260312014143LGN00 --outputFile=testImg.tif

class accessLandsatProcessing:
	def __init__(self, options, args):
		
		landsat = satProc.landsat8Scene(options.directory, options.id)

		if options.imageType == "RGB":
			landsat.getRGB()
			landsat.createImage(options.outputFile)
			print "An RGB image was created."
			
		if options.imageType == "CIR":
			landsat.getCIR()
			landsat.createImage(options.outputFile)
			print "A CIR image was created."
			
		if options.imageType == "NDVI":
			landsat.getNDVI()
			landsat.createImage(options.outputFile)
			print "An NDVI image was created."


parser = OptionParser()

parser.add_option("--imageType", type="string", dest="imageType")
parser.add_option("--directory", type="string", dest="directory")
parser.add_option("--id", type="string", dest="id")
parser.add_option("--outputFile", type="string", dest="outputFile")

options, args = parser.parse_args()

image = accessLandsatProcessing(options, args)
