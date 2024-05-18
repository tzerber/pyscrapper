#curl -X POST -H "Content-Type: application/json" -d '{"playernames": ["20113/deko", "20709/r3salt", "19236/kensi","19882/norwi"]}' http://10.0.1.169:5000/update_playernames
#curl -X POST -H "Content-Type: application/json" http://10.0.1.169:5000/scrape
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import subprocess
import logging
import time
import os
import tempfile
os.environ['XAUTHORITY'] = '/root/.Xauthority'

app = Flask("HLTV Scraper")

logging.basicConfig(level=logging.INFO)

statistics_data = {}
upcoming_data = {}
team_data = {}
matches_data = {}
playernames = {}

display = Display(visible=0, size=(1280, 1024)).start()

def write_long_text_to_tmp_file(text):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(text.encode('utf-8'))
        tmp_filename = tmp_file.name
    return tmp_filename

def remove_last_lines_from_file(filename, lines_to_remove):
    with open(filename, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(lines[:-lines_to_remove])

def read_tmp_file_as_string(filename):
    with open(filename, 'r') as file:
        return file.read()
    
def append_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(text)
    
@app.route('/system/reload')
def reload():
    if subprocess.call( [ "killall", "-9", "firefox-bin" ] ) > 0:
        return(jsonify({'error':'Firefox cleanup - FAILURE!'})), 500
    else:
        return(jsonify({'message':'Firefox cleanup - SUCCESS!'})), 200


@app.route('/system/accept_cookies')
def accept_cookies():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'
    profile_arg_param = '-profile'
    profile_arg_value = os.getenv('HOME') + '/snap/firefox/common/.mozilla/firefox/Selenium'
    options.add_argument(profile_arg_param)
    options.add_argument(profile_arg_value)
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    driver.implicitly_wait(10)
    driver.get("https://www.hltv.org/stats/players")
    time.sleep(5)
    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialog"]')))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))).click()
        logging.debug('Accepted cookies consent')
        return jsonify({'message': 'Cookies Accepted'}), 200
    except Exception as e:
        logging.debug(f'Cookies consent button not found or already accepted: {e}')
        return jsonify({'message': 'Cookies already Accepted'}), 200

    finally:
        driver.quit()
    

@app.route('/players/update_playernames', methods=['POST'])
def update_playernames():
    global playernames
    global statistics_data
    new_playernames = request.json.get('playernames')
    if new_playernames is not None and isinstance(new_playernames, list):
        playernames = new_playernames
        statistics_data = {}
        return jsonify({'message': 'Player names updated successfully', 'playernames': playernames}), 200
    else:
        return jsonify({'error': 'Invalid request format'}), 400

@app.route('/players/statistics')
def get_statistics():
        global statistics_data
        return jsonify(statistics_data)

@app.route('/players/scrape', methods=['POST'])
def scrape_statistics():
    global statistics_data
    global playernames
    url_base = "https://www.hltv.org/stats/players"
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'
    profile_arg_param = '-profile'
    profile_arg_value = os.getenv('HOME') + '/snap/firefox/common/.mozilla/firefox/Selenium'
    options.add_argument(profile_arg_param)
    options.add_argument(profile_arg_value)
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    driver.implicitly_wait(10)

    for id_name in playernames:
        url = url_base + "/" + id_name
        driver.get(url)
        time.sleep(15)
        accept_cookies() 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        statistics_div = soup.find('div', class_='statistics')
        if statistics_div:
            columns_divs = statistics_div.find_all('div', class_='col stats-rows standard-box')
            stats = {}
            for column_div in columns_divs:
                for stat_row in column_div.find_all('div', class_='stats-row'):
                    stat_name = stat_row.find('span').text
                    stat_value = stat_row.find_all('span')[1].text
                    stats[stat_name] = stat_value
                statistics_data[id_name] = stats
        else:
            print("No statistics found for:", id_name)
    driver.close()
    return jsonify({'result': 'Success'}), 200

@app.route('/upcoming/uri', methods=['POST'])
def scrape_and_store():
    global upcoming_data
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'
    profile_arg_param = '-profile'
    profile_arg_value = os.getenv('HOME') + '/snap/firefox/common/.mozilla/firefox/Selenium'
    options.add_argument(profile_arg_param)
    options.add_argument(profile_arg_value)
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    driver.implicitly_wait(10)
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        driver.get(url)
        time.sleep(8)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        left_player = soup.select_one('.lineups-compare-left .lineups-compare-playername').text.strip()
        left_rating = soup.select_one('.lineups-compare-middle-table-stat.left-stat.best-stat').text.strip()
        right_player = soup.select_one('.lineups-compare-right .lineups-compare-playername').text.strip()
        right_rating = soup.select('.lineups-compare-middle-table-stat.right-stat')[-1].text.strip()
        upcoming_data = {
            'left': {
                'name': left_player,
                'rating': left_rating
            },
            'right': {
                'name': right_player,
                'rating': right_rating
            }
        }
        return jsonify({'message': 'Data scraped and stored successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        driver.quit()

@app.route('/upcoming/rating', methods=['GET'])
def get_upcoming_data():
    return jsonify(upcoming_data)

@app.route('/team/uri', methods=['POST'])
def scrape_and_store_team():
    global team_data
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'
    profile_arg_param = '-profile'
    profile_arg_value = os.getenv('HOME') + '/snap/firefox/common/.mozilla/firefox/Selenium'
    options.add_argument(profile_arg_param)
    options.add_argument(profile_arg_value)
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    driver.implicitly_wait(10)
    data = request.json
    logging.debug(f'Received data: {data}')
    
    url = data.get('url')
    logging.debug(f'Extracted URL: {url}')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        logging.debug(f'Navigating to team URL: {url}')
        driver.get(url)
        time.sleep(8)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        player_links = []
        for a_tag in soup.select('.playersBox-wrapper .playersBox-first-cell a'):
            player_href = a_tag['href'].replace('/player/', '/players/')
            full_url = f'https://www.hltv.org/stats{player_href}'
            player_links.append(full_url)
        
        logging.info(f'Extracted player links: {player_links}')
        time.sleep(3)
        player_ratings = {}
        for player_url in player_links:
            logging.info(f'Navigating to player URL: {player_url}')
            driver.get(player_url)
            accept_cookies()
            player_html = driver.page_source
            player_soup = BeautifulSoup(player_html, 'html.parser')
            player_name_element = player_soup.select_one('.context-item-name')
            rating_element = player_soup.select_one('.stats-row:contains("Rating 2.0") .strong') or player_soup.select_one('.stats-row:contains("Rating 1.0") .strong')

            if player_name_element:
                player_name = player_name_element.text.strip()
                if rating_element:
                    rating = rating_element.text.strip()
                else:
                    rating = 'N/A'
                player_ratings[player_name] = rating
                logging.info(f'Extracted rating for {player_name}: {rating}')
            else:
                logging.warning(f'Could not find player name or rating for URL: {player_url}')
                logging.debug(f'Player page HTML: {player_html}')
            
            time.sleep(8)

        team_data = player_ratings
        logging.debug(f'Stored team data: {team_data}')
        return jsonify({'message': 'Data scraped and stored successfully'}), 200

    except Exception as e:
        logging.error(f'Error during team scraping: {e}')
        return jsonify({'error': str(e)}), 500

    finally:
        driver.quit()

@app.route('/team/rating', methods=['GET'])
def get_team_data():
    return jsonify(team_data)

@app.route('/matches/uri', methods=['POST'])
def scrape_match():
    global matches_data
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'
    profile_arg_param = '-profile'
    profile_arg_value = os.getenv('HOME') + '/snap/firefox/common/.mozilla/firefox/Selenium'
    options.add_argument(profile_arg_param)
    options.add_argument(profile_arg_value)
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=options, service=service)
    driver.implicitly_wait(10)

    try:
        driver.get(url)
        time.sleep(8)
        accept_cookies()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        match_stats_div = soup.find('div', {"id": "all-content"})
        if not match_stats_div:
            logging.error('Match stats div not found')
            return jsonify({'error': 'Match stats div not found'}), 404
        table = match_stats_div.find_all('table', class_='totalstats')
        if not table:
            logging.error('Stats table not found')
            return jsonify({'error': 'Stats table not found'}), 404
        match_stats_div.find('table', class_='hidden').extract()
        match_stats_div.find('table', class_='hidden').extract()
        match_stats_div.find_next('table', class_='hidden').extract()
        tmp_filename = write_long_text_to_tmp_file(str(match_stats_div))
        remove_last_lines_from_file(tmp_filename, 78)
        append_to_file(tmp_filename, "</div>")
        var = BeautifulSoup(read_tmp_file_as_string(tmp_filename), 'html.parser')
        match_stats_div2 = var.find('div', {"id": "all-content"})
        os.remove(tmp_filename)
        matches_data = {}
        player_rows = match_stats_div2.find_all('tr', class_='')
        if not player_rows:
            logging.error('Player rows not found')
            return jsonify({'error': 'Player rows not found'}), 404

        for row in player_rows:
            player_cell = row.find('td', class_='players')
            if player_cell:
                player_name_div = player_cell.find('div', class_='smartphone-only statsPlayerName')
                if player_name_div:
                    player_name = player_name_div.text.strip()
                    rating_cell = row.find('td', class_='rating text-center')
                    if rating_cell:
                        player_rating = rating_cell.text.strip()
                        logging.info(f'Player: {player_name}, Rating: {player_rating}')
                        matches_data[player_name] = player_rating
                    else:
                        logging.error('Rating cell not found in row')
                else:
                    logging.error('Player name div not found in row')

        return jsonify({'message': 'Data scraped and stored successfully', 'data': matches_data}), 200

    except Exception as e:
        logging.error(f'Error during match scraping: {e}')
        return jsonify({'error': str(e)}), 500

    finally:
        driver.quit()

@app.route('/matches/rating')
def get_match_data():
    global matches_data
    return jsonify(matches_data)
  
if __name__ == '__main__':
    app.run(host="0.0.0.0")
