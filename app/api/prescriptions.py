from flask import current_app
from app import db
from app.utils import requests_retry_session
from flask_restful import Resource
import requests
import requests_cache
import os
from datetime import timedelta
from flask import jsonify, request
import json

from app.utils import get_error, generate_json_for_metrics
from app.models import Patient, Physician, Clinic, Prescription


class PrescriptionAPI(Resource):
    def post(self):
        # Initializing Requests_cache with the expire_after config
        requests_cache.install_cache(
            cache_name="APIcache", backend="sqlite", expire_after=timedelta(hours=12)
        )
        # Calling environment variable for the authorization header
        headers = {"Authorization": "Bearer " + os.environ.get("METRICS_BEARER")}
        # Setting up some variables to use on the request
        timeout = 6
        urlMetrics = "https://mysterious-island-73235.herokuapp.com/api/metrics"
        # Getting data passed through the post request using request providade by Flask
        requestData = request.get_json(force=True)

        # Checking if the request data is correct else returns "malformed request"
        if (
            requestData["text"]
            and requestData["clinic"]
            and requestData["physician"]
            and requestData["patient"]
        ):
            # Initializing variables
            physician_id = requestData["physician"]["id"]

            physician = False
            resp_physician = None
            try:
                # Check if physician is in the database
                physician = Physician.query.get_or_404(physician_id)
            except Exception as e:
                # If it is, pass, else get it from the api
                if physician:
                    pass
                else:
                    try:
                        resp_physician = requests_retry_session().get(
                            "http://localhost:5000/api/v2/physician/"
                            + str(requestData["physician"]["id"])
                        )

                        resp_physician = resp_physician.json()

                    except:
                        # In case of exception returns error
                        return resp_physician.get_json(force=True)

                    # Create physician object to add to database
                    physician = Physician(
                        id=resp_physician["data"]["id"],
                        fullname=resp_physician["data"]["fullName"],
                        crm=resp_physician["data"]["crm"],
                    )
                    db.session.add(physician)
                    db.session.commit()

            patient_id = requestData["patient"]["id"]
            patient = None
            resp_patient = None
            try:
                # Check if patient is in the database
                patient = Patient.query.get_or_404(patient_id)
            except:
                if patient:
                    # If it is, pass, else get it from the api
                    pass
                else:
                    try:
                        resp_patient = requests_retry_session().get(
                            "http://localhost:5000/api/v2/patient/"
                            + str(requestData["patient"]["id"])
                        )
                        resp_patient = resp_patient.json()
                    except:
                        return resp_patient.get_json(force=True)

                    # Create patient object to add to database
                    patient = Patient(
                        id=resp_patient["data"]["id"],
                        fullname=resp_patient["data"]["fullName"],
                        email=resp_patient["data"]["email"],
                        phone=resp_patient["data"]["phone"],
                        clinic=resp_patient["data"]["clinic"]["id"],
                        active=resp_patient["data"]["active"],
                    )
                    db.session.add(patient)
                    db.session.commit()
            clinic = requestData["clinic"]["id"]

            resp_clinic = None
            try:
                # Check if clinic is in the database
                clinic = Clinic.query.get_or_404(clinic)
            except:
                if clinic:
                    # If it is, pass, else get it from the api
                    pass
                else:
                    try:
                        resp_clinic = requests_retry_session().get(
                            "http://localhost:5000/api/v2/clinic/"
                            + str(requestData["clinic"]["id"])
                        )
                        resp_clinic = resp_clinic.json()
                    except:
                        return resp_clinic.json()
                    # Create clinic object to add to database
                    clinic = Clinic(
                        id=resp_clinic["data"]["id"], name=resp_clinic["data"]["name"]
                    )
                    db.session.add(clinic)
                    db.session.commit()

            # Create generate json to send to POST API Metrics
            jsonForMetrics = generate_json_for_metrics(
                patient=patient, physician=physician, clinic=clinic
            )

            # Create requests Session
            r = requests_retry_session(retries=5)
            try:
                # Try to post to Metrics, returns the json or in case of exception returns an error
                r = r.post(
                    urlMetrics, headers=headers, timeout=timeout, data=jsonForMetrics
                )
                reqJson = r.json()
            except Exception as e:
                return get_error("metrics service not available", "04")

            if "errorCode" in reqJson:
                # If Metrics API returns an error, execute a rollback.
                db.session.rollback()

                return (get_error(reqJson["userMessage"], reqJson["errorCode"]), 404)

            else:
                # Create prescription object to add to database
                prescription = Prescription(
                    text=requestData["text"],
                    clinic=requestData["clinic"]["id"],
                    patient=requestData["patient"]["id"],
                    physician=requestData["physician"]["id"],
                )
                db.session.add(prescription)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return get_error(e.__class__.__name__, "10")

                # This is to check if the transaction have been successful
                presc_object = Prescription.query.filter_by(
                    patient=requestData["patient"]["id"],
                    physician=requestData["physician"]["id"],
                    text=requestData["text"],
                ).first()

                # Create dict to be sent as a response
                resp = dict()
                resp["data"] = dict(
                    id=presc_object.id,
                    clinic=dict(id=presc_object.clinic),
                    physician=dict(id=presc_object.physician),
                    patient=dict(id=presc_object.patient),
                    text=presc_object.text,
                )

                current_app.logger.info("POST on /v2/prescriptions/")
                # Flask-Restful sends a JSON back so no need to dump the dict into one
                return resp, 200

        else:
            return get_error("malformed requests", "01"), 200
