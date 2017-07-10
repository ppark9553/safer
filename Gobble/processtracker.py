import time

class ProcessTracker:

    def __init__(self):
        self.process_dict = {"starting": "Data collection starting", \
                             "step_one": "Connecting to Kiwoom API and saving Kospi code/name data", \
                             "step_one_finish": "Successfully downloaded Kospi dict data to 'data' directory", \
                             "init_thread": "Initializing thread lock and queue", \
                             "finishing": "Project successfully finished"}

    def print_track(method):
        """decorator for printing out process tracks"""
        def tracked(*args, **kwargs):
            record = method(*args, **kwargs)
            print(record)
        return tracked

    @print_track
    def starting(self):
        return self.process_dict["starting"]

    @print_track
    def step_one(self):
        return self.process_dict["step_one"]

    @print_track
    def step_one_finish(self):
        return self.process_dict["step_one_finish"]

    @print_track
    def init_thread(self):
        return self.process_dict["init_thread"]

    @print_track
    def finishing(self):
        return self.process_dict["finishing"]
