# 🌤️ Automated Weather ELT Pipeline

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Airflow](https://img.shields.io/badge/Airflow-3.0.0-017CEE?logo=apache-airflow)](https://airflow.apache.org/)
[![DBT](https://img.shields.io/badge/DBT-1.9-FF694B?logo=dbt)](https://www.getdbt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.17-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📊 Project Overview

A production-ready ELT (Extract, Load, Transform) pipeline that extracts real-time weather data via Weatherstack API, orchestrates SQL-based transformations with DBT, and visualizes insights through Apache Superset. This project demonstrates modern data engineering best practices for micro-batch processing without the overhead of distributed computing frameworks.

**Core Value Proposition:** Right-sized architecture that prioritizes maintainability, idempotency, and developer experience over premature optimization.

---

## 🏗️ High-Level Architecture

```
┌─────────────────┐
│ Weatherstack API│
│  (Every 10 min) │
└────────┬────────┘
         │ HTTP GET
         ▼
┌─────────────────────────────┐
│   Apache Airflow (3.0.0)    │
│  ┌──────────────────────┐   │
│  │  PythonOperator      │   │
│  │  - Fetch API data    │   │
│  │  - Insert to Postgres│   │
│  └──────────┬───────────┘   │
│             │                │
│             ▼                │
│  ┌──────────────────────┐   │
│  │  DockerOperator      │   │
│  │  - Run DBT models    │   │
│  └──────────────────────┘   │
└─────────────┬───────────────┘
              │
              ▼
┌──────────────────────────────┐
│   PostgreSQL (14.17)         │
│  ┌─────────────────────┐     │
│  │ dev.raw_weather_data│     │
│  └──────────┬──────────┘     │
│             │ DBT Transform  │
│             ▼                │
│  ┌─────────────────────┐     │
│  │ Staging Layer       │     │
│  │ - Deduplication     │     │
│  │ - Type casting      │     │
│  └──────────┬──────────┘     │
│             ▼                │
│  ┌─────────────────────┐     │
│  │ Mart Layer          │     │
│  │ - Daily aggregates  │     │
│  │ - Weather reports   │     │
│  └─────────────────────┘     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Apache Superset (3.0.0)    │
│   - Temperature trends       │
│   - Humidity distribution    │
│   - Wind speed analytics     │
└──────────────────────────────┘
```

**[Suggested: Insert actual architecture diagram here]**

---

## 🎯 Key Design Decisions

### Why DBT over Spark?
**Problem:** Processing ~144 API records per day (10-minute intervals)  
**Analysis:** Spark cluster startup overhead (10-20 seconds) exceeds actual transformation time (<0.5 seconds)  
**Solution:** SQL-first transformations via PostgreSQL + DBT  
**Result:** Sub-second query execution, zero infrastructure complexity

### Why DockerOperator for DBT?
**Problem:** Python dependency conflicts between Airflow and DBT packages  
**Solution:** Isolated DBT execution in ephemeral Docker containers  
**Result:** Clean separation of concerns, reproducible builds

### Idempotency by Design
**Problem:** Airflow retries cause duplicate data insertion  
**Solution:** Window function deduplication in DBT staging layer  
```sql
WITH de_dup AS (
    SELECT *, 
           row_number() OVER(PARTITION BY time ORDER BY inserted_at) AS rn
    FROM source
)
SELECT * FROM de_dup WHERE rn = 1
```
**Result:** Retry-safe pipeline operations

### 10-Minute Scheduling (Not Real-Time)
**Reasoning:**
- Weatherstack API rate limits: 1,000 requests/month (free tier)
- Weather patterns change gradually (minutes, not milliseconds)
- Batch processing reduces complexity without sacrificing business value

---

## 📋 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 4.x+ | Container orchestration |
| Docker Compose | 2.x+ | Multi-service management |
| Weatherstack API Key | Free tier | Weather data source |

**System Requirements:**
- 4 GB RAM minimum
- 10 GB free disk space

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/adamxiang/automated-elt-pipeline.git
cd automated-elt-pipeline
```

### 2. Obtain API Key
Register at [Weatherstack](https://weatherstack.com/) for a free API key (1,000 requests/month).

### 3. Start Infrastructure
```bash
docker-compose up -d
```

**Services Startup Time:** ~2 minutes

### 4. Configure Airflow Variables
Access Airflow UI at `http://localhost:8000` (username: `admin`, password: check logs)

Navigate to **Admin > Variables** and add:
```
WEATHER_API_KEY = your_weatherstack_api_key
DB_PASSWORD = postgres
```

### 5. Trigger DAG
```bash
# Via UI: Toggle ON the weather_api_orchestrator DAG
# Or via CLI:
docker exec -it airflow_container airflow dags trigger weather_api_orchestrator
```

### 6. Access Dashboards
- **Airflow:** http://localhost:8000
- **Superset:** http://localhost:8088 (username: `admin`, password: `admin`)

---

## 📂 Project Structure

```
automated-elt-pipeline/
├── dags/
│   └── orchestrator.py          # Main Airflow DAG definition
│       ├── Task 1: API extraction & database insertion
│       └── Task 2: DBT transformation via DockerOperator
│
├── api-request/
│   ├── api_request.py           # Weatherstack API client
│   └── insert_records.py        # PostgreSQL insertion with error handling
│
├── dbt/weather_project/
│   ├── models/
│   │   ├── sources/
│   │   │   └── sources.yml      # Raw table definitions
│   │   ├── staging/
│   │   │   └── staging_weather_data.sql  # Deduplication logic
│   │   └── mart/
│   │       ├── daily_average.sql         # Aggregated metrics
│   │       └── weather_report.sql        # Clean reporting table
│   └── dbt_project.yml
│
├── postgres/
│   ├── airflow_init.sql         # Airflow metadata database
│   └── superset_init.sql        # Superset metadata database
│
├── docker-compose.yaml          # Multi-container orchestration
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🔧 Usage Guide

### Manual DAG Trigger
```bash
# Start the DAG immediately
docker exec -it airflow_container airflow dags trigger weather_api_orchestrator

# View DAG runs
docker exec -it airflow_container airflow dags list-runs -d weather_api_orchestrator
```

### DBT Operations
```bash
# Run all transformation models
docker exec -it dbt_container dbt run

# Run specific model
docker exec -it dbt_container dbt run --select staging_weather_data

# Test data quality (if tests are defined)
docker exec -it dbt_container dbt test

# Generate documentation
docker exec -it dbt_container dbt docs generate
docker exec -it dbt_container dbt docs serve
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it postgres_container psql -U weather_user -d weather_db

# Query raw data
SELECT * FROM dev.raw_weather_data ORDER BY inserted_at DESC LIMIT 10;

# Query transformed data
SELECT * FROM dev.daily_average ORDER BY date DESC;
```

---

## 🧪 Data Quality & Error Handling

### API Validation
**Implementation:** `insert_records.py`
```python
if 'current' not in data:
    print(f"❌ CRITICAL ERROR: API response missing 'current' key.")
    print(f"❌ BAD DATA: {json.dumps(data, indent=2)}")
    raise KeyError("Missing 'current' key in API response")
```

**Handles:**
- Malformed API responses
- Rate limit errors
- Network timeouts

### Retry Strategy
**Airflow Configuration:**
```python
default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
```

### Deduplication Logic
**DBT Staging Layer:**
- Uses `row_number()` window function to identify duplicate records
- Preserves latest insertion timestamp
- Ensures idempotency across pipeline retries

---

## 📈 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| End-to-End Latency | ~2 minutes | API call → DBT transform → Dashboard refresh |
| Data Volume | ~10,000 records | Adequate for single-node PostgreSQL |
| Schedule Interval | 10 minutes | Balances API rate limits with data freshness |
| Database Size | <50 MB | Includes raw + transformed tables |
| Docker Memory Usage | ~3 GB | All services combined |

---

## 🚧 Known Limitations & Roadmap

### Current Limitations
- ❌ No DBT tests for data validation
- ❌ No automated alerts for DAG failures
- ❌ Single-city tracking (Taipei only)
- ❌ No historical data backfilling mechanism

### Planned Enhancements
- [ ] **Q2 2026:** Implement DBT tests
  ```sql
  -- models/staging/staging_weather_data.yml
  tests:
    - dbt_utils.accepted_range:
        column_name: temperature
        min_value: -20
        max_value: 50
  ```

- [ ] **Q2 2026:** Add Slack/Email alerts
  ```python
  def alert_on_failure(context):
      slack_webhook = Variable.get("SLACK_WEBHOOK")
      # Send notification logic
  
  default_args = {
      'on_failure_callback': alert_on_failure
  }
  ```

- [ ] **Q3 2026:** Multi-city expansion (Tokyo, London, NYC)
- [ ] **Q4 2026:** Migrate to TimescaleDB for time-series optimization

---

## 🛠️ Troubleshooting

### Issue: Airflow DAG not appearing
**Solution:**
```bash
# Refresh DAG list
docker exec -it airflow_container airflow dags list-import-errors

# Restart Airflow scheduler
docker-compose restart airflow
```

### Issue: DBT command fails with "Connection refused"
**Solution:** Ensure PostgreSQL is fully initialized before running DBT
```bash
# Check PostgreSQL logs
docker logs postgres_container

# Wait for this line: "database system is ready to accept connections"
```

### Issue: Superset shows "No data"
**Solution:** Verify DBT models have been executed
```bash
# Check if tables exist
docker exec -it postgres_container psql -U weather_user -d weather_db -c "\dt dev.*"

# Re-run DBT models
docker exec -it dbt_container dbt run
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Code Style:**
- Python: PEP 8 compliance
- SQL: Use lowercase keywords, 2-space indentation
- DBT: Follow [dbt Style Guide](https://docs.getdbt.com/guides/best-practices/how-we-style/0-how-we-style-our-dbt-projects)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Architecture Inspiration:** Modern ELT patterns from [dbt Labs](https://www.getdbt.com/)
- **API Provider:** [Weatherstack](https://weatherstack.com/)
- **Community:** Apache Airflow and DBT Slack communities for troubleshooting support

---

## 📚 Additional Resources

- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DBT Style Guide](https://docs.getdbt.com/guides/best-practices/how-we-style/0-how-we-style-our-dbt-projects)
- [Superset Documentation](https://superset.apache.org/docs/intro)
- [ELT vs ETL: When to Use Which](https://www.getdbt.com/analytics-engineering/transformation/elt-vs-etl/)

---

## 📧 Contact

**Author:** Adam Chang  
**GitHub:** [@adamxiang](https://github.com/AdamXiang)  
**LinkedIn:** [Connect with me](https://www.linkedin.com/in/ching-hsiang-chang-782281217/)

---

## 🙏 Acknowledgments

* **Calvin Yoon** for providing this amazing project tutorial | [Youtube](https://www.youtube.com/@cyprojects)

---

**⭐ If this project helped you, consider giving it a star!**
