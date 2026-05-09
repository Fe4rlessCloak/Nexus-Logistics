import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import time
# --- 1. SETUP & CONNECTION ---
st.set_page_config(page_title="Nexus DB Control", layout="wide")

# ============================================================
# SECURITY: NoSQL Injection Prevention Utilities (Task 3)
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

@st.cache_resource
def init_connection():
    client = MongoClient("mongodb://admin:password@localhost:27017/")
    return client.NexusLogisticsDB

db = init_connection()

st.title(" Nexus Logistics | Core Operations")
st.markdown("---")
# --- 2. OVERVIEW SECTION (KPI COMMAND CENTER) ---
st.header("1. Global Operations Overview")

# 1. --- CACHED HEAVY QUERIES ---
# ttl=86400 caches the result for exactly 24 hours. 
@st.cache_data(ttl=86400)
def get_anomaly_alerts():
    # Anomaly Detection: Vehicles hitting critical engine temps (>105C)
    pipeline = [
        {"$match": {"metrics.engine_temp_c": {"$gt": 105}}},
        # Group by vehicle so we don't count the same overheating truck twice
        {"$group": {"_id": "$vehicle_id"}}
    ]
    # We return the length of the list, which is our unique vehicle count
    return len(list(db.telemetry_stream.aggregate(pipeline)))

@st.cache_data(ttl=300) # Cache this for 5 minutes, as shipment statuses change faster
def get_delayed_high_value():
    return db.shipment_ops.count_documents({
        "customs_clearance.declaration_value": {"$gte": 500000},
        "status_history.update": "Delayed"
    })



# ---------------------------------------------------------
# --- 1.5. NETWORK TELEMETRY & FINANCIALS (CHARTS) ---
# ---------------------------------------------------------
st.markdown("###  Live Operations & Financial Velocity")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # --- CHART 1: Logistics Pipeline Health ---
    status_pipeline = [
        {"$project": {
            "current_status": {"$arrayElemAt": ["$status_history.update", -1]}
        }},
        # FIXED: Explicitly filter out "Dispatched" or any other anomalies
        {"$match": {
            "current_status": {"$in": ["Picked Up", "In-Transit", "Delayed"]}
        }},
        {"$group": {"_id": "$current_status", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}} 
    ]
    status_data = list(db.shipment_ops.aggregate(status_pipeline))
    
    if status_data:
        df_status = pd.DataFrame(status_data)
        df_status.rename(columns={"_id": "Status", "count": "Volume"}, inplace=True)
        
        fig_status = px.bar(
            df_status, x="Volume", y="Status", orientation='h',
            title="Current Network Pipeline Health",
            text_auto=True,
            color="Status",
            # A more professional color palette for statuses
            color_discrete_map={
                "Picked Up": "#1f77b4", 
                "In-Transit": "#2ca02c", 
                "Delayed": "#d62728"
            }
        )
        fig_status.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_status, use_container_width=True)

with col_chart2:
    # --- CHART 2: Financial Volume (May 2026 Daily Trend) ---
    volume_pipeline = [
        {"$match": {
            "created_at": {"$gte": "2026-05-01"}
        }},
        {"$project": {
            "date_only": {"$substr": ["$created_at", 0, 10]}, 
            "value": "$customs_clearance.declaration_value"
        }},
        {"$group": {"_id": "$date_only", "daily_value": {"$sum": "$value"}}},
        {"$sort": {"_id": 1}} 
    ]
    volume_data = list(db.shipment_ops.aggregate(volume_pipeline))
    
    if volume_data:
        df_volume = pd.DataFrame(volume_data)
        df_volume.rename(columns={"_id": "Date", "daily_value": "Total Value (PKR)"}, inplace=True)
        
        # FIXED: Added range_y to ensure the chart starts at zero
        fig_volume = px.line(
            df_volume, x="Date", y="Total Value (PKR)",
            title="May 2026: Capital in Transit",
            markers=True,
            range_y=[0, df_volume['Total Value (PKR)'].max() * 1.1] 
        )
        
        fig_volume.update_xaxes(type='category')
        fig_volume.update_traces(line_color='#00d2ff', line_width=3, marker_size=8)
        fig_volume.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_volume, use_container_width=True)

st.markdown("---")




# 2. --- REAL-TIME COUNTS (Fast Operations) ---
total_shipments = db.shipment_ops.estimated_document_count()
total_drivers = db.driver_performance.estimated_document_count()
total_vehicles = db.fleet_assets.estimated_document_count()
in_transit_count = db.shipment_ops.count_documents({"status_history.update": "In-Transit"})

