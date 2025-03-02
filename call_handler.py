import os
import time
import requests
from twilio.rest import Client
from dotenv import load_dotenv
from gpt import GPTProcessor

load_dotenv()

class CallHandler:
    def __init__(self, patient_preferences, dentist_details):
        
        # Twilio configuration
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.destination_phone_number = dentist_details.get("dentist_phone_number")
        #self.destination_phone_number = "+553123916031"
        
        # Ultravox configuration
        self.ultravox_api_key = os.getenv('ULTRAVOX_API_KEY')
        self.ultravox_api_url = 'https://api.ultravox.ai/api/calls'
        
        # Generate system prompt
        self.system_prompt = self.generate_prompt(patient_preferences, dentist_details)
        
        self.ultravox_call_config = {
            'systemPrompt': self.system_prompt,
            'model': 'fixie-ai/ultravox',
            'voice': 'Mark',
            'temperature': 0.5,
            'firstSpeaker': 'FIRST_SPEAKER_USER',
            'medium': {'twilio': {}},
            'transcriptOptional': False,
            'languageHint': 'pt'
        }
        
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
    
    def generate_prompt(self, patient_preferences, dentist_details):
        """Generate a structured prompt based on patient preferences and dentist details."""
        prompt = f"""
        You are an AI virtual assistant making a phone call to book a dental appointment on behalf of {patient_preferences.get('patient_name')}. 

        **Important Rules:**
        1. **Role Clarification:**
        - You are NOT the receptionist or dentist.
        - You are an AI calling on behalf of the patient.
        - Your goal is to speak to the **receptionist or dentist** and book an appointment.
        - Wait for the receptionist or dentist to introduce themselves first.
        - Never introduce yourself as the **clinic receptionist or dentist**.

        2. **Conversation Guidelines:**
        - Keep the conversation **short, concise, and to the point**.
        - Avoid repeating the same information or questions.
        - Speak politely and professionally at all times.
        - Highlight the user preferred dates clearly.
        - If the receptionist provides information, acknowledge it and move forward without restating it unnecessarily.
        - If the receptionist speaks any other language, you must speak caller's language then.

        **Patient Details:**
        - Name: {patient_preferences.get('patient_name')}
        - Gender: {patient_preferences.get('patient_gender')}
        - Age: {patient_preferences.get('patient_age')}
        - Preferred Dates for Appointment: {patient_preferences.get('preferred_dates')}
        - Relation to the Caller: {patient_preferences.get('relation', 'N/A')}
        - Special Notes: {patient_preferences.get('special_notes', 'None')}

        **Dentist Details:**
        - Name: {dentist_details.get('dentist_name')}
        - Speciality: {dentist_details.get('dentist_speciality')}
        - Clinic: {dentist_details.get('dentist_clinic')}
        - Address: {dentist_details.get('dentist_address')}

        **Steps for the Call:**
        1. **Introduction:**
        - Start with: **"Hello, I am calling on behalf of {patient_preferences.get('patient_name')} to book a dental appointment."**
        - Wait for the receptionist or dentist to respond before proceeding.

        2. **Request Appointment:**
        - Ask: **"Could you please let me know if there are any available appointments on {patient_preferences.get('preferred_dates')}?"**
        - If no slots are available on preferred dates, ask: **"What is the earliest available appointment?"**

        3. **Confirm Details:**
        - Once a slot is provided, confirm: **"Could you please confirm the appointment for date at time?"**
        - Ask: **"Are there any documents or preparations required for the appointment?"**

        4. **Closing the Call:**
        - Thank the receptionist: **"Thank you for your help. I appreciate it."**
        - End the call politely: **"Have a great day!"**

        **Key Reminders:**
        - Do not repeat information unless absolutely necessary.
        - Do not over-explain or provide unnecessary details.
        - Stay focused on booking the appointment and avoid digressing.
        - Always wait for the receptionist or dentist to respond before asking the next question.

        Let's begin the call now. Remember to Talk in Portuguese completely as receptionist or doctor doesn't know English.
        """
        return prompt.strip()
    
    def create_ultravox_call(self):
        """Initiate a call request to Ultravox API."""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.ultravox_api_key
        }
        response = requests.post(self.ultravox_api_url, json=self.ultravox_call_config, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def initiate_twilio_call(self, join_url):
        """Initiate the call using Twilio by connecting it to Ultravox."""
        call = self.twilio_client.calls.create(
            twiml=f'<Response><Connect><Stream url="{join_url}"/></Connect></Response>',
            to=self.destination_phone_number,
            from_=self.twilio_phone_number
        )
        return call.sid
    
    def get_call_status(self, call_id):
        """Poll the Ultravox API for the call status until it ends."""
        headers = {'X-API-Key': self.ultravox_api_key}
        
        while True:
            response = requests.get(f'{self.ultravox_api_url}/{call_id}', headers=headers)
            response.raise_for_status()
            call_data = response.json()
            
            if call_data.get('ended') is not None:
                return call_data.get('summary')
            time.sleep(10)

    def format_chat(self, json_data):
        roles = {
            "MESSAGE_ROLE_USER": "User",
            "MESSAGE_ROLE_AGENT": "Agent"
        }
        
        chat_text = ""
        for message in json_data["results"]:
            role = roles.get(message["role"], "Unknown")
            text = message.get("text", "[No response]")
            medium = "(Voice)" if message.get("medium") == "MESSAGE_MEDIUM_VOICE" else "(Text)"
            chat_text += f"{role} {medium}: {text}\n"
    
        return chat_text
    
    def get_call_transcript(self, call_id):
        """Retrieve the transcript of a completed call from Ultravox."""
        headers = {'X-API-Key': self.ultravox_api_key}
        transcript_url = f'{self.ultravox_api_url}/{call_id}/messages'
        
        response = requests.get(transcript_url, headers=headers)
        response.raise_for_status()
        formatted_chat = self.format_chat(response.json())
        #print(formatted_chat)
        return formatted_chat
    
    def process_call(self):
        """Main function to handle the complete call flow."""
        try:
            print('Creating Ultravox call...')
            response = self.create_ultravox_call()
            
            join_url = response.get('joinUrl')
            call_id = response.get('callId')
            
            if not join_url or not call_id:
                raise ValueError("Missing required fields in API response")
            
            #print(f'Join URL: {join_url}')
            #print(f'Call ID: {call_id}')
            
            call_sid = self.initiate_twilio_call(join_url)
            #print(f'Call initiated: {call_sid}')
            
            summary = self.get_call_status(call_id)
            #print(f'Call Summary: {summary}')
            
            transcript = self.get_call_transcript(call_id)
            #print(f'Call Transcript: {transcript}')

            gpt = GPTProcessor()
            appointment_details = gpt.generate_appointment_details(transcript)
            print(f'Appointment Details: {appointment_details}')
            
            return {
                'call_id': call_id,
                'summary': summary,
                'transcript': transcript,
                'appointment_details': appointment_details
            }
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

# if __name__ == '__main__':

#     patient_preferences = {
#     "patient_name": "John Doe",
#     "patient_gender": "Male",
#     "patient_age": "30",
#     "patient_phone_number": "+1234567890",
#     "patient_email_address": "johndoe@example.com",
#     "preferred_dates": "2025-02-20, 2025-02-22",
#     "relation": "Self",
#     "special_notes": "Patient has mild tooth pain and prefers a morning appointment."
#     }

#     dentist_details = {
#     "dentist_name": "Dr. Emily Carter",
#     "dentist_speciality": "Endodontist",
#     "dentist_clinic": "Smile Dental Care",
#     "dentist_phone_number": "+553123916031",
#     "dentist_email": "dr.carter@smiledental.com",
#     "dentist_address": "123 Main Street, Springfield",
#     "dentist_working_hours": "Monday-Friday, 9 AM - 6 PM"
#     }
#     call_handler = CallHandler(patient_preferences, dentist_details)
#     call_handler.process_call()
