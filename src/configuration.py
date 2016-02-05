#
#   configuration.py
#
# Created:  2015/Jan/25
# Purpose:  Read and process setting from a configuration file. 
# Notes:    
#
#----------------------------------------------------------------------------#

from configparser import ConfigParser as cp
from configparser import NoOptionError

#----------------------------------------------------------------------------#

class Configuration(cp): 

    global sectionSet
    sectionSet = ['simulation', 'properties', 'parameters', 'optimization']
    #TODO maybe no need to be global

    def read(self, confFile):
        print "Reading input configurations from \"%s\"..." % (confFile)
        super(Configuration, self).read(confFile)
 
        if not set(self.sections()) == set(sectionSet):
            raise ValueError("Incorrect section format.")

    def get_config(self, section):
        '''
        Get required configurations for the "section".

        type_section: str
        rtype: list
        '''
        # "LOWER CASE" if adding new words!
        optionsRequired = {'optimization': ['optmethod',
                                           ], 
                           'properties': ['totalproperties',
                                         ],
                           'parameters': ['initparatablefile', 
                                          'paratablefile', 
                                          'ffforsimulation',
                                          'fftemplate', 
                                         ], 
                           'simulation': ['lmp','path','infilename'
                                         ],
                          }

        optionsRequired = optionsRequired[section]
        setRead = set(self.options(section))
        if set(optionsRequired).issubset(setRead): 
            values = [self.get(section, option) for option in optionsRequired]
            #TODO Unicode matters?
            #values = map(str, values)  

            if section =='properties':
                totalProperties = int(values[0])
                suffixes = ['property' + str(i+1) 
                            for i in range(totalProperties)]
                propertyNames = []
                propertyRefs = []
                propertySpecials = [] 
                for suffix in suffixes:
                    propertyNames.append(self.get(
                                         section, suffix + 'name'))
                    propertyRefs.append(self.getfloat(
                                        section, suffix + 'ref'))
                    if self.has_option(section, suffix + 'special'):
                        special = [self.get(
                                   section, suffix + 'special')]
                    else:
                        special = ''
                    if self.has_option(section, suffix + 'specialArg'):
                        special.append(self.getfloat(
                                       section, suffix + 'specialArg'))
                    propertySpecials.append(special)
                values = [totalProperties, propertyNames, propertyRefs, propertySpecials]
         
        return values
