### Run on Python 3.4 ###
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import sys, time
import pandas as pd
from pymongo import MongoClient

# Kiwoom requires that you take at least 3.8 seconds before another request,
# (it's their new policy)
TR_REQ_TIME_INTERVAL = 3.8

# connection information for MongoDB
USER = "minestoned"
PW = "moneyisnoweverythingdawg"
IP = "45.55.86.183"
DB = "stock"

def timeit(method):
    """method timing decorator"""
    def timed(*args, **kwargs):
        ts = time.time()
        method(*args, **kwargs)
        te = time.time()
        print("Initialization took " + str(te-ts) + " seconds")
    return timed


class Kiwoom(QAxWidget):
    """Kiwoom class: connects to Kiwoom OpenAPI
       requests OHLCV, Buy, Sell data"""

    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def prepare_data(self):
        # prepares data for database insertion
        self.data = {"ohlcv": [], "buy": [], "sell": []}

    def _add_data(self, type, data):
        # adds data to front of each self.data list
        # for date sorting purposes
        self.data[type].insert(0, data)

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        # returns full code list of each markets:
        # 0: kospi, 10: kosdaq, 8: etf
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        # returns company name of each code you input
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        # setting input befor request calls
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        # committing all inputs set and requests data
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        # returns how many requests you have left till the end
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)
        elif rqname == "opt10059_req":
            self._opt10059(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            update_data = {"date": int(date), \
                           "open": int(open), \
                           "high": int(high), \
                           "low": int(low), \
                           "close": int(close), \
                           "volume": int(volume)}

            self._add_data("ohlcv", update_data)

    def _opt10059(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            individual = self._comm_get_data(trcode, "", rqname, i, "개인투자자")
            for_retail = self._comm_get_data(trcode, "", rqname, i, "외국인투자자")
            institution = self._comm_get_data(trcode, "", rqname, i, "기관계")
            financial = self._comm_get_data(trcode, "", rqname, i, "금융투자")
            insurance = self._comm_get_data(trcode, "", rqname, i, "보험")
            trust = self._comm_get_data(trcode, "", rqname, i, "투신")
            etc_finance = self._comm_get_data(trcode, "", rqname, i, "기타금융")
            bank = self._comm_get_data(trcode, "", rqname, i, "은행")
            pension = self._comm_get_data(trcode, "", rqname, i, "연기금등")
            private = self._comm_get_data(trcode, "", rqname, i, "사모펀드")
            nation = self._comm_get_data(trcode, "", rqname, i, "국가")
            etc_corporate = self._comm_get_data(trcode, "", rqname, i, "기타법인")
            foreign = self._comm_get_data(trcode, "", rqname, i, "내외국인")

            update_data = {"date": int(date), \
                           "individual": int(individual), \
                           "foreign_retail": int(for_retail), \
                           "institution": int(institution), \
                           "financial": int(financial), \
                           "insurance": int(insurance), \
                           "trust": int(trust), \
                           "etc_finance": int(etc_finance), \
                           "bank": int(bank), \
                           "pension": int(pension), \
                           "private": int(private), \
                           "nation": int(nation), \
                           "etc_corporate": int(etc_corporate), \
                           "foreign": int(foreign)}

            self._add_data(self.buysell_state, update_data)


class DataCollector:

    def __init__(self, user, password, ip_address, db_name):
        self.db_name = db_name
        self.mongo = MongoClient("mongodb://{0}:{1}@{2}/{3}".format(user, password, ip_address, db_name))

    def set_collection(self, collection):
        self.collection = self.mongo[self.db_name].data

    def _get_total_stock_num(self, kiwoom):
        total_stock_list = list()
        for market_type in [0, 10]:
            stock_list = kiwoom.get_code_list_by_market(str(market_type))
            total_stock_list += stock_list
        return len(total_stock_list)

    def initialize_db(self, kiwoom):
        total_stock_num = self._get_total_stock_num(kiwoom)
        code_looped = 0

        # get code list (0: KOSPI, 10: KOSDAQ)
        for market_type in [0, 10]:
            if market_type == 0:
                market = "kospi"
            elif market_type == 10:
                market = "kosdaq"
            code_list = kiwoom.get_code_list_by_market(str(market_type))

            for code in code_list:
                self._initialize_data(code, market, kiwoom)
                code_looped += 1
                stocks_left = str(total_stock_num - code_looped)
                print(stocks_left + " stocks left to initialize")
                print("---------------------------------------------------")

    @timeit
    def _initialize_data(self, code, market, kiwoom):
        global TR_REQ_TIME_INTERVAL

        name = kiwoom.get_master_code_name(code)
        time.sleep(TR_REQ_TIME_INTERVAL)
        print(code + ": " + name + " data initializing")
        kiwoom.prepare_data()

        # opt10081 TR 요청
        kiwoom.set_input_value("종목코드", code)
        kiwoom.set_input_value("기준일자", time.strftime('%Y%m%d'))
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(TR_REQ_TIME_INTERVAL)

        while kiwoom.remained_data == True:
            kiwoom.set_input_value("종목코드", code)
            kiwoom.set_input_value("기준일자", time.strftime('%Y%m%d'))
            kiwoom.set_input_value("수정주가구분", 1)
            kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
            time.sleep(TR_REQ_TIME_INTERVAL)
        print("OHLCV data initialized, ready for DB")

        for buysell in [1, 2]:
            if buysell == 1:
                kiwoom.buysell_state = "buy"
            elif buysell == 2:
                kiwoom.buysell_state = "sell"

            # opt10059 TR 요청
            kiwoom.set_input_value("일자", time.strftime('%Y%m%d'))
            kiwoom.set_input_value("종목코드", code)
            kiwoom.set_input_value("금액수량구분", 2)
            kiwoom.set_input_value("매매구분", buysell)
            kiwoom.set_input_value("단위구분", 1)
            kiwoom.comm_rq_data("opt10059_req", "opt10059", 0, "0101")
            time.sleep(TR_REQ_TIME_INTERVAL)

            while kiwoom.remained_data == True:
                kiwoom.set_input_value("일자", time.strftime('%Y%m%d'))
                kiwoom.set_input_value("종목코드", code)
                kiwoom.set_input_value("금액수량구분", 2)
                kiwoom.set_input_value("매매구분", buysell)
                kiwoom.set_input_value("단위구분", 1)
                kiwoom.comm_rq_data("opt10059_req", "opt10059", 2, "0101")
                time.sleep(TR_REQ_TIME_INTERVAL)
            if buysell == 1:
                print("BUY data initialized, ready for DB")
            elif buysell == 2:
                print("SELL data initialized, ready for DB")

        db_initializer = {"code": code, "name": name, "market": market, "ohlcv": kiwoom.data["ohlcv"], "buy": kiwoom.data["buy"], "sell": kiwoom.data["sell"]}
        self.collection.insert_one(db_initializer)
        print(code + ": " + name + " data successfully initialized")


if __name__ == "__main__":
    print(sys.argv)
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    # dc = DataCollector(USER, PW, IP, DB)
    # dc.set_collection("stock")
    # dc.initialize_db(kiwoom)
