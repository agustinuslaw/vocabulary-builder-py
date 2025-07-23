import time

class Stopwatch:
    """This class measures elapsed time from enter to exit in seconds"""

    def __init__(self, name="Process"):
        self.name = name
        self.start = None
        self.end = None
        self.elapsed = None

    def __enter__(self):
        # print(self.name)
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"{self.name} elapsed: {self.elapsed:.2f} seconds")
