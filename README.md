# Markdown to YAML Extractor

This is a small utility script designed to automate the process of extracting code blocks from Markdown files and saving them into YAML format.

It’s nothing too fancy, but it helps bridge the gap when you need to pull code examples out of documentation and into a structured data format.

> **Note:** This project was coded with the assistance of Gemini AI. While it is functional and tested for the current use case, there are likely areas for improvement or edge cases that haven't been caught yet.

## Features

* **Batch Processing:** Convert a whole folder of Markdown files into corresponding YAML files.
* **Single File Mode:** targeted extraction of a single file to a specific output name.
* **Custom Triggers:** You can define the specific text string (e.g., `## Solution`) that tells the script where to start looking for code.

## Setup

1. Make sure you have **Python** installed.
2. Install the required dependencies (currently just `PyYAML`):

```bash
pip install -r requirements.txt

```

## How to Use

The script `extract_cli.py` is run from the command line. It accepts three arguments:

* `-i` or `--input`: The path to a file or a folder of files.
* `-o` or `--output`: The destination path.
* `--trigger`: (Optional) The specific string to look for. Defaults to `## Solution`.

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

### 3. Changing the search trigger

If your markdown files use a different header or string to denote where the code starts (e.g., `### Code Example`), you can override the default:

```bash
python extract_cli.py -i ./docs -o ./output --trigger "### Code Example"

```

## Future Plans

I am planning to do more work on this as I learn more. Some features I'm hoping to add include:

* **Language Tags:** Preserving the language identifier (e.g., `python`, `js`) in the YAML output.
* **Format Options:** Adding support for exporting to JSON in addition to YAML.
* **Better Error Handling:** Making the script more robust when encountering badly formatted Markdown.

## License

Feel free to use this however you like!
