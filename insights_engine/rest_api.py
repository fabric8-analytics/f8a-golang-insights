"""Implementation of the REST API for the PyPi insights service."""

import json
import logging

import connexion
from connexion import NoContent
import daiquiri

from insights_engine.data_store.s3_data_store import S3DataStore
from insights_engine.data_store.local_filesystem import LocalFileSystem
from insights_engine import config as config
from insights_engine.scoring.rules_predict import ScoringEngine

daiquiri.setup(level=logging.INFO)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logger = daiquiri.getLogger(__name__)


def liveness():
    """Endpoint with the implementation of hhe liveness probe."""
    return NoContent, 200


def readiness():
    """Endpoint with the implementation the readiness probe."""
    try:
        if config.USE_AWS == "True":
            S3DataStore(config.S3_BUCKET_NAME, config.AWS_S3_ACCESS_KEY_ID,
                        config.AWS_S3_SECRET_ACCESS_KEY)
        else:
            LocalFileSystem(config.S3_BUCKET_NAME)
        logger.info("Service up and ready to serve requests.")
    except Exception as e:
        logger.critical("Could not bring up service.")
        logger.critical(e)
        return NoContent, 500
    return NoContent, 200


# Create a global recommender instance- this has to be global or else we would overload S3
recommender = ScoringEngine()


def companion_recommendation():
    """Endpoint for the  main companion recommendation endpoint that serves incoming requests."""
    response_json = []
    for recommendation_request in connexion.request.json:
        missing, recommendations = recommender.predict(
            recommendation_request['package_list'],
            companion_threshold=recommendation_request['comp_package_count_threshold'])
        response_json.append({
            "missing_packages": missing,
            "companion_packages": recommendations,
            "ecosystem": "golang",  # Hardcoding because I don't think this is reqd. elsewhere
            "package_to_topic_dict": {}  # We don't have any topics here, use Kronos if you do.
        })
    return json.dumps(response_json), 200


app = connexion.App(__name__, specification_dir='swagger/')
app.add_api('swagger.yaml')


if __name__ == '__main__':
    # running in development mode
    app.run(port=6006, debug=True)
