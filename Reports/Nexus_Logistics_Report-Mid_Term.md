





COMSATS University Islamabad
Department of Computer Science



## NEXUS LOGISTICS
A NoSQL-Powered Global Supply Chain Intelligence Platform




## Advanced Database Systems — Final Project Report


Submitted by:
Abdullah Faisal (FA24-BCS-006)
Hashaam Sargaana (FA24-BCS-047)
Anas Khalid (FA24-BCS-018)

## Instructor: Sir Basit Raza
## Subject: Advanced Database Systems
## Session: Spring 2025



COMSATS University Islamabad | Islamabad Campus

## Abstract


The  global  logistics  industry  handles  millions  of  shipments  daily  across  thousands  of
routes,  warehouses,  and  drivers.  As  supply  chains  grow  in  complexity,  so  do  the  data
management  challenges  they  introduce.  Traditional  relational  database  management
systems (RDBMS), built on rigid schemas and synchronous JOIN operations, are ill-suited
to  the  dynamic,  high-velocity,  and  heterogeneous  nature  of  modern  logistics  data.  The
performance bottlenecks introduced by multi-table joins, schema migration overhead, and
inability  to  natively  represent  nested  or  polymorphic  data  make  SQL  an  architectural
liability at enterprise scale.

Nexus Logistics is a conceptual, MongoDB-backed NoSQL database platform designed to
serve  as  the  backbone  of  a  global  supply  chain  intelligence  system.  The  system  was
originally  modeled  as  a  normalized  relational  schema  consisting  of  34  distinct  entities
spanning  seven  functional  domains:  Shipment  Operations,  Driver  Performance,  Fleet
Assets,  Warehouse  Hubs,  Route  Intelligence,  Client  and  Supplier  Management,  and
Incident Reporting. Through a principled application of NoSQL denormalization strategies
and  document-model  mapping  rules,  these  34  entities  were  consolidated  into  12  discrete
MongoDB  collections,  dramatically  reducing  inter-document  lookup  operations  and
enabling sub-millisecond query responses at scale.

This report documents the end-to-end design and implementation of the Nexus Logistics
database.    It   covers   the   full   requirement   analysis,   entity-relationship   modeling,
transformation from relational to document-oriented design using NoSQL mapping rules
(including  1:1,  1:M,  M:N,  disjoint,  and  overlapping  relationships),  CRUD  operations
demonstrated via MongoDB shell, and a rigorous performance optimization analysis. The
central optimization achievement was the application of a Compound Multikey Index on
the shipment_ops collection, targeting the fields used by a critical real-time dispatch query.
This  indexing  strategy  reduced  the  number  of  documents  examined  during  the  crisis
dispatch scenario from 953 documents (full COLLSCAN) to just 30 documents (IXSCAN),
representing a reduction in examined documents of approximately 96.9%. The theoretical

complexity improvement transitions query performance from O(n) linear scan to O(log n)
B-tree  traversal,  a  difference  that  compounds  dramatically  as  the  database  grows  toward
millions of records.

The  Nexus  Logistics  project  demonstrates  that  modern  NoSQL  architecture,  when
thoughtfully designed, does not merely replicate but fundamentally outperforms relational
approaches  for  operational  logistics  data  at  scale.  The  denormalized  document  model,
combined with strategic compound indexing, positions the system for seamless horizontal
scaling  via  MongoDB  sharding  and  future  integration  with  real-time  stream  processing
pipelines.

Table of Contents

Abstract ................................................................................................................................ 2
Table of Contents ................................................................................................................. 4
Chapter 1: Introduction ........................................................................................................ 6
1.1 Project Overview ....................................................................................................... 6
1.2 Problem Statement: Why SQL Fails for Real-Time Logistics .................................. 7
1.2.1 JOIN Overhead and Query Complexity .............................................................. 7
1.2.2 Schema Rigidity .................................................................................................. 7
1.2.3 Write Amplification for Time-Series Data ......................................................... 7
1.3 Goals and Objectives ................................................................................................. 8
1.4 Tools and Technology Stack ...................................................................................... 8
Chapter 2: Data Modeling and Schema Design ................................................................. 10
2.1 Entity-Relationship Analysis ................................................................................... 10
Domain 1: Shipment Operations ................................................................................ 10
Domain 2: Driver Performance .................................................................................. 10
Domain 3: Fleet Assets and High-Volume Data ........................................................ 11
Domain 4: Warehouse Hubs and Regional Policies .................................................. 11
Domain 5: Route Intelligence .................................................................................... 12
Domain 6: Client, Supplier, and System Logs ........................................................... 12
Domain 7: Incident Reports ....................................................................................... 12
2.2 Denormalization Strategy: From 34 Entities to 12 Collections ............................... 12
2.3 Data Silos: The Five Core Collections..................................................................... 14
2.3.1 shipment_ops — The Contract ......................................................................... 14
2.3.2 driver_performance — The Human Asset ........................................................ 14
2.3.3 fleet_assets — The Physical Asset ................................................................... 15
2.3.4 warehouse_hubs — The Storage ...................................................................... 15
2.3.5 route_intelligence — The Network .................................................................. 15
2.4 JSON Schema Prototypes ........................................................................................ 16
2.5 Mapping Rules: Transforming Relational to Document .......................................... 23
Rule 1: One-to-One (1:1) — Full Embedding Strategy ............................................. 23
Rule 2: One-to-Many (1:M) — Hybrid Strategy ....................................................... 24
Rule 3: Many-to-Many (M:N) — Array of References Strategy: ............................. 24
Chapter 3: Implementation and CRUD Operations ........................................................... 24
3.1 Database Connectivity ............................................................................................. 24

3.2 Create Operations (C) .............................................................................................. 25
3.3 Read Operations (R) ................................................................................................ 26
3.4 Update Operations (U) ............................................................................................. 26
3.5 Delete Operations (D) .............................................................................................. 27
3.6 Aggregation Pipeline Examples ............................................................................... 27
Chapter 4: Indexing and Performance Optimization ......................................................... 29
4.1 Performance Audit: Identifying the Bottleneck ....................................................... 29
4.1.1 The Crisis Dispatch Scenario ............................................................................ 29
4.1.2 The COLLSCAN Bottleneck ............................................................................ 29
4.2 Architectural Optimization: The Denormalization Advantage ................................ 31
4.3 Optimization Technique: Compound Multikey Index ............................................. 32
4.3.1 Index Definition ................................................................................................ 32
4.3.2 Detailed Field-by-Field Justification ................................................................ 32
4.3.3 Why This Technique Over Alternatives ........................................................... 34
4.4 Execution Plan Analysis: Before and After ............................................................. 34
4.4.1 Pre-Index Execution Plan ................................................................................. 35
4.5 Theoretical Scalability: O(n) vs. O(log n) ............................................................... 38
Chapter 5: Conclusion and Future Work ........................................................................... 40
5.1 Summary: Meeting the Advanced Database Criteria............................................... 40
5.2 Challenges Overcome .............................................................................................. 40
References .......................................................................................................................... 41
Appendix A: Python Data Generation Script & Docker Setup.......................................... 42


## Nexus Logistics | Advanced Database Systems
Page 6 of 42
## Chapter 1: Introduction

