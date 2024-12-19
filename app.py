import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import requests  # Import the requests library

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Simplified ncic-like functionality ---

# In-memory store for tunnels (replace with a persistent store if needed)
tunnels = {}

@app.route('/ncic', methods=['POST'])
def create_tunnel():
    """
    Creates a new tunnel.

    Expects a JSON payload with:
    - 'name': A unique name for the tunnel (optional).
    - 'port': The local port to expose.
    """
    data = request.get_json()
    name = data.get('name')
    port = data.get('port')

    if not port:
        return jsonify({'error': 'Missing "port" in request'}), 400

    if name:
        if name in tunnels:
            return jsonify({'error': f'Tunnel with name "{name}" already exists'}), 409
    else:
        # Generate a unique name if not provided
        name = os.urandom(16).hex()

    # For simplicity, the public URL is just the server's URL with the tunnel name
    public_url = f"{request.host_url}ncic/{name}"

    tunnels[name] = {'port': port}
    return jsonify({'public_url': public_url}), 201

@app.route('/ncic/<tunnel_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def tunnel_handler(tunnel_name):
    """
    Handles requests to the tunnel.

    Forwards requests to the corresponding local port.
    """
    tunnel = tunnels.get(tunnel_name)
    if not tunnel:
        return jsonify({'error': 'Tunnel not found'}), 404

    # --- Forward the request to the local port ---
    try:
        # Build the URL for the local service
        local_url = f"http://localhost:{tunnel['port']}{request.path}"

        # Forward the request to the local service
        response = requests.request(
            method=request.method,
            url=local_url,
            headers=request.headers,
            data=request.get_data(),
            stream=True  # Important for large responses
        )

        # Return the response from the local service
        return Response(response.iter_content(chunk_size=1024),
                        status=response.status_code,
                        content_type=response.headers['content-type'])

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error forwarding request: {e}'}), 500
    # --- End of request forwarding ---

# --- End of ncic-like functionality ---


# Endpoint for users to test tunneling
@app.route('/api', methods=['GET', 'POST'])
def api_tunnel():
    if request.method == 'POST':
        data = request.json
        return jsonify({"message": "Received your data", "data": data})
    return jsonify({"message": "Welcome to the Code Engine Tunnel!"})

# WebSocket for real-time communication
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit("server_response", {"message": "Connection established!"})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('client_message')
def handle_client_message(data):
    print(f"Received from client: {data}")
    emit("server_response", {"message": f"Received: {data}"})

if __name__ == "__main__":
    # Use port 5000 by default
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)