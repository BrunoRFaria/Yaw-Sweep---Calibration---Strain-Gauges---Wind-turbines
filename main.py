# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:10:59 2023

@authors: brofa and zjaf
"""
from yaw_sweep_sg_cali.Load_data import (get_SQL_1_min,
                                         get_SQL_50_Hz)

from yaw_sweep_sg_cali.Yaw_sweep_identification import identify_yaw_sweep

from yaw_sweep_sg_cali.Curve_fitting import curve_fitting_ys

from yaw_sweep_sg_cali.Calibration_factors import get_cali_factors

# %% User Input -> year/month from/to

start = (2018, 1)
stop = (2022, 5)

turbine_file = 'V52_inputs.txt'

# %% First Data loading (SQL or Local)

data_1_min = get_SQL_1_min(start, stop)

# %% Identifying the Yaw Sweep (ys) instants based on name and scan_id

name_ys, scan_id_ys, numb_ys = identify_yaw_sweep(data_1_min,
                                                  partial_plot=True,
                                                  )

# %% Second Data Loading (SQL or Local) for calibration factors

data_50_Hz = get_SQL_50_Hz(name_ys)

# %% Fitting Sinus to extract max, min, mean, errs of curve fitting

fitted_curve_outputs, warnings = curve_fitting_ys(numb_ys, data_50_Hz,
                                                  name_ys, scan_id_ys,
                                                  partial_plot=True,
                                                  )

# %% Calibration Factors (offset,gain,windspeed)

calibration_factors = get_cali_factors(fitted_curve_outputs,
                                       turbine_file,
                                       warnings,
                                       plot=True,
                                       )
