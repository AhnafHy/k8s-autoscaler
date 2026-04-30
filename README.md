[README.md](https://github.com/user-attachments/files/27262102/README.md)
# Kubernetes Autoscaling Demo

A production-grade Kubernetes autoscaling demonstration. A Python web app containerized and deployed onto a local Kubernetes cluster via Helm charts, with a Horizontal Pod Autoscaler that automatically scales from 1 to 4 replicas under CPU load, monitored by Prometheus. All deployment configuration is defined as code using Helm templates.

---

## What It Does

- **GET /** — returns a health status JSON response including the pod name serving the request
- **GET /health** — liveness and readiness probe endpoint used by Kubernetes to monitor pod health
- **GET /cpu** — CPU-intensive computation endpoint used to trigger autoscaling under load
- **Horizontal Pod Autoscaler** — monitors CPU utilization and automatically scales pods between 1 and 5 replicas
- **Prometheus** — scrapes and stores cluster metrics via kube-prometheus-stack
- **Load test script** — simulates 20 concurrent threads hitting the `/cpu` endpoint to trigger autoscaling

---

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │         Minikube Cluster             │
                        │                                      │
  Load Test Script ────►│  Kubernetes Service (NodePort)       │
  (20 threads)          │         │                            │
                        │         ▼                            │
                        │  ┌─────────────────────┐            │
                        │  │   Pod 1 (Flask App)  │            │
                        │  ├─────────────────────┤            │
                        │  │   Pod 2 (Flask App)  │◄─────────┐│
                        │  ├─────────────────────┤           ││
                        │  │   Pod 3 (Flask App)  │           ││
                        │  ├─────────────────────┤           ││
                        │  │   Pod 4 (Flask App)  │           ││
                        │  └─────────────────────┘           ││
                        │                                     ││
                        │  Horizontal Pod Autoscaler ─────────┘│
                        │  (scales 1→5 based on CPU ≥ 50%)     │
                        │                                      │
                        │  Prometheus (kube-prometheus-stack)  │
                        │  (scrapes cluster metrics)           │
                        └─────────────────────────────────────┘

Deployment managed via Helm charts
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python 3.11 / Flask / Gunicorn |
| Containerization | Docker (Minikube internal daemon) |
| Orchestration | Kubernetes (Minikube) |
| Package Management | Helm |
| Autoscaling | Kubernetes Horizontal Pod Autoscaler (HPA) |
| Monitoring | Prometheus (kube-prometheus-stack) |
| Metrics Server | Minikube metrics-server addon |
| Load Testing | Python threading (urllib) |

---

## Project Structure

```
k8s-autoscaler/
├── app/
│   ├── app.py                  # Flask app with /, /health, and /cpu endpoints
│   ├── requirements.txt        # Flask and Gunicorn dependencies
│   └── Dockerfile              # Container definition using python:3.11-slim
├── helm/
│   └── k8s-autoscaler/
│       ├── Chart.yaml          # Helm chart metadata
│       ├── values.yaml         # Configurable values (replicas, CPU limits, HPA thresholds)
│       └── templates/
│           ├── deployment.yaml # Kubernetes Deployment with liveness/readiness probes
│           ├── service.yaml    # NodePort Service to expose the app
│           └── hpa.yaml        # HorizontalPodAutoscaler (min: 1, max: 5, target CPU: 50%)
├── load-test.py                # Multi-threaded load test script to trigger autoscaling
├── .gitignore
└── README.md
```

---

## How to Deploy

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Helm](https://helm.sh/docs/intro/install/) installed
- [VirtualBox](https://www.virtualbox.org/) installed (used as Minikube driver)
- [Python 3.11+](https://www.python.org/downloads/) installed

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/AhnafHy/k8s-autoscaler.git
cd k8s-autoscaler
```

**2. Start Minikube**
```bash
minikube start --driver=virtualbox
```

**3. Enable the metrics server**
```bash
minikube addons enable metrics-server
```

**4. Build the Docker image inside Minikube**
```bash
minikube image build -t k8s-autoscaler:latest ./app
```
Confirm the image exists:
```bash
minikube image ls
```

**5. Install Prometheus monitoring stack**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```
Wait until all monitoring pods are running:
```bash
kubectl get pods -n monitoring
```

**6. Deploy the app via Helm**
```bash
helm install k8s-autoscaler ./helm/k8s-autoscaler
```
Confirm pods and HPA are running:
```bash
kubectl get pods
kubectl get hpa
```

**7. Expose the app**
```bash
minikube service k8s-autoscaler --url
```
Copy the URL printed (e.g. `http://192.168.59.100:XXXXX`) and test it:
```powershell
Invoke-WebRequest -Uri "http://192.168.59.100:XXXXX/" -Method GET
```
You should see a JSON response with `status: healthy` and the pod name.

**8. Run the load test**

Update the URL at the top of `load-test.py` to match your Minikube URL:
```python
URL = "http://192.168.59.100:XXXXX/cpu"
```

Open a second terminal and watch the autoscaler in real time:
```bash
kubectl get hpa -w
```

In your first terminal run the load test:
```bash
python load-test.py
```

Watch the replica count climb from 1 to 4 as CPU exceeds the 50% threshold, then scale back down to 1 after the load test completes.

**9. Clean up**
```bash
helm uninstall k8s-autoscaler
helm uninstall prometheus -n monitoring
minikube stop
```

---

## Autoscaling Behavior

| Phase | CPU Utilization | Replicas |
|---|---|---|
| Idle | 1% | 1 |
| Load increasing | 89% | 2 |
| Peak load | 200% | 4 |
| Load decreasing | 110% | 4 |
| Post load test | 1% | 1 |

---

## HPA Configuration

```yaml
minReplicas: 1
maxReplicas: 5
targetCPUUtilizationPercentage: 50
```

The autoscaler checks CPU metrics every 15 seconds and scales up when average utilization across all pods exceeds 50%. Scale-down occurs gradually after load subsides to avoid thrashing.

---

## Screenshots

**HPA scaling under load — replicas climbing from 1 to 4:**

<img width="702" height="208" alt="HPA Scaling" src="https://github.com/user-attachments/assets/3a18b1cd-197e-4cd0-82b8-bd19ff0bd44a" />


---

## Key Concepts Demonstrated

- **Container orchestration** — Kubernetes managing pod lifecycle, health checks, and self-healing
- **Helm packaging** — entire deployment defined as reusable, parameterized Helm templates
- **Horizontal Pod Autoscaling** — CPU-based autoscaling with configurable min/max replicas and target utilization
- **Liveness and readiness probes** — Kubernetes continuously health-checking pods via the `/health` endpoint
- **Observability** — Prometheus scraping cluster-wide metrics via kube-prometheus-stack
- **Load testing** — multi-threaded Python script simulating concurrent traffic to validate autoscaling behavior
- **Infrastructure as code** — no manual Kubernetes configuration, everything defined in YAML templates
