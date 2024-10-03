import time
from models.base import SQLModel
from utils.logger import log
from utils.session import SessionFactory
from utils.config import config
from utils.libs.daemon import Daemon, thread_exists

class TaskQueue:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.db_session = SessionFactory()

    #Obtain next task candidate
    def task_candidate(self): pass

    #Precondition checks before task assignation
    def task_precondition(self, task_candidate: SQLModel): pass

    #Task assignation for this thread
    def task_assignation(self, task_candidate: SQLModel): pass

    #Task execution for this thread
    def task_execution(self, task_candidate: SQLModel): pass
    
    #Queue process
    def start(self):
        max_inactive_retries = int(config.db.get("DB_MANAGER_QUEUE_INACTIVE_RETRIES"))
        query_db_wait_time = config.db.get("DB_MANAGER_QUEUE_DB_WAIT_TIME")
        log.info(action="[%s]" % self.name, message="Thread created and ready for execute tasks")
        
        inactive_counter = 0
        while True:
            #Check if there is something to do
            task_candidate = self.task_candidate()

            #Nothing to do -> Add to inactive counter and wait
            if task_candidate == None:
                #Add to inactive counter and check limit
                inactive_counter += 1

                #If retries limit is reached, stop the loop
                if inactive_counter >= max_inactive_retries: 
                    log.info(action="[%s]" % self.name, message="Thread destroyed after being inactive for %s seconds" % max_inactive_retries * query_db_wait_time)
                    self.db_session.close()
                    break
                else:
                    time.sleep(query_db_wait_time)
            
            #Something to do -> Reset inactive counter
            else:
                inactive_counter = 0

                #Check if precondition is met
                if not self.task_precondition(task_candidate=task_candidate) == True: continue

                #Check if task can be assignated
                if not self.task_assignation(task_candidate=task_candidate) == True: continue
                
                #Execute task
                self.task_execution(task_candidate=task_candidate)

class Queue():
    def __init__(self, name, instance, args): 
        self.instance = instance(name=name, args=args)
        self.name = name

class QueueManager():
    queues = []

    def add_all(self, queues):
        self.queues = queues

    def start_all(self):
        for queue in self.queues:
            if not thread_exists(name=queue.name):  
                Daemon(func=queue.instance.start, name=queue.name).start()
        
queue_manager = QueueManager()