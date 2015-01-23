#!/usr/bin/python


import socket


class agilent_SCPI :
        
    host_ip = None
    scpi_port = None
    connection = None

    def __init__(self) :
        self.host_ip = '192.168.1.102'
        self.scpi_port = 5025
        
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host_ip, self.scpi_port))
        #self.connection.setblocking(0)
        #self.connection.settimeout(0.3)


    def sendCmd(self, command) :
        #print 'cmd> ' + command
        self.connection.sendall(command + '\n')


    def readData(self) :
        data = ''
        while 1:
            buf = self.connection.recv(1024)
            data += buf
            if len(buf) > 1:
                if buf[-1] == '\n':
                    break
            else:
                break
        data = data[:-1]
        #print 'dat> ' + data
        return data


    def readErr(self) :
        self.connection.sendall(':syst:err?')
        return self.readData()


    def __del__(self) :
        self.connection.close()


###############################################################################


if __name__ == '__main__':

    a = agilent_SCPI()
    a.send_cmd(':syst:pres') # ISVOSA
    a.send_cmd('*idn?')  # ISVOSA
    a.sendCmd(':sens1:swe:poin 1601; *wai')
    a.sendCmd(':sens1:swe:poin?')
    print a.readData()
    print a.read_err() # ISVOSA
    del a

