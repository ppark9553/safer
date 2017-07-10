import pandas as pd
import pandas_datareader.data as web
import datetime
import pickle
import time
from pymongo import MongoClient

USER = "minestoned"
PW = "moneyisnoweverythingdawg"
IP = "45.55.86.183"
DB = "stock"

mongo = MongoClient("mongodb://{0}:{1}@{2}/{3}".format(USER, PW, IP, DB))
collection = mongo[DB].pandas

start = datetime.datetime(2012, 1, 1)
end = datetime.datetime(2017, 7, 9)

pickle_in = open("./data/kospi-dict.pickle","rb")
code_dict = pickle.load(pickle_in)

for code, name in code_dict.items():
    ts = time.time()
    df = web.DataReader("KRX:" + code, "google", start, end)
    df.columns = map(str.lower, df.columns)
    df['date'] = df.index.strftime("%Y%m%d").astype(int)
    df.index = range(len(df.index))

    ohlcv = list()
    for i in range(len(df.index)):
        update_data = dict()
        keys = df.ix[i].index
        vals = df.ix[i].values.astype(int)
        for j in range(len(keys)):
            update_data[str(keys[j])] = int(vals[j])
        ohlcv.append(update_data)
    db_initializer = {"code": code, "name": name, "market": "kospi", "ohlcv": ohlcv}
    collection.insert_one(db_initializer)
    print(code + ": " + name + " data successfully initialized")
    print("Took " + str(time.time() - ts) + " seconds")
    print("---------------------------------")
