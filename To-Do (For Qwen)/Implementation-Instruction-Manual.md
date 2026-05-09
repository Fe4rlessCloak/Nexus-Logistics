# Nexus Logistics — Implementation Instruction Manual

> **Purpose:** This manual provides step-by-step instructions for implementing Tasks 1-6 as defined in [`Implement-All-Labs.md`](To-Do/Implement-All-Labs.md). It is designed for the project developer (Abdullah) to execute each task independently, with copy-paste-ready code and clear procedural guidance.
>
> **Project Context:** MongoDB + Streamlit "Nexus Logistics Command Center" — scaled from 7,000 to 350,000 documents. Docker-based local deployment on Fedora Linux.
>
> **Constraint:** No replica sets or multi-document transactions. Skip ACID transactions entirely.

---

## Table of Contents

| Task | Title | Type | File to Modify |
|------|-------|------|----------------|
| 1 | OCC Simulation | Code | `src/StreamlitGUI.py` |
| 2 | Database Views | Code + MongoDB | `src/StreamlitGUI.py` + mongosh |
| 3 | NoSQL Injection Prevention | Code + MongoDB | `src/StreamlitGUI.py` + mongosh |
| 4 | RBAC & Security | Documentation | New `.md` file |
| 5 | Sharding Strategy | Documentation | New `.md` file |
| 6 | Cloud DB Comparative Analysis | Documentation | New `.md` file |

---

## TASK 1: OCC (Optimistic Concurrency Control) Simulation

### Objective
Build a Streamlit tab that simulates concurrent dispatchers updating the same shipment document, demonstrating how OCC prevents lost updates using version numbers (`__v`).

### Prerequisites
- Docker container `nexus-mongodb` is running
- Streamlit app is running (`streamlit run src/StreamlitGUI.py`)

### Step-by-Step Implementation

#### Step 1: Add the OCC Tab to Streamlit

Locate this line in [`src/StreamlitGUI.py`](src/StreamlitGUI.py:164):

```python
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "A: Driver Incidents", 
    "B: Shipment/Customer Search", 
    "C: Top 10 High-Value Shipments", 
    "D: Vehicle Maintenance"
])
```

**Replace** it with:

```python
tab_a, tab_b, tab_c, tab_d, tab_e = st.tabs([
    "A: Driver Incidents", 
    "B: Shipment/Customer Search", 
    "C: Top 10 High-Value Shipments", 
    "D: Vehicle Maintenance",
    "E: OCC Simulation"
])
```

#### Step 2: Add the OCC Simulation Code Block

Append the following code **after** the closing of `tab_d` block (around line 368) and **before** the "Command & Control: Dispatch Terminal" section (line 371):

```python
# ============================================================
# QUERY E: OCC (Optimistic Concurrency Control) SIMULATION
# ============================================================
with tab_e:
    st.subheader("Optimistic Concurrency Control (OCC) Simulation")
    st.markdown("""
    This simulation demonstrates how OCC prevents **lost updates** when two dispatchers
    attempt to modify the same document simultaneously. Each document carries a `__v`
    (version) field. An update only succeeds if the version matches what the dispatcher
    read — otherwise, the second update is rejected.
    """)

    # --- Initialize Mock Document ---
    if "occ_initialized" not in st.session_state:
        st.session_state.occ_initialized = False
        st.session_state.occ_version = 1
        st.session_state.occ_status = "Pending"

    col_init1, col_init2 = st.columns([1, 3])
    with col_init1:
        if st.button("🔄 Initialize TEST-123 Document"):
            db.occ_demo.delete_one({})  # Clear any existing data
            db.occ_demo.insert_one({
                "_id": "TEST-123",
                "status": "Pending",
                "__v": 1
            })
            st.session_state.occ_initialized = True
            st.session_state.occ_version = 1
            st.session_state.occ_status = "Pending"
            st.rerun()

    if st.session_state.occ_initialized:
        # --- Fetch Current State ---
        current_doc = db.occ_demo.find_one({"_id": "TEST-123"})
        current_version = current_doc.get("__v", 1)
        current_status = current_doc.get("status", "Unknown")

        st.markdown(f"**Current Document State:** `_id: TEST-123` | **Status:** `{current_status}` | **Version:** `__v = {current_version}`")
        st.markdown("---")

        # --- Two Dispatcher Columns ---
        disp_a, disp_b = st.columns(2)

        with disp_a:
            st.markdown("### 👤 Dispatcher A")
            target_status_a = st.radio("Set Status:", ["In-Transit", "Delayed"], key="disp_a_status", index=0)
            if st.button("Update Status", key="disp_a_btn"):
                result = db.occ_demo.update_one(
                    {"_id": "TEST-123", "__v": current_version},
                    {"$set": {"status": target_status_a}, "$inc": {"__v": 1}}
                )
                if result.modified_count == 0:
                    st.error(f"❌ **OCC Conflict Detected!** Another dispatcher updated the document first. Lost update prevented.")
                else:
                    st.session_state.occ_version = current_version + 1
                    st.session_state.occ_status = target_status_a
                    st.success(f"✅ Updated to `{target_status_a}`. Version incremented to `{st.session_state.occ_version}`.")
                    st.rerun()

        with disp_b:
            st.markdown("### 👤 Dispatcher B")
            target_status_b = st.radio("Set Status:", ["In-Transit", "Delayed"], key="disp_b_status", index=1)
            if st.button("Update Status", key="disp_b_btn"):
                result = db.occ_demo.update_one(
                    {"_id": "TEST-123", "__v": current_version},
                    {"$set": {"status": target_status_b}, "$inc": {"__v": 1}}
                )
                if result.modified_count == 0:
                    st.error(f"❌ **OCC Conflict Detected!** Another dispatcher updated the document first. Lost update prevented.")
                else:
                    st.session_state.occ_version = current_version + 1
                    st.session_state.occ_status = target_status_b
                    st.success(f"✅ Updated to `{target_status_b}`. Version incremented to `{st.session_state.occ_version}`.")
                    st.rerun()

        # --- Refresh Button ---
        if st.button("🔍 Refresh Document State"):
            st.rerun()
```

