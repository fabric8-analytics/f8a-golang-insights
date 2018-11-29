#!/bin/bash

gunicorn rest_api:app --pythonpath /insights_engine -b 0.0.0.0:$SERVICE_PORT --workers=2 -k sync -t $SERVICE_TIMEOUT
