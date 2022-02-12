#flask app

from flask import Flask, render_template
from bokeh.embed import server_session
from bokeh.client import pull_session

#instatiate the flask app
app = Flask(__name__)

url = "http://127.0.0.1:5006"

#create example page function
@app.route("/example")
def example():
    session=pull_session(url=url + "/example")
    bokeh_script=server_session(None,url=url + "/example", session_id=session.id)
    return render_template("example.html", bokeh_script=bokeh_script)

#create example page function
@app.route("/start")
def start():
    session=pull_session(url=url + "/start")
    bokeh_script=server_session(None,url=url + "/start", session_id=session.id)
    return render_template("start.html", bokeh_script=bokeh_script)

#create example page function
@app.route("/")
def introduction():
    session=pull_session(url=url + "/example")
    bokeh_script=server_session(None,url=url + "/example", session_id=session.id)
    return render_template("example.html", bokeh_script=bokeh_script)


#run the app
if __name__ == "__main__":
    app.run(debug=True)