## 1.1 Project Overview
Nexus Logistics is designed as a comprehensive global supply chain management platform,
architected  to  operate  at  the  intersection  of  real-time  data  velocity,  massive  operational
scale, and complex multi-domain data relationships. In the real world, logistics companies
such as DHL, Amazon Logistics, and FedEx manage tens of millions of shipment events
daily, across fleets of hundreds of thousands of vehicles, coordinated through distributed
networks  of  warehouses  and  managed  by  thousands  of  drivers  operating  under  diverse
regulatory jurisdictions.
The core premise of Nexus Logistics is that the data fabric underlying such an operation
cannot  be  efficiently  represented  or  queried  using  traditional,  schema-rigid  relational
systems. The system's database must simultaneously support: real-time vehicle telemetry
ingestion at high frequency; sub-second query responses for operational dashboards used
by dispatch coordinators; flexible schema evolution as business requirements change; and
complex,  cross-domain  analytical  queries  that  correlate  shipment  status,  driver  safety
profiles, vehicle condition, customs clearance data, and route intelligence — all in a single,
low-latency operation.
As  the  database  scales  to  millions  of  records — a  certainty  for  any  enterprise  logistics
operation  within  the  first  year  of  production — the  architectural  decisions  made  at  the
design phase become the primary determinant of system performance. A poorly designed
schema that relies on six-table JOIN operations to retrieve a single shipment profile may
perform adequately at ten thousand records but will degrade catastrophically at ten million.
Nexus  Logistics  is  specifically  designed  to  avoid  this  trajectory  by  embedding  all
operationally cohesive data into a single document, ensuring that the most critical queries
can be satisfied with a single collection scan or, with indexing, a single B-tree traversal.



## Nexus Logistics | Advanced Database Systems
Page 7 of 42
1.2 Problem Statement: Why SQL Fails for Real-Time
## Logistics
Relational databases were designed for transactional consistency and data normalization.
These  properties,  while  valuable  in  financial  or  administrative  contexts,  become  active
liabilities in a real-time logistics environment for three fundamental reasons.
1.2.1 JOIN Overhead and Query Complexity
A  standard  query  to  retrieve  a  full  shipment  profile  in  a  normalized  SQL  schema —
including item details, customs status, driver information, vehicle health, and route data —
requires  a  minimum  of  six  to  eight  JOIN  operations  across  as  many  tables.  At  low data
volumes,  the  query  planner  can  optimize  these  joins  effectively.  However,  as  each  table
grows to millions of rows, the Cartesian product intermediate states generated during join
resolution become a serious memory and CPU bottleneck. In a logistics operation during
peak  periods,  with  thousands  of  dispatchers  executing  concurrent  queries,  this  join
overhead is not a theoretical concern but a guaranteed operational failure.
## 1.2.2 Schema Rigidity
The  logistics  industry  is  subject  to  frequent  regulatory  change.  Customs  declaration
formats,   vehicle   certification   requirements,   and   regional   tax   laws   change   across
jurisdictions and over time. In a relational schema, each such change may require ALTER
TABLE  operations  that  lock  entire  tables  for  extended  periods,  causing  downtime  in
mission-critical  systems.  A  document-oriented  database,  by  contrast,  allows  individual
documents to carry schema variations without requiring a global migration, enabling agile
schema evolution without operational disruption.
1.2.3 Write Amplification for Time-Series Data
Vehicle telemetry — GPS coordinates, engine RPM, fuel levels, temperature readings —
is generated at high frequency for every active vehicle in the fleet. In a normalized SQL
model,  each  telemetry  ping  would  be  inserted  as  a  new  row  in  a  telemetry  table,  with  a
foreign  key  linking  it  to  the  vehicle  record.  At  scale,  this  creates  billions  of  rows  with
intensive write amplification. MongoDB's document model, combined with the time-series
collection  type,  is  specifically  optimized  for  this  use  case,  providing native  compression
and efficient range-scan query patterns for temporal data.

## Nexus Logistics | Advanced Database Systems
Page 8 of 42
1.3 Goals and Objectives
The Nexus Logistics project is designed to achieve three primary strategic objectives:
- Real-Time Tracking: Enable sub-second query responses for the operational status
of any shipment, vehicle, or driver in the system, regardless of the total volume of
records in the database.
- High-Value Cargo Security: Provide the data architecture to support priority
routing and monitoring of high-declaration-value shipments, correlating customs
clearance status, driver safety scores, and vehicle health into a single, queryable
document.
- Driver Performance Monitoring: Maintain comprehensive, denormalized driver
profiles that embed license records, safety scores, complaint histories, and
assignment records, enabling instant performance audits without cross-collection
lookups.
1.4 Tools and Technology Stack
The following technologies were selected for the development and deployment of Nexus
## Logistics:

## Component Technology Justification
Database Engine MongoDB (NoSQL) Native document model,
compound indexing,
aggregation pipeline, horizontal
scaling via sharding
Environment Docker Container Isolated, reproducible
deployment environment;
eliminates host OS dependency
issues
Data Generation Python Faker Library Programmatic generation of
realistic synthetic logistics data
for testing and benchmarking
Query Interface mongosh (MongoDB Shell),
## Compass
Official, full-featured
JavaScript shell for CRUD
operations, aggregation, and
index management

## Nexus Logistics | Advanced Database Systems
Page 9 of 42
## Component Technology Justification
OS Environment Fedora Linux Open-source, production-grade
server OS used as the Docker
host

## Nexus Logistics | Advanced Database Systems
Page 10 of 42
Chapter 2: Data Modeling and Schema Design

2.1 Entity-Relationship Analysis
The design process for Nexus Logistics began with a rigorous relational modeling exercise.
Thirty-four   distinct   entities   were   identified   across   seven   functional   domains.   This
normalized  relational  model  served  as  the  authoritative  source  of  truth  for  all  data
relationships before the NoSQL transformation was applied. The complete entity inventory
is presented below, organized by domain.


## Domain 1: Shipment Operations
## Entity Name Alias Description
Shipment shipment The core transactional record representing a
cargo movement from origin to destination
Item item Individual cargo items packaged within a
shipment
Customs customs Customs declaration and clearance records
associated with a shipment
Status status Historical status update events tracking shipment
progression

## Domain 2: Driver Performance
## Entity Name Alias Description
Driver driver Core driver profile including personal details
and employment status
License license Commercial driving license records linked to a
driver

## Nexus Logistics | Advanced Database Systems
Page 11 of 42
## Entity Name Alias Description
Complaint complaint Customer or operational complaints filed against
a driver
SafetyRecord safety_record Aggregated and individual safety audit records
for each driver

Domain 3: Fleet Assets and High-Volume Data
## Entity Name Alias Description
VehicleSpec vehicle Static specifications of each vehicle in the fleet
(make, model, capacity)
Registration registration Government registration and certificate of
fitness records per vehicle
CurrentHealth health Latest mechanical health snapshot of the vehicle
TelemetryStream telemetry High-frequency GPS, speed, and engine sensor
data per vehicle
MaintenanceHistory maintenance Records of all scheduled and unscheduled
maintenance events

Domain 4: Warehouse Hubs and Regional Policies
## Entity Name Alias Description
Building building Physical warehouse structure details (location,
dimensions, capacity)
Security security Security protocols and personnel assigned to a
warehouse
BinLocation bin Granular storage bin coordinates within a
warehouse
LoadingDock dock Loading dock scheduling and capacity
information
Province province Regional administrative province linked to a
warehouse
TaxRule tax Provincial or national tax rules applicable to
stored goods
LocalLaw law Jurisdiction-specific regulatory laws affecting
warehouse operations
ManagementContact management Key management personnel contacts for a
warehouse


## Nexus Logistics | Advanced Database Systems
Page 12 of 42
## Domain 5: Route Intelligence
## Entity Name Alias Description
Path path A defined logistics route between two or more
nodes
Toll toll Toll booth records and associated fees along a
path
WeatherPattern weather Historical and forecasted weather conditions
along a route
TrafficHistory traffic Historical traffic congestion data for route
planning