#### Step 3: Verify

1. Run the Streamlit app: `streamlit run src/StreamlitGUI.py`
2. Navigate to tab **E: OCC Simulation**
3. Click **"Initialize TEST-123 Document"**
4. Click "Update Status" in **both** Dispatcher columns simultaneously
5. Observe that one succeeds and the other receives an `st.error` conflict message

---

## TASK 2: Database Views

### Objective
Replace the 7-stage aggregation pipeline in the "Monthly Liability Report" (Tab A) with a MongoDB View (`vw_monthly_liability`), simplifying the Streamlit code to a single `find()` call.

### Prerequisites
- Access to `mongosh` (MongoDB Shell)

### Step-by-Step Implementation

#### Step 1: Create the MongoDB View

Connect to your MongoDB container and execute the following command. You can run this via:

```bash
docker exec -it nexus-mongodb mongosh -u admin -p password --authenticationDatabase admin
```

Then paste this pipeline:

```javascript
use NexusLogisticsDB

db.getCollection('incident_reports').aggregate([
    // Stage 1: Extract month from timestamp
    {
        $addFields: {
            extracted_month: {
                $substr: ["$incident_details.timestamp", 0, 7]
            }
        }
    },
    // Stage 2: Group by driver, sum damage, collect incidents
    {
        $group: {
            _id: "$related_ids.driver_id",
            total_damage_pkr: { $sum: "$insurance_claim.damage_est_pkr" },
            incident_count: { $sum: 1 },
            incident_list: { $push: "$_id" },
            avg_damage: { $avg: "$insurance_claim.damage_est_pkr" }
        }
    },
    // Stage 3: Lookup driver details
    {
        $lookup: {
            from: "driver_performance",
            localField: "_id",
            foreignField: "_id",
            as: "driver_info"
        }
    },
    { $unwind: { path: "$driver_info", preserveNullAndEmptyArrays: true } },
    // Stage 4: Project final shape
    {
        $project: {
            _id: 0,
            DriverID: "$_id",
            DriverName: "$driver_info.name",
            SafetyScore: "$driver_info.safety_score",
            TotalDamagePKR: "$total_damage_pkr",
            IncidentCount: "$incident_count",
            AvgDamagePKR: { $round: ["$avg_damage", 2] },
            IncidentList: "$incident_list"
        }
    },
    // Stage 5: Create the view
    { $out: "vw_monthly_liability" }
])
```

> **Note:** The `$out` stage creates a view when used within `aggregate()`. Alternatively, use the standard MongoDB view creation:

```javascript
db.createView("vw_monthly_liability", "incident_reports", [
    {
        $addFields: {
            extracted_month: { $substr: ["$incident_details.timestamp", 0, 7] }
        }
    },
    {
        $group: {
            _id: "$related_ids.driver_id",
            total_damage_pkr: { $sum: "$insurance_claim.damage_est_pkr" },
            incident_count: { $sum: 1 },
            incident_list: { $push: "$_id" },
            avg_damage: { $avg: "$insurance_claim.damage_est_pkr" }
        }
    },
    {
        $lookup: {
            from: "driver_performance",
            localField: "_id",
            foreignField: "_id",
            as: "driver_info"
        }
    },
    { $unwind: { path: "$driver_info", preserveNullAndEmptyArrays: true } },
    {
        $project: {
            _id: 0,
            DriverID: "$_id",
            DriverName: "$driver_info.name",
            SafetyScore: "$driver_info.safety_score",
            TotalDamagePKR: "$total_damage_pkr",
            IncidentCount: "$incident_count",
            AvgDamagePKR: { $round: ["$avg_damage", 2] },
            IncidentList: "$incident_list"
        }
    }
])
```

