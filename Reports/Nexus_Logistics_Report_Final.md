# NEXUS LOGISTICS COMMAND CENTER

## A NoSQL-Powered Global Supply Chain Intelligence Platform

**Project: Lab Terminal Project — Nexus Logistics
Command Center
Subject:** Advanced Database Systems
**Instructor:** Sir Basit Raza
**University:** COMSATS University Islamabad, Islamabad
Campus
**Session:** Spring 2026
**Submitted By:** • Abdullah Faisal (FA24-BCS-006)

- Hashaam Sargaana (FA24-BCS-047)
- Anas Khalid (FA24-BCS-018)


## Table of Contents

**1. Project Recap & Data Scaling**
1.1 Database Recap
1.2 Data Scaling & Synthetic Generation
**2. System Architecture**
2.1 Frontend Framework — Streamlit
2.2 Technology Stack
**3. The Nexus Logistics Command Center (GUI)**
3.1 Global Operations & Telemetry Dashboard
3.2 Investigative Queries & Analytics
3.3 Command & Control — Dispatch Terminal
**4. Advanced Database Implementations (Post-Midterm Labs)**
4.1 Optimistic Concurrency Control (OCC)
4.2 Database Views
4.3 Security & NoSQL Injection Prevention
4.4 Role-Based Access Control (RBAC)
4.5 Scaling Strategy — Sharding
4.6 Cloud Database Comparative Analysis
**5. Conclusion
6. References**


## 1. Project Recap & Data Scaling

### 1.1 Database Recap

The Nexus Logistics platform is built on a MongoDB NoSQL database comprising 12 distinct collections,
originally derived from a normalized relational schema of 34 entities across seven functional domains.
These collections span the core operational areas of a global supply chain intelligence system:
**Collection Description
shipment_ops** Core shipment contracts — embeds items, customs
clearance, and status history
**driver_performance** Driver profiles with embedded licenses, safety scores,
and complaints
**fleet_assets** Vehicle specifications, registration, and current health
diagnostics
**telemetry_stream** High-frequency IoT telemetry (GPS, engine temp, fuel
level) per vehicle
**maintenance_history** Scheduled and unscheduled maintenance records
linked to vehicles
**warehouse_hubs** Warehouse locations with embedded bin locations,
loading docks, and security
**route_intelligence** Defined logistics routes with embedded tolls, weather,
and traffic data
**regional_policies** Provincial tax rules and regulatory laws
**client_portals** Customer accounts with billing details and credit
standing
**supplier_network** Vendor profiles with contact details and performance
ratings
**incident_reports** Operational incidents with embedded investigations
and insurance claims
**audit_logs** System audit trail recording all data modification
events
Through principled NoSQL denormalization strategies — including 1:1 embedding, 1:M hybrid
embedding, and M:N array-of-references patterns — these 12 collections eliminate the need for
multi-table JOIN operations that would severely degrade performance at scale. The guiding design
principle was simple: operationally cohesive data is physically co-located within a single document.

### 1.2 Data Scaling & Synthetic Generation

The Nexus Logistics database was scaled from an initial test dataset of approximately 7,000 documents
to a production-scale dataset of ~350,000 documents. This scaling was achieved through the
Python-based data generation script (`Generator.py`), which leverages the `Faker` library to produce
realistic, enterprise-scale synthetic logistics data.
**Key aspects of the data generation methodology:**
● Referential Integrity: The generator seeds static entities first (warehouses, routes, drivers,
vehicles), then generates dependent entities (shipments, incidents) with valid foreign key
references, ensuring no orphaned documents exist.


