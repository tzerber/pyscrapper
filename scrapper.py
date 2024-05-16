from flask import Flask, request, jsonify
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Dictionary to store the statistics for different combinations of ID and name
statistics_data = {}
playernames = ["1/1", "2,2", "3/3" ]

@app.route('/statistics')
def get_statistics():
        global statistics_data
        return jsonify(statistics_data)

@app.route('/update_playernames', methods=['POST'])
def update_playernames():
    global playernames
    global statistics_data
    new_playernames = request.json.get('playernames')
    if new_playernames is not None and isinstance(new_playernames, list):
        playernames = new_playernames
        statistics_data = {} # delete old stats
        return jsonify({'message': 'Player names updated successfully', 'playernames': playernames}), 200
    else:
        return jsonify({'error': 'Invalid request format'}), 400

@app.route('/scrape', methods=['POST'])
def scrape_statistics():
    global statistics_data
    global playernames
    url_base = "https://www.hltv.org/stats/players"
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/home/kaloyan/.config/google-chrome2")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    for id_name in playernames:
        url = url_base + "/" + id_name
        driver.get(url)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the div with class 'statistics'
        statistics_div = soup.find('div', class_='statistics')
        if statistics_div:
            # Find all divs with class 'col stats-rows standard-box'
            columns_divs = statistics_div.find_all('div', class_='col stats-rows standard-box')
            stats = {}
            for column_div in columns_divs:
                # Extract statistics from each column div
                
                for stat_row in column_div.find_all('div', class_='stats-row'):
                    stat_name = stat_row.find('span').text
                    stat_value = stat_row.find_all('span')[1].text
                    stats[stat_name] = stat_value

                # Store the statistics in the dictionary
                statistics_data[id_name] = stats
        else:
            print("No statistics found for:", id_name)
    driver.close()
    return "Success", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0")