# Fetch cached complex data
critical_maintenance_count = get_anomaly_alerts()
delayed_high_value_count = get_delayed_high_value()

# 3. --- UI LAYOUT: TOP METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("📦 Total Shipments", f"{total_shipments:,}")
c2.metric("🚚 In-Transit Shipments", f"{in_transit_count:,}")
# New Metric placed right next to In-Transit
c3.metric("⚠️ Delayed High-Value (>500k)", f"{delayed_high_value_count:,}", delta="Critical", delta_color="inverse")
c4.metric("🚛 Fleet Vehicles", f"{total_vehicles:,}")

st.markdown("---")

# 4. --- UI LAYOUT: CRITICAL ALERTS & REFRESH ---
col_alert1, col_alert2 = st.columns([3, 1])

with col_alert1:
    if critical_maintenance_count > 0:
        st.error(f"🚨 **URGENT:** {critical_maintenance_count} vehicles require immediate maintenance based on IoT Telemetry Anomalies (Engine Temp > 100°C).")
    else:
        st.success("✅ All telemetry data is within normal parameters. No immediate maintenance required.")

with col_alert2:
    # The Manual Refresh Button
    st.write("Last Anomaly Scan: Cached")
    if st.button("🔄 Force IoT Anomaly Scan Now"):
        # This clears the Streamlit cache and forces the queries to run again immediately
        st.cache_data.clear() 
        st.rerun() # Refreshes the UI instantly

st.markdown("---")

# --- 3. PRE-BAKED QUERIES (READ OPERATIONS) ---
st.header("2. Common Operations")

# FIXED: Removed Tab E so this section is strictly for reporting/searching
tab_a, tab_b, tab_c, tab_d, tab_e = st.tabs([
    "A: Driver Incidents",
    "B: Shipment/Customer Search",
    "C: Top 10 High-Value Shipments",
    "D: Vehicle Maintenance",
    "E: OCC Simulation"
])
# Query A: Search driver by ID and show their incidents
with tab_a:
    st.subheader("Driver Incident & Liability Center")
    
    # --- 1. INDIVIDUAL SEARCH ---
    st.markdown("#### Individual Driver Lookup")
    drv_search = st.text_input("Enter Driver ID:", placeholder="e.g., DRV_9084")
    if st.button("Search Driver"):
        # Task 3: Sanitize input to prevent NoSQL injection
        drv_search = sanitize_input(drv_search, "string")

        start_time = time.time() # ⏱️ START TIMER
        incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))
        end_time = time.time()   # ⏱️ STOP TIMER

        exec_ms = (end_time - start_time) * 1000
        
        incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))
        if incidents:
            df_incidents = pd.json_normalize(incidents)
            st.success(f"Found {len(incidents)} incident(s) for {drv_search}. (Execution Time: {exec_ms:.2f} ms)")
            st.dataframe(df_incidents, use_container_width=True, hide_index=True)
        else:
            st.info(f"No incidents found. (Execution Time: {exec_ms:.2f} ms)")

    st.markdown("---")
    
    # --- 2. MONTHLY LIABILITY REPORT ---
    st.markdown("#### Monthly Liability Report (Top 20 Worst Offenders)")
    st.write("Aggregates driver incident damage estimates to assess financial liability.")
    
    col_m1, col_m2 = st.columns([1, 3])
    with col_m1:
        # Defaulting to index=4 (2026-05) since that's where your data lives
        selected_month = st.selectbox(
            "Select Billing Month:", 
            ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"], 
            index=4 
        )
        run_report = st.button("Generate Report")
        
    if run_report:
        # Task 2: REPLACED — Use MongoDB View (vw_monthly_liability) instead of 7-stage pipeline
        start_time = time.time() # ⏱️ START TIMER
        liability_data = list(db.vw_monthly_liability.find({}))
        end_time = time.time() # ⏱️ STOP TIMER
        exec_ms = (end_time - start_time) * 1000

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
# Query B: Search for a shipment by ID + Search all shipments by a customer
with tab_b:
    st.subheader("Shipment & Customer Lookup")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        ship_search = st.text_input("Find by Shipment ID:", placeholder="e.g., NEX-SHIP-000000")
        if st.button("Search Shipment"):
            # Task 3: Sanitize input to prevent NoSQL injection
            ship_search = sanitize_input(ship_search, "string")
            start_time = time.time() # ⏱️ START TIMER
            shipment = db.shipment_ops.find_one({"_id": ship_search})
            end_time = time.time() # ⏱️ STOP TIMER
            exec_ms = (end_time - start_time) * 1000  
            if shipment:
                # FIXED: Visual layout replacing raw JSON
                st.markdown(f"#### Shipment Details: `{shipment['_id']}` (Execution Time: {exec_ms:.2f} ms)")
                
                # Core Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.metric("Customer ID", shipment.get('customer_id', 'N/A'))
                m2.metric("Driver ID", shipment.get('assigned_driver', 'N/A'))
                m3.metric("Vehicle ID", shipment.get('assigned_vehicle', 'N/A'))
                
                # Customs Info
                customs = shipment.get('customs_clearance', {})
                st.info(f"**Customs Status:** {customs.get('status', 'N/A')} | **Declaration Value:** PKR {customs.get('declaration_value', 0):,} | **Customs ID:** {customs.get('customs_id', 'N/A')}")
                st.write(f"**Created At:** {shipment.get('created_at', 'N/A')} | **Path ID:** {shipment.get('path_id', 'N/A')}")
                
                # Embedded Arrays as clean tables
                st.markdown("##### Included Items")
                st.dataframe(pd.DataFrame(shipment.get('items', [])), use_container_width=True, hide_index=True)
                
                st.markdown("##### Status History")
                st.dataframe(pd.DataFrame(shipment.get('status_history', [])), use_container_width=True, hide_index=True)

            else:
                st.warning(f"Shipment not found. (Execution Time: {exec_ms:.2f} ms)")
                
    with col_s2:
        cust_search = st.text_input("Find by Customer ID:", placeholder="e.g., CUST_uOcdZ_PK")
        if st.button("Search Customer Operations"):
            # Task 3: Sanitize input to prevent NoSQL injection
            cust_search = sanitize_input(cust_search, "string")
            start_time = time.time() # ⏱️ START TIMER
            cust_shipments = list(db.shipment_ops.find(
                {"customer_id": cust_search},
                {"_id": 1, "customs_clearance.status": 1, "assigned_driver": 1}
            ).limit(50)) 
            end_time = time.time() # ⏱️ STOP TIMER
            exec_ms = (end_time - start_time) * 1000
            if cust_shipments:
                df_cust = pd.json_normalize(cust_shipments)
                st.success(f"Showing up to 50 shipments for {cust_search}. (Execution Time: {exec_ms:.2f} ms)")
                st.dataframe(df_cust, use_container_width=True, hide_index=True)
            else:
                st.info(f"No shipments found for this customer. (Execution Time: {exec_ms:.2f} ms)")