● Weighted Distributions: Rather than uniform random data, the generator uses weighted
probability distributions to produce realistic data patterns — most shipments are standard cargo,
with a small percentage classified as high-value (declaration value > 500,000 PKR).
● Temporal Realism: Timestamps are generated with realistic date ranges, ensuring that telemetry
data, status history events, and incident reports follow chronological order.
● Collection-Level Scaling: Each of the 12 collections receives proportionally scaled data, with
high-volume collections like `telemetry_stream` and `shipment_ops` receiving the majority of
generated records to simulate real-world data distribution patterns.
● JSON Serialization: The final output is serialized into JSON arrays compatible with `mongoimport`
or direct `insertMany()` operations, enabling rapid database population.
This synthetic data generation approach allows the team to stress-test the database under realistic load
conditions, validate query performance at scale, and demonstrate the system's ability to handle
enterprise-level data volumes without relying on production data.

## 2. System Architecture

### 2.1 Frontend Framework — Streamlit

The Nexus Logistics Command Center utilizes Streamlit as its primary frontend framework. Streamlit was
selected for this project based on several architectural advantages:
● Rapid Prototyping: Streamlit's single-file Python application model enables rapid development
and iteration. The entire GUI was built and refined within a single Python file (`StreamlitGUI.py`),
eliminating the need for separate frontend/backend codebases.
● Native Python Integration: Streamlit runs Python natively, allowing direct integration with
PyMongo for database operations. This eliminates the need for REST API layers or data
serialization/deserialization between frontend and backend.
● Data-Heavy Dashboard Capabilities: Streamlit natively supports pandas DataFrames, Plotly
charts, and interactive widgets (text inputs, selectboxes, radio buttons, forms), making it ideal
for building operational dashboards that display real-time logistics data.
● Session State Management: Streamlit's `st.session_state` enables persistent state across script
re-runs, which was essential for implementing the OCC simulation and maintaining user
interaction context.
● Caching Support: Streamlit's `@st.cache_data` and `@st.cache_resource` decorators enable
efficient caching of expensive database queries, reducing redundant computation and improving
dashboard responsiveness.


### 2.2 Technology Stack

```
Component Technology Justification
Database Engine MongoDB 5.0 (NoSQL) Native document model,
compound multikey indexing,
aggregation pipeline, horizontal
scaling via sharding
Containerization Docker Isolated, reproducible deployment;
eliminates host OS dependency
issues
Frontend Framework Streamlit Rapid Python-based dashboard
development with native PyMongo
integration
Data Generation Python + Faker Library Programmatic generation of
realistic synthetic logistics data
Query Interface mongosh (MongoDB Shell) Full-featured JavaScript shell for
CRUD operations, aggregation, and
index management
Charting Plotly Express Interactive, publication-quality
charts embedded in Streamlit
Data Processing pandas DataFrame manipulation for
displaying query results in tabular
format
OS Environment Fedora Linux Open-source, production-grade
server OS used as the Docker host
```
## 3. The Nexus Logistics Command Center (GUI)

The Nexus Logistics Command Center is the primary operational interface for dispatch coordinators, fleet
managers, and logistics analysts. Built entirely in Streamlit, the application provides a comprehensive
suite of tools for monitoring, querying, and managing the logistics database.

### 3.1 Global Operations & Telemetry Dashboard

The dashboard's primary view presents real-time Key Performance Indicators (KPIs) and operational
charts, providing dispatch coordinators with an instant snapshot of the entire network's health.
**Key dashboard components include:**
● KPI Metrics Row: Four primary metrics are displayed — Total Shipments, In-Transit Shipments,
Delayed High-Value Shipments (declaration value > 500,000 PKR), and Total Fleet Vehicles. The
Delayed High-Value metric includes an inverse delta indicator that turns red when delayed
high-value shipments exceed zero, providing immediate visual alerting.
● Network Pipeline Health Chart: A horizontal bar chart shows the volume of shipments by
operational status (Picked Up, In-Transit, Delayed). This chart uses a $group aggregation pipeline
to count shipments by their most recent status, providing instant visibility into the distribution of
shipments across the logistics pipeline.


