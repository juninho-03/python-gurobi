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

def case3b():
    ppc = {"version": '2'}

    ##-----  Power Flow Data  -----##
    ## system MVA base
    ppc["baseMVA"] = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    ppc["bus"] = array([
        [1, 1, 0,  30.99,  0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [2, 3, 100, 105.35, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [3, 1, 100, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
    ])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    ppc["gen"] = array([
        [1, 0, 0, 100, -100, 1, 100, 1, 100, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 100, -100, 1, 100, 1, 120, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 100, -100, 1, 100, 1, 150, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    ## branch data
    #fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
    ppc["branch"] = array([
        [1, 2, 0.01008, 0.1, 0.1025, 20, 250, 250, 0, 0, 1, -360, 360],
        [1, 3, 0.00744, 0.2, 0.0775, 100, 250, 250, 0, 0, 1, -360, 360],
        #[0, 2, 0.00744, 0.2, 0.0775, 100, 250, 250, 0, 0, 1, -360, 360],
        [2, 3, 0.01272, 0.3, 0.1275, 100, 250, 250, 0, 0, 1, -360, 360]
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
            [2, 1500, 0, 2, 60,   0],
            [2, 2000, 0, 2, 100,  0],
            [2, 3000, 0, 2, 190,  0]
        ])
            

    return ppc
