# Task 4: RBAC & Security Documentation

## 4.1 Current Authentication Approach

The Nexus Logistics platform uses a Docker-based MongoDB deployment with **root-level authentication** enabled. The local environment authenticates connections using the following credentials:

- **Username:** `admin`
- **Password:** `password` (as defined in [`docker-compose.yaml`](../docker-compose.yaml))
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
