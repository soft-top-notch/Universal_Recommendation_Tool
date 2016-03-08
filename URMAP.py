# Copyright ActionML, LLC under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# ActionML licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 

from pyspark.sql import SQLContext
from pyspark.sql import functions as F
import numpy as np
import matplotlib.pyplot as plt
import ml_metrics as metrics
import predictionio

# Expects a header'd CSV file with columns: [entityId,event,targetEntityId]
def getDFfromCSV(csvName, sc):
    sqlContext = SQLContext(sc)
    df = sqlContext.read.format('com.databricks.spark.csv').options(header='true', quote='@').load(csvName)

    return df.withColumn('entityType', F.lit('user')).withColumn('targetEntityType', F.lit('item'))

def partitionAndSaveDF(df):
    seed = 92671
    traindf,testdf = df.distinct().randomSplit([0.8,0.2], seed)
    traindf.repartition(1).write.json("trainData.json")
    testdf.repartition(1).write.json("testData.json")

#Assumes PIO/UR up and running on localhost, trained with all event types
def calculateMAPAtOneToN(n, eventNames, sc):
    sqlContext = SQLContext(sc)
    engine_client = predictionio.EngineClient(url="http://localhost:8000")
    df = sqlContext.read.json("testData.json")
    data = df.collect()

    d = {}
    for i in data:
        #Assumes first event name is primary
        if i.event == eventNames[0]:
            k = i.entityId
            v = i.targetEntityId
            d.setdefault(k,[]).append(v)
    holdoutUsers = d.keys()

    prediction = []
    ground_truth = []
    for user in holdoutUsers:
        q = {
            "user": user,
            "eventNames": eventNames
        }
        try:
            res = engine_client.send_query(q)
            prediction.append([r["item"] for r in res["itemScores"]])
            ground_truth.append(d.get(user, []))
        except predictionio.NotFoundError:
            print("Error with user: %s" % user)

    #recs = [engine_client.send_query({"user": x, "eventNames": eventNames}) for x in holdoutUsers]
    #recslist = [[x['item'] for x in y['itemScores']] for y in recs]
    #heldoutList = d.values()
    return [metrics.mapk(ground_truth, prediction, k) for k in range(1, n + 1)]
    #return [metrics.mapk(heldoutList,recslist, x) for x in range(1,n + 1)]

# 'count' is overloaded, hence the rename
# log scale
def generateEntityDistPNG(df, entityColName, entity, eventName):
    counts = df.filter(df.event == eventName).groupBy('event', entityColName).count().select('count').withColumnRenamed('count','counter').collect()
    sortedCounts = sorted([ z.counter for z in counts])
    sortedCounts.reverse()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ## the data
    N = len(sortedCounts)
    ind = np.arange(N)                # the x locations for the groups
    width = 0.000005                     # the width of the bars

    ## the bars
    rects1 = ax.bar(ind, sortedCounts, width, log=True)
    ax.set_xlim(-width,len(ind)+width)
    ax.set_ylim(0,max(sortedCounts))
    ax.set_ylabel(eventName + ' events')
    ax.set_title(eventName + ' events by ' + entity)
    plt.savefig(entity + "dist.png")
