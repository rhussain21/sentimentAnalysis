# Sentiment Analysis API

## Description of application

This application is designed to classify positive and negative sentiment based on user text input. It consists of two main services: 1) a prediction API that handles user input and Natural Langauge Processing (NLP) model and 2) a Redis cache that stores and retrieves outputs for frequent requests. Caching is employed to optimize system performance by alleviating the load on backend servers and improving overall response times. As part of system evaluation, a load test is conducted to ensure robustness and minimal latency under high user demand.


## Deployment

This application is deployed in an Azure Kubernetes cluster with the namespace `rh1330`. It consists of a Python-API deployment and a Redis deployment. The Python-API provides the prediction service, and Redis functions as the cache.

### Prerequisites

It's assumed that the user has access to their own Kubernetes cluster (Azure Kubernetes Service, AKS) and Azure Container Registry (ACR). Users will need to modify the run script for dev testing and pushing the image to their registry.

### Deployment Steps

1. **Code Modifications**: Make the necessary changes in the code and test them in the development environment.
2. **Docker Build**: Build the Docker image and push it to Azure Container Registry.
3. **Update Configuration**: Modify the base and prod overlay files as required.
4. **Apply Configuration**:
    - Navigate to the `prod` folder inside the `.k8s` directory.
    - Apply all the files. Kustomize is configured to link to the base settings and then apply the patch:
      ```bash
      kubectl apply -k .
      ```

### Application Workflow

1. **Data Submission**: The user submits a POST Payload to the API.
2. **Data Validation**: The API validates the data.
   - If the data is not valid, a 422 error response is returned.
   - If the data is valid, the API proceeds to the next step.
3. **Cache Check**: The API checks if the value is already in the cache (Redis).
   - If the value exists, it is then returned to the user.
   - If the value is not cached, the API proceeds to the next step.
4. **Prediction**: The input is processed by the prediction model. The output value is then stored in the cache and returned to the user.

## How to Test


To test the prediction service deployed on your Kubernetes cluster, you can use the following `curl` command:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": ["sentence 1", "sentence 2", ... "sentence N"]}' https://{namespace}.{domain}/predict
```

Replace {namespace} with your specific namespace and {domain} with your domain to match your deployment setup. In the data payload, replace "sentence 1", "sentence 2", ... "sentence N" with the actual sentences you intend to analyze for sentiment. Note that the list inside the "text" key can contain any number of sentences.

For the data model:
```bash
{
  "text": ["sentence 1", "sentence 2", ... "sentence N"]
}
```
The sentences within the "text" key are expected to adhere to this format. They will be validated using a Pydantic model to ensure compliance.

For example, in the given setup, the `curl` command could look like:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": ["I enjoyed the movie.", "The weather is nice today.", "I didn't like the food."]}'
 https://rh1330.mids255.com/predict
```
