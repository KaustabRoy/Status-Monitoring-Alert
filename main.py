import mysql.connector as sql_conn
from sms import TextMessage as send_msg
from termcolor import colored
import time

class TeleData:

    def __init__(self, dbname):
        self.db_name = dbname
        self.chval = 0

    def test_connection(self):
        """
        Tests a demo connection to the assigned database.
        """
        stat = False
        try:
            test_conn = sql_conn.connect(
                host = "localhost",
                user = "root",
                passwd = "LabDB88",
                database = self.db_name,
                )
            if test_conn.is_connected():
                stat = True
                print(colored(f"Successfully connected to database", "green"))
                return stat
            else:
                stat = False
                print(colored(f"Failed to connect database", "red"))
                return stat
        except Exception as e:
            print(colored(f"Error connecting to database : {e}", "red"))
            

    def connect_db(self):
        """
        Create connection to the assigned database.
        """
        db_conn = sql_conn.connect(
            host = "localhost",
            user = "root",
            passwd = "LabDB88",
            database = self.db_name,
        )
        return db_conn

    def show_tables(self):
        """
        Shows all the tables present in the assigned database.
        """
        conn = self.connect_db()
        db_cursor = conn.cursor()
        db_cursor.execute("show tables")
        for t in db_cursor:
            print(colored(t, "magenta"))
    
    def global_status(self):
        """
        Return the list of the global recipients' numbers
        and the status if sending globally is active or not.
        0 -> inactive, 1 -> active
        """
        conn = self.connect_db()
        db_cursor = conn.cursor()
        db_cursor.execute("select * from mob_list")
        data = db_cursor.fetchone()
        # data[2] -> phn no. list & data[1] -> status(0/1)
        return data[2], data[1]
    
    def port_data(self):
        conn = self.connect_db()
        db_cursor = conn.cursor()
        db_cursor.execute("select * from port_setting")
        data = db_cursor.fetchall()
        dev_port = data[0][1]
        mod_port = data[1][1]
        print(f"Device Port: {dev_port} | {type(dev_port)}\nModule Port: {mod_port} | {type(mod_port)}")
        return dev_port, mod_port

    def msg_trigger(self):
        """
        Triggers sending sms to respective phone number(s).
        """
        conn = self.connect_db()
        db_cursor = conn.cursor()
        db_cursor.execute("select * from ch_settings")
        data = db_cursor.fetchall()
        print(colored(data, "blue"))
        glob_stat, phn_list = self.global_status()
        _, mod_port = self.port_data()
        print(colored(mod_port, "magenta"))
        for d in data:
            print(colored(d, "cyan")) 
            chval = d[2]
            sms_text = d[3]
            phn_nos = d[4].split(',')
            sms_stat = d[5]
            sms_norm = d[6]
            norm_text = d[7]

            if glob_stat == 1:
                if chval == 1 and sms_stat == 0:
                    for phn in phn_list.split(','):
                        print(colored(f"Sending sms : {sms_text} to {phn}", "light_green"))
                        send_msg(recipient = phn, message = sms_text, port = mod_port)
                    # change sms stat 0 to 1
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_stat = 1 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_stat 0 to 1.\nSuccessfully updated database!", "yellow"))
                    # if sms_norm != 0:
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_norm = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_norm 0 to 0.\nSuccessfully updated database!", "yellow"))
                elif chval == 1 and sms_stat == 1:
                    print(colored("SMS already sent", "dark_grey"))
                    # if sms_norm != 0:
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_norm = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_norm 0 to 0.\nSuccessfully updated database!", "yellow"))
                elif chval == 0 and sms_stat == 1:
                    print(colored(f"Not sending sms : {sms_text} to global, sms sent previously, channel currently inactive.", "red"))
                    # change sms stat 1 to 0
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_stat = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_stat 1 to 0.\nSuccessfully updated database!", "yellow"))
                    # if sms_norm == 0:
                    try:
                        for phn in phn_list.split(','):
                            print(colored(f"Sending Normal State sms : {norm_text} to {phn}", "light_green"))
                            send_msg(recipient = phn, message = sms_text, port = mod_port)
                        conn = self.connect_db()
                        db_cursor = conn.cursor()
                        query = "update ch_settings set sms_norm = 1 where chid = '{}'".format(d[0])
                        db_cursor.execute(query)
                        conn.commit()
                        print(colored("Changed sms_norm 0 to 1.\nSuccessfully updated database!", "yellow"))
                    except Exception as e:
                        print(colored(f"Exception Occurred:: {e}", "red"))
                elif chval == 0 and sms_stat == 0:
                    print(colored(f"Not sending sms : {sms_text} to global, channel currently inactive.", "light_red"))
                    # if sms_norm == 0:
                    try:    
                        for phn in phn_list.split(','):
                            print(colored(f"Sending Normal state sms : {norm_text} to {phn}", "light_green"))
                            send_msg(recipient = phn, message = sms_text, port = mod_port)
                        conn = self.connect_db()
                        db_cursor = conn.cursor()
                        query = "update ch_settings set sms_norm = 1 where chid = '{}'".format(d[0])
                        db_cursor.execute(query)
                        conn.commit()
                        print(colored("Changed sms_norm 0 to 1.\nSuccessfully updated database!", "yellow"))
                    except Exception as e:
                        print(colored(f"Exception Occurred:: {e}", "red"))

            elif glob_stat == 0:
                if chval == 1 and sms_stat == 0:
                    for phn in phn_nos:
                        print(colored(f"Sending sms : {sms_text} to {phn}", "light_green")) 
                        send_msg(recipient = phn, message = sms_text, port = mod_port)
                    # change sms stat 0 to 1
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_stat = 1 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_stat 0 to 1.\nSuccessfully updated database!", "yellow"))
                    # if sms_norm != 0:
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_norm = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_norm 0 to 0.\nSuccessfully updated database!", "yellow"))
                elif chval == 1 and sms_stat == 1:
                    print(colored("SMS already sent", "dark_grey"))
                    # if sms_norm != 0:
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_norm = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_norm 0 to 0.\nSuccessfully updated database!", "yellow"))
                elif chval == 0 and sms_stat == 1:
                    print(colored(f"Not sending sms : {sms_text} to {phn_nos}, sms sent previously, channel currently inactive.", "red"))
                    # change sms stat 1 to 0
                    conn = self.connect_db()
                    db_cursor = conn.cursor()
                    query = "update ch_settings set sms_stat = 0 where chid = '{}'".format(d[0])
                    db_cursor.execute(query)
                    conn.commit()
                    print(colored("Changed sms_stat 1 to 0.\nSuccessfully updated database!", "yellow"))
                    # if sms_norm == 0:
                    try:
                        for phn in phn_list.split(','):
                            print(colored(f"Sending Normal State sms : {norm_text} to {phn}", "light_green"))
                            send_msg(recipient = phn, message = sms_text, port = mod_port)
                        conn = self.connect_db()
                        db_cursor = conn.cursor()
                        query = "update ch_settings set sms_norm = 1 where chid = '{}'".format(d[0])
                        db_cursor.execute(query)
                        conn.commit()
                        print(colored("Changed sms_norm 0 to 1.\nSuccessfully updated database!", "yellow"))
                    except Exception as e:
                        print(colored(f"Exception Occurred:: {e}", "red"))
                elif chval == 0 and sms_stat == 0:
                    print(colored(f"Not sending sms : {sms_text} to {phn_nos}, channel currently inactive.", "light_red"))
                    # if sms_norm == 0:
                    try:
                        for phn in phn_list.split(','):
                            print(colored(f"Sending Normal state sms : {norm_text} to {phn}", "light_green"))
                            send_msg(recipient = phn, message = sms_text, port = mod_port)
                        conn = self.connect_db()
                        db_cursor = conn.cursor()
                        query = "update ch_settings set sms_norm = 1 where chid = '{}'".format(d[0])
                        db_cursor.execute(query)
                        conn.commit()
                        print(colored("Changed sms_norm 0 to 1.\nSuccessfully updated database!", "yellow"))
                    except Exception as e:
                        print(colored(f"Exception Occurred:: {e}", "red"))

if __name__ == '__main__':
    db = TeleData(dbname = "isn04dm")
    connection_status = db.test_connection()
    if connection_status:
        db.show_tables()
        db.global_status()
        while True:
            db.msg_trigger()
            time.sleep(1)
            print(colored("="*50, "magenta"))