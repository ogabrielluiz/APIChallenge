from app import create_app, db
from app.models import Patient, Physician, Clinic, Prescription

application = create_app()


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'Patient': Patient, 'Physician': Physician, 'Clinic': Clinic, 'Prescription': Prescription}
