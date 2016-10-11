import threading
import traceback

class CrawlUrlThreads:
    def __init__(self, queue, runnable, threads=2):
        self.url_queue = queue
        self.runnable = runnable
        self.threads = threads

    class Worker(threading.Thread):
        def __init__(self, outer):
            threading.Thread.__init__(self)
            self.outer = outer
            self.daemon = True

        def run(self):
            while not self.outer.url_queue.empty():
                try:
                    item = self.outer.url_queue.get_nowait()
                    self.outer.runnable(item)
                    self.outer.url_queue.task_done()
                except Exception as e:
                    self.outer.url_queue.task_done()
                    print str(e.message)
                    print traceback.format_exc()
                    continue

    def start(self):
        for i in range(self.threads):
            worker = self.Worker(self)
            worker.start()
        self.url_queue.join()


class CrawlPageThreads:
    def __init__(self, runnable, paginator, threads=2):
        self.runnable = runnable
        self.paginator = paginator
        self.threads = threads

    class Worker(threading.Thread):
        def __init__(self, outer):
            threading.Thread.__init__(self)
            self.outer = outer
            self.daemon = True

        def run(self):
            while True:
                if not self.outer.runnable(self.outer.paginator.inc()):
                    break

    def start(self):
        workers = [self.Worker(self) for i in range(int(self.threads))]
        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()