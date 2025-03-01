import argparse
import yaml
import os

def add_rule_to_config(args):
    net = args.net
    suffix = args.suffix

    # Define the path to the config file
    config_path = os.path.expanduser("~/.config/clash/my_config.yaml")
    
    # Check if the file exists
    if not os.path.exists(config_path):
        print(f"Error: The configuration file {config_path} does not exist.")
        return

    # Load the existing YAML file
    with open(config_path, 'r', encoding='utf-8') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            return
    
    # Ensure 'rules' key exists in the config, create it if necessary
    if 'rules' not in config:
        config['rules'] = []

    # Create the new rule entry
    if suffix:
        new_rule = f"DOMAIN-SUFFIX,{net},🚀 节点选择"
    else:
        new_rule = f"DOMAIN,{net},🚀 节点选择"

    # Add the new rule to the rules section, ensure it emerges before 漏网之🐟
    config['rules'].insert(-2, new_rule)

    # Write the updated configuration back to the file
    with open(config_path, 'w', encoding='utf-8') as file:
        try:
            yaml.safe_dump(config, file, default_flow_style=False, allow_unicode=True)
            print(f"Successfully added the rule: {new_rule}")
        except yaml.YAMLError as e:
            print(f"Error writing to YAML file: {e}")
            return

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Add a rule to the Clash config file.")
    parser.add_argument('--net', required=True, help='The network name to be added in the rules section')
    parser.add_argument('--suffix', action='store_true', help='Indicates if the network name is a suffix')
    # Parse arguments
    args = parser.parse_args()

    # Add the rule to the config
    add_rule_to_config(args)

if __name__ == '__main__':
    main()


