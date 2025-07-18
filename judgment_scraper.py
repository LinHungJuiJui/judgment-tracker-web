import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def run_judgment_by_case(keyword="112重訴8", output_path="data/results.json"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    print(f"🔍 啟動 Selenium，搜尋裁判字號：{keyword}")
    base_url = "https://judgment.judicial.gov.tw/FJUD/default.aspx"
    driver.get(base_url)
    print("✅ 開啟裁判書查詢頁面")

    # 輸入字號並查詢
    search_input = driver.find_element(By.ID, "txtKW")
    search_input.send_keys(keyword)
    driver.find_element(By.ID, "btnSimpleQry").click()
    print("✅ 查詢送出")

    wait.until(EC.frame_to_be_available_and_switch_to_it(
        (By.ID, "iframe-data")))
    wait.until(EC.presence_of_element_located((By.ID, "jud")))
    print("✅ 成功進入 iframe 查詢結果")

    result = []
    for page in range(1, 6):
        print(f"📄 處理第 {page} 頁")
        rows = driver.find_elements(By.XPATH, '//table[@id="jud"]/tbody/tr')
        for row in rows:
            text = row.text.strip()
            if not text or "裁判字號" in text:
                continue
            parts = text.split()
            try:
                date_str = parts[-2]
                date_obj = datetime.datetime.strptime(
                    date_str, "%Y.%m.%d").date()
                if (datetime.date.today() - date_obj).days > 5:
                    continue
                link = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                result.append({
                    "裁判日期": str(date_obj),
                    "法院": parts[1],
                    "案號": parts[2],
                    "事由": parts[-1],
                    "摘要": text,
                    "連結": link
                })
            except Exception as e:
                continue

        try:
            next_btn = driver.find_element(By.ID, "hlNext")
            next_btn.click()
            time.sleep(1)
        except:
            break

    driver.quit()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "keyword": keyword,
            "last_updated": datetime.datetime.now().isoformat(),
            "results": result
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 共找到 {len(result)} 筆資料，已儲存到 {output_path}")
