import importlib

config = {"filters": ["filters.filter-1", "filters.filter-4"], "validators": ["validators.validator-1", "validators.validator-2"]}
environment = {}

for i_config in config["filters"]:
    output = importlib.import_module(i_config).filter({'f': 'f'})
    environment[i_config] = output
    print(f'environment = {environment}')

for i_config in config["validators"]:
    output = importlib.import_module(i_config).validator({'v': 'v'})
    environment[i_config] = output
    print(f'environment = {environment}')

# Test performances
# for i in range(6):
#     im = importlib.import_module("filters.filter-" + str((i % 2) + 1))
#     environment = im.filter(environment)
