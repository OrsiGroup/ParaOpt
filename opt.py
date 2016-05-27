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
# -------------------------------------------------------------------------- #

from __future__ import print_function

import math
import subprocess
import sys
# import scipy.optimize
from src.minimize import minimize
import numpy as np
from src.configuration import Configuration
from src.parameter import ParameterTable
from src.simulation import Simulation
from src.property import Property


# -------------------------------------------------------------------------- #

def welcome():
    print("Nothing yet...")
    print("\n")

def get_cmd_arg():
    """ Get the command line arguments and pass it to main programs.

    r_type: str
    """
    if len(sys.argv) == 2:
        return sys.argv[1]
    else:
        print("Syntax: opt.py configureFile")
        sys.exit()

def print_info(argDict):
    """ Print on screen the table of configs read from the input file.
    """
    l = 20
    print("%s |%s" %("ATTRIBUTE".center(l), "VALUE".center(l)))
    print("-" * 2 * (l + 1))
    for key in sorted(argDict):
        print("%s |%s"
              %(key.ljust(l), argDict[key].rjust(l)))
    print("-" * 2 * (l + 1), "\n")

# -------------------------------------------------------------------------- #

def initialize_parameters(inTable, outTable, ffFile=None, ffTemp=None):
    """ Initialize input/output PT (parameter table) objects and read input 
    parameters.
 
    type_inTable: str
    type_outTable: str
    rtype: (float list, PT object)
    """
    paraTableInitial = ParameterTable(inTable)
    paraValuesInitial = paraTableInitial.current_parameter()
    subprocess.call(
        "head -1 %s > %s" % (inTable, outTable),
        shell=True,
    )
    paraTable = ParameterTable(outTable, datafile=ffFile, datatemp=ffTemp)
    
    nDim = len(paraValuesInitial)
    paraArrayInitial = np.empty((nDim + 1, nDim))
    paraArrayInitial[0] = paraValuesInitial
    nonzdelt = 1.05
    zdelt = 0.00025
    for k in range(0, nDim):
        y = np.array(paraValuesInitial, copy=True)
        if y[k] != 0:
            y[k] *= nonzdelt
        else:
            y[k] = zdelt
        paraArrayInitial[k + 1] = y
    return paraArrayInitial, paraTable
    
def initialize_properties(nameList, refList, specList, n):
    """ Initialize targeted property objects, given the list of input property
    names (nameList), references (refList), specials(specList), and the total
    number of total properties (n).
    
    type_nameList: str list
    type_n: int
    rtype: property object list
    """
    if not len(nameList) == n:
        raise ValueError(
            '%s properties indicated, but %d given.' % (n, len(nameList))
        )
    properties = [''] * n
    for i, name in enumerate(nameList):
        if not name:
            name = "q_" + str(i + 1)
            print("Property %d name not set, Reset as \"%s\"." % (i + 1, name))
        properties[i] = Property(name)
        properties[i].reference = refList[i]
        properties[i].special = specList[i]
    return properties


def test_flow(x, xt, y):
    """ Testing sub-routine.
    x: parameters
    xtable: the table to be written every step.
    y: targeted properties
    
    type_x: float list
    type_xtable: parameterTable object
    type_y: property object list
    rtype: float
    """
    print("\n#---- Step %d -------------#\n" % xt.len)
    xt.update_table(x)
    
    yTargetedValues = [math.sin(x[0])**2 +
                       math.cos(x[1])**2 +
                       math.sin(x[2])**2] * len(y)
    yTargetedValues = [str(value) for value in yTargetedValues]

    print("Saving Property Values...")
    for yn, value in zip(y, yTargetedValues):
        yn.value = value
        yn.update_property_list()

    print("\nCalculating Target Value...:")
    targetValue = sum([yn.target_function() for yn in y])
    print("Current targeted value:", targetValue)

    return targetValue

def simulation_flow(x, xtable, sim, y):
    """ The sub-routine to be optimized. 
    x: parameters
    xtable: the parameter table to be written every step
    sim: the simulation to be run
    y: targeted properties
    
    type_x: float list
    type_xtable: parameterTable object
    type_sim: simulation object
    type_y: property object list
    rtype: float
    """
    print("\n#---- Step %d -------------#\n" % xtable.len)
    xtable.update_table(x)
    xtable.write_datafile(xtable.current_parameter())

    print("\nRunning Simulation...:")
    sim.run(execute)
    propertyResults = sim.post_process()

    print("Saving Property Values...")
    if not len(propertyResults) == len(y):
        raise ValueError(
            '%s target properties needed, but %d produced by simulation.' % (
                len(y), len(propertyResults)
            )
        )
    for yn, value in zip(y, propertyResults):
        yn.value = value
        yn.update_property_list()

    print("\nCalculating Target Value...:")
    targetValue = sum([yn.target_function() for yn in y])
    print("Current targeted value:", targetValue)

    return targetValue
    
if __name__ == "__main__":

    welcome()

    confFile = get_cmd_arg()
    cfg = Configuration()
    cfg.read(confFile)
    #TODO no need a class.
    
    (
        optMethod,
    ) = cfg.get_config("optimization")
    (
        initParaTableFile,
        paraTableFile,
        ffForSimulation,
        ffTemplate,
    ) = cfg.get_config('parameters')
    (
        mode,
        execute,
        path,
        processScript,
    ) = cfg.get_config('simulation')
    (
        totalProperties,
        propertyNames,
        propertyRefs,
        propertySpecials,
    ) = cfg.get_config('properties')

    INFO_DICT = {
        "Optimization Method": optMethod,
        "Parameters Input"   : initParaTableFile,
        "Parameters Output"  : paraTableFile,
        "Simulation Folder"  : path,
        "Post-Process"       : processScript,
    }
    print_info(INFO_DICT)

    (
        paraArrayInitial, 
        paraTable,
    ) = initialize_parameters(initParaTableFile, paraTableFile,
                             ffFile=ffForSimulation, ffTemp=ffTemplate)
    properties = initialize_properties(propertyNames, propertyRefs,
                                       propertySpecials, int(totalProperties))
    simulation = Simulation(path, processScript)
    
    # ----------------------------------------------------------------------- #
    def test_flow_with_1_arg(p):
        return test_flow(p, paraTable, properties)
    
    def simulation_with_1_arg(p):
        return simulation_flow(p, paraTable, simulation, properties)
        
    #TODO wrap this part as a function and give 'func' as input?
    print("\nOptimizing...:")
    if mode == "test":
        func = test_flow_with_1_arg
    elif mode == "simulation":
        func = simulation_with_1_arg

    optParaValues = minimize(
        func,
        paraArrayInitial,
        method=optMethod,
        options={'disp': True,
                 'maxiter': 100,
                 'ftol': 0.0001,
        },
        # callback=callbackF,
    )
