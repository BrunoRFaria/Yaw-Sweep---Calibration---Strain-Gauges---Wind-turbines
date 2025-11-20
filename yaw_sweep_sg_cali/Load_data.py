"""
Created on Tue Apr 18 09:43:12 2023

@author: brofa

Functions to help to access 1 min data and full SG recordings
"""
from pathlib import Path
import numpy as np
import pandas as pd
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from yaw_sweep_sg_cali.SQL_utilities import (inputs_SQL, get_data_from_SQL,
                                             get_time_series,
                                             slice_name_string_from,
                                             slice_name_string_to)


def get_table_name(start, stop):
    """
    Generate a list of table names that contain the
    data wanted within a given time frame.
    Parameters
    ----------
    start : tuple of int
        A tuple containing the start year
        and month in the format (YYYY, MM).
    stop : tuple of int
        A tuple containing the stop year and
        month in the format (YYYY, MM). The table name for
        the stop month is not included in the list.
    Returns
    -------
    table_name : list of str
        A list of table names to access the SQL
        database for the wanted months or to load
        data locally if available.
    """
    start_aux = date(start[0], start[1], 1)
    stop_aux = date(stop[0], stop[1], 1)
    table_name = []
    while start_aux < stop_aux:
        table_name.append('caldata_{}_{}_50hz'.format(
                str(start_aux.year),
                str(start_aux.month).zfill(2)))
        start_aux += relativedelta(months=1)
    return table_name


def get_SQL_1_min(start, stop):
    '''
    Retrieves 1-minute data from an
    SQL database or local files.
    This function retrieves 1-minute
    data from an SQL database or from local
    files if available. If local files are not available,
    the function accesses the SQL database and saves the
    data in the correct format for future use. The data is
    organized by month, and each month takes approximately
    5-10 minutes to load from the SQL database, but less
    than a second to load from local files.
    Parameters
    ----------
    start : tuple of int
        A tuple containing the year and
        month to start data retrieval.
    stop : tuple of int
        A tuple containing the year and month
        to stop data retrieval (non-inclusive).
    Returns
    -------
    compiled : tuple of lists
        A tuple containing several lists of numpy
        arrays, each list corresponding to a different
        month of data. The following sensor data is
        included in each numpy array: name, scan_id,
        yaw, rotor speed, pitch, wind speed, and bending moment.
    '''
    lst_tablename = get_table_name(start, stop)
    # Variables wanted
    name = []
    scan_id = []
    yaw = []
    pitch = []
    rot = []
    ws = []
    MxTB = []
    count = 0
    for tablename in lst_tablename:
        YYYY = tablename.split('_')[1]
        MM = calendar.month_name[int(tablename.split('_')[2])]
        file_name = '{}_{}_V52_data_1min.txt'.format(YYYY, MM)
        folder_file = Path('V52_1min_data')
        folder_data = Path('Data')
        folder_package = Path.cwd().joinpath(folder_data)
        folder_complete = folder_package.joinpath(folder_file)
        file = folder_complete.joinpath(file_name)
        if file.exists():
            name_m, scan_id_m, yaw_m, yaw_err_m, pitch_m, rot_m, ws_m, MxTB_m\
                = np.loadtxt(file, dtype={'names': ('col1', 'col2', 'col3',
                                                    'col4', 'col5', 'col6',
                                                    'col7', 'col8'),
                                          'formats': (np.int64, np.int64,
                                                      np.float64, np.float64,
                                                      np.float64, np.float64,
                                                      np.float64, np.float64)},
                             skiprows=1, unpack=True)
        else:
            if count == 0:
                I = inputs_SQL()
                count += 1
                # cnx = SQLconnect(I)
            downsampling = str(50*60)  # from 50Hz to 1min
            df = get_data_from_SQL(I['user'], I['password'],
                                   '*', I['database'],
                                   ['yaw', 'Wdir_41m', 'WS',
                                    'ROT', 'pitch', 'MxTB', 'name', 'scan_id'],
                                   tablename, I['host'],
                                   ['`scan_id`%'+downsampling+'=0'])
            MxTB_m = df['MxTB'].to_numpy()
            yaw_m = df['yaw'].to_numpy()
            ws_m = df['WS'].to_numpy()
            pitch_m = df['pitch'].to_numpy()
            rot_m = df['ROT'].to_numpy()
            scan_id_m = df['scan_id'].to_numpy()
            Wdir_41m_m = df['Wdir_41m'].to_numpy()
            name_m = df['name'].to_numpy()
            yaw_err_m = yaw_m - Wdir_41m_m
            compiled_saving = (name_m, scan_id_m, yaw_m, yaw_err_m,
                               pitch_m, rot_m, ws_m, MxTB_m)
            saving_1_min_data(compiled_saving)
        name.append(name_m)
        scan_id.append(scan_id_m)
        yaw.append(yaw_m)
        pitch.append(pitch_m)
        rot.append(rot_m)
        ws.append(ws_m)
        MxTB.append(MxTB_m)
    compiled = (name, scan_id, yaw, rot, pitch, ws, MxTB)
    return compiled


