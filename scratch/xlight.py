from openclem import xlightv2
import time

xlight = xlightv2.XLightV2()
xlight.connect()
print(xlight.get_status())
xlight.disk_position(0)
xlight.disk_onoff(0)
# time.sleep(3)
# xlight.disk_position(1)
# xlight.disk_onoff(1)
xlight.emission_filter(1)
print(xlight.get_status())
xlight.disconnect()



#49.8549 x
#0.1537 y