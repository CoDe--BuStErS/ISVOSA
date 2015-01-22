#!/usr/bin/python


import socket


class AgilentSCPI:

    _host_ip = None
    _scpi_port = None
    _connection = None

    def __init__(self):
        self._host_ip = '192.168.1.102'
        self._scpi_port = 5025 #23
        
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((self._host_ip, self._scpi_port))
        #self._connection.setblocking(0)
        #self._connection.settimeout(0.3)


    def send_cmd(self, command):
        #print 'cmd> ' + command
        self._connection.sendall(command + '\n')


    def read_data(self):
        data = ''
        while 1:
            buf = self._connection.recv(1024)
            #print 'buf> "' + buf + '"'
            data += buf
            if len(buf) > 1:
                if buf[-1] == '\n':
                    break
            else:
                break
        data = data[:-1]
        #print 'dat> ' + data
        return data

    def read_err(self):
        self.send_cmd(':syst:err?')
        return self.read_data()


    def __del__(self):
        self._connection.close()
