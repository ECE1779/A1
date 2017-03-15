#!venv/bin/python
from app import webapp
from app import autoscale
import threading
high_threshold = 30
low_threshold = 20

grow_ratio=2
shrink_ratio=2
#webapp.run(host='0.0.0.0',debug=True)
monitor_process = threading.Thread(target=autoscale.background_monitor)
monitor_process.start()
webapp.run(host='0.0.0.0')