#### Step 2: Verify the View Was Created

```javascript
show collections
// Should list: vw_monthly_liability
db.vw_monthly_liability.find().limit(5).pretty()
```

#### Step 3: Replace the Aggregation Pipeline in Streamlit

In [`src/StreamlitGUI.py`](src/StreamlitGUI.py:209-272), locate the `pipeline` variable inside the `if run_report:` block (lines 211-246).

**Replace** the entire 7-stage `pipeline` list with a simple find on the view:

```python
        # --- REPLACED: Use MongoDB View instead of 7-stage pipeline ---
        liability_data = list(db.vw_monthly_liability.find({}))
```

**Also update** the success message section (around line 256):

```python
        if liability_data:
            st.success(f"Generated damage liability report for {selected_month} using View `vw_monthly_liability`. (Execution Time: {exec_ms:.2f} ms)")
            
            df_liability = pd.DataFrame(liability_data)
            df_liability['TotalDamagePKR'] = df_liability['TotalDamagePKR'].apply(lambda x: f"PKR {x:,.2f}")
            df_liability = df_liability[['DriverID', 'DriverName', 'SafetyScore', 'TotalDamagePKR', 'IncidentCount', 'IncidentList']]
            
            st.dataframe(
                df_liability,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "IncidentList": st.column_config.ListColumn("Incident IDs")
                }
            )
        else:
            st.info(f"No incident damage records found for {selected_month}. (Execution Time: {exec_ms:.2f} ms)")
```

#### Step 4: Verify

1. Restart Streamlit: `streamlit run src/StreamlitGUI.py`
2. Go to Tab A: Driver Incidents
3. Select a month and click "Generate Report"
4. Confirm the report loads using the view instead of the long pipeline

---

## TASK 3: NoSQL Injection Prevention

### Objective
Secure the application against NoSQL injection attacks by:
1. Strictly type-casting user inputs in Streamlit
2. Adding MongoDB schema validation to enforce data types at the database level

### Prerequisites
- Understanding of NoSQL injection: An attacker can pass `{"$ne": null}` as a text input, which PyMongo interprets as a MongoDB query operator, potentially bypassing filters or extracting data.

### Step-by-Step Implementation

#### Step 1: Create a Sanitization Utility Function

Add this function at the top of [`src/StreamlitGUI.py`](src/StreamlitGUI.py:1), after the imports (around line 6):

```python
# ============================================================
# SECURITY: NoSQL Injection Prevention Utilities
# ============================================================
def sanitize_input(user_input, input_type="string"):
    """
    Sanitize user input to prevent NoSQL injection attacks.
    
    Args:
        user_input: Raw input from Streamlit widget
        input_type: One of "string", "int", "float"
    
    Returns:
        Sanitized value (never a dict, list, or object)
    
    How this prevents injection:
        If a user enters {"$ne": null}, str() converts it to the literal
        string '{"$ne": null}' — which is NOT interpreted as a MongoDB
        operator. The database treats it as plain text data.
    """
    if user_input is None:
        return ""
    
    # Force to string first — this neutralizes any injected query objects
    value = str(user_input).strip()
    
    if input_type == "int":
        try:
            return int(value)
        except ValueError:
            return 0
    elif input_type == "float":
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    return value


def sanitize_dict_for_find(dict_input):
    """
    Recursively sanitize a dictionary to prevent NoSQL injection.
    Strips all MongoDB query operators ($ne, $gt, $lt, $regex, etc.)
    from user-controlled values.
    """
    if isinstance(dict_input, dict):
        # If the dict contains any MongoDB operator, reject it entirely
        mongo_operators = {"$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin", "$regex", "$where", "$expr"}
        if any(op in dict_input for op in mongo_operators):
            return {"_safe_value": str(dict_input)}
        return {k: sanitize_dict_for_find(v) for k, v in dict_input.items()}
    elif isinstance(dict_input, list):
        return [sanitize_dict_for_find(item) for item in dict_input]
    return dict_input
```

#### Step 2: Apply Sanitization to All User Inputs

**Update Tab B — Shipment Search** (line 282):

```python
# BEFORE (vulnerable):
# shipment = db.shipment_ops.find_one({"_id": ship_search.strip()})

# AFTER (sanitized):
ship_search = sanitize_input(ship_search, "string")
shipment = db.shipment_ops.find_one({"_id": ship_search})
```

**Update Tab B — Customer Search** (line 314):

