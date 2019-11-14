#!/usr/bin/env python
# coding: utf-8

# # Economic dispatch problem (ED)

# \begin{alignat*}{1}\min\quad & 60 Pg_{1} + 100 Pg_{2} + 190 Pg_{3}\\
# \text{Subject to} \quad & Pg_{1} + Pg_{2} + Pg_{3} = 200\\
#  & 10 \leq Pg_{1} \leq 100\\
#  & 50 \leq Pg_{2} \leq 120\\
#  & 40 \leq Pg_{3} \leq 150\\
#  & Pg_{i} \geq 0 \quad\forall i \in \{1,2,3\}\\
# \end{alignat*}

# Se necesita primero cargar la librería que permite utilizar los objectos de Gurobi en Python.

# In[ ]:


from gurobipy import *


# Puede ser útil iniciar el reloj de la computadora para determinar el tiempo de formulación del problema de optimización.

# In[ ]:


import time
t00 = time.time() #formulation time


# Para poder leer el archivo donde se encuentra la información del SEP y de la función de costo del problema se realiza lo siguiente:

# In[ ]:


import case3b as mpc
sep=mpc.case3b()


# Para representar la cantidad de generadores y la red de transmisión a través de la matriz de incidencia, la matriz Ybus (Xbus), debemos definir los parámetros del SEP.

# In[ ]:


ng = len(sep['gen'])
nb = len(sep['bus']) #aplicable para A (incidencia)
nl = len(sep['branch']) #aplicable para A


# Inicializamos en Python el problema de optimización utilizando el objeto "Model" de Gurobi. 
# 
# (*) Hay veces que es útil resetear el problema, especialmente cuando estamos actualizando la FO o las restricciones, y en algunos al aplicar técnicas de descomposición. En Spyder es muy útil hacerlo ya que las variables y objetos de la Terminal de Python pueden estar aún disponibles ocasionando errores en la formulación del problema.

# In[ ]:


m = Model('ED')
m.reset(0)


# La definición de variables se realiza a través del comando "addVars" de la API de Python. Esto permite añadir múltiples variables de decisión al modelo de optimización. 
# 
# Para el caso mostrado se ha definido el dominio de las variables como números reales positivos. En el caso que no se definan estos Gurobi asume por default que son números reales positivos $[0,+inf[$. Para este caso, si bien se podría utilizar las características técnicas de las unidades generadoras, esto haría que no se muestren los multiplicadores de Lagrange asociados a los límites de las variables de decisión.
# 
# Para mayor información y detalle de todas las características de Gurobi se puede utilizar la información contenida en el siguiente link:
# https://www.gurobi.com/documentation/8.0/refman/py_python_api_details.html

# In[ ]:


# VARIABLE DEFINITIONS
p = m.addVars(ng, vtype=GRB.CONTINUOUS, lb=0, name='Pg') #diccionario


# Gurobi asigna una clase de Python denominada diccionario (tupledict: https://www.gurobi.com/documentation/8.0/refman/py_tupledict.html#pythonclass:tupledict). Los keys del diccionario son derivados de los índices del argumento, para este caso $ng$ (range($ng$)).
# 
# (*) Se debe recordar que en Python la secuncia de números enteros empieza con el cero.

# Es posible asignar el detalle de las variables de decisión a un arreglo (array). Esto con el objetivo de hacer más eficiente la formulación del problema, tanto para la FO como para las restricciones.

# In[ ]:


var_p = [p[i] for i in range(ng)] #array


# Con la definición anterior, la FO se formula como una combinación lineal de las variables de decisión (array) y el vector de los costos de generación. En el ejemplo se ha definido un arreglo a través del comando "quicksum" de Gurobi.
# 
# El resultado lo hemos asignado a un arreglo $Cop$ que define los costos de operación (FO) del problema del ED. Esto permitiría que a la componente de costo creada previamente podamos imprimirla, o utilizarla de acuerdo a nuestra conveniencia (inversión, operación, ENS, etc.).
# 
# Para plantear la FO se utiliza la definición del tipo de problema utilizando de la librería de Gurobi los comandos GRB.MINIMIZE y GRB.MAXIMIZE.

# In[ ]:


# OPTIMIZATION PROBLEM - OF
COp = quicksum(var_p*sep['gencost'][:,4])
m.setObjective(COp, GRB.MINIMIZE)


