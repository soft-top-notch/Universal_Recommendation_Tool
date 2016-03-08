# MAP @ k test for implicit feedback

`data_preparation.ipynb` should be run under pyspark in ipython notebook mode: 

`IPYTHON_OPTS="notebook" ~/PredictionIO/vendors/spark-1.5.1/bin/pyspark --packages com.databricks:spark-csv_2.10:1.3.0`

It loads event data ('fresh', 'rotten') and produces train and test datasets. Train dataset then can be directly imported to PredictioIO: 

`pio import --appid <AppID> --input train_events.json`

And test dataset is then used by `perform_test.py` to query and recommender service and calculate MAP @ k (k = 1..20)