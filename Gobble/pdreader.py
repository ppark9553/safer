import _pickle as pickle
import datetime
import pandas as pd
import pandas_datareader.data as web


class PDReader:
    """initializes Kospi OHLCV data
       updates Kospi OHLCV data"""

    def __init__(self, start, end):
        start_y = int(start[:4])
        start_m = int(start[4:6])
        start_d = int(start[6:])
        end_y = int(end[:4])
        end_m = int(end[4:6])
        end_d = int(end[6:])
        self.start = datetime.datetime(start_y, start_m, start_d)
        self.end = datetime.datetime(end_y, end_m, end_d)

    def set_task(self):
        pickle_in = open("./data/kospi-dict.pickle", "rb")
        self.task = pickle.load(pickle_in)

    def request_df(self, code):
        df = web.DataReader("KRX:" + code, "google", self.start, self.end)
        df.columns = map(str.lower, df.columns)
        df['date'] = df.index.strftime("%Y%m%d").astype(int)
        df.index = range(len(df.index))
        return df

    def create_ohlcv(self, df):
        ohlcv = list()
        for i in range(len(df.index)):
            update_data = dict()
            keys = df.ix[i].index
            vals = df.ix[i].values.astype(int)
            for j in range(len(keys)):
                update_data[str(keys[j])] = int(vals[j])
            ohlcv.append(update_data)
        return ohlcv

    def get_db_initializer(self, code, name, ohlcv):
        return {"code": code, "name": name, "market": "kospi", "ohlcv": ohlcv}