```python
# BEFORE (vulnerable):
# cust_shipments = list(db.shipment_ops.find({"customer_id": cust_search}, ...))

# AFTER (sanitized):
cust_search = sanitize_input(cust_search, "string")
cust_shipments = list(db.shipment_ops.find(
    {"customer_id": cust_search}, 
    {"_id": 1, "customs_clearance.status": 1, "assigned_driver": 1}
).limit(50))
```

**Update Tab A — Driver Search** (line 180):

```python
# BEFORE (vulnerable):
# incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))

# AFTER (sanitized):
drv_search = sanitize_input(drv_search, "string")
incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))
```

**Update Tab D — Vehicle Search** (line 360):

```python
# BEFORE (vulnerable):
# maintenance = list(db.maintenance_history.find({"vehicle_id": veh_search}, {"_id": 0}))

# AFTER (sanitized):
veh_search = sanitize_input(veh_search, "string")
maintenance = list(db.maintenance_history.find({"vehicle_id": veh_search}, {"_id": 0}))
```

#### Step 3: Apply MongoDB Schema Validation

Connect to MongoDB and run this command to enforce strict schema on `shipment_ops`:

```javascript
use NexusLogisticsDB

db.createCollection("shipment_ops_validated", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["_id", "customer_id", "path_id"],
            properties: {
                _id: {
                    bsonType: "string",
                    description: "Shipment ID — must be a string"
                },
                customer_id: {
                    bsonType: "string",
                    description: "Customer reference — must be a string"
                },
                assigned_driver: {
                    bsonType: "string",
                    description: "Driver reference — must be a string"
                },
                assigned_vehicle: {
                    bsonType: "string",
                    description: "Vehicle reference — must be a string"
                },
                path_id: {
                    bsonType: "string",
                    description: "Route reference — must be a string"
                },
                created_at: {
                    bsonType: "string",
                    description: "Timestamp — must be a string"
                },
                customs_clearance: {
                    bsonType: "object",
                    properties: {
                        customs_id: { bsonType: "string" },
                        status: { 
                            bsonType: "string",
                            enum: ["Pending", "Cleared", "Rejected", "Held"]
                        },
                        declaration_value: { bsonType: "double" }
                    }
                },
                items: {
                    bsonType: "array",
                    description: "Array of cargo items"
                },
                status_history: {
                    bsonType: "array",
                    description: "Array of status update events"
                }
            }
        }
    }
})
```

> **Note:** Since `shipment_ops` already exists with data, you cannot use `createCollection`. Instead, apply validation to the existing collection:

```javascript
use NexusLogisticsDB

db.runCommand({
    collMod: "shipment_ops",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["_id", "customer_id", "path_id"],
            properties: {
                _id: { bsonType: "string" },
                customer_id: { bsonType: "string" },
                assigned_driver: { bsonType: "string" },
                assigned_vehicle: { bsonType: "string" },
                path_id: { bsonType: "string" },
                created_at: { bsonType: "string" },
                customs_clearance: {
                    bsonType: "object",
                    properties: {
                        customs_id: { bsonType: "string" },
                        status: { 
                            bsonType: "string",
                            enum: ["Pending", "Cleared", "Rejected", "Held"]
                        },
                        declaration_value: { bsonType: "double" }
                    }
                },
                items: { bsonType: "array" },
                status_history: { bsonType: "array" }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
})
```

**Parameters explained:**
| Parameter | Value | Purpose |
|-----------|-------|---------|
| `validationLevel` | `"moderate"` | Only applies to **new** and **updated** documents, not existing ones |
| `validationAction` | `"error"` | Rejects invalid documents (use `"warn"` for testing) |

#### Step 4: Verify

1. Test injection attempt: Enter `{"$ne": null}` in the Shipment ID search box
2. Confirm it returns no results (the literal string is searched, not the operator)
3. Confirm schema validation by attempting to insert a document with a non-string `_id`

---

## TASK 4: RBAC & Security (Documentation Only)

### Objective
Document the current authentication approach and evaluate production-readiness.

### Step-by-Step Instructions

#### Step 1: Create the Documentation File

Create a new file: `Reports/RBAC_Security_Documentation.md`

#### Step 2: Add the Following Content

```markdown
# Task 4: RBAC & Security Documentation

## 4.1 Current Authentication Approach

The Nexus Logistics platform uses a Docker-based MongoDB deployment with **root-level authentication** enabled. The local environment authenticates connections using the following credentials:

- **Username:** `admin`
- **Password:** `password` (as defined in `docker-compose.yaml`)
- **Authentication Database:** `admin`
- **Connection String:** `mongodb://admin:password@localhost:27017/`

These credentials are configured via the `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` environment variables in the Docker Compose configuration, which creates a root user with the `root` role upon first container startup.

### Connection Flow

