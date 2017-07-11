from kiwoom import Kiwoom
from dbwrapper import MongoDB
from pdreader import PDReader
from processtracker import ProcessTracker, timeit

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import os, time
import _pickle as pickle
from pathlib import Path


class Gobble(ProcessTracker):

    @timeit
    def __init__(self):
        super().__init__() # initialize ProcessTracker
        self.starting()
        self.app = QApplication(["kiwoom.py"])
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

    @timeit
    def start_db(self):
        pickle_in = open("db-info.pickle", "rb")
        db_info = pickle.load(pickle_in)
        user = db_info["USER"]
        pw = db_info["PW"]
        ip = db_info["IP"]
        db = db_info["DB"]
        self.connecting_db()
        self.db = MongoDB(user, pw, ip, db)
        self.connect_successful()

    @timeit
    def step_one_kiwoom(self):
        self.step_one()
        for market_type in ["0", "10"]:
            pickle_name = "kospi-dict.pickle" if market_type == "0" else "kosdaq-dict.pickle"
            code_list = self.kiwoom.get_code_list_by_market(market_type)
            name_list = [self.kiwoom.get_master_code_name(code) for code in code_list]
            market_dict = dict(zip(code_list, name_list))
            pickle_out = open("./data/" + pickle_name, "wb")
            pickle.dump(market_dict, pickle_out)
            pickle_out.close()
        self.step_one_finish()

    @timeit
    def start_pdreader(self, start_date, end_date):
        self.starting_pdreader()
        dict_pickle = Path("./data/kospi-dict.pickle")
        if not dict_pickle.exists():
            self.step_one_skipped()
            self.step_one_kiwoom()
        self.pr = PDReader(start_date, end_date)
        self.pr.set_task()
        self.pdreader_started()

    @timeit
    def init_kospi_ohlcv(self):
        db = self.db
        pr = self.pr
        self.initializing_kospi_ohlcv()
        uninitialized = list()
        for code, name in pr.task.items():
            try:
                self.starting_request(code, name)
                df = pr.request_df(code)
                ohlcv = pr.create_ohlcv(df)
                db_initializer = pr.get_db_initializer(code, name, ohlcv)
                db.initialize(db_initializer)
                self.data_initialized()
            except:
                self.skipped_data(code, name)
                uninitialized.append(code)
        pickle_out = open("./data/kospi-uninitialized.pickle", "wb")
        pickle.dump(uninitialized, pickle_out)
        self.kospi_ohlcv_initialized()
