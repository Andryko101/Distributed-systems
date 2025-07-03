from flask import Flask, request, jsonify
import threading
import time
import requests
import sys
import Pyro5.api

app = Flask(__name__)

# CONFIGURATION
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
SERVER_URL = f"http://localhost:{PORT}"
LOAD_BALANCER_URL = "http://localhost:8000/heartbeat"
HEARTBEAT_INTERVAL = 5  # seconds

# Utility function to perform basic math
def perform_operation(operation, numbers):
    try:
        if operation == "sum":
            return sum(numbers)
        elif operation == "subtract":
            return numbers[0] - sum(numbers[1:])
        elif operation == "multiply":
            result = 1
            for n in numbers:
                result *= n
            return result
        elif operation == "divide":
            result = numbers[0]
            for n in numbers[1:]:
                result /= n
            return result
        else:
            return f"Unsupported operation: {operation}"
    except Exception as e:
        return f"Error during operation: {e}"

def pull_tasks():
    task_queue = Pyro5.api.Proxy("PYRONAME:middleware.task_queue")
    while True:
        try:
            task = task_queue.get_task()
            if task:
                operation = task.get("operation")
                numbers = task.get("numbers")
                task_id = task.get("task_id")

                print(f"[Server {PORT}] Task received: {operation} on {numbers}")
                result = perform_operation(operation, numbers)
                print(f"[Server {PORT}] Result: {result}")

                # Send result back to middleware
                task_queue.store_result(task_id, result)
        except Exception as e:
            print(f"[Server {PORT}] Error pulling task: {e}")
        time.sleep(1)


@app.route('/task', methods=['POST'])
def handle_task():
    data = request.get_json()
    operation = data.get("operation")
    numbers = data.get("numbers")

    print(f"[Server {PORT}] Received task: {operation} on {numbers}")

    result = perform_operation(operation, numbers)

    return jsonify({
        "result": result,
        "server": SERVER_URL
    })

def send_heartbeat():
    while True:
        try:
            requests.post(LOAD_BALANCER_URL, json={"server_url": SERVER_URL}, timeout=2)
            print(f"[Server {PORT}] Heartbeat sent.")
        except Exception as e:
            print(f"[Server {PORT}] Failed to send heartbeat: {e}")
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == '__main__':
    # Start heartbeat in background
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=pull_tasks, daemon=True).start()
    app.run(port=PORT)
