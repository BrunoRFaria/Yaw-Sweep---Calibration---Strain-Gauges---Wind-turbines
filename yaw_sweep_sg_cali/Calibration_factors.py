# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:54:13 2023

@author: brofa
"""
import numpy as np
from pathlib import Path
from yaw_sweep_sg_cali.SQL_utilities import slice_name_string_from
from datetime import datetime
import matplotlib.pyplot as plt


def get_cali_factors(data_all, file_name, warnings, plot=False):
    '''
    Adds information to a given dictionary of ys, with the expected
    calibration factors.
    Parameters
    ----------
    data_all : dict
        contains the information of the different ys identifies.
    file_name : str
        contains the file name of the turbine to be analyzed.
    warnings :  list
        Contains the initial and end name of the signals where the
        fiting function did not suceed to fit at all an sinus shape.
    plot : bool, optional
        if final plotted is wanted. The default is False.
    Returns
    -------
    dic : dict
        similar to the input dict, but now adding the generated calibration
        factors.
    '''
    # load data for analytical
    # offset in kNm  = 15953.44*offset
    # maxmment hanging = 15953.44*amp
    dic = {}
    # plotting over time
    folder_data = Path('Data')
    folder_package = Path.cwd().joinpath(folder_data)
    file = folder_package.joinpath(file_name)
    # analytical
    if file.exists():
        gain_ana = np.genfromtxt(file, dtype=float, skip_header=28)[0]
    else:
        print('\nThere is no .txt providing the analytical gains for the\
get_cali_factors.py to properly convert measured [mV/V] into\
[kNm]\n')
        return
    for n in range(len(data_all)):
        data = data_all['Yaw Sweep ' + str(n + 1)]
        data['offset_kNm'] = gain_ana*data['offset']
        data['max_kNm'] = gain_ana*abs(data['amp'])
        data['offset_kNm_unc'] = gain_ana*data['perr'][3]
        dic['Yaw Sweep '+str(n+1)] = data
    if plot:
        plotting_calibration_factors(dic, warnings)
    return dic


def plotting_calibration_factors(dic, warnings):
    '''
    Final plot of the calibration factors. Plot the main results
    (offset/amp and mean wind speed) together with their uncertanties
    and mean wind speed (strong assumption of low wind speed)
    Parameters
    ----------
    dic : dict
        contains the information of the different ys identifies together with
        the calibration factors of each.
    warnings : list
        Contains the initial and end name of the signals where the
        fiting function did not suceed to fit at all an sinus shape.

    Returns
    -------
    None.
    '''
    offset = []
    max_bm = []
    mw = []
    time = []
    std_offset = []
    for n in range(len(dic)):
        data = dic['Yaw Sweep '+str(n+1)]
        output_is_bad = check_warnings(warnings, data['name'])
        if not output_is_bad:
            offset.append(data['offset_kNm'])
            max_bm.append(data['max_kNm'])
            mw.append(data['mean_wind'])
            std_offset.append(data['offset_kNm_unc'])
            time_str = str(data['name'][0])
            YYYY, MM, DD, hh, mm = slice_name_string_from(time_str)
            time_date = datetime(YYYY, MM, DD, hh, mm)
            time.append(time_date)
    fig, ax = plt.subplots(1, clear=True, figsize=(15, 8))
    fig.suptitle('Calibration Factors for the MxTB', fontsize=18)
    fs_sub = 14
    fs_axis = 14
    ax.set_ylim([0, 2000])
    ax.plot(time, offset, 'k', label='offset')
    ax.plot(time, max_bm, 'k--', label='max amplitude')
    ax.legend(fontsize=fs_sub)
    plt.errorbar(time, offset,
                 yerr=std_offset,
                 fmt='o',
                 markersize=10,
                 elinewidth=2,
                 capsize=5)
    ax.set_ylabel('Calibration Factors [kNm]', fontsize=fs_axis)
    ax.set_xlabel('date [year-month]', fontsize=fs_axis)
    plt.gcf().autofmt_xdate()
    ax2 = ax.twinx()
    ax2.set_ylabel('Mean Wind Speed [m/s] ', color='blue')
    ax2.plot(time, mw, 'o', color='blue')
    ax2.set_ylim([0, 6])
    ax2.tick_params(axis='y', labelcolor='blue')
    plt.grid()
    plt.show()
    fig.tight_layout()
    return


def check_warnings(warnings, name):
    '''
    Function created to check whether the information in a given ys comes
    from a proper fitting sinus function or it failed. If failed, returns an
    output that neglect the given fitted information.
    Parameters
    ----------
    warnings : list
        Contains the initial and end name of the signals where the
        fiting function did not suceed to fit at all an sinus shape.
    name : list
        Contains the initial and end name of the specific ys signal.
    Returns
    -------
    output_is_bad : bool
        in case, True, the result should not be included in the final
        plot.
    '''
    output_is_bad = False
    for reference in warnings:
        if name[0] == reference[0] and name[1] == reference[1]:
            output_is_bad = True
    return output_is_bad
