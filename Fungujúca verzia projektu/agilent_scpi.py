#!/usr/bin/python


import socket


class AgilentSCPI:
        
    _host_ip = None
    _scpi_port = None
    _connection = None

    def __init__(self):
        self._host_ip = '192.168.1.102'
        self._scpi_port = 5025
        
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((self._host_ip, self._scpi_port))


    def send_cmd(self, command):
        self._connection.sendall(command + '\n')


    def read_data(self):
        data = ''
        while 1:
            buf = self._connection.recv(1024)
            data += buf
            if len(buf) > 1:
                if buf[-1] == '\n':
                    break
            else:
                break
        data = data[:-1]
        return data


    def read_err(self):
        self.send_cmd(':syst:err?')
        return self.read_data()


    def __del__(self):
        self._connection.close()



if __name__ == '__main__':

    def novy_stroj():
        a = AgilentSCPI()

	a.send_cmd(':syst:pres')
	a.send_cmd(':calc1:form smit')
	a.send_cmd(':abor')
	a.send_cmd(':sens1:swe:poin 1601')
	
	a.send_cmd(':form:data asc')
	a.send_cmd('*wai')

	a.send_cmd(':init1:cont off')
	a.send_cmd('*wai')

	a.send_cmd(':sens1:freq:span ' + ('%f' % 40000))

	a.send_cmd(':sens1:freq:cent ' + ('%f' % 7981000))

	a.send_cmd('*wai')

	print 'FREKV'
        a.send_cmd(':trig:sing')
        a.send_cmd('*wai') 
	a.send_cmd(':calc1:data:fdat?')
	data = a.read_data()
	print data
    a.send_cmd(':calc1:data:fdat?')
	data = a.read_data()
	print data
	a.send_cmd(':sens1:freq:star?')
	print 'START',a.read_data()

	a.send_cmd(':sens1:freq:stop?')

	print 'STOP',a.read_data()
	
	a.send_cmd('*wai')

	a.send_cmd(':init1:cont on')
    
        del a

    novy_stroj()

