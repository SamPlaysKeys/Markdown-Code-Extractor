import os
import re
import yaml

# --- CONFIGURATION ---
SEARCH_DIR = "."                  # Directory containing .md files
TRIGGER_STRING = "## Solution"    # The string to look for
OUTPUT_FILE = "extracted_code.yaml"
# ---------------------

def extract_code_blocks():
    # Dictionary to store results: { filename: [code_block_1, code_block_2] }
    extracted_data = {}

    # Regex to find code blocks enclosed in triple backticks
    # captures content inside ```...```
    code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)

    # Loop through all files in the directory
    for filename in os.listdir(SEARCH_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(SEARCH_DIR, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the trigger string exists in the file
            if TRIGGER_STRING in content:
                # Split the file and take everything AFTER the trigger string
                # maxsplit=1 ensures we only split on the first occurrence
                relevant_content = content.split(TRIGGER_STRING, 1)[1]

                # Find all code blocks in the remaining text
                matches = code_block_pattern.findall(relevant_content)

                if matches:
                    # formatting: strip leading/trailing whitespace from the code itself
                    cleaned_matches = [m.strip() for m in matches]
                    extracted_data[filename] = cleaned_matches

    # Save to YAML
    if extracted_data:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
            # default_flow_style=False makes it readable (block style)
            yaml.dump(extracted_data, outfile, default_flow_style=False, allow_unicode=True)
        print(f"Success! Extracted code blocks from {len(extracted_data)} files into '{OUTPUT_FILE}'.")
    else:
        print("No code blocks found after the trigger string in any files.")

if __name__ == "__main__":
    extract_code_blocks()
