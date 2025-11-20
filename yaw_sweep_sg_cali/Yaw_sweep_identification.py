# -*- coding: utf-8 -*-
"""
Module for Yaw sweep identification functions to make life easier
"""
import numpy as np
import matplotlib.pyplot as plt
import calendar


def find_yaw_sweep_boolean(yaw_list, rot_list, pitch_list, ws_list):
    '''
    This function will read out a yaw array (1/60 Hz) and search for
    yaw sweeps operations based on rotor speed, pitch angle and the
    slope of the yaw.
    Parameters
    ----------
    yaw_list : list of numpy arrays
        yaw array for each month.
    rot_list : list of numpy arrays
        rotor array for each month.
    pitch_list : list of numpy arrays
        pitch array for each month.
    ws_list : list of numpy arrays
        wind speed array for each month.
    Returns
    -------
    yaw_sweep : boolean
        TRUE when yaw sweep is found, False otherwise.

    '''
    # I had to do that bcz list with numpy arrays of different sizes
    yaw = np.concatenate(np.array(yaw_list, dtype=object))
    rot = np.concatenate(np.array(rot_list, dtype=object))
    pitch = np.concatenate(np.array(pitch_list, dtype=object))
    ws = np.concatenate(np.array(ws_list, dtype=object))
    # Exclude NaN values and add zero as a replacer
    yaw = isNaN_update(yaw)
    rot = isNaN_update(rot)
    pitch = isNaN_update(pitch)
    ws = isNaN_update(ws)
    # First Mask: triggers to make calibration more robust
    mask_triggers = (rot == 0) & (pitch >= 85.5)\
        & (pitch <= 86.5)  # & (ws <=10)
    # decision not to include wind speed for now, and evaluate bending
    # moment even though wind speed might be high, and then afterwards take
    # a decision on how to come up with calibration factors
    # Second Mask: function to check the slope
    first_der = np.diff(yaw)
    first_der = np.insert(first_der, 0, 0)  # to be size consistent
    a = 25.75
    tolerance = 0.15
    mask_der = ((first_der >= a-tolerance) &
                (first_der <= a+tolerance)) | \
        ((first_der <= -(a-tolerance)) &
         (first_der >= -(a+tolerance)))
    # Combine first and second: final mask can be something
    # like mask = np.logical_and(mask1, mask2, mask3...)
    mask = np.logical_and(mask_triggers, mask_der)
    # Third mask: function that masks where
    # there are sequential clusters
    # with less than 6 values (1min signal
    # and half deltax is 6.5)
    mask_yaw_sweep = min_chunck_size(mask)
    # Final Adjustment to account to the fact
    # that yaw is polar, so for example,
    # from 360 it might "jump" to 0 and vice-versa,
    # so polar_jump is added
    yaw_sweep = polar_jump(mask_yaw_sweep)
    return yaw_sweep


def isNaN_update(num):
    '''
    Replace NaN values for zero, as it does not mislead results
    Parameters
    ----------
    num : array of float
        any array that might contain NaN values.
    Returns
    -------
    num : array of float
        array updated without NaN.
    '''
    for i in range(len(num)):
        if num[i] != num[i]:
            num[i] = 0
    return num


def get_name_scan_ys(name, scan_id, idx):
    '''
    Find the name and scan_id out from the indexes found for the data
    at 1/60Hz sampling frequency
    Parameters
    ----------
    name : list of numpy array
        each numpy array is names for each of the 1 month data.
    scan_id : list
        each numpy array is scan_ids for each of the 1 month data.
    idx : list
        contains the indexes, initial and end, for the found ys.
    Returns
    -------
    name_ys : array of int
        contains the a 2xn, where 2 is for the initial and end, and n
        is for the number of ys.
    scan_id_ys : array of int
        contains the a 2xn, where 2 is for the initial and end, and n
        is for the number of ys.

    '''
    name_array = np.concatenate(np.array(name, dtype=object))
    scan_id_array = np.concatenate(np.array(scan_id, dtype=object))
    name_ys = name_array[idx]
    scan_id_ys = scan_id_array[idx]
    return name_ys, scan_id_ys


def identify_yaw_sweep(sensors, partial_plot=False):
    '''
    Function created to read operational data from a turbine,
    find possible yaw sweep operations and output the time
    instances where the happen. Time instance can be precisely defined
    based on the name and scan_id of a point in the operational data.
    Parameters
    ----------
    sensors : tuble with lists
        Each list contains n number of numpy arrays, n equal to the number
        of months loaded.
        The sensors should include: name,
                                    scan_id,
                                    yaw,
                                    rotor speed,
                                    pitch,
                                    wind speed,
                                    bending moment
    partial_plot : bool, optional
        If true, plot the identified yaw sweeps. The default is False.
        Obs: we only plot in case one month is analayzed. Otherwise, the
        chart would not be clear.

    Returns
    -------
    name_ys : array of int
        contains the a 2xn, where 2 is for the initial and end name,
        and n is for the number of ys.
    scan_id_ys : array of int
        contains the a 2xn, where 2 is for the initial and end scan_id,
        and n is for the number of ys.
    numb_ys : int
        number of identified ys.

    '''
    name_list, scan_id_list, yaw_list, rot_list,\
        pitch_list, ws_list, MxTB_list = sensors
    mask = find_yaw_sweep_boolean(yaw_list, rot_list,
                                  pitch_list, ws_list)
    if partial_plot and len(name_list) == 1:
        plotting_yaw_sweep_identified(yaw_list,
                                      name_list, MxTB_list, mask)
    elif partial_plot and len(name_list) != 1:
        print("\nSorry my friend, but plotting function works if only \n \
               one month is requested at the input! :( \n")
    a = groupby_list(mask)
    idx_init = []
    idx_final = []
    for i in range(len(a)):
        if a[i][0]:
            idx_init.append(np.concatenate(a[0:i]).size)
            idx_final.append(np.concatenate(a[0:i+1]).size-1)
    idx = [idx_init, idx_final]
    name_ys, scan_id_ys = get_name_scan_ys(name_list, scan_id_list, idx)
    numb_ys = len(name_ys[0])
    return name_ys, scan_id_ys, numb_ys