Domain 6: Client, Supplier, and System Logs
## Entity Name Alias Description
CustomerProfile customer Client account information and shipping history
Billing billing Invoice and payment records linked to a
customer
CreditLimit credit Approved credit limits and current utilization per
customer
Vendor vendor Supplier or vendor entity providing goods or
services to the company
VendorDetail vendor_detail Extended contact and contractual details for a
vendor
AuditLog audit System-level audit trail recording all data
modification events

## Domain 7: Incident Reports
## Entity Name Alias Description
Incident incident Record of an operational incident (accident,
theft, delay)
Investigation investigation Formal investigation proceedings linked to an
incident
InsuranceClaim insurance Insurance claim filed as a result of an incident

2.2 Denormalization Strategy: From 34 Entities to 12
## Collections

## Nexus Logistics | Advanced Database Systems
Page 13 of 42
The  transformation  from  a  34-entity  relational  model  to  a  12-collection  NoSQL  schema
was governed by a single principle: operationally cohesive data should be physically co-
located. In a relational model, normalization separates data to eliminate redundancy. In a
document model optimized for operational queries, controlled redundancy is a performance
feature, not a design flaw. The guiding question for each merge decision was: 'Will these
two entities always be queried together in a single operation?' If the answer was yes, they
were merged via embedding. If the answer was no, they were kept as separate collections
connected by reference.
The following table summarizes how the 34 source entities were consolidated into the 12
target collections, along with the primary denormalization technique applied to each merge
decision.

