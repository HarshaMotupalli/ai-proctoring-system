# AI-Based Proctoring System Using Temporal Verification

<p align="center">
  <!-- <img src="screenshots/system_architecture.png" alt="System Architecture" width="850"/> -->
</p>

<p align="center">
An AI-powered online examination monitoring system that combines <b>Computer Vision</b>, <b>Face Recognition</b>, <b>Object Detection</b>, <b>Identity Verification</b>, and <b>Real-Time Analytics</b> to ensure secure and fair online examinations.
</p>

---

## 📖 Project Overview

The **AI-Based Proctoring System** is an intelligent online examination monitoring platform designed to maintain academic integrity during remote examinations.

Unlike traditional online examination systems that rely on manual invigilation, this project continuously monitors candidates using Artificial Intelligence and Computer Vision. The system verifies student identity, detects suspicious activities in real time, captures evidence, and generates detailed reports for invigilators.

The project integrates **YOLOv8**, **YOLOv8-Face**, **ArcFace**, and **MediaPipe** to provide accurate and reliable proctoring while minimizing false-positive detections using **Temporal Verification**.

---

## 🚀 Key Features

### 👤 Student Registration
- Register student details
- Capture facial image
- Generate ArcFace facial embedding
- Store embeddings securely in the database

### ✅ Identity Verification
- Face visibility validation
- Lighting condition verification
- Student authentication before examination
- Prevent unauthorized access

### 🎥 Real-Time Exam Monitoring
- Live webcam monitoring
- WebSocket-based communication
- Continuous AI inference
- Real-time event logging

### 🔍 Identity Matching
- Compare live face embedding with stored embedding
- Detect impersonation attempts
- Generate automatic warnings

### 🚨 AI-Based Violation Detection

The system detects:

- 📱 Mobile Phone Usage
- 👥 Multiple Person Detection
- ❌ Face Not Visible
- 🧑 Identity Mismatch
- 👀 Head Movement Monitoring

### ⏱ Temporal Verification

Instead of generating alerts immediately, the system validates suspicious activities over a predefined time threshold.

This helps:

- Reduce false positives
- Improve detection accuracy
- Prevent unnecessary warnings

### 📸 Evidence Generation

Every confirmed violation includes:

- Timestamp
- Evidence image
- Violation type
- Duration
- Risk score

### 📊 Result Dashboard

The invigilator dashboard provides:

- Student information
- Session summary
- Live monitoring status
- Violation history
- Analytics charts


---

# 🏗 System Architecture

<p align="center">
<img src="screenshots/system_architecture.png" width="800">
</p>

The system follows the workflow below:

1. Student Registration
2. Face Embedding Generation
3. Identity Verification
4. Examination Starts
5. Real-Time AI Monitoring
6. Suspicious Behaviour Detection
7. Temporal Verification
8. Violation Detection
9. Evidence Storage
10. Dashboard & Final Report

---

# 🔄 Project Workflow

```text
Student Registration
        │
        ▼
Face Embedding Generation
        │
        ▼
Identity Verification
        │
        ▼
Exam Starts
        │
        ▼
Real-Time Monitoring
        │
        ▼
AI Detection Module
        │
        ▼
Suspicious Behaviour Detection
        │
        ▼
Temporal Verification
        │
        ▼
Violation Detection
        │
        ▼
Evidence Storage
        │
        ▼
Dashboard & Reports
```

---

# ⚡ Optimized Detection Pipeline

To improve performance, different AI modules execute at different intervals.

| Module | Execution Frequency |
|---------|--------------------|
| Face Detection | Every Frame |
| Head Pose Detection | Every 2 Frames |
| Object Detection | Every 3 Frames |
| Identity Matching | Every 10 Frames |

---

# 📁 Folder Description

| Folder | Description |
|---------|-------------|
| **backend/** | Backend APIs, AI models, database, monitoring logic |
| **app/** | Core backend application |
| **evaluation/** | Evaluation reports and metrics |
| **evidence/** | Captured violation images |
| **frontend/** | Frontend pages |
| **models/** | AI model files |
| **Docs/** | Commands and project documentation |
| **screenshots/** | Images used in README |
| **README.md** | Project documentation |

---

# 🤖 Required AI Models

Download the official models before running the project.

| Model | Official Download |
|--------|-------------------|
| ArcFace (InsightFace) | https://github.com/deepinsight/insightface |
| YOLOv8n | https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt |
| YOLOv8m | https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt |
| YOLOv8l | https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8l.pt |
| YOLOv8-Face | https://github.com/derronqi/yolov8-face |

Place all downloaded models inside:

```text
backend/models/
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/HarshaMotupalli/ai-proctoring-system.git

cd ai-proctoring-system
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# ▶ Running the Project

All commands required to run the project are documented inside:

```text
Docs/COMMANDS.md
```

The document contains:

- Environment setup
- Backend execution
- Frontend execution
- Database setup
- Model placement
- Troubleshooting
- Development commands

---

# 🔮 Future Enhancements

- Eye Gaze Tracking
- Audio Monitoring
- Cloud Deployment
- Multi-Camera Support
- Advanced Behaviour Analysis
- AI-Based Risk Prediction
- Mobile Dashboard
- Email Notifications

---

# 👨‍💻 Author

**Harsha Motupalli**

- 🎓 B.Tech – Artificial Intelligence & Machine Learning
- 💻 GitHub: https://github.com/HarshaMotupalli
- If you found this project useful, please consider giving it a **⭐ Star** on GitHub.
- Your support helps improve the project and motivates future development.

---

## 📜 License

This project is developed for **educational and research purposes**. Feel free to explore, learn, and build upon it with appropriate attribution.
