## **Application Flow Breakdown**

### **1. User Authentication (Sign Up / Login)**

* **User signs up or logs in** to the system.
* The user’s details are stored in the **`users`** table.
* On successful login, the user sees  **two main options** :
  1. **Browse Services** → See available dental services first, then choose a dentist.
  2. **Browse Dentists** → Directly pick a preferred dentist.

---

### **2. Viewing Available Services**

* User selects **a service** from the `services` table (e.g., "Teeth Whitening").
* The system displays **all dentists** that offer this service.
* **User selects a dentist** and moves to appointment preferences.

**OR**

### **3. Viewing Dentists Directly**

* The user skips service selection and  **directly browses all available dentists** .
* The system lists all dentists  **along with their services** .
* The user picks a **preferred dentist** and moves to appointment preferences.

---

### **4. Setting Appointment Preferences**

* After selecting a  **dentist** , the user:
  * Selects **2-3 preferred dates** for an appointment.
  * Enters **a problem description** (e.g., "Tooth pain for 3 days").
  * Adds **optional notes** (e.g., "I prefer morning slots").
* This information is stored in the **`appointment_preferences`** table.

---

### **5. AI-Powered Appointment Booking**

* **AI Agent picks up the request** and calls the dentist’s clinic.
* AI follows these steps:
  1. **Calls the clinic** using Twilio.
  2. **AI tries to make booking by providing user preferences.**
  3. If  **no response** , AI retreats and notifies.
  4. **If an appointment is booked** , AI **updates the `appointments` table** and notifies the user.

---

### **6. Appointment Confirmation & Notification**

* The **appointment status** is updated in the  **Booked Appointments menu** .
* The **user is notified via email** with:
  * **Appointment Date & Time**
  * **Dentist Details**
  * **Clinic Address & Contact Info**
* The user can also check the  **real-time booking status in the app** .
