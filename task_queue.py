
import Pyro5.api
from queue import Queue

@Pyro5.api.expose
class TaskQueue:
    def __init__(self):
        self.queue = Queue()
        self.results = {}  # Store task results by ID

    def push_task(self, task):
        print(f"[Middleware] Task received: {task}")
        task_id = task.get("task_id")
        if task_id:
            self.results[task_id] = None  # Mark result as pending
            self.queue.put(task)
            return "task received"
        return "task_id missing"

    def get_task(self):
        if not self.queue.empty():
            task = self.queue.get()
            print(f"[Middleware] Task sent: {task}")
            return task
        return None

    def store_result(self, task_id, result):
        print(f"[Middleware] Storing result for {task_id}: {result}")
        self.results[task_id] = result
        return "result stored"

    def get_result(self, task_id):
        return self.results.get(task_id, None)

def main():
    queue = TaskQueue()
    daemon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(queue)
    ns.register("middleware.task_queue", uri)
    print("[Middleware] TaskQueue registered. Ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
