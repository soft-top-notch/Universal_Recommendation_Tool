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

import predictionio
import ml_metrics as metrics
import argparse


DATA_FILE = "test_data.txt"
ENGINE_URL = "http://0.0.0.0:8000"

N = 20

def read_data(file_name):
    d = {}
    with open(file_name, "r") as f:
        for line in f:
            user_id, movie_id = line.rstrip('\n').split(",")
            user_id = user_id.strip()
            movie_id = movie_id.strip()
            if (user_id != "") and (movie_id != ""):
                d.setdefault(user_id, []).append(movie_id)
        f.close()
    return d

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='MAP @ k tester', description='...')
    parser.add_argument('event_names', metavar='eventNames', type=str, nargs="+",
                   help='List of evenNames')

    parser.add_argument('--test', action='store_true',
        help='Query only few samples')

    args = parser.parse_args()
    eventNames = args.event_names
    #eventNames = ["like"]

    d = read_data(DATA_FILE)
    test_users = d.keys()
    engine_client = predictionio.EngineClient(url=ENGINE_URL)

    if args.test:
        test_users_sbs = test_users[0:10]
    else:
        test_users_sbs = test_users


    prediction = []
    ground_truth = []

    for user in test_users_sbs:
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

    fres = [metrics.mapk(ground_truth, prediction, k) for k in range(1, N + 1)]

    print("")
    print(eventNames)
    for i, score in enumerate(fres):
        print("%d %lf" % (i + 1, score))
