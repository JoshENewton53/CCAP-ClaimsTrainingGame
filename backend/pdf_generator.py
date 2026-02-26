"""
PDF Death Certificate Generator
Creates realistic death certificates with intentional errors for training
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import random
from datetime import datetime, timedelta

class DeathCertificateGenerator:
    def __init__(self):
        self.states = ['Florida', 'Texas', 'California', 'New York', 'Illinois', 'Pennsylvania']
        self.first_names = ['John', 'Mary', 'Robert', 'Patricia', 'Michael', 'Jennifer', 'William', 'Linda', 'David', 'Barbara']
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        self.causes = [
            ('Natural causes - Cardiac arrest', 'I21.9'),
            ('Respiratory failure', 'J96.90'),
            ('Cerebrovascular accident', 'I63.9'),
            ('Pneumonia', 'J18.9'),
            ('Cancer - Lung', 'C34.90'),
            ('Diabetes complications', 'E11.9'),
            ('Alzheimer\'s disease', 'G30.9'),
            ('Renal failure', 'N19')
        ]
    
    def generate_certificate(self, policy_data, errors=None):
        """Generate a death certificate PDF with optional intentional errors"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 0.75*inch, "CERTIFICATE OF DEATH")
        
        # State header
        state = policy_data.get('state', random.choice(self.states))
        if errors and 'jurisdiction_mismatch' in errors:
            state = random.choice([s for s in self.states if s != policy_data.get('state')])
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - inch, f"State of {state}")
        c.drawCentredString(width/2, height - 1.2*inch, "Department of Health - Bureau of Vital Statistics")
        
        # Certificate number
        cert_num = f"{state[:2].upper()}-{random.randint(2020, 2024)}-{random.randint(100000, 999999)}"
        c.drawString(inch, height - 1.6*inch, f"Certificate No: {cert_num}")
        
        # Decedent Information
        y = height - 2.2*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "DECEDENT INFORMATION")
        
        y -= 0.3*inch
        c.setFont("Helvetica", 10)
        
        # Name
        name = policy_data.get('policy_holder', f"{random.choice(self.first_names)} {random.choice(self.last_names)}")
        if errors and 'name_mismatch' in errors:
            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
        
        c.drawString(inch, y, f"Full Legal Name: {name}")
        
        # Date of Birth and Death
        y -= 0.25*inch
        age = policy_data.get('age', random.randint(50, 80))
        if errors and 'age_mismatch' in errors:
            age = random.randint(30, 45)
        
        birth_date = datetime.now() - timedelta(days=age * 365)
        c.drawString(inch, y, f"Date of Birth: {birth_date.strftime('%m/%d/%Y')}")
        c.drawString(4*inch, y, f"Age: {age} years")
        
        y -= 0.25*inch
        death_date = policy_data.get('death_date')
        if death_date:
            death_dt = datetime.strptime(death_date, '%Y-%m-%d')
        else:
            death_dt = datetime.now() - timedelta(days=random.randint(1, 180))
        
        if errors and 'date_inconsistency' in errors:
            policy_date = datetime.strptime(policy_data.get('policy_effective_date', '2020-01-01'), '%Y-%m-%d')
            death_dt = policy_date - timedelta(days=random.randint(30, 365))
        
        c.drawString(inch, y, f"Date of Death: {death_dt.strftime('%m/%d/%Y')}")
        c.drawString(4*inch, y, f"Time: {random.randint(0, 23):02d}:{random.randint(0, 59):02d}")
        
        # Place of Death
        y -= 0.25*inch
        c.drawString(inch, y, f"Place of Death: {random.choice(['Hospital', 'Residence', 'Nursing Home', 'Hospice'])}")
        c.drawString(4*inch, y, f"County: {random.choice(['Miami-Dade', 'Harris', 'Los Angeles', 'Cook'])}")
        
        # Residence
        y -= 0.25*inch
        residence_state = state
        if errors and 'state_mismatch' in errors:
            residence_state = random.choice([s for s in self.states if s != state])
        c.drawString(inch, y, f"Residence: {random.randint(100, 9999)} Main St, {random.choice(['Springfield', 'Riverside', 'Oak Park'])}, {residence_state}")
        
        # Cause of Death
        y -= 0.4*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "CAUSE OF DEATH")
        
        y -= 0.3*inch
        c.setFont("Helvetica", 10)
        cause, icd_code = random.choice(self.causes)
        if errors and 'invalid_cause_code' in errors:
            icd_code = f"X{random.randint(10, 99)}.{random.randint(0, 9)}"
        
        c.drawString(inch, y, f"Immediate Cause: {cause}")
        y -= 0.2*inch
        c.drawString(inch, y, f"ICD-10 Code: {icd_code}")
        
        y -= 0.25*inch
        c.drawString(inch, y, f"Manner of Death: {random.choice(['Natural', 'Accident', 'Pending Investigation'])}")
        
        # Certifier Information
        y -= 0.4*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "CERTIFIER INFORMATION")
        
        y -= 0.3*inch
        c.setFont("Helvetica", 10)
        physician = f"Dr. {random.choice(self.first_names)} {random.choice(self.last_names)}, M.D."
        c.drawString(inch, y, f"Certifying Physician: {physician}")
        
        y -= 0.25*inch
        cert_date = death_dt + timedelta(days=random.randint(1, 3))
        if errors and 'expired_certification' in errors:
            cert_date = death_dt + timedelta(days=random.randint(45, 90))
        
        c.drawString(inch, y, f"Date Certified: {cert_date.strftime('%m/%d/%Y')}")
        
        y -= 0.25*inch
        c.drawString(inch, y, f"License Number: MD-{random.randint(100000, 999999)}")
        
        # Signature line
        y -= 0.4*inch
        if not (errors and 'missing_signature' in errors):
            c.setFont("Courier-Oblique", 12)
            c.drawString(inch, y, physician.split(',')[0])
        c.setFont("Helvetica", 8)
        c.line(inch, y - 5, 4*inch, y - 5)
        c.drawString(inch, y - 20, "Signature of Certifying Physician")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 0.5*inch, "This is a legal document. Any alteration or falsification is punishable by law.")
        c.drawCentredString(width/2, 0.35*inch, f"Issued: {datetime.now().strftime('%m/%d/%Y')}")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
