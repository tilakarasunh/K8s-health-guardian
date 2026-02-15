# 🏥 AKS Health Guardian

A comprehensive Kubernetes cluster health monitoring and analysis system powered by Azure OpenAI (GPT-4o-Mini). Health Guardian automatically monitors your AKS cluster, analyzes health metrics using AI, and delivers actionable insights through intelligent HTML reports.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Workflow](#workflow)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup & Configuration](#setup--configuration)
- [Deployment](#deployment)
- [Usage](#usage)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Contributing](#contributing)

## 📖 Overview

Health Guardian is an automated AKS (Azure Kubernetes Service) health checking system that runs as a Kubernetes CronJob. It performs comprehensive cluster analysis and leverages Azure OpenAI to provide intelligent insights and recommendations for maintaining optimal cluster health.

**Key Characteristics:**
- ✅ Fully automated daily health checks (configurable schedule)
- ✅ AI-powered analysis using Azure OpenAI GPT-4o-Mini
- ✅ Comprehensive cluster metrics collection
- ✅ Intelligent health scoring (0-100)
- ✅ Predictive analytics for potential issues
- ✅ Actionable kubectl command recommendations
- ✅ Beautiful HTML email reports
- ✅ Graceful fallback to rule-based analysis if AI unavailable

## ✨ Features

### Comprehensive Monitoring
- **Pod Status Tracking**: Monitor pod states (Running, Pending, Failed, Unknown)
- **Node Metrics**: Track node capacity, allocatable resources, and conditions
- **Event Monitoring**: Analyze cluster events with severity filtering (Warning, Normal)
- **Resource Usage**: Monitor CPU and memory consumption across the cluster
- **Failed Pod Analysis**: Detailed diagnostics of failed or problematic pods

### AI-Powered Intelligence
- Analyzes cluster health using Azure OpenAI GPT-4o-Mini model
- Generates context-aware insights based on real-time metrics
- Identifies critical, warning, and informational issues
- Predicts potential problems in the next 24-48 hours
- Provides specific, actionable recommendations with kubectl commands

### Professional Reporting
- Generates beautiful HTML reports styled with modern UI
- Includes executive summary with actionable insights
- Health score visualization with color-coded severity indicators
- Issue breakdown with severity levels
- Predictive problem analysis
- Complete resource usage statistics
- Recent event timeline
- Automated email delivery via Azure Logic Apps

### Clustering Awareness
- Works seamlessly in-cluster or from local machines
- Automatic Kubernetes configuration detection
- Metrics API integration for resource usage
- Support for multi-namespace environments
- Complete RBAC implementation for security

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    AKS Cluster                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Health Guardian CronJob (Daily 9 AM UTC)     │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ KubernetesMonitor Module                        │ │   │
│  │  │ - Collects pod status                           │ │   │
│  │  │ - Gathers node metrics                          │ │   │
│  │  │ - Fetches resource usage from Metrics API       │ │   │
│  │  │ - Retrieves cluster events (24h window)         │ │   │
│  │  │ - Identifies failed pods with diagnostics       │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                        ↓                              │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ AIAnalyzer Module                               │ │   │
│  │  │ - Prepares contextualized cluster data          │ │   │
│  │  │ - Sends to Azure OpenAI REST API                │ │   │
│  │  │ - Parses JSON health analysis response          │ │   │
│  │  │ - Fallback to rule-based analysis on failure    │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                        ↓                              │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ ReportGenerator Module                          │ │   │
│  │  │ - Formats data as polished HTML report          │ │   │
│  │  │ - Generates metric visualizations              │ │   │
│  │  │ - Compiles issue & recommendation summaries     │ │   │
│  │  │ - Delivers via Azure Logic Apps webhook         │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                        ↓                                      │
│         ┌─────────────────────────────────────────┐          │
│         │  Azure Key Vault                        │          │
│         │  - Azure OpenAI credentials             │          │
│         │  - Logic Apps webhook URL               │          │
│         └─────────────────────────────────────────┘          │
│                        ↓                                      │
└─────────────────────────────────────────────────────────────┘
                         ↓
      ┌──────────────────────────────────────┐
      │    Azure OpenAI (GPT-4o-Mini)        │
      │    - Analyzes cluster health         │
      │    - Generates JSON insights         │
      └──────────────────────────────────────┘
                         ↓
      ┌──────────────────────────────────────┐
      │    Azure Logic Apps                  │
      │    - Receives webhook POST           │
      │    - Sends HTML email to recipients  │
      └──────────────────────────────────────┘
```

### Kubernetes Resources

| Resource | Purpose |
|----------|---------|
| **CronJob** | Orchestrates daily health checks at 9 AM UTC |
| **ServiceAccount** | Provides container identity for cluster access |
| **ClusterRole** | Defines permissions for pod/node/event access |
| **ClusterRoleBinding** | Binds ServiceAccount to ClusterRole |
| **ConfigMap** | Stores non-sensitive configuration (email recipients) |
| **Secret** | Stores sensitive data (API keys, webhook URLs) |

## 🔄 Workflow

### Daily Execution Flow

```
[9:00 AM UTC]
     ↓
[CronJob triggers]
     ↓
[main.py initializes components]
     ├─ KubernetesMonitor loads cluster config
     ├─ AIAnalyzer initializes Azure OpenAI client
     └─ ReportGenerator prepares formatting engine
     ↓
[Data Collection Phase]
     ├─ get_pod_status() → Pod health snapshot
     ├─ get_node_metrics() → Node capacity & conditions
     ├─ get_resource_usage() → CPU/Memory metrics via Metrics API
     ├─ get_recent_events(24h) → Cluster events with warnings
     └─ get_failed_pods() → Detailed failed pod diagnostics
     ↓
[AI Analysis Phase]
     ├─ _prepare_context() → Summarize cluster data
     ├─ POST to Azure OpenAI REST API with prompt
     ├─ Parse JSON response with:
     │   ├─ health_score (0-100)
     │   ├─ summary (executive assessment)
     │   ├─ issues (with severity levels)
     │   ├─ predictions (24-48h forecast)
     │   └─ recommendations (with kubectl commands)
     └─ Fallback to rule-based analysis if API fails
     ↓
[Report Generation Phase]
     ├─ create_report() → Generate styled HTML
     ├─ Color-code health scores
     ├─ Format issues by severity
     ├─ Include actionable recommendations
     ├─ Compile resource usage tables
     └─ Append recent event timeline
     ↓
[Delivery Phase]
     ├─ POST to Azure Logic Apps webhook
     ├─ Logic App sends HTML as email
     └─ Email delivered to configured recipients
     ↓
[Completion & Logging]
     └─ Log all phases to stdout (captured in pod logs)
```

### Data Flow

1. **Collection**: KubernetesMonitor queries the Kubernetes API
2. **Context Preparation**: Cluster data is summarized for AI analysis
3. **AI Analysis**: Contextualized data sent to Azure OpenAI (REST API)
4. **Report Creation**: Analysis results formatted as professional HTML
5. **Distribution**: Report delivered via email through Logic Apps

## 📋 Prerequisites

### Azure Services Required
- **Azure Kubernetes Service (AKS)** cluster running Kubernetes 1.24+
- **Azure OpenAI Service** with GPT-4o-Mini deployment
  - Model: `gpt-4o-mini`
  - API Version: `2024-02-15-preview`
  - Sufficient quota for regular analysis requests
- **Azure Key Vault** for secure credential storage
- **Azure Logic Apps** for email delivery (or alternative email service)
- **Container Registry** (Azure Container Registry recommended)

### Local Prerequisites (for development/testing)
- Python 3.11+
- Docker Desktop (for local image building)
- `kubectl` configured with access to your AKS cluster
- Azure CLI (`az` command-line tool)

### Cluster Requirements
- **Metrics Server** installed (for resource usage API)
  ```bash
  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
  ```
- Appropriate RBAC permissions for system:masters or cluster-admin
- Network connectivity to Azure OpenAI endpoint (HTTPS 443)
- Network connectivity to Azure Logic Apps webhook URL (HTTPS 443)

## 📁 Project Structure

```
health-guardian/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Container image definition
│
├── app/                               # Application source code
│   ├── main.py                        # Entry point & orchestration
│   ├── k8s_monitor.py                 # Kubernetes API interactions
│   ├── ai_analyzer.py                 # Azure OpenAI integration
│   └── report_generator.py            # HTML report & email delivery
│
└── k8s/                               # Kubernetes manifests
    ├── cronjob.yaml                   # CronJob resource definition
    ├── rbac.yaml                      # ServiceAccount, ClusterRole, ClusterRoleBinding
    ├── cm.yaml                        # ConfigMap for non-sensitive config
    └── deployment.yaml                # Namespace & other resources (optional)
```

## 🔧 Setup & Configuration

### Step 1: Prepare Azure Resources

#### 1.1 Create or Use Existing Azure OpenAI Deployment

```bash
# Login to Azure
az login

# Create Azure OpenAI service (if needed)
az cognitiveservices account create \
  --name health-guardian-openai \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --kind OpenAI \
  --sku s0 \
  --location eastus

# Create gpt-4o-mini deployment
az cognitiveservices account deployment create \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --name health-guardian-openai \
  --deployment-name gpt-4o-mini \
  --model name=gpt-4o-mini \
  --model version=1 \
  --model-format OpenAI

# Get endpoint and API key
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --name health-guardian-openai \
  --query properties.endpoint -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --name health-guardian-openai \
  --query key1 -o tsv)
```

#### 1.2 Create Azure Logic Apps Webhook

```bash
# Create a Logic App with HTTP trigger for email functionality
# In Azure Portal:
# 1. Create Logic App
# 2. Add "When a HTTP request is received" trigger
# 3. Copy the HTTP POST URL
# 4. Add "Send an email (V2)" action using Office 365 Outlook connector

LOGIC_APP_WEBHOOK_URL="https://prod-xx.logic.azure.com/..."
```

#### 1.3 Create Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name health-guardian-kv \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --enable-rbac-authorization

# Store secrets
az keyvault secret set \
  --vault-name health-guardian-kv \
  --name azure-openai-endpoint \
  --value "$OPENAI_ENDPOINT"

az keyvault secret set \
  --vault-name health-guardian-kv \
  --name azure-openai-api-key \
  --value "$OPENAI_KEY"

az keyvault secret set \
  --vault-name health-guardian-kv \
  --name logic-app-webhook-url \
  --value "$LOGIC_APP_WEBHOOK_URL"
```

### Step 2: Build & Push Container Image

```bash
# Login to container registry
az acr login --name <YOUR_ACR_NAME>

# Build image
docker build -t health-guardian:1.4 .

# Tag for registry
docker tag health-guardian:1.4 <YOUR_ACR_NAME>.azurecr.io/health-guardian:1.4

# Push to registry
docker push <YOUR_ACR_NAME>.azurecr.io/health-guardian:1.4
```

### Step 3: Configure Kubernetes Secrets & ConfigMaps

#### 3.1 Create Secret for Sensitive Data

```bash
kubectl create secret generic health-guardian-secrets \
  --from-literal=AZURE_OPENAI_ENDPOINT="<YOUR_ENDPOINT>" \
  --from-literal=AZURE_OPENAI_API_KEY="<YOUR_API_KEY>" \
  --from-literal=LOGIC_APP_WEBHOOK_URL="<YOUR_WEBHOOK_URL>" \
  -n default
```

#### 3.2 Update ConfigMap with Your Email

Edit `k8s/cm.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-guardian-config
  namespace: default
data:
  REPORT_RECIPIENTS: "your-email@example.com,team@example.com"
  LOG_LEVEL: "INFO"
```

Then apply:

```bash
kubectl apply -f k8s/cm.yaml
```

### Step 4: Update CronJob Image Reference

Edit `k8s/cronjob.yaml` to use your container registry:

```yaml
image: <YOUR_ACR_NAME>.azurecr.io/health-guardian:1.4
```

## 🚀 Deployment

### Deploy to Kubernetes Cluster

```bash
# 1. Apply RBAC configuration
kubectl apply -f k8s/rbac.yaml

# 2. Apply ConfigMap
kubectl apply -f k8s/cm.yaml

# 3. Create secret (done in setup step 3.1)

# 4. Apply CronJob
kubectl apply -f k8s/cronjob.yaml

# Verify deployment
kubectl get sa -n default | grep health-guardian
kubectl get clusterrole | grep health-guardian
kubectl get cronjob -n default | grep health-guardian
```

### Verify Status

```bash
# Check if CronJob is created
kubectl describe cronjob health-guardian -n default

# Check job history
kubectl get jobs -n default | grep health-guardian

# View pod logs from last run
kubectl logs -n default -l app=health-guardian --tail=100
```

### Manual Trigger (Testing)

Create a one-off Job for testing:

```bash
# Trigger immediate job run
kubectl create job --from=cronjob/health-guardian health-guardian-manual -n default

# Monitor execution
kubectl logs -n default -l app=health-guardian -f

# Clean up test job
kubectl delete job health-guardian-manual -n default
```

## 💻 Usage

### Local Development

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Set Environment Variables

```bash
# Linux/macOS
export AZURE_OPENAI_ENDPOINT="https://your-service.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export LOGIC_APP_WEBHOOK_URL="https://prod-xx.logic.azure.com/..."
export REPORT_RECIPIENTS="your-email@example.com"

# Windows PowerShell
$env:AZURE_OPENAI_ENDPOINT = "https://your-service.openai.azure.com"
$env:AZURE_OPENAI_API_KEY = "your-api-key"
$env:LOGIC_APP_WEBHOOK_URL = "https://prod-xx.logic.azure.com/..."
$env:REPORT_RECIPIENTS = "your-email@example.com"
```

#### 3. Run the Application

```bash
python app/main.py
```

Expected output:
```
INFO:__main__:Starting AKS Health Guardian...
INFO:__main__:Collecting cluster metrics...
INFO:__main__:Analyzing data with Azure OpenAI...
INFO:__main__:Generating health report...
INFO:__main__:Sending report via email...
INFO:__main__:Health check completed successfully!
```

### Module Overview

#### KubernetesMonitor (`app/k8s_monitor.py`)

Collects comprehensive cluster metrics:

```python
monitor = KubernetesMonitor()

# Pod status across all namespaces
pods = monitor.get_pod_status()
# Returns: {total, running, pending, failed, unknown, details[]}

# Node metrics
nodes = monitor.get_node_metrics()
# Returns: [{name, cpu_capacity, memory_capacity, conditions}]

# Resource usage from Metrics API
usage = monitor.get_resource_usage()
# Returns: {total_cpu_usage, total_memory_usage, high_cpu_pods[], high_memory_pods[]}

# Cluster events from last 24 hours
events = monitor.get_recent_events(hours=24)
# Returns: [events] sorted by timestamp

# Failed/problematic pods
failed = monitor.get_failed_pods()
# Returns: [{name, namespace, status, reason, container_statuses[]}]
```

#### AIAnalyzer (`app/ai_analyzer.py`)

Leverages Azure OpenAI for intelligent analysis:

```python
analyzer = AIAnalyzer(endpoint, api_key)

# Analyze cluster health using GPT-4o-Mini
analysis = analyzer.analyze_cluster_health(cluster_data)
# Returns: {
#   health_score: 0-100,
#   summary: "...",
#   issues: [{severity, title, description}],
#   predictions: [{timeframe, issue, probability}],
#   recommendations: [{priority, action, command}]
# }
```

**Fallback Behavior**: If Azure OpenAI is unavailable, the analyzer falls back to rule-based analysis using configured thresholds:
- Detects failed pods, high CPU/memory usage, pending pods
- Generates basic recommendations based on detected issues

#### ReportGenerator (`app/report_generator.py`)

Generates professional HTML reports and delivers via email:

```python
report_gen = ReportGenerator()

# Create styled HTML report
report = report_gen.create_report(cluster_data, analysis)

# Send via Logic Apps webhook
report_gen.send_email(report, recipients=['user@example.com'])
```

## 📊 Report Contents

The generated HTML report includes:

| Section | Details |
|---------|---------|
| **Health Score** | 0-100 score with color-coded severity |
| **Cluster Overview** | Pod counts (total, running, failed, pending) |
| **Executive Summary** | High-level cluster assessment |
| **Issues Detected** | Critical, Warning, and Info level issues |
| **Predictions** | Forecasted problems with probability |
| **Recommendations** | Actionable items with specific kubectl commands |
| **Resource Usage** | CPU and memory consumption statistics |
| **Recent Events** | Cluster event timeline (last 24 hours) |

## 🔍 Monitoring & Troubleshooting

### View Logs

```bash
# Last 100 lines from most recent run
kubectl logs -n default -l app=health-guardian --tail=100

# Follow logs in real-time
kubectl logs -n default -l app=health-guardian -f --all-containers=true

# Check previous run (if job is recent)
kubectl logs -n default <pod-name> --previous
```

### Common Issues

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| **Pod in CrashLoopBackOff** | Check pod logs | `kubectl logs -n default <pod-name>` |
| **RBAC Forbidden errors** | Permissions issue | Verify `rbac.yaml` applied and ServiceAccount bound |
| **Azure OpenAI auth fails** | Invalid credentials | Verify secrets in Key Vault match current API keys |
| **Metrics API error** | Metrics Server not installed | `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/.../components.yaml` |
| **Logic Apps webhook fails** | URL invalid/expired | Regenerate webhook in Logic Apps and update secret |
| **No email received** | Logic App flow issue | Test Logic App with sample payload manually |

### Debug Mode

To increase logging verbosity, edit `k8s/cm.yaml`:

```yaml
data:
  LOG_LEVEL: "DEBUG"
```

Then restart the CronJob to pick up configuration.

### Manual Test

```bash
# Create test pod
kubectl run health-guardian-test --image=<YOUR_ACR>.azurecr.io/health-guardian:1.4 \
  --env="AZURE_OPENAI_ENDPOINT=..." \
  --env="AZURE_OPENAI_API_KEY=..." \
  --env="LOGIC_APP_WEBHOOK_URL=..." \
  --env="REPORT_RECIPIENTS=..." \
  -n default

# Check output
kubectl logs health-guardian-test
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 conventions
2. **Logging**: Use Python logging module with appropriate levels
3. **Error Handling**: Implement graceful fallbacks for API failures
4. **Testing**: Test locally before pushing to container registry

### Adding New Metrics

To add new monitoring metrics:

1. Add collection method to `KubernetesMonitor` class
2. Include data in cluster_data dictionary in `main.py`
3. Update context preparation in `AIAnalyzer._prepare_context()`
4. Update report generation in `ReportGenerator`

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI service endpoint URL |
| `AZURE_OPENAI_API_KEY` | ✅ | Azure OpenAI API authentication key |
| `LOGIC_APP_WEBHOOK_URL` | ✅ | Azure Logic Apps HTTP webhook for email |
| `REPORT_RECIPIENTS` | ✅ | Comma-separated email addresses |
| `LOG_LEVEL` | ❌ | Logging level (default: INFO) |

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| kubernetes | 28.1.0 | Kubernetes Python client |
| azure-identity | 1.15.0 | Azure authentication |
| azure-monitor-query | 1.2.0 | Azure Monitor integration |
| requests | 2.31.0 | HTTP requests for REST APIs |
| python-dateutil | 2.8.2 | Date/time utilities |

## 📄 License

[NA]

## 📧 Support & Questions

For issues, questions, or feature requests, please:
1. Check the Troubleshooting section
2. Review pod logs and error messages
3. Consult Azure OpenAI API documentation
4. Contact your infrastructure team

---

**Last Updated**: February 2026  
**Version**: 1.4  
**Status**: Production Ready ✅