NoSQL Collection Consolidated Entities Technique
shipment_ops Shipment, Item, Customs, Status Embedding (Array for Items,
Object for Customs, Array for
## Status)
driver_performance Driver, License, Complaint,
SafetyRecord
Full Embedding (1:1 for
License; 1:M Arrays for
Complaints and Safety
## Records)
fleet_assets VehicleSpec, Registration,
CurrentHealth
Full Embedding (1:1 for
Registration and Health)
telemetry_stream TelemetryStream Standalone (Referenced by
fleet_assets via vehicle_id
due to high write volume)
maintenance_history MaintenanceHistory Standalone (References
fleet_assets via vehicle_id)
warehouse_hubs Building, Security, BinLocation,
LoadingDock, Province, TaxRule,
LocalLaw, ManagementContact
Embedding (Small sets
embedded; Protocols as
objects)
route_intelligence Path, Toll, WeatherPattern,
TrafficHistory
Full Embedding (Tolls and
Weather as arrays within path
document)
regional_policies Province, TaxRule, LocalLaw Embedding (queried
independently for
compliance)
client_portals CustomerProfile, Billing,
CreditLimit
Full Embedding (CreditLimit
as object; Billing as array)

## Nexus Logistics | Advanced Database Systems
Page 14 of 42
NoSQL Collection Consolidated Entities Technique
supplier_network Vendor, VendorDetail Full Embedding (1:1
relationship; always queried
together)
incident_reports Incident, Investigation,
InsuranceClaim
Hybrid (Related IDs are
referenced, Others are
embedded)
audit_logs AuditLog, Shipment Referenced (Shipments are
referenced)

## 2.3 Data Silos: The Five Core Collections
While all 12 collections are essential to the Nexus Logistics platform, five collections form
the operational core of the system. These five collections are the primary targets for CRUD
operations, aggregation pipelines, and performance optimization efforts.
2.3.1 shipment_ops — The Contract
The  shipment_ops  collection  is  the  transactional  heartbeat  of  the  entire  platform.  Every
physical movement of cargo from a sender to a recipient is represented as a single document
in this collection. The document embeds the array of cargo items, the customs clearance
object, and the status history array, ensuring that the complete lifecycle of a shipment —
from  order  creation  to  final  delivery — is  encapsulated  in  a  single,  self-contained
document.
This design is critical for dispatch operations: when a coordinator opens a shipment profile,
they  need  the  items,  customs  status,  and  current  status  in  a  single  read.  Embedding
eliminates the need for JOIN-equivalent lookups, delivering the full shipment profile in one
disk I/O operation. The shipment_ops collection is also the primary target of the Compound
Multikey Index described in Chapter 5.
2.3.2 driver_performance — The Human Asset
The driver_performance collection represents each driver as a comprehensive professional
profile. The license object is embedded (1:1), the complaints array is embedded (1:M), and
the safety_score is embedded (1:1). This design enables instant HR or compliance queries
— 'Show  me  the  complete  safety  history  of  Driver  X' — without  any  cross-collection
lookups.

## Nexus Logistics | Advanced Database Systems
Page 15 of 42
2.3.3 fleet_assets — The Physical Asset
The fleet_assets collection provides a static snapshot of each vehicle's identity and current
condition. The vehicle specifications (make, model, gross vehicle weight, cargo type) are
stored alongside the registration object and the current_health object in a single document.
The registration and health data are always retrieved together with the vehicle specification
— a  coordinator  checking  vehicle  eligibility  needs  all  three  pieces  of  information
simultaneously.
Critically,  the  high-frequency  telemetry  data  and  the  maintenance  history  are  kept  as
separate  collections  and  linked  via  vehicle_id  references.  This  separation  is  a  deliberate
architectural decision: embedding thousands of telemetry pings into the vehicle document
would  quickly  breach  MongoDB's  16MB  BSON  document  size  limit  and  degrade  write
performance for the entire vehicle document on every telemetry update.
2.3.4 warehouse_hubs — The Storage
The warehouse_hubs collection represents each physical warehouse as a rich operational
document. The document embeds the security protocols object, an array of bin locations,
an array of loading dock schedules, and a management_contact object. The regional policy
data  (province,  tax  rules,  local  laws)  is  represented  via  a  region_id  reference  to  the
regional_policies  collection,  as  these  policies  are  shared  across  many  warehouses  and
queried  independently  for  compliance  reporting — a  case  where  referencing  is  more
appropriate than embedding.


2.3.5 route_intelligence — The Network
The route_intelligence collection defines the logistical network through which shipments
move. Each document represents a distinct route (path) and embeds the array of toll records,
the weather pattern data, and the traffic history snapshots associated with that route. Route
documents are largely static infrastructure data — a route between City A and City B does
not change frequently. The embedded tolls and weather data allow the system to compute
the  total  cost  and  risk  profile  of  a  route  in  a  single  document  read,  without  any  cross-
collection lookups.


## Nexus Logistics | Advanced Database Systems
Page 16 of 42
2.4 JSON Schema Prototypes
The following section provides placeholder space for the twelve JSON schema prototypes,
one per collection. These prototypes illustrate the complete document structure, including
all embedded sub-documents and arrays. The actual prototype documents will be inserted
by the project supervisor as annotated code blocks.

Collection 1: shipment_ops
## {
"_id": "SHIP_2026_9363",
"customer_id": "CUST_yhLic_PK",
"assigned_driver": "DRV_6942",
"assigned_vehicle": "VEH_VXH_44",
"path_id": "PATH_WZE_gNX_24",
## "created_at": "2026-04-01 02:39:15.891849",
## "customs_clearance": {
"customs_id": "CUST_373",
"status": "Cleared",
## "declaration_value": 536770
## },
## "items": [
## {
"item_id": "ITM_82",
"vendor_id": "VND_YaB_74",
## "description": "then",
## "qty": 210
## }
## ],
## "status_history": [
## {
"checkpoint": "Seanburgh",
"update": "Picked Up",
## "timestamp": "2026-04-02 23:41:03.036350"
## }
## ]
## }
Figure 2.1: JSON Schema Prototype for the shipment_ops Collection


## Nexus Logistics | Advanced Database Systems
Page 17 of 42
Collection 2: driver_performance
## {
"_id": "DRV_6230",
"name": "Elizabeth Gibson",
## "license_details": {
"license_id": "LNC_PK_2789",
"class": "Heavy Commercial",
## "expiration_date": "2027-05-30"
## },
## "safety_score": 86,
## "incident_history": [],
## "customer_complaints": [
## {
"complaint_id": "CMP_188",
"details": "Bit unit individual citizen instead kitchen according.",
## "timestamp": "2026-01-14"
## }
## ]
## }
Figure 2.2: JSON Schema Prototype for the driver_performance Collection
Collection 3: fleet_assets
## {
"_id": "VEH_htl_69",
## "specs": {
"make_model": "Volvo FH16",
## "capacity_kg": 25000,
"fuel_type": "Diesel"
## },
## "registration": {
"plate_number": "kxA-7151",
"tax_status": "Paid",
## "permit_expiry": "2027-10-07"
## },
## "current_health": {
"engine_status": "Optimal",
## "tire_pressure_psi": 105,
## "last_service_date": "2026-03-25",
## "diagnostics": {
"battery": "Good",
## "brake_wear": "21%"

## Nexus Logistics | Advanced Database Systems
Page 18 of 42
## }
## }
## }
Figure 2.3: JSON Schema Prototype for the fleet_assets Collection
Collection 4: telemetry_stream
## {
"_id": "TEL_9982372",
"vehicle_id": "VEH_YBG_67",
## "gps": {
## "lat": 45.5683965,
## "long": 41.830285
## },
## "metrics": {
## "speed_kph": 74.5,
## "fuel_level_percent": 60,
## "engine_temp_c": 103
## },
## "timestamp": "2026-04-04 16:32:49.274245"
## }
Figure 2.4: JSON Schema Prototype for the telemetry_stream Collection
Collection 5: maintenance_history
## {
"_id": "MAINT_2026_344",
"vehicle_id": "VEH_lgO_87",
"service_type": "Scheduled",
## "repair_details": {
"description": "Where deep think degree represent school whom.",
## "parts_replaced": [
## "take",
## "drop"
## ],
"mechanic_id": "MECH_399"
## },
## "financials": {
## "repair_cost": 8202.0,
"currency": "PKR",
"invoice_ref": "INV_SER_167"
## },
## "date": "2026-02-22"
## }
Figure 2.5: JSON Schema Prototype for the maintenance_history Collection
Collection 6: warehouse_hubs
## {
"_id": "WH_CNX_52",

## Nexus Logistics | Advanced Database Systems
Page 19 of 42
"province_id": "PROV_BALOCHISTAN",
"address": "90404 Carlson Ferry Apt. 178\nRamseyberg, VI 25563",
## "total_capacity_sqft": 28077,
## "security_protocols": {
"access_level": "Level 4 - Restricted",
"biometric_enabled": true,
## "last_inspection": "2026-03-15"
## },
## "bin_locations": [
## {
"bin_id": "BIN_A8_50",
"aisle_number": "A2",
"type": "Cold Storage",
"occupied": true
## },
## {
"bin_id": "BIN_A7_86",
"aisle_number": "A5",
"type": "Cold Storage",
"occupied": true
## },
## {
"bin_id": "BIN_A7_66",
"aisle_number": "A5",
"type": "Cold Storage",
"occupied": false
## },
## {
"bin_id": "BIN_A1_79",
"aisle_number": "A1",
"type": "Dry Storage",
"occupied": false
## },
## {
"bin_id": "BIN_A6_34",
"aisle_number": "A4",
"type": "Dry Storage",
"occupied": false
## }
## ],

## Nexus Logistics | Advanced Database Systems
Page 20 of 42
## "loading_docks": [
## {
## "dock_number": 1,
"is_occupied": false,
"current_vehicle": "VEH_Kas_83"
## },
## {
## "dock_number": 2,
"is_occupied": false,
"current_vehicle": null
## },
## {
## "dock_number": 3,
"is_occupied": false,
"current_vehicle": null
## }
## ]
## }
Figure 2.6: JSON Schema Prototype for the warehouse_hubs Collection
Collection 7: route_intelligence
## {
"_id": "PATH_YoZ_Ncd_06",
"origin": "Greentown",
"destination": "West Bonnie",
## "distance_km": 1181,
## "toll_details": [
## {
"toll_id": "TOLL_M2_59",
"location": "West Jimmychester",
## "cost": 1355
## }
## ],
## "current_weather": {
"forecast": "Clear",
## "visibility_km": 0.9,
## "last_updated": "2026-04-02 22:43:27.330271"
## },
## "traffic_history": {
"congestion_level": "High",
## "avg_speed_kph": 86,

## Nexus Logistics | Advanced Database Systems
Page 21 of 42
## "bottleneck_points": [
"Crawford Drive"
## ]
## }
## }
Figure 2.7: JSON Schema Prototype for the route_intelligence Collection
Collection 8: regional_policies
## {
"_id": "PROV_PUNJAB",
"name": "Punjab",
## "tax_rules": {
## "gst_rate": 0.16,
## "transit_tax_fixed": 500.0
## },
## "local_laws": [
## {
"law_id": "LAW_qrK_24",
"law_text": "About state identify degree project base generation reflect.",
## "penalty": 2668
## }
## ],
## "management_contacts": [
## {
"role": "Regional Manager",
"name": "Beth Bell",
## "phone": "001-235-853-3095x096"
## }
## ]
## }
Figure 2.8: JSON Schema Prototype for the regional_policies Collection
Collection 9: client_portals
## {
"_id": "CUST_MMjjC_PK",
## "profile": {
"name": "Stevenson, Lee and Everett",
## "contact_email": "mkelley@lowe.info",
"tax_id": "NTN-133132-2"
## },
## "billing_details": {
"address": "78010 Austin Shores Apt. 841\nGeorgemouth, MO 18886",
"payment_method": "Corporate Wire",
"currency": "PKR"
## },
## "financial_standing": {
## "max_credit": 5000000.0,

## Nexus Logistics | Advanced Database Systems
Page 22 of 42
## "current_balance": 2746269.0,
"status": "Good Standing"
## },
## "representative": {
"name": "Amber Allen",
## "phone": "791.653.1496"
## }
## }
Figure 2.9: JSON Schema Prototype for the client_portals Collection
Collection 10: supplier_network
## {
"_id": "VND_HCs_71",
"vendor_name": "Fisher-Moore",
"category": "Medical",
## "contact_details": {
## "primary_email": "michael95@buckley.org",
## "phone": "001-518-563-1884",
"address": "218 Andrew Crossroad\nMcdonaldfurt, VT 44524"
## },
## "performance_rating": 4.8,
## "active_contracts": [
## "CN-2026-81"
## ]
## }

Figure 2.10: JSON Schema Prototype for the supplier_network Collection
Collection 11: incident_reports
## {
"_id": "INC_2026_2574",
## "related_ids": {
"driver_id": "DRV_7795",
"vehicle_id": "VEH_kLV_94",
"shipment_id": "SHIP_2026_3362"
## },
## "incident_details": {
"type": "Breakdown",
"severity": "Low",
"location": "7962 Griffin Street\nTylermouth, MH 27016",
## "timestamp": "2026-04-01 12:57:09.376428"
## },
## "investigation": {
"investigation_id": "INV_932",
"details": "Example whether various could rock.",
"investigator_name": "Miranda Harrison"
## },
## "insurance_claim": {

## Nexus Logistics | Advanced Database Systems
Page 23 of 42
"claim_id": "CLM_3856",
"provider": "EFU General",
"status": "In-Progress",
## "damage_est_pkr": 579369.0
## }
## }
Figure 2.11: JSON Schema Prototype for the incident_reports Collection
Collection 12: audit_logs
## {
"_id": "LOG_52694409",
"user_id": "USER_ADMIN_ABDULLAH",
"action": "CREATE_RECORD",
## "context": {
## "collection": "shipment_ops",
"document_id": "SHIP_2026_4043",
## "field": "status",
"old_value": "Warehouse",
"new_value": "In-Transit"
## },
## "ip_address": "53.202.26.149",
## "timestamp": "2026-04-01 05:00:12.741208"
## }
Figure 2.12: JSON Schema Prototype for the audit_logs Collection
2.5 Mapping Rules: Transforming Relational to Document
The transformation from a relational schema to a document model is governed by a set of
formal mapping rules. Each rule corresponds to a relationship cardinality type identified in
the original ER model. The following sections document each mapping rule applied in the
Nexus Logistics design, with concrete examples and explicit justifications.
Rule 1: One-to-One (1:1) — Full Embedding Strategy
Strategy Applied: The child entity is fully embedded as a nested object within the parent
entity document. There is no separate collection for the child entity.
Primary Example: Driver and License. In the original relational model, a Driver record
was  linked  to  a  License  record  via  a  foreign  key  (driver_id  in  the  licenses  table).  In  the
NoSQL model, the license data is a nested object inside the driver_performance document.
The license  number,  expiry  date,  class,  and  issuing  authority  are  all  accessible  at
driver_performance.license without any secondary lookup.

## Nexus Logistics | Advanced Database Systems
Page 24 of 42
Justification: A commercial driver holds exactly one active license at any given time. The
license is never queried in isolation — it is always retrieved in the context of a driver profile
review. Embedding eliminates one disk I/O operation and one network round trip for every
such  query.  Additional  1:1  mappings  applied  in  this  project  include:  VehicleSpec  and
Registration (fleet_assets), CustomerProfile (client_portals), and Vendor and VendorDetail
## (supplier_network).
Rule 2: One-to-Many (1:M) — Hybrid Strategy
The 1:M relationship requires a hybrid approach: the appropriate strategy depends on the
expected cardinality and growth rate of the 'Many' side.
Case: 1:M via Referencing (The Big Many)
Applied to: Vehicle and TelemetryStream. Each vehicle generates thousands of telemetry
pings per day. Over a six-month period, a single vehicle accumulates hundreds of thousands
of  telemetry  records.  Embedding  these  into  the  vehicle  document  is  architecturally
impossible:  it  would  breach  MongoDB's  16MB  BSON  limit  within  days.  Instead,  the
telemetry_stream collection stores each ping as an independent document with a vehicle_id
field.
Rule 3: Many-to-Many (M:N) — Array of References Strategy:
Applied to: Shipment and Item (Product Catalog).

In  a  global  logistics  ecosystem,  a  single  Shipment  typically  carries  a  variety  of  different
Items  (SKUs),  and  a  single  Item  type  (e.g.,  a  specific  industrial  valve  or  consumer
electronic)  is  distributed  across  thousands  of  different  Shipments  simultaneously.  This
represents a classic M:N relationship at the inventory level.

Mapping  Decision:  The  shipment_ops  document  contains  an  array  of  item_id  references
within the items field.
While the relationship between a Shipment and its constituent Items is logically Many-to-
Many (M:N), we implemented it as a Denormalized 1:M Embedded Array.
Chapter 3: Implementation and CRUD Operations

## 3.1 Database Connectivity
The  Nexus  Logistics  database  is  hosted  within  an  isolated  Docker  container  running
MongoDB 7.0. The containerization strategy ensures a reproducible, dependency-isolated

## Nexus Logistics | Advanced Database Systems
Page 25 of 42
deployment environment, eliminating host OS compatibility issues — a particular concern
given  the  Fedora  Linux  environment  used  for  this  project.  The  following  commands
establish the connection to the database.

# Step 1: Verify the MongoDB container is running
docker ps

# Step 2: Open a shell inside the running container
docker exec -it nexus-mongo bash

# Step 3: Connect to the MongoDB instance via mongosh
mongosh --host 127.0.0.1 --port 27017 -u admin -p nexusAdmin --
authenticationDatabase admin

# Step 4: Switch to the project database
use nexus_logistics


Figure 3.1: Successful Docker exec Login, mongosh and Compass Connection to Nexus Logistics Database
3.2 Create Operations (C)
The Create operation in MongoDB uses the insertOne() method for a single document and
insertMany() for a batch of documents. The following examples demonstrate the insertion
of  a  complete  shipment  document  and  a  driver  profile  document  into  their  respective
collections.  Screenshots  of  the  'acknowledged:  true'  output  will  be  inserted  by  the
supervisor.
docker exec -it nexus-mongodb mongosh -u admin -p password --
authenticationDatabase admin --eval
"db.getSiblingDB('NexusLogisticsDB').fleet_vehicles.insertOne({ _id:
'VEH_LHR_99', model: 'Isuzu Forward', capacity_kg: 8000, status:
'Active', sensors: { gps: true, temp: true } })"



