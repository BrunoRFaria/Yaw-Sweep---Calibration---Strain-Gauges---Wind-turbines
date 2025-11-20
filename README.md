# V52 Tower Strain Gauges Calibration

## Installation:

```
**update on 02/05 :(**

on the repo folder:
pip install -e .

instead of:
pip install yaw-sweep-sg-cali

Note: Python 3.8 is the minimum requirement version. 

```
Note: In case there is no [Data](https://gitlab.windenergy.dtu.dk/brofa/v52-strain-gauge-calibration/-/tree/main/Data) already available and V52 is the wanted turbine, remember to connect to DTU VPN.
Note2: A "Data" folder is then needed, with high frequency strain gauges signals in one subfolder and lower frequency yaw angle (e.g. 1 min data) in another subfolder. If Yaw is not available, one can avoid it, but the identification of Yaw sweeps will take longer as all parked conditions will be tried.


## Project Overview:

Tower strain gauges are commonly used in wind turbine applications to measure the strain on the tower or structure. To ensure accurate readings, it is important to regularly calibrate these gauges. This project aims to develop an automatic routine to generate strain gauge calibration factors (offset and gain) for a given amount of input time-series, considering the zero drift. The validation of the recordings will be pursued through specific idling operations, so called **Yaw Sweeps**. 

Basically, ***Yaw Sweeps*** are idling operations that might happen for the sake of detwisting the power cable of a wind turbine from time to time (if necessary). As you can see, such operations are not intrinsically related to any kind of calibration routine. However, due the quite linear yaw rotation speed presented during the yaw sweeps, where the turbine is shut down (low wind speeds, zero rotor speed and blades fully pitched), the aerodynamic contributions to the bending moment at the turbine tower are negligible and the only contribution to the bending should be structural (Center of Mass misalignment). And hopefully, the turbine mass is not changing. And by so, the measurements of bending should be constant.

Strain gauges, as stresses measuring devices (and by consequence bending moment) are known for presenting zero-drift over their lifetime. So, we expect, to generate calibration factors that could correct for such offset but also check for the amplitude of the measurements.


## Repo files 

- ***main.py*** is an example applied for DTU V52 using around 4 years of data. The code is built so that it can be used for different time ranges (from 2018 to 2022). From april 2022 on, we faced some problems still unknown to access the V52 SQL database. 
- ***yaw_sweep_sg_cali*** contains the modules from the package that are to calibrate strain gauges in a given wind turbine tower.
- ***how_to_use.ipynb*** is a Jupyter notebook with an input of only one month. This will facilitate the user to understand the code and  visualize two partial results: the yaw sweep identification and the curve fitting.
- ***Data*** contains already loaded and saved DTU V52 SQL data(1 min and 50Hz) that will be used (using also Load_data.py). The idea is to save time and help the user to visualize the functioning of the package. This will be further commented below.


## The research wind turbine V52

The research wind turbine V52 from Vestas is situated at DTU Risø Campus as a part of the row of wind turbines at the fjord. The 850 kW wind turbine arrived at DTU in 2015.- [DTU Wind and Energy Systems](https://wind.dtu.dk/Facilities/The-research-wind-turbine-V52) 

- Database:

To perform the project the databases used to test (SQL):

	- SCADA data from V52 and data from Risø met mast.
	- Strain measures from V52 tower 
	
- Package stepwise:

First, identify yaw sweep operations, in which the aerodynamic contribution to the tower bending moment is negligible (low wind speed). Secondly, using such operations, automatically curve fits the raw bending moment signal and extracts relavant information, as max, min, and mean values. Finally, generate recommended calibration factors (offsets). The number of yaw sweeps operation throughout a year is unknown. 

# Lets start running the code :) 

We strongly recommend you to start with the [Jupyter Notebook](https://gitlab.windenergy.dtu.dk/python-at-risoe/spp-2023/group_4_shaking_hands/-/blob/main/Final_Project/Yaw_Sweep_SG_Calibration.ipynb) to learn how to use the package. 

Afterwards, the **main.py** description below can further facilitate the usage of the package together with the types of inputs and outputs on each major function, based on their respective docstrings.

## main.py: Getting Started - How it works

***Please make sure to have the "Data" folder as in the repo if you want to run a first trial for the V52 turbine. Since, if not included, the code will ask for V52 DTU SQL login information (which you might have as a DTU colleague). Anyhow, each month of data can take around 5min to be loaded from the database. For the sake of testing, we provided the already loaded and saved operational data for both 1min and 50Hz cases. But feel free to remove data and test the SQL routines***

The package includes four main modules:

- ***Load_data.py***: for loading the 1-minute and 50Hz data from SQL or local source and save it (if SQL).
- ***Yaw_sweep_identification.py***: for identifying the yaw sweep instants based on the linear behavior of the yaw; and triggers of rotor speed and blade pitch.
- ***Curve_fitting.py***: for fitting sinusoidal curves to the bending moment (strain gauge) while in a yaw sweep operation to extract max, min, mean, and error values.
- ***Calibration_factor.py***: for calculating the calibration factors (offset, gain, and wind speed) for the yaw sensors in kNm.


In the following section, we will provide a detailed explanation of the main.py file.

 

### Step 1: User Input

The following variables are required to be defined by the user:

- start: A tuple 

of the form (year, month) representing the start time period for analysis.

- stop: A tuple 

of the form (year, month) representing the end time period for analysis.

- turbine_file: 

The name of the file containing turbine data that will be used for calibration factors.

### Step 2: First Data loading (SQL or Local)(get_SQL_1_min)

 This code loads data either from a local source or from an SQL database. It uses the function get_SQL_1_min(start, stop) from the module yaw_sweep_sg_cali.Load_data.
 
#### Inputs

- start: A tuple 

representing the start date and time for the data to be loaded in the format (year, month).

- stop: A tuple 

representing the stop date and time for the data to be loaded in the format (year, month).

#### Outputs

- data_1_min: A pandas DataFrame 

containing the loaded data.

**Note:**
 The specific source of the data (local or SQL) is determined by the implementation of the get_SQL_1_min() function, and is not directly controlled by the user through these inputs

### Step 3: Identifying the Yaw Sweep (ys) instants based on name and scan_id (identify_yaw_sweep)

This code line identifies the Yaw Sweep (ys) instants based on the input data data_1_min. It returns three variables name_ys, scan_id_ys, and numb_ys.

#### Inputs

- sensors : tuble with lists

Each list contains n number of numpy arrays, n equal to the number of months loaded.

The sensors should include: name, scan_id, yaw, rotor speed, pitch, wind speed, bending moment.

- partial_plot : bool, optional

If true, plot the identified yaw sweeps. The default is False.

Obs: we only plot in case one month is analayzed. Otherwise, the
chart would not be clear.

***Note***

If the input is less than three months, the program will execute successfully. However, if the input exceeds three months, the program will display a message to the user indicating that it cannot visualize the results for such a large timeframe. This is simply to help users understand the limitations of the program 

#### Outputs

- name_ys : array of int

contains the a 2xn, where 2 is for the initial and end name, and n is for the number of ys.

- scan_id_ys : array of int

contains the a 2xn, where 2 is for the initial and end scan_id, and n is for the number of ys.

- numb_ys : int

number of identified ys

### Step 4: Second Data Loading (SQL or Local) for calibration factors(get_SQL_50_Hz)

Retrieves 1-minute data from an SQL database or local files. This function retrieves 1-minute data from an SQL database or from local files if available. If local files are not available, the function accesses the SQL database and saves the data in the correct format for future use. The data is organized by month, and each month takes approximately 5-10 minutes to load from the SQL database, but less than a second to load from local files.
   
#### Inputs

- start : tuple of int

containing the year and month to start data retrieval.

- stop : tuple of int

containing the year and month to stop data retrieval (non-inclusive).

#### Outputs

- data_50_Hz: a pandas DataFrame 

containing the 50Hz yaw sweep data.

### Step 5: Fitting Sinus to extract max, min, mean, errs of curve fitting(curve_fitting_ys)

The curve_fitting_ys function in this module fits a sinusoidal curve to the yaw sweep data and returns the maximum, minimum, mean, and error values. The input parameters for this function are:

#### Inputs

- data_50_Hz: An array of intdata 

with 50 Hz sampling frequency.

- name_ys: a string 

specifying the name of the yaw sweep.

- scan_id_ys: A string 

specifying the scan id of the yaw sweep.

- partial_plot: A boolean

 specifying whether or not to plot partial results.

#### Outputs

 dic: A dictionary 
 
 containing the fitted curve outputs and warnings.

## Step 5:Calibration Factors (offset,gain,windspeed)(get_cali_factors)

This script is designed to calculate calibration factors for a wind turbine based on data collected during yaw sweeps. The script requires several input parameters, and the output is a set of calibration factors that can be used to improve the accuracy of wind speed measurements.

### Inputs

- data_all : A dictionary

 contains the information of the different ys identifies.
 
- file_name : A string 

contains the file name of the turbine to be analyzed.

- warnings : A list 

Contains the initial and end name of the signals where the fiting function did not suceed to fit at all an sinus shape.

- plot : A bool

 optional if final plotted is wanted. The default is False.

### Outputs

dic : A dictionary 

similar to the input dict, but now adding the generated calibration factors.

***Note***: the dictionary contains way more nice information than the plotting functions can handle for now. More in progress.

## Authors and acknowledgment

- Thanks to [Mikkel Friis-Møller](https://gitlab.windenergy.dtu.dk/V52/V52) that provided some of the functions inside the module [SQL_utilities.py](https://gitlab.windenergy.dtu.dk/python-at-risoe/spp-2023/group_4_shaking_hands/-/blob/main/Final_Project/yaw_sweep_sg_cali/SQL_utilities.py).

- DTU for the V52 SQL data.

## License
This code is licensed under the MIT License.

## Improvements performed from first submission to final submission

- The code was made more robust, adding safety features to avoid the code did not run due to mistakes or missunderstandings. For this, some functions were created to avoid errors and ensure the code run as expected.  
- The code was check with pycodestyle, to ensure was properly with the recommended standards. 
- PEP 257 information added to each function

## Peer Review
