# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 14:58:02 2019
Economic Dispatch
@author: Victor Hinojosa
"""

from gurobipy import *
import data_ED
import time

t00 = time.time() #formulation time

# EPS parameters
g = data_ED.generators()
d = data_ED.demand_sep
l_gen = list(g.keys())

# Initializing model
m = Model('ED')
m.setParam('OutputFlag', False)

# VARIABLE DEFINITIONS
p = m.addVars(l_gen, vtype=GRB.CONTINUOUS, lb=0, name='Pg') 

# OPTIMIZATION PROBLEM
# O.F.
f_obj = 0 
for i in l_gen:
    f_obj += g[i]['a']* p[i] * p[i] + g[i]['b'] * p[i] + g[i]['c']
m.setObjective(f_obj, GRB.MINIMIZE)
# s.t.
m.addConstr(p.sum('*'),GRB.EQUAL,d,'Balance')
for i in l_gen:
    m.addConstr(p[i],GRB.GREATER_EQUAL,g[i]['Pmin'],'Pmin[%d]' % i)
    m.addConstr(-p[i],GRB.GREATER_EQUAL,-g[i]['Pmax'],'Pmax[%d]' % i)

t11 = time.time()
# SOLVER
m.optimize()
status = m.Status
if status == GRB.Status.OPTIMAL:
    print ('Cost = %.2f ($/h)' % m.objVal)        
    print ('Decision variables')  
    for v in m.getVars():
        print('%s = %g (MW)' % (v.VarName, v.X))
    print ('Lagrange multipliers')
    for v in m.getConstrs():
        if v.pi > 0:
            print('%s = %g ($/MWh)' % (v.ConstrName,v.pi))
    print('=> Formulation time: %.4f (s)'% (t11-t00))
    print('=> Solver time: %.4f (s)' % (m.Runtime))
elif status == GRB.Status.INF_OR_UNBD or \
   status == GRB.Status.INFEASIBLE  or \
   status == GRB.Status.UNBOUNDED:
   print('The model cannot be solved because it is infeasible or unbounded => status "%d"' % status)
   sys.exit(1)   #1
if True:
    m.write('ED.lp')   