"""
Created on Wed Aug 28 14:19:06 2019
DC-based TCEP using PTDF
@author: Victor Hinojosa
"""

from gurobipy import *
from scipy.sparse import csr_matrix as sparse
from scipy.sparse import identity as sparseI
from numpy import pi, append, array, ones, zeros, arange, ix_, r_, flatnonzero as find
from numpy.linalg import inv
import numpy as np
import time

t00 = time.time() #formulation time

if False:
    import case3b_TCEP as mpc
    sep=mpc.case3b_TCEP()
else:
    import Garver as mpc
    sep=mpc.Garver()
    #import case6ww as mpc
    #sep=mpc.case6ww()
    #import case118 as mpc
    #sep=mpc.case118()

# Initializing model
m = Model('TCEP_PTDF')
#m.Params.MIPGap=1e-6
m.Params.OutputFlag=0 #m.setParam('OutputFlag', False)

# SEP parameters
tE = 8760
M=2*pi*sep['baseMVA']
ng = len(sep['gen'])
nb = len(sep['bus'])
nl = len(sep['branch'])
#total
b = 1 / (sep['branch'][:,3] / (sep['branch'][:,13]+sep['branch'][:,15]))
f = sep['branch'][:, 0]-1
t = sep['branch'][:, 1]-1
I = r_[range(nl), range(nl)]
S = sparse((r_[ones(nl), -ones(nl)], (I, r_[f, t])), (nl, nb))#total
Bf = sparse((r_[b, -b], (I, r_[f, t])), (nl,nb))
Bbus = S.T * Bf
slack_bus=find(sep['bus'][:,1]==3)
buses = arange(1, nb)
noslack = find(arange(nb) != slack_bus)
SF_aux = zeros((nl, nb))
SF_aux[:,noslack]=Bf[:, buses].todense()*inv(Bbus[ix_(noslack, buses)].todense()) 
SF = zeros((nl, nb))
for i in range(nb):
    SF[:,i]=SF_aux[:,i]/ (sep['branch'][:,13]+sep['branch'][:,15])
PF_sl=np.dot(SF,sep['bus'][:,2].T) #Slack PF
rhs_1=-sep['branch'][:,5]-PF_sl #FM - Slack PF
rhs_2=-sep['branch'][:,5]+PF_sl
#exiting
pos_le = find(sep['branch'][:,13]==1)
nle = len(pos_le)
#new
pos_ln_aux = find(sep['branch'][:,15]!=0)
nln_aux = len(pos_ln_aux)
pos_ln = []
for i in range(nln_aux):
    for j in range(int(sep['branch'][pos_ln_aux[i],15])):
        pos_ln.append(pos_ln_aux[i])
n_var = len(pos_ln)        
f = sep['branch'][pos_ln, 0]-1 #new
t = sep['branch'][pos_ln, 1]-1
In = r_[range(n_var), range(n_var)]
Cf = sparse((r_[ones(n_var), -ones(n_var)], (In, r_[f, t])), (n_var, nb)) # S new lines
PTDFe = SF[pos_le] * Cf.T 
PTDFn = SF[pos_ln] * Cf.T 

# VARIABLE DEFINITIONS
p = m.addVars(range(ng), vtype=GRB.CONTINUOUS, lb=0, name='Pg') #power unit generation
var_p = [p[i] for i in range(ng)]
n = m.addVars(range(n_var), vtype=GRB.BINARY, name='n') #investment decitions
var_n = [n[i] for i in range(n_var)]
fv = m.addVars(range(n_var), vtype=GRB.CONTINUOUS, ub=M, lb=-M, name='fv') #investment decitions
var_fv = [fv[i] for i in range(n_var)]

# OPTIMIZATION PROBLEM - OF
COp = tE* quicksum(var_p*sep['gencost'][:,4])
CInv = quicksum(var_n*sep['branch'][pos_ln,14])

m.setObjective(COp/1e6+CInv, GRB.MINIMIZE)

# s.t.
m.addConstr(sum(var_p),GRB.EQUAL,sum(sep['bus'][:,2]),'Balance') # Nodal balance

for i in range(nle): # existing power flows 
    expr1 = quicksum(var_p*SF[pos_le[i],sep['gen'][:,0]-1])
    expr2 = quicksum(var_fv*PTDFe[i])
    tx = str(int(sep['branch'][pos_le[i],0])) + str(int(sep['branch'][pos_le[i],1]))
    m.addConstr(-expr1-expr2,GRB.GREATER_EQUAL,rhs_1[pos_le[i]],'fe%sm' %  tx)
    m.addConstr(expr1+expr2,GRB.GREATER_EQUAL,rhs_2[pos_le[i]],'fe%sM' % tx)

