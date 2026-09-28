# GCP - Google Cloud Provider

### Create a project on GCP

Create a new project on Google Cloud - https://console.cloud.google.com/

### Install the gcloud CLI

Command line for running GCP commands in the terminal. The Google Cloud CLI includes the command-line tools 'gcloud' and 'gsutil' - https://cloud.google.com/sdk/docs/install

```bash
$ gcloud version
```

### Authenticating with Google Cloud

```bash
$ gcloud auth login
```

### Choose the project

```bash
$ gcloud config set project <project_id>
```

### To run a container in the cloud 'serverless'
Without creating Virtual Machines. Google manages how it scales.

```bash
$ gcloud run deploy --port=8000
```
Options that will be presented:
- Choose the project folder (Dockerfile) or 'enter' if already in the project folder;
- Choose the service name;
- Confirm the installation of other required APIs (Artifact Registry, etc);
- Choose a region: [32] southamerica-east1;
- Confirm the creation of an Artifact Registry;
- Confirm 'Allow unauthenticated invocations';

At the end, the service URL will be provided.

### In GCP, go to Artifact Registry

Verify the creation of the Docker image on Google Cloud

### In GCP, go to Cloud Run

Information about the deploy, metrics, logs.
