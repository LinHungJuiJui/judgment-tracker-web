import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime


def run_crawler():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    keyword = "家福"
    base_url = "https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/qryresult.aspx?judtype=JUDBOOK&sys=V&page="

    found = []

    for page in range(1, 6):
        url = base_url + str(page)
        driver.get(url)
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 5:
                continue
            court = tds[0].text.strip()
            date = tds[1].text.strip()
            case_no = tds[2].text.strip()
            reason = tds[3].text.strip()
            summary = tds[4].text.strip()

            if keyword in summary or keyword in reason or keyword in case_no:
                try:
                    link = row.find_element(
                        By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "(無連結)"
                found.append({
                    "法院": court,
                    "案號": case_no,
                    "裁判日期": date,
                    "事由": reason,
                    "摘要": summary,
                    "連結": link
                })

    driver.quit()

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump({
            "keyword": keyword,
            "last_updated": datetime.now().isoformat(),
            "results": found
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_crawler()
