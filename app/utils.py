import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from flask import jsonify

# Function to return a session with retries configured
def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# A function to help create the error dict.
def get_error(message, code):
    """Returns a json containing an error with a message and its code """
    error = {"error": {"message": message, "code": code}}
    return error


# Generate the json from objects and, in case the clinic service doesn't respond,
# change the format to accomodate the data
def generate_json_for_metrics(patient, physician, clinic=None):

    if isinstance(clinic, str) or isinstance(clinic, int):
        metrics = {
            "clinic_id": clinic,
            "clinic_name": "",
            "physician_id": physician.id,
            "physician_name": physician.fullname,
            "physician_crm": physician.crm,
            "patient_id": patient.id,
            "patient_name": patient.fullname,
            "patient_email": patient.email,
            "patient_phone": patient.phone,
        }
        return json.dumps(metrics)

    else:
        metrics = {
            "clinic_id": clinic.id,
            "clinic_name": clinic.name,
            "physician_id": physician.id,
            "physician_name": physician.fullname,
            "physician_crm": physician.crm,
            "patient_id": patient.id,
            "patient_name": patient.fullname,
            "patient_email": patient.email,
            "patient_phone": patient.phone,
        }
        return json.dumps(metrics)
