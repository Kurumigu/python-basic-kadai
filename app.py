from dotenv import load_dotenv
import os

load_dotenv()  # .env読み込み
api_key = os.getenv("OPENAI_API_KEY")

import html
import json
import requests
# flaskモジュールからFlaskクラス、requestオブジェクト、render_template関数をインポートする
from flask import Flask, request, render_template

# Flaskクラスのインスタンスを作成する
app = Flask(__name__)

# FlaskアプリのルートURL("/")にアクセスしたときの処理
@app.route("/", methods=["GET", "POST"])
def index():
    # OpenAIのAPIキー

    # OpenAI APIのエンドポイント
    url = "https://api.openai.com/v1/chat/completions"

    # APIからの返答内容を格納する変数
    answer = None

    # エラー内容を格納する変数
    error_message = None

    # 「フォームの初期値として表示する前回の質問」を格納するための変数（初回アクセス時は空欄）
    old_question = ""
    user_question = ""

    # HTTPリクエストメソッドがPOSTのとき（「質問する」ボタンを押したとき）の処理
    if request.method == "POST":
        # フォームからの入力値を取得する
        user_question = request.form.get("question", "")
        old_question = html.escape(user_question)

    # HTTPヘッダーの内容
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # HTTPリクエストのPostメソッドで送信するデータ
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content":"語尾がおかしい友人風に返答して。"},
            {"role": "user", "content": user_question}
        ],
        "max_tokens":500
    }

    try:
        # OpenAI APIにHTTPリクエストを送信し、HTTPレスポンスを取得する
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # HTTPステータスコードをチェックし、200番台（成功）以外の場合は例外を発生させる
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # 例外が発生した場合、そのエラー内容を返す（ネットワークエラーなど）
        error_message = f"HTTPリクエストエラー: {html.escape(str(e))}"
    else:
        # 例外が発生しなかった場合、JSON形式のHTTPレスポンスをPython辞書型に変換する
        result = response.json()
        if "error" in result:
            # HTTPレスポンスにエラーが含まれていれば、そのエラー内容を返す(OpenAI API側のエラー)
            api_error_message = result["error"].get("message", "原因不明のエラー")
            error_message = f"APIエラー: {api_error_message}"
        else:
            content = result.get("choices", [{}])[0].get("message", {}).get("content")
            if content:
                # contentが存在する場合、その内容(ChatGPTからの返答内容)を返す
                answer = html.escape(content)
            else:
                # contentが存在しない場合は何らかのエラーが発生しているため、HTTPレスポンスの内容をそのまま返す
                error_message = f"エラー: {html.escape(json.dumps(result, ensure_ascii=False))}"

    # テンプレートファイルをレンダリングしてHTMLを返す
    return render_template("index.html", answer=answer, error_message=error_message, old_question=old_question)        
# このファイルが直接実行された場合、Flaskアプリとして起動する（デフォルトではポート番号5000）
if __name__ == "__main__":
    app.run(debug=True)