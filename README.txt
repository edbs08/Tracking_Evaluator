******************************************************
******  	VIDEO TRACKING EVALUATOR       *******
******              PPKE - UAM - UB            *******
******************************************************

----------------------------------------------------------
		SET UP
----------------------------------------------------------
******** Pre-requisites:
Make sure to have the following python libraries installed:
	-wget
	-shapely
	-PyQt5
	-pyhtgen
	-dominate
	-opencv
For optional functions install:
	-pylatex - to generate latex report
	-scipy - to download otb and read results from .mat files.

To set up the environment in linux, user can run the pip install commands in accompanying 'requirements.txt', some variations on this may be required for windows.

******** User should create two folders called "squences" and "interface", where the corresponding sequences and trackers for the analysis should be added.
----------------------------------------------------------
		HOW TO RUN
----------------------------------------------------------
In console go to the path of the main.py file and run:
python main.py

When the evaluator is first run, user is provided the option of downloading some data for comparison. This allows the automated download of some online benchmark results and groundtruth - OTB and VOT. This will allow the download of the VOT sequences and results(although for the results it is much faster to download the zip file corresponding to the challenge year at the below link and add it to the directory of the evaluator) and the download of some of the OTB benchmark results from 2013. The sequences must be downloaded separately although they are not necessary to run the evaluator. For custom data the user should add at least a groundtruth.txt file to the corresponding sequence folder and a results file labelled {sequence name}_001.txt to the corresponding tracker folder following the same directory structure as with the automated download.

http://www.votchallenge.net/

----------------------------------------------------------
		RESULTS
----------------------------------------------------------
**** Output Results are visible in the file:
evaluation_results.html