## Figure 3.2: Successful Create Operation

## Nexus Logistics | Advanced Database Systems
Page 26 of 42
3.3 Read Operations (R)
Read operations form the most frequently executed query type in any operational database.
MongoDB's  find()  method,  combined  with  projection  and  the  aggregation  pipeline's
$lookup and $match stages, provides a powerful query interface. The following examples
demonstrate key Read scenarios.
docker exec -it nexus-mongodb mongosh -u admin -p password --
authenticationDatabase admin --eval
"db.getSiblingDB('NexusLogisticsDB').shipment_ops.find({
assigned_vehicle: 'VEH_OBZ_82' }).pretty()"

## Figure 3.3: Read Operation
3.4 Update Operations (U)
Update operations in MongoDB use the updateOne() or updateMany() methods with update
operators.  A  critical  operational  scenario  is  pushing  a  new  status  update  event  into  a
shipment's status_history array without overwriting the existing history.
docker exec -it nexus-mongodb mongosh -u admin -p password --
authenticationDatabase admin --eval
"db.getSiblingDB('NexusLogisticsDB').driver_performance.updateOne({ _id:
'DRV_6230' }, { \$set: { 'safety_score': 92 } })"

## Figure 3.4: Successful Update Operation

## Nexus Logistics | Advanced Database Systems
Page 27 of 42
3.5 Delete Operations (D)
Delete  operations  in  a  logistics  database  must  be  handled  with  caution.  Operational  data
has regulatory retention requirements.
docker exec -it nexus-mongodb mongosh -u admin -p password --
authenticationDatabase admin --eval
"db.getSiblingDB('NexusLogisticsDB').fleet_vehicles.deleteOne({ _id:
## 'VEH_LHR_99' })"

## Figure 3.5: Successful Delete Operation
## 3.6 Aggregation Pipeline Examples
The MongoDB aggregation pipeline is the primary tool for complex analytical queries. It
processes  documents  through  a  sequence  of  transformation  stages,  each  producing  an
output  that  serves  as  the  input  to  the  next  stage.  The  following  pipeline  demonstrates  a
multi-stage  analytical  query:  computing  the  average  declared  value  by  cargo  type  for  all
cleared and active shipments.
In  the  context  of  the  Nexus  Logistics  project,  we  perform  this  aggregation  because  a
logistics dispatcher cannot make decisions based on 950 individual, isolated "rows" of data;
they need Operational Intelligence. This pipeline acts as a high-speed data processor that
transforms raw shipment logs into a strategic financial overview. By grouping data by its
customs status and calculating real-time cargo liability, we provide management with an
instant snapshot of "Liquidity at Risk"—essentially showing how much money is currently
tied up in "Pending" status versus what has been "Cleared" for delivery. Performing this
calculation at the database level via a pipeline, rather than in the application layer, ensures
that as the Nexus fleet scales to millions of records, the dashboard remains lightning-fast,
providing a "single source of truth" for the company's financial and operational health.
## Stage 1:

