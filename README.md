# Model curation process

A python module for the model curation process in the HBP. It curates entries from their submission in the Model Catalog to their publications in the HBP Knowledge Graph.

## Curation schematic (current pipeline)

![schematic](docs/process.svg)

## Dependencies

Two python modules of the Human Brain Project ecosystem:

- ![fairgraph](https://github.com/HumanBrainProject/fairgraph) A high-level Python API for the HBP Knowledge Graph
- ![hbp-validation-client](https://github.com/HumanBrainProject/hbp-validation-client) A Python package for working with the Human Brain Project Model Validation Framework.

Python APIs for working with Google Spreadsheets:

- ![Google Spreadsheet API](https://developers.google.com/sheets/api)
- ![gspread](https://github.com/burnash/gspread)

