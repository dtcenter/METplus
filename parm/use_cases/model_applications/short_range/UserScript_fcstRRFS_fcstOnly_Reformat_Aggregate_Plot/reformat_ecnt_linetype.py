import os
from METdataio.METreformat import write_stat_ascii as wsa
import metcalcpy.util.read_env_vars_in_config as readconfig

if __name__ == "__main__":
    reformat_config_file = os.getenv("REFORMAT_YAML_CONFIG_NAME", "reformat_ecnt.yaml")
    config_dict = readconfig.parse_config(reformat_config_file)
    wsa.main()