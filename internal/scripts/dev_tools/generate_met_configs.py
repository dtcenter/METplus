#! /usr/bin/env python3

import sys
import os
import re
import string


def parse_metplus_log(lines):
    """
    Parses a METplus log file to extract environment variables and
    wrapped configuration files for specific commands.
    """

    # regex to find a file path ending in Config_wrapped
    # \S matches any non-whitespace character
    config_pattern = re.compile(r'(\S+Config_wrapped)')

    results = []

    current_env_vars = {}
    capturing_env = False

    for line in lines:
        # Detect start of the block
        if "COPYABLE ENVIRONMENT FOR NEXT COMMAND" in line:
            capturing_env = True
            current_env_vars = {}  # Reset dictionary for new block
            continue

        # Capture export lines if we are inside a block
        if capturing_env and line.startswith("export"):
            # Remove export and trailing semicolon
            content = line[7:].rstrip(';')

            # Split on the first = to get key and value
            key, val = content.split('=', 1)
            val = _handle_quotes(val)

            current_env_vars[key] = val
            continue

        # Detect the Command line to close the block
        if capturing_env and "INFO: COMMAND:" in line:
            # Search for the config file in this line
            match = config_pattern.search(line)

            if match:
                config_file = match.group(1)

                # Store the result
                results.append({
                    'config_file': config_file,
                    'env_vars': current_env_vars
                })

            # Reset state
            capturing_env = False
            current_env_vars = {}

    return results

def _handle_quotes(val):
    # remove whitespace around string
    val = val.strip()
    # If value is wrapped in double quotes, remove them
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]

    # Handle escaped quotes often found in these logs (e.g. \"ADPUPA\")
    val = val.replace('\\"', '"')
    return val

def process_parsed_logs(parsed_items, output_dir, id_str):
    """
    Takes the output from the log parser, reads the referenced config files,
    substitutes the environment variables, and writes unique output files.

    Args:
        parsed_items (list): List of dicts containing 'config_file' (str)
                             and 'env_vars' (dict).
        output_dir (str): Directory where processed files will be saved.
        id_str (str): Identifier string to append to output filenames.

    Returns:
        list: A list of file paths to the newly created configuration files.
    """
    created_files = []

    for item in parsed_items:
        config_file = item.get('config_file')
        env_vars = item.get('env_vars', {})

        if not config_file:
            continue

        # Check if the wrapped config file exists
        if not os.path.exists(config_file):
            print(f"ERROR: Wrapped config file not found: {config_file}")
            continue

        # Read the template config file
        try:
            with open(config_file, 'r') as f:
                template_content = f.read()
        except IOError as e:
            print(f"ERROR: Could not read '{config_file}': {e}")
            continue

        # Perform Variable Substitution
        # string.Template handles ${VAR} and $VAR syntax.
        # safe_substitute is used so it doesn't crash if a variable is missing
        # from the log (it will leave the ${VAR} placeholder intact).
        try:
            template = string.Template(template_content)
            final_content = template.safe_substitute(env_vars)
        except Exception as e:
            print(f"ERROR: Could not substitute variables for '{config_file}': {e}")
            continue

        # Determine unique output filename
        # Format: {OriginalName}_{ID}[_{Counter}].{Ext}
        filename = os.path.basename(config_file).replace('_wrapped', '')

        target_name = f"{filename}_{id_str}"
        target_path = os.path.join(output_dir, target_name)

        # Collision detection: increment a counter until a unique name is found
        counter = 1
        while os.path.exists(target_path):
            target_name = f"{filename}_{id_str}_{counter}"
            target_path = os.path.join(output_dir, target_name)
            counter += 1

        # Write the processed file
        os.makedirs(output_dir, exist_ok=True)
        try:
            with open(target_path, 'w') as f:
                f.write(final_content)
            created_files.append((target_path, final_content))
            print(f"Success: Created '{target_path}'")
        except IOError as e:
            print(f"ERROR: Could not write to '{target_path}': {e}")

    return created_files

def print_usage():
    print(f"Usage: {os.path.basename(__file__)} <metplus_log_file> <output_directory> <id_string>")
    print("  metplus_log_file is METplus log to parse. Must be run with LOG_LEVEL=DEBUG.")
    print("  output_directory is where generated MET config files will be saved.")
    print("  id_string is appended to output filenames, e.g. PB2NCConfig_<id>_<n>.")
    print(f"Example: {os.path.basename(__file__)} /path/to/metplus.log.20260112223529 /path/to/my/output/dir test")

def main():
    if len(sys.argv) != 4:
        print("ERROR: Must supply 3 arguments: log file, output directory, and ID string")
        print_usage()
        sys.exit(1)

    filename = sys.argv[1]
    output_dir = sys.argv[2]
    id_str = sys.argv[3]

    try:
        with open(filename, 'r') as file_handle:
            lines = file_handle.read().splitlines()
    except FileNotFoundError:
        print(f"ERROR: Log file not found: {filename}")
        sys.exit(1)

    items = parse_metplus_log(lines)
    if not items:
        print("ERROR: No items parsed from log. Check that LOG_LEVEL=DEBUG")
        sys.exit(1)

    process_parsed_logs(items, output_dir, id_str)

if __name__ == "__main__":
    main()