# Si bien se puede utilizar un lazo iterativo para ir acumulando el costo de cada generador, cuando formulamos problemas de gran dimensión es más eficiente utilizar este tipo de operación.

# Siempre es útil mostrar si lo que hemos formulado está correcto. Para el caso de la función objetivo se utiliza el comando es "getObjetive()".

# In[ ]:


m.getObjective() 
# m.update() #es necesario a veces actualizar


# El problema está sujeto a un conjunto de restricciones (igualdad y desigualdad), las cuales pueden ser definidas de acuerdo a la librería que tiene Gurobi como: GRB.EQUAL, GRB.GREATER_EQUAL, etc. 
# 
# Se puede también utilizar el símbolo que muestra el tipo de restricción (==, >=, <=). Incluso, se puede asociar un nombre a cada restricción. El objetivo es mostrar con nombres las restricciones formuladas (diccionario), asímismo es útil mostrar esta información cuando se formula el problema lineal (archivo LP) o entregar información de los precios sombras asociados al nombre de la restrición. Sino no se entrega esta información, las variables y restricciones aparecerán con nombres genéricos de Gurobi.
# 
# (*) A mi criterio es mejor utilizar estas definiciones, pensando en generalizar la modelación del problema en cualquier lenguaje de programación (Ansi C o C++).

# Para este caso el conjunto de restricciones es el siguiente:
# 
# * Balance de potencia:

# In[ ]:


# s.t.
m.addConstr(p.sum('*'),GRB.EQUAL,sum(sep['bus'][:,2]),'Balance')


# * Características técnicas de los generadores:

# In[ ]:


# P min & P max
for i in range(ng):
    m.addConstr(p[i],GRB.GREATER_EQUAL,sep['gen'][i,9],'Pmin%d' % sep['gen'][i,0])
    m.addConstr(-p[i],GRB.GREATER_EQUAL,-sep['gen'][i,8],'Pmax%d' % sep['gen'][i,0])


# Notar que al nombre de la restricción podemos agregarle información respecto al elemento (generador) que estamos limitando. Esto se puede realizar con el símbolo de porcentaje (%). Dependiendo del tipo de restricción, se puede asignar números enteros (%d) o cadena de caracteres (%s).

# En el caso que deseamos mostrar la formulación de estas restricciones podemos iterar en el conjunto de restricciones con el comando "getConstrs", y obtener cualquier restricción formulada. De la misma manera no olvidar que se crea la restricción desde el cero.
# 
# Con las siguientes instrucciones se pueden mostrar dos formas de poder acceder a su formulación matemática.

# In[ ]:


# show constraints
for c in m.getConstrs():
  print m.getRow(c)
xx=m.getConstrs()
print(m.getRow(xx[0]))


# Para calcular el tiempo de formulación del problema de optimización debemos asignar a una nueva variable la información del tiempo (reloj). Por lo que, el tiempo se podría calcularía como la diferencia de ambas variables.

# In[ ]:


t11 = time.time()


# La resolución del problema se realiza a través de la instrucción "optimize".

# In[ ]:


# SOLVER & INFO
t2 = time.time()
m.optimize()
t3 = time.time()


# Para comparar con la información de Gurobi, se procederá a iniciar el reloj antes y despues de la resolución del problema de optimización.

# Si queremos mostrar el archivo *.LP (linear problem):

# In[ ]:


if True:
    m.write('ED.lp')


# Es util asignar a una variable el tipo de solución encontra. Así podríamos determinar si la solución es óptima, infactible o no acotada.

# En las siguientes línea de texto se presenta información relacionada con la solución óptima:
# 
# * El costo de la FO.
# * Las variables de decisión.
# * Los precios sombra asociados a las restricciones.

# In[ ]:


status = m.Status
if status == GRB.Status.OPTIMAL:
    print ('Cost = %.2f ($) / COp = %.2f' % (m.objVal,COp.getValue()))
    # primera forma
    print ('Decision variables (Pg):')
    for v in m.getVars():
        print('%s = %g (MW)' % (v.VarName, v.X))
    # segunda forma
    print ('Decision variables (Pg):')    
    sol_p = m.getAttr('x', p)
    for i in range(ng):
        print('Pg[%.0f] = %.3f (MW)' % (sep['gen'][i,0], sol_p[i]))
    # shadow prices
    print ('Lagrange multipliers')
    for v in m.getConstrs():
        if v.pi > 0:
            print('%s = %g ($/MWh)' % (v.ConstrName,v.pi))

