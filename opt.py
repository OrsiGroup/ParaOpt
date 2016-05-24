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
    if len(sys.argv) == 2:
        return sys.argv[1]
    else:
        print("Syntax: opt.py configureFile")
        sys.exit()

def print_info(argDict):
    ATTR_DICT = {
        0: "Optimization Method",
        1: "Input Parameters",
        2: "Output Parameters",
        3: "Simulation Folder",
        4: "Post-Process"
    }
    l = 20
    print("%s |%s" %("ATTRIBUTE".center(l), "VALUE".center(l)))
    print("-" * 2 * (l + 1))
    for key in ATTR_DICT:
        print("%s |%s"
              %(ATTR_DICT[key].ljust(l), argDict[key].rjust(l)))

# -------------------------------------------------------------------------- #
def test_flow(parameters):
    paraTable.update_table(parameters)
    print("\n#---- Step %d -------------#\n" % paraTable.len)

    propertyValues = [math.sin(parameters[0])**2 +
                      math.cos(parameters[1])**2 +
                      math.sin(parameters[2])**2] * len(properties)
    propertyValues = [str(value) for value in propertyValues]

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

def simulation_flow(parameters):
    """ The sub-routine to be optimized. Take in a set of parameters, and
    return a targeted function value.

    type_parameters: float list
    rtype: float
    """
    paraTable.update_table(parameters)
    print("\n#---- Step %d -------------#\n" % paraTable.len)

    paraTable.write_datafile(
        paraTable.current_parameter(),
        dataFileOut=ffForSimulation,
        dataFileTemp=ffTemplate,
    )

    print("\nRunning Simulation...:")
    simulation = Simulation(path)
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

    paraTableInitial = ParameterTable(initParaTableFile)
    paraValuesInitial = paraTableInitial.current_parameter()
    subprocess.call(
        "head -1 %s > %s" % (initParaTableFile, paraTableFile),
        shell=True,
    )
    paraTable = ParameterTable(paraTableFile)

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

    # ----------------------------------------------------------------------- #
    print("\nOptimizing...:")
    if mode == "test":
        func = test_flow
    elif mode == "simulation":
        func = simulation_flow

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
