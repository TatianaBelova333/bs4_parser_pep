# Python and PEP documentation parser.

## Description
This parser parses data from https://docs.python.org/3/ и https://peps.python.org/.

## Installation
- Clone the repository
  ```
  git clone https://github.com/TatianaBelova333/bs4_parser_pep.git
  ```
- Install all dependencies and activate virtual enironment
  ```
  python -m venv venv
  ```
  ```
  pip install -r requirements.txt
  ```
- Navigate from the project root directory to src folder:
  ```
  cd src/
  ```
- To start the parser, run the following command
  ```
  python main.py [mode] [args]
  ```

### Parser mode arguments
* whats-new \
  Parses url links to the information on updates in each python version.

  ```
  python main.py whats-new [args]
  ```
* latest_versions \
  Parses statuses and url links to documentation for each Python version.
  ```
  python main.py latest-versions [args]
  ```
* download \
  Downloads zip archive with Python documenttion in pdf format.
  ```
  python main.py download [args]
  ```
* pep \
  Parses all PEP documentation statuses and the number of documents for each status.
  ```
  python main.py pep [args]
  ```

### Other arguments
The parser has the following arguments. \
  *-h, --help 
  General info about all arguments.
  ```
  python main.py -h
  ```
  *--c, --clear-cache \
  Cache clearing before parsing.
  ```
  python main.py [mode] -c
  ```
  * -o {pretty,file}, --output {pretty,file}
  Additional output options. \
  pretty - prints the data in the terminal in a table format \
  file - saves the data in csv format in the RESULT_DIR folder.

### Authors
[Tatiana Belova](https://github.com/TatianaBelova333)
