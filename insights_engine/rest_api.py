import json
import logging

import connexion
from connexion import NoContent
import daiquiri

daiquiri.setup(level=logging.WARNING)
logger = daiquiri.getLogger(__name__)


def companion_recommendation(stack):
    """Endpoint for the  main companion recommendation endpoint that serves incoming requests."""
    # TODO
    return json.dumps({}), 200


def liveness():
    """Endpoint with the implementation of hhe liveness probe."""
    return NoContent, 200


def readiness():
    """Endpoint with the implementation the readiness probe."""
    logger.debug("Service up and ready to serve requests.")
    return NoContent, 200


app = connexion.App(__name__, specification_dir='swagger/')
app.add_api('swagger.yaml')


if __name__ == '__main__':
    # running in development mode
    app.run(port=6006, debug=True)
