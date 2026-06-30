# =========================================================
# AI PROCTORING SYSTEM - COMMANDS FILE
# =========================================================

# ==============================
# 1️⃣ CREATE VIRTUAL ENVIRONMENT
# ==============================

# Windows

```bash
python -m venv venv
venv\Scripts\activate
```

# Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

# ==============================
# 2️⃣ UPGRADE PIP
# ==============================

```bash
pip install --upgrade pip
```

# ==============================
# 3️⃣ INSTALL DEPENDENCIES
# ==============================

```bash
pip install -r backend/requirements.txt
```

# ==============================
# 4️⃣ RUN BACKEND SERVER
# ==============================

```bash
uvicorn backend.app.main:app --reload
```

# ==============================
# 5️⃣ RUN FRONTEND SERVER
# ==============================

```bash
cd frontend
python -m http.server 5500
```

# ==============================
# 6️⃣ CHECK TORCH GPU
# ==============================

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

# ==============================
# 7️⃣ CHECK PYTHON VERSION
# ==============================

```bash
python --version
```

# ==============================
# 8️⃣ TEST AUDIO DEVICES
# ==============================

```bash
python -m sounddevice
```

# ==============================
# 9️⃣ CLEAR EVIDENCE FOLDER
# ==============================

# Windows

```bash
rmdir /s /q backend\evidence
```

# Linux / macOS

```bash
rm -rf backend/evidence
```

# ==============================
# 🔟 RECREATE CLEAN ENVIRONMENT
# ==============================

# Windows

```bash
deactivate
rmdir /s /q venv

python -m venv venv
venv\Scripts\activate

pip install -r backend/requirements.txt
```

# Linux / macOS

```bash
deactivate
rm -rf venv

python3 -m venv venv
source venv/bin/activate

pip install -r backend/requirements.txt
```

# ==============================
# 11️⃣ RUN DOCKER (OPTIONAL)
# ==============================

```bash
docker-compose up --build
docker-compose down
```

# =========================================================
# WEBSOCKET ENDPOINT
# =========================================================

```plaintext
ws://127.0.0.1:8000/ws/proctor
```

# =========================================================
# BACKEND SERVER URL
# =========================================================

```plaintext
http://127.0.0.1:8000
```

# =========================================================
# FRONTEND SERVER URL
# =========================================================

```plaintext
http://127.0.0.1:5500
```
