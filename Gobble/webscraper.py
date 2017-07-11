import os, sys, re, random, datetime, time
import _pickle as pickle
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SejongScraper:
    """scrapes 2007-2016 financial statements data from Sejong Data,
       the company closes at 201707, future scrapers should find other source
       simply use to initialize Kospi/Kosdaq Value data"""

    def __init__(self):
        self.browser = webdriver.PhantomJS(executable_path=os.getcwd() + '/phantomjs.exe')
        self.main_window = self.browser.window_handles[0]
        self.url = "http://www.sejongdata.com/business/fin_fr_01.html?&no="

    def set_tasks(self):
        kospi_in = open("./data/kospi-dict.pickle", "rb")
        self.kospi_task = pickle.load(kospi_in)

        kosdaq_in = open("./data/kosdaq-dict.pickle", "rb")
        self.kosdaq_task = pickle.load(kosdaq_in)

    def _scrape_tables(self, code):
        browser = self.browser
        browser.get(self.url + code)
        iframes = browser.find_elements_by_tag_name("iframe")
        base_info = browser.find_element_by_class_name('bus_left_top').text

        # first iframe: 요약재무정보
        browser.switch_to.frame(iframes[0])
        tables = browser.find_elements_by_tag_name('table')
        self.a_table = tables[1].text # 요약재무정보

        # second iframe: 분기재무정보
        browser.switch_to_window(self.main_window)
        browser.switch_to.frame(iframes[1])
        tables = browser.find_elements_by_tag_name('table')
        self.q_table = tables[0].text # 분기재무정보

    def _parse_table_html(self, table_type):
        if table_type == "annual":
            table_list = self.a_table.split("\n")
            list_cut = -7
        elif table_type == "quarter":
            table_list = self.q_table.split("\n")
            list_cut = -6
        dates = table_list[:list_cut]
        dates = [int(date.split(" ")[-1].replace(".", "")) for date in dates[:-1]]
        dict_data = dict()
        dict_data["구간"] = dates
        for data_chunk in table_list[list_cut:]:
            data = data_chunk.split(" ")
            if (table_type == "quarter") & ((data[0] == "영업이익률") | (data[0] == "순이익률")):
                continue
            dict_data[data[0]] = [int(num.replace(",", "")) for num in data[1:]]
        df = pd.DataFrame.from_dict(dict_data)
        return df

    def _format_df_data(self, df):
        formatted = list()
        for i in range(len(df.index)):
            update_data = dict()
            keys = df.ix[i].index
            vals = df.ix[i].values.astype(int)
            for j in range(len(keys)):
                update_data[str(keys[j])] = int(vals[j])
            formatted.append(update_data)
        return formatted

    def create_value(self, code):
        self._scrape_tables(code)
        value_dict = dict()
        for table_type in ["annual", "quarter"]:
            df = self._parse_table_html(table_type)
            value = self._format_df_data(df)
            value_dict[table_type] = value
        return value_dict