```
● Capital in Transit Chart: A line chart displays the daily declared value of shipments over time,
providing financial oversight. This chart uses a $match and $group pipeline to aggregate
declaration values by date, enabling management to track capital flow patterns.
● IoT Anomaly Detection: The system monitors vehicle telemetry data for critical engine
temperatures (>105°C). A dedicated alert banner displays the count of vehicles requiring
immediate maintenance, with a manual refresh button to force a fresh scan.
```
### 3.2 Investigative Queries & Analytics

The Investigative Queries section provides four specialized analytical tabs, each designed to answer
specific operational questions that logistics managers face daily.
**Tab A: Driver Incident & Liability Center**
This tab serves two purposes. First, the Individual Driver Lookup allows coordinators to search for any
driver by ID and retrieve all associated incident reports.


Second, the Monthly Liability Report identifies the top 20 drivers causing the most financial damage.
Originally implemented as a 7-stage aggregation pipeline in Python, this report was migrated to a
MongoDB View (`vw_monthly_liability`) to improve performance and simplify the code. The view
performs $group, $lookup, $unwind, and $project stages natively within the database, returning
pre-computed results to the application layer.
**Tab B: Shipment & Customer Lookup**
This tab provides two search capabilities. The Shipment ID search retrieves the complete shipment
profile — including embedded items, customs clearance details, and status history — and displays it in a
clean, structured layout. The Customer ID search lists all shipments associated with a given customer,
with a limit of 50 results for performance.


Both searches implement NoSQL injection prevention through the `sanitize_input()` utility function,
which type-casts all user inputs to strings before passing them to PyMongo queries.
**Tab C: Top 10 High-Value Shipments**
This tab displays the 10 shipments with the highest declared values, sorted in descending order. Each
entry shows the shipment ID, customer ID, declaration value (formatted in PKR), and customs clearance


status. This query leverages the compound multikey index `idx_dispatch_priority` on `shipment_ops` for
efficient sorting.
**Tab D: Vehicle Maintenance History**
This tab allows coordinators to search for any vehicle by ID and retrieve its complete maintenance
history from the `maintenance_history` collection. Each record shows the service type, repair details,
parts replaced, and associated costs.


### 3.3 Command & Control — Dispatch Terminal

The Dispatch Terminal is the operational heart of the Nexus Logistics Command Center. It provides a
no-code interface that allows dispatch coordinators to create new shipment records via an interactive
form.
**Key features of the Dispatch Terminal:**
● Referential Integrity via Dropdowns: All entity selections (Customer, Driver, Vehicle, Route,
Vendor) are populated from live database queries, ensuring that only valid, existing references
can be selected. This prevents orphaned records and maintains data consistency.
● Automated Shipment ID Generation: The form automatically generates a unique shipment ID in a
timestamp-based format (NEX-SHIP-{timestamp}), which can be overridden if needed.
● Nested JSON Injection: When the form is submitted, the application constructs a complete
shipment document with embedded `customs_clearance`, `items` array, and `status_history`
array, then inserts it into the `shipment_ops` collection via `insert_one()`.
● Real-Time Feedback: Upon successful dispatch, the system displays a confirmation message with
shipment details and a celebratory animation.

## 4. Advanced Database Implementations (Post-Midterm Labs)

### 4.1 Optimistic Concurrency Control (OCC)

Optimistic Concurrency Control (OCC) is a concurrency control mechanism that allows multiple
transactions to proceed without locking resources, detecting conflicts only at commit time. Unlike
pessimistic locking (which prevents conflicts by acquiring locks upfront), OCC assumes that concurrent
modifications are rare and optimizes for the common case of no conflicts.
**How OCC Prevents Lost Updates**
In a logistics environment, multiple dispatch coordinators may simultaneously view and attempt to
update the same shipment document. Without concurrency control, the last writer wins — overwriting


