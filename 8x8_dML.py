# date:2023.07.22.02..54

from machine import Pin,freq
import time
from dML_driver import dML
import dht

pin_clk = Pin(14, Pin.OUT, value=1) # 接D5脚,时钟，上升跳变时数据位移锁存
pin_cs  = Pin(15, Pin.OUT, value=1) # 接D8脚,上升跳变时，数据全部推入锁存
pin_din = Pin(13, Pin.OUT, value=1) # 接D7脚,待移入的数据
dml = dML(pin_clk, pin_cs, pin_din) # 实例化一个对象

# 获取实时温湿度
def tem_hum(pin):
    d = dht.DHT11(machine.Pin(pin))
    d.measure()
    return d.temperature(),d.humidity()

while True:
    tem, hum = tem_hum(4)
    col1 = dml.num_proc(tem)
    col2 = dml.num_proc(hum)
    
    # 显示温度
    for n in range(8):
        if n == 7:
            dml.write_data(n+1, 0b11110000) # 最后一行前四个灯亮，表示温度
        else:
            dml.write_data(n+1, col1[n])
    time.sleep(1)
    
    # 显示湿度
    for l in range(8):
        if l == 7:
            dml.write_data(l+1, 0b00001111) # 最后一行后四个灯亮，表示湿度
        else:
            dml.write_data(l+1, col2[l])
    time.sleep(1)