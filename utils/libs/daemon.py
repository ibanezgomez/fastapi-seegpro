import threading

def thread_exists(name):
    return any(thread.getName() == name for thread in threading.enumerate())

class Daemon(object):
    running = False
    args = None

    def __init__(self, func, args=None, name=None):
        # Connect to the reader
        self.function = func
        self.name = name
        if args: self.args = [args]

    def start(self):
        if self.running: return
        # Reader Thread
        if self.args: 
            self.thread = threading.Thread(target=self.function, args=self.args, name=self.name)
        else: 
            self.thread = threading.Thread(target=self.function, name=self.name)
        self.thread.setDaemon(True)
        self.running = True
        self.thread.start()

    def stop(self):
        if not self.running: return
        self.running = False
        self.thread.join()

    def isActive(self):
        return self.running