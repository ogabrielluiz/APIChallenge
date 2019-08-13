from app.utils import requests_retry_session
from flask_restful import Resource
import requests
import requests_cache
import os
from datetime import timedelta
from flask import jsonify
from app.utils import get_error


class ClinicAPI(Resource):
    def get(self, clinic_id):

        requests_cache.install_cache(
            cache_name="APIcache", backend="sqlite", expire_after=timedelta(hours=12)
        )
        # Calling environment variable for the authorization header
        headers = dict(Authorization="Bearer " + os.environ.get("CLINIC_BEARER"))
        # Setting up some variables to use on the request
        timeout = 3
        url = "https://agile-earth-43435.herokuapp.com/v1/clinics/"

        if isinstance(clinic_id, int):
            try:
                r = requests_retry_session(retries=2).get(
                    url + str(clinic_id), headers=headers, timeout=timeout
                )
            except Exception as e:
                return ("We have a problem.", e.__class__.__name__)

            if r.status_code == 200:

                return r.json(), 200
            elif r.status_code == 408:
                return get_error("Request Timeout", "07")
            elif r.status_code == 503:
                return get_error("clinics service not available", "08")
            elif r.status_code == 404:
                return get_error("clinic not found", "09")
        else:
            return get_error("malformed requests", "01")
