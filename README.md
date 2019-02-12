# Universal Recommender Analysis Tool V2

The primary change to V2 of the tool is to simplify by integrating all external processes so one line will execute all steps.

The steps to execute all workflow are:

 1. **Verify the PIO EventServer is running** `pio status` will do this.
 2. **Export Data** We assume that the data exists in the EventServer or in HDFS. Export the data to the location specified in the `config.json` file.  
 3. **Split** the data using the `map_test split` directive. It is often desirable to use an existing data split so the split step can be omitted.
 4. **Train and Deploy** To do this 3 PIO workflow steps need to be taken. These must be executed inside the directory of the UR version we are testing.
    1. **`pio build`** This will create the Universal Recommender code and register the algorithm parameters
    2. **`pio train`** This will create a model with the UR from the `engine.json` parameters. There are parameters in engine.json that are passed to Spark in the training process that are system and data dependent so make sure train completes correctly before moving on. Using these tools usually happens after the bootstrap dataset has be3en successfully trained so the split is made on the dataset.
    3. **`pio deploy`** This will create a running PIO PredictionServer that responds to UR queries based on the training split of the dataset.
 5. **Analyze** Same as Alexey's #3   

# Setup

Install Spark, PredictionIO v0.11.0 or greater, and the Universal Recommender v0.7.3 or greater. Make sure `pio status` completes with no errors and the integration-test for the UR runs correctly.

 1. Install Python and check the version

 	`python --v`

 	if the version is less than 2.7.9 upgrade to the most recent stable version of python using systems package management tools like `apt-get` for Ubuntu linux or `brew` for the macOS. This tool has not been tested with Python 3 so stick with Python 2.7

 2. Install Python libraries using the Python package manager found [here](https://pip.pypa.io/en/stable/installing/)

 	```
 	sudo pip install numpy scipy pandas ml_metrics predictionio tqdm click openpyxl
 	```

 3. Setup Spark and Pyspark paths in `.bashrc` (linux) or `.bash_profile` macOS.

 	```
 	export SPARK_HOME=/path/to/spark
	export PYTHONPATH=$SPARK_HOME/python/:$SPARK_HOME/python/build/:$PYTONPAHTH
	```

# Run Analysis Script

Analysis script should be run from UR (Universal recommender) folder. It uses two configuration files:

- `engine.json` (configuration of UR, this file is used to take event list and primary event)
- `config.json` (all other configuration including engine.json path if necessary)

## Configuration options

config.json has the following structure:

```
{
  "engine_config": "./engine.json",

  "splitting": {
    "version": "1",
    "source_file": "hdfs:...<PUT SOME PATH>...",
    "train_file": "hdfs:...<PUT SOME PATH>...train",
    "test_file": "hdfs:...<PUT SOME PATH>...test",
    "type": "date",
    "train_ratio": 0.8,
    "random_seed": 29750,
    "split_event": "<SOME NAME>"
  },

  "reporting": {
    "file": "./report.xlsx"
  },

  "testing": {
    "map_k": 10,
    "non_zero_users_file": "./non_zero_users.dat",
    "consider_non_zero_scores_only": true,
    "custom_combos": {
      "event_groups": [["ev2", "ev3"], ["ev6", "ev8", "ev9"]]
    }
  },

  "spark": {
    "master": "spark://<some-url>:7077"
  }
}
```

- __engine_config__ - file to be used as engine.json (see configuration of UR)
- __splitting__ - this section is about splitting data into train and test sets
	- __version__ - version to append to train and test file names (may be helpful is different test with different split configurations are run)
	- __source_file__ - file with data to be split
	- __train_file__ - file with training data to be produced (note that version will be append to file name)
	- __test_file__ - file with test data to be produced (note that version will be append to file name)
	- __type__ - split type (can be time in this case eventTime will be used to make split or random)
	- __train_ratio__ - float in (0..1), share of training samples
	- __random_seed__ - seed for random split
	- __split_event__ - in case of __type__ = "date", this is event to use to look for split date, all events with this name are ordered by eventTime and time which devides all such events into first __train_ratio__ and last (1 - __train_ratio__) sets is used to split all the rest data (events with all names) into training set and test set
- __reporting__ - reporting settings
	- __file__ - excel file to write report to
  - __csv_dir__ - directory name for csv reporting
  - __use_uuid__ - append to csv file names unique uuid associated with script run (can be useful to manage different results and reports)
- __testing__ - this section is about different tests and how to perform them
	- __map_k__ - maximum map @ k to be reported
	- __non_zero_users_file__ - file to save users with scores != 0 after first run of test set with primary event, this set may be much smaller then initial set of users so saving it and reusing can save much time
	- __consider_non_zero_scores_only__ (default: true) whether take into account only users with non-zero scores (i.e. users for which recommendations exist)
	- __custom_combos__
		- __event_groups__ - groups of events to be additionally tested if necessary
- __spark__ - Apache Spark configuration
	- __master__ - for now only master URL is configurable

## Split the Data

Get data from the EventServer with:

	pio export --output path/to/store/events

Use this command to run split of data into "train" and "test" sets

```
SPARK_HOME=/usr/local/spark PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.9-src.zip ./map_test.py split
```

Additional options are available:

- `--csv_report` - put report to csv file not excel
- `--intersections` - calculate train / test event intersection data (**Advanced**)

## Train a Model

The above command will create a test and training split in the location specified in config.json. Now you must import, setup engine.json, train and deploy the "train" model so the rest of the MAP@k tests will be able to query the model.

## Test and Analysis

To run tests
```
SPARK_HOME=/usr/local/spark PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.9-src.zip ./map_test.py test --all
```

Additional options are available and may be used to run not all test:

- `--csv_report` -
- `--dummy_test` - run dummy test
- `--separate_test` - run test for each separate event
- `--all_but_test` - run test with all events and tests with all but each every event
- `--primary_pairs_test` - run tests with all pairs of events with primary event
- `--custom_combos_test` - run custom combo tests as configured in config.json
- `--non_zero_users_from_file` - use list of users from file prepared on previous script run to save time

## Generated Report

Todo

### Old ipython analysis script
This is not recommended old approach to run ipython notebook.
```
IPYTHON_OPTS="notebook" /usr/local/spark/bin/pyspark --master spark://spark-url:7077
```
