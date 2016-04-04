#!/usr/bin/env python
#
#   opt.py
#
# Created:  2015/Jan/15
# Purpose:  A generic routine to optimize CG-lipid parameters
# Syntax:   opt.py configureFile
# Options:  
# Example:
# Notes:    Based on "framework-6.py" from Michalis
#
#  ------------------------------------------------------------------------- #

from __future__ import print_function

import subprocess
import sys
import scipy.optimize
from src.configuration import Configuration
from src.parameter import ParameterTable
from src.simulation import Simulation
from src.property import Property

import math
import numpy as np

# -------------------------------------------------------------------------- #

WELCOME_INFO = ("Nothing yet..."
                "\n"
                )


# -------------------------------------------------------------------------- #

if len(sys.argv) == 2:
    confFile = sys.argv[1]
elif len(sys.argv) == 1:
    confFile = 'config.sample'
else:
    print("Syntax: opt.py configureFile")
    sys.exit()


# Preparations
print(WELCOME_INFO)
cfg = Configuration()
cfg.read(confFile)

(
    optMethod,
) = cfg.get_config('optimization')
print("The \"%s\" optimizing method will be used.\n" % optMethod)

(
    initParaTableFile,
    paraTableFile,
    ffForSimulation,
    ffTemplate,
) = cfg.get_config('parameters')
print("Fetch initial parameters from \"%s\"." % initParaTableFile)
paraTableInitial = ParameterTable(initParaTableFile)
paraValuesInitial = paraTableInitial.current_parameter()
print("Optimized parameters will be saved in \"%s\".\n" % paraTableFile)
subprocess.call(
    "head -1 %s > %s" % (initParaTableFile, paraTableFile),
    shell=True
)
paraTable = ParameterTable(paraTableFile)


(
    mode,
    execFile,
    path,
    inFileName,
    processScript,
) = cfg.get_config('simulation')
print("Simulation will be performed in folder: %s.\n" % path)


(
    totalProperties,
    propertyNames,
    propertyRefs,
    propertySpecials,
) = cfg.get_config('properties')
if not int(totalProperties) == len(propertyNames):
    raise ValueError(
        '%s properties indicated, but %d given.' % (
            totalProperties, len(propertyNames)
        )
    )
properties = [''] * len(propertyNames)
for i, name in enumerate(propertyNames):
    if not name:
        name = "q_" + str(i + 1)
        print("Property%d name not set, Reset as \"%s\"." % (i + 1, name))
    properties[i] = Property(name)
    properties[i].reference = propertyRefs[i]
    properties[i].special = propertySpecials[i]
    # TODO @setter here?


# -------------------------------------------------------------------------- #

def simulation_flow(parameters):
    """ The sub-routine to be optimized. Take in a set of parameters, and
    return a targeted function value.

    type_parameters: float list
    rtype: float
    """
    paraTable.update_table(parameters)
    print("\n#---- Step %d -------------#\n" % paraTable.len)
    
  
    if mode=='test':
      
      y1=math.sin(parameters[0])**2+math.cos(parameters[1])**2+math.sin(parameters[2])**2
      y2=math.sin(parameters[0])**2+math.cos(parameters[1])**2+math.sin(parameters[2])**2
      y3=math.sin(parameters[0])**2+math.cos(parameters[1])**2+math.sin(parameters[2])**2
      y4=math.sin(parameters[0])**2+math.cos(parameters[1])**2+math.sin(parameters[2])**2
      propertyValues = np.array([y1,y2,y3,y4])
    else:       
      
      paraTable.write_datafile(
          paraTable.current_parameter(),
          dataFileOut=ffForSimulation,
          dataFileTemp=ffTemplate,
      )

      print("\nRunning Simulation...:")
      simulation = Simulation(path, inFileName)
      simulation.run(execFile)
      # TODO add config "Nthread" to control mpirun thread number.

      propertyValues = simulation.post_process(processScript)
      # propertyValues= ['70.8745', '29.7267', '1005.19', '1.146']
    

    print("Saving Property Values...")
    if not len(propertyValues) == int(totalProperties):
        raise ValueError(
            '%s target properties needed, but %d produced by simulation.' % (
                totalProperties, len(propertyValues)
            )
        )
    for _, p in enumerate(properties):
        p.value = str(propertyValues[_])
        p.update_property_list()

    print("\nCalculating Target Value...:")
    targetValue = sum([p.target_function() for p in properties])
    print("Current targeted value:", targetValue)

    return targetValue

# -------------------------------------------------------------------------- #

print("\nOptimizing...:")
optParaValues = scipy.optimize.minimize(
    simulation_flow,
    paraValuesInitial,
    method=optMethod,
    options={'disp': True,
             'maxiter': 100,
             'ftol': 0.0001,
             },
    # callback=callbackF,
)
