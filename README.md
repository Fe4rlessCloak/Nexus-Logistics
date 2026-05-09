# Nexus Logistics: Advanced NoSQL Engine

## Project Overview

**Nexus Logistics** is a specialized database system designed to address the challenges of real-time supply chain management. By leveraging a document-oriented architecture with MongoDB, the system replaces traditional relational bottlenecks with a denormalized, query-optimized model. The system manages a high-volume dataset of approximately **350,000 documents**.

### Key Focus Areas:
* **Shipment Tracking:** Monitoring high-value shipments in real-time.
* **Driver Performance:** Tracking metrics and efficiency.
* **Fleet Health:** Maintaining maintenance schedules and vehicle status.
* **Concurrency:** Supporting high-traffic, high-concurrency environments.

*Developed as part of the Advanced Databases curriculum at COMSATS University Islamabad.*

---

## Architectural Design

The database employs advanced NoSQL modeling techniques to ensure data locality and low-latency access:

### Embedded Data Model Pattern
* Consolidates **34 relational entities** into just **12 collections**.
* Eliminates expensive multi-table joins.
* Significantly improves read performance through data locality.

### Streamlit Management Dashboard
An interactive web-based interface providing:
* **Global Operations Overview:** Real-time KPIs and anomaly detection (e.g., IoT telemetry alerts for engine temperatures).
* **Common Operations (Query Center):** Deep-dive analytical tabs for Driver Incidents, Shipment/Customer lookups, High-Value shipment tracking, and Vehicle maintenance history.
* **Dispatch Terminal:** A command & control interface for real-time shipment deployment, including driver, vehicle, and route assignment.

---

## New Features (Post-Midterm Labs)

### 1. Optimistic Concurrency Control (OCC) Simulation
A dedicated tab in the Streamlit dashboard demonstrates how OCC prevents "lost updates" when multiple dispatchers attempt to modify the same document simultaneously. The simulation uses a `__v` version field to detect conflicts and reject stale writes.

**How it works:**
1. Each dispatcher "reads" the document to capture its current version.
2. When updating, the system verifies the version hasn't changed.
3. If a conflict is detected, the update is rejected with a clear error message.

### 2. MongoDB Views
The "Monthly Liability Report" was migrated from a 7-stage Python aggregation pipeline to a **MongoDB View** (`vw_monthly_liability`). This simplifies application code from 40+ lines to a single `find()` call while maintaining the same analytical output.

### 3. NoSQL Injection Prevention
All user inputs are sanitized through a `sanitize_input()` utility function that type-casts inputs to strings before passing them to PyMongo queries. This neutralizes NoSQL injection attacks (e.g., `{"$ne": null}`). Additionally, MongoDB `$jsonSchema` validation enforces strict data types on the `shipment_ops` collection at the database level.

---

## Execution Plan Analysis

Performance improvements were validated using MongoDB's `explain()` utility:

| Stage | Documents Examined | Method |
| :--- | :--- | :--- |
| **Pre-Optimization** | 953 | `COLLSCAN` (Collection Scan) |
| **Post-Optimization** | 30 | `IXSCAN` (Index Scan) |

### Results
* **96.8% reduction** in documents scanned.
* Achieves **$O(\log n)$** scalability.
* Highly efficient for datasets exceeding **1,000,000+ records**.

---

## Project Structure

```
lab-mid/
├── docker-compose.yaml          # Container orchestration (MongoDB + Seeder)
├── README.md                    # This file
├── docs/
│   ├── generate_final_report.py # Python script to generate .docx report
│   └── Nexus_Logistics_Final_Report.docx
├── Data/
│   └── Generator.py             # Synthetic data generation script
├── ERD/
│   └── ERD.plantuml             # Entity-Relationship Diagram source
├── JSON-Prototypes/             # Sample JSON documents for each collection
├── Reports/
│   ├── Nexus_Logistics_Report (Final)-1.md
│   ├── RBAC_Security_Documentation.md
│   ├── Sharding_Strategy_Documentation.md
│   └── Cloud_DB_Comparative_Analysis.md
├── src/
│   ├── StreamlitGUI.py          # Main Streamlit application
│   ├── setup_database_tasks.js  # Post-midterm database setup script
│   └── NexusData_Output/        # Generated JSON data files
└── To-Do/
    ├── Implement-All-Labs.md
    └── Implementation-Instruction-Manual.md
```

---

## Deployment & Environment

The system runs in a containerized environment to ensure consistency across development and production.

### Infrastructure Requirements
* **OS:** Any (tested on Fedora Linux)
* **Container Runtime:** Docker CE / Docker Compose
* **Database:** MongoDB 5.0
* **Python:** 3.10+ (for Streamlit and data generation)

### Getting Started

#### 1. Start the Database Container
```bash
docker compose up -d
```

This starts the MongoDB container and automatically seeds the database with synthetic data using the `seeder` service.

#### 2. Run Post-Midterm Database Setup (Required)

After the database is running, execute the setup script to create views, apply schema validation, and initialize the OCC demo collection:

**Method A — Direct execution (recommended):**
```bash
docker exec -it nexus-mongodb mongosh -u admin -p password \
  --authenticationDatabase admin < src/setup_database_tasks.js
```

**Method B — Interactive (paste contents into mongosh):**
```bash
docker exec -it nexus-mongodb mongosh -u admin -p password \
  --authenticationDatabase admin
# Then paste the entire contents of src/setup_database_tasks.js
```

**Method C — Copy file into container first:**
```bash
docker cp src/setup_database_tasks.js nexus-mongodb:/tmp/setup.js
docker exec -it nexus-mongodb mongosh -u admin -p password \
  --authenticationDatabase admin /tmp/setup.js
```

The script performs three operations:
1. **Initializes OCC Demo Collection** — Creates `occ_demo` with a test document.
2. **Creates MongoDB View** — Creates `vw_monthly_liability` for the Monthly Liability Report.
3. **Applies Schema Validation** — Enforces strict data types on `shipment_ops`.

#### 3. Launch Streamlit Dashboard
```bash
streamlit run src/StreamlitGUI.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`.

#### 4. Access MongoDB Shell (Optional)
```bash
docker exec -it nexus-mongodb mongosh -u admin -p password --authenticationDatabase admin
```

Once connected, switch to the project database:
```javascript
use NexusLogisticsDB
```

---

### Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10 | Data generation using Faker |
| Web Framework | Streamlit | Interactive dashboard |
| Database | MongoDB 5.0 | Document-oriented storage |
| Data Visualization | Pandas, Plotly Express | Charts and data tables |
| Modeling Tool | PlantUML | ERD generation |
| Environment | Docker | Containerized deployment |

---

### Docker Compose Configuration

The `docker-compose.yaml` file defines two services:

| Service | Image | Purpose |
|---------|-------|---------|
| `mongodb` | `mongo:5.0` | MongoDB database with authentication |
| `seeder` | `mongo:5.0` | One-time data population from JSON files |

The seeder service waits for MongoDB to be ready, then imports all JSON files from `src/NexusData_Output/` into their respective collections.

---

## Team

* **Abdullah Faisal** (FA24-BCS-006)
* **Hashaam Sargaana** (FA24-BCS-047)
* **Anas Khalid** (FA24-BCS-018)

**Instructor:** Sir Basit Raza  
**Subject:** Advanced Database Systems  
**Session:** Spring 2026
**University:** COMSATS University Islamabad, Islamabad Campus
