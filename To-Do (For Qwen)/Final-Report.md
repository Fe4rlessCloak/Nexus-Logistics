 System Prompt & Instructions for Qwen 3.6 35B A3B
**Role:** Expert Technical Writer & Database Architect
**Task:** Generate a comprehensive, professionally formatted Final Lab Project Report for "Nexus Logistics Command Center." 
**Output Format:** You must use your code execution environment (if available) to generate and output a `.docx` file using the `python-docx` library, OR output pristine, Word-ready Markdown that strictly follows the formatting rules below. 

---

## 📋 1. Project Metadata (Title Page)
The document must begin with a formal title page containing:
* **Project:** Lab Terminal Project - Nexus Logistics Command Center
* **Subject:** Advanced Database Systems
* **Instructor:** Basit Raza
* **University:** COMSATS University Islamabad, Islamabad Campus
* **Team Members:**
  * Abdullah Faisal (FA24-BCS-006)
  * Hashaam Sargaana (FA24-BCS-047)
  * Anas Khalid (FA24-BCS-018)

---

## 📐 2. Formatting & Constraint Rules
* **Length:** The generated content should be comprehensive but concise enough to fit within a 45-page limit once exported to Word.
* **Visuals:** DO NOT use abstract ASCII diagrams. Use formal Markdown/Word tables for all comparisons and data representations.
* **Code:** Minimize raw code blocks. Only include small snippets if absolutely necessary to explain a concept (e.g., a query structure). Explain the *logic* over the *syntax*.
* **Placeholders:** I will add screenshots later. You MUST leave highly visible placeholders exactly where relevant, formatted like this: `[INSERT SCREENSHOT HERE: <Description of what the screenshot should show>]`.

---

## 📑 3. Document Outline & Content Directives

### Section 1: Project Recap & Data Scaling
* **1.1 Database Recap:** Write a brief, high-level summary of the 12 MongoDB collections based on your prior knowledge of the midterm report. Do not repeat the entire midterm report, just set the stage.
* **1.2 Data Scaling & Synthetic Generation:** Explain how the project scaled from an initial 7,000 documents to a massive dataset of ~350,000 documents. Detail the use of `Generator.py` and the Python `Faker` library to simulate enterprise-scale logistics data for stress-testing.

### Section 2: System Architecture
* **2.1 Frontend Framework:** Explain the architectural decision to use Streamlit for the GUI. Discuss its rapid prototyping capabilities, native Python integration with PyMongo, and ability to handle data-heavy interactive dashboards.

### Section 3: The Nexus Logistics Command Center (GUI)
*Break down the Streamlit interface. For each sub-section, explain its purpose, how it works, and leave a screenshot placeholder.*
* **3.1 Global Operations & Telemetry:** Explain the live KPI metrics and charts (e.g., Pipeline Health, Capital in Transit). `[INSERT SCREENSHOT HERE: Main Dashboard Charts]`
* **3.2 Investigative Queries & Analytics:** Detail the core searches we offer and *why* they matter to a logistics company. Highlight complex queries like the "Monthly Liability Report" which identifies the top drivers costing the company money in damages. `[INSERT SCREENSHOT HERE: Analytics/Query Tab]`
* **3.3 Command & Control (Dispatch System):** Explain how the CRUD operations work without requiring the user to write code. Describe the manual dispatch form, how it maintains referential integrity using dropdowns, and how it injects nested JSON into MongoDB. `[INSERT SCREENSHOT HERE: Dispatch Terminal Form]`

### Section 4: Advanced Database Implementations (Post-Midterm Labs)
*Integrate the knowledge from the previous .md files and code implementations into formal report sections.*
* **4.1 Optimistic Concurrency Control (OCC):** Explain what OCC is and how it prevents "Lost Updates." Detail our practical implementation in the Streamlit "Simulation Tab" using the `__v` version field. `[INSERT SCREENSHOT HERE: OCC Simulation Tab showing a conflict]`
* **4.2 Database Views:** Explain the transition from frontend Python aggregation to backend MongoDB Views. Detail how we wrapped the 7-stage "Monthly Liability Report" pipeline into the `vw_monthly_liability` view to simplify application code.
* **4.3 Security & NoSQL Injection Prevention:** * Explain the practical implementation of backend sanitization (casting inputs to strings/floats) to neutralize operator injections (e.g., `{"$ne": null}`). 
  * Explain the practical implementation of MongoDB `$jsonSchema` validation to enforce strict data types on the `shipment_ops` collection.
* **4.4 Role-Based Access Control (RBAC):** Detail the security architecture. Explain the current local setup using the `dbOwner` role (`admin:password`) and outline how it would scale to least-privilege `readWrite` roles in production.
* **4.5 Scaling Strategy (Sharding):** Present the theoretical sharding strategy for horizontal scaling. Use a clean table to identify the Shard Keys (e.g., Hashed key on `vehicle_id` for telemetry, Ranged key on `created_at` for shipments) and explain the reasoning.
* **4.6 Cloud Database Comparative Analysis:** Present a formal comparison of MongoDB vs. AWS DynamoDB, Google Firestore, and Azure Cosmos DB. Use a well-structured table. Conclude with a strong justification for why MongoDB's aggregation pipeline and document model were the superior choice for this specific logistics architecture.