# 🏇 UmaCP — Umamusume Completionist Planner

> Umamusume Completionist Planner (UmaCP) - career optimization engine and schedule generator for easier "\[Your Oshi\] Completionist" title acquiring, built with Python + Streamlit

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Local Development](#-local-development)
4. [Production Deployment (Docker)](#-production-deployment-docker)
5. [Architecture & Project Structure](#-architecture--project-structure)
6. [Licensing & Compliance (AGPL v3)](#-licensing--compliance-agpl-v3)

---

## 🔍 Overview

**UmaCP** is a career optimization tool and schedule generator designed to minimize the number of career runs required to achieve the "Completionist" title (winning all graded races) during training.

It implements:

* **Constraint Satisfaction & Backtracking Solver** to plan collision-free calendars across Junior, Classic, and Senior years.
* **Inheritance Factor Math Engine** that computes the minimum star/slot genetic requirements (fitting under the game limits: max 18★ total, max 6 grandparent/parent slots, cost scaling: +1 step = 1★, +2 = 4★, +3 = 7★, +4 = 10★).
* **Automated Distance Prioritization** to prioritize distance upgrades and dynamically scale down surface upgrades in mathematically impossible combinations, maintaining a valid build.

---

## ⚡ Key Features

* **Career Optimization Solver**: Groups, scales, and schedules user-selected races into the minimal number of career runs.
* **Cached Database Loading**: SQLite database queries are cached in session memory to reduce server overhead during page executions.
* **Dynamic Search Filter**: Filter races by name, surface (Turf/Dirt), and distance (Sprint/Mile/Medium/Long) with automatic UI updates.
* **Responsive Visual Calendar Grid**: Rendered as a custom dark-themed calendar showing Turn 1 to 72 assignments.
* **Excel Export Engine**: Multi-sheet export to `.xlsx` containing inheritance builds, stars/slots summaries, and styled tables.
* **Session Persistence**: Persistent race selections saved securely using browser cookies.

---

## 🛠️ Local Development

### Prerequisites

* Python 3.10+
* Virtual Environment tools (`venv`)

### Automated Setup

Simply run the script corresponding to your operating system to set up a virtual environment, install dependencies, and launch the server:

**Linux / macOS**:

```bash
chmod +x run.sh
./run.sh
```

**Windows**:

```cmd
run.bat
```

### Manual Setup

1. Create a virtual environment and activate it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

---

## 🐳 Production Deployment (Docker)

UmaCP is fully containerized and ready for cloud deployment.

### 1. Docker Compose

Run the pre-configured container stack in the background:

```bash
docker compose up -d --build
```

The application will build, auto-initialize the internal SQLite database, perform internal health checks, and start listening on port `8501`.

### 2. Nginx Reverse Proxy

To host the app behind Nginx, use the following configuration block (crucial for WebSocket handling):

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        
        # Enable WebSocket forwarding (Required for Streamlit)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Connection timeouts
        proxy_read_timeout 86400;
    }
}
```

---

## 🗂️ Architecture & Project Structure

```
├── app.py           # Streamlit entry point and UI components
├── scheduler.py     # Backtracking scheduling algorithm and build evaluation
├── db.py            # SQLite database interface & auto-initializer
├── renderer.py      # Custom HTML Calendar layout renderer
├── racelist.csv     # Semicolon-delimited database source with 152 races
├── requirements.txt # Project dependencies
├── Dockerfile       # Multi-stage production container setup
├── docker-compose.yml # Compose services definition
└── LICENSE          # GNU AGPL v3 License Text
```

---

## ⚖️ Licensing & Compliance (AGPL v3)

This program is distributed under the **GNU Affero General Public License Version 3 (AGPL v3)**.

### Remote Network Interaction (Section 13)

If you modify this program and run it on a public network server, you **must** make the Corresponding Source code of your version available to all remote users. By default, the application UI contains a **"View & Download Source"** button in the sidebar linked directly to the repository (<https://github.com/1njure/uma-cp>) to comply with this requirement.
