import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(10):
    socket.send(b"Hello")
    print("Sent request")
    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))