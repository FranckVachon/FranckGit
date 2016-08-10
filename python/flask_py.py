# from flask import Flask
# app = Flask(__name__)

#You can setup mutiple "routes", e.g. addresses at which flask will route traffic to accomplish certain tasks. You can have multiple tasks assigned to different URL. This is actually pretty awesome.

from flask import Flask
from flask.ext.cors import CORS
from flask_test_v15 import main
import json
app = Flask(__name__)
CORS(app)
@app.route("/test")
def run_script():
   answer = str(main())
   return answer 
if __name__ == "__main__":
   app.run()