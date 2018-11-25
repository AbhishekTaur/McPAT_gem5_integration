import re
import simplejson
import os

pattern = "((config|stats)\.(\w+_*\.)+\w+:*\w*)"


def get_stats_value(config):
    with open('./output_gem5/stats.txt') as f:
        for line in f:
            if config.split('stats.')[-1] in line:
                line = line.split(config.split('stats.')[-1])[-1]
                value = re.search("\d+", line).group()
                return int(value)


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

    return value


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
                if '/' in parameter:
                    parameter = parameter.split('/')[-1]
                match_obj = re.findall(pattern, parameter)
                for config in match_obj:
                    configs.append(config[0])

    return configs, parameters


def main():
    configs = []
    parameters = []

    configs, parameters = read_mcpat(configs=configs, parameters=parameters)
    values = read_config_value(configs=configs)
    write_config_values_parameters(values=values, parameters=parameters)


if __name__ == '__main__':
    main()
