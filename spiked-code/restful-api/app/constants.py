import os
import yaml

# Hard code some source data for now
with open("./lookup.yaml") as f:
    RESOURCE_LOOKUP = yaml.load(f, Loader=yaml.FullLoader)
