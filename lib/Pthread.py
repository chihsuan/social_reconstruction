import threading

class Pthread (threading.Thread):
    
    threadLock = threading.Lock()
    
    def __init__(self, threadID, name, startPoint, finishPoint):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.startPoint = startPoint
        self.finishPoint = finishPoint

    def run(self):
        global faceLists
        # Get lock to synchronize threads
        # doing
        print self.name + ' start'
        mergeByFaceMatch(faceLists, self.startPoint, self.finishPoint) 
        # Free lock to release next thread
