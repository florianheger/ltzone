# LT-Zone

## Installation instructions

### 1. Install the required packages
Install the required packages in the main folder using the requirements.txt:
```bash
pip -r requirements.txt
```

### 2. Run the falsk server
In the main folder, execute:

```bash
python app.py
```

### 3. Run the Bokeh server
In another window, execute:

```bash
bokeh serve start.py example.py --allow-websocket-origin=127.0.0.1:5000
```

In the browser, the web app can now be called via the IP 127.0.0.1:5000. You can reach the start page for the data upload via 127.0.0.1:5000/start and the page with the example values via 127.0.0.1:5000/example.
