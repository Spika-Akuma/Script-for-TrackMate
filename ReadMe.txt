This script was made for Fiji (https://fiji.sc/) with the plugins CSBDeep (https://github.com/CSBDeep/CSBDeep_fiji), TrackMate (https://github.com/trackmate-sc/TrackMate) and StarDist (https://github.com/stardist/stardist-imagej).

How to use the Automatize.py:

Underneath you will find the steps to use the Jython
script to automatize the nuclei tracking from microscopy
images via Fiji’s plugin TrackMate.

1) Open Fiji. Make sure Trackmate (especially Trackmate-StarDist), StarDist and CSBDeep are installed.
2) Drag Automatize.py into Fiji to open it.
3) Make sure the folder paths (input folder; output folder)are set to the respective folders.
	a) Use full paths to make sure it works.
	b) Use single slashes or backslashes only with none at the end. 
	   This is how a correct example path looks like: ’C:\user\User\Desktop\Input’.
	c) Do not remove the r in front of the quotation marks for the two paths. 
	   They are important to ensure the paths are read and interpreted correctly.
	d) Make sure the output-folder is not the input-folder.
	e) Make sure the only files in the input-folder are the image series you want to process. 
	   The code does not filter out files and might come up with errors with other files in the folder.
4) Click ”Run” and wait until the Script is finished.

In case there are errors please check your Fiji and TrackMate
versions. The following versions were used and tested in this
script:
	• Fiji 2.14.0/1.54f/ Java 1.8.0 322 (64-bit)
	• TrackMate v7.13.2

By default this script produces six output files per processed image series. 
They conclude of two each of files with the names 
	”[channel-image series name] Spots.csv”,
	”[channel-image series name] Tracks.csv”, and
	”[channel-image series name] Overlay.tif”. 
”channel” refers to which channel this image was created from. It will be either C1 or C2 respectively. 
”image series name” refers to the name of the original file inside the input-folder.

The default export files for the .csv-files are currently set to TrackMate’s spot table (holds information about all spots assigned to tracks) and the track table (holds information about all tracks, like the amount of spots per track, that is not directly correlated to the individual spots’ data). 

There is an option to output the ”AllSpots” table as well. This table holds the same information as the spot table but includes all spots detected. This means it will also include the detected spots that were not assigned to a track by TrackMate. 
To output this table three # have to be removed in the code (Listing 1 on lines 160, 169 and 170). They are specified in comments within the script as well.

The output consists of four .csv-files (or maximum six per file if all tables should be exported) as well as two .tif-files each.
These .csv-files have just one column and use commas as separation characters. 
It does not use a character like ” or ’ to signify text. 
Some programs might split the .csv-file into a nicer table automatically. 
The .tif-file holds the visual data of Trackmate. 
It shows the original image series together with the TrackMate-made overlay for the spots and tracks.
