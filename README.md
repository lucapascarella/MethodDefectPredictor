# Method Defect Predictor

_Method Defect Predictor_ (MDP) contains a pool of scripts designed to perform a method-level just-in-time machine learning defect prediction. This project uses the [TensorFlow](https://www.tensorflow.org/) python library to implement a neural network used in the prediction. TMDP includes a pre-trained model created sampling last 2 years of the [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev) project.

## Usage
MDP contains a pre-trained dataset, however, a better model may be trained following these steps.
1. *Fix identification*. In this example, an external tool [bugbug](https://github.com/mozilla/bugbug) from [Mozilla](https://github.com/mozilla) has been used to define a list of commits containing the actual fixes in the project [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev).

##### Example
_data/fix_commits.csv_ contains the list of fixes identified with *bugbug*.

2. *Bug inducing commit*. _bic.py_ is a python script designed to identify the bug inducing commits of a given list of GIT commits.
_data/bic_commits.csv_ expands the previous list by adding the bug inducing commits (BIC) found with the SZZ algorithm embedded in [PyDriller](https://github.com/ishepard/pydriller).

##### Commands
```sh
python3 -r local/path/to/mozilla/gecko-dev -i data/fix_commits.csv -f fixes -o data/bic_commits.csv
```

To perform a method-level defect prediction the TensorFlow module has been trained with about 2 years of commits.

1. Create a proper dataset to train the model and perform an accurate defect prediction.



### Bug inducing commit extractor



## License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
 
[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)
 
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

### References
Sponsor: [LP Systems](https://lpsystems.eu/)
Author: [Luca Pascarella](https://lucapascarella.com/)