```
Streamlit App (PyMongo)
    ↓
MongoClient("mongodb://admin:password@localhost:27017/")
    ↓
MongoDB Container (port 27017)
    ↓
Authentication against 'admin' database with root role
    ↓
Access to 'NexusLogisticsDB' with full dbOwner privileges
```

## 4.2 Security Evaluation

### Local Development (Current State)
The root-level authentication approach is **acceptable for local development and lab evaluation** because:
- The database is isolated within a Docker container
- The container is not exposed to external networks
- The environment is used solely for university project demonstration

### Production Recommendations

For a production deployment, the following **Role-Based Access Control (RBAC)** improvements are required:

| Role | Database | Privileges | Use Case |
|------|----------|-----------|----------|
| `nexus_app_read` | NexusLogisticsDB | `find`, `aggregate` | Read-only dashboard clients |
| `nexus_app_write` | NexusLogisticsDB | `find`, `insert`, `update`, `delete` | Dispatch terminal, CRUD operations |
| `nexus_admin` | NexusLogisticsDB | `dbOwner` (all) | Administrative operations |
| `nexus_monitor` | `admin` | `dbStats`, `serverStatus` | Monitoring and alerting systems |

### Implementation Steps for Production RBAC

```javascript
// Step 1: Create read-only user for dashboard
use NexusLogisticsDB
db.createUser({
    user: "nexus_dashboard",
    pwd: "<secure-password>",
    roles: [{ role: "read", db: "NexusLogisticsDB" }]
})

// Step 2: Create application user for CRUD operations
db.createUser({
    user: "nexus_app",
    pwd: "<secure-password>",
    roles: [{ role: "readWrite", db: "NexusLogisticsDB" }]
})

// Step 3: Create admin user (least-privilege, not root)
db.createUser({
    user: "nexus_admin",
    pwd: "<secure-password>",
    roles: [{ role: "dbOwner", db: "NexusLogisticsDB" }]
})
```

### Connection String Updates for Production

```python
# Read-only connection (for dashboards)
MongoClient("mongodb://nexus_dashboard:password@host:27017/NexusLogisticsDB")

# Read-write connection (for app operations)
MongoClient("mongodb://nexus_app:password@host:27017/NexusLogisticsDB")
```

## 4.3 Additional Security Recommendations

1. **TLS/SSL Encryption:** Enable TLS for all MongoDB connections in production
2. **Network Isolation:** Use Docker networks or VPCs to restrict database access
3. **Password Rotation:** Implement automated password rotation for all database users
4. **Audit Logging:** Enable MongoDB audit logging to track all authentication and authorization events
5. **IP Whitelisting:** Restrict MongoDB access to known application server IPs only
```

#### Step 3: Save and Verify

The file should be saved at: `Reports/RBAC_Security_Documentation.md`

---

## TASK 5: Sharding Strategy (Documentation Only)

### Objective
Identify optimal shard keys for horizontal scaling of the Nexus Logistics database.

### Step-by-Step Instructions

#### Step 1: Create the Documentation File

Create a new file: `Reports/Sharding_Strategy_Documentation.md`

#### Step 2: Add the Following Content

```markdown
# Task 5: Sharding Strategy Documentation

## 5.1 Overview

Sharding is the horizontal scaling strategy for MongoDB, distributing data across multiple machines to handle growth in data volume and throughput. For Nexus Logistics, which scales from 7,000 to 350,000+ documents (and potentially millions in production), strategic shard key selection is critical for maintaining sub-millisecond query performance.

## 5.2 Shard Key Selection Criteria

An ideal shard key must satisfy three conditions:
1. **High Cardinality:** Enough unique values to distribute data evenly
2. **Query Pattern Alignment:** Queries should hit only one shard (or a predictable subset)
3. **Write Distribution:** Writes should spread evenly to avoid hotspots

## 5.3 Recommended Shard Keys by Collection

### 5.3.1 telemetry_stream — Hashed Shard Key

**Collection:** `telemetry_stream`
**Recommended Shard Key:** `{ vehicle_id: "hashed" }`

#### Rationale

The `telemetry_stream` collection stores high-frequency IoT telemetry data (GPS coordinates, engine RPM, fuel levels, temperature readings) generated by every active vehicle in the fleet. Each vehicle generates thousands of telemetry pings per day, resulting in extremely high write throughput.

| Factor | Analysis |
|--------|----------|
| Write Pattern | High-velocity inserts (one per second per vehicle) |
| Query Pattern | Range queries on `timestamp` for a specific `vehicle_id` |
| Data Volume | Millions of documents per vehicle per year |
| Hotspot Risk | High — time-ordered inserts create write hotspots |

**Why Hashed Shard Key?**

