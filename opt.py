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
import scipy.optimize
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
    ATTR_DICT = {
        0: "Optimization Method",
        1: "Input Parameters",
        2: "Output Parameters",
        3: "Simulation Folder",
        4: "Post-Process",
    }
    l = 20
    print("%s |%s" %("ATTRIBUTE".center(l), "VALUE".center(l)))
    print("-" * 2 * (l + 1))
    for key in ATTR_DICT:
        print("%s |%s"
              %(ATTR_DICT[key].ljust(l), argDict[key].rjust(l)))
    print("-" * 2 * (l + 1))

# -------------------------------------------------------------------------- #

def initialze_parameters(inFileName, outFileName):
    """ Initialize input/output PT (parameter table) objects and read input 
    parameters.
 
    type_inFileName: str
    type_outFileName: str
    rtype: (float list, PT object)
    """
    paraTableInitial = ParameterTable(inFileName)
    paraValuesInitial = paraTableInitial.current_parameter()
    subprocess.call(
        "head -1 %s > %s" % (inFileName, outFileName),
        shell=True,
    )
    paraTable = ParameterTable(outFileName)
    return paraValuesInitial, paraTable
    
def initialze_properties(nameList, n):
    """ Initialize targeted property objects, given the list of input property
    names (nameList) and the indicated total number of total properties (n).
    
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
        properties[i].reference = propertyRefs[i]
        properties[i].special = propertySpecials[i]
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
    xt.update_table(x)
    print("\n#---- Step %d -------------#\n" % xt.len)

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

def simulation_flow(x, xt, ffFile):
    """ The sub-routine to be optimized. 
    x: parameters
    xt: the table to be written every step.
    y: targeted properties
    
    type_x: float list
    type_xtable: parameterTable object
    type_y: property object list
    rtype: float
    """
    xt.update_table(x)
    print("\n#---- Step %d -------------#\n" % xt.len)

    xt.write_datafile(
        xt.current_parameter(),
        dataFileOut=ffFile,
        dataFileTemp=ffTemplate,
    )

    print("\nRunning Simulation...:")
    simulation.run(execute)
    propertyValues = simulation.post_process(processScript)

    print("Saving Property Values...")
    if not len(propertyValues) == int(totalProperties):
        raise ValueError(
            '%s target properties needed, but %d produced by simulation.' % (
                totalProperties, len(propertyValues)
            )
        )
    for p, value in zip(properties, propertyValues):
        p.value = value
        p.update_property_list()

    print("\nCalculating Target Value...:")
    targetValue = sum([p.target_function() for p in properties])
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
        0: optMethod,
        1: initParaTableFile,
        2: paraTableFile,
        3: path,
        4: processScript,
    }
    print_info(INFO_DICT)

    (
        paraValuesInitial, 
        paraTable,
    ) = initialze_parameters(initParaTableFile, paraTableFile)
    properties = initialze_properties(propertyNames, int(totalProperties))
    simulation = Simulation(path)
    
    # ----------------------------------------------------------------------- #
    def test_flow_with_1_arg(p):
        return test_flow(p, paraTable, properties)
    
    def simulation_with_1_arg(p):
        return simulation_flow(p, paraTable, ffForSimulation)
        
    #TODO wrap this part as a function and give 'func' as input?
    print("\nOptimizing...:")
    if mode == "test":
        func = test_flow_with_1_arg
    elif mode == "simulation":
        func = simulation_with_1_arg

    optParaValues = scipy.optimize.minimize(
        func,
        paraValuesInitial,
        method=optMethod,
        options={'disp': True,
                 'maxiter': 100,
                 'ftol': 0.0001,
        },
        # callback=callbackF,
    )
