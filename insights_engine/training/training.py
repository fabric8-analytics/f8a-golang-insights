#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mine and store the association rules that'll be used to make the recommendations.

Copyright © 2018 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import logging
import os
import time
import datetime

import daiquiri
from pyspark.ml.fpm import FPGrowth
from pyspark.sql import SparkSession

import insights_engine.config as config
from insights_engine.data_store.s3_data_store import S3DataStore

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)
logging.getLogger('botocore').setLevel(level=logging.ERROR)
logging.getLogger('boto3').setLevel(level=logging.ERROR)

s3_bucket = S3DataStore(config.S3_BUCKET_NAME, config.AWS_S3_ACCESS_KEY_ID,
                        config.AWS_S3_SECRET_ACCESS_KEY)

# Load our data.
golang_manifests = s3_bucket.read_json_file(config.NORMALIZED_MANIFEST_PATH)

logger.info("Training with %d manifests" % (len(golang_manifests)))

package_to_index_map = {}
index_to_pacakge_map = {}
next_i = 0

package_ingestion_list = s3_bucket.read_generic_file(config.PACKAGE_INGESTION_LIST)

for next_p in package_ingestion_list.split('\n'):
    next_p = next_p.strip()
    package_to_index_map[next_p] = next_i
    index_to_pacakge_map[next_i] = next_p
    next_i += 1


encoded_manifests = []

for manifest in golang_manifests:
    encoded_manifests.append([package_to_index_map[pkg] for pkg in manifest])

encoded_manifests = [list(set(manifest)) for manifest in encoded_manifests]
spark = SparkSession.builder.appName("golang_recommender").getOrCreate()
df_rows = []
for idx, man in enumerate(encoded_manifests):
    df_rows.append((idx, man))
df = spark.createDataFrame(df_rows, ["id", "packages"])

# Train the FP-growth model
fpGrowth = FPGrowth(itemsCol="packages", minSupport=config.MIN_SUPPORT,
                    minConfidence=config.MIN_CONFIDENCE)
logger.info("Association rule mining started at %s" % time.ctime())
model = fpGrowth.fit(df)
logger.info("Association rule mining ended at %s" % time.ctime())
logger.info("Mined %d rules" % model.associationRules.count())

# Get the model as json
rule_json = model.associationRules.toJSON().collect()

# Now get the rules in a pandas dataframe
rules_df = model.associationRules.toPandas()

with open(config.ASSOCIATION_RULE_JSON, 'w') as f:
    json.dump(rule_json, f)

with open(config.PACKAGE_IDX_MAPS, 'w') as f:
    json.dump({"package_to_index_map": package_to_index_map,
               "index_to_package_map": index_to_pacakge_map}, f)

# Now save the dataframe from Pandas
rules_df.to_pickle(config.ASSOCIATION_RULES_DF)

# Upload files to S3

trained_date = datetime.datetime.now().strftime('%Y-%m-%d')
s3_bucket.upload_file(config.ASSOCIATION_RULE_JSON,
                      os.path.join(config.ECOSYSTEM, config.DEPLOYMENT_PREFIX, trained_date,
                                   config.ASSOCIATION_RULE_JSON))
s3_bucket.upload_file(config.ASSOCIATION_RULES_DF,
                      os.path.join(config.ECOSYSTEM, config.DEPLOYMENT_PREFIX, trained_date,
                                   config.ASSOCIATION_RULES_DF))
s3_bucket.upload_file(config.PACKAGE_IDX_MAPS,
                      os.path.join(config.ECOSYSTEM, config.DEPLOYMENT_PREFIX, trained_date,
                                   config.PACKAGE_IDX_MAPS))
