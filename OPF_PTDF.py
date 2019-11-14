# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:43:35 2019
DC-based Optimal power flow (DCOPF) using PTDF
@author: Victor Hinojosa
"""

from gurobipy import *
from scipy.sparse import csr_matrix as sparse
from numpy import diag, ones, zeros, arange, ix_, r_, flatnonzero as find
from numpy.linalg import solve, inv
import numpy as np
import time
if False:
    import case3b as sep
    sep=sep.case3b()
else:
    import case6ww as mpc
    sep=mpc.case6ww()
#    import case57 as sep
#    sep=sep.case57()    
#    import case118 as mpc
#    sep=mpc.case118()

t00 = time.time() #formulation time

# SEP parameters

ng = len(sep['gen'])
nb = len(sep['bus'])
nl = len(sep['branch'])
b = 1 / sep['branch'][:,3] 
f = sep['branch'][:, 0]-1 # from
t = sep['branch'][:, 1]-1 # to
I = r_[range(nl), range(nl)]
S = sparse((r_[ones(nl), -ones(nl)], (I, r_[f, t])), (nl, nb))
Bf = sparse((r_[b, -b], (I, r_[f, t])),(nl,nb))
Bbus = S.T * Bf
slack_bus=find(sep['bus'][:,1]==3)
buses = arange(1, nb)
noslack = find(arange(nb) != slack_bus)
SF = zeros((nl, nb))
SF[:,noslack]=Bf[:, buses].todense()*inv(Bbus[ix_(noslack, buses)].todense()) 
#PTDF[:, noslack] = solve((Bbus[ix_(noslack, noref)].todense()).T, (Bf[:, noref].todense()).T ).T
PF_sl=np.dot(SF,sep['bus'][:,2].T) #Slack PF
rhs_1=-sep['branch'][:,5]-PF_sl #FM - Slack PF
rhs_2=-sep['branch'][:,5]+PF_sl

# Initializing model
m = Model('DCOPF_PTDF')
m.setParam('OutputFlag', False)

# VARIABLE DEFINITIONS
p = m.addVars(ng, vtype=GRB.CONTINUOUS, lb=0, name='Pg')
var_p = [p[i] for i in range(ng)] #array

# OPTIMIZATION PROBLEM
if sep['gencost'][0,3] == 2: #linear
    COp = quicksum(var_p*sep['gencost'][:,4])
    m.setObjective(COp, GRB.MINIMIZE)
else:
    Quad = 0 #quadratic
    for i in range(ng):
        Quad += sep['gencost'][i,4] * p[i] * p[i]
    COp = quicksum(var_p*sep['gencost'][:,5]) + sum(sep['gencost'][:,6])
    m.setObjective(Quad+COp, GRB.MINIMIZE)

# Nodal balance
m.addConstr(p.sum('*'),GRB.EQUAL,sum(sep['bus'][:,2]),'Balance')

# Transmission network 
pos_g = (sep['gen'][:,0]-1).astype(np.int64) # gen location
for i in range(nl):
    expr = quicksum(var_p * SF[i,pos_g])
    tx = str(int(sep['branch'][i,0])) + str(int(sep['branch'][i,1]))
    m.addConstr(-expr,GRB.GREATER_EQUAL,rhs_1[i],'f%sM' % tx)
    ff=m.addConstr(expr,GRB.GREATER_EQUAL,rhs_2[i],'f%sm' % tx)

for i in range(ng): #P min & P max
    m.addConstr(p[i],GRB.GREATER_EQUAL,sep['gen'][i,9],'Pmin%d' % sep['gen'][i,0])
    m.addConstr(-p[i],GRB.GREATER_EQUAL,-sep['gen'][i,8],'Pmax%d' % sep['gen'][i,0])

t11 = time.time()

# SOLVER & INFO
t2 = time.time() 
m.optimize()
t3 = time.time()
if False:
    m.write('DCOPF_PTDF.lp')       
status = m.Status
if status == GRB.Status.OPTIMAL:
    print ('Cost = %.2f ($/h)' % m.objVal)        
    if nb < 100:
        print ('Power generation solution (Pg):')          
        sol_p = m.getAttr('x', p) 
        for i in range(ng):
            if sol_p[i] > 1e-2:
                print('Pg[%.0f] = %.3f (MW)' % (sep['gen'][i,0], sol_p[i]))
        print ('Power flows:')  
        Cg = sparse((ones(ng), (sep['gen'][:,0]-1, range(ng))), (nb, ng)) #conection gen matrix
        PF=np.dot(SF,Cg*sol_p.values()-sep['bus'][:,2])
        for i in range(nl):
            print('f[%.0f-%.0f] = %.3f (MW)' % (sep['branch'][i,0], sep['branch'][i,1], PF[i]))
        print ('Lagrange multipliers:')
        for v in m.getConstrs():
            if v.pi > 1e-2:
                print('%s = %g ($/MWh)' % (v.ConstrName,v.pi))
    print('=> Formulation time: %.4f (s)'% (t11-t00))
    print('=> Solution time: %.4f (s)' % (t3-t2))
    print('=> Solver time: %.4f (s)' % (m.Runtime))
elif status == GRB.Status.INF_OR_UNBD or \
   status == GRB.Status.INFEASIBLE  or \
   status == GRB.Status.UNBOUNDED:
   print('The model cannot be solved because it is infeasible or unbounded => status "%d"' % status)
   sys.exit(1)   #1