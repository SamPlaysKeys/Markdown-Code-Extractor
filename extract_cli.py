#!/usr/bin/env python3

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

class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedDumper, self).increase_indent(flow, False)

def extract_from_file(file_path, triggers):
    """
    Helper function to read a file and extract code blocks after the triggers.
    Returns a combined list of code blocks (strings) found for all triggers,
    deduplicated by their position in the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        unique_blocks = {} # Map start_index -> block_content
        
        # Ensure triggers is a list
        if isinstance(triggers, str):
            triggers = [triggers]

        for trigger in triggers:
            # Find the first occurrence of the trigger
            # We use re.escape to treat the trigger string literally
            trigger_match = re.search(re.escape(trigger), content)
            if trigger_match:
                start_search_pos = trigger_match.end()
                relevant_content = content[start_search_pos:]
                
                # Regex for code blocks
                code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
                
                for match in code_block_pattern.finditer(relevant_content):
                    # Calculate absolute position in the file to identify unique blocks
                    abs_start = start_search_pos + match.start()
                    
                    if abs_start not in unique_blocks:
                        unique_blocks[abs_start] = match.group(1).strip()
        
        # Return blocks sorted by their appearance in the file
        sorted_blocks = [unique_blocks[k] for k in sorted(unique_blocks.keys())]
        return sorted_blocks if sorted_blocks else None

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    # --- ARGUMENT SETUP ---
    parser = argparse.ArgumentParser(description="Extract code blocks that follow a trigger string from Markdown to YAML.")
    
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
        "-t", "--trigger", 
        default="YAML", 
        help="The string to search for. Defaults to the string 'YAML'."
    )
    parser.add_argument(
        "-a", "--all", 
        action="store_true", 
        help="Extract all code blocks into separate files. If not set, only the first block is extracted."
    )
    parser.add_argument(
        "-c", "--concat", 
        action="store_true", 
        help="Concatenate multiple code blocks into a single YAML file. Used with -a."
    )

    args = parser.parse_args()

    # --- TRIGGER PARSING ---
    triggers = []
    if args.trigger.startswith("(") and args.trigger.endswith(")"):
        # Format: ([Trigger 1], [Trigger 2])
        # Find content inside brackets
        raw_triggers = re.findall(r'\[(.*?)\]', args.trigger)
        triggers = raw_triggers
    else:
        triggers = [args.trigger]

    # --- LOGIC ---
    
    def save_single_file(data, path):
        """Helper to write a list of data objects to a single YAML file."""
        with open(path, "w", encoding="utf-8") as outfile:
            if len(data) == 1:
                yaml.dump(data[0], outfile, Dumper=IndentedDumper, default_flow_style=False, allow_unicode=True)
            else:
                yaml.dump_all(data, outfile, Dumper=IndentedDumper, default_flow_style=False, allow_unicode=True)

    def save_extracted_blocks(blocks, dest_path, split_files=False):
        """
        Parses extracted blocks as YAML and saves them.
        If split_files is True, saves each block to a separate file (appending _N).
        Otherwise, saves all blocks to the single dest_path.
        """
        # Parse all blocks first
        parsed_blocks = []
        for b in blocks:
            block_data = []
            try:
                for doc in yaml.safe_load_all(b):
                    block_data.append(doc)
            except Exception as e:
                print(f"Warning: Failed to parse block as YAML. Keeping as string. Error: {e}")
                block_data.append(b)
            parsed_blocks.append(block_data)

        if split_files:
            base, ext = os.path.splitext(dest_path)
            for i, data in enumerate(parsed_blocks):
                # Construct filename: file.yaml, file_2.yaml, file_3.yaml...
                if i == 0:
                    current_path = dest_path
                else:
                    current_path = f"{base}_{i+1}{ext}"
                
                save_single_file(data, current_path)
        else:
            # Flatten all parsed data into one list for a single file
            all_data = [item for sublist in parsed_blocks for item in sublist]
            save_single_file(all_data, dest_path)

    # CASE 1: Input is a Directory
    if os.path.isdir(args.input):
        count = 0
        for filename in os.listdir(args.input):
            if filename.endswith(".md"):
                source_path = os.path.join(args.input, filename)
                file_stem = os.path.splitext(filename)[0]
                first_word = file_stem.split(' ')[0]
                
                # Determine output path (handle placeholders)
                target_path = args.output
                replacements = {
                    "{filename}": file_stem,
                    "{firstword}": first_word
                }
                
                for placeholder, replacement in replacements.items():
                    if placeholder in target_path:
                        target_path = target_path.replace(placeholder, replacement)
                
                # Check if target_path looks like a file (ends in .yaml/.yml) or directory
                if target_path.lower().endswith(('.yaml', '.yml')):
                    dest_path = target_path
                    dest_dir = os.path.dirname(dest_path)
                else:
                    dest_dir = target_path
                    dest_path = os.path.join(dest_dir, file_stem + ".yaml")
                
                # Ensure output directory exists
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                
                blocks = extract_from_file(source_path, triggers)
                
                if blocks:
                    # Filter blocks based on -a flag
                    if not args.all:
                        blocks = blocks[:1]
                    
                    should_split = args.all and not args.concat
                    save_extracted_blocks(blocks, dest_path, split_files=should_split)
                    print(f"Processed: {filename} -> {dest_path} (Split: {should_split})")
                    count += 1
        print(f"--- Batch Complete. Processed {count} source files. ---")

    # CASE 2: Input is a Single File
    elif os.path.isfile(args.input):
        blocks = extract_from_file(args.input, triggers)
        
        if blocks:
            # If output path is a directory, verify valid filename provided or derive it
            if os.path.isdir(args.output):
                 print("Error: Input is a file, but output is a directory. Please specify a full output filename.")
                 sys.exit(1)

            # Filter blocks based on -a flag
            if not args.all:
                blocks = blocks[:1]

            should_split = args.all and not args.concat
            save_extracted_blocks(blocks, args.output, split_files=should_split)
            print(f"Success! Extracted to '{args.output}' (Split: {should_split})")
        else:
            print(f"No blocks found in '{args.input}' with provided triggers.")

    else:
        print("Error: Input path does not exist.")

if __name__ == "__main__":
    main()
