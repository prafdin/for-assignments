import os
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

DEPLOY_DATE = datetime.now().strftime("%Y%m%d%H%M%S")
DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")

@app.route("/")
def index():
    return render_template(
        "index.html",
        deployref=DEPLOY_REF
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
