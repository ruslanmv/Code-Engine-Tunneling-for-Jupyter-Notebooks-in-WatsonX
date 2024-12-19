# Code Engine Tunneling for Jupyter Notebooks in Cloud Pak

This repository demonstrates how to use Code Engine to create a tunnel for accessing Jupyter Notebooks running in a Cloud Pak environment from outside the cluster. This solution provides a secure and convenient way to interact with your notebooks and web apps without complex network configurations.

## Architecture

The solution consists of two main components:

1.  **Code Engine Tunnel (server-side):** A Flask application deployed on Code Engine that acts as a tunnel, forwarding requests to your local machine.
2.  **Client-side code:** A FastAPI application running alongside your Jupyter Notebook in the Cloud Pak environment. This application communicates with the Code Engine tunnel to expose your notebook or web app.

## How it Works

1.  **Deploy the Code Engine Tunnel:**
    *   The `app.py` file contains the Flask application that serves as the tunnel.
    *   Deploy this application to Code Engine. This will provide you with a public URL for your tunnel.

2.  **Run the Client-side Code:**
    *   The `client.ipynb` file contains the FastAPI application.
    *   Run this application in your Cloud Pak environment, alongside your Jupyter Notebook.
    *   This application will:
        *   Automatically create a tunnel by making a request to the `/ncic` endpoint of your Code Engine tunnel app.
        *   Receive a public URL for the tunnel.
        *   Expose your Jupyter Notebook or web app on this public URL.

3.  **Access your Notebook/Web App:**
    *   Use the public URL provided by the client-side code to access your Jupyter Notebook or web app from outside the Cloud Pak environment.
    *   The Code Engine tunnel will forward requests to your notebook/web app running in the Cloud Pak environment and return the responses.

## Files

*   `app.py`: Flask application for the Code Engine tunnel.
*   `client.py`: FastAPI application to run alongside your Jupyter Notebook.

## Setup and Running

1.  **Prerequisites:**
    *   IBM Cloud account with Code Engine enabled.
    *   Cloud Pak environment with Jupyter Notebook.
    *   Python 3.8 or higher.
    *   Install the required Python packages: `pip install fastapi uvicorn nest_asyncio requests Flask flask-socketio`

2.  **Deploy Code Engine Tunnel:**
    *   Create a new Code Engine project.
    *   Deploy the `app.py` application to Code Engine.
    *   Note the public URL of the deployed application.

3.  **Configure and Run Client-side Code:**
    *   In the `client.ipynb` file, update the URL in the `ncic_custom()` function to point to your Code Engine tunnel's public URL.
    *   Run the `client.ipynb` file in your Cloud Pak environment.
    *   The application will print the public URL for accessing your notebook/web app.

4.  **Access your Notebook/Web App:**
    *   Open the public URL in your web browser to access your Jupyter Notebook or web app.

## Example Scenario

Let's say you have a machine learning model training notebook running in Jupyter Notebook on Cloud Pak. You want to monitor the training progress and access the results from your mobile device while you're away from your workstation.

By using this Code Engine tunneling solution, you can:

1.  Expose your Jupyter Notebook through a public URL.
2.  Access the notebook from your mobile device to track the training progress.
3.  Interact with the notebook, make changes, and visualize the results in real-time, all from outside the Cloud Pak environment.

## Security Considerations

*   While this solution provides a convenient way to access your notebooks, it's crucial to consider security implications.
*   The Code Engine tunnel should be configured with appropriate authentication and authorization mechanisms to restrict access to authorized users only.
*   Avoid exposing sensitive information or critical applications without proper security measures in place.

Below is the full Python code to deploy a FastAPI application on **IBM Cloud Code Engine** and use it as a publicly accessible proxy-like solution, similar to `ngrok`. This approach ensures that the application is hosted on the cloud and accessible through a permanent URL while being serverless and scalable.

---

### **Steps to Set Up IBM Code Engine**

#### 1. **Prepare the Python Code for Code Engine**

Create a Python script (e.g., `app.py`) for your FastAPI application. The following code includes the `/inference` endpoint and is ready for deployment.



---

#### 2. **Create a `Dockerfile` for Containerization**

This `Dockerfile` specifies how to containerize the FastAPI application:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN pip install fastapi uvicorn

# Expose the port that the FastAPI app will run on
EXPOSE 8080

# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

#### 3. **Build and Push the Docker Image**

1. **Build the Docker Image**:
   ```bash
   docker build -t my-fastapi-app .
   ```

2. **Push the Docker Image to IBM Cloud Container Registry**:
   ```bash
   ibmcloud login
   ibmcloud cr login
   ibmcloud cr namespace-add mynamespace
   docker tag my-fastapi-app us.icr.io/mynamespace/my-fastapi-app
   docker push us.icr.io/mynamespace/my-fastapi-app
   ```

---

#### 4. **Deploy to IBM Cloud Code Engine**

1. **Create a Code Engine Project**:
   ```bash
   ibmcloud ce project create --name my-code-engine-project
   ```

2. **Deploy the Application**:
   ```bash
   ibmcloud ce application create --name my-fastapi-app \
       --image us.icr.io/mynamespace/my-fastapi-app \
       --cpu 0.5 --memory 1G --port 8080
   ```

3. **Get the Public URL**:
   After deployment, Code Engine will automatically provide a public URL for your application. You can retrieve it using:
   ```bash
   ibmcloud ce application get --name my-fastapi-app
   ```
   Example output:
   ```
   URL: https://my-fastapi-app.us-south.codeengine.appdomain.cloud
   ```

---

#### 5. **Test the Application**

Once the application is deployed, you can test it using `curl` or Postman:

1. **Using `curl`**:
   ```bash
   curl -X POST https://my-fastapi-app.us-south.codeengine.appdomain.cloud/inference \
        -H "Content-Type: application/json" \
        -d '{"message": "Test message"}'
   ```

2. **Using Postman or Browser**:
   - Open the URL in your browser: `https://my-fastapi-app.us-south.codeengine.appdomain.cloud/inference`.
   - Use a tool like Postman to send a `POST` request with the JSON body:
     ```json
     {
       "message": "Test message"
     }
     ```

---

### **Advantages of Using IBM Cloud Code Engine**
1. **Permanent Public URL**:
   Unlike `ngrok`, the application is always available at a fixed URL provided by Code Engine.
2. **Serverless and Scalable**:
   Code Engine automatically scales your application based on usage.
3. **No Infrastructure Management**:
   No need to manage servers or tunnels—Code Engine handles everything.
4. **Secure and Reliable**:
   Built-in HTTPS and IBM's cloud reliability.

---

### **Summary of the Workflow**

1. **Write and Containerize**:
   - Develop the FastAPI application and prepare a `Dockerfile`.

2. **Push to IBM Cloud**:
   - Push the container to IBM Cloud Container Registry.

3. **Deploy on Code Engine**:
   - Deploy the containerized app to Code Engine and obtain the public URL.

4. **Access the Public Endpoint**:
   - Use the public URL provided by Code Engine to access the `/inference` endpoint.

## Further Enhancements

*   Implement authentication and authorization for the tunnel.
*   Use a persistent store (e.g., a database) for tunnel information.
*   Add support for different protocols (e.g., WebSockets).
*   Implement more advanced routing and request handling logic.

This solution offers a flexible and secure way to access Jupyter Notebooks and web apps running in Cloud Pak from anywhere. By leveraging Code Engine's capabilities, you can simplify network configurations and enhance your remote development experience.