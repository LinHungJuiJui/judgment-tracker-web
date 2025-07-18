import os
import json
import time
import datetime
import re
from flask import Flask, render_template_string, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
KEYWORD = "112重訴8"
RESULT_PATH = "results.json"


def crawl_judgment():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    base_url = "https://judgment.judicial.gov.tw/FJUD/default.aspx"
    driver.get(base_url)

    search_input = driver.find_element(By.ID, "txtKW")
    search_input.send_keys(KEYWORD)
    driver.find_element(By.ID, "btnSimpleQry").click()

    wait.until(EC.frame_to_be_available_and_switch_to_it(
        (By.ID, "iframe-data")))
    wait.until(EC.presence_of_element_located((By.ID, "jud")))

    result = []

    for page in range(1, 6):
        rows = driver.find_elements(By.XPATH, '//table[@id="jud"]/tbody/tr')
        for row in rows:
            try:
                text = row.text.strip()
                date_match = re.search(
                    r"((\d{3}|\d{4})[./年](\d{1,2})[./月](\d{1,2}))", text)
                if not date_match:
                    continue
                y, m, d = date_match.group(
                    2), date_match.group(3), date_match.group(4)
                year = int(y) + 1911 if len(y) == 3 else int(y)
                month = int(m)
                day = int(d)
                date_obj = datetime.date(year, month, day)
                if (datetime.date.today() - date_obj).days > 4:
                    continue

                case_match = re.search(r"(\d{3}年度.+?字第\d+號)", text)
                court_match = re.match(r"^\d+\.\s*(.*?)\d{3}年度", text)
                reason_match = re.search(
                    r"\d{1,3}[./年](\d{1,2})[./月](\d{1,2})\s+(.+)", text)

                result.append({
                    "裁判日期": f"{year}/{month:02d}/{day:02d}",
                    "法院": court_match.group(1).strip() if court_match else "(無法院)",
                    "案號": case_match.group(1) if case_match else "(無案號)",
                    "案由": reason_match.group(3).strip() if reason_match else "(未知案由)",
                    "原始內容": text
                })

            except:
                continue

        try:
            driver.find_element(By.ID, "hlNext").click()
            time.sleep(1.5)
        except:
            break

    driver.quit()

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


@app.route("/")
def index():
    if not os.path.exists(RESULT_PATH):
        data = crawl_judgment()
    else:
        with open(RESULT_PATH, encoding="utf-8") as f:
            data = json.load(f)

    with open("index.html", encoding="utf-8") as f:
        html_template = f.read()

    return render_template_string(html_template, results=data)


@app.route("/api/crawl")
def api_crawl():
    data = crawl_judgment()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
