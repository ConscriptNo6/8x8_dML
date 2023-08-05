# date:2023.08.05.08..20

from machine import Pin
import time

'''
一个简单的实例
A simple example

>>>from machine import Pin
>>>from dML_driver import dML

>>>clk = Pin(14, Pin.OUT, value=1)
>>>cs  = Pin(15, Pin.OUT, value=1)
>>>din = Pin(13, Pin.OUT, value=1)

>>>dml = dML(clk, cs, din)
>>>col = dml.num_proc(84)
>>>for n in range(8):
...         dml.write_data(n+1, col[n])
'''

class dML:
    def __init__(self, pin_clk, pin_cs, pin_din):
        self.clk = pin_clk
        self.cs = pin_cs
        self.din = pin_din
        
        # 左半屏，十位数，二进制
        self.col1 = [
            0b00000000,0b01000000,0b01000000,0b01000000,0b01000000,0b01000000,0b00000000,0b00000000, # 1
            0b00000000,0b11100000,0b00100000,0b11100000,0b10000000,0b11100000,0b00000000,0b00000000, # 2
            0b00000000,0b11100000,0b00100000,0b11100000,0b00100000,0b11100000,0b00000000,0b00000000, # 3
            0b00000000,0b10100000,0b10100000,0b11100000,0b00100000,0b00100000,0b00000000,0b00000000, # 4
            0b00000000,0b11100000,0b10000000,0b11100000,0b00100000,0b11100000,0b00000000,0b00000000, # 5
            0b00000000,0b11100000,0b10000000,0b11100000,0b10100000,0b11100000,0b00000000,0b00000000, # 6
            0b00000000,0b11100000,0b00100000,0b00100000,0b00100000,0b00100000,0b00000000,0b00000000, # 7
            0b00000000,0b11100000,0b10100000,0b11100000,0b10100000,0b11100000,0b00000000,0b00000000, # 8
            0b00000000,0b11100000,0b10100000,0b11100000,0b00100000,0b11100000,0b00000000,0b00000000, # 9
            0b00000000,0b11100000,0b10100000,0b10100000,0b10100000,0b11100000,0b00000000,0b00000000, # 0
        ]

        # 右半屏，个位数，二进制
        self.col2 = [
            0b00000000,0b00000010,0b00000010,0b00000010,0b00000010,0b00000010,0b00000000,0b00000000, # 1
            0b00000000,0b00000111,0b00000001,0b00000111,0b00000100,0b00000111,0b00000000,0b00000000, # 2
            0b00000000,0b00000111,0b00000001,0b00000111,0b00000001,0b00000111,0b00000000,0b00000000, # 3
            0b00000000,0b00000101,0b00000101,0b00000111,0b00000001,0b00000001,0b00000000,0b00000000, # 4
            0b00000000,0b00000111,0b00000100,0b00000111,0b00000001,0b00000111,0b00000000,0b00000000, # 5
            0b00000000,0b00000111,0b00000100,0b00000111,0b00000101,0b00000111,0b00000000,0b00000000, # 6
            0b00000000,0b00000111,0b00000001,0b00000001,0b00000001,0b00000001,0b00000000,0b00000000, # 7
            0b00000000,0b00000111,0b00000101,0b00000111,0b00000101,0b00000111,0b00000000,0b00000000, # 8
            0b00000000,0b00000111,0b00000101,0b00000111,0b00000001,0b00000111,0b00000000,0b00000000, # 9
            0b00000000,0b00000111,0b00000101,0b00000101,0b00000101,0b00000111,0b00000000,0b00000000, # 0
        ]

        # 初始化模块
        self.write_data(0x0c, 0x00)  # 关断处于关闭状态 
        self.write_data(0x0f, 0x00)  # 不测试
        self.write_data(0x0b, 0x07)  # 扫描所有位码
        self.write_data(0x0a, 0x0F)  # 亮度0x07，半亮
        self.write_data(0x09, 0x00)  # 不译码
        self.write_data(0x0c, 0x01)  # 关断处于显示状态 

    def write_byte(self, data):
        '''按位移入数据到模块'''
        self.cs.off()
        for i in range(8):
            self.clk.off()
            self.din.value(1 if ((data << i) & 0x80) else 0)  # 从高位开始送数据
            self.clk.on()
            
    def write_data(self, addr, data):
        '''写入地址和对应的数据'''
        self.cs.off()
        self.write_byte(addr)
        self.write_byte(data)
        time.sleep_us(5)
        self.cs.on()

    def format_binary(self, i, width):
        '''esp8266固件format函数不可用，模拟format函数'''
        binary_str = bin(i)[2:]  # 将整数转换为二进制字符串，去掉前缀 '0b'
        padded_str = '0' * (width - len(binary_str)) + binary_str  # 使用 '0' 在左侧填充字符串至指定宽度
        return padded_str
    
    def num_comb(self, num):
        '''将数字十位和个位拆开后按col1和col2分别转换成两个八位二进制数，
        再将十位数的前四位和个位数的后四位进行拼接，
        最后得到一个长度为8的列表'''
        decimal_number = str(num)
        
        # 如果传入的是一位数字，则十位用0补全
        if len(decimal_number) == 1:
            ones_digit = int(decimal_number[0])
            tens_digit = 0
        else:
            ones_digit = int(decimal_number[1])
            tens_digit = int(decimal_number[0])

        list_col1= []
        list_col2 = []
        list_fin = []
        
        # 判断个位数是否为0
        if ones_digit == 0:
            for i in self.col2[72:80]:
                list_col2.append(self.format_binary(i, 8))
        else:
            for j in self.col2[ones_digit * 8 - 8:ones_digit * 8]:
                list_col2.append(self.format_binary(j, 8))
        
        # 判断十位数是否为0
        if tens_digit == 0:
            for a in self.col1[72:80]:
                list_col1.append(self.format_binary(a, 8))
        else:
            for b in self.col1[tens_digit * 8 - 8:tens_digit * 8]:
                list_col1.append(self.format_binary(b, 8))
                
        # 将个位数字和十位数字组合起来
        for k in range(8):
            comb = str(list_col1[k])[0:4] + str(list_col2[k][4:8])
            list_fin.append(comb)

        return list_fin
    
    def num_proc(self, num):
        '''将传入的数字转换成一个长度为8的列表，
        列表中每一个数字表示对应行数的灯珠亮灭与否，
        如果传入的数字不在[0,99]的区间内则溢出，返回∞'''
        if 0 <= num <= 99:
            listfin = self.num_comb(num)
            list_fin_num = []
            
            # 将列表中的每个数字由str型转换成int型
            for i in listfin:
                i = int(i,2)
                list_fin_num.append(i)

            return list_fin_num
        else:
            overflow_list = [0x00,0x66,0x99,0x99,0x66,0x00,0x00,0x00] # ∞
            return overflow_list

