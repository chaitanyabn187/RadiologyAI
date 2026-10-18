RadiologyAI — AI-Assisted Radiology Case Prioritization System

"Python" (https://img.shields.io/badge/Python-3.x-blue)
"Flask" (https://img.shields.io/badge/Framework-Flask-black)
"AI" (https://img.shields.io/badge/AI-Chest%20X--ray%20Analysis-purple)
"Status" (https://img.shields.io/badge/Status-Academic%20Prototype-orange)

📌 Project Overview

RadiologyAI is an academic prototype that demonstrates how artificial intelligence can assist with organizing chest X-ray cases for review.

The system uses a pretrained deep-learning model to generate experimental chest X-ray findings. It displays the uploaded images, patient case details, model outputs, and a review ranking through a web-based dashboard.

The project combines Python web development, deep learning, image processing, and database management in a single application.

Disclaimer: This project is intended for educational and demonstration purposes only. Its AI outputs are not confirmed diagnoses and must not be used for clinical decision-making.»

---

🎯 Problem Statement

Medical imaging departments may receive many X-ray cases that need professional review. Organizing case information and reviewing images can be challenging when information is stored across different records.

This project explores a software-based approach to organizing chest X-ray cases and presenting experimental AI outputs in a centralized dashboard.

🎯 Objectives

- Develop a web application for managing chest X-ray cases.
- Integrate a pretrained deep-learning model for experimental image analysis.
- Display AI-generated findings alongside uploaded X-ray images.
- Organize cases using a model-score-based review ranking.
- Detect duplicate image uploads.
- Store and manage case information using a database.
- Provide a simple dashboard for viewing and deleting cases.

---

✨ Key Features

🩻 Chest X-ray Upload

Upload supported chest X-ray images in PNG, JPG, and JPEG formats.

🤖 AI-Assisted Analysis

Use a pretrained deep-learning model to generate experimental findings from chest X-ray images.

📊 Interactive Case Dashboard

View case IDs, patient details, review rankings, uploaded images, and AI-generated findings.

🔢 Review Ranking

Organize cases according to the highest returned model score. This ranking is experimental and does not establish clinical urgency.

🔍 Duplicate Image Detection

Use SHA-256 hashing to identify identical image files and help prevent duplicate uploads.

🗂️ Case Management

Add and delete cases through the web interface.

💾 Database Integration

Store case details and model outputs using SQLite.

📍 Finding Location Field

Display the location field when available. The current implementation shows "Not localized" when an anatomical location has not been determined.

---

🛠️ Technologies Used

Technology| Purpose
Python| Application logic
Flask| Web application framework
PyTorch| Deep-learning inference
TorchXRayVision| Pretrained chest X-ray model
NumPy| Numerical data processing
SQLite| Database management
HTML5| Web page structure
CSS3| User interface styling
JavaScript| Client-side interaction
Git| Version control
GitHub| Source code hosting

---

🏗️ Project Structure

Radiology_case_prioritization/
│
├── app.py
├── ai_model.py
├── chest_xray.py
├── debug_prediction.py
├── test_model.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── images/
│   ├── script.js
│   └── style.css
│
└── templates/
    ├── dashboard.html
    ├── index.html
    └── upload.html

The exact files and folders may vary depending on the current version of the project.

---

⚙️ Installation and Setup

Prerequisites

Before running the project, ensure that you have:

- Python installed.
- Git installed.
- An internet connection to install dependencies and download model weights if required.
- A compatible Python environment with sufficient memory for the deep-learning model.

Step 1: Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

Replace "YOUR_GITHUB_REPOSITORY_URL" with the HTTPS URL of your GitHub repository.

Step 2: Open the Project Folder

cd Radiology_case_prioritization

Step 3: Create a Virtual Environment

python -m venv venv

Step 4: Activate the Environment

For Windows:

venv\Scripts\activate

For macOS or Linux:

source venv/bin/activate

Step 5: Install Dependencies

python -m pip install -r requirements.txt

PyTorch and related packages may require compatible versions depending on your Python version and operating system.

Step 6: Run the Application

python app.py

Step 7: Open the Application

Open your browser and visit:

Home page

http://127.0.0.1:5000/

Case dashboard

http://127.0.0.1:5000/dashboard

The application uses a local SQLite database for case storage.

---

🔄 How the System Works

1. The user opens the web application.
2. The user enters case details and selects a chest X-ray image.
3. The application validates the submitted information and file type.
4. The system checks whether the same image file has already been uploaded.
5. The pretrained model processes the image and returns scores for its supported findings.
6. The application stores the case information and available model outputs.
7. The dashboard displays the uploaded image, case details, findings, and review ranking.
8. The user can view or delete cases through the dashboard.

---

🧠 AI Model Information

The current implementation uses a pretrained DenseNet121 model through TorchXRayVision.

The model generates scores for supported chest X-ray finding categories.

Important limitations:

- Model scores are not necessarily calibrated disease probabilities.
- A high model score does not confirm that a patient has a disease.
- The model does not currently provide reliable exact anatomical localization through this application.
- The review ranking is not a validated clinical triage system.
- Model performance on a particular image or population has not been established by this project.

All outputs require appropriate professional interpretation and must not be used as a substitute for medical assessment.

---

🔐 Privacy and Security

This project handles medical-image-related data, so privacy must be considered.

- Do not upload real patient information or identifiable medical images to a public repository.
- Keep local databases and uploaded case images out of version control.
- Use synthetic or appropriately de-identified examples for demonstrations.
- Add authentication and access controls before considering use in a multi-user environment.
- Do not use this academic prototype to make patient-care decisions.

---

⚠️ Limitations

- The system is an academic prototype and has not been clinically validated.
- AI-generated findings may be inaccurate or incomplete.
- Model outputs may be affected by image quality and preprocessing.
- Exact anatomical localization is not currently implemented.
- The model-score-based review ranking is not a validated measure of clinical urgency.
- Secure multi-user authentication and authorization may require further development.
- Further evaluation is necessary before making claims about accuracy or clinical usefulness.

---

🚀 Future Enhancements

Potential future improvements include:

- Investigating reliable anatomical localization methods.
- Evaluating model performance using appropriate datasets and metrics.
- Improving the dashboard design and accessibility.
- Implementing secure authentication and role-based access control.
- Adding audit logs and stronger privacy safeguards.
- Improving error handling and input validation.
- Exploring a more carefully evaluated case-prioritization approach.
- Adding automated tests and deployment documentation.

These are proposed enhancements and should not be considered implemented features unless they are developed and tested.

---

🎓 Project Purpose

RadiologyAI is an educational engineering project exploring the integration of deep learning, web development, and medical-image workflow organization.

It provides practical experience with Python, Flask, pretrained AI models, image handling, database integration, and dashboard development.

---

📄 Disclaimer

RadiologyAI is provided for educational and demonstration purposes only.

It is not a medical device, does not provide confirmed diagnoses, and is not intended for diagnosis, treatment, or clinical decision-making. Medical images must be interpreted by qualified healthcare professionals.

---

Developed as an academic engineering project.
