# -*- coding: utf-8 -*-
"""
Module for curve fitting
"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def cutting_signal(initial_name, initial_scan_id, end_name, end_scan_id,
                   name_ys_wanted, scan_id_ys_wanted, signal):
    '''
    Function that remove from the load data, the initial and end boundaries
    so to improve the sinus fitting routine performance and avoid errors
    Parameters
    ----------
    initial_name : int
        intiial point name to be cutted.
    initial_scan_id : int
        intiial point scan_id to be cutted.
    end_name : int
        end point name to be cutted.
    end_scan_id : int
        end point scan_id to be cutted.
    name_ys_wanted : array of int
        contains all the name from the loaded data.
    scan_id_ys_wanted : array of int
        contains all the scan_id from the laoded data.
    signal : array of float
        contains the signal to be cutted.
    Returns
    -------
    cutted_signal : array of float
        contains the signal cutted.
    list
        contains the indexes of the cutting.
    '''
    cut_init = np.where((name_ys_wanted == initial_name) &
                        (scan_id_ys_wanted == initial_scan_id))[0][0]
    cut_final = np.where((name_ys_wanted == end_name) &
                         (scan_id_ys_wanted == end_scan_id))[0][0]
    cutted_signal = signal[cut_init:cut_final]
    return cutted_signal, [cut_init, cut_final]


def fit_sin(time_array, y, initial_name, end_name):
    '''
    Fit sin to the input time sequence, and return fitting
    parameters.
    Parameters
    ----------
    time_array : array of float
        artificial time array for the given signal.
    y : array of float
        sinusoidal siganl to be fitted with pure sinus.
    initial_name : int
        in case, fitting does not succeed, information of the ys
        will be saved.
    end_name : int
        in case, fitting does not succeed, information if the ys
        will be saved.
    Returns
    -------
    dict
        contains information of the fitted sinus such as amp, offset,
        phase,
        omega but also the fitting routine errors/performance indexes.
    err_fitting : list
        contains all the ys intervals where the fitting function did
        not work.
    '''
    err_fitting = []
    # computing the frequencies associated
    # with the Fourier transform of a signal.
    # assume uniform spacing
    ff = np.fft.fftfreq(len(time_array), (time_array[1]-time_array[0]))
    # absolute value Fourier transform
    Fy = abs(np.fft.fft(y))
    # Compute an initial guess for the frequency of the signal using the
    # frequency associated with the maximum amplitude
    # in the Fourier transform of y
    # excluding the zero frequency "peak", which is related to offset
    guess_freq = abs(ff[np.argmax(Fy[1:])+1])
    guess_amp = np.std(y)*2.**0.5
    guess_offset = np.mean(y)
    p0 = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])
    def sinfunc(t, A, w, p, c): return A * np.sin(w*t + p) + c
    try:
        popt, pcov = curve_fit(sinfunc, time_array, y, p0=p0)
        A, w, p, c = popt
    except RuntimeError:
        print('\nPlease check the bending moment signal between\n'
              + str(initial_name) + ' and ' + str(end_name) +
              '\n The fit function did not found apropriate sinus\
              function\n')
        A, w, p, c = 1, 1, 1, 1
        popt = (A, w, p, c)
        pcov = np.ones([4, 4])
        err_fitting = [initial_name, end_name]
    f = w/(2.*np.pi)
    perr = np.sqrt(np.diag(pcov))
    def fitfunc(t): return A * np.sin(w*t + p) + c
    # Calculating Residuals
    residuals = y - sinfunc(time_array, *popt)
    # Calculate the root mean square error (RMSE)
    rmse = np.sqrt(np.mean(residuals**2))
    # Calculate the coefficient of determination (R-squared)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - (ss_res/ss_tot)
    return {"max": c+A, "min": c-A, "offset": -c, "amp": A,
            "omega": w, "phase": p,
            "freq": f, "period": 1./f,
            "fitfunc": fitfunc, "maxcov": np.max(pcov),
            "rawres": (p0, popt, pcov),
            "RMSE": rmse, "R-Squared": r_squared,
            "perr": perr}, err_fitting


def curve_fitting_ys(numb_ys, data_ys, name_ys,
                     scan_id_ys, partial_plot=False):
    '''
    The goal is to fit sinus functions automatically into noisy data from
    identified ys and extract relavant information from the fitted curve
    and from the fitting routine performance.
    Parameters
    ----------
    numb_ys : int
        Number of identified yaw sweeps in the given time range.
    data_ys : tuple containing lists of numpy array
        Lists with len of numb_ys
        containing: bending moment, scan_id, name and wind speed
        all in 50 Hz data for each ys.
    name_ys : array of int
        The initial and end point name of each ys.
    scan_id_ys : array of int
        The initial and end point scan_id of each ys.
    partial_plot : bool, optional
        In case user wants to visualize the fitting routine for each ys.
        The default is False.

    Returns
    -------
    dic_ys : dict
        Kew words refer to a yaw sweep
        Inside dict contain the main information of the signal fitted and
        the error/performance of the fitting function.
    warnings : list
        Contains the initial and end name of the signals where the
        fiting function did not suceed to fit at all an sinus shape.
    '''
    dic_ys = {}
    MxTB_all_ys = data_ys[0]
    scan_id_all_ys = data_ys[1]
    name_all_ys = data_ys[2]
    ws_all_ys = data_ys[3]
    count = True
    warnings = []
    for n in range(numb_ys):
        MxTB_noisy = MxTB_all_ys[n]
        initial_name = name_ys[0][n]
        initial_scan_id = scan_id_ys[0][n]
        end_name = name_ys[1][n]
        end_scan_id = scan_id_ys[1][n]
        time_noisy = np.arange(0, int(MxTB_noisy.size)/50, 0.02)
        MxTB_cutted, idx = cutting_signal(initial_name, initial_scan_id,
                                          end_name, end_scan_id,
                                          name_all_ys[n],
                                          scan_id_all_ys[n],
                                          MxTB_noisy)
        time_cutted = np.arange(time_noisy[idx[0]],
                                time_noisy[idx[1]], 0.02)
        dic_one_ys, warnings_ys = fit_sin(time_cutted,
                                          MxTB_cutted,
                                          initial_name,
                                          end_name)
        dic_one_ys['mean_wind'] = np.mean(ws_all_ys[0][idx[0]:idx[1]])
        dic_one_ys['TI'] = np.std(ws_all_ys[0]
                                  [idx[0]:idx[1]]) / dic_one_ys['mean_wind']
        dic_one_ys['name'] = [name_ys[0][n], name_ys[1][n]]
        dic_ys['Yaw Sweep ' + str(n + 1)] = dic_one_ys
        if partial_plot and numb_ys <= 20:
            plotting_curve_fitting(MxTB_noisy, time_noisy,
                                   time_cutted, dic_one_ys, idx)
        elif partial_plot and numb_ys > 20 and count:
            print("\nSorry my friend, the curve_fitting_ys\n\
function would generate too many\n\
yaw sweeps plots,try only one\n\
month at a time for the sake\n\
of plotting! :( \n")
            count = False
        if len(warnings_ys) != 0:
            warnings.append(warnings_ys)
    return dic_ys, warnings


def plotting_curve_fitting(signal_noisy, time_noisy,
                           time_fitted, dic_one_ys, idx):
    '''
    Plotting function to visually compare the raw signal with the
    fitted sinus.
    Parameters
    ----------
    signal_niosy : array of float
        contains the raw signal.
    time_noisy : array of float
        artificial time array .
    time_fitted : array of float
        artificial time array for the sliced signal.
    dic_one_ys : dic
        contain the information of the fitted ys.
    idx : list
        indexes of the fitted sinus within the raw signal.

    Returns
    -------
    None.

    '''
    time_array_noisy = np.arange(0, int(signal_noisy.size)/50, 0.02)
    amp = dic_one_ys['amp']
    omega = dic_one_ys['omega']
    phase = dic_one_ys['phase']
    offset = dic_one_ys['offset']
    signal_fitted = amp * np.sin(omega * time_fitted + phase) - offset
    title_from = str(dic_one_ys['name'][0])
    title_to = str(dic_one_ys['name'][1])
    title_aux = 'Fitting noisy signals with sinusoidal\
                 shape \n From file '\
        + title_from + ' to ' + title_to
    fig, ax = plt.subplots(1, clear=True, figsize=(15, 8))
    fig.suptitle(title_aux, fontsize=18)
    fs_sub = 14
    fs_axis = 10
    ax.plot(time_noisy, signal_noisy, color='k', label='Noisy Signal')
    ax.plot(time_fitted, signal_fitted, 'r', label='Fitted Sinus')
    ax.plot(time_noisy[idx], signal_noisy[idx], '*',
            color='r', markersize=35, label='Fitting limits')
    ax.set_ylabel('Bending Moment [mV/V]', fontsize=fs_axis)
    ax.set_xlabel('time [s]', fontsize=fs_axis)
    ax.grid()
    ax.legend(fontsize=fs_sub)
    plt.tight_layout()
    fig.tight_layout()
    plt.show()
    return
