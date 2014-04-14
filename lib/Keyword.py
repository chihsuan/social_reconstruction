class Keyword(object):

    

    def __init__(self, word, currTime):
        self.word = word
        self.currTime = currTime
        self.lastTime = currTime   #default
        self.nextTime = currTime

    def insertLastTime(self, lastTime):
        self.lastTime = lastTime

    def insertNextTime(self, nextTime):
        self.nextTime = nextTime
        

