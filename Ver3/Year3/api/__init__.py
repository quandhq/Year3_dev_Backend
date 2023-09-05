from .djangoClient import Mqtt
import sys

if 'runserver' in sys.argv:
    print("Running __init__.py ............")
    # client1 = Mqtt("10.14.79.13", 1883, "farm/1/monitor", "api_sensormonitor",)
    # client1.run()