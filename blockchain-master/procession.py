import threading
import iotpeer

class Procession(object):
    def __init__(self, operation):
        self.operation = operation
        self.shutdown = False
            self.tasks = self.operation.task_queue
        self.method_handler = iotpeer.Handles(self.operation)

    def procession_loop(self):
        while self.shutdown is not True:
            task = self.tasks.get()
            # do sth



class ProcessionThread(threading.Thread):
    def __init__(self,operation):
        self.threadname="procession"
        threading.Thread.__init__(self)
        self.operation = operation
        self.procession = Procession(self.operation)

    def run(self):
        print "Starting procession loop"
        self.procession.procession_loop()

