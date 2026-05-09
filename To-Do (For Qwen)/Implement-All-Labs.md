# System Instructions for Qwen 3.6 35B A3B
**Context:** We are finalizing a MongoDB + Streamlit dashboard called "Nexus Logistics Command Center" for a university Viva. 
**Constraint:** DO NOT implement Replica Sets or multi-document transactions. We are skipping ACID transactions entirely to avoid infrastructure hassle.
**Goal:** Provide the required Python/PyMongo code for tasks 1-3, and generate the final report markdown text for tasks 4-6. Keep the code as simple and copy-paste ready as possible.

---

## TASK 1: OCC Simulation (Code Implementation)
**Objective:** Build a simple Optimistic Concurrency Control (OCC) simulation in Streamlit to prove the concept without complex overhead.
**Instructions for Qwen:**
1. Provide the Python code to add a new Streamlit tab: `tab_e = st.tabs(["...","E: OCC Simulation"])[-1]`.
2. In this tab, create a dummy button to initialize a mock shipment document in a new collection called `occ_demo` with `{"_id": "TEST-123", "status": "Pending", "__v": 1}`.
3. Create two Streamlit columns side-by-side: "Dispatcher A" and "Dispatcher B".
4. Both columns should fetch the document and display its current status and `__v` (version).
5. Give both columns a button to "Update Status to [In-Transit / Delayed]". 
6. In the PyMongo `update_one` query, explicitly require the version to match: `{"_id": "TEST-123", "__v": current_version}`. 
7. If `modified_count == 0`, display an `st.error` saying OCC prevented a lost update. Otherwise, increment `$inc: {"__v": 1}` and show success.

## TASK 2: Database Views (Code Implementation)
**Objective:** Simplify the Streamlit app by moving a complex aggregation pipeline into a MongoDB View.
**Instructions for Qwen:**
1. Provide the PyMongo script (or mongosh command) to create a View named `vw_monthly_liability`. It should be based on the `incident_reports` collection and use a standard pipeline to group by driver, calculate total damage, and lookup driver details.
2. Provide the updated Streamlit code for the "Monthly Liability Report" section. It must replace the massive 7-stage aggregation list in `app.py` with a simple `db.vw_monthly_liability.find(...)`.

## TASK 3: NoSQL Injection Prevention (Code Implementation)
**Objective:** Secure the application against basic NoSQL injection attacks.
**Instructions for Qwen:**
1. Provide the Python code to strictly type-cast and sanitize user inputs from Streamlit text inputs (e.g., using `str(ship_search).strip()`) before passing them to `find_one()`. Explain briefly how this prevents object injection like `{"$ne": null}`.
2. Provide a MongoDB `$jsonSchema` validation command to apply to the `shipment_ops` collection. It should strictly enforce that `_id`, `customer_id`, and `path_id` are strings, rejecting any objects or malformed data at the database level.

## TASK 4: RBAC & Security (Documentation Only)
**Objective:** Document the current security approach. DO NOT WRITE ANY APP CODE FOR THIS.
**Instructions for Qwen:**
Write a 2-3 paragraph markdown section for the final report. 
- Explain that the local Docker setup uses standard authentication via `admin:password` connection strings.
- Evaluate this approach: State that while it works for a local lab (authenticating via the `dbOwner` role), a production environment would require creating scoped, least-privilege users (e.g., a `readWrite` user restricted only to the `NexusLogisticsDB`).

## TASK 5: Sharding Strategy (Documentation Only)
**Objective:** Identify Shard Keys for horizontal scaling. DO NOT IMPLEMENT SHARDING.
**Instructions for Qwen:**
Write a brief markdown section for the final report identifying the ideal shard keys for this architecture:
- `telemetry_stream`: Recommend a **Hashed Shard Key** on `vehicle_id` to evenly distribute high-velocity IoT write operations.
- `shipment_ops`: Recommend a **Ranged Shard Key** on `created_at` or `status` since queries typically look for recent or active shipments.

## TASK 6: Cloud DB Comparative Analysis (Documentation Only)
**Objective:** Compare MongoDB to Cloud alternatives.
**Instructions for Qwen:**
Generate a concise Markdown table comparing MongoDB against AWS DynamoDB, Google Firestore, and Azure Cosmos DB based on this project's needs. Focus the conclusion on why MongoDB was the right choice for handling deeply nested logistical arrays and heavy aggregation pipelines compared to the others.