any changes made by other coordinators. This 'lost update' problem can result in critical operational data
being silently discarded.
**Implementation Details**
The OCC simulation was implemented as a dedicated tab (Tab E) in the Streamlit application. The
simulation uses a dedicated `occ_demo` collection with a document structure that includes a version
field (`__v`):
**The implementation follows a three-phase Read-Verify-Write cycle:**
● Read Phase: Each dispatcher clicks 'Read Document' to capture the current database version.
This version is stored in Streamlit's session state, simulating the dispatcher's local copy of the
document.
● Verify Phase: When a dispatcher clicks 'Update Status', the application first checks whether the
stored version matches the current database version. If another dispatcher updated the
document in the meantime, the versions will differ, and the conflict is detected.
● Write Phase: Only if the versions match does the actual MongoDB update proceed. The update
uses a version-matching filter (`{__v: current_version}`) and increments the version counter
(`$inc: {__v: 1}`).
**Technical Implementation:**
The PyMongo update query requires the version to match: `db.occ_demo.update_one({'_id': 'TEST-123',
'__v': current_version}, {'$set': {'status': new_status}, '$inc': {'__v': 1}})`. If `modified_count == 0`, the
update failed because the version didn't match, indicating a concurrent modification.

### 4.2 Database Views

MongoDB Views provide a powerful mechanism for encapsulating complex aggregation pipelines as
named, queryable entities. By moving aggregation logic from the application layer into the database
layer, Views simplify application code, improve maintainability, and ensure consistent query results.
**The vw_monthly_liability View**
The 'Monthly Liability Report' was originally implemented as a 7-stage aggregation pipeline in Python
(Streamlit), consisting of $match, $group, $lookup, $unwind, $project, $sort, and $limit stages. This
pipeline was migrated to a MongoDB View named `vw_monthly_liability`.


**The view pipeline performs the following operations:**
● Stage 1 — Month Extraction: Extracts the year-month portion from each incident's timestamp
using `$substr`.
● Stage 2 — Aggregation: Groups incidents by driver ID, summing total damage costs, counting
incidents, collecting incident IDs, and calculating average damage.
● Stage 3 — Driver Lookup: Performs a `$lookup` against the `driver_performance` collection to
retrieve driver names and safety scores.
● Stage 4 — Projection: Formats the final output with clean field names (DriverID, DriverName,
SafetyScore, TotalDamagePKR, etc.).
After the view creation, the Streamlit application code was simplified from a 40+ line aggregation
pipeline to a single line: `liability_data = list(db.vw_monthly_liability.find({}))`.

### 4.3 Security & NoSQL Injection Prevention

**4.3.1 Application-Layer Input Sanitization**
NoSQL injection is a security vulnerability where attackers inject MongoDB query operators (such as
`$ne`, `$gt`, `$regex`) into user input fields to manipulate query behavior. For example, entering `{"$ne":
null}` as a search term could bypass authentication or extract unauthorized data.
The practical implementation of NoSQL injection prevention in Nexus Logistics uses a `sanitize_input()`
utility function that type-casts all user inputs to strings before passing them to PyMongo queries:
When a user enters `{"$ne": null}` as text input, `str()` converts it to the literal string `'{$ne: null}'` —
which is NOT interpreted as a MongoDB query operator. The database treats it as plain text data,
searching for documents where the field literally contains that string.
**Sanitization is applied to all user-facing search inputs:**
● Driver ID search (Tab A)
● Shipment ID search (Tab B)
● Customer ID search (Tab B)


● Vehicle ID search (Tab D)
**4.3.2 Database-Level Schema Validation**
In addition to application-layer sanitization, MongoDB's `$jsonSchema` validation provides a
database-level enforcement mechanism that rejects documents violating the defined schema.
The `shipment_ops` collection was configured with the following validation rules using the `collMod`
command:
**Field Type Validation Rule
_id** string Required — must be a string
**customer_id** string Required — must be a string
**path_id** string Required — must be a string
**assigned_driver** string Must be a string
**assigned_vehicle** string Must be a string
**created_at** string Must be a string (timestamp)
**customs_clearance.status** string Enum: Pending, Cleared, Rejected,
Held
**customs_clearance.declaration_val
ue**
integer Must be an integer
**items** array Must be an array
**status_history** array Must be an array
The validation was applied with `validationLevel: 'moderate'` (only new and updated documents are
validated, not existing ones) and `validationAction: 'error'` (invalid documents are rejected).

