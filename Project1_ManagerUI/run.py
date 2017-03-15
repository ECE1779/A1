#!venv/bin/python
from app import webapp
from app import autoscale
import threading
#webapp.run(host='0.0.0.0',debug=True)
monitor_process = threading.Thread(target=autoscale.background_monitor)
monitor_process.start()
webapp.run(host='0.0.0.0')
