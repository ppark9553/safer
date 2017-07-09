import sys, time, sqlite3
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        # creating COM object for Kiwoom OpenAPI+
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        # connect slots(our functions) to events(from server)
        # specifies slots that will specifically handle server events
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        # using Kiwoom API requires log in
        # manually login after calling CommConnect() funtion dynamically
        self.dynamicCall("CommConnect()")

        # creating event loop, because no visible GUI for PyQt
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        # handles _event_connect method after OnEventConnect(log in) event
        # receives err_code from Kiwoom server
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        # returns codes list by market types:
        # 0 - KOSPI, 10 - KOSDAQ, 8 - ETF
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        # returns company name as code is given as input
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
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
        # requests daily open, high, low, close, volume data

        date = self._comm_get_data(trcode, "", rqname, 0, "일자")
        open = self._comm_get_data(trcode, "", rqname, 0, "시가")
        high = self._comm_get_data(trcode, "", rqname, 0, "고가")
        low = self._comm_get_data(trcode, "", rqname, 0, "저가")
        close = self._comm_get_data(trcode, "", rqname, 0, "현재가")
        volume = self._comm_get_data(trcode, "", rqname, 0, "거래량")

        kiwoom.values = [str(date), str(open), str(high), str(low), str(close), str(volume)]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    # get code list (0: KOSPI, 10: KOSDAQ, 8: ETF)
    for market_type in [0, 10, 8]:
        code_list = kiwoom.get_code_list_by_market(str(market_type))
        time.sleep(TR_REQ_TIME_INTERVAL)

        ### ohlcv data ###
        for code in code_list:
            name = kiwoom.get_master_code_name(code)
            time.sleep(TR_REQ_TIME_INTERVAL)

            if market_type == 0:
                db_name = 'kospi.db'
            elif market_type == 10:
                db_name = 'kosdaq.db'
            elif market_type == 8:
                db_name = 'etf.db'
            con = sqlite3.connect(db_name)
            cursor = con.cursor()
            table_exists = cursor.execute('SELECT * FROM sqlite_master WHERE type = "table" AND name = ' + '"' + code + '_' + name + '";').fetchone()

            if table_exists == None:
                cursor.execute("CREATE TABLE '" + code + "_" + name + "' (Date text, Open int, High int, Low int, Closing int, Volume int);")

            print(code + ': ' + name + ' request starting')

            # opt10081 TR 요청
            kiwoom.set_input_value("종목코드", code)
            kiwoom.set_input_value("기준일자", time.strftime('%Y%m%d'))
            kiwoom.set_input_value("수정주가구분", 1)
            kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

            print(kiwoom.values)

            cursor.execute("INSERT INTO '" + code + "_" + name + "' VALUES ('" + kiwoom.values[0] + "'," + kiwoom.values[1] + "," + kiwoom.values[2] + "," + kiwoom.values[3] + "," + kiwoom.values[4] + "," + kiwoom.values[5] + ");")
            con.commit()
            con.close()

            print('All requests successful, now saving into database')
            print('Finished updating ' + code + '_' + name + ' table in ' + db_name + ' database')
            print('\n')
