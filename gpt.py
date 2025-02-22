import openai
from dotenv import load_dotenv
import os
load_dotenv()

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentDetails(BaseModel):
    appointment_date: str
    appointment_time: str
    appointment_status: str

def get_appointment_details_prompt():
    return """You are an AI assistant tasked with extracting appointment details from a conversation between a receptionist/agent and a dentist. Given the transcript, extract and format the following details:

- `appointment_date`: The date of the appointment in `YYYY-MM-DD` format as a Python `datetime` object. If no explicit date is mentioned, this should be `null`.
- `appointment_time`: The time of the appointment in `HH:MM:SS` format as a `datetime` object. If no explicit time is mentioned, this should be `null`.
- `appointment_status`: The status of the appointment, which can be **Booked**, **Canceled**, **Rescheduled**, or **Pending**.

### Important Instructions:
- The year is **2025**.
- **Do not infer or assume any values** for `appointment_date` or `appointment_time` if they are not explicitly mentioned in the transcript.
- If the transcript **does not explicitly mention a confirmed appointment date and time**, return:
  - `"appointment_status": "Pending"`
  - `"appointment_date": null`
  - `"appointment_time": null`
- If the conversation suggests a rescheduling but no confirmed new date/time is mentioned, return:
  - `"appointment_status": "Rescheduled"`
  - `"appointment_date": null`
  - `"appointment_time": null`
- If the appointment is explicitly canceled, return:
  - `"appointment_status": "Canceled"`
  - `"appointment_date": null`
  - `"appointment_time": null`
- If the appointment is explicitly booked with a confirmed date and time, return:
  - `"appointment_status": "Booked"`
  - `"appointment_date": "YYYY-MM-DD"`
  - `"appointment_time": "HH:MM:SS"`

Your response must be a valid JSON object with the following structure:

```json
{
  "appointment_date": "YYYY-MM-DD" | null,
  "appointment_time": "HH:MM:SS" | null,
  "appointment_status": "Booked" | "Canceled" | "Rescheduled" | "Pending"
}
"""

openai.api_key = os.getenv("OPENAI_API_KEY")

class GPTProcessor:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_appointment_details(self, formatted_text):
        response = openai.beta.chat.completions.parse(
            model="gpt-4o-mini",  
            messages=[{"role": "system", "content": get_appointment_details_prompt()},
                      {"role": "user", "content": formatted_text}],
            response_format=AppointmentDetails
        )
        return response.choices[0].message.parsed
    