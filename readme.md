# LTZone

## Installation instructions
### 1. Run the falsk server
In the main folder, execute:

```bash
python3 app.py
```

### 2. Run the Bokeh server
In another windows, execute:

```bash
bokeh serve start.py example.py --allow-websocket-origin=127.0.0.1:5000
```

In the browser, the web app can now be called via the IP 127.0.0.1:5000. You can reach the start page for the data upload via 127.0.0.1:5000/start and the page with the example values via 127.0.0.1:5000/example.
