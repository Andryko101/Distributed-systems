from flask import Flask, request, jsonify
import uuid
import time
import threading
import requests
import Pyro5.api

app = Flask(__name__)

# Registered servers
servers = {}  # { "http://localhost:5001": {"load": 0, "last_heartbeat": time.time()} }
heartbeat_timeout = 10  # seconds

lock = threading.Lock()


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    server_url = data.get("server_url")

    if not server_url:
        return jsonify({"error": "Missing server_url"}), 400

    with lock:
        if server_url not in servers:
            print(f"[LoadBalancer] Registered new server: {server_url}")
        servers[server_url] = {"load": 0, "last_heartbeat": time.time()}

    return jsonify({"status": "heartbeat received"}), 200


@app.route('/request', methods=['POST'])
def handle_client_request():
    data = request.get_json()
    try:
        data["task_id"] = str(uuid.uuid4())  # ✅ assign task ID
        print(f"[LoadBalancer] Sending task to middleware: {data}")
        task_queue = Pyro5.api.Proxy("PYRONAME:middleware.task_queue")
        task_queue.push_task(data)
        return jsonify({"status": "task sent to middleware", "task_id": data["task_id"]}), 200
    except Exception as e:
        print(f"[LoadBalancer] Error: {e}")
        return jsonify({
            "error": "Failed to push task to middleware",
            "details": str(e)
        }), 500



def cleanup_dead_servers():
    now = time.time()
    dead = [s for s, info in servers.items() if now - info["last_heartbeat"] > heartbeat_timeout]
    for s in dead:
        print(f"[LoadBalancer] Removing dead server: {s}")
        del servers[s]

def run_cleanup_loop():
    while True:
        time.sleep(heartbeat_timeout)
        with lock:
            cleanup_dead_servers()

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    try:
        task_queue = Pyro5.api.Proxy("PYRONAME:middleware.task_queue")
        result = task_queue.get_result(task_id)

        if result is None:
            return jsonify({"status": "pending"}), 202
        else:
            return jsonify({"status": "complete", "result": result}), 200
    except Exception as e:
        print(f"[LoadBalancer] Error fetching result: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    threading.Thread(target=run_cleanup_loop, daemon=True).start()
    app.run(port=8000)


