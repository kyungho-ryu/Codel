from Codel import CoDelQeueue
from Packet import Packet

import time

queue = CoDelQeueue()
queue.enqueue(Packet(1, bytes(5000)))
queue.enqueue(Packet(2, bytes(5000)))
queue.enqueue(Packet(3, bytes(5000)))
queue.enqueue(Packet(4, bytes(5000)))
queue.enqueue(Packet(5, bytes(5000)))

queue.dequeue()
queue.dequeue()
queue.dequeue()
queue.dequeue()
queue.dequeue()