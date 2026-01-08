import os
import re
import yaml
import argparse
import sys

def str_presenter(dumper, data):
    """Configures yaml for dump to look like a block literal"""
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def extract_from_file(file_path, trigger_string):
    """
    Helper function to read a file and extract code blocks after the trigger.
    Returns a list of code blocks (strings) or None if no trigger found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if trigger_string in content:
            # Split and take content after the trigger
            relevant_content = content.split(trigger_string, 1)[1]
            
            # Regex for code blocks
            code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
            matches = code_block_pattern.findall(relevant_content)
            
            return [m.strip() for m in matches] if matches else []
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    # --- ARGUMENT SETUP ---
    parser = argparse.ArgumentParser(description="Extract code blocks from Markdown to YAML.")
    
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Path to input file OR directory of files."
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Path to output file (if input is file) OR output directory (if input is dir)."
    )
    parser.add_argument(
        "--trigger", 
        default="## Solution", 
        help="The string to search for. Defaults to '## Solution'."
    )

    args = parser.parse_args()

    # --- LOGIC ---
    
    # CASE 1: Input is a Directory
    if os.path.isdir(args.input):
        count = 0
        for filename in os.listdir(args.input):
            if filename.endswith(".md"):
                source_path = os.path.join(args.input, filename)
                file_stem = os.path.splitext(filename)[0]
                first_word = file_stem.split(' ')[0]
                
                # Determine output directory (handle placeholders)
                current_output_dir = args.output
                if "$filename" in current_output_dir:
                    current_output_dir = current_output_dir.replace("$filename", file_stem)
                if "$firstword" in current_output_dir:
                    current_output_dir = current_output_dir.replace("$firstword", first_word)
                
                # Ensure output directory exists
                if not os.path.exists(current_output_dir):
                    os.makedirs(current_output_dir)

                # Create output filename: input.md -> input.yaml
                out_name = file_stem + ".yaml"
                dest_path = os.path.join(current_output_dir, out_name)
                
                blocks = extract_from_file(source_path, args.trigger)
                
                if blocks:
                    with open(dest_path, "w", encoding="utf-8") as outfile:
                        yaml.dump(blocks, outfile, default_flow_style=False, allow_unicode=True)
                    print(f"Processed: {filename} -> {dest_path}")
                    count += 1
        print(f"--- Batch Complete. Created {count} YAML files. ---")

    # CASE 2: Input is a Single File
    elif os.path.isfile(args.input):
        blocks = extract_from_file(args.input, args.trigger)
        
        if blocks:
            # If output path is a directory, verify valid filename provided or derive it
            if os.path.isdir(args.output):
                 print("Error: Input is a file, but output is a directory. Please specify a full output filename.")
                 sys.exit(1)

            with open(args.output, "w", encoding="utf-8") as outfile:
                yaml.dump(blocks, outfile, default_flow_style=False, allow_unicode=True)
            print(f"Success! Extracted to '{args.output}'")
        else:
            print(f"No blocks found in '{args.input}' after trigger '{args.trigger}'")

    else:
        print("Error: Input path does not exist.")

if __name__ == "__main__":
    main()
