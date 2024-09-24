import sys
import os

from ij import IJ
from ij import WindowManager
from java.io import File

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.stardist import StarDistDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SimpleSparseLAPTrackerFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackMateObject
from fiji.plugin.trackmate.features.track import TrackIndexAnalyzer

import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.visualization.table import AllSpotsTableView
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettings

from ij.plugin import ChannelSplitter#, ZProjector
from fiji.plugin.trackmate.action import CaptureOverlayAction #as CaptureOverlayAction


##### We have to do the following to avoid errors with UTF8 chars generated in 
##### TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')


#####---------------------------------------------------
##### Path of the folder with the files to be processed	
#####---------------------------------------------------
input_folder = r"[YOUR INPUT PATH HERE]"

#####------------------------------------------------------------
##### Path of the folder to which the .csv-files should be saved
#####------------------------------------------------------------
output_folder = r"[YOUR OUTPUT PATH HERE]"




#####----------------------------------------
##### Function to pre-process the .czi-files
#####----------------------------------------
def pre_processing(imp):
	imp.show()
	
##### Save the current channel, slice, and frame position
	channel = imp.getChannel()
	slice = imp.getSlice()
	frame = imp.getFrame()
	
##### Enhance contrast on the current channel
	IJ.run("Enhance Contrast", "saturated=0.35")
	
##### Move to the next channel and apply "Orange Hot" LUT
	imp.setPosition(channel + 1, slice, frame)
	IJ.run("Orange Hot")
	IJ.resetMinAndMax(imp)
	
##### Move to the third channel, apply "Grays" LUT, and enhance contrast
	imp.setPosition(channel + 2, slice, frame)
	IJ.run("Grays")
	IJ.run("Enhance Contrast", "saturated=0.35")
	
##### Split channels into separate images
	channel_images = ChannelSplitter.split(imp)
	
##### Close the third channel's window
	channel_images[2].close()
	imp.close()
	
##### Process the first two channels
	for i in range(2):
	    imp_channel = channel_images[i]
	    imp_channel.show()  # Ensure the channel image is active
	    imp_channel = IJ.run("Gaussian Blur...", "sigma=2 stack")
	    imp_channel = IJ.run("Subtract Background...", "rolling=50 stack")
	    imp_channel = IJ.run("Out [-]")




#####------------------------------------------------
##### Function to perform the tracking via Trackmate
#####------------------------------------------------
def track_and_export(imp, output_path, imp_name):
#####----------------------------
##### Create the model object now
#####----------------------------
##### Some of the parameters we configure below need to have
##### a reference to the model at creation. So we create an
##### empty model now.
	
	model = Model()
	
##### Send all messages to ImageJ log window.
	model.setLogger(Logger.IJ_LOGGER)
	
	
	
#####------------------------
##### Prepare settings object
#####------------------------
	settings = Settings(imp)
	
##### Configure detector
	settings.detectorFactory = StarDistDetectorFactory()
	settings.detectorSettings = {
	    'TARGET_CHANNEL' : 1
	}  
	
##### Configure spot filters - Filter by Radius
	filter_min = FeatureFilter('RADIUS', 5, True)  # Keep spots with RADIUS >= 5 µm
	settings.addSpotFilter(filter_min)
	
	filter_max = FeatureFilter('RADIUS', 30, False)  # Keep spots with RADIUS <= 30 µm
	settings.addSpotFilter(filter_max)
	
##### Configure tracker
	settings.trackerFactory = SimpleSparseLAPTrackerFactory()
	settings.trackerSettings = {
	    'LINKING_MAX_DISTANCE': 15.0,
	    'MAX_FRAME_GAP': 2,
	    'GAP_CLOSING_MAX_DISTANCE': 30.0,
	    'ALLOW_TRACK_SPLITTING': True,
	    'ALLOW_TRACK_MERGING': True,
	    'ALLOW_GAP_CLOSING': True,
	    'SPLITTING_MAX_DISTANCE': 15.0,
	    'MERGING_MAX_DISTANCE': 15.0,
	    'CUTOFF_PERCENTILE': 0.9,
	    'ALTERNATIVE_LINKING_COST_FACTOR': 1.05,
	    'BLOCKING_VALUE': float('inf')
	}
	