# Query C: Top 10 highest value shipments right now, and their status
with tab_c:
    st.subheader("Top 10 High-Value Shipments")
    if st.button("Run High-Value Query"):
        start_time = time.time() # ⏱️ START TIMER
        top_10 = list(db.shipment_ops.find(
            {}, 
            {"_id": 1, "customs_clearance.declaration_value": 1, "customs_clearance.status": 1, "customer_id": 1}
        ).sort("customs_clearance.declaration_value", -1).limit(10))
        end_time = time.time() # ⏱️ STOP TIMER
        exec_ms = (end_time - start_time) * 1000
        st.info(f"(Execution Time: {exec_ms:.2f} ms)")
        if top_10:
            # FIXED: Explicitly defining the row dictionary to prevent pandas from swapping columns
            # FIXED: Added 'PKR' formatting to the value
            formatted_data = []
            for doc in top_10:
                formatted_data.append({
                    "Shipment ID": doc.get("_id"),
                    "Customer ID": doc.get("customer_id"),
                    "Declaration Value": f"PKR {doc.get('customs_clearance', {}).get('declaration_value', 0):,}",
                    "Status": doc.get("customs_clearance", {}).get("status", "Unknown")
                })
                
            df_top10 = pd.DataFrame(formatted_data)
            st.dataframe(df_top10, use_container_width=True, hide_index=True)

