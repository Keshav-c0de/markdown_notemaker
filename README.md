# 📝 Cloud-Native Notes App

A full-stack, containerized Notes application built with a decoupled architecture. The frontend provides a seamless UI, while the backend API securely manages data communication with the database. Entirely containerized using Docker and deployed on an AWS EC2 Linux server.

---

## 📸 App Preview

![Image](https://github.com/user-attachments/assets/b3eacbe8-8d33-45b3-89bc-dd1397f47f90)
![Image](https://github.com/user-attachments/assets/3b4b7eef-4644-42c0-9e06-9f809269d515)

---

## 🏗️ Tech Stack & Architecture

This project is split into two independent microservices running in Docker containers, utilizing a modern, lightning-fast Python environment.

* **Frontend:** [Streamlit](https://streamlit.io/) (Runs on Port `8501`)
* **Backend API:** [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn (Runs on Port `8000`)
* **Database:** Supabase / PostgreSQL *(Connected via secure environment variables)*
* **Package Manager:** [uv](https://github.com/astral-sh/uv) *(For ultra-fast dependency resolution and isolated virtual environments)*
* **DevOps / Deployment:** Docker, Docker Compose, AWS EC2 (Ubuntu LTS)

---

## 📂 Project Structure

```text
.
├── app/                    # FastAPI backend code (main.py, routers, models)
├── frontend/               # Streamlit UI code (frontend.py)
├── backend.Dockerfile      # Multi-stage blueprint for the API
├── frontend.Dockerfile     # Multi-stage blueprint for the UI
├── docker-compose.yml      # Orchestrates both containers and maps ports/secrets
├── pyproject.toml          # Modern Python dependency file (used by uv)
├── uv.lock                 # Strict dependency locking
└── README.md

```
## 🚀 How to Run Locally

If you want to clone this repository and run it on your own machine, follow these steps.
1. Prerequisites

    * Ensure you have Docker installed and running.

    * Ensure you have Git installed.

2. Setup Environment Variables
This app requires a database connection to run. You must create a .env file in the root directory.

    ```bash 
    # Create the file
    touch .env
    ```
Inside the .env file, add your secret keys:

   ```bash
      DATABASE_URL="your_supabase_or_postgres_url_here"
      # Add any other required secrets here 
   ```
    
3. Build and Run with Docker
Thanks to docker-compose, booting up the entire infrastructure takes just one command:

    ```bash  
    docker compose up --build  
    ```

    * Frontend: Visit http://localhost:8501

    * Backend API Docs: Visit http://localhost:8000/docs to see the automated Swagger UI.

##  Cloud Deployment (AWS EC2)

This application is production-ready and designed to be hosted on a cloud server.

   1. Provision an EC2 Instance: Ubuntu LTS recommended.

   2. Open Firewalls: Ensure Inbound Rules in the AWS Security Group allow Custom TCP traffic on ports     8000 and 8501.

   3. Transfer Code & Secrets: Clone the repo and securely recreate the .env file on the server.

   4. Launch in Background:

   ```bash
   sudo docker compose up -d --build
   ```
   5. Monitor Logs:

   ```bash
   sudo docker compose logs -f
   ```

## Built by keshav-c0de