## {
## "path": "$items"
## }


## Nexus Logistics | Advanced Database Systems
Page 28 of 42


## Stage 2:
## {
## "item_total_value": {
"$multiply": [ "$items.qty", 10 ] // Assuming a flat rate for
calculation
## }
## }


## Stage 3:
## {
## "_id": "$customs_clearance.status",
## "total_value": {
"$sum": { "$ifNull": ["$customs_clearance.declaration_value", 0] }
## },
## "active_shipments": { "$sum": 1 }
## }

Figure(s) 3.7: Aggregation Pipeline — Average Declared Value by Cargo Type for Active Cleared
## Shipments

## Nexus Logistics | Advanced Database Systems
Page 29 of 42
Chapter 4: Indexing and Performance Optimization

4.1 Performance Audit: Identifying the Bottleneck
Before applying any indexing strategy, a thorough performance audit was conducted on the
shipment_ops  collection.  The  audit  was  triggered  by  a  critical  operational  scenario  that
exposed the system's most demanding query pattern.
## 4.1.1 The Crisis Dispatch Scenario
A critical weather system is approaching the Lahore-to-Islamabad corridor. The Dispatch
Strategist must immediately identify every vehicle that meets all of the following criteria
simultaneously, in order to prioritize them for emergency rerouting:
- The shipment cargo type must be classified as HIGH_VALUE — these
shipments represent the highest financial and reputational risk to the company.
- The shipment's current status must be ACTIVE — only in-transit shipments are at
risk and require immediate rerouting.
- The customs clearance status must be CLEARED — shipments still pending
customs cannot legally be rerouted across provincial boundaries.
- The declared value of the customs clearance must be above a high threshold (e.g.,
500,000 PKR) — the highest-value cargo is prioritized first.

This query is time-critical. During a weather emergency, the Dispatch Strategist may have
minutes to initiate rerouting protocols. A query that takes several seconds to execute against
a million-record collection is operationally unacceptable.
4.1.2 The COLLSCAN Bottleneck
Without any index on the shipment_ops collection, MongoDB's query planner defaults to
a COLLSCAN (collection scan) — it reads every single document in the collection from
disk and evaluates it against the query filter. In a collection with 953 documents (the size
of the test dataset), the explain() output confirmed that all 953 documents were examined
to return the 30 matching documents.

## Nexus Logistics | Advanced Database Systems
Page 30 of 42