def get_SQL_50_Hz(name_ys):
    """Get SQL data in a 50Hz base.
    This function loads data from SQL database
    and saves it locally, if it
    is not already available. In case data is
    already available locally,
    the code loads it. The difference from the
    `get_SQL_50_Hz` function is
    that it loads data only when a ys exists.
    Parameters
    ----------
    name_ys : array of int
        Contains a 2xn, where 2 is for the
        initial and end name,
        and n is for the number of ys.
    Returns
    -------
    compiled : tuple with lists
        Each list contains n number of numpy arrays,
        n equal to the number
        of months loaded. The sensors include bending
        moment, name, scan_id,
        and wind speed.
    Notes
    -----
    Each +- 30 min of data takes around
    1 min to load from SQL
    and less than a second from local.
    """
    tablename = 'caldata_{}_{}_50hz'
    MxTB_all_ys = []
    name_all_ys = []
    scan_id_all_ys = []
    ws_all_ys = []
    count = 0
    for n in range(len(name_ys[0])):
        name_from = name_ys[0, n]
        name_to = name_ys[1, n]
        file_name = '{}_to_{}_V52_data_50Hz.txt'.format(name_from, name_to)
        folder_file = Path('V52_50Hz_data')
        folder_data = Path('Data')
        folder_package = Path.cwd().joinpath(folder_data)
        folder_complete = folder_package.joinpath(folder_file)
        file = folder_complete.joinpath(file_name)
        if file.exists():
            name_sliced, scan_id_sliced, MxTB_sliced, ws_sliced =\
                np.loadtxt(file, dtype={'names': ('col1', 'col2',
                                                  'col3', 'col4'),
                                        'formats': (np.int64,
                                                    np.int64,
                                                    np.float64,
                                                    np.float64)},
                           skiprows=1, unpack=True)
        else:
            start = slice_name_string_from(str(name_from))
            stop = slice_name_string_to(str(name_to))
            timestamps = get_time_series(start, stop)
            if count == 0:
                I = inputs_SQL()
                count += 1
            df = get_data_from_SQL(I['user'], I['password'],
                                   timestamps, I['database'],
                                   ['MxTB', 'name', 'scan_id', 'WS'],
                                   tablename, I['host'])
            MxTB_sliced = df['MxTB'].to_numpy()
            scan_id_sliced = df['scan_id'].to_numpy()
            name_sliced = df['name'].to_numpy()
            ws_sliced = df['WS'].to_numpy()
            compiled_saving = (name_sliced, scan_id_sliced,
                               MxTB_sliced, ws_sliced)
            saving_50_Hz_data(compiled_saving, name_from, name_to)
        MxTB_all_ys.append(MxTB_sliced)
        scan_id_all_ys.append(scan_id_sliced)
        name_all_ys.append(name_sliced)
        ws_all_ys.append(ws_sliced)
    compiled = (MxTB_all_ys, scan_id_all_ys, name_all_ys, ws_all_ys)
    return compiled