##### Add ALL the feature analyzers known to TrackMate. They will 
##### yield numerical features for the results, such as speed, mean intensity etc.
	settings.addAllAnalyzers()		
	
#####-------------------
##### Instantiate plugin
#####-------------------
	
	trackmate = TrackMate(model, settings)
	
#####--------
##### Process
#####--------
	
	ok = trackmate.checkInput()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
	
	ok = trackmate.process()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
    
#####----------------
##### Display results
#####----------------
		 
##### A selection.
	selectionModel = SelectionModel( model )
		 
##### Read the default display settings.
	ds = DisplaySettingsIO.readUserDefault()
##### Color by tracks.
	ds.setTrackColorBy( TrackMateObject.TRACKS, TrackIndexAnalyzer.TRACK_INDEX )
	ds.setSpotColorBy( TrackMateObject.TRACKS, TrackIndexAnalyzer.TRACK_INDEX )
		 
	displayer =  HyperStackDisplayer( model, selectionModel, imp, ds )
	displayer.render()
	displayer.refresh()
	
#####----------------------------------------------------
##### 3/ Export spots, edges and track data to CSV files.
#####----------------------------------------------------
	 
##### The following uses the tables that are displayed in the TrackMate
##### GUI. Doesn't work in headless mode, just run in Fiji as Script.
	 
##### Create default SelectionModel and DisplaySettings
	sm = SelectionModel(trackmate.getModel())
	ds = DisplaySettings()
	
##### Create JavaFile for Export
	csvFileSpots = File(os.path.join(output_path, imp_name + "_Spots.csv"))
##### prepare files for Tracks and AllSpots - remove respective # if you want an exported file for either
	csvFileTracks = File(os.path.join(output_path, imp_name + "_Tracks.csv"))
	#csvFileAllSpots = File(os.path.join(output_path, imp_name + "_AllSpots.csv"))
	
	# Save spot and track statistics
	trackTableView = TrackTableView(trackmate.getModel(), sm, ds, "trackTableView")
	trackTableView.getSpotTable().exportToCsv(csvFileSpots)
##### Save track table - remove # if you want an exported file of the track details
##### (number of tracks, etc in a separate file)
	trackTableView.getTrackTable().exportToCsv(csvFileTracks)
	
##### Save all spots table  - remove # if you want an exported file of all spots detected even if they
##### were not assigned to a track
	#spotsTableView = AllSpotsTableView(trackmate.getModel(), sm, ds, "spotsTableView")
	#spotsTableView.exportToCsv(csvFileAllSpots.getAbsolutePath())
	


#####-----------------------------------------------------------------------------------------
##### Main body to process .czi files in a folder and output tracking data to another folder
#####-----------------------------------------------------------------------------------------
# Walk through all files in the input folder
for filename in os.listdir(input_folder):
	imp = IJ.openImage(os.path.join(input_folder, filename))
	imp.show()
##### Get the number of timeframes of the image
	imp_frames = imp.getNFrames()
##### Pre-process the file
	pre_processing(imp)
##### Process all open images through Trackmate until no images are open anymore
	while not WindowManager.getCurrentImage() == None:
		imp_current = WindowManager.getCurrentImage()
		imp_name = imp_current.getTitle()[:-4]
		track_and_export(imp_current, output_folder, imp_name)
######### Set necessary arguments for capturing the overlay
		logger = Logger.IJ_LOGGER		
		model = Model()
		settings = Settings(imp_current)		
		trackmate = TrackMate(model, settings)		
######### Capture the overlay so it is saved together with the image
		capture = CaptureOverlayAction.capture(trackmate, -1, imp_frames, logger)
######### Make sure the captured image is active
		capture.show()
######### Save image together with the captured overlay as .tif into the output folder
		IJ.saveAs("TIFF", output_folder + "\\" + imp_name + "_Overlay")
######### Close the capture and currently open image so the next image can be processed
		capture.close()
		imp_current.changes = False  # Prevents the "Do you want to save?" dialog
		imp_current.close()
