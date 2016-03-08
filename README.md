# MAP-Test

install Spark / pyspark:

1) Assuming you have PIO working, you have spark installed somewhere.


Add the following to your .bashrc or equivalent
```
export SPARK_HOME={WHEREVER}/PredictionIO/vendors/spark-1.5.1

export PYTHONPATH=$SPARK_HOME/python/:$SPARK_HOME/python/build/:$PYTHONPATH

```

then

```
source ~/.bashrc
```

or open a new terminal


You also need Python2, numpy, matplotlib, predictionio and ml_metrics.

I'd advise installing Anaconda2 : https://www.continuum.io/downloads

Then you can either :

```
conda install X
```

or 

```
pip install X
```

the modules you need.


invoke from within pyspark, in this repo directory, pass in the SparkContext where needed

Example usage:

```
pyspark --packages com.databricks:spark-csv_2.10:1.2.0 
```

```
from URMAP import *
dataFrame = getDFfromCSV("RT.csv",sc)
partitionAndSaveDF(dataFrame)
mapAtOneToTen = calculateMAPAtOneToN(10,["fresh","rotten"],sc)
generateEntityDistPNG(dataFrame, "targetEntityId", "item", "fresh")
```

You now have a reproducible data split, the MAP values using held-out events, and a PNG image displaying the number of fresh events per item, for all items in descending order, log scale. 