# 测试用
# import dht
# pin_clk = Pin(14, Pin.OUT, value=1) #接D5脚,时钟，上升跳变时数据位移锁存
# pin_cs  = Pin(15, Pin.OUT, value=1) #接D8脚,上升跳变时，数据全部推入锁存
# pin_din = Pin(13, Pin.OUT, value=1) #接D7脚,待移入的数据
# dml = dML(pin_clk, pin_cs, pin_din)
# 
# # 获取实时温湿度
# def tem_hum(pin):
#     d = dht.DHT11(machine.Pin(pin))
#     d.measure()
#     return d.temperature(),d.humidity()
# 
# while True:
#     tem, hum = tem_hum(2)
#     col1 = dml.num_proc(tem)
#     col2 = dml.num_proc(hum)
#     
#     # 显示温度
#     for n in range(8):
#         if n == 7:
#             dml.write_data(n+1, 0b11110000) # 最后一行前四个灯亮，表示温度
#         else:
#             dml.write_data(n+1, col1[n])
#     time.sleep(1)
#     
#     # 显示湿度
#     for l in range(8):
#         if l == 7:
#             dml.write_data(l+1, 0b00001111) # 最后一行后四个灯亮，表示湿度
#         else:
#             dml.write_data(l+1, col2[l])
#     time.sleep(1)