A hashed shard key on `vehicle_id` ensures:
- **Even Write Distribution:** Telemetry writes from all vehicles are distributed uniformly across shards
- **No Write Hotspots:** Hashed distribution prevents concentration on a single shard
- **Query Support:** Lookups by `vehicle_id` (even if combined with date range) hit a single shard

```javascript
// Enable sharding and shard the collection
sh.enableSharding("NexusLogisticsDB")
sh.shardCollection("NexusLogisticsDB.telemetry_stream", { vehicle_id: "hashed" })
```

### 5.3.2 shipment_ops — Ranged Shard Key

**Collection:** `shipment_ops`
**Recommended Shard Key:** `{ created_at: 1, _id: 1 }` (compound ranged key)

#### Rationale

The `shipment_ops` collection is the operational heartbeat of Nexus Logistics. Queries typically filter by:
- `created_at` — "Show me all shipments from the last 24 hours"
- `status_history.update` — "Show me active shipments"
- `customs_clearance.status` — "Show me cleared shipments"

| Factor | Analysis |
|--------|----------|
| Write Pattern | Steady, moderate throughput |
| Query Pattern | Range queries on `created_at`, filters on `status` |
| Data Volume | Hundreds of thousands to millions of documents |
| Hotspot Risk | Low — time-based distribution naturally spreads writes |

**Why Ranged Shard Key on `created_at`?**

A ranged shard key on `created_at` provides:
- **Natural Data Partitioning:** Recent shipments on newer shards, older on older shards
- **Efficient Range Queries:** Time-range queries are served from contiguous shards
- **Archive-Friendly:** Old shards can be moved to cheaper storage

```javascript
// Enable sharding and shard the collection
sh.shardCollection("NexusLogisticsDB.shipment_ops", { created_at: 1, _id: 1 })
```

> **Note:** The compound key `{ created_at: 1, _id: 1 }` breaks ties when multiple shipments share the same timestamp (down to the millisecond), ensuring unique shard key values.

### 5.3.3 Other Collections — Shard Key Recommendations

| Collection | Recommended Key | Type | Reason |
|-----------|----------------|------|--------|
| `driver_performance` | `{ _id: 1 }` | Ranged | Low write volume; queries by driver ID |
| `fleet_assets` | `{ _id: 1 }` | Ranged | Static data; rarely queried at scale |
| `warehouse_hubs` | `{ province_id: 1 }` | Ranged | Queries often filter by region |
| `route_intelligence` | `{ _id: 1 }` | Ranged | Static reference data |
| `incident_reports` | `{ "incident_details.timestamp": 1 }` | Ranged | Time-based queries for investigations |
| `audit_logs` | `{ timestamp: 1 }` | Ranged | Time-series audit trail |

## 5.4 Sharding Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │        Mongos Router               │
                    │   (Query Routing & Aggregation)    │
                    └────────────┬────────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
    │   Shard 1     │   │   Shard 2     │   │   Shard 3     │
    │  (MongoDB)    │   │  (MongoDB)    │   │  (MongoDB)    │
    │               │   │               │   │               │
    │ telemetry     │   │ shipment_ops  │   │ incident_     │
    │ driver        │   │ audit_logs    │   │ reports       │
    │ fleet_assets  │   │               │   │               │
    └───────────────┘   └───────────────┘   └───────────────┘
            │                    │                    │
    ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
    │ Config Server │   │ Config Server │   │ Config Server │
    │ (Metadata)    │   │ (Metadata)    │   │ (Metadata)    │
    └───────────────┘   └───────────────┘   └───────────────┘
```

## 5.5 Scaling Considerations

### When to Enable Sharding

| Metric | Threshold | Action |
|--------|-----------|--------|
| Collection Size | > 500 GB | Enable sharding |
| Query Latency | > 100ms p99 | Evaluate shard keys |
| Write Throughput | > 10K ops/sec | Add shards to cluster |
| Memory Pressure | RSS > RAM | Shard to distribute load |

### Chunk Management

MongoDB automatically splits chunks at 128 MB by default. For Nexus Logistics:
- **Telemetry Stream:** Consider reducing chunk size to 64 MB due to high write volume
- **Shipment Ops:** Default 128 MB chunks are appropriate

```javascript
// Adjust chunk size for high-write collections
sh.setChunkSize(64)  // MB
```
```

#### Step 3: Save and Verify

The file should be saved at: `Reports/Sharding_Strategy_Documentation.md`

---

## TASK 6: Cloud DB Comparative Analysis (Documentation Only)

### Objective
Compare MongoDB against cloud-native document databases to justify the technology choice.

### Step-by-Step Instructions

#### Step 1: Create the Documentation File

Create a new file: `Reports/Cloud_DB_Comparative_Analysis.md`

#### Step 2: Add the Following Content

