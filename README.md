# Method Defect Predictor

_Method Defect Predictor_ (MDP) is a open-source project designed to perform a _method-level_ _just-in-time_ _machine-learning_ defect prediction.
It consists of a pool of scripts that advises when the latest committed methods are prone to be defective.
The machine learning algorithm relays on two different solutions. The first uses the [TensorFlow](https://www.tensorflow.org/) python library to implement a neural network used by our algorithm. The second uses [XGBoost](https://xgboost.readthedocs.io/en/latest/) python library to implement a machine learning model to predict defects. 
Since performance between the two solutions are comparable we choose XGBoost because it is a bit faster during the training. MDP includes a pre-trained model created sampling the last two years of the publicly available [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev) project.

## Usage
MDP contains a pre-trained dataset, however, a better model may be created following this guide.

### 1. Identification of fixes
In this example, an external tool [bugbug](https://github.com/mozilla/bugbug) from [Mozilla](https://github.com/mozilla) has been used to define a list of commits containing the actual fixes in the project [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev).

```data/fix_commits.csv``` contains a pre-mined list of fixes identified with *bugbug*.

### 2. Bug inducing commits 
```bic.py``` is a python script designed to identify _bug inducing commits_ (BIC) starting from a list of GIT commits. This tool relies on git hyper blame to ignore a specified list of commits that may contain huge refactoring. 
Git Hyper Blame is a git extension available belonging to [Chromium tools](https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/git-hyper-blame.html).
To use pydriller with git hyper blame install it locally with ```git clone https://chromium.googlesource.com/chromium/tools/depot_tools```
However, the git hyper blame cuts the blame hash to 8 characters, this creates collisions in huge repositories.  

##### Command example
```sh
python3 bic.py -r local/path/to/mozilla/gecko-dev -i data/fix_commits.csv -f fix_hash -o data/bic_commits.csv -n /example/data/ignore_commits.txt
```
```data/bic_commits.csv``` uses the list of fix commits contained in ```data/fix_commits.csv``` to identify the bug inducing commits (BIC). Deeply, ```bic.py``` relays on the SZZ algorithm embedded in [PyDriller](https://github.com/ishepard/pydriller) to recreate a list of bug inducing commits for each fix commit.
It also uses git hyper blame if it is available on your machine, before running ```bic.py``` export git hyper-blame in PATH environment variables

The following is an example for Unix machines  
```sh
export PATH=$PATH:path/to/hyper-blame/folder
```

The ```-n``` option requires a *full path* to the ignore file containing the list of hashes to ignore.



### 3. Metrics extractor
To perform a method-level defect prediction the TensorFlow or GXBoost module has been trained with about two years of GIT commits. We use both product and process metrics to characterize c++ methods of the [Mozilla gecko-dev](https://github.com/mozilla/gecko-dev) project.

```extractor.py``` is a python script designed for calculating a set of code metrics for each method of each file of each commit. So, it requires time to collect all these data.

##### Command example
```sh
python3 extractor.py -r local/path/to/mozilla/gecko-dev -s 5192e340815e9aad5a59b350b9772319e4518417 -p d411f2814cc535b9a440bec670e08d37712b63c9 -i data/bic_commits.csv -o data/method_metrics.csv
```
```data/method_metrics.csv``` contains the output of ```extractor.py```. In details, it is a huge collection of metrics for every method at both product and process level.


### 4. Machine learning trainer
In this project we use the [TensorFlow](https://www.tensorflow.org/) python library for creating a neural network model. On the top, we relay on the [Keras](https://keras.io/) python layer that provides a simplified abstract API to create, train, and test neural networks.

```keras.py``` is python script designed to create and train our neural network model. It requires a few mandatory inputs such as the path of the dataset and the path where save the TensorFlow built model.

##### Command example
```sh
python3 keras.py -i data/method_metrics_cleaned.csv
```

### 5. Machine learning prediction
At this point, we can run the predictor. In this project we use the [XGBoost](https://xgboost.readthedocs.io/en/latest/) python library for creating a machine learning model.

```tester.py``` is python script designed to predict our machine learning model. It requires a few mandatory inputs such as the path of the pre-trained model, the start and stop commits.

##### Command example
```sh
python3 tester.py -r local/path/to/mozilla/gecko-dev -s db6ecd1b6eb514cc5bf327d101d5cf861dd73926 -p 11fbfb6d5381726bbc55472bbf0b816d9859ee79 -m pre-trained-model
```


## License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
 
[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)
 
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

### References
<!--- (Sponsor: [LP Systems](https://lpsystems.eu/) -->
Author: [Luca Pascarella](https://lucapascarella.com/)