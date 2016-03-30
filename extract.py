import scipy.optimize
import numpy as np
import math

expRho=0.997 # g/cm^3
expGamma=71.73 # mN/m
expComp=45.3 # 10^-6 1/bar
expDiff=2.3 # 10^-9 m^2/s
F0 = np.array([expRho,expGamma,expComp,expDiff])

sigma0=8.0
epsilon0=0.40
mu0=2.00
rcut0=2
x0 = np.array([sigma0,epsilon0,mu0])

optMethod='Nelder-Mead' # Optimization algorithm

def norm(f):
  global F0
  res=0.0
  for i in range(0,f.shape[0]):
    res += (f[i]-1.0)*(f[i]-1.0)
  return res

def testFunc(x):
  #time.sleep(0.5)
  y1=math.sin(x[0])**2+math.cos(x[1])**2+math.sin(x[2])**2
  y2=math.sin(x[0])**2+math.cos(x[1])**2+math.sin(x[2])**2
  y3=math.sin(x[0])**2+math.cos(x[1])**2+math.sin(x[2])**2
  y4=math.sin(x[0])**2+math.cos(x[1])**2+math.sin(x[2])**2

  print (np.array([y1,y2,y3,y4]))
  print (x)
  print ("#-----------------------------------------")
  print ("\n")
  return np.array([y1,y2,y3,y4])  

def optFunction(x):
  F = testFunc(x)
  F_DLess=F/F0
  normValue=norm(F_DLess)
  ### Save results in global variables to avoid unneccary calling of function ###
  functionResult=F_DLess
  return normValue

print("\nOptimizing...:")
optParaValues = scipy.optimize.minimize(
    optFunction,
    x0,
    method=optMethod,
    options={'disp': True,
             'maxiter': 100,
             'ftol': 0.0001,
             },
)
