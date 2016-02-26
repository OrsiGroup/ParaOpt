# ParaOpt

A python optimizer for developing molecular simulation forcefield.

**Author:** MP, WD

## Installation

### 

## Usage

To use this code, an input text file is needed to configure all stuffs to
control the optimizing process. You also need your own post-processing script
to extract the values of the properties you chose as the optimization target.

To run:

    $ opt.py YOUR_CONFIG_FILE

### Configurations

The input configuration file is organized in the standard .INI file format,
which is also similar to the .mdp format in Gromacs. All options are grouped
in four sections: simulation, properties, parameters, and optimization.
See [config.sample] as a example to create your config file, and below is a 
brief explanation for options in each section.

#### Simulation
```Ini
[ simulation ]

lmp = The LAMMPS executable called to run your simulation.
path = The path under which you run your simulation, relative to the 
                current executing directory.
inFileName = Your LAMMPS input file.
processScript = A script to post-process your simulation output to obtain 
                targeted property values.
```
**Note:** the values of options "`inFileName`" and "`processScript`" indicate a
relative path to the value of option "`path`". E.g., "`inFileName = in.lammps`"
points to the input file under the simulation folder, and "`processScript = 
../process.sh`" points to a script file in the parent directory.

#### Optimization
```Ini
[ optimization ]

optMethod = The optimization algorithm. 
```
**Note:** the value of "`optMethod`" could be one of the following:
 - "`Nelder-Mead`"

#### Properties
```Ini
[ properties ]

totalProperties = The number of targeted properties, which should match the
                  output by your post-processing script.
propertyNName = The name you use to identify the Nth targeted property.
propertyNRef = The reference value for the Nth property.
propertyNSpecial  = The special handling for the target-function of the Nth 
                    property. ;(optional)
propertyNSpecialArg = The argument for the special handling, which is only 
                      useful when "propertyNSpecial = scaled". ;(optional)
```
**Note:** If "`totalProperties = M`", in total M bunches of "`propertyN*`"
options should be given, where N = 1, 2, ..., M. 
"`propertyNName`" can be left blank, and if so, it will be automatically 
assigned as "q_N".
The value of "`propertyNSpecial`" could be one of the following, and then 
"`propertyNSpecialArg`" is only useful for value "`scaled`", indicating the 
scaling coefficient:
 - "`log`": calculate the target-function for the logarithmized value;
 - "`scaled`": calculate the scaled target-function.

#### Parameters
```Ini
[ parameters ]

initParaTableFile = A tabulated text file you prepared, listing the initial 
                    values of the forcefield parameters to be optimized (see 
                    below for further explanation about the required format).
paraTableFile = The tabulated file that will be generated during every 
                optimizing step, saving the output parameter values. 
ffTemplate = A template of the forcefield file you prepared for running the 
             simulation (see rules below).
ffForSimulation = The forcefield file that will be read for your simulation, 
                  written based on the "ffTemplate".
```
The "`initParaTableFile`" should contain only 2 lines. The 1st line starts 
with "`#`" and then lists the parameter "names" (or "tags"), and the 2nd
line lists the corresponding values from which you want to start the 
optimization. Now assume you have such a set of parameters to optimize:
```
# epsilon_1 sigma_1 epsilon_2 sigma_2 epsilon_3 sigma_3
0.1 10 0.2 20 0.3 30
```
The parameter names are important because they are used in the "`ffTemplate`" 
so that the code finds the correct positions in the template and replace them 
with corresponding numbers and runs the simulation. Your template forcefield 
file looks something like this:
```bash
pair_coeff    1    1	  @epsilon_1 @sigma_1
pair_coeff    1    2	  @epsilon_2 @sigma_2 
pair_coeff    1    3	  @epsilon_3 @sigma_3 
```
Note the "`@`" placeholder that indicates here the following string should be 
replaced, and the code tries to match it from the "`initParaTableFile`" (1st 
step) or "`paraTableFile`". So, a real force field file ("`ffForSimulation`") 
you would expect to be generated in the 1st step will be:
```bash
pair_coeff    1    1	  0.1 10 
pair_coeff    1    2	  0.2 20 
pair_coeff    1    3	  0.3 30 
```
Then after each step, the freshly optimized parameter values are saved into 
"`paraTableFile`" --thus, it will contain the same number of columns as 
"initParaTableFile" and N+2 rows after N iteration steps -- and the 
"`ffForSimulation`" are updated.

**Note:** all files identified in this section imply a path relative to the 
executing directory, or an absolute path is  also accepted.


### Post-processing script

You can use whatever script you like to post-process your data. The only 
requirement is: the final numbers of all target property should be saved in
one line, separated by blank space, in a file named "`res.postprocess`" under 
your simulation path.

For example, it can be a shell script like:
```bash

q1=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY1)
q2=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY2)
q3=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY3)
q4=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY4)

echo ${q1} ${q2} ${q3} ${q4} > res.postprocess
```

[config.sample]: https://github.com/wdingsjtu/ParaOpt/blob/master/config.sample
