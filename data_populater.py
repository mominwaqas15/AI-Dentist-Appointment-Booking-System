import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Dentist  # Ensure the schema module is correctly named
import os, models
from dotenv import load_dotenv  

load_dotenv()

# Database connection URL (Modify with your actual credentials)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create tables if they don't exist
models.Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Load CSV file
csv_file_path = "dentist-data.csv"  # Adjust path if necessary
df = pd.read_csv(csv_file_path)

# Insert data into the Dentist table
for _, row in df.iterrows():
    dentist = Dentist(
        dentist_name=row["Full Name"],
        years_of_experience=row["Years of Experience"],
        dentist_speciality=row["Specialty"],
        dentist_clinic=row["Clinic Address"],
        dentist_phone_number=row["Contact Number"],
        dentist_email=row["Email"],
        dentist_address=row["Clinic Address"],
        dentist_working_hours=row["Working Hours"]
    )
    session.add(dentist)

# Commit the transaction
session.commit()
print("Dentist data inserted successfully!")

# Close the session
session.close()
