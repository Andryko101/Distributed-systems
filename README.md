# Distributed-systems
Question
In this assignment, you will develop a scalable distributed system that simulates load balancing
and fault tolerance in a client-server architecture. The system should consist of multiple servers
and a load balancer that evenly distributes client requests among available servers based on their
current load. Each server should handle requests from the client and perform a simple task, such
as calculating the sum of numbers or handling remote method calls. Implement a heartbeat
mechanism that allows servers to notify the load balancer of their availability. If a server fails, the
load balancer should redirect incoming requests to other active servers.
Additionally, integrate asynchronous communication between the client and server to allow nonblocking request handling and improve performance. The system should also have automatic
scaling, where the number of active servers increases or decreases based on the incoming traffic.
For fault tolerance, implement data replication to ensure that data is available even if a server
goes down. Use middleware to facilitate communication between the servers and load balancer,
and ensure that your system can handle high traffic efficiently. 