def min_chunck_size(boolean):
    '''
    Checking clusters of True booleans and
    updating to False in case clusters
    has less than 6 elements
    Parameters
    ----------
    boolean :array of  bool
        boolean arary.
    Returns
    -------
    np.concatenate(clusters): array of bool
        boolean array.
    '''
    clusters = groupby_list(boolean)
    for i in range(len(clusters)):
        if clusters[i][0] and len(clusters[i]) < 6:
            clusters[i] = [False] * len(clusters[i])
    return np.concatenate(clusters)


def polar_jump(boolean):
    '''
    Since the yaw is a polar signal, it might jump from 360 to 0
    and the other way around.
    This function tries to account for that in case of consecutive
    ys.
    Parameters
    ----------
    boolean : array of bool
       boolean array.
    Returns
    -------
    np.concatenate(clusters): array of bool
       boolean array.
    '''
    clusters = groupby_list(boolean)
    for i in range(len(clusters)):
        if len(clusters[i]) == 1 and not clusters[i][0]:
            clusters[i] = [True]
    return np.concatenate(clusters)


def groupby_list(array):
    '''
    Function that groups consecutives False and True values in a
    boolean array
    Parameters
    ----------
    array : array of bool
    Returns
    -------
    [list(g) for _, g in groupby(array)]: list
        contains a list of consecutive boolean values.
    '''
    from itertools import groupby
    return [list(g) for _, g in groupby(array)]


def plotting_yaw_sweep_identified(yaw, name, MxTB, mask):
    '''
    Plot the partial results to help the user to visualize
    what is a yaw sweep and its behavior in the yaw and
    bending moment time series within one month of data.
    Parameters
    ----------
    yaw : list of numpy array
        yaw time series.
    name : list of numpy array
        name time series..
    MxTB : list of numpy array
        bending moment time series.
    mask : array of bool
        True when ys, False otherwise.
    Returns
    -------
    None.

    '''
    yaw = np.array(yaw).reshape(np.array(yaw).size,)
    name = np.array(name).reshape(yaw.size)
    MxTB = np.array(MxTB).reshape(yaw.size)
    # i = sum(mask)/yaw.size
    # perc_masked = f"{i:.4%}"
    # print(perc_masked)
    time_array = np.arange(1, name.size+1, 1)
    year_i = str(name[0])[0:4]
    year_f = str(name[-1])[0:4]
    month_i = calendar.month_name[int(str(name[0])[4:6])]
    month_f = calendar.month_name[int(str(name[-1])[4:6])]
    day_i = str(name[0])[6:8]
    day_f = str(name[-1])[6:8]
    initial = year_i + ' ' + month_i + ' ' + day_i
    final = year_f + ' ' + month_f + ' ' + day_f
    title_aux = 'From ' + initial + ' to ' + final + '\n '
    # + 'Percentage data filtered = '+perc_masked
    fig, ax = plt.subplots(3, 1, clear=True, figsize=(15, 8))
    fig.suptitle(title_aux, fontsize=18)
    fs_sub = 14
    fs_axis = 10
    ax[0].plot(time_array, yaw, color='b', label='Yaw Recording each 1min')
    ax[0].plot(time_array[mask], yaw[mask], 'x',
               markersize=20, color='r', label='Yaw Sweep')
    ax[0].set_ylabel('\u03B3 [°]', fontsize=fs_axis)
    # ax[0].set_xlabel('time [min]', fontsize=fs_axis)
    ax[0].grid()
    ax[0].legend(fontsize=fs_sub)
    plt.tight_layout()
    ax[0].set_title('Yaw', fontsize=fs_sub)
    ax[1].plot(time_array[mask], yaw[mask], 'x', markersize=20, color='r')
    ax[1].set_ylabel('\u03B3 [°]', fontsize=fs_axis)
    # ax[1].set_xlabel('time [min]', fontsize=fs_axis)
    ax[1].grid()
    ax[1].set_title('Yaw Sweep Zoom', fontsize=fs_sub)
    ax[2].plot(time_array[mask], MxTB[mask],
               'b-x', label='MxTB - 1min - recordings')
    ax[2].set_ylabel('Bending Moment Sensor Output [mV/V]', fontsize=fs_axis)
    ax[2].set_xlabel('time [min]', fontsize=fs_axis)
    ax[2].grid()
    ax[2].set_title('MxTB (masked)- Tower Bottom 324°-144° ', fontsize=fs_sub)
    fig.tight_layout()
    plt.show()
