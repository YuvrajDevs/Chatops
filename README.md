# Opsidian: A Jenkins ChatOps Bot Framework

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED?logo=docker&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-LTS-D24939?logo=jenkins&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-Socket_Mode-4A154B?logo=slack&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-v2-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-OSS-F46800?logo=grafana&logoColor=white)
![Pytest](https://img.shields.io/badge/Test-Pytest-0A9B0A?logo=pytest&logoColor=white)

<br>

Opsidian is an extensible **framework** and **starter-kit** for a Python-based ChatOps bot that integrates Jenkins CI/CD pipelines directly into Slack.
It provides a complete, production-ready CI pipeline, secure key handling, and an integrated monitoring stack right out of the box. This allows a development team to immediately start **building and adding their own custom commands** without worrying about the underlying plumbing.


<br>

## Features

This framework comes with 4 common commands as a starting point. Adding new commands is as simple as adding a new `case` to the `match` statement in `app.py`.

* `build <job-name>`: Triggers a new build for a specified Jenkins job.
* `get-last-build <job-name>`: Fetches the status (`SUCCESS`, `FAILED`, `IN_PROGRESS`) of the most recent build.
* `abort-build <job-name> <build-number>`: Stops a currently running build.
* `get-build-logs <job-name> <build-number>`: Retrieves the complete console output for a build and uploads it as a `.txt` file directly to the Slack channel.

<br>

## Architecture

This project consists of three independent, interconnected systems that work together.

### 1. Bot Architecture

The bot's runtime architecture is built for security and simplicity. It uses **Slack's Socket Mode** to open a persistent WebSocket connection *outbound* to Slack's APIs. This avoids the need for a public IP address, firewall rules, or a reverse proxy.



**Flow:**
1.  A user `@mentions` the bot in a Slack channel.
2.  Slack pushes the event message down the Socket Mode (WebSocket) connection to the running Python container.
3.  The `slack-bolt` library receives the event, parses the command (e.g., `build`), and collects the arguments.
4.  The bot makes a REST API call (using `requests`) to the Jenkins server's URL, authenticating with the provided `JENKINS_USER` and `JENKINS_TOKEN`.
5.  Jenkins executes the action and returns a response.
6.  The bot formats this response into a user-friendly message and sends it back to the Slack channel via the `chat:write` API.

<br>

### 2. CI/CD Pipeline Architecture 

The entire project is built and published by its own **Pipeline-as-Code** `Jenkinsfile`. This creates a fully automated CI system that tests, builds, and publishes the bot itself.



**Stages:**
1.  **Checkout Code:** Clones the `main` branch from the Git repository.
2.  **Run Tests:** Runs `pytest` inside a temporary `python:3.11-slim` container (using `docker.inside()`) to act as a quality gate. The build fails if tests fail.
3.  **Build Docker Image:** If tests pass, Jenkins builds a new Docker image of the bot using the project's `Dockerfile`.
4.  **Push to Docker Hub:** The new image is tagged with the 7-character Git commit hash (e.g., `yuvrajdevs/chatops-bot:dcb4b2c`) for traceability. Jenkins then uses the stored `DOCKERHUB_CREDENTIALS_ID` to log in and push the versioned image to Docker Hub.

<br>

### 3. Monitoring Architecture 

The system is fully observable using the included `docker-compose.yml` stack. The bot, Prometheus, and Grafana all run in the same Docker network (`monitoring_net`) for easy service discovery.


**Flow:**
1.  **Export:** The Python bot (`app.py`) uses the `prometheus_client` library to export a custom counter (`bot_commands_total`) on its internal port `8000`.
2.  **Scrape:** The `prometheus.yml` file configures the Prometheus server to find and scrape the bot's metrics using its Docker container name (`bot:8000`).
3.  **Visualize:** The Grafana server is pre-configured to connect to Prometheus as a data source, allowing you to build dashboards that visualize which commands are being used most often.

<br>

## Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Bot Framework** | Python 3.11, `slack-bolt` | The core application logic and Slack connection. |
| **CI/CD** | Jenkins (Pipeline-as-Code) | For the automated `test` -> `build` -> `push` lifecycle. |
| **Containerization** | Docker, Docker Compose | To package the bot and run the full stack locally. |
| **Artifact Registry** | Docker Hub | To store versioned, immutable Docker images of the bot. |
| **Testing** | `pytest` | To run automated tests as a quality gate in the CI pipeline. |
| **Monitoring** | Prometheus | To scrape and store custom metrics from the bot. |
| **Visualization** | Grafana | To build dashboards for bot performance and usage. |

<br>

## Getting Started (Local Deployment)

You can run the entire bot and its monitoring stack locally in just a few steps.

### 1. Prerequisites
* A **Slack Workspace** where you can create an app.
* A **Jenkins Server** (can be running in Docker).
* **Docker** and **Docker Compose** installed.

### 2. Configuration

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YuvrajDevs/Chatops.git](https://github.com/YuvrajDevs/Chatops.git)
    cd Chatops
    ```

2.  **Set up your Slack App**
    * Go to `api.slack.com/apps` and create a new app.
    * Enable **Socket Mode**.
    * Generate an **App-Level Token** (`xapp-...`) with `connections:write` scope.
    * Go to **OAuth & Permissions** and add these Bot Token Scopes:
        * `app_mentions:read` (to see messages)
        * `chat:write` (to send messages)
        * `files:write` (to upload logs)
    * Install the app to your workspace and get the **Bot User OAuth Token** (`xoxb-...`).

3.  **Create your `.env` file**
    Copy the `env.example` (you should create this file) or create a new `.env` file with your credentials:
    ```ini
    # Slack Tokens
    SLACK_BOT_TOKEN=xoxb-...
    SLACK_APP_TOKEN=xapp-...

    # Jenkins Credentials
    JENKINS_URL=http://<YOUR_JENKINS_IP_OR_URL>:8080
    JENKINS_USER=<your_jenkins_username>
    JENKINS_TOKEN=<your_jenkins_api_token>
    ```
    > **Note:** If Jenkins is running as a Docker container, use its host IP (e.g., `http://172.17.0.1:8080`), not `localhost`.

### 3. Run the Stack
```bash
docker compose up -d
```

Your stack is now running. You can verify the services are up:

  * **Prometheus** is available at `http://localhost:9090`
  * **Grafana** is available at `http://localhost:3000` (user/pass: `admin`/`admin`)

### 4. Invite and Use Your Bot

1.  Open your Slack workspace and go to any channel.
2.  Invite your bot to the channel. Type `/invite` and select your bot's name (e.g., `@Opsidian`).
3.  Once it's in the channel, send it a command:

```bash
@Opsidian get-last-build <your-jenkins-job-name>
```

<br>

## Detailed Documentation

For a more in-depth guide covering advanced configuration, troubleshooting, and detailed explanations of the pipeline and code, please refer to the full project documentation.

[**Detailed Project Documentation**]([https://link](https://drive.google.com/file/d/1bHPcqiIouGlt0vXt-7_LHEaUgbcbIili/view?usp=sharing))

<br>
