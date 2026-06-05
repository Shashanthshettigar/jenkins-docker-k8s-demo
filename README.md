# Python CI/CD Pipeline with Jenkins & Docker

A simple, end-to-end CI/CD pipeline for a Python Flask app using Jenkins and Docker.  
Every push to GitHub automatically tests the code and ships a Docker image to DockerHub.

---

## Pipeline Overview

```
GitHub Push → Checkout → Test → Build Docker Image → Push to DockerHub
```

| Stage | What it does |
|---|---|
| **Checkout** | Pulls the latest code from GitHub |
| **Test** | Creates a virtualenv, installs deps, runs pytest |
| **Build** | Builds a Docker image tagged with the build number |
| **Push** | Pushes the image to DockerHub using stored credentials |

---

## Project Structure

```
.
├── app/
│   └── __init__.py       # Flask app
├── tests/
│   └── test_app.py       # Pytest tests
├── Dockerfile            # Container definition
├── Jenkinsfile           # Pipeline definition
├── requirements.txt
└── wsgi.py               # Entry point
```

---

## How to Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run the app
python wsgi.py
# → http://localhost:5000
# → http://localhost:5000/health
```

---

## Jenkins Setup

### 1. Install Jenkins (Docker)
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

### 2. Add AWS credentials in Jenkins
Go to **Manage Jenkins → Credentials → Add** — create three **Secret text** entries:

| Credential ID | Value |
|---|---|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |

> The IAM user needs these ECR permissions: `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`

### 2b. Create the ECR repository (once)
```bash
aws ecr create-repository --repository-name python-cicd-app --region us-east-1
```

### 3. Create the pipeline job
1. New Item → **Pipeline**
2. Under *Pipeline*, select **Pipeline script from SCM**
3. SCM: Git → enter your GitHub repo URL
4. Script path: `Jenkinsfile`
5. Save → **Build Now**

### 4. Add a GitHub Webhook (optional, for auto-trigger)
In your GitHub repo → Settings → Webhooks → Add:
- Payload URL: `http://<your-jenkins-ip>:8080/github-webhook/`
- Content type: `application/json`
- Event: **Just the push event**

---

## What the recruiter sees

- Clean, readable `Jenkinsfile` with 4 well-named stages
- Real tests that run inside the pipeline
- Docker image tagged with the Jenkins build number (e.g. `:42`)
- Credentials handled securely — never hardcoded
- `post` block handles cleanup and status messages
