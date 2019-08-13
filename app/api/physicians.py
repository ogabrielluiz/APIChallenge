from app.utils import requests_retry_session
from flask_restful import Resource
import requests
import requests_cache
import os
from datetime import timedelta
from app.utils import get_error
from flask import jsonify


class PhysicianAPI(Resource):
    def get(self, physician_id):

        requests_cache.install_cache(
            cache_name="APIcache", backend="sqlite", expire_after=timedelta(days=2)
        )
        # Calling environment variable for the authorization header
        headers = dict(Authorization="Bearer " + os.environ.get("PHYSICIAN_BEARER"))
        # Setting up some variables to use on the request
        timeout = 4
        url = "https://cryptic-scrubland-98389.herokuapp.com/v2/physicians/"
        if isinstance(physician_id, int):
            try:
                r = requests_retry_session(retries=2).get(
                    url + str(physician_id), headers=headers, timeout=timeout
                )
            except Exception as e:
                return ("We have a problem.", e.__class__.__name__)

            if r.status_code == 200:

                return r.json(), 200
            elif r.status_code == 408:
                return get_error("Request Timeout", "07")
            elif r.status_code == 503:
                return get_error("physicians service not available", "05")
            elif r.status_code == 404:
                return get_error("physician not found", "02")
        else:
            return "malformed requests", "01"
