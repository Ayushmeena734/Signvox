# SignVox – Sign Language to Voice Translator

SignVox is an AI-based web application designed to help people communicate through sign language.

The project aims to recognize hand gestures using computer vision and convert recognized signs into text and speech.

## Features

- Live camera interface
- Sign language translation interface
- React frontend
- FastAPI backend
- Planned hand landmark detection using MediaPipe
- Planned machine learning-based sign recognition
- Planned text-to-speech output

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript
- React.js
- Tailwind CSS

### Backend
- Python
- FastAPI
- REST API

### AI / Machine Learning
- MediaPipe (planned)
- Scikit-learn (planned)

## Project Structure

```text
Signvox/
├── Backend/
│   ├── main.py
│   └── requirements.txt
│
├── Frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── component/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ayushmeena734/Signvox.git
cd Signvox
```

### 2. Start the Backend

```bash
cd Backend
python -m venv venv
```

Activate virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Backend URL: http://127.0.0.1:8000

### 3. Start the Frontend

Open another terminal:

```bash
cd Frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173

## Project Status

React frontend and FastAPI backend are connected successfully.

MediaPipe integration, dataset collection, machine learning and voice recognition are planned development stages.

## Developers

- Ayush Meena
- Atharv Deshmukh

---

**SignVox – Breaking Communication Barriers Through Technology.**