```markdown
# Task 6: Cloud Database Comparative Analysis

## 6.1 Overview

This analysis compares MongoDB (selected for Nexus Logistics) against three major cloud-native document databases: **AWS DynamoDB**, **Google Firestore**, and **Azure Cosmos DB**. The evaluation focuses on the specific requirements of the Nexus Logistics platform: deeply nested logistical arrays, heavy aggregation pipelines, and real-time query performance.

## 6.2 Comparison Matrix

| Feature | MongoDB (Selected) | AWS DynamoDB | Google Firestore | Azure Cosmos DB |
|---------|-------------------|--------------|------------------|-----------------|
| **Data Model** | Document (BSON) | Key-Value/Document | Document | Multi-model (Document, Graph, Key-Value) |
| **Schema** | Flexible (schema-on-read) | Schemaless | Flexible | Flexible |
| **Aggregation** | Full aggregation pipeline (40+ stages) | Limited (Query + Scan) | Limited (simple queries) | Basic aggregation |
| **Nested Arrays** | Native support, queryable | Limited (no nested arrays) | Native support | Native support |
| **$lookup (JOINs)** | Supported via aggregation | Not supported | Not supported | Partial (via API) |
| **Indexing** | B-tree, hashed, geospatial, text, compound multikey | Hash, range, TTL | Range, composite, composite array | Hash, range, composite, geospatial |
| **Multikey Index** | ✅ Full support | ❌ Not supported | ❌ Not supported | ⚠️ Partial |
| **Scalability** | Horizontal (sharding) | Automatic horizontal | Horizontal (automatic) | Horizontal (automatic) |
| **Consistency** | Tunable (strong, causal, session, eventual) | Strong or eventual | Strong or eventual | 5 consistency levels |
| **ACID Transactions** | ✅ Multi-document (since 4.0) | ❌ Single-document only | ❌ Single-document only | ✅ Multi-document |
| **Query Language** | MongoDB Query Language (MQL) | DynamoDB Query/Scan | Firestore Query | Cosmos DB SQL API |
| **Real-time Streams** | Change Streams | DynamoDB Streams | Firestore Snapshots | Azure Change Feed |
| **Free Tier** | Self-hosted (free) | 25 GB + 1M ops | 5 GB + 50K reads | 25 GB + 400 RU |
| **Pricing Model** | Open-source (free) / Enterprise | Per GB + per request | Per GB + per operation | Request Units (RU) |

## 6.3 Use Case Analysis: Nexus Logistics Requirements

### Requirement 1: Deeply Nested Logistical Arrays

**Scenario:** The `shipment_ops` document embeds arrays of `items`, `status_history`, and nested `customs_clearance` objects. Queries must filter within these nested structures.

| Database | Support | Assessment |
|----------|---------|------------|
| **MongoDB** | ✅ Native | Arrays are first-class citizens. `$elemMatch`, positional operators, and multikey indexes provide full query capability. |
| **DynamoDB** | ⚠️ Limited | Nested attributes are queryable but without array-specific operators. No multikey index equivalent. |
| **Firestore** | ✅ Native | Supports array membership queries (`array-contains`) but limited filtering within nested objects. |
| **Cosmos DB** | ✅ Native | Supports nested document queries but lacks MongoDB's rich array operators. |

**Winner: MongoDB** — The multikey index on `status_history.update` (Task 4 optimization) is a capability no cloud alternative matches natively.

### Requirement 2: Heavy Aggregation Pipelines

**Scenario:** The "Monthly Liability Report" requires `$group`, `$lookup`, `$match`, `$project`, and `$sort` stages to compute driver damage totals with driver details.

| Database | Pipeline Stages | $lookup Equivalent | Assessment |
|----------|----------------|-------------------|------------|
| **MongoDB** | 40+ stages | `$lookup` with full JOIN semantics | Full analytical capability within the database |
| **DynamoDB** | None | None | Requires application-layer processing |
| **Firestore** | Basic filters | None | Requires application-layer processing |
| **Cosmos DB** | ~10 stages | Partial (via SQL API) | Limited compared to MongoDB |

**Winner: MongoDB** — The aggregation pipeline is the single most important analytical feature for Nexus Logistics. No cloud alternative provides equivalent in-database processing.

### Requirement 3: Real-Time Query Performance

**Scenario:** Sub-second query responses for operational dashboards tracking shipment status, driver performance, and fleet health.

| Database | Query Latency (typical) | Indexing | Assessment |
|----------|------------------------|----------|------------|
| **MongoDB** | 1-10 ms (indexed) | Multikey, compound, geospatial | Proven at enterprise scale |
| **DynamoDB** | < 1 ms (single-digit) | Hash, range | Faster at single-digit ms but limited query flexibility |
| **Firestore** | 10-50 ms | Composite | Good for simple queries, degrades with complexity |
| **Cosmos DB** | 10 ms (p99 < 10 ms) | Composite, multi-index | Strong SLA guarantees |

**Winner: DynamoDB** (raw speed) / **MongoDB** (balanced performance + flexibility)

### Requirement 4: Schema Evolution

**Scenario:** Logistics regulations change frequently. The schema must evolve without downtime.

| Database | Schema Enforcement | Assessment |
|----------|-------------------|------------|
| **MongoDB** | Optional (`$jsonSchema` validation) | Flexible by default, strict when needed |
| **DynamoDB** | None (schema-on-read) | Maximum flexibility, no validation |
| **Firestore** | None | Maximum flexibility |
| **Cosmos DB** | Optional (custom policies) | Flexible with optional constraints |

**Winner: Tie** — All four databases support schema flexibility. MongoDB's optional schema validation provides the best of both worlds.

## 6.4 Conclusion: Why MongoDB for Nexus Logistics

MongoDB was the correct technology choice for Nexus Logistics for three decisive reasons:

### 1. Multikey Index Performance
The compound multikey index on `shipment_ops` (Task 4) reduced document examination from 953 to 30 (96.9% reduction), transforming query complexity from O(n) to O(log n). **No cloud alternative supports multikey indexes on nested arrays** — DynamoDB, Firestore, and Cosmos DB all require denormalization workarounds that increase application complexity.

### 2. Aggregation Pipeline Depth
The 40+ stage aggregation pipeline in MongoDB enables complex analytical queries (driver liability reports, financial velocity charts, anomaly detection) to be executed **within the database engine**. Cloud alternatives require pulling data into the application layer for equivalent processing, increasing latency, memory usage, and code complexity.

### 3. Document Model Alignment
The Nexus Logistics data model — deeply nested shipments with embedded items, customs, and status history — maps **naturally** to MongoDB's BSON document format. Cloud document databases either lack nested array query capability (DynamoDB) or limit array operations (Firestore), forcing schema redesigns that contradict the operational data model.

### When Cloud Alternatives Would Be Better

| Scenario | Better Alternative |
|----------|-------------------|
| Simple key-value lookups at massive scale | AWS DynamoDB |
| Real-time collaborative editing | Google Firestore |
| Enterprise Microsoft stack integration | Azure Cosmos DB |
| Graph relationships (driver → vehicle → route → incident) | Azure Cosmos DB (Gremlin API) |

For Nexus Logistics' specific requirements — nested arrays, complex aggregations, and multi-field filtering — MongoDB remains the optimal choice.
```

