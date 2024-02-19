## Reads the configuration file of mva_runner to check if there is any repeated element. Repeated elements (indexes or variables) cause mva runner to stop
import yaml
from itertools import chain


def main():
    config_path = "/lhome/ific/p/pamarag/Work/BDT_tHq/tHqIFIC/tHqMVA/Utils/config.yaml"
    variables_set = 'GeneralMVA'
    config_content = OpenYaml(config_path, variables_set)

    list_of_variables= []
    list_of_keys = []
    for key, value in config_content.items():
        list_of_keys.append(str(key))
        aux = value
        list_of_variables.append(aux['Name'])
    finduplicate(list_of_keys)
    finduplicate(list_of_variables)

def OpenYaml(path, variable_set, option = 'r'):
    with open(path, option) as stream:
        out = yaml.load(stream)
    return out[variable_set]

def finduplicate(thelist):
    l1 = []
    for i in thelist:
        if i not in l1:
           l1.append(i) 
        else: # This "else" is only activated when an element of the list is already present
            print i 

#def ifducplicates(thelist):
#    if len(thelist) != len(set(thelist)):
#        print "There are duplicates"
#        return True
#    else:
#        return False


if __name__ == '__main__':
  main()
