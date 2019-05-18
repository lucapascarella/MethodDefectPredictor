# Method Defect Predictor

Method Defect Predictor (MDP) is a pool of scripts designed to perform a method-level just-in-time machine learning defect prediction.

## Usage
To train the model and performing an accurate prediction a proper dataset with low noise must be used.
In the specific case of this example, an external tool [bugbug](https://github.com/mozilla/bugbug) from [Mozilla](https://github.com/mozilla) has been used to identify a list of commits containing the actually fixes in the project [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev).

The file _xxx.csv_ contains the list of fixes identified with *bugbug* tool.
The file _yyy.csv_ expands the previous list by adding the bug inducing commits (BIC) evaluate with the SZZ algorithm embedded in [PyDriller](https://github.com/ishepard/pydriller).

### Bug inducing commit extractor
The python file _bic.py_ contains a simplified script designed to identify the bug inducing commits of a given commit HASH.

##### Usage Example
```sh
python3 -r path/to/local/git/repo -i input_file.csv -f fixes -o bic.csv
```