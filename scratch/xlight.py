from openclem import xlightv2
import time

xlight = xlightv2.XLightV2()
xlight.connect()
xlight.disk_onoff(0)
time.sleep(3)
xlight.disk_position(0)
print(xlight.get_status())
xlight.disk_position(1)
xlight.disk_onoff(0)
# xlight.emission_filter(0)
xlight.disconnect()