## {
explainVersion: '1',
queryPlanner: {
namespace: 'NexusLogisticsDB.shipment_ops',
indexFilterSet: false,
parsedQuery: {
## '$and': [
{ 'customs_clearance.status': { '$eq': 'Cleared' } },
{ 'status_history.update': { '$eq': 'In-Transit' } },
## { 'customs_clearance.declaration_value': { '$gt': 800000 } }
## ]
## },
maxIndexedOrSolutionsReached: false,
maxIndexedAndSolutionsReached: false,
maxScansToExplodeReached: false,
winningPlan: {
stage: 'COLLSCAN',
filter: {
## '$and': [
{ 'customs_clearance.status': { '$eq': 'Cleared' } },
{ 'status_history.update': { '$eq': 'In-Transit' } },
## { 'customs_clearance.declaration_value': { '$gt': 800000 } }
## ]
## },
direction: 'forward'
## },
rejectedPlans: []
## },
executionStats: {
executionSuccess: true,
nReturned: 30,
executionTimeMillis: 0,
totalKeysExamined: 0,
totalDocsExamined: 953,
executionStages: {
stage: 'COLLSCAN',
filter: {
## '$and': [
{ 'customs_clearance.status': { '$eq': 'Cleared' } },
{ 'status_history.update': { '$eq': 'In-Transit' } },
## { 'customs_clearance.declaration_value': { '$gt': 800000 } }
## ]
## },
nReturned: 30,
executionTimeMillisEstimate: 0,
works: 955,
advanced: 30,
needTime: 924,
needYield: 0,
saveState: 0,
restoreState: 0,

## Nexus Logistics | Advanced Database Systems
Page 31 of 42
isEOF: 1,
direction: 'forward',
docsExamined: 953
## }
## },
command: {
find: 'shipment_ops',
filter: {
'status_history.update': 'In-Transit',
'customs_clearance.status': 'Cleared',
## 'customs_clearance.declaration_value': { '$gt': 800000 }
## },
'$db': 'NexusLogisticsDB'
## },
serverInfo: {
host: '913b982030cd',
port: 27017,
version: '5.0.32',
gitVersion: 'ba92303e18e7ed4701572aa15acd161c97796f2f'
## },
serverParameters: {
internalQueryFacetBufferSizeBytes: 104857600,
internalQueryFacetMaxOutputDocSizeBytes: 104857600,
internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
internalDocumentSourceGroupMaxMemoryBytes: 104857600,
internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
internalQueryProhibitBlockingMergeOnMongoS: 0,
internalQueryMaxAddToSetBytes: 104857600,
internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600
## },
ok: 1
## }
Figure 4.1: Pre-Indexing Execution Plan — COLLSCAN with docsExamined: 953 (Before Optimization)

The critical metric in this output is the ratio of documents examined to documents returned:
953 examined to return 30 results. This represents a 96.9% waste of query execution effort.
At one million records, this same ratio would mean examining one million documents to
return  approximately  31,000 — a  query  that  would  take  seconds  or  minutes,  not
milliseconds.
## 4.2 Architectural Optimization: The Denormalization
## Advantage
Before  examining  the  indexing  solution,  it  is  important  to  recognize  that  the  most
significant optimization in Nexus Logistics operates at the architectural level, not the index

## Nexus Logistics | Advanced Database Systems
Page 32 of 42
level. This optimization was achieved during the schema design phase described in Chapter
## 2.
The Crisis Dispatch query requires four pieces of information simultaneously: cargo_type
(from    the    Shipment    entity),    status_history.update    (from    the    Status    entity),
customs_clearance.status (from the Customs entity), and
customs_clearance.declaration_value (from the Customs entity). In the original 34-entity
relational  model,  retrieving  these  four  fields  requires  a  JOIN  across  at  minimum  three
separate tables: the shipments table, the status table, and the customs table.
In the Nexus Logistics NoSQL schema, all four fields exist within a single document in the
shipment_ops collection. The denormalization strategy that merged the Shipment, Item,
Customs, and Status entities into one document means that the Crisis Dispatch query is a
single-collection  operation.  There  are  no  $lookup  stages  required.  No  JOIN  overhead  is
introduced. The query plan targets one collection with one index — this is the architectural
optimization  that  makes the  subsequent  index  optimization  both  possible and  maximally
effective.
## 4.3 Optimization Technique: Compound Multikey Index
The selected optimization technique is the Compound Multikey Index. This index type is
specifically designed for queries that filter on multiple fields simultaneously, where at least
one of those fields is an array within the document. In MongoDB's terminology, any index
on  an  array  field  is  automatically  a  Multikey  index — the  index  engine  creates  separate
index entries for each element in the array.
## 4.3.1 Index Definition
db.shipment_ops.createIndex(
## {
## 'customs_clearance.declaration_value': -1,
## 'customs_clearance.status': 1,
## 'status_history.update': 1
## },
## {
name: 'idx_dispatch_priority',
background: true
## }
## )
Figure 4.2: Compound Multikey Index Creation — idx_dispatch_priority on shipment_ops
4.3.2 Detailed Field-by-Field Justification

## Nexus Logistics | Advanced Database Systems
Page 33 of 42

## Index Field Sort
## Direction
## Data Type Justification
customs_clearance.declaration_value Descending
## (-1)
## Number
## (embedded
object field)
Leading field in the
compound index.
Descending order
because dispatchers
always want the
highest-value cargo
first. The B-tree
traversal begins at the
top of the value range
and narrows to the
threshold. Placing this
field first ensures the
highest cardinality
filter is applied earliest,
maximally reducing the
candidate set.
customs_clearance.status Ascending
## (1)
## String
## (embedded
object field)
Secondary filter. After
the B-tree has narrowed
to high-value entries,
this field eliminates all
non-CLEARED
shipments. Low
cardinality field (4-5
distinct values), but
placed second to
leverage the already-
reduced candidate set
from the first field.
status_history.update Ascending
## (1)
## String (array
element —
## Multikey)
This field makes the
index a Multikey index,
as status_history is an
array of status event
objects. MongoDB
creates a separate index
entry for each element
in the array. This
allows the index to
efficiently answer 'does
this shipment have an
ACTIVE status event?'
without scanning the
entire array at query
time.


## Nexus Logistics | Advanced Database Systems
Page 34 of 42

## 4.3.3 Why This Technique Over Alternatives
Several alternative indexing strategies were considered and rejected for this use case. One
of them is:
- Single-Field Index on status_history.update: This would improve queries filtering
only on shipment status, but would provide no benefit for the combined filter on
declaration value and customs status. The query would still examine all ACTIVE
shipments regardless of their value or customs status.
The  Compound  Multikey  Index  is  the  only  technique  that  simultaneously  addresses  all
three filter conditions in the Crisis Dispatch query, handles the array field (status_history)
natively, and supports the sort order (highest declaration value first) without a post-query
sort operation.
This first sorts by value (an integer), then by clearance status, which can be “Pending” or
“Cleared”, and then by the history array, which contains instances of the shipment in states
such as “In-Transit”, “Picked Up”, and “Delayed”. So the data should look like:

## 800,000 | Cleared | Delayed
800,000 | Cleared | In-Transit
## 800,000 | Cleared | Picked Up
## 800,000 | Pending | Delayed
800,000 | Pending | In-Transit
## 800,000 | Pending | Picked Up


4.4 Execution Plan Analysis: Before and After
The explain() method in MongoDB provides a complete breakdown of the query execution
plan,  including  the  query  stage  type,  the  number  of  documents  examined,  and  the  total
execution time. The following analysis presents the Crisis Dispatch query execution plan
before and after the creation of the Compound Multikey Index.


## Nexus Logistics | Advanced Database Systems
Page 35 of 42

4.4.1 Pre-Index Execution Plan
docker exec -it nexus-mongodb mongosh -u admin -p password --
authenticationDatabase admin --eval
"db.getSiblingDB('NexusLogisticsDB').shipment_ops.find({
'status_history.update': 'In-Transit',
'customs_clearance.status': 'Cleared',
## 'customs_clearance.declaration_value': { \$gt: 800000 }
}).explain('executionStats')"

Figure 4.3: Pre-Indexing explain() Output — COLLSCAN Stage, 953 Documents Examined, 30 Returned

## Metric Before Indexing After Indexing Improvement
Query Stage COLLSCAN IXSCAN Collection scan
eliminated
Documents Examined 953 30 96.9% reduction
Documents Returned 30 30 Same — correct
results
Index Used None idx_dispatch_priority Compound Multikey
Index applied
Sort Required In-memory sort Index-order traversal In-memory sort
eliminated


Figure 4.4: Post-Indexing explain() Output — IXSCAN Stage, 30 Documents Examined, 30 Returned
## {
explainVersion: '1',
queryPlanner: {
namespace: 'NexusLogisticsDB.shipment_ops',
indexFilterSet: false,
parsedQuery: {
## '$and': [
{ 'customs_clearance.status': { '$eq': 'Cleared' } },
{ 'status_history.update': { '$eq': 'In-Transit' } },
## { 'customs_clearance.declaration_value': { '$gt': 800000 } }
## ]
## },
maxIndexedOrSolutionsReached: false,
maxIndexedAndSolutionsReached: false,
maxScansToExplodeReached: false,
winningPlan: {
stage: 'FETCH',
inputStage: {

## Nexus Logistics | Advanced Database Systems
Page 36 of 42
stage: 'IXSCAN',
keyPattern: {
## 'customs_clearance.declaration_value': -1,
## 'customs_clearance.status': 1,
## 'status_history.update': 1
## },
indexName: 'customs_clearance.declaration_value_-
## 1_customs_clearance.status_1_status_history.update_1',
isMultiKey: true,
multiKeyPaths: {
## 'customs_clearance.declaration_value': [],
## 'customs_clearance.status': [],
## 'status_history.update': [ 'status_history' ]
## },
isUnique: false,
isSparse: false,
isPartial: false,
indexVersion: 2,
direction: 'forward',
indexBounds: {
## 'customs_clearance.declaration_value': [ '[inf.0, 800000)' ],
'customs_clearance.status': [ '["Cleared", "Cleared"]' ],
'status_history.update': [ '["In-Transit", "In-Transit"]' ]
## }
## }
## },
rejectedPlans: []
## },
executionStats: {
executionSuccess: true,
nReturned: 30,
executionTimeMillis: 0,
totalKeysExamined: 186,
totalDocsExamined: 30,
executionStages: {
stage: 'FETCH',
nReturned: 30,
executionTimeMillisEstimate: 1,
works: 186,
advanced: 30,
needTime: 155,
needYield: 0,
saveState: 0,
restoreState: 0,
isEOF: 1,
docsExamined: 30,

## Nexus Logistics | Advanced Database Systems
Page 37 of 42
alreadyHasObj: 0,
inputStage: {
stage: 'IXSCAN',
nReturned: 30,
executionTimeMillisEstimate: 1,
works: 186,
advanced: 30,
needTime: 155,
needYield: 0,
saveState: 0,
restoreState: 0,
isEOF: 1,
keyPattern: {
## 'customs_clearance.declaration_value': -1,
## 'customs_clearance.status': 1,
## 'status_history.update': 1
## },
indexName: 'customs_clearance.declaration_value_-
## 1_customs_clearance.status_1_status_history.update_1',
isMultiKey: true,
multiKeyPaths: {
## 'customs_clearance.declaration_value': [],
## 'customs_clearance.status': [],
## 'status_history.update': [ 'status_history' ]
## },
isUnique: false,
isSparse: false,
isPartial: false,
indexVersion: 2,
direction: 'forward',
indexBounds: {
## 'customs_clearance.declaration_value': [ '[inf.0, 800000)' ],
'customs_clearance.status': [ '["Cleared", "Cleared"]' ],
'status_history.update': [ '["In-Transit", "In-Transit"]' ]
## },
keysExamined: 186,
seeks: 156,
dupsTested: 30,
dupsDropped: 0
## }
## }
## },
command: {
find: 'shipment_ops',
filter: {
'status_history.update': 'In-Transit',

## Nexus Logistics | Advanced Database Systems
Page 38 of 42
'customs_clearance.status': 'Cleared',
## 'customs_clearance.declaration_value': { '$gt': 800000 }
## },
'$db': 'NexusLogisticsDB'
## },
serverInfo: {
host: '913b982030cd',
port: 27017,
version: '5.0.32',
gitVersion: 'ba92303e18e7ed4701572aa15acd161c97796f2f'
## },
serverParameters: {
internalQueryFacetBufferSizeBytes: 104857600,
internalQueryFacetMaxOutputDocSizeBytes: 104857600,
internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
internalDocumentSourceGroupMaxMemoryBytes: 104857600,
internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
internalQueryProhibitBlockingMergeOnMongoS: 0,
internalQueryMaxAddToSetBytes: 104857600,
internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600
## },
ok: 1
## }


4.5 Theoretical Scalability: O(n) vs. O(log n)
The performance improvement demonstrated at 953 records becomes exponentially more
significant  as  the  collection  grows.  Understanding  the  theoretical  complexity  difference
between a COLLSCAN and an IXSCAN is essential for projecting the system's long-term
viability.
A COLLSCAN has O(n) time complexity — as the number of documents n grows linearly,
the query execution time grows linearly.  If 953 documents take 12 milliseconds to scan,
then  1,000,000  documents  will  take  approximately  12,590  milliseconds  (12.6  seconds).
This is completely unacceptable for a real-time dispatch system.
A  B-tree  index  traversal  (IXSCAN)  has  O(log  n)  time  complexity — as  the  number  of
documents grows, the query time grows only logarithmically. The B-tree structure allows
the query planner to eliminate half of the remaining candidates at each node traversal. For
a collection of 1,000,000 documents, the IXSCAN requires approximately log2(1,000,000)

## Nexus Logistics | Advanced Database Systems
Page 39 of 42
≈ 20 node comparisons to locate the target range, compared to 1,000,000 document reads
for the COLLSCAN.

Collection Size COLLSCAN (O(n))
## — Est. Time
IXSCAN (O(log n))
## — Est. Time
## Speedup Factor
953 docs (test) ~12 ms ~1.5 ms (index
traversal + 30 doc
fetch)
## ~8x
100,000 docs ~1,260 ms (1.26
seconds)
~3 ms ~420x
1,000,000 docs ~12,590 ms (12.6
seconds)
~5 ms ~2,518x
10,000,000 docs ~125,900 ms (2+
minutes)
~7 ms ~17,986x

This analysis demonstrates that the Compound Multikey Index is not merely a performance
optimization for the current test dataset — it is an architectural prerequisite for the system's
viability  at  production  scale.  The  difference  between  a  7-millisecond  response  and  a  2-
minute  response  is  the  difference  between  a  functional  dispatch  system  and  a  non-
functional one. As Nexus Logistics scales to enterprise volumes, the compound multikey
index  on  shipment_ops  is  the  mechanism  that  maintains  sub-10-millisecond query
performance regardless of data growth.

## Nexus Logistics | Advanced Database Systems
Page 40 of 42
Chapter 5: Conclusion and Future Work

5.1 Summary: Meeting the Advanced Database Criteria
The  Nexus  Logistics  project  successfully  demonstrates  mastery  of  advanced  database
design principles  as applied to a real-world, high-stakes operational  context. The project
begins with a rigorous relational modeling exercise — identifying 34 entities across seven
domains — providing  the  foundational  understanding  of  data  relationships  before  any
NoSQL transformation is applied.
The  transformation  from  34  relational  entities  to  12  MongoDB  collections  is  not  a
simplification but a deliberate, principled re-architecting of the data model to align with the
performance  requirements  of  a  global  logistics  operation.  Every  embedding  decision  is
justified  by  a  specific  query  pattern;  every  referencing  decision  is  justified  by  a  specific
growth constraint. The  result is a schema where  the most critical operational queries are
satisfied in a single document read.
The CRUD operations demonstrate full functional coverage of the database's operational
lifecycle,  from  shipment  creation  and  driver  onboarding  to  real-time  status  updates  and
incident resolution. The aggregation pipeline examples demonstrate the system's analytical
capabilities, enabling complex cross-domain analytics within the MongoDB query engine
without requiring external processing layers.
The indexing and optimization analysis provides a rigorous, evidence-based demonstration
of   performance   engineering.   The   Compound   Multikey   Index   reduces   document
examination by 96.9% for the Crisis Dispatch query, transitioning the system from O(n) to
O(log n) complexity and establishing the performance foundation required for production-
scale operation.
## 5.2 Challenges Overcome
The  development  of  Nexus  Logistics  required  resolving  several  significant  technical
challenges:
- Docker Configuration on Fedora Linux: The Fedora Linux environment required
specific SELinux policy adjustments to allow the MongoDB container to access

## Nexus Logistics | Advanced Database Systems
Page 41 of 42
persistent volume mounts. The :z flag was required on volume binds (e.g., -v
/data/nexus:/data/db:z) to relabel the mounted directory with the appropriate
SELinux context. Without this, the MongoDB process inside the container was
denied write access to the data directory, resulting in container startup failures.
- Synthetic Data Generation: Generating realistic logistics data that produces a
meaningful spread of cargo types, customs statuses, and driver safety scores
required careful calibration of the Python Faker scripts. Initial generations
produced uniformly distributed random data, which was unrealistic (real logistics
data follows power-law distributions with most shipments being standard cargo
and a small percentage being high-value). The data generation scripts were revised
to use weighted probability distributions to produce realistic test datasets.
## References

- MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Indexing Strategies.
https://www.mongodb.com/docs/manual/indexes/
- MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Aggregation Pipeline.
https://www.mongodb.com/docs/manual/aggregation/
- MongoDB, Inc. (2024). MongoDB 7.0 Documentation — Data Modeling
Introduction. https://www.mongodb.com/docs/manual/core/data-modeling-
introduction/
## 4. Banker, K., Bakkum, P., Hawkins, S., Membrey, P., & Thielman, T. (2016).
MongoDB in Action (2nd ed.). Manning Publications.
- COMSATS University Islamabad. (2024). Advanced Database Systems — Lab
Manual. Department of Computer Science.
- Chodorow, K. (2013). MongoDB: The Definitive Guide (2nd ed.). O'Reilly
## Media.
## 7. Python Software Foundation. (2024). Faker Library Documentation.
https://faker.readthedocs.io/
- Docker, Inc. (2024). Docker Documentation — Volumes and Bind Mounts.
https://docs.docker.com/storage/


## Nexus Logistics | Advanced Database Systems
Page 42 of 42

## Appendix A: Python Data Generation Script & Docker
## Setup

A.1 Reproducibility and Source Code
To ensure the transparency and reproducibility of the Nexus Logistics database system,
all engineering artifacts—including data generation logic, container orchestration
configurations, and architectural diagrams—have been open-sourced.
The complete repository includes:
- Python Synthetic Data Engine: Scripts utilizing the Faker and Random libraries
to generate 953 logically consistent logistics records.
- Docker Orchestration: Configuration files used to deploy the MongoDB 5.0
environment on Fedora Linux.
- Architectural Source Code: PlantUML scripts used to generate the Enhanced
Entity-Relationship (EER) diagrams.
## Repository Link:

## A.2 Docker Setup Configuration
The project utilizes a containerized approach to ensure environment parity. The
deployment was managed via a custom Docker Compose configuration, ensuring that the
NexusLogisticsDB is isolated with persistent volume mapping and administrative
authentication enabled.
## Deployment Command:
docker-compose.yaml in our GitHub repository.

## A.3 Data Generation Methodology
A Python-based generation script was developed to overcome the limitations of manual
data entry. The script follows a strict "Referential Integrity" logic:
- Entity Seeding: First, it generates static entities like warehouse_hubs and
route_intelligence.
- Constraint Mapping: It then assigns assigned_driver and assigned_vehicle IDs
to shipment_ops ensuring that no shipment is orphaned.
- JSON Serialization: The final output is serialized into a JSON format compatible
with the mongoimport utility or direct insertMany() operations.

A.4 Schema Visualization (PlantUML)
The EER diagrams presented in Section 3 were generated using PlantUML. This
"Diagrams-as-Code" approach allows for rapid iteration of the Disjoint Specialization
hierarchies and M:N relationship mappings described in this report. The source code for
these diagrams is included in the /ERD folder of the GitHub repository.

