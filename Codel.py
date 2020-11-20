# https://codereview.appspot.com/110110044/patch/1/10006
from collections import deque
from Packet import Packet

import time, math

def Drop(p : Packet) :
    print("Drop packet", p.get_no())

class CoDelTimestampTag() :
    def __init__(self):
        self.m_creationTime = time.time()

    def get_createTime(self):
        return self.m_creationTime

class Queue() :
    m_target = 0.005
    m_interval = 0.1
    m_maxPackets = 10

class CoDelQeueue(Queue) :
    def __init__(self):
        self.m_packets = deque()
        self.m_bytesInQueue = 0
        self.m_maxBytes = 1000000   # 1MB
        self.m_minBytes = 1500      # MTU
        self.m_dropCount = 0
        self.m_count = 0
        self.m_lastCount = 0
        self.m_dropOverLimit = 0
        self.m_firstAboveTime = 0
        self.m_dropping = False
        self.m_dropNext = 0
        self.m_state1 = 0           # from enqueue
        self.m_state2 = 0           # from now > dropNext of dequeue
        self.m_state3 = 0           # Frist packet is drop
        self.m_states = 0


    def enqueue(self, p : Packet):
        if len(self.m_packets) +1 > self.m_maxPackets :
            print("Queue full (at max packets) -- dropping pkt")
            self.m_dropOverLimit +=1
            Drop(p)

            return False

        elif self.m_bytesInQueue + p.get_size() > self.m_maxBytes :
            print("Queue full (packet would exceed max bytes) -- dropping pkt")
            self.m_dropOverLimit += 1
            Drop(p)

            return False

        tag = CoDelTimestampTag()
        p.add_tag(tag)

        self.m_bytesInQueue += p.get_size()
        self.m_packets.append(p)

        print("Number packets : ", len(self.m_packets))
        print("Number bytes : ", self.m_bytesInQueue)

        return True

    def should_drop(self, p : Packet, now : time):
        tag = p.get_tag()
        drop = False

        sojourn_time = now - tag
        print("sojourn time : ", sojourn_time)

        if sojourn_time < self.m_target or self.m_bytesInQueue < self.m_minBytes :
            self.m_firstAboveTime = 0
            return False

        if self.m_firstAboveTime == 0 :
            self.m_firstAboveTime = now + self.m_interval

        elif now > self.m_firstAboveTime :
            drop = True
            self.m_state1 +=1

        return drop

    def dequeue(self):
        if len(self.m_packets) == 0 :
            self.m_dropping = False
            self.m_firstAboveTime = 0

            print("Queue empty")
            return

        now = time.time()
        p = self.m_packets.popleft()
        self.m_bytesInQueue -= p.get_size()

        print("Poped : ", p.get_no())
        print("Number packets : ", p.get_size())
        print("Number bytes : ", self.m_bytesInQueue)

        drop = self.should_drop(p, now)

        if self.m_dropping :
            if not drop :
                self.m_dropping = False
            else :
                if now > self.m_dropNext :
                    self.m_state2 +=1

                    while self.m_dropping and now > self.m_dropNext :
                        Drop(p)
                        self.m_dropCount +=1
                        self.m_count +=1

                        if len(self.m_packets) == 0 :
                            self.m_dropping = False
                            print("Queue empty")
                            self.m_states +=1
                            return

                        p = self.m_packets.popleft()
                        self.m_bytesInQueue -= p.get_size()

                        print("Poped : ", p.get_no())
                        print("Number packets : ", p.get_size())
                        print("Number bytes : ", self.m_bytesInQueue)

                        if not self.should_drop(p, now) :
                            self.m_dropping = False

                        else :
                            self.m_dropNext = self.ControlLaw(self.m_dropNext)

        elif drop :
            self.m_dropCount +=1
            Drop(p)

            if len(self.m_packets) == 0:
                # QUEUE가 비워있으면, 이후 dequeue할때 sojourn_time은 target보다 낮을 것이다.
                self.m_dropping = False
                drop = False

                print("Queue empty")
                self.m_states +=1
            else :
                p = self.m_packets.popleft()
                self.m_bytesInQueue -= p.get_size()

                print("Poped : ", p.get_no())
                print("Number packets : ", p.get_size())
                print("Number bytes : ", self.m_bytesInQueue)

                # 이전 packet이 이미 target보다 높으므로, 현재 packet도 target보다 높을 것이다.
                # return True
                drop = self.should_drop(p, now)
                self.m_dropping = True

            self.m_state3 +=1

            delta = self.m_count - self.m_lastCount
            if delta > 1 and (now - self.m_dropNext) < 16 * self.m_interval :
                self.m_count = delta
            else :
                self.m_count = 1

            self.m_lastCount = self.m_count
            self.m_dropNext = self.ControlLaw(now)

            if not drop : return

        self.m_states +=1
        return p

    def ControlLaw(self, t):
        return t + self.m_interval / math.sqrt(self.m_count)



