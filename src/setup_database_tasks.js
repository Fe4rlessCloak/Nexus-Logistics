// Switch to the project database
db = db.getSiblingDB("NexusLogisticsDB");

print("============================================================");
print("  Nexus Logistics — Post-Midterm Database Setup (FIXED)");
print("============================================================\n");

// --- TASK 1: Initialize OCC Demo Collection ---
print("[TASK 1] Initializing OCC Demo Collection...");
try {
    db.occ_demo.drop(); // Cleaner than deleteMany
    db.occ_demo.insertOne({
        _id: "TEST-123",
        status: "Pending",
        __v: NumberInt(1)
    });
    print("  ✓ occ_demo collection initialized with TEST-123 document.");
    // FIX: Changed tojson() to printjson()
    print("  ✓ Document:");
    printjson(db.occ_demo.findOne({ _id: "TEST-123" }));
} catch (e) {
    print("  ✗ Error initializing occ_demo: " + e.message);
}

// --- TASK 2: Create MongoDB View ---
print("\n[TASK 2] Creating MongoDB View: vw_monthly_liability...");
try {
    // FIX: Use db.collection.drop() instead of db.dropView()
    db.getCollection("vw_monthly_liability").drop();

    db.createView(
        "vw_monthly_liability",
        "incident_reports",
        [
            { $addFields: { extracted_month: { $substr: ["$incident_details.timestamp", 0, 7] } } },
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
        ]
    );
    print("  ✓ View vw_monthly_liability created successfully.");
} catch (e) {
    print("  ✗ Error creating view: " + e.message);
}

// --- TASK 3: Apply Schema Validation ---
print("\n[TASK 3] Applying Schema Validation to shipment_ops...");
try {
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
                            status: { bsonType: "string", enum: ["Pending", "Cleared", "Rejected", "Held"] },
                            // FIX: Changed 'integer' to 'int' or 'double'
                            declaration_value: { bsonType: ["double", "int", "long"] }
                        }
                    },
                    items: { bsonType: "array" },
                    status_history: { bsonType: "array" }
                }
            }
        },
        validationLevel: "moderate",
        validationAction: "error"
    });
    print("  ✓ Schema validation applied successfully.");
} catch (e) {
    print("  ✗ Error: " + e.message);
}

print("\n============================================================");
print("  Setup Complete!");
print("============================================================");