def saving_1_min_data(sensors_to_be_saved):
    """
    This function saves 1-minute data per
    month in order to reduce time spent accessing SQL.
    The data includes necessary variables
    to identify the Yaw Sweep.
    Parameters
    ----------
    sensors_to_be_saved : tuple
        A tuple with lists, where each list contains
        n number of numpy arrays.
        The sensors should include the following
        variables: name, scan_id, yaw,
        rotor speed, pitch, wind speed, and
        bending moment. n is equal to the number
        of months loaded.
    Returns
    -------
    None
    """
    name, scan_id, yaw, yaw_err, pitch, rot, ws, MxTB = sensors_to_be_saved
    num_col = len(sensors_to_be_saved)
    final_output = np.empty((name.size, num_col))
    # Add values to the empty array
    final_output[:, 0] = name
    final_output[:, 1] = scan_id
    final_output[:, 2] = yaw
    final_output[:, 3] = yaw_err
    final_output[:, 4] = pitch
    final_output[:, 5] = rot
    final_output[:, 6] = ws
    final_output[:, 7] = MxTB
    year_i = str(name[0])[0:4]
    month_i = calendar.month_name[int(str(name[0])[4:6])]
    # Creating a directory only for the first
    output_file = year_i + '_' + month_i + '_V52_data_1min.txt'
    output_path1 = 'Data'
    output_path2 = 'V52_1min_data'
    folder_package = Path.cwd().joinpath(output_path1)
    folder_package.mkdir(exist_ok=True)
    output_path = folder_package.joinpath(output_path2)
    output_path.mkdir(exist_ok=True)
    output = output_path.joinpath(output_file)
    # Setting the header of the output
    header = 'Name(-)\tscan_id(-)\tyaw(deg)\tyaw_err(deg)\
    \tpitch(deg)\tROT(rpm)\tWS(m/s)\tMxTB(mV/V)'
    np.savetxt(output, final_output,
               fmt=("%d", "%d", "%.3f", "%.3f",  "%.2f",
                    "%.2f", "%.2f", "%.8f"), header=header,
               delimiter='\t', comments='')
    return


def saving_50_Hz_data(sensors_to_be_saved, name_from, name_to):
    """
    Create a saving function to be used once,
    since accessing the SQL is time-consuming.
    The goal is to store 50Hz data for all ys identified.

    Parameters
    ----------
    sensors_to_be_saved : tuple with lists
        Each list contains n number of numpy arrays, n equal to the number
        of months loaded. The sensors should include:
        - bending moment,
        - name,
        - scan_id,
        - wind speed.
    name_from : int
        Starting name index for the saved data.
    name_to : int
        Ending name index for the saved data.

    Returns
    -------
    None.

    """
    name, scan_id, MxTB, ws = sensors_to_be_saved
    num_col = len(sensors_to_be_saved)
    final_output = np.empty((name.size, num_col))
    # Add values to the empty array
    final_output[:, 0] = name
    final_output[:, 1] = scan_id
    final_output[:, 2] = MxTB
    final_output[:, 3] = ws
    output_file = '{}_to_{}_V52_data_50Hz.txt'.format(name_from, name_to)
    output_path1 = 'Data'
    output_path2 = 'V52_50Hz_data'
    folder_package = Path.cwd().joinpath(output_path1)
    folder_package.mkdir(exist_ok=True)
    output_path = folder_package.joinpath(output_path2)
    output_path.mkdir(parents=True, exist_ok=True)
    output = output_path.joinpath(output_file)
    # Setting the header of the output
    header = 'Name(-)\tscan_id(-)\tMxTB(mV/V)\tws(m/s)'
    np.savetxt(output, final_output, fmt=("%d", "%d",
                                          "%.8f", "%.2f"), header=header,
               delimiter='\t', comments='')
    return
