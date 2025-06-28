from flask import Flask
from threading import Thread
import os

app = Flask('')


@app.route('/')
def home():
    return "Hexa Bot is running."


def run():
    app.run(host='0.0.0.0', port=5050)


Thread(target=run).start()

import bot
