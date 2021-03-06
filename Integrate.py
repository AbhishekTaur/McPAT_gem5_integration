import re
import simplejson
import os
from shutil import rmtree, copyfile

# Pattern to recognize the parameters in mcpat file
pattern = "((config|stats)\.(\w+_*\.)+\w+:*\w*)"

# Read values from the stats file
# Inputs:
#   config: Input configuration whose value is required


def get_stats_value(config):
    value = 0
    with open('./output_gem5/stats.txt') as f:
        for line in f:
            if config.split('stats.')[-1] in line:
                line = line.split(config.split('stats.')[-1])[-1]
                value = re.search("\d+", line).group()

    return int(value)

# Read the config values from config.ini
# Inputs:
#   config: Input configuration whose value is required


def get_config_value(config):
    with open('./output_gem5/config.ini') as f:
        found = False
        complete_param = config.split('config.')[-1]
        group = re.match("(\w+\.)*", complete_param).group()
        group = group[0: len(group) - 1]
        param = complete_param.replace(group, "").replace(".", "")
        value = 0
        for line in f:
            if group in line and "=" not in line:
                found = True
            if found:
                if param in line:
                    value = int(line.split("=")[-1].strip())
                    found = False
                    break

    return value

# Caller method for reading from stats.txt and config.ini
# Read the config values from config.ini
# Inputs:
#   configs: Input configurations


def read_config_value(configs):
    values = {}
    if 'output_gem5' not in os.listdir('.'):
        raise ValueError("Missing Output Dir: output_gem5")
    if ("stats.txt" not in os.listdir("./output_gem5")) or ("config.ini" not in os.listdir("./output_gem5")):
        raise ValueError('stats.txt or config.ini file not present')
    else:
        for config in configs:
            if 'stats' in config:
                values[config] = get_stats_value(config=config)
            else:
                values[config] = get_config_value(config=config)
    return values

# Method for writing the configuration values.
# First a check is made if there is output.txt file present.
# Using simplejson it dumps one by one the configurations and
# parameters to be computed.
# Inputs:
#   values: Input configurations
#   parameters: parameters in template file to computed


def write_config_values_parameters(values, parameters):
    if 'output.txt' in os.listdir('.'):
        os.remove('./output.txt')
        f = open('output.txt', 'w')
        simplejson.dump('Configurations and values', f)
        f.write('\n\n')
        for key in values.keys():
            simplejson.dump(key + '=' + str(values.get(key)), f)
            f.write('\n')
        f.write('\n')
        simplejson.dump('Parameters to be evaluated', f)
        f.write('\n\n')
        for parameter in parameters:
            simplejson.dump(parameter, f)
            f.write('\n')


def read_mcpat(configs, parameters):
    if 'mcpat-template.xml' not in os.listdir("."):
        raise ValueError("Missing mcpat-template.xml in the present directory")
    with open('./mcpat-template.xml') as f:
        for i, line in enumerate(f):
            if 'REPLACE' in line:
                line = line.strip()
                parameter = line.split("REPLACE{")[-1].split("}")[0]
                parameters.append(parameter)
                match_obj = re.findall(pattern, parameter)
                for config in match_obj:
                    configs.append(config[0])

    return configs, parameters

# Update the McPAT file with the computed values of the parameters
# Input:
#   params: All computed parameter values


def update_mcpat_file(params):
    if 'tmp' in os.listdir('.'):
        rmtree('tmp')
    os.mkdir('tmp')
    copyfile('mcpat-template.xml', 'tmp/mcpat-template.xml')
    with open('tmp/mcpat-template.xml') as f:
        file_str = f.read()
    file_contents = file_str.split('\n')
    i = 0
    for j, content in enumerate(file_contents):
        if 'REPLACE' in content:
            replace_str = re.search('REPLACE{.*}', content).group()
            content = content.replace(replace_str, params[i])
            file_contents[j] = content
            i = i + 1
    f = open('tmp/mcpat-template.xml', 'w')
    for content in file_contents:
        f.write(content)
        f.write('\n')

# Computes the parameters values give the value of each configuration
# Inputs:
#   values: values of the configurations
#   parameters: The parameters to be computed


def compute_parameters(values, parameters):
    param_values = []
    for parameter in parameters:
        matchObj = re.findall(pattern, parameter)
        for config in matchObj:
            parameter = parameter.replace(config[0], str(values.get(config[0])))
        if ',' not in parameter:
            if isinstance(eval(parameter), float):
                param_values.append(str(int(eval(parameter)+1)))
            else:
                param_values.append(str(int(eval(parameter))))
        else:
            param_values.append(parameter)
    update_mcpat_file(params=param_values)

# Main Method


def main():
    configs = []
    parameters = []

    configs, parameters = read_mcpat(configs=configs, parameters=parameters)
    values = read_config_value(configs=configs)
    write_config_values_parameters(values=values, parameters=parameters)
    compute_parameters(values=values, parameters=parameters)

# Calls the main method


if __name__ == '__main__':
    main()
