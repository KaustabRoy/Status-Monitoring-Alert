from main import TeleData
from termcolor import colored
import minimalmodbus
import time
import io
import csv
import requests
from datetime import datetime


class IOModAcVal:

    def test_get_chsettings_data(self):
        try:
            conn = TeleData(dbname = "< database name >").connect_db()
            db_cursor = conn.cursor()
            db_cursor.execute("select * from ch_settings")
            db_cursor.fetchall()
            return True
        except Exception as e:
            print(colored(f"Exception : {e}", "red"))
            return False

    def mod_ival(self):
        ts = datetime.today()
        client.clear_buffers_before_each_transaction = True
        client.close_port_after_each_call = True


        data = client.read_bits(222, 34 , 2)


        if data:
            ss_dict = {
                "ss1":  data[0],
                "ss2":  data[1],
                "ss3":  data[2],
                "ss4":  data[3],
                "ss5":  data[4],
                "ss6":  data[5],
                "ss7":  data[6],
                "ss8":  data[7],
                "ss9":  data[8],
                "ss10": data[9],
                "ss11": data[10],
                "ss12": data[11],
                "ss13": data[12],
                "ss14": data[13],
                "ss15": data[14],
                "ss16": data[15],
                "ss17": data[16],
                "ss18": data[17],
                "ss19": data[18],
                "ss20": data[19],
                "ss21": data[20],
                "ss22": data[21],
                "ss23": data[22],
                "ss24": data[23],
                "ss25": data[24],
                "ss26": data[25],
                "ss27": data[26],
                "ss28": data[27],
                "ss29": data[28],
                "ss30": data[29],
                "ss31": data[30],
                "ss32": data[31],
            }
            self.set_chmod_val(mod_val = ss_dict)
        else:
            pass



    def set_chmod_val(self, mod_val):
        conn = TeleData("< database name >").connect_db()
        db_cursor = conn.cursor()
        for key in mod_val:
            # print(f"{key} : {mod_val[key]}")
            key_id = int(key[2:])
            if key_id < 10:
                value = mod_val[key]
                chid = "c0" + str(key_id)
                query = "update ch_settings set chval = {} where chid = '{}'".format(value, chid)
                db_cursor.execute(query)
                conn.commit()
            elif key_id >= 10:
                value = mod_val[key]
                chid = "c" + str(key_id)
                query = "update ch_settings set chval = {} where chid = '{}'".format(value, chid)
                db_cursor.execute(query)
                conn.commit()





if __name__ == '__main__':
    modop = IOModAcVal()
    test = modop.test_get_chsettings_data()
    if test:
        dev_port, _ = TeleData("isn04dm").port_data()

        print(colored("Chanel Settings : Access Successful", "green"))
        sl_addr = 1
        client = minimalmodbus.Instrument(dev_port ,sl_addr)

        client.serial.baudrate = 19200
        client.serial.bytesize = 8
        client.serial.parity = minimalmodbus.serial.PARITY_NONE
        client.serial.stopbits = 1
        client.serial.timeout = 0.5
        client.mode = minimalmodbus.MODE_RTU

        while True:
            modop.mod_ival()
            new_dev_port, _ = TeleData("isn04dm").port_data()
            print(datetime.today())
            # print(dev_port)
            dev_port = new_dev_port 
        # modop.mod_ival()
    else:
        print(colored("Chanel Settings : Access failed", "red"))
