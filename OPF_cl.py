# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 14:58:02 2019
DC-based Optimal power flow (DCOPF)
@author: Victor Hinojosa
"""

from gurobipy import *
from numpy import pi, flatnonzero as find 
import time
if False:
    import case3b as mpc
    sep=mpc.case3b()
else:
    import case6ww as mpc
    sep=mpc.case6ww()
    import case118 as mpc
    sep=mpc.case118()

t00 = time.time() #formulation time

# SEP parameters

ng = sep['gen'].shape[0]
nb = sep['bus'].shape[0]
nl = sep['branch'].shape[0]

b = 1 / sep['branch'][:,3] 
f = sep['branch'][:, 0]
t = sep['branch'][:, 1]

# Initializing model
m = Model('DCOPF_Cl')
m.setParam('OutputFlag', False)

# VARIABLE DEFINITIONS
p = m.addVars(range(ng), vtype=GRB.CONTINUOUS, lb=0, name='Pg')
f = m.addVars(range(nl), vtype=GRB.CONTINUOUS, ub=GRB.INFINITY,lb=-GRB.INFINITY,name='f')
delta = m.addVars(range(nb), vtype=GRB.CONTINUOUS, ub=pi,lb=-pi,name='delta')
#delta = m.addVars(range(nb), vtype=GRB.CONTINUOUS, ub=GRB.INFINITY,lb=-GRB.INFINITY,name='delta')

# OPTIMIZATION PROBLEM
f_obj = 0 # O.F.
for i in range(ng):
    if sep['gencost'][0,3] == 2:
        f_obj += sep['gencost'][i,4] * p[i] * sep['baseMVA'] #LP
    else:
        f_obj += sep['gencost'][i,4] * p[i] * p[i] * sep['baseMVA'] ** 2 + sep['gencost'][i,5] * p[i] * sep['baseMVA'] + sep['gencost'][i,6] #QP
m.setObjective(f_obj, GRB.MINIMIZE)
# s.t.
slack_bus=find(sep['bus'][:,1]==3)
m.addConstr(delta[int(slack_bus)],GRB.EQUAL,0,'SL') #Slack bus

for i in range(nb): #nodal balance LCK
    f_from=0; f_to=0;
    for j in range(nl):
        if sep['bus'][i,0]==sep['branch'][j,0]:
            f_from += f[j]
        if sep['bus'][i,0]==sep['branch'][j,1]:
            f_to += f[j]
    m.addConstr(p.sum(j for j in range(ng) if sep['bus'][i,0]==sep['gen'][j,0])-f_from+f_to,GRB.EQUAL,sep['bus'][i,2]/sep['baseMVA'],'BN%d' % sep['bus'][i,0])
for i in range(nl): #Line PF LVK #f min & max
    m.addConstr(f[i]-1/sep['branch'][i,3]*(delta[sep['branch'][i,0]-1]-delta[sep['branch'][i,1]-1]),GRB.EQUAL,0,'f%s' % str(int(sep['branch'][i,0])) + str(int(sep['branch'][i,1])))
    m.addConstr(f[i],GRB.GREATER_EQUAL,-sep['branch'][i,5]/sep['baseMVA'],'fmin%s' % str(int(sep['branch'][i,0])) + str(int(sep['branch'][i,1])))   
    m.addConstr(-f[i],GRB.GREATER_EQUAL,-sep['branch'][i,5]/sep['baseMVA'],'fmax%s' % str(int(sep['branch'][i,0])) + str(int(sep['branch'][i,1])))   
for i in range(ng): #P min & max
    m.addConstr(p[i],GRB.GREATER_EQUAL,sep['gen'][i,9]/sep['baseMVA'],'Pmin%d' % sep['gen'][i,0])
    m.addConstr(-p[i],GRB.GREATER_EQUAL,-sep['gen'][i,8]/sep['baseMVA'],'Pmax%d' % sep['gen'][i,0])

t11 = time.time()

# SOLVER & INFO
t2 = time.time() 
m.optimize()
t3 = time.time()
if False:
    m.write('DCOPF_Cl.lp')   
status = m.Status
if status == GRB.Status.OPTIMAL:
    print ('Cost = %.2f ($/h)' % m.objVal)      
    if nb < 100:
        print ('Decision variables:')  
        aux=0
        for v in m.getVars():
            if aux < ng+nl:
                print('%s = %.3f (MW)' % (v.VarName, v.X * sep['baseMVA']))
            else:
                break
            aux += 1
        print ('Lagrange multipliers:')
        for v in m.getConstrs():
            if v.pi > 1e-2:
                print('%s = %g ($/MWh)' % (v.ConstrName,v.pi / sep['baseMVA']))
    print('=> Formulation time: %.4f (s)'% (t11-t00))
    print('=> Solution time: %.4f (s)' % (t3-t2))
    print('=> Solver time: %.4f (s)' % (m.Runtime))
elif status == GRB.Status.INF_OR_UNBD or \
   status == GRB.Status.INFEASIBLE  or \
   status == GRB.Status.UNBOUNDED:
   print('The model cannot be solved because it is infeasible or unbounded => status "%d"' % status)
   sys.exit(1)   #1