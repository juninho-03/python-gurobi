# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 17:12:22 2019
OSEP
@author: Victor Hinojosa
"""

# Copyright 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Power flow data for 4 bus, 2 gen case from Grainger & Stevenson.
"""

from numpy import array

def case3b_TCEP_multi():
    ppc = {"version": '2'}

    ##-----  Power Flow Data  -----##
    ## system MVA base
    ppc["baseMVA"] = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    ppc["bus_ini"] = array([
        [1, 3, 0,  30.99,  0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [2, 1, 0, 105.35, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [3, 1, 1*100, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [4, 1, 1*100, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9]
    ])
    ppc["bus_end"] = array([
        [1, 3, 0,  30.99,  0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [2, 1, 0, 105.35, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [3, 1, 1.5*100, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [4, 1, 2*100, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9]
    ])
    ppc["p_load"] = array([1.0, 0.5]) # load period factor   
    ppc["p_hours"] = array([8760]) # number of hours for each load period    
    ppc["T"] = 3

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    ppc["gen"] = array([
        [1, 0, 0, 100, -100, 1, 100, 1, 250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 100, -100, 1, 100, 1, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 0, 0, 100, -100, 1, 100, 1, 110, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    ## branch data
    #fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
    if False:
        ppc["branch"] = array([
            [1, 2, 0.01008, 0.1, 0.1025, 100, 250, 250, 0, 0, 1, -360, 360, 1, 10, 1],
            [1, 3, 0.00744, 0.2, 0.0775, 100, 250, 250, 0, 0, 1, -360, 360, 1,  4, 1],
            [2, 3, 0.01272, 0.3, 0.1275, 100, 250, 250, 0, 0, 1, -360, 360, 1,  8, 0],
            [1, 4, 0.01272, 0.2, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  9, 1],
            [2, 4, 0.01272, 0.1, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  6, 1],
            [3, 4, 0.01272, 0.1, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  5, 1]
        ])
    else:
        ppc["branch"] = array([
            [1, 2, 0.01008, 0.1, 0.1025, 100, 250, 250, 0, 0, 1, -360, 360, 1, 10, 0],
            [1, 3, 0.00744, 0.2, 0.0775, 100, 250, 250, 0, 0, 1, -360, 360, 1,  4, 1],
            [2, 3, 0.01272, 0.3, 0.1275, 100, 250, 250, 0, 0, 1, -360, 360, 1,  8, 0],
            #[1, 4, 0.01272, 0.2, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  9, 2],
            [2, 4, 0.01272, 0.1, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  6, 1],
            [3, 4, 0.01272, 0.1, 0.1275, 150, 250, 250, 0, 0, 1, -360, 360, 0,  5, 2]
        ])

    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    if False:
        ppc["gencost"] = array([
            [2, 1500, 0, 3, 0.005,  11.7,   213],
            [2, 2000, 0, 3, 0.009,  10.3,   200],
            [2, 3000, 0, 3, 0.007,  10.8,   240]
        ])
    else:
        ppc["gencost"] = array([
            [2, 1500, 0, 2, 10,   0],
            [2, 2000, 0, 2, 14,  0],
            [2, 3000, 0, 2, 8,  0]
        ])
            

    return ppc
