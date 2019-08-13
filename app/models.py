from app import db

association_table = db.Table(
    "tb_physician_patient",
    db.Column(
        "Physician_id", db.Integer, db.ForeignKey("physician.id"), primary_key=True
    ),
    db.Column("Patient_id", db.Integer, db.ForeignKey("patient.id"), primary_key=True),
)


class Clinic(db.Model):

    __tablename__ = "clinic"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    patients = db.relationship("Patient")

    def __str__(self):
        return "<Patient %s>" % self.fullname


class Patient(db.Model):

    __tablename__ = "patient"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    clinic = db.Column(db.Integer, db.ForeignKey("clinic.id"))
    active = db.Column(db.Boolean, nullable=False)

    def __str__(self):
        return "<Patient %s>" % self.fullname


class Physician(db.Model):

    __tablename__ = "physician"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(60), unique=True, nullable=False)
    crm = db.Column(db.String(13), nullable=False)
    patients = db.relationship("Patient", secondary=association_table)

    def __str__(self):
        return "<Physician %s>" % self.fullname


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    clinic = db.Column(db.Integer, db.ForeignKey("clinic.id"))
    patient = db.Column(db.Integer, db.ForeignKey("patient.id"))
    physician = db.Column(db.Integer, db.ForeignKey("physician.id"))