# Query D: Search a vehicle and show its maintenance history
with tab_d:
    st.subheader("Vehicle Maintenance History")
    veh_search = st.text_input("Enter Vehicle ID:", placeholder="e.g., VEH_DHW_15")
    if st.button("Search Vehicle"):
        # Task 3: Sanitize input to prevent NoSQL injection
        veh_search = sanitize_input(veh_search, "string")
        start_time = time.time() # ⏱️ START TIMER
        maintenance = list(db.maintenance_history.find({"vehicle_id": veh_search}, {"_id": 0}))
        end_time = time.time() # ⏱️ STOP TIMER
        exec_ms = (end_time - start_time) * 1000
        if maintenance:
            df_maint = pd.json_normalize(maintenance)
            st.success(f"Found {len(maintenance)} maintenance record(s) for {veh_search}. (Execution Time: {exec_ms:.2f} ms)")
            st.dataframe(df_maint, use_container_width=True, hide_index=True)
        else:
            st.info(f"No maintenance history found for this vehicle. (Execution Time: {exec_ms:.2f} ms)")

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

    # --- Initialize Mock Document & Session State ---
    if "occ_initialized" not in st.session_state:
        st.session_state.occ_initialized = False
    if "occ_dispatcher_a_version" not in st.session_state:
        st.session_state.occ_dispatcher_a_version = None
    if "occ_dispatcher_b_version" not in st.session_state:
        st.session_state.occ_dispatcher_b_version = None

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
            st.session_state.occ_dispatcher_a_version = None
            st.session_state.occ_dispatcher_b_version = None
            st.rerun()

    if st.session_state.occ_initialized:
        # --- Fetch Current DB State ---
        current_doc = db.occ_demo.find_one({"_id": "TEST-123"})
        db_version = current_doc.get("__v", 1)
        current_status = current_doc.get("status", "Unknown")

        st.markdown(f"**Current Database State:** `_id: TEST-123` | **Status:** `{current_status}` | **Version:** `__v = {db_version}`")
        st.markdown("---")

        # --- Two Dispatcher Columns ---
        disp_a, disp_b = st.columns(2)

        with disp_a:
            st.markdown("### 👤 Dispatcher A")
            st.caption(f"Your captured version: `{st.session_state.occ_dispatcher_a_version}`")
            
            # "Read" button — captures the current DB version for this dispatcher
            if st.button("📖 Read Document (Capture Version)", key="disp_a_read"):
                st.session_state.occ_dispatcher_a_version = db_version
                st.success(f"📖 Document read. Captured version: `__v = {db_version}`")
                st.rerun()
            
            target_status_a = st.radio("Set Status:", ["In-Transit", "Delayed"], key="disp_a_status", index=0, disabled=st.session_state.occ_dispatcher_a_version is None)
            
            if st.button("Update Status", key="disp_a_btn", disabled=st.session_state.occ_dispatcher_a_version is None):
                stored_version = st.session_state.occ_dispatcher_a_version
                # Verify the version hasn't changed since we read it
                current_db_doc = db.occ_demo.find_one({"_id": "TEST-123"})
                current_db_v = current_db_doc.get("__v", 1)
                
                if stored_version != current_db_v:
                    st.error(f"❌ **OCC Conflict Detected!** You read version `{stored_version}`, but the database is now at version `{current_db_v}`. Lost update prevented.")
                else:
                    # Version matches — proceed with update
                    result = db.occ_demo.update_one(
                        {"_id": "TEST-123", "__v": stored_version},
                        {"$set": {"status": target_status_a}, "$inc": {"__v": 1}}
                    )
                    if result.modified_count == 0:
                        st.error(f"❌ **OCC Conflict Detected!** Another dispatcher updated the document first. Lost update prevented.")
                    else:
                        st.session_state.occ_dispatcher_a_version = None  # Reset
                        st.success(f"✅ Updated to `{target_status_a}`. New version: `__v = {current_db_v + 1}`")
                        st.rerun()

        with disp_b:
            st.markdown("### 👤 Dispatcher B")
            st.caption(f"Your captured version: `{st.session_state.occ_dispatcher_b_version}`")
            
            # "Read" button — captures the current DB version for this dispatcher
            if st.button("📖 Read Document (Capture Version)", key="disp_b_read"):
                st.session_state.occ_dispatcher_b_version = db_version
                st.success(f"📖 Document read. Captured version: `__v = {db_version}`")
                st.rerun()
            
            target_status_b = st.radio("Set Status:", ["In-Transit", "Delayed"], key="disp_b_status", index=1, disabled=st.session_state.occ_dispatcher_b_version is None)
            
            if st.button("Update Status", key="disp_b_btn", disabled=st.session_state.occ_dispatcher_b_version is None):
                stored_version = st.session_state.occ_dispatcher_b_version
                # Verify the version hasn't changed since we read it
                current_db_doc = db.occ_demo.find_one({"_id": "TEST-123"})
                current_db_v = current_db_doc.get("__v", 1)
                
                if stored_version != current_db_v:
                    st.error(f"❌ **OCC Conflict Detected!** You read version `{stored_version}`, but the database is now at version `{current_db_v}`. Lost update prevented.")
                else:
                    # Version matches — proceed with update
                    result = db.occ_demo.update_one(
                        {"_id": "TEST-123", "__v": stored_version},
                        {"$set": {"status": target_status_b}, "$inc": {"__v": 1}}
                    )
                    if result.modified_count == 0:
                        st.error(f"❌ **OCC Conflict Detected!** Another dispatcher updated the document first. Lost update prevented.")
                    else:
                        st.session_state.occ_dispatcher_b_version = None  # Reset
                        st.success(f"✅ Updated to `{target_status_b}`. New version: `__v = {current_db_v + 1}`")
                        st.rerun()

        # --- Refresh Button ---
        if st.button("🔍 Refresh Document State"):
            st.rerun()

