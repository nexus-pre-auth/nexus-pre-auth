# Nexus Pre-Auth

**A V28-Native Risk Adjustment Engine by CodemedGroup/NexusAuth AI**

Nexus Pre-Auth is the flagship repository for CodemedGroup's V28-Native Risk Adjustment Engine. It provides a high-performance, secure, and auditable solution for processing healthcare data, specifically designed for V28 risk adjustment. The engine is built with a PHI-blind architecture to ensure patient privacy and data integrity, using SHA-256 hashing to create an immutable audit trail.

## Key Features

- **V28-Native Analysis**: Core functionality is built around the V28 risk adjustment model.
- **PHI-Blind Architecture**: Ensures that no Protected Health Information (PHI) is processed or stored, enhancing security and compliance.
- **Data Integrity**: Utilizes SHA-256 hashing to ensure the integrity of data as it is processed.
- **High Performance**: Built with FastAPI and asynchronous processing for speed and scalability.
- **Auditable**: Every transaction is logged, creating a clear and immutable audit trail.

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy (with asyncpg)
- **API Interaction**: HTTPX, Pydantic
- **Containerization**: Docker
- **Utilities**: Loguru, python-dotenv

## Project Structure

```
/nexus-pre-auth
├── Caddyfile
├── Dockerfile
├── LICENSE
├── README.md
├── data/
├── deploy.sh
├── docker-compose.prod.yml
├── docker-compose.yml
├── frontend/
├── main.py
├── requirements.txt
├── scripts/
├── src/
└── tests/
```

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/nexus-pre-auth/nexus-pre-auth.git
    cd nexus-pre-auth
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**

    ```bash
    uvicorn main:app --reload
    ```

## API Endpoints

The primary endpoint for the service is:

- `POST /v28/analyze`: Accepts a `chart_id` and `note_text`, extracts V28 HCC signals, and returns the RAF lift, HCC code, audit UUID, and SHA-256 integrity hash.
- `GET /health`: Returns the service health status.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
