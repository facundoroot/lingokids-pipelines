# Lingokids Data Engineering & Analytics Engineering Assessment

Welcome! This repository contains a complete data pipeline built with modern data engineering tools. This project demonstrates ETL/ELT best practices, including orchestration, transformation, testing, and incremental processing.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Exploring the Data](#exploring-the-data)
- [Project Structure](#project-structure)
- [Learn More](#learn-more)

---

## 🎯 Overview

This project implements a **medallion architecture** (bronze → silver → gold) data pipeline that:

1. **Ingests** raw JSON files from MinIO (S3-compatible object storage)
2. **Merges** small files into larger consolidated files (solving the "small file problem")
3. **Transforms** data through multiple layers using dbt
4. **Tests** data quality at every stage
5. **Serves** aggregated metrics for analytics

The repository is split into two parts:
- **Data Engineering (DE)**: The main pipeline handling event data ingestion and transformation
- **Analytics Engineering (AE)**: SQL-based analytics answering specific business questions

---

## 🛠️ Tech Stack

### **Dagster** - Data Orchestration
[Dagster](https://dagster.io/) is a modern data orchestrator that manages the entire pipeline. It provides:
- Asset-based development (treating data tables as first-class assets)
- Dependency management and lineage tracking
- Built-in testing and data quality checks
- A beautiful web UI for monitoring and debugging

### **dbt (data build tool)** - Data Transformation
[dbt](https://www.getdbt.com/) handles SQL-based transformations with:
- Version-controlled SQL models
- Incremental materialization strategies
- Built-in testing framework
- Documentation generation

### **DuckDB** - Analytics Database
[DuckDB](https://duckdb.org/) is an embedded analytical database that:
- Runs entirely in-process (no separate server needed)
- Provides extremely fast analytical queries
- Works directly with files (JSON, Parquet, CSV)
- Requires zero configuration

### **MinIO** - Object Storage
[MinIO](https://min.io/) is an S3-compatible object storage that:
- Simulates cloud storage locally
- Allows for realistic production-like development
- Runs in Docker for easy setup

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### 1. **uv** - Python Package Manager
[uv](https://docs.astral.sh/uv/) is an extremely fast Python package installer and resolver written in Rust. It's similar to pip but significantly faster and more reliable.

**Why uv?**
- 10-100x faster than pip
- Better dependency resolution
- Built-in virtual environment management
- Lock file support for reproducible builds

**Installation:**
Follow the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### 2. **Docker & Docker Compose**
Docker is required to run MinIO (our S3-compatible storage).

**Installation:**
Follow the [official Docker installation guide](https://docs.docker.com/get-docker/) for your operating system.

### 3. **DuckDB CLI** (Optional but recommended)
The DuckDB CLI allows you to explore the database interactively.

**Installation:**
Follow the [official DuckDB installation guide](https://duckdb.org/docs/installation/)

---

## 🚀 Getting Started

Follow these steps to set up and run the pipeline:

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd lingokids
```

### Step 2: Start MinIO (S3 Storage)

MinIO will simulate cloud object storage and automatically load the raw data files.

```bash
docker compose up -d
```

This command:
- Starts MinIO server on ports 9000 (API) and 9001 (Web UI)
- Automatically uploads raw JSON files to three buckets:
  - `raw-events` - User activity events
  - `raw-users` - User metadata
  - `raw-activities` - Activity catalog

**Check MinIO UI** (optional):
- Navigate to http://localhost:9001
- Login credentials:
  - Username: `lingokidsadmin`
  - Password: `lingokidsadmin`

### Step 3: Install Python Dependencies

Using **uv** (recommended):
```bash
uv sync
```

This creates a virtual environment in `.venv/` and installs all dependencies with locked versions.

Or using **pip**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Step 4: Activate Virtual Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 5: Install dbt Dependencies

dbt uses external packages (like `dbt-utils` for additional test macros):

```bash
cd dbt
dbt deps
cd ..
```

### Step 6: Start Dagster

Launch the Dagster development server:

```bash
dg dev
```

You should see:
```
Serving dagster-webserver on http://127.0.0.1:3000 in process [...]
```

Open your browser to **http://localhost:3000** to see the Dagster UI.

---

## 🎮 Running the Pipeline

Once Dagster is running, you can materialize (execute) the data pipeline through the UI.

### Understanding the Asset Groups

The pipeline is organized into **two groups**:

#### 1️⃣ **user_activity_pipeline** (Data Engineering)

This group contains the main ETL pipeline:

- **Bronze Layer** (Python assets):
  - `bronze_events` - Merges raw event files from MinIO
  - `bronze_users` - Merges raw user files from MinIO
  - `bronze_activities` - Merges raw activity files from MinIO

- **Silver Layer** (dbt staging views):
  - `stg_events` - Cleaned and typed event data
  - `stg_users` - Cleaned user metadata
  - `stg_activities` - Cleaned activity catalog

- **Silver Layer** (dbt intermediate tables):
  - `intermediate_activity_events_enriched` - Events joined with user and activity metadata

- **Gold Layer** (dbt mart tables):
  - `activity_engagement_metrics` - Daily aggregated KPIs by country, OS, app version, etc.

#### 2️⃣ **analytics_exercises** (Analytics Engineering)

This group contains the analytics questions:

- **Seeds** (CSV data):
  - `activities` - Activity reference data
  - `activity_events` - Event log
  - `subscriptions` - Subscription events

- **Analytics Models** (dbt views):
  - `q1_completion_rate` - Completion rate by theme
  - `q2_price_tier_engagement` - Engagement metrics by price tier
  - `q3_subscription_impact` - Activity behavior before/after subscription

### How to Run

#### Option 1: Run the Entire DE Pipeline

1. In the Dagster UI, click on the **search/filter bar** at the top
2. Type: `group:user_activity_pipeline`
3. Click **"Materialize all"** button
4. Watch as Dagster executes the pipeline in dependency order

This will:
- Download and merge files from MinIO → bronze layer
- Transform raw data → staging views
- Enrich events → intermediate tables
- Aggregate metrics → final mart table

#### Option 2: Run the AE Exercises

1. In the search/filter bar, type: `group:analytics_exercises`
2. Click **"Materialize all"**
3. This will load the seeds and run the analytics queries

#### Option 3: Run Individual Assets

You can also click on any individual asset in the graph view and click **"Materialize"** to run just that asset and its dependencies.

### Monitoring Execution

- **Real-time logs**: Click on any running asset to see live logs
- **Asset checks**: After materialization, dbt tests run automatically
- **Test results**: Click on the "Checks" tab to see test results (green = pass, red = fail)

---

## 🔍 Exploring the Data

After running the pipeline, you can explore the data using DuckDB.

### What is DuckDB?

DuckDB is an **embedded analytical database** - think of it as "SQLite for analytics". It:
- Runs entirely in-process (no server to manage)
- Stores data in a single file (`lingokids.duckdb`)
- Provides blazing-fast analytical queries
- Supports rich SQL features (window functions, CTEs, JSON parsing, etc.)

### Locating the Database

The DuckDB database is located at:
```
dbt/warehouse/lingokids.duckdb
```

### Opening the Database

Navigate to the dbt directory and open DuckDB:

```bash
cd dbt/warehouse
duckdb lingokids.duckdb
```

You'll see the DuckDB prompt:
```
v1.x.x
Enter ".help" for usage hints.
D
```

### Useful Commands

#### List all tables and views:
```sql
SHOW TABLES;
```

#### Describe a table schema:
```sql
DESCRIBE main.activity_engagement_metrics;
```

#### View table row count:
```sql
SELECT COUNT(*) FROM main.activity_engagement_metrics;
```

### Example Queries

You can run queries just like you would with any other SQL database. For example, to view the aggregated engagement metrics:

```sql
SELECT * FROM main.activity_engagement_metrics LIMIT 10;
```

To see the analytics exercise results:

```sql
-- Q1: Completion rate by theme
SELECT * FROM main.q1_completion_rate;

-- Q2: Price tier engagement
SELECT * FROM main.q2_price_tier_engagement;

-- Q3: Subscription impact
SELECT * FROM main.q3_subscription_impact;
```

### Exiting DuckDB
```sql
.quit
```
Or press `Ctrl+D`

---

## 📊 Data Quality & Testing

This project includes comprehensive data quality tests using dbt.

### Where to View Tests

In the Dagster UI:
1. Navigate to any asset (e.g., `activity_engagement_metrics`)
2. Click on the **"Checks"** tab
3. You'll see all tests that run on that asset

### Types of Tests

#### 1. **Schema Tests** (defined in `schema.yml` files)
- `not_null` - Ensures critical columns have no null values
- `unique` - Ensures columns contain unique values
- `accepted_range` - Validates numeric columns are within expected ranges
- `unique_combination_of_columns` - Ensures composite keys are unique

#### 2. **Model-Level Tests**
- Uniqueness of the grain (date + country + OS + version + subscription + activity type)
- Completion rate bounds (0-1 for intermediate, 0-100 for AE questions)

### Running Tests Manually

You can also run dbt tests from the command line:

```bash
cd dbt

# Run all tests
dbt test

# Run tests for a specific model
dbt test --select activity_engagement_metrics

# Run tests for a specific group
dbt test --select user_activity_pipeline
```

Test results are stored in:
```
dbt/target/compiled/lingokids/models/.../[test_name].sql
```

---

## 📁 Project Structure

```
lingokids/
├── dbt/                                    # dbt project
│   ├── models/
│   │   ├── staging/                        # Silver layer - cleaned data
│   │   │   ├── stg_events.sql
│   │   │   ├── stg_users.sql
│   │   │   ├── stg_activities.sql
│   │   │   └── sources.yml                 # Bronze source definitions
│   │   ├── intermediate/                   # Silver layer - enriched data
│   │   │   ├── intermediate_activity_events_enriched.sql
│   │   │   └── schema.yml
│   │   ├── marts/                          # Gold layer - aggregated metrics
│   │   │   ├── activity_engagement_metrics.sql
│   │   │   └── schema.yml
│   │   ├── ae/                             # Analytics exercises
│   │   │   ├── q1_completion_rate.sql
│   │   │   ├── q2_price_tier_engagement.sql
│   │   │   ├── q3_subscription_impact.sql
│   │   │   └── schema.yml
│   │   └── groups.yml                      # Group definitions
│   ├── seeds/                              # CSV reference data for AE
│   │   ├── activities.csv
│   │   ├── activity_events.csv
│   │   └── subscriptions.csv
│   ├── data/
│   │   └── bronze/                         # Merged files from Dagster
│   │       ├── bronze_events.json
│   │       ├── bronze_users.json
│   │       └── bronze_activities.json
│   ├── warehouse/
│   │   └── lingokids.duckdb               # DuckDB database file
│   ├── dbt_project.yml
│   └── packages.yml                        # dbt dependencies
│
├── src/lingokids/
│   ├── defs/
│   │   ├── bronze/                         # Bronze layer assets
│   │   │   ├── __init__.py
│   │   │   └── assets.py                   # MinIO → local merge logic
│   │   └── dbt_ingest/
│   │       └── defs.yaml                   # dbt component config
│   └── definitions.py                      # Main Dagster definitions
│
├── scripts/
│   └── init_minio.py                       # MinIO initialization script
│
├── docker-compose.yml                      # MinIO service definition
├── Dockerfile.minio-init                   # MinIO setup container
├── pyproject.toml                          # Python dependencies
└── README.md                               # You are here!
```

### Key Files Explained

- **`bronze/assets.py`**: Python code that downloads files from MinIO buckets and merges them into single files
- **`stg_*.sql`**: Staging models that parse JSON and apply initial transformations
- **`intermediate_*.sql`**: Models that join multiple sources and add business logic
- **`marts/*.sql`**: Final aggregated tables optimized for analytics
- **`dbt_project.yml`**: dbt configuration including materializations and groups
- **`sources.yml`**: Defines bronze layer as sources for lineage tracking
- **`schema.yml`**: Contains test definitions and documentation

---

## 🧩 Key Concepts Demonstrated

### 1. **Small File Problem Solution**
Instead of reading thousands of tiny JSON files (slow!), the bronze layer assets merge them into three consolidated files. This dramatically improves read performance.

### 2. **Incremental Processing**
The intermediate and mart models use incremental materialization:
- First run: Load all historical data
- Subsequent runs: Only process new/changed data
- Strategy: `delete+insert` to handle late-arriving data

### 3. **Data Lineage**
Dagster tracks dependencies between assets:
- Bronze assets → dbt staging models (via temporal dependencies)
- Staging → intermediate → marts (via dbt refs)

### 4. **Separation of Concerns**
- **Dagster**: Orchestration, file handling, dependency management
- **dbt**: SQL transformations, testing, documentation
- **DuckDB**: High-performance analytics queries

### 5. **Medallion Architecture**
- **Bronze**: Raw data, minimal processing
- **Silver**: Cleaned, typed, deduplicated
- **Gold**: Aggregated, business-ready metrics

---

## 🧪 Development Workflow

### Making Changes to dbt Models

1. Edit SQL files in `dbt/models/`
2. Run the model:
   ```bash
   dbt run --select your_model_name
   ```
3. Test the model:
   ```bash
   dbt test --select your_model_name
   ```
4. Or use Dagster UI to materialize the asset

### Making Changes to Python Assets

1. Edit `src/lingokids/defs/bronze/assets.py`
2. Dagster will auto-reload the code
3. Materialize the asset in the UI

### Adding New Tests

Add tests in the relevant `schema.yml` file:
```yaml
models:
  - name: your_model
    columns:
      - name: your_column
        tests:
          - not_null
          - unique
```

---

## 🛑 Troubleshooting

### MinIO containers not starting
```bash
docker compose down
docker compose up -d
```

### DuckDB file locked
Close any open DuckDB sessions. Only one process can write at a time.

### dbt command not found
Make sure you're in the activated virtual environment:
```bash
source .venv/bin/activate
```

### Dagster can't find assets
Restart the Dagster development server:
```bash
# Stop with Ctrl+C, then:
dg dev
```

### Tests failing
Check test details in Dagster UI or run:
```bash
cd dbt
dbt test --select failing_model --store-failures
```

---

## 📚 Learn More

### Dagster
- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)

### dbt
- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [dbt Discourse Community](https://discourse.getdbt.com/)

### DuckDB
- [DuckDB Documentation](https://duckdb.org/docs/)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)

### MinIO
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)

---

## 🎓 Assessment Notes

This project was built as part of the Lingokids technical assessment to demonstrate:

- ✅ Modern data stack proficiency (Dagster, dbt, DuckDB)
- ✅ ETL/ELT pipeline design and implementation
- ✅ Data quality testing and validation
- ✅ Incremental processing strategies
- ✅ SQL and Python skills
- ✅ Documentation and code organization
- ✅ Reproducible development environments

---

## 🏭 Production Considerations

While this project demonstrates a working local pipeline, moving to production would require several enhancements. Below is a phased approach based on scale, team size, and business requirements.

### Immediate Production Changes (Week 1)

#### 1. Orchestration & Scheduling
**Current State**: Manual materialization via UI
**Production Need**: Automated scheduling

- **Dagster Schedules**: Define schedules for different asset groups
  ```python
  from dagster import ScheduleDefinition, AssetSelection

  daily_pipeline = ScheduleDefinition(
      name="daily_user_activity_pipeline",
      cron_schedule="0 2 * * *",  # 2 AM daily
      target=AssetSelection.groups("user_activity_pipeline")
  )
  ```
- **Sensors**: Event-driven execution when new files land in S3
  ```python
  from dagster import sensor, RunRequest

  @sensor(target=...)
  def s3_file_sensor(context):
      # Check for new files in S3, trigger runs
  ```
- **Separate SLAs**: Critical metrics run hourly, reports run daily

#### 2. Observability & Monitoring
**Current State**: Local logs only
**Production Need**: Centralized monitoring and alerting

- **Logging**:
  - CloudWatch Logs for centralized log aggregation
  - Structured logging with JSON format for parsing
  - DataDog or New Relic for metrics and dashboards

- **Alerting**:
  - Dagster's built-in Slack/email alerts for failed runs
  - PagerDuty integration for critical failures
  - SLA monitoring (alert if pipeline takes >2 hours)

- **Dashboards**:
  - Dagster asset materialization trends
  - dbt test failure rates over time
  - Data freshness metrics

#### 3. Security & Secrets Management
**Current State**: Hardcoded credentials in docker-compose
**Production Need**: Secure credential management

- **AWS Secrets Manager** or **Parameter Store** for credentials
- **IAM Roles** instead of access keys (ECS task roles)
- **Encryption**: S3 server-side encryption (SSE-S3 or SSE-KMS)
- **Network Security**: VPC with private subnets, security groups

---

### Short-term Improvements (Month 1-3)

#### 4. Infrastructure as Code & CI/CD

**Repository Structure**:
```
lingokids-platform/
├── dagster-app/           # This repo - pipeline code
│   ├── src/
│   ├── dbt/
│   └── Dockerfile
└── infrastructure/        # Separate IaC repo
    ├── terraform/
    │   ├── modules/
    │   │   ├── ecs/
    │   │   ├── s3/
    │   │   ├── rds/
    │   │   └── networking/
    │   └── environments/
    │       ├── dev/
    │       ├── staging/
    │       └── prod/
    └── README.md
```

**Deployment Architecture (ECS)**:
```
┌─────────────────────────────────────────────┐
│ AWS ECS Cluster                             │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │ dagster-webserver│  │ dagster-daemon  │ │
│  │  (Fargate Task)  │  │ (Fargate Task)  │ │
│  └──────────────────┘  └─────────────────┘ │
│                                             │
│  ┌──────────────────┐                      │
│  │dagster-user-code │                      │
│  │  (Fargate Task)  │                      │
│  └──────────────────┘                      │
└─────────────────────────────────────────────┘
         │                    │
         ↓                    ↓
    ┌────────┐          ┌─────────┐
    │  RDS   │          │   S3    │
    │ (Meta) │          │ (Data)  │
    └────────┘          └─────────┘
```

**Container Images**:
- `dagster-webserver`: Serves UI on port 3000
- `dagster-daemon`: Runs schedules, sensors, run queue
- `dagster-user-code`: Contains your assets (this repo)

**CI/CD Pipeline** (GitHub Actions):
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    - Run dbt test
    - Run Python unit tests
    - Lint SQL (sqlfluff)

  build:
    - Build Docker images
    - Tag with git SHA
    - Push to ECR

  deploy:
    - Update ECS task definitions via Terraform
    - Blue/green deployment
    - Run smoke tests
```

**Infrastructure Components** (Terraform):
- **Networking**: VPC, subnets (public/private), NAT gateway, security groups
- **Compute**: ECS cluster, Fargate task definitions, auto-scaling
- **Storage**: S3 buckets (raw/bronze/silver/gold), lifecycle policies
- **Database**: RDS PostgreSQL for Dagster metadata (multi-AZ for HA)
- **Monitoring**: CloudWatch dashboards, alarms, SNS topics
- **IAM**: Roles for ECS tasks, S3 access policies

**Environment Strategy**:
- **Dev**: Smaller instances, single AZ, sample data
- **Staging**: Production-like, full data, integration tests
- **Prod**: Multi-AZ, auto-scaling, full backups

#### 5. Data Quality & Governance

**Enhanced Testing**:
- **Great Expectations** or **Soda** for advanced data quality
  - Distribution checks (outlier detection)
  - Schema evolution monitoring
  - Row count anomaly detection

- **dbt Exposures**: Document downstream BI dashboards
- **Data Contracts**: Define SLAs between data producers/consumers

**Lineage & Documentation**:
- Auto-generate data catalogs (dbt docs, DataHub, Atlan)
- Column-level lineage for impact analysis
- Business glossary for metric definitions

---

### Long-term Considerations (6+ months)

#### 6. Data Warehouse Strategy

The choice between DuckDB and cloud warehouses depends on scale:

**Current Setup (DuckDB)**:
- ✅ Great for: <100GB data, <5 users, fast iteration
- ✅ Zero cost for compute
- ❌ Limited concurrency, single-node bottleneck

**Option A: Export to Cloud Warehouse**
```
DuckDB (transformations) → Parquet → Snowflake/BigQuery
```
- **When**: >100GB data, >10 concurrent users
- **Pro**: Leverage DuckDB speed for complex SQL, use warehouse for serving
- **Con**: Extra data movement step

**Option B: Full Warehouse Migration**
```
S3 (raw data) → dbt in Snowflake/BigQuery → marts
```
- **When**: Enterprise scale, large team, need governance features
- **Pro**: Simpler architecture, built-in concurrency, time travel, sharing
- **Con**: Higher costs ($), more rigid

**Option C: MotherDuck (Cloud DuckDB)**
```
DuckDB API → MotherDuck (managed) → S3
```
- **When**: Want DuckDB benefits with cloud scalability
- **Pro**: Familiar DuckDB syntax, serverless, cheap
- **Con**: Newer product, smaller ecosystem

**Decision Criteria**:
| Factor | Keep DuckDB | Migrate to Warehouse |
|--------|-------------|----------------------|
| Data Volume | <500GB | >1TB |
| Query Users | <10 | >50 |
| Budget | Minimal | $1k+/month |
| Team Size | 1-5 | 10+ |
| Compliance Needs | Low | High (SOC2, HIPAA) |

#### 7. Small File Problem - Scale Solutions

**Current Approach**: Merge in Dagster (Python)
**Works for**: Thousands of small files, <100GB/day

**At Scale (millions of events/day)**:

**Option A: Stream Processing**
```
Events → Kafka/Kinesis → Flink/Spark Streaming → S3 (micro-batches)
```
- **When**: Need real-time or sub-hourly updates
- **Pro**: Low latency, natural deduplication
- **Con**: Complex infrastructure, higher costs

**Option B: AWS Glue (Serverless Spark)**
```
S3 (small files) → Glue Job → S3 (partitioned Parquet)
```
- **When**: Daily batch, large volumes, unpredictable load
- **Pro**: Serverless, auto-scaling, no cluster management
- **Con**: Cold start delays, less control than EMR

**Option C: Fivetran/Airbyte**
```
Data Sources → Managed Connector → Warehouse
```
- **When**: Many SaaS sources, want to focus on transformations
- **Pro**: Pre-built connectors, handles API pagination, retries
- **Con**: Can be expensive, less customization

**Spark vs Current Approach**:
- **Use Spark when**: Individual files >1GB AND total >1TB/day
- **Avoid Spark when**: Files <10MB each (overhead > benefit)
- **Middle ground**: DuckDB can process 100GB+ efficiently on single node

**Partitioning Strategy** (critical at scale):
```
s3://bucket/events/
  └── year=2025/
      └── month=01/
          └── day=06/
              └── hour=14/
                  └── events.parquet  (100MB-1GB each)
```

#### 8. Alternative Architectures

**Kubernetes (EKS) vs ECS**:
- **Use EKS when**: >20 microservices, multi-cloud, need advanced orchestration
- **Use ECS when**: AWS-only, simpler setup, smaller team
- **Dagster Cloud**: Skip infrastructure entirely, managed service ($)

**Dagster Deployment Options**:
| Option | Complexity | Cost | Scale |
|--------|------------|------|-------|
| Local (current) | Low | $0 | Dev only |
| ECS Fargate | Medium | $$$ | 100s of assets |
| EKS | High | $$ | 1000s of assets |
| Dagster Cloud | Low | $$$$ | Any scale |

---

### Cost Optimization Strategies

1. **Compute**:
   - Use Spot instances for non-critical jobs (70% cheaper)
   - Right-size ECS tasks (don't over-provision)
   - Schedule non-urgent jobs during off-peak hours

2. **Storage**:
   - S3 lifecycle policies: Standard → Infrequent Access → Glacier
   - Compress files (Parquet with Snappy)
   - Delete temporary/staging data after 7 days

3. **Warehouse**:
   - Use clustering keys (Snowflake) or partitioning (BigQuery)
   - Materialize frequently-queried aggregations
   - Set query timeouts to prevent runaway costs
   - Monitor with cost dashboards

4. **Monitoring**:
   - AWS Cost Explorer with daily alerts
   - Tag all resources for cost allocation
   - Set budgets with automatic alerts

---

### Disaster Recovery & Business Continuity

1. **Backup Strategy**:
   - **S3 raw data**: Cross-region replication (critical data)
   - **RDS metadata**: Automated daily snapshots, 30-day retention
   - **Code**: Git (already versioned)
   - **Infrastructure**: Terraform state in S3 with versioning

2. **Recovery Procedures**:
   - **RTO (Recovery Time Objective)**: 4 hours to restore service
   - **RPO (Recovery Point Objective)**: <24 hours of data loss
   - **Runbook**: Documented steps in Confluence/Notion
   - **DR Drills**: Quarterly test restores

3. **High Availability**:
   - Multi-AZ RDS deployment
   - ECS tasks spread across availability zones
   - S3 (99.999999999% durability by default)

---

### Scalability Roadmap

**Phase 1: Current → 10x Scale**
- Same architecture, just tune configurations
- Add horizontal scaling for user-code containers
- Optimize dbt models (incremental, partitioning)

**Phase 2: 10x → 100x Scale**
- Migrate to cloud warehouse (Snowflake/BigQuery)
- Implement stream processing for hot path
- Consider data lakehouse (Delta Lake, Iceberg)

**Phase 3: 100x+ Scale**
- Multi-region deployment
- Dedicated data platform team
- Real-time + batch lambda architecture

**Key Metrics to Monitor**:
- Pipeline runtime (alert if >2x baseline)
- Data freshness (SLAs per table)
- Error rates (failed tests, runs)
- Cost per GB processed

---

### Technology Selection Framework

When evaluating production changes, consider:

1. **Data Volume**:
   - <100GB/day → Current setup scales fine
   - 100GB-1TB/day → Add warehouse or MotherDuck
   - >1TB/day → Distributed compute (Spark) + warehouse

2. **Latency Requirements**:
   - Daily updates → Batch (current approach)
   - Hourly updates → Optimized batch + incremental
   - Minutes/real-time → Stream processing (Kafka + Flink)

3. **Team Size**:
   - 1-5 people → Keep simple, minimize ops overhead
   - 5-20 people → Invest in platform, separate dev/prod
   - 20+ people → Data platform team, multi-tenant

4. **Budget**:
   - <$1k/month → DuckDB + ECS
   - $1k-$10k/month → Cloud warehouse + managed services
   - $10k+/month → Enterprise warehouse + real-time

**The right architecture balances cost, complexity, and capabilities based on actual constraints - not just what's technically possible.**

---

Thank you for reviewing! 🚀