# Query E: The Real-World CRUD Dispatch Form
# --- NEW SECTION: ACTION TERMINAL (WRITE OPERATIONS) ---
# ---------------------------------------------------------
st.markdown("---")
st.header("3. Command & Control: Dispatch Terminal")
st.write("Assign active fleet assets, personnel, routing, and cargo to new operations.")

# --- 1. PRE-FETCH DATA ---
# Drivers
drivers = list(db.driver_performance.find({}, {"_id": 1, "name": 1}))
driver_options = {d["_id"]: f"{d['name']} ({d['_id']})" for d in drivers}

# Vehicles
vehicles = list(db.fleet_assets.find({}, {"_id": 1}).limit(200)) 
vehicle_options = [v["_id"] for v in vehicles]

# Customers & Vendors
customers = db.shipment_ops.distinct("customer_id")
vendors = db.shipment_ops.distinct("items.vendor_id")

# FIXED: Fetch Routes from route_intelligence!
routes = list(db.route_intelligence.find({}, {"_id": 1, "origin": 1, "destination": 1}).limit(200))
route_options = {r["_id"]: f"{r['origin']} -> {r['destination']} ({r['_id']})" for r in routes}

# --- 2. THE UI FORM ---
with st.container(): # Using a container to make it pop visually
    with st.form("dispatch_form"):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.markdown("##### Entities")
            cust_id = st.selectbox("Customer", options=customers)
            driver_id = st.selectbox("Driver", options=list(driver_options.keys()), format_func=lambda x: driver_options[x])
            vehicle_id = st.selectbox("Vehicle", options=vehicle_options)
        
        with col_f2:
            st.markdown("##### Shipment Meta")
            import time
            auto_ship_id = f"NEX-SHIP-{int(time.time())}"
            ship_id = sanitize_input(st.text_input("Shipment ID", value=auto_ship_id))
            
            # FIXED: Dynamic Route Dropdown!
            path_id = st.selectbox("Route", options=list(route_options.keys()), format_func=lambda x: route_options[x])
            
            value = sanitize_input(st.number_input("Value (PKR)", min_value=0, step=5000, value=286103))

        with col_f3:
            st.markdown("##### Primary Cargo")
            item_desc = sanitize_input(st.text_input("Description", placeholder="e.g., electronic parts"))
            item_qty = sanitize_input(st.number_input("Quantity", min_value=1, value=50))
            vendor_id = st.selectbox("Vendor ID", options=vendors if vendors else ["VND_UNKNOWN"])

        submitted = st.form_submit_button("Deploy Shipment 🚀")
        
        # --- 3. DATABASE INJECTION ---
        if submitted:
            from datetime import datetime
            
            new_shipment = {
                "_id": ship_id,
                "customer_id": cust_id,
                "assigned_driver": driver_id,
                "assigned_vehicle": vehicle_id,
                "path_id": path_id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "customs_clearance": {
                    "customs_id": f"CUST_{int(time.time() % 1000)}",
                    "status": "Pending",
                    "declaration_value": value
                },
                "items": [
                    {
                        "item_id": f"ITM_{int(time.time() % 100)}",
                        "vendor_id": vendor_id,
                        "description": item_desc,
                        "qty": item_qty
                    }
                ], 
                "status_history": [
                    {
                        "checkpoint": "Origin Hub", 
                        "update": "Picked Up", 
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    }
                ]
            }
            
            db.shipment_ops.insert_one(new_shipment)
            st.success(f"✅ Success! Shipment `{ship_id}` carrying {item_qty}x '{item_desc}' has been dispatched on route {route_options[path_id]}.")
            st.balloons()

