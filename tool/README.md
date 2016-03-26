# Analysis script

Use this command to run:
```
IPYTHON_OPTS="notebook" /usr/local/spark/bin/pyspark --master spark://spark-url:7077
```

It's also necessary to install python packages:

	- numpy
	- scipy
	- pandas
	- ml_metrics
	- predictionio
	- tqdm
    - click
    - openpyxl

SPARK_HOME=/usr/local/spark PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.9-src.zip ./map_test.py split --intersections
