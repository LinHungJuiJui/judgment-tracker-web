from flask import Flask, render_template
import json
import os
from judgment_scraper import run_judgment_by_case  # ✅ 自動呼叫爬蟲函數

app = Flask(__name__, template_folder='.')


@app.route("/")
def index():
    keyword = "112重訴8"
    json_path = os.path.join("data", "results.json")

    # ✅ 每次刷新都重新爬一次
    run_judgment_by_case(keyword=keyword, output_path=json_path)

    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("results", [])
    else:
        results = []

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
