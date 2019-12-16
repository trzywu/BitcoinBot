import re
import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
from os import path
import os
import time
import pandas as pd
import threading
import tkinter
import matplotlib
import logging

import telegrambot  # python file with telegram token
'''
Something like this will work with your own token and chatID
bot_token = '3334123:ss123123asd'
bot_chatID = '1111111'
send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
response = requests.get(send_text)
return response.json()
'''

# declaring needed atribute for matplotlib
matplotlib.use('TkAgg')

threads = []
list_btc = list()
list_eth = list()
list_time = list()
list_all = list()

# website with prizes of BTC and ETH
url = 'https://cryptowat.ch/'
# headers for scapper
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}


def plikcsv():
    fields = ['Time', 'Bitcoin', 'Ethereum']
    filename = datetime.now()
    file_name = filename.strftime("%d-%b-%Y")
    file_name = str(file_name + '.csv')

    # check if file exist if yes then sleep for 3 sec, if not read file from last day 60 values

    if ((path.isfile(file_name))) == False:
        print("File does not exist")
        d_minus1 = datetime.today() - timedelta(days=1)
        d_minus1 = d_minus1.strftime("%d-%b-%Y")

        with open(file_name, 'w') as file:
            writer = csv.writer(file)
            try:
                with open(str(d_minus1) + '.csv', 'r') as fd:
                    csv_lenght = sum(1 for row in fd)
                    print("Lenght", csv_lenght)
                    csv_lenght_new = csv_lenght - 60
                    print("new", csv_lenght)
                    oldfile = str(d_minus1) + '.csv'
                    d_minus1dF = pd.read_csv(oldfile, skiprows=csv_lenght_new, header=None)
                    d_minus1dF.style.hide_index()
                    d_minus1dF.to_csv(file_name, index=False, header=None)
                    time.sleep(3)
            except:
                print("File with yesterday data not found")

    else:
        time.sleep(3)

    time.sleep(1)


def scrapper(n=1):
    while n == 1:
        filename = datetime.now()
        file_name = filename.strftime("%d-%b-%Y")
        file_name = str(file_name + '.csv')
        with open(file_name, 'a') as csv_file:

            data_writer = csv.writer(csv_file)

            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')

            price_eth = soup.find(title="Ethereum").get_text()
            price_btc = soup.find(title="Bitcoin").get_text()

            matches3 = re.finditer(r"um\d+[.]\d\d", price_eth)
            for match in matches3:
                string_eth = (match.group())
            price_eth = string_eth[2:]  # delete 'um' from list

            matches3 = re.finditer(r"in\d+[.]\d\d", price_btc)
            for match in matches3:
                string_btc = (match.group())
            price_btc = string_btc[2:]

            dateTimeObj = datetime.now()
            time_now = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            print(time_now)

            btc_price_str = 'Bitcoin: ' + price_btc
            eth_price_str = 'Ethernum: ' + price_eth
            price_btc = float(price_btc)
            price_eth = float(price_eth)
            print(price_btc)
            print(price_eth)

            telegrambot.telegram_bot_sendtext((eth_price_str + '\n' + str(btc_price_str)))
            print("Telegram send")

            list_btc.append(price_btc)
            list_eth.append(price_eth)
            list_time.append(time_now)

            list_all = [list_time[-1], list_btc[-1], list_eth[-1]]
            data_writer.writerow(list_all)
            csv_file.close()
            time.sleep(1)
            n = 0


def plotting():

    time.sleep(5)
    filename = datetime.now()
    file_name = filename.strftime("%d-%b-%Y")
    file_name = str(file_name + '.csv')

    ax1 = fig.add_subplot(1, 1, 1)
    nl = '\n'

    dataframe = pd.read_csv(file_name, names=["Time", "BTC", "ETH"])
    file_name = file_name[:len(file_name) - 4]

    t = dataframe['Time']
    y1 = dataframe['BTC'].astype(float)
    y1 = pd.to_numeric(y1, downcast='float')
    y2 = dataframe['ETH']
    ax1.clear()
    max_btc = y1.max()
    max_btc = float("{0:.2f}".format(max_btc))

    min_btc = y1.min()
    min_btc = float("{0:.2f}".format(min_btc))

    max_eth = y2.max()
    max_eth = float("{0:.2f}".format(max_eth))

    min_eth = y2.min()
    min_eth = float("{0:.2f}".format(min_eth))

    pd.plotting.register_matplotlib_converters()
    ax1.plot(t, y1, 'b-')
    ax1.set_xlabel(file_name)
    ax1.set_ylabel('BTC', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(t, y2, 'r-')
    ax2.set_ylabel('ETH', color='r')
    ax2.tick_params('y', colors='r')

    my_xticks = ax1.get_xticks()
    lenght_xaxis = len(my_xticks)
    middle_xaxis = int(lenght_xaxis / 2)

    plt.xticks([my_xticks[1], my_xticks[-1], my_xticks[middle_xaxis]], visible=True, rotation="horizontal")
    plt.text(0.15, 1.1, (f" Max BTC: {max_btc} Min BTC {min_btc}{nl}Max ETH: {max_eth} Min ETH {min_eth}"),
             ha='center', va='center', transform=ax1.transAxes)

    plt.tight_layout()
    plt.savefig(file_name + ".pdf")
    time.sleep(55)



def main():
    loop_counter = 1
    while loop_counter <= 20:

        t1 = threading.Thread(target=plikcsv)
        t1.setDaemon(True)
        t1.start()
        t2 = threading.Thread(target=scrapper)
        threads.append(t2)
        t2.start()
        t3 = threading.Thread(target=plotting)
        threads.append(t3)
        t3.start()
        for t in threads:
            t.join()
        loop_counter = loop_counter + 1
        print(f'loop_counter {loop_counter}')
        plt.clf()
        # making sure that matplotlib clear his cache
        if (loop_counter == 21):
            loop_counter = 0
        # savings log to txt file
        logging.basicConfig(filename="log.txt", level=logging.DEBUG, format='(asctime)s - %(levelname)s - %(message)s')
        time.sleep(2)


fig = plt.figure()
main()
