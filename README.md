# Markdown to YAML Extractor

This is a small utility script designed to automate the process of extracting code blocks from Markdown files and saving them into YAML format.

It’s nothing too fancy, but it helps bridge the gap when you need to pull code examples out of documentation and into a structured data format.

> **Note:** This project was coded with the assistance of Gemini AI. While it is functional and tested for the current use case, there are likely areas for improvement or edge cases that haven't been caught yet.

## Features

* **Batch Processing:** Convert a whole folder of Markdown files into corresponding YAML files.
* **Single File Mode:** Targeted extraction of a single file to a specific output name.
* **Custom Triggers:** Define specific text strings or a list of strings (e.g., `## Solution`) to locate code blocks.
* **Multiple Blocks:** Extract every code block after a trigger using `-a` or `--all`.
* **Concatenation:** Combine multiple extracted blocks into one YAML file using `-c` or `--concat`.
* **Output Placeholders:** Use `{filename}` and `{firstword}` in output paths for dynamic file naming.

## Setup

1. Make sure you have **Python** installed.
2. Install the required dependencies (currently just `PyYAML`):

```bash
pip install -r requirements.txt
```

## How to Use

The script `extract_cli.py` is run from the command line. It accepts several arguments:

* `-i` or `--input`: The path to a file or a folder of files.
* `-o` or `--output`: The destination path (supports `{filename}` and `{firstword}` placeholders).
* `--trigger`: (Optional) The string(s) to look for. Defaults to `YAML`. 
    * Single trigger: `--trigger "## Solution"`
    * Multiple triggers: `--trigger "([Trigger 1], [Trigger 2])"`
* `-a` or `--all`: (Optional) Extract all code blocks found after the trigger.
* `-c` or `--concat`: (Optional) When using `-a`, combine all blocks into a single YAML file instead of splitting them.

### 1. Processing a specific file

Use this if you want to convert one `.md` file into one specific `.yaml` file.

```bash
python extract_cli.py -i ./docs/my_notes.md -o ./exports/output_data.yaml
```

### 2. Processing a whole folder (Batch)

Use this if you have a directory of markdown files. The script will create a YAML file for every Markdown file found.

```bash
# Takes all .md files in 'raw_docs' and saves .yaml files to 'processed_data'
python extract_cli.py -i ./raw_docs -o ./processed_data
```

### 3. Extracting Multiple Blocks

If a file has multiple code blocks after a trigger, use `-a` to get them all. By default, they are saved as separate files (`output.yaml`, `output_2.yaml`, etc.).

```bash
python extract_cli.py -a -i ./docs/file.md -o ./output/data.yaml
```

### 4. Concatenating Blocks

To combine all blocks from one file into a single multi-document YAML file:

```bash
python extract_cli.py -a -c -i ./docs/file.md -o ./output/combined.yaml
```

### 5. Using Multiple Triggers

You can search for multiple different markers in the file:

```bash
python extract_cli.py --trigger "([Metadata], [Configuration])" -i ./docs -o ./output
```

## Examples

### Dynamic Batch Output
```bash
python extract_cli.py -a -i ./docs -o ./output/{filename}/output.yaml
```

**Structure:**
```
docs/
├── file1.md (contains 2 blocks)
└── file2.md (contains 1 block)

output/
├── file1/
│   ├── output.yaml
│   └── output_2.yaml
└── file2/
    └── output.yaml
```

### Concatenated Batch Output
```bash
python extract_cli.py -a -c -i ./docs -o ./output/{filename}_all.yaml
```

**Structure:**
```
docs/
├── file1.md (contains 2 blocks)
└── file2.md (contains 1 block)

output/
├── file1_all.yaml (multi-document YAML)
└── file2_all.yaml
```

## Future Plans

I am planning to do more work on this as I learn more. Some features I'm hoping to add include:

* **Language Tags:** Preserving the language identifier (e.g., `python`, `js`) in the YAML output.
* **Format Options:** Adding support for exporting to JSON in addition to YAML.
* **Better Error Handling:** Making the script more robust when encountering badly formatted Markdown.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
