#
#   configuration.py
#
# Created:  2015/Jan/25
# Purpose:  Read and process setting from a configuration file. 
# Notes:    
#
# -------------------------------------------------------------------------- #

from __future__ import print_function

from configparser import ConfigParser as cp
# from configparser import NoOptionError


# -------------------------------------------------------------------------- #

class Configuration(cp):

    # A dict containing all mandatory options.
    # "LOWER CASE" if adding new words!
    _optionsDict = {
        'optimization': ['optmethod',
                         ],
        'properties': ['totalproperties',
                       ],
        'parameters': ['totalparameters',
                       ],
        'simulation': [
                       'mode',
                       'execute',
                       'path',
                       'processscript',
                       'paratablefile',
                       'ffforsimulation',
                       'fftemplate'
                       ],
    }

    def read(self, confFile):
        """ Based on configparser.ConfigParser.read().

        t_confFile: str
        rtype: None
        """
        super(Configuration, self).read(confFile)

        print("Reading input configurations from \"%s\"..." % confFile)
        if set(self.sections()) != set(self._optionsDict.keys()):
            raise ValueError("Incorrect section in %s." % confFile)

    def get_config(self, section):
        """
        Get required configurations for each "section".

        type_section: str
        rtype: list
        """
        optionsRequired = self._optionsDict[section]
        optionsRead = self.options(section)
        if not set(optionsRequired).issubset(set(optionsRead)):
            raise ValueError(
                "Option \"%s\" (mandatory) not found." % (
                    (set(optionsRequired) - set(optionsRead)).pop()
                )
            )
        configs = [self.get(section, option) for option in optionsRequired]

        # TODO Unicode matters?
        # configs = map(str, configs)
        
        if section == 'simulation':
            if configs[0] != "test" and configs[0] != "simulation":
                raise ValueError("Wrong type of objective function!")
            return configs

        elif section == 'properties':
            return self._get_config_for_property(configs)

        else:
            return configs

    def _get_config_for_property(self, configGot):
        """ Special parsing for the 'properties' section.

        type_configGot: list
        rtype: list
        """
        SECTION = 'properties'

        totalProperties = int(configGot[0])
        propertyNames = []
        propertyRefs = []
        propertySpecials = []

        suffixes = ['property' + str(i) for i in range(1, totalProperties+1)]
        for suffix in suffixes:
            propertyNames.append(self.get(SECTION, suffix + 'name'))
            propertyRefs.append(self.getfloat(SECTION, suffix + 'ref'))

            if self.has_option(SECTION, suffix + 'special'):
                specialType = self.get(SECTION, suffix + 'special')
                special = [specialType]  # It's a list!
                if self.has_option(SECTION, suffix + 'specialArg'):
                    specialArg = self.getfloat(SECTION, suffix + 'specialArg')
                    special.append(specialArg)
            else:
                special = ''
            propertySpecials.append(special)

        return [totalProperties, propertyNames, propertyRefs, propertySpecials]