### 4.4 Role-Based Access Control (RBAC)

The Nexus Logistics platform uses a Docker-based MongoDB deployment with authentication enabled.
The local development environment uses root-level credentials for simplicity:
**Parameter Value
Username** admin
**Password** password (as defined in docker-compose.yaml)
**Authentication Database** admin
**Connection String** mongodb://admin:password@localhost:27017/
**Role** root (full administrative access)


While this approach is acceptable for local development and lab evaluation, a production deployment
would require scoped, least-privilege users:
**Role Database Privileges Use Case
nexus_dashboard** NexusLogisticsDB read (find, aggregate) Read-only dashboard
clients
**nexus_app** NexusLogisticsDB readWrite Dispatch terminal, CRUD
operations
**nexus_admin** NexusLogisticsDB dbOwner Administrative operations
**nexus_monitor** admin dbStats, serverStatus Monitoring and alerting
systems
Additional security recommendations include TLS/SSL encryption for all connections, network isolation
via Docker networks or VPCs, automated password rotation, MongoDB audit logging, and IP whitelisting.

### 4.5 Scaling Strategy — Sharding

Sharding is MongoDB's horizontal scaling strategy, distributing data across multiple machines to scale
with growing data volume and throughput. For Nexus Logistics, which scales from 350,000 to potentially
millions of documents, strategic shard key selection is critical for maintaining sub-millisecond query
performance.
**An ideal shard key must satisfy three conditions:**
● High Cardinality: Enough unique values to distribute data evenly
● Query Pattern Alignment: Queries should hit only one shard (or a predictable subset)
● Write Distribution: Writes should spread evenly to avoid hotspots
**Recommended Shard Keys by Collection:
Collection Shard Key Type Reasoning
telemetry_stream** { vehicle_id: 'hashed' } Hashed Evenly distributes
high-velocity IoT writes;
prevents write hotspots
**shipment_ops** { created_at: 1, _id: 1 } Ranged Natural time-based
partitioning; efficient
range queries
**driver_performance** { _id: 1 } Ranged Low write volume;
queries by driver ID
**fleet_assets** { _id: 1 } Ranged Static reference data
**warehouse_hubs** { province_id: 1 } Ranged Queries often filter by
region
**incident_reports** {
incident_details.timestam
p: 1 }
Ranged Time-based investigation
queries
**audit_logs** { timestamp: 1 } Ranged Time-series audit trail
The hashed shard key on `telemetry_stream` is particularly important because this collection
experiences the highest write throughput — each vehicle generates thousands of telemetry pings per


day. A hashed key ensures writes are uniformly distributed across all shards, preventing any single shard
from becoming a bottleneck.
The ranged shard key on `shipment_ops` leverages the `created_at` field, which naturally partitions data
chronologically. Recent shipments reside on newer shards, while older shipments can be archived to
cheaper storage. The compound key `{ created_at: 1, _id: 1 }` breaks ties when multiple shipments share
the same timestamp.

### 4.6 Cloud Database Comparative Analysis

