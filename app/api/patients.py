from app.utils import requests_retry_session
from flask_restful import Resource
import requests
import requests_cache
import os
from datetime import timedelta
from flask import jsonify
from app.utils import get_error


class PatientAPI(Resource):
    def get(self, patient_id):

        requests_cache.install_cache(
            cache_name="APIcache", backend="sqlite", expire_after=timedelta(days=3)
        )
        # Calling environment variable for the authorization header
        headers = dict(Authorization="Bearer " + os.environ.get("PATIENT_BEARER"))
        # Setting up some variables to use on the request
        timeout = 3
        url = "https://limitless-shore-81569.herokuapp.com/v3/patients/"
        if isinstance(patient_id, int):
            try:
                r = requests_retry_session(retries=2).get(
                    url + str(patient_id), headers=headers, timeout=timeout
                )
            except Exception as e:
                return ("We have a problem.", e.__class__.__name__)

            if r.status_code == 200:

                return r.json(), 200
            elif r.status_code == 408:
                return get_error("Request Timeout", "07")
            elif r.status_code == 503:
                return get_error("patients service not available", "06")
            elif r.status_code == 404:
                return "patient not found", "03"
        else:
            return get_error("malformed requests", "01")