I_PTDF = sparseI(n_var) - PTDFn
for i in range(n_var): # future power flows 
    expr1 = quicksum(var_p*SF[pos_ln[i],sep['gen'][:,0]-1])
    aux=array(I_PTDF[i])
    expr2 = quicksum(var_fv*aux[0])
    tx = str(int(sep['branch'][pos_ln[i],0])) + str(int(sep['branch'][pos_ln[i],1]))
    m.addConstr(expr1-expr2+sep['branch'][pos_ln[i],5]*n[i],GRB.GREATER_EQUAL,PF_sl[pos_ln[i]],'fv%sm' %  tx)
    m.addConstr(-expr1+expr2+sep['branch'][pos_ln[i],5]*n[i],GRB.GREATER_EQUAL,-PF_sl[pos_ln[i]],'fv%sM' %  tx)

for i in range(n_var): #Fv min & max
    m.addConstr(-fv[i]-M*n[i],GRB.GREATER_EQUAL,-M,'fv2_m%s' % i)
    m.addConstr(fv[i]-M*n[i],GRB.GREATER_EQUAL,-M,'fv2_M%s' % i)

for i in range(ng): #P min & P max
    m.addConstr(p[i],GRB.GREATER_EQUAL,sep['gen'][i,9],'Pmin%d' % sep['gen'][i,0])
    m.addConstr(-p[i],GRB.GREATER_EQUAL,-sep['gen'][i,8],'Pmax%d' % sep['gen'][i,0])

t11 = time.time()

# SOLVER & INFO
t2 = time.time() 
m.optimize()
t3 = time.time()

if True:
    m.write('TCEP_PTDF.lp')      
status = m.Status
if status == GRB.Status.OPTIMAL:
    print ('Cost = %.2f ($MM) => CInv = %.2f & COp = %.2f' % (m.objVal,CInv.getValue(),COp.getValue()/1e6))        
    if nb < 100:
        print ('New investment decisions:') 
        sol_n = m.getAttr('x', n)
        for i in range(n_var):
            if sol_n[i] != 0:
                print('n[%.0f-%.0f] = %.3f' % (sep['branch'][pos_ln[i],0], sep['branch'][pos_ln[i],1], sol_n[i]))
        print ('Power generation solution (Pg):')  
        sol_p = m.getAttr('x', p)
        for i in range(ng):
            if sol_p[i] != 0:
                print('Pg[%.0f] = %.3f (MW)' % (sep['gen'][i,0], sol_p[i]))
        sol_fv = m.getAttr('x', fv)
        print ('Existing power flows:')  
        Cg = sparse((ones(ng), (sep['gen'][:,0]-1, range(ng))), (nb, ng)) #conection gen matrix
        PF = np.dot(SF[pos_le],Cg*sol_p.values()-sep['bus'][:,2]) + np.dot(PTDFe,sol_fv.values())
        for i in range(nle):
            print('f[%.0f-%.0f] = %.3f (MW)' % (sep['branch'][pos_le[i],0], sep['branch'][pos_le[i],1], PF[i]))    
        print ('Investment power flows:')  
        PF = np.dot(SF[pos_ln],Cg*sol_p.values()-sep['bus'][:,2]) + np.dot(PTDFn,sol_fv.values())
        for i in range(n_var):
            if sol_n[i] != 0:
                print('f[%.0f-%.0f] = %.3f (MW)' % (sep['branch'][pos_ln[i],0], sep['branch'][pos_ln[i],1], PF[i]))    
    print('=> Formulation time: %.4f (s)'% (t11-t00))
    print('=> Solution time: %.4f (s)' % (t3-t2))
    print('=> Solver time: %.4f (s)' % (m.Runtime))
#    fixed = m.fixed()
#    fixed.optimize()
#    print ('Lagrange multipliers:')
#    for v in fixed.getConstrs():
#        if v.pi > 1e-2:
#            print('%s = %g ($/MWh)' % (v.ConstrName,v.pi))
elif status == GRB.Status.INF_OR_UNBD or \
   status == GRB.Status.INFEASIBLE  or \
   status == GRB.Status.UNBOUNDED:
   print('The model cannot be solved because it is infeasible or unbounded => status "%d"' % status)
   sys.exit(1)   #1