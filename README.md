# Method Defect Predictor

_Method Defect Predictor_ (MDP) is a open-source project designed to perform a method-level just-in-time machine learning defect prediction. It contains a pool of scripts and uses the [TensorFlow](https://www.tensorflow.org/) python library to implement a neural network used in the prediction. Moreover, MDP includes a pre-trained model created sampling last 2 years of the [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev) project.

## Usage
MDP contains a pre-trained dataset, however, a better model may be created following this guide.

### 1. Fix identification
In this example, an external tool [bugbug](https://github.com/mozilla/bugbug) from [Mozilla](https://github.com/mozilla) has been used to define a list of commits containing the actual fixes in the project [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev).
_data/fix_commits.csv_ contains the list of fixes identified with *bugbug*.

### 2. Bug inducing commit 
_bic.py_ is a python script designed to identify the bug inducing commits starting from a given list of GIT commits.

##### Commands
```sh
python3 bic.py -r local/path/to/mozilla/gecko-dev -i data/fix_commits.csv -f fixes -o data/bic_commits.csv
```
_data/bic_commits.csv_ uses the list contained in _data/fix_commits.csv_ to identify the bug inducing commits (BIC). _bic.py_ relays on the SZZ algorithm embedded in [PyDriller](https://github.com/ishepard/pydriller) to identify the bug inducing commits.


### 3. Metrics extractor
To perform a method-level defect prediction the TensorFlow module has been trained with about 2 years of commits. We used product and process metrics to characterize c++ code methods.

_extractor.py_ is a python script designed for calculating a set of code metrics for each method of each file of each commit. So, it requires time to collect data.

##### Commands
```sh
python3 extractor.py -r local/path/to/mozilla/gecko-dev -s 49dbdb7f535106aa96e952222fd42ea6b91074fb -p 5192e340815e9aad5a59b350b9772319e4518417 -i data/bic_commits.csv -o data/method_metrics.csv
```




## License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
 
[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)
 
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

### References
Sponsor: [LP Systems](https://lpsystems.eu/)
Author: [Luca Pascarella](https://lucapascarella.com/)