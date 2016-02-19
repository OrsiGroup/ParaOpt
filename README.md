# ParaOpt

A python optimizer for developing molecular simulation forcefield 

Author: MP, WD

## Installation

## Usage

An input text file is needed to configure all stuffs related to the optimizing 
process. You also need your own post-processing script to extract the values of
the properties you choosed as the optimization target.

### Configurations

### Post-processing script

You can use whatever script you like to post-process your data. The only 
requirement is that the final numbers of all target property should be saved in
one line, separated by blank space, in a file named "res.postprocess" under 
your simulation path.

For example, it can be a shell script like:
```bash

q1=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY1)
q2=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY2)
q3=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY3)
q4=$(SOME_COMMANDS_TO_OBTAIN_PROPERTY4)

echo ${q1} ${q2} ${q3} ${q4} > res.postprocess
```
