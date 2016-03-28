# Analysis script

In order to run MAP analysis some prerequisites are necessary:

- PredictionIO with all necessary dependencies (use ActionML recommended setup)
- Data file to run test with (should be in PredictionIO export/import JSON format)
- Properly configured universal recommender template

Analysis script is written in Python and should be run with Apache Spark. So make sure that Spark is correctly configured and cluster resources are available for script when you run it.

Python packages to be present:

- numpy
- scipy
- pandas
- ml_metrics
- predictionio
- tqdm
- click
- openpyxl

Analysis script should be run from UR (Universal recommender) folder. And it uses two configuration files:

- engine.json (configuration of UR, this file is used to take event list and primary event)
- config.json (all other configuration including engine.json path if necessary)

###Configuration options

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
- __testing__ - this section is about different tests and how to perform them 
	- __map_k__ - maximum map @ k to be reported
	- __non_zero_users_file__ - file to save users with scores != 0 after first run of test set with primary event, this set may be much smaller then initial set of users so saving it and reusing can save much time
	- __consider_non_zero_scores_only__ (default: true) whether take into account only users with non-zero scores (i.e. users for which recommendations exist)
	- __custom_combos__
		- __event_groups__ - groups of events to be additionally tested if necessary
- __spark__ - Apache Spark configuration
	- __master__ - for now only master URL is configurable

	
Use this command to run split of data:

```
SPARK_HOME=/usr/local/spark PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.9-src.zip ./map_test.py split
```

To run tests
```
SPARK_HOME=/usr/local/spark PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.9-src.zip ./map_test.py test --all
```

Additional options are available and may be used to run not all test:

- --dummy_test - run dummy test
- --separate_test - run test for each separate event
- --all_but_test - run test with all events and tests with all but each every event
- --primary_pairs_test - run tests with all pairs of events with primary event
- --custom_combos_test - run custom combo tests as configured in config.json
- --non_zero_users_from_file - use list of users from file prepared on previous script run to save time 


###Old ipython analysis script
This is not recommended old approach to run ipython notebook.
```
IPYTHON_OPTS="notebook" /usr/local/spark/bin/pyspark --master spark://spark-url:7077
```
