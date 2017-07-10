from processtracker import ProcessTracker
from kiwoom import Kiwoom
from pdreader import PDReader

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import os, time, pickle, threading
from pathlib import Path
from queue import Queue


class Gobble(ProcessTracker):

    def __init__(self):
        super().__init__()
        self.starting()
        self.app = QApplication(["kiwoom.py"])
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

    def timeit(method):
        """decorator for timing processes"""
        def timed(*args, **kwargs):
            ts = time.time()
            method(*args, **kwargs)
            te = time.time()
            print("Process took " + str(te-ts) + " seconds")
        return timed

    def initialize_thread(self):
        self.init_thread()
        self.thread_lock = threading.Lock()
        self.thread_queue = Queue()

    @timeit
    def kiwoom_step_one(self):
        self.step_one()
        kospi_code_list = self.kiwoom.get_code_list_by_market("0")
        kospi_name_list = [self.kiwoom.get_master_code_name(code) for code in kospi_code_list]
        kospi_dict = dict(zip(kospi_code_list, kospi_name_list))
        pickle_out = open("./data/kospi-dict.pickle", "wb")
        pickle.dump(kospi_dict, pickle_out)
        pickle_out.close()
        self.step_one_finish()

    def start_pdreader(self):
        kospi_list_pickle = Path("./data/kospi-list.pickle")
        if not kospi_list_pickle.exists():
            self.kiwoom_step_one()