This section presents a formal comparison of MongoDB against three major cloud-native document
databases: AWS DynamoDB, Google Firestore, and Azure Cosmos DB. The evaluation focuses on the
specific requirements of the Nexus Logistics platform.
**Feature MongoDB
(Selected)
AWS DynamoDB Google Firestore Azure Cosmos DB
Data Model** Document (BSON) Key-Value/Documen
t
Document Multi-model
**Aggregation** Full pipeline (40+
stages)
Limited (Query +
Scan)
Limited Basic
**Nested Arrays** Native, queryable Limited Native Native
**$lookup (JOINs)** Supported Not supported Not supported Partial
**Multikey Index** Full support Not supported Not supported Partial
**Scalability** Horizontal
(sharding)
Automatic Automatic Automatic
**ACID Transactions** Multi-document Single-document Single-document Multi-document
**Free Tier** Self-hosted (free) 25 GB + 1M ops 5 GB + 50K reads 25 GB + 400 RU
**Use Case Analysis:
Requirement 1: Deeply Nested Logistical Arrays**
The `shipment_ops` document embeds arrays of `items`, `status_history`, and nested
`customs_clearance` objects. MongoDB provides native support for querying within nested arrays using
`$elemMatch`, positional operators, and multikey indexes — a capability no cloud alternative matches
natively.
**Requirement 2: Heavy Aggregation Pipelines**
The 'Monthly Liability Report' requires `$group`, `$lookup`, `$match`, `$project`, and `$sort` stages.
MongoDB's 40+ stage aggregation pipeline enables this level of complexity within the database engine.
Cloud alternatives require pulling data into the application layer for equivalent processing.
**Requirement 3: Real-Time Query Performance**
MongoDB's compound multikey index on `shipment_ops` reduced document examination from 953 to
30 (96.9% reduction), transforming query complexity from O(n) to O(log n). While DynamoDB offers
slightly faster, single-digit-millisecond responses for simple key lookups, MongoDB provides the best
balance of speed and query flexibility.


**Conclusion: Why MongoDB for Nexus Logistics**
MongoDB was the correct technology choice for Nexus Logistics for three decisive reasons:
● Multikey Index Performance: The compound multikey index is a capability no cloud alternative
supports natively on nested arrays.
● Aggregation Pipeline Depth: The 40+ stage pipeline enables complex analytical queries within
the database engine, eliminating the need for application-layer processing.
● Document Model Alignment: The deeply nested shipment model maps naturally to MongoDB's
BSON format, whereas cloud alternatives either lack nested-array query support or limit array
operations.

## 5. Conclusion

The Nexus Logistics Command Center demonstrates the successful application of modern NoSQL
database architecture to a real-world, high-stakes operational context. The project evolved from a
foundational 34-entity relational model to 12 optimized MongoDB collections via principled NoSQL
denormalization, achieving sub-millisecond query performance through strategic compound multikey
indexing.
The integration of Streamlit as a frontend framework transformed the database from a command-line
tool into an interactive operational platform, providing dispatch coordinators with real-time visibility into
shipment status, driver performance, fleet health, and financial metrics.
The post-midterm lab implementations — Optimistic Concurrency Control, MongoDB Views, NoSQL
injection prevention, schema validation, RBAC evaluation, and sharding strategy — demonstrate
comprehensive mastery of advanced database concepts and their practical application to
production-grade systems.
The comparative analysis against cloud alternatives (AWS DynamoDB, Google Firestore, Azure Cosmos
DB) confirms that MongoDB's document model, aggregation pipeline, and multikey indexing capabilities
make it the optimal choice for Nexus Logistics' specific requirements of deeply nested data structures
and complex analytical queries.
As the platform scales toward enterprise-level data volumes, the theoretical sharding strategy provides a
clear roadmap for horizontal scaling, ensuring the system maintains its performance characteristics as
the database grows from 350,000 to millions of documents.


## 6. References

[1] MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Indexing Strategies.
https://www.mongodb.com/docs/manual/indexes/
[2] MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Aggregation Pipeline.
https://www.mongodb.com/docs/manual/aggregation/
[3] MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Data Modeling Introduction.
https://www.mongodb.com/docs/manual/core/data-modeling-introduction/
[4] Banker, K., Bakkum, P., Hawkins, S., Membrey, P., & Thielman, T. (2016). MongoDB in Action (2nd ed.).
Manning Publications.
[5] COMSATS University Islamabad (2024). Advanced Database Systems — Lab Manual. Department of
Computer Science.
[6] Chodorow, K. (2013). MongoDB: The Definitive Guide (2nd ed.). O'Reilly Media.
[7] Python Software Foundation (2024). Faker Library Documentation. https://faker.readthedocs.io/
[8] Docker, Inc. (2024). Docker Documentation — Volumes and Bind Mounts.
https://docs.docker.com/storage/


