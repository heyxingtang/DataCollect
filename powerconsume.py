#!/usr/bin/env python
# encoding: utf-8

import serial
import time
import MySQLdb
import serial.tools.list_ports
import logging


class SmartMeter:

    def __init__(self, addr, command):
        self.__addr = addr
        self.__command = command

    def collect(self, ser):
        """
        通过采集程序采集数据，保存到到数据库
        :param ser:
        :return: None
        """
        elecused = self.getCons(ser)
        logging.debug("Meter addr : %s, collect power consumed : %0.2f ", self.__addr, elecused)
        self.insertMeterdata(elecused)

    def getCons(self, ser):
        """
        采集程序，通过采集耗电量指令采集数据并返回实时耗电量
        :param ser:串口对象
        :return: 实时耗电量(浮点数)
        """
        ser.write(self.__command.decode('hex'))
        while True:
            if ser.inWaiting() == 20:
                break
        elecmd = ser.read(ser.inWaiting()).encode('hex')
        eledec = 0.01 * float(self.getBCD(elecmd[28:30]))
        eleint = float(self.getBCD(elecmd[30:36]))
        return eledec + eleint

    def insertMeterdata(self, consum):
        """
        数据库相关操作
        :param consum: 耗电量
        :return: None
        """
        db = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="db_bupt", charset="utf8")
        cursor = db.cursor()
        try:
            sql = 'SELECT * FROM t_meterdata WHERE meter_id="%s" ORDER BY timestamp DESC' % self.__addr
            cursor.execute(sql)
            rs = cursor.fetchall()
            if len(rs) < 1:
                # new meter
                logging.info("New meter discovery, meter addr : %s", self.__addr)
                cursor.execute('INSERT INTO t_meterdata VALUES(NULL,"%s", %f, %f, %d)' % (self.__addr, 0.0, 100, int(time.time())))
                db.commit()
            else:
                # exist meter
                logging.debug("Meter data collected, meter addr : %s, power consumed : %0.2f", self.__addr, consum)
                data = rs[0]
                cursor.execute('INSERT INTO t_meterdata VALUES(NULL,"%s", %f, %f, %d)' % (self.__addr, consum, data[3] + data[2] - consum, int(time.time())))
                db.commit()
        except MySQLdb.Error as e:
            logging.error("Mysql Error %d: %s", e.args[0], e.args[1])
            db.rollback()
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def searchPort():
        """
        查找串口设备
        :return: 串口设备
        """
        port_list = list(serial.tools.list_ports.comports())
        for port in port_list:
            if port[2] != 'n/a':
                return port[0]

    @staticmethod
    def getAddr(ser):
        """
        获取电表通信地址
        :param ser:
        :return: 电表通信地址
        """
        ser.write(b'\x68\xAA\xAA\xAA\xAA\xAA\xAA\x68\x13\x00\xDF\x16')
        while True:
            if ser.inWaiting() == 18:
                break
        addr = ser.read(ser.inWaiting()).encode('hex')[2:14]
        return addr

    @staticmethod
    def getCS(command):
        """
        获取校验和checksum
        :param command:
        :return:校验和
        """
        cs = sum(map(ord, command.decode('hex')))
        checksum = hex(cs % 256)
        return checksum.encode('ascii')[2:]

    @staticmethod
    def getBCD(command):
        """
        BCD码转十进制
        :param command:BCD码
        :return:十进制结果
        """
        bcd = 0.0
        for i in range(0, len(command), 2):
            s = int(bin((int(command[i:i + 2], 16) / 0x10)), 2) * 10 + int(bin((int(command[1:i + 2], 16) % 0x10)),
                                                                           2) - 33
            bcd += s * pow(10.0, i)
        return bcd


def InitParam(ser):
    """
    初始化电表通信地址，操作指令等参数
    :param ser:
    :return:
    """
    addr = SmartMeter.getAddr(ser)
    command = b'68' + addr + b'68110433333433' + SmartMeter.getCS(b'68' + addr + b'68110433333433') + b'16'
    logging.info("Init meter parameters, addr : %s, collect command : %s", addr, command)
    return addr, command


if __name__ == '__main__':
    logging.basicConfig(filename="./logs/powerconsume.log", level=logging.DEBUG, format='%(asctime)s-[line:%(lineno)-3d]-%(levelname)-6s : %(message)s')
    ser = serial.Serial(SmartMeter.searchPort(), 2400, parity='E', timeout=1)
    addr, cmd = InitParam(ser)
    meter = SmartMeter(addr, cmd)

    while True:
        meter.collect(ser)
        time.sleep(40)
