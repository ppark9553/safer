from kiwoom import Kiwoom
from dbwrapper import MongoDB
from pdreader import PDReader
from webscraper import SejongScraper
from processtracker import ProcessTracker, timeit

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import os, time, json
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
    def save_kospi_ohlcv(self):
        # task done by: pdreader.PDReader
        # roughly 35 minutes
        pr = self.pr
        self.saving_kospi_ohlcv()
        notsaved = list()
        for code, name in pr.task.items():
            try:
                self.starting_request(code, name)
                df = pr.request_df(code)
                ohlcv = pr.create_ohlcv(df)
                db_initializer = pr.get_db_initializer(code, name, ohlcv)
                with open("./data/stock/" + code + ".json", "w") as f:
                    json.dump(db_initializer, f)
                self.data_saved()
            except:
                self.skipped_data(code, name)
                notsaved.append(code)
        pickle_out = open("./data/kospi-notsaved.pickle", "wb")
        pickle.dump(notsaved, pickle_out)
        self.data_saved()

    @timeit
    def start_sejongscraper(self):
        self.ss = SejongScraper()
        self.ss.set_tasks()

    @timeit
    def save_financial_sejong(self, market_type):
        # task done by: webscraper.SejongScraper
        # do after saving kospi ohlcv
        ss = self.ss
        notsaved = list()
        task = ss.kospi_task if market_type == "kospi" else ss.kosdaq_task
        for code, name in task.items():
            try:
                value_dict = ss.create_value(code)
                with open("./data/stock/" + code + ".json") as f:
                    data = json.load(f)
                    data["annual"] = value_dict["annual"]
                    data["quarter"] = value_dict["quarter"]
                    json.dump(data, f)
            except:
                continue
                notsaved.append(code)
        pickle_out = open("./data/financial-notsaved.pickle", "wb")
        pickle.dump(notsaved, pickle_out)
