#!/usr/bin/env python
# encoding: utf-8

import serial
import time
import MySQLdb
import serial.tools.list_ports
import logging
import argparse


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

    # @staticmethod
    # def getAddr(ser):
    #     """
    #     获取电表通信地址
    #     :param ser:
    #     :return: 电表通信地址
    #     """
    #     ser.write(b'\x68\xAA\xAA\xAA\xAA\xAA\xAA\x68\x13\x00\xDF\x16')
    #     while True:
    #         if ser.inWaiting() == 18:
    #             break
    #     addr = ser.read(ser.inWaiting()).encode('hex')[2:14]
    #     return addr

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

    @staticmethod
    def convertAddr(meter_id):
        """
        通过电表id转换为电表通信地址addr
        :param id_str: 电表表盘上的id
        :return: 电表通信地址
        """
        if len(meter_id) != 16:
            logging.fatal("Incorrect length of meter id. Expecting 16")
            exit(1)
        else:
            addr = "%s%s%s%s%s%s" % (
                meter_id[14:16], meter_id[12:14], meter_id[10:12], meter_id[8:10], meter_id[6:8], meter_id[4:6])
            logging.info("id:%s convert to addr:%s", meter_id, addr)
            return addr


def InitParam(id_list):
    """
    初始化电表通信地址，操作指令等参数
    :param ser:
    :return:电表对象列表
    """
    meter_list = []
    for meter_id in id_list:
        addr = SmartMeter.convertAddr(meter_id)
        command = b'68' + addr + b'68110433333433' + SmartMeter.getCS(b'68' + addr + b'68110433333433') + b'16'
        logging.info("Init meter parameters, addr : %s, collect command : %s", addr, command)
        meter_list.append(SmartMeter(addr, command))
    return meter_list


if __name__ == '__main__':
    logging.basicConfig(filename="~/access-point/logs/powerconsume.log", level=logging.DEBUG, format='%(asctime)-19s-[line:%(lineno)-3d]-%(levelname)-5s : %(message)s')
    ser = serial.Serial(SmartMeter.searchPort(), 2400, parity='E', timeout=1)

    parser = argparse.ArgumentParser(description="Multi meter acquisition program")
    parser.add_argument("-m", "--meter", help="Initial start up list", default="1605343448000232,1605343453000135")
    parser.add_argument("-a", "--add", help="Add new meter into collect program", action="append")
    args = parser.parse_args()
    id_list = []
    if args.add:
        id_list = args.add
    else:
        id_list = args.meter.split(',')

    meter_list = InitParam(id_list)

    while True:
        for meter in meter_list:
            meter.collect(ser)
        time.sleep(40)
