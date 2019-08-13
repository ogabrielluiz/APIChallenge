import unittest
from config import base_dir, TestingConfig
from app import create_app
from app.models import (
    Patient,
    Physician,
    Clinic,
    Prescription,
    db as models_db,
)  # importing db used in models.py to avoid sql errors
import requests
from app.utils import requests_retry_session
import requests_cache

from dotenv import load_dotenv
from flask import jsonify
import json

load_dotenv(".flaskenv")

requests_cache.install_cache(cache_name="APItest", backend="sqlite", expire_after=300)


class APITestCase(unittest.TestCase):
    """Tests API's GET endpoints and POST endpoint /v2/prescriptions"""

    def setUp(self):

        self.app = create_app(env="testing")
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        # initialize variables to be used on tests
        self.patient_id = 1
        self.physician_id = 1
        self.clinic_id = 1
        self.prescription = {
            "clinic": {"id": 1},
            "physician": {"id": 1},
            "patient": {"id": 1},
            "text": "Dipirona 1x ao dia",
        }
        with self.app_context:
            models_db.create_all()

    def tearDown(self):
        models_db.session.remove()
        models_db.drop_all()
        self.app_context.pop()

    def test_api_can_get_patient(self):
        response = self.client().get(
            f"http://localhost:5000/v2/patient/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Rodrigo", response.get_json()["data"]["fullName"])

    def test_save_patient_to_db(self):
        response = self.client().get(
            f"http://localhost:5000/v2/patient/{self.patient_id}"
        )
        response = response.get_json()

        patient = Patient(
            id=response["data"]["id"],
            fullname=response["data"]["fullName"],
            email=response["data"]["email"],
            phone=response["data"]["phone"],
            clinic=response["data"]["clinic"]["id"],
            active=response["data"]["active"],
        )
        models_db.session.add(patient)
        models_db.session.commit()

        query_patient = Patient.query.filter_by(id=response["data"]["id"]).first()
        self.assertEqual(response["data"]["id"], query_patient.id)

    def test_api_can_get_physician(self):
        response = self.client().get(
            f"http://localhost:5000/v2/physician/{self.physician_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("João", response.get_json()["data"]["fullName"])

    def test_save_physician_to_db(self):
        response = self.client().get(
            f"http://localhost:5000/v2/physician/{self.physician_id}"
        )
        response = response.get_json()

        physician = Physician(
            id=response["data"]["id"],
            fullname=response["data"]["fullName"],
            crm=response["data"]["crm"],
        )
        models_db.session.add(physician)
        models_db.session.commit()

        query_physician = Physician.query.filter_by(id=response["data"]["id"]).first()
        self.assertEqual(response["data"]["id"], query_physician.id)

    def test_api_can_get_clinic(self):
        response = self.client().get(
            f"http://localhost:5000/v2/clinic/{self.clinic_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Clínica A", response.get_json()["data"]["name"])

    def test_save_clinic_to_db(self):
        response = self.client().get(
            f"http://localhost:5000/v2/clinic/{self.clinic_id}"
        )
        response = response.get_json()

        clinic = Clinic(id=response["data"]["id"], name=response["data"]["name"])
        models_db.session.add(clinic)
        models_db.session.commit()

        query_clinic = Clinic.query.filter_by(id=response["data"]["id"]).first()
        self.assertEqual(response["data"]["id"], query_clinic.id)

    def test_api_can_post_prescription(self):
        response = self.client().post(
            "http://localhost:5000/v2/prescriptions", data=json.dumps(self.prescription)
        )
        jsonResponse = response.get_json(force=True)

        expectedResponse = {
            "data": {
                "id": 1,
                "clinic": {"id": 1},
                "physician": {"id": 1},
                "patient": {"id": 1},
                "text": "Dipirona 1x ao dia",
            }
        }

        self.assertEqual(expectedResponse, jsonResponse)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
