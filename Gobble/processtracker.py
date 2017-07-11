import time

def timeit(method):
    """decorator for timing processes"""
    def timed(*args, **kwargs):
        ts = time.time()
        method(*args, **kwargs)
        te = time.time()
        print("Process took " + str(te-ts) + " seconds")
    return timed

class ProcessTracker:

    def __init__(self):
        self.process_dict = {"starting": "Data collection starting", \
                             "connecting_db": "Connecting to MongoDB database", \
                             "connect_successful": "Database connection successful", \
                             "step_one": "Connecting to Kiwoom API and saving market code/name to 'data'", \
                             "step_one_finish": "Successfully downloaded market dict data to 'data'", \
                             "starting_pdreader": "Starting PDReader to initialize and update Kospi OHLCV data", \
                             "step_one_skipped": "Step one skipped, going back and running step one", \
                             "pdreader_started": "PDReader started, ready to initialize and update Kospi OHLCV data", \
                             "saving_kospi_ohlcv": "PDReader saving Kospi OHLCV", \
                             "data_saved": "Data successfully saved in 'data/stock'", \
                             "kospi_ohlcv_initialized": "Kospi OHLCV data initialized, check for errors", \
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
    def connecting_db(self):
        return self.process_dict["connecting_db"]

    @print_track
    def connect_successful(self):
        return self.process_dict["connect_successful"]

    @print_track
    def step_one(self):
        return self.process_dict["step_one"]

    @print_track
    def step_one_finish(self):
        return self.process_dict["step_one_finish"]

    @print_track
    def starting_pdreader(self):
        return self.process_dict["starting_pdreader"]

    @print_track
    def step_one_skipped(self):
        return self.process_dict["step_one_skipped"]

    @print_track
    def pdreader_started(self):
        return self.process_dict["pdreader_started"]

    @print_track
    def saving_kospi_ohlcv(self):
        return self.process_dict["saving_kospi_ohlcv"]

    @print_track
    def starting_request(self, code, name):
        return "Starting data collection for " + code + ", " + name

    @print_track
    def data_saved(self):
        return self.process_dict["data_saved"]

    @print_track
    def skipped_data(self, code, name):
        return code + ", " + name + " skipped due to error"

    @print_track
    def kospi_ohlcv_initialized(self):
        return self.process_dict["kospi_ohlcv_initialized"]

    @print_track
    def finishing(self):
        return self.process_dict["finishing"]
