#!/usr/bin/env python3
"""
Nexus Logistics Command Center — Final Lab Report Generator
Generates a professional .docx file using python-docx.
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from datetime import datetime

doc = Document()

# ============================================================
# STYLES CONFIGURATION
# ============================================================
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

# Heading styles
for level in range(1, 4):
    heading_style = doc.styles[f'Heading {level}']
    heading_style.font.name = 'Calibri'
    heading_style.font.color.rgb = RGBColor(0, 51, 102)
    if level == 1:
        heading_style.font.size = Pt(18)
        heading_style.font.bold = True
    elif level == 2:
        heading_style.font.size = Pt(14)
        heading_style.font.bold = True
    elif level == 3:
        heading_style.font.size = Pt(12)
        heading_style.font.bold = True

# Set margins
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 51, 102)
    return p

def add_subtitle(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0, 51, 102)
    return p

def add_body(text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    return p

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 1.27)
    return p

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)
    # Data rows
    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_data in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(cell_data)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
    return table

def add_screenshot_placeholder(description):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"[INSERT SCREENSHOT HERE: {description}]")
    run.bold = True
    run.font.color.rgb = RGBColor(180, 0, 0)
    run.font.size = Pt(11)
    # Add a border box effect
    from docx.oxml.ns import qn
    pPr = p._p.get_or_add_pPr()
    pBdr = pPr.makeelement(qn('w:pBdr'), {})
    bottom = pBdr.makeelement(qn('w:bottom'), {
        qn('w:val'): 'single',
        qn('w:sz'): '12',
        qn('w:space'): '1',
        qn('w:color'): '003366'
    })
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

# ============================================================
# TITLE PAGE
# ============================================================
for _ in range(6):
    doc.add_paragraph()

add_title("NEXUS LOGISTICS COMMAND CENTER")
doc.add_paragraph()
add_subtitle("A NoSQL-Powered Global Supply Chain Intelligence Platform")
doc.add_paragraph()
doc.add_paragraph()

# Project metadata box
meta_table = doc.add_table(rows=9, cols=2)
meta_table.style = 'Light Shading Accent 1'
meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER

meta_data = [
    ("Project:", "Lab Terminal Project — Nexus Logistics Command Center"),
    ("Subject:", "Advanced Database Systems"),
    ("Instructor:", "Sir Basit Raza"),
    ("University:", "COMSATS University Islamabad, Islamabad Campus"),
    ("Session:", "Spring 2025"),
    ("Submitted By:", ""),
    ("", "• Abdullah Faisal (FA24-BCS-006)"),
    ("", "• Hashaam Sargaana (FA24-BCS-047)"),
    ("", "• Anas Khalid (FA24-BCS-018)"),
]

for i, (label, value) in enumerate(meta_data):
    cell_label = meta_table.rows[i].cells[0]
    cell_value = meta_table.rows[i].cells[1]
    run_l = cell_label.paragraphs[0].add_run(label)
    run_l.bold = True
    run_l.font.size = Pt(11)
    run_v = cell_value.paragraphs[0].add_run(value)
    run_v.font.size = Pt(11)
    if not value:
        cell_value.paragraphs[0].clear()

doc.add_page_break()

# ============================================================
# TABLE OF CONTENTS (Manual)
# ============================================================
doc.add_heading('Table of Contents', level=1)
doc.add_paragraph()

toc_items = [
    ("1.", "Project Recap & Data Scaling", "3"),
    ("", "1.1 Database Recap", "3"),
    ("", "1.2 Data Scaling & Synthetic Generation", "3"),
    ("2.", "System Architecture", "4"),
    ("", "2.1 Frontend Framework — Streamlit", "4"),
    ("", "2.2 Technology Stack", "4"),
    ("3.", "The Nexus Logistics Command Center (GUI)", "5"),
    ("", "3.1 Global Operations & Telemetry Dashboard", "5"),
    ("", "3.2 Investigative Queries & Analytics", "6"),
    ("", "3.3 Command & Control — Dispatch Terminal", "7"),
    ("4.", "Advanced Database Implementations (Post-Midterm Labs)", "8"),
    ("", "4.1 Optimistic Concurrency Control (OCC)", "8"),
    ("", "4.2 Database Views", "9"),
    ("", "4.3 Security & NoSQL Injection Prevention", "10"),
    ("", "4.4 Role-Based Access Control (RBAC)", "11"),
    ("", "4.5 Scaling Strategy — Sharding", "12"),
    ("", "4.6 Cloud Database Comparative Analysis", "13"),
    ("5.", "Conclusion", "15"),
    ("6.", "References", "15"),
]

for num, title, page in toc_items:
    p = doc.add_paragraph()
    if num:
        run = p.add_run(f"{num} {title}")
        run.bold = True
    else:
        run = p.add_run(f"    {title}")
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15))

doc.add_page_break()

# ============================================================
# SECTION 1: PROJECT RECAP & DATA SCALING
# ============================================================
doc.add_heading('1. Project Recap & Data Scaling', level=1)

doc.add_heading('1.1 Database Recap', level=2)
add_body(
    "The Nexus Logistics platform is built on a MongoDB NoSQL database comprising 12 distinct "
    "collections, originally derived from a normalized relational schema of 34 entities across "
    "seven functional domains. These collections span the core operational areas of a global "
    "supply chain intelligence system:"
)

collections_summary = [
    ("Collection", "Description"),
    ("shipment_ops", "Core shipment contracts — embeds items, customs clearance, and status history"),
    ("driver_performance", "Driver profiles with embedded licenses, safety scores, and complaints"),
    ("fleet_assets", "Vehicle specifications, registration, and current health diagnostics"),
    ("telemetry_stream", "High-frequency IoT telemetry (GPS, engine temp, fuel level) per vehicle"),
    ("maintenance_history", "Scheduled and unscheduled maintenance records linked to vehicles"),
    ("warehouse_hubs", "Warehouse locations with embedded bin locations, loading docks, and security"),
    ("route_intelligence", "Defined logistics routes with embedded tolls, weather, and traffic data"),
    ("regional_policies", "Provincial tax rules and regulatory laws"),
    ("client_portals", "Customer accounts with billing details and credit standing"),
    ("supplier_network", "Vendor profiles with contact details and performance ratings"),
    ("incident_reports", "Operational incidents with embedded investigations and insurance claims"),
    ("audit_logs", "System audit trail recording all data modification events"),
]
add_table(collections_summary[0], collections_summary[1:])

add_body(
    "Through principled NoSQL denormalization strategies — including 1:1 embedding, 1:M hybrid "
    "embedding, and M:N array-of-references patterns — these 12 collections eliminate the need "
    "for multi-table JOIN operations that would severely degrade performance at scale. The "
    "guiding design principle was simple: operationally cohesive data is physically co-located "
    "within a single document.",
    bold=False
)

doc.add_heading('1.2 Data Scaling & Synthetic Generation', level=2)
add_body(
    "The Nexus Logistics database was scaled from an initial test dataset of approximately 7,000 "
    "documents to a production-scale dataset of ~350,000 documents. This scaling was achieved "
    "through the Python-based data generation script (`Generator.py`), which leverages the "
    "`Faker` library to produce realistic, enterprise-scale synthetic logistics data."
)

add_body("Key aspects of the data generation methodology:", bold=True)
add_bullet(
    "Referential Integrity: The generator seeds static entities first (warehouses, routes, "
    "drivers, vehicles), then generates dependent entities (shipments, incidents) with valid "
    "foreign key references, ensuring no orphaned documents exist."
)
add_bullet(
    "Weighted Distributions: Rather than uniform random data, the generator uses weighted "
    "probability distributions to produce realistic data patterns — most shipments are standard "
    "cargo, with a small percentage classified as high-value (declaration value > 500,000 PKR)."
)
add_bullet(
    "Temporal Realism: Timestamps are generated with realistic date ranges, ensuring that "
    "telemetry data, status history events, and incident reports follow chronological order."
)
add_bullet(
    "Collection-Level Scaling: Each of the 12 collections receives proportionally scaled data, "
    "with high-volume collections like `telemetry_stream` and `shipment_ops` receiving the "
    "majority of generated records to simulate real-world data distribution patterns."
)
add_bullet(
    "JSON Serialization: The final output is serialized into JSON arrays compatible with "
    "`mongoimport` or direct `insertMany()` operations, enabling rapid database population."
)

add_body(
    "This synthetic data generation approach allows the team to stress-test the database under "
    "realistic load conditions, validate query performance at scale, and demonstrate the system's "
    "ability to handle enterprise-level data volumes without relying on production data."
)

doc.add_page_break()

# ============================================================
# SECTION 2: SYSTEM ARCHITECTURE
# ============================================================
doc.add_heading('2. System Architecture', level=1)

doc.add_heading('2.1 Frontend Framework — Streamlit', level=2)
add_body(
    "The Nexus Logistics Command Center utilizes Streamlit as its primary frontend framework. "
    "Streamlit was selected for this project based on several architectural advantages:"
)

add_bullet(
    "Rapid Prototyping: Streamlit's single-file Python application model enables rapid "
    "development and iteration. The entire GUI was built and refined within a single Python "
    "file (`StreamlitGUI.py`), eliminating the need for separate frontend/backend codebases."
)
add_bullet(
    "Native Python Integration: Streamlit runs Python natively, allowing direct integration "
    "with PyMongo for database operations. This eliminates the need for REST API layers or "
    "data serialization/deserialization between frontend and backend."
)
add_bullet(
    "Data-Heavy Dashboard Capabilities: Streamlit natively supports pandas DataFrames, "
    "Plotly charts, and interactive widgets (text inputs, selectboxes, radio buttons, forms), "
    "making it ideal for building operational dashboards that display real-time logistics data."
)
add_bullet(
    "Session State Management: Streamlit's `st.session_state` enables persistent state across "
    "script re-runs, which was essential for implementing the OCC simulation and maintaining "
    "user interaction context."
)
add_bullet(
    "Caching Support: Streamlit's `@st.cache_data` and `@st.cache_resource` decorators enable "
    "efficient caching of expensive database queries, reducing redundant computation and "
    "improving dashboard responsiveness."
)

doc.add_heading('2.2 Technology Stack', level=2)

tech_headers = ["Component", "Technology", "Justification"]
tech_rows = [
    ["Database Engine", "MongoDB 5.0 (NoSQL)", "Native document model, compound multikey indexing, aggregation pipeline, horizontal scaling via sharding"],
    ["Containerization", "Docker", "Isolated, reproducible deployment; eliminates host OS dependency issues"],
    ["Frontend Framework", "Streamlit", "Rapid Python-based dashboard development with native PyMongo integration"],
    ["Data Generation", "Python + Faker Library", "Programmatic generation of realistic synthetic logistics data"],
    ["Query Interface", "mongosh (MongoDB Shell)", "Full-featured JavaScript shell for CRUD operations, aggregation, and index management"],
    ["Charting", "Plotly Express", "Interactive, publication-quality charts embedded in Streamlit"],
    ["Data Processing", "pandas", "DataFrame manipulation for displaying query results in tabular format"],
    ["OS Environment", "Fedora Linux", "Open-source, production-grade server OS used as the Docker host"],
]
add_table(tech_headers, tech_rows)

doc.add_page_break()

# ============================================================
# SECTION 3: THE NEXUS LOGISTICS COMMAND CENTER (GUI)
# ============================================================
doc.add_heading('3. The Nexus Logistics Command Center (GUI)', level=1)
add_body(
    "The Nexus Logistics Command Center is the primary operational interface for dispatch "
    "coordinators, fleet managers, and logistics analysts. Built entirely in Streamlit, the "
    "application provides a comprehensive suite of tools for monitoring, querying, and managing "
    "the logistics database."
)

doc.add_heading('3.1 Global Operations & Telemetry Dashboard', level=2)
add_body(
    "The dashboard's primary view presents real-time Key Performance Indicators (KPIs) and "
    "operational charts that give dispatch coordinators an instant snapshot of the entire "
    "network's health."
)

add_body("Key dashboard components include:", bold=True)

add_bullet(
    "KPI Metrics Row: Four primary metrics are displayed — Total Shipments, In-Transit "
    "Shipments, Delayed High-Value Shipments (declaration value > 500,000 PKR), and Total "
    "Fleet Vehicles. The Delayed High-Value metric includes an inverse delta indicator that "
    "turns red when delayed high-value shipments exceed zero, providing immediate visual "
    "alerting."
)
add_bullet(
    "Network Pipeline Health Chart: A horizontal bar chart displays the volume of shipments "
    "in each operational status (Picked Up, In-Transit, Delayed). This chart uses a "
    "$group aggregation pipeline to count shipments by their most recent status, providing "
    "instant visibility into the distribution of shipments across the logistics pipeline."
)
add_bullet(
    "Capital in Transit Chart: A line chart displays the daily declared value of shipments "
    "over time, providing financial oversight. This chart uses a $match and $group pipeline "
    "to aggregate declaration values by date, enabling management to track capital flow "
    "patterns."
)
add_bullet(
    "IoT Anomaly Detection: The system monitors telemetry data for vehicles with critical "
    "engine temperatures (>105°C). A dedicated alert banner displays the count of vehicles "
    "requiring immediate maintenance, with a manual refresh button to force a fresh scan."
)

add_screenshot_placeholder("Main Dashboard showing KPI metrics, Pipeline Health bar chart, and Capital in Transit line chart")

doc.add_heading('3.2 Investigative Queries & Analytics', level=2)
add_body(
    "The Investigative Queries section provides four specialized analytical tabs, each designed "
    "to answer specific operational questions that logistics managers face daily."
)

add_body("Tab A: Driver Incident & Liability Center", bold=True)
add_body(
    "This tab serves two purposes. First, the Individual Driver Lookup allows coordinators to "
    "search for any driver by ID and retrieve all associated incident reports. The query uses "
    "an index on `related_ids.driver_id` for efficient lookups."
)
add_body(
    "Second, the Monthly Liability Report identifies the top 20 drivers causing the most "
    "financial damage. Originally implemented as a 7-stage aggregation pipeline in Python, "
    "this report was migrated to a MongoDB View (`vw_monthly_liability`) for improved "
    "performance and code simplicity. The view performs $group, $lookup, $unwind, and "
    "$project stages natively within the database, returning pre-computed results to the "
    "application layer."
)

add_screenshot_placeholder("Driver Incident tab showing Monthly Liability Report with top 20 worst offenders")

add_body("Tab B: Shipment & Customer Lookup", bold=True)
add_body(
    "This tab provides two search capabilities. The Shipment ID search retrieves the complete "
    "shipment profile — including embedded items, customs clearance details, and status "
    "history — displayed in a clean, structured layout. The Customer ID search lists all "
    "shipments associated with a given customer, limited to 50 results for performance."
)
add_body(
    "Both searches implement NoSQL injection prevention through the `sanitize_input()` "
    "utility function, which type-casts all user inputs to strings before passing them to "
    "PyMongo queries."
)

add_screenshot_placeholder("Shipment Lookup tab showing detailed shipment profile with items and status history")

add_body("Tab C: Top 10 High-Value Shipments", bold=True)
add_body(
    "This tab displays the 10 shipments with the highest declared values, sorted in descending "
    "order. Each entry shows the shipment ID, customer ID, declaration value (formatted in "
    "PKR), and customs clearance status. This query leverages the compound multikey index "
    "`idx_dispatch_priority` on `shipment_ops` for efficient sorting."
)

add_screenshot_placeholder("Top 10 High-Value Shipments tab")

add_body("Tab D: Vehicle Maintenance History", bold=True)
add_body(
    "This tab allows coordinators to search for any vehicle by ID and retrieve its complete "
    "maintenance history from the `maintenance_history` collection. Each record shows the "
    "service type, repair details, parts replaced, and associated costs."
)

add_screenshot_placeholder("Vehicle Maintenance History tab")

doc.add_heading('3.3 Command & Control — Dispatch Terminal', level=2)
add_body(
    "The Dispatch Terminal is the operational heart of the Nexus Logistics Command Center. "
    "It provides a no-code interface for dispatch coordinators to create new shipment records "
    "through an interactive form."
)

add_body("Key features of the Dispatch Terminal:", bold=True)
add_bullet(
    "Referential Integrity via Dropdowns: All entity selections (Customer, Driver, Vehicle, "
    "Route, Vendor) are populated from live database queries, ensuring that only valid, "
    "existing references can be selected. This prevents orphaned records and maintains "
    "data consistency."
)
add_bullet(
    "Automated Shipment ID Generation: The form auto-generates a unique shipment ID "
    "using a timestamp-based format (NEX-SHIP-{timestamp}), which can be overridden if "
    "needed."
)
add_bullet(
    "Nested JSON Injection: When the form is submitted, the application constructs a "
    "complete shipment document with embedded `customs_clearance`, `items` array, and "
    "`status_history` array, then inserts it into the `shipment_ops` collection via "
    "`insert_one()`."
)
add_bullet(
    "Real-Time Feedback: Upon successful dispatch, the system displays a confirmation "
    "message with shipment details and a celebratory animation."
)

add_screenshot_placeholder("Dispatch Terminal form showing all input fields and Deploy Shipment button")

doc.add_page_break()

# ============================================================
# SECTION 4: ADVANCED DATABASE IMPLEMENTATIONS
# ============================================================
doc.add_heading('4. Advanced Database Implementations (Post-Midterm Labs)', level=1)

doc.add_heading('4.1 Optimistic Concurrency Control (OCC)', level=2)
add_body(
    "Optimistic Concurrency Control (OCC) is a concurrency control mechanism that allows "
    "multiple transactions to proceed without locking resources, detecting conflicts only at "
    "commit time. Unlike pessimistic locking (which prevents conflicts by acquiring locks "
    "upfront), OCC assumes that concurrent modifications are rare and optimizes for the "
    "common case of no conflicts."
)

add_body("How OCC Prevents Lost Updates", bold=True)
add_body(
    "In a logistics environment, multiple dispatch coordinators may simultaneously view and "
    "attempt to update the same shipment document. Without concurrency control, the last "
    "writer wins — overwriting any changes made by other coordinators. This 'lost update' "
    "problem can result in critical operational data being silently discarded."
)

add_body("Implementation Details", bold=True)
add_body(
    "The OCC simulation was implemented as a dedicated tab (Tab E) in the Streamlit "
    "application. The simulation uses a dedicated `occ_demo` collection with a document "
    "structure that includes a version field (`__v`):"
)

add_body("The implementation follows a three-phase Read-Verify-Write cycle:", bold=True)
add_bullet(
    "Read Phase: Each dispatcher clicks 'Read Document' to capture the current database "
    "version. This version is stored in Streamlit's session state, simulating the dispatcher's "
    "local copy of the document."
)
add_bullet(
    "Verify Phase: When a dispatcher clicks 'Update Status', the application first checks "
    "whether the stored version matches the current database version. If another dispatcher "
    "updated the document in the meantime, the versions will differ, and the conflict is "
    "detected."
)
add_bullet(
    "Write Phase: Only if the versions match does the actual MongoDB update proceed. The "
    "update uses a version-matching filter (`{__v: current_version}`) and increments the "
    "version counter (`$inc: {__v: 1}`)."
)

add_body("Technical Implementation:", bold=True)
add_body(
    "The PyMongo update query requires the version to match: "
    "`db.occ_demo.update_one({'_id': 'TEST-123', '__v': current_version}, {"
    "'$set': {'status': new_status}, '$inc': {'__v': 1}})`. If `modified_count == 0`, "
    "the update failed because the version didn't match, indicating a concurrent modification."
)

add_screenshot_placeholder("OCC Simulation tab showing Dispatcher A and Dispatcher B columns with a conflict error message")

doc.add_heading('4.2 Database Views', level=2)
add_body(
    "MongoDB Views provide a powerful mechanism for encapsulating complex aggregation "
    "pipelines as named, queryable entities. By moving aggregation logic from the application "
    "layer into the database layer, Views simplify application code, improve maintainability, "
    "and ensure consistent query results."
)

add_body("The vw_monthly_liability View", bold=True)
add_body(
    "The 'Monthly Liability Report' was originally implemented as a 7-stage aggregation "
    "pipeline in Python (Streamlit), consisting of $match, $group, $lookup, $unwind, "
    "$project, $sort, and $limit stages. This pipeline was migrated to a MongoDB View "
    "named `vw_monthly_liability`."
)

add_body("The view pipeline performs the following operations:", bold=True)
add_bullet(
    "Stage 1 — Month Extraction: Extracts the year-month portion from each incident's "
    "timestamp using `$substr`."
)
add_bullet(
    "Stage 2 — Aggregation: Groups incidents by driver ID, summing total damage costs, "
    "counting incidents, collecting incident IDs, and calculating average damage."
)
add_bullet(
    "Stage 3 — Driver Lookup: Performs a `$lookup` against the `driver_performance` "
    "collection to retrieve driver names and safety scores."
)
add_bullet(
    "Stage 4 — Projection: Formats the final output with clean field names (DriverID, "
    "DriverName, SafetyScore, TotalDamagePKR, etc.)."
)

add_body(
    "After the view creation, the Streamlit application code was simplified from a 40+ line "
    "aggregation pipeline to a single line: `liability_data = list(db.vw_monthly_liability.find({}))`."
)

add_screenshot_placeholder("MongoDB View query result showing vw_monthly_liability output")

doc.add_heading('4.3 Security & NoSQL Injection Prevention', level=2)

add_body("4.3.1 Application-Layer Input Sanitization", bold=True)
add_body(
    "NoSQL injection is a security vulnerability where attackers inject MongoDB query operators "
    "(such as `$ne`, `$gt`, `$regex`) into user input fields to manipulate query behavior. "
    "For example, entering `{\"$ne\": null}` as a search term could bypass authentication "
    "or extract unauthorized data."
)

add_body(
    "The practical implementation of NoSQL injection prevention in Nexus Logistics uses a "
    "`sanitize_input()` utility function that type-casts all user inputs to strings before "
    "passing them to PyMongo queries:"
)

add_body(
    "When a user enters `{\"$ne\": null}` as text input, `str()` converts it to the literal "
    "string `'{$ne: null}'` — which is NOT interpreted as a MongoDB query operator. The "
    "database treats it as plain text data, searching for documents where the field literally "
    "contains that string."
)

add_body("Sanitization is applied to all user-facing search inputs:", bold=True)
add_bullet("Driver ID search (Tab A)")
add_bullet("Shipment ID search (Tab B)")
add_bullet("Customer ID search (Tab B)")
add_bullet("Vehicle ID search (Tab D)")

add_body("4.3.2 Database-Level Schema Validation", bold=True)
add_body(
    "In addition to application-layer sanitization, MongoDB's `$jsonSchema` validation provides "
    "a database-level enforcement mechanism that rejects documents violating the defined schema."
)

add_body(
    "The `shipment_ops` collection was configured with the following validation rules using "
    "the `collMod` command:"
)

schema_headers = ["Field", "Type", "Validation Rule"]
schema_rows = [
    ["_id", "string", "Required — must be a string"],
    ["customer_id", "string", "Required — must be a string"],
    ["path_id", "string", "Required — must be a string"],
    ["assigned_driver", "string", "Must be a string"],
    ["assigned_vehicle", "string", "Must be a string"],
    ["created_at", "string", "Must be a string (timestamp)"],
    ["customs_clearance.status", "string", "Enum: Pending, Cleared, Rejected, Held"],
    ["customs_clearance.declaration_value", "integer", "Must be an integer"],
    ["items", "array", "Must be an array"],
    ["status_history", "array", "Must be an array"],
]
add_table(schema_headers, schema_rows)

add_body(
    "The validation was applied with `validationLevel: 'moderate'` (only new and updated "
    "documents are validated, not existing ones) and `validationAction: 'error'` (invalid "
    "documents are rejected)."
)

add_screenshot_placeholder("Schema validation error when attempting to insert a document with invalid data types")

doc.add_heading('4.4 Role-Based Access Control (RBAC)', level=2)
add_body(
    "The Nexus Logistics platform uses a Docker-based MongoDB deployment with authentication "
    "enabled. The local development environment uses root-level credentials for simplicity:"
)

rbac_headers = ["Parameter", "Value"]
rbac_rows = [
    ["Username", "admin"],
    ["Password", "password (as defined in docker-compose.yaml)"],
    ["Authentication Database", "admin"],
    ["Connection String", "mongodb://admin:password@localhost:27017/"],
    ["Role", "root (full administrative access)"],
]
add_table(rbac_headers, rbac_rows)

add_body(
    "While this approach is acceptable for local development and lab evaluation, a production "
    "deployment would require scoped, least-privilege users:"
)

prod_rbac_headers = ["Role", "Database", "Privileges", "Use Case"]
prod_rbac_rows = [
    ["nexus_dashboard", "NexusLogisticsDB", "read (find, aggregate)", "Read-only dashboard clients"],
    ["nexus_app", "NexusLogisticsDB", "readWrite", "Dispatch terminal, CRUD operations"],
    ["nexus_admin", "NexusLogisticsDB", "dbOwner", "Administrative operations"],
    ["nexus_monitor", "admin", "dbStats, serverStatus", "Monitoring and alerting systems"],
]
add_table(prod_rbac_headers, prod_rbac_rows)

add_body(
    "Additional security recommendations include TLS/SSL encryption for all connections, "
    "network isolation via Docker networks or VPCs, automated password rotation, MongoDB "
    "audit logging, and IP whitelisting."
)

doc.add_heading('4.5 Scaling Strategy — Sharding', level=2)
add_body(
    "Sharding is MongoDB's horizontal scaling strategy, distributing data across multiple "
    "machines to handle growth in data volume and throughput. For Nexus Logistics, which "
    "scales from 350,000 to potentially millions of documents, strategic shard key selection "
    "is critical for maintaining sub-millisecond query performance."
)

add_body("An ideal shard key must satisfy three conditions:", bold=True)
add_bullet("High Cardinality: Enough unique values to distribute data evenly")
add_bullet("Query Pattern Alignment: Queries should hit only one shard (or a predictable subset)")
add_bullet("Write Distribution: Writes should spread evenly to avoid hotspots")

add_body("Recommended Shard Keys by Collection:", bold=True)

sharding_headers = ["Collection", "Shard Key", "Type", "Reasoning"]
sharding_rows = [
    ["telemetry_stream", "{ vehicle_id: 'hashed' }", "Hashed", "Evenly distributes high-velocity IoT writes; prevents write hotspots"],
    ["shipment_ops", "{ created_at: 1, _id: 1 }", "Ranged", "Natural time-based partitioning; efficient range queries"],
    ["driver_performance", "{ _id: 1 }", "Ranged", "Low write volume; queries by driver ID"],
    ["fleet_assets", "{ _id: 1 }", "Ranged", "Static reference data"],
    ["warehouse_hubs", "{ province_id: 1 }", "Ranged", "Queries often filter by region"],
    ["incident_reports", "{ incident_details.timestamp: 1 }", "Ranged", "Time-based investigation queries"],
    ["audit_logs", "{ timestamp: 1 }", "Ranged", "Time-series audit trail"],
]
add_table(sharding_headers, sharding_rows)

add_body(
    "The hashed shard key on `telemetry_stream` is particularly important because this "
    "collection experiences the highest write throughput — each vehicle generates thousands "
    "of telemetry pings per day. A hashed key ensures writes are uniformly distributed across "
    "all shards, preventing any single shard from becoming a bottleneck."
)

add_body(
    "The ranged shard key on `shipment_ops` leverages the `created_at` field, which naturally "
    "partitions data chronologically. Recent shipments reside on newer shards, while older "
    "shipments can be archived to cheaper storage. The compound key `{ created_at: 1, _id: 1 }` "
    "breaks ties when multiple shipments share the same timestamp."
)

doc.add_heading('4.6 Cloud Database Comparative Analysis', level=2)
add_body(
    "This section presents a formal comparison of MongoDB against three major cloud-native "
    "document databases: AWS DynamoDB, Google Firestore, and Azure Cosmos DB. The "
    "evaluation focuses on the specific requirements of the Nexus Logistics platform."
)

cloud_headers = ["Feature", "MongoDB (Selected)", "AWS DynamoDB", "Google Firestore", "Azure Cosmos DB"]
cloud_rows = [
    ["Data Model", "Document (BSON)", "Key-Value/Document", "Document", "Multi-model"],
    ["Aggregation", "Full pipeline (40+ stages)", "Limited (Query + Scan)", "Limited", "Basic"],
    ["Nested Arrays", "Native, queryable", "Limited", "Native", "Native"],
    ["$lookup (JOINs)", "Supported", "Not supported", "Not supported", "Partial"],
    ["Multikey Index", "Full support", "Not supported", "Not supported", "Partial"],
    ["Scalability", "Horizontal (sharding)", "Automatic", "Automatic", "Automatic"],
    ["ACID Transactions", "Multi-document", "Single-document", "Single-document", "Multi-document"],
    ["Free Tier", "Self-hosted (free)", "25 GB + 1M ops", "5 GB + 50K reads", "25 GB + 400 RU"],
]
add_table(cloud_headers, cloud_rows)

add_body("Use Case Analysis:", bold=True)

add_body("Requirement 1: Deeply Nested Logistical Arrays", bold=True)
add_body(
    "The `shipment_ops` document embeds arrays of `items`, `status_history`, and nested "
    "`customs_clearance` objects. MongoDB provides native support for querying within "
    "nested arrays using `$elemMatch`, positional operators, and multikey indexes — a "
    "capability no cloud alternative matches natively."
)

add_body("Requirement 2: Heavy Aggregation Pipelines", bold=True)
add_body(
    "The 'Monthly Liability Report' requires `$group`, `$lookup`, `$match`, `$project`, "
    "and `$sort` stages. MongoDB's 40+ stage aggregation pipeline enables this "
    "complexity within the database engine. Cloud alternatives require pulling data into "
    "the application layer for equivalent processing."
)

add_body("Requirement 3: Real-Time Query Performance", bold=True)
add_body(
    "MongoDB's compound multikey index on `shipment_ops` reduced document examination "
    "from 953 to 30 (96.9% reduction), transforming query complexity from O(n) to O(log n). "
    "While DynamoDB offers slightly faster single-digit millisecond responses for simple "
    "key lookups, MongoDB provides the best balance of speed and query flexibility."
)

add_body("Conclusion: Why MongoDB for Nexus Logistics", bold=True)
add_body(
    "MongoDB was the correct technology choice for Nexus Logistics for three decisive reasons:"
)
add_bullet(
    "Multikey Index Performance: The compound multikey index is a capability no cloud "
    "alternative supports natively on nested arrays."
)
add_bullet(
    "Aggregation Pipeline Depth: The 40+ stage pipeline enables complex analytical queries "
    "within the database engine, eliminating the need for application-layer processing."
)
add_bullet(
    "Document Model Alignment: The deeply nested shipment model maps naturally to "
    "MongoDB's BSON format, while cloud alternatives either lack nested array query "
    "capability or limit array operations."
)

doc.add_page_break()

# ============================================================
# SECTION 5: CONCLUSION
# ============================================================
doc.add_heading('5. Conclusion', level=1)
add_body(
    "The Nexus Logistics Command Center demonstrates the successful application of modern "
    "NoSQL database architecture to a real-world, high-stakes operational context. The project "
    "evolved from a foundational 34-entity relational model through principled NoSQL "
    "denormalization into 12 optimized MongoDB collections, achieving sub-millisecond query "
    "performance through strategic compound multikey indexing."
)
add_body(
    "The integration of Streamlit as a frontend framework transformed the database from a "
    "command-line tool into an interactive operational platform, providing dispatch coordinators "
    "with real-time visibility into shipment status, driver performance, fleet health, and "
    "financial metrics."
)
add_body(
    "The post-midterm lab implementations — Optimistic Concurrency Control, MongoDB Views, "
    "NoSQL injection prevention, schema validation, RBAC evaluation, and sharding strategy — "
    "demonstrate comprehensive mastery of advanced database concepts and their practical "
    "application to production-grade systems."
)
add_body(
    "The comparative analysis against cloud alternatives (AWS DynamoDB, Google Firestore, "
    "Azure Cosmos DB) confirms that MongoDB's document model, aggregation pipeline, and "
    "multikey indexing capabilities make it the optimal choice for Nexus Logistics' specific "
    "requirements of deeply nested data structures and complex analytical queries."
)
add_body(
    "As the platform scales toward enterprise-level data volumes, the theoretical sharding "
    "strategy provides a clear roadmap for horizontal scaling, ensuring that the system can "
    "maintain its performance characteristics as the database grows from 350,000 to millions "
    "of documents."
)

doc.add_page_break()

# ============================================================
# SECTION 6: REFERENCES
# ============================================================
doc.add_heading('6. References', level=1)

references = [
    "MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Indexing Strategies. https://www.mongodb.com/docs/manual/indexes/",
    "MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Aggregation Pipeline. https://www.mongodb.com/docs/manual/aggregation/",
    "MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Data Modeling Introduction. https://www.mongodb.com/docs/manual/core/data-modeling-introduction/",
    "Banker, K., Bakkum, P., Hawkins, S., Membrey, P., & Thielman, T. (2016). MongoDB in Action (2nd ed.). Manning Publications.",
    "COMSATS University Islamabad (2024). Advanced Database Systems — Lab Manual. Department of Computer Science.",
    "Chodorow, K. (2013). MongoDB: The Definitive Guide (2nd ed.). O'Reilly Media.",
    "Python Software Foundation (2024). Faker Library Documentation. https://faker.readthedocs.io/",
    "Docker, Inc. (2024). Docker Documentation — Volumes and Bind Mounts. https://docs.docker.com/storage/",
]

for i, ref in enumerate(references, 1):
    p = doc.add_paragraph(f"[{i}] {ref}")
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(-1.27)

# ============================================================
# SAVE DOCUMENT
# ============================================================
output_path = "docs/Nexus_Logistics_Final_Report.docx"
doc.save(output_path)
print(f"Report generated successfully: {output_path}")
