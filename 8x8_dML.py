# date:2023.07.22.02..54

from machine import Pin,freq
import time
from dML_driver import num_proc
import dht

pin_clk = Pin(14, Pin.OUT, value=1) #接D5脚,时钟，上升跳变时数据位移锁存
pin_cs  = Pin(15, Pin.OUT, value=1) #接D8脚,上升跳变时，数据全部推入锁存
pin_din = Pin(13, Pin.OUT, value=1) #接D7脚,待移入的数据

# 获取实时温湿度
def tem_hum(pin):
    d = dht.DHT11(machine.Pin(pin))
    d.measure()
    return d.temperature(),d.humidity()

# 按位移入数据到模块
def write_byte(data):
    pin_cs.off()
    for i in range(8):
        pin_clk.off()
        pin_din.value(1 if ((data << i) & 0x80) else 0)  # 从高位开始送数据
        pin_clk.on()
        
# 写入地址和对应的数据
def write_data(addr, data):
    pin_cs.off()
    write_byte(addr)
    write_byte(data)
    time.sleep_us(5)
    pin_cs.on()

# 初始化模块
def init_max7219():
    write_data(0x0c, 0x00)  #关断处于关闭状态 
    write_data(0x0f, 0x00)  #不测试
    write_data(0x0b, 0x07)  #扫描所有位码
    write_data(0x0a, 0x0F)  #亮度0x07，半亮
    write_data(0x09, 0x00)  #不译码
    write_data(0x0c, 0x01)  #关断处于显示状态 

time.sleep_ms(50)
init_max7219()

while True:
    tem, hum = tem_hum(2)
    col1 = num_proc(tem)
    col2 = num_proc(hum)
    
    # 显示温度
    for n in range(8):
        if n == 7:
            write_data(n+1, 0b11110000) # 最后一行前四个灯亮，表示温度
        else:
            write_data(n+1, col1[n])
    time.sleep(1)
    
    # 显示湿度
    for l in range(8):
        if l == 7:
            write_data(l+1, 0b00001111) # 最后一行后四个灯亮，表示湿度
        else:
            write_data(l+1, col2[l])
    time.sleep(1)