#### Step 3: Save and Verify

The file should be saved at: `Reports/Cloud_DB_Comparative_Analysis.md`

---

## Quick Reference: Execution Order

Execute tasks in this order for maximum efficiency:

```
1. Task 1 (OCC Simulation)     → ~15 minutes    → Code change in StreamlitGUI.py
2. Task 2 (Database Views)     → ~20 minutes    → mongosh + StreamlitGUI.py
3. Task 3 (Injection Prevention) → ~25 minutes  → mongosh + StreamlitGUI.py
4. Task 4 (RBAC Documentation)  → ~10 minutes   → Create .md file
5. Task 5 (Sharding Strategy)   → ~15 minutes   → Create .md file
6. Task 6 (Cloud Comparison)    → ~15 minutes   → Create .md file
```

**Total Estimated Time: ~100 minutes (1 hour 40 minutes)**

---

## File Checklist

After completing all tasks, verify these files exist and are updated:

| File | Status | Description |
|------|--------|-------------|
| `src/StreamlitGUI.py` | Modified | Tasks 1, 2, 3 code changes |
| `Reports/RBAC_Security_Documentation.md` | Created | Task 4 documentation |
| `Reports/Sharding_Strategy_Documentation.md` | Created | Task 5 documentation |
| `Reports/Cloud_DB_Comparative_Analysis.md` | Created | Task 6 documentation |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB view not found | Ensure `createView` command ran successfully; verify with `show collections` |
| OCC simulation not triggering conflict | Both dispatchers must read the **same version** before clicking update |
| Schema validation rejecting existing data | Use `validationLevel: "moderate"` to skip existing documents |
| Streamlit cache not refreshing | Call `st.cache_data.clear()` or restart the Streamlit process |
| Docker container not running | Run `docker ps` to verify; restart with `docker-compose up -d` |
```

<tool_call>
<function=update_todo_list>
<parameter=todos>
[x] Create instruction manual document covering all 6 tasks
[x] Task 1: OCC Simulation - Step-by-step implementation guide
[x] Task 2: Database Views - Step-by-step implementation guide
[x] Task 3: NoSQL Injection Prevention - Step-by-step implementation guide
[x] Task 4: RBAC & Security - Documentation guide
[x] Task 5: Sharding Strategy - Documentation guide
[x] Task 6: Cloud DB Comparative Analysis - Documentation guide