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


        



if __name__ == '__main__':


    # verzia stareho stroja funkcna



    def stary_stroj():
        a = AgilentSCPI()

        a.send_cmd('init1:cont off')
        print 'init1:cont off'
        
        a.send_cmd('init1; *wai')
        print 'init1; *wai'
        a.send_cmd('trac? ch1fdata')
        print 'trac? ch1fdata'
        data = a.read_data()
        print data
        #printing to file 
        f = open('dataOLD.txt', 'w')
        f.write(str(data))
        f.close()
        
        #self.sendCmd('sens1:freq:star?')
        #self.frequency['start'] = float(self.readData())
        
        #self.sendCmd('sens1:freq:stop?')
        #self.frequency['stop'] = float(self.readData())

        a.send_cmd('init1:cont on')    
    
        del a

    #novy stroj - otestovana verzia + ukladanie vzstupu so suboru
    def novy_stroj():
        a = AgilentSCPI()

	a.send_cmd('*idn?')
	print a.read_data()

	a.send_cmd(':syst:pres')
	a.send_cmd(':calc1:form smit')
	#self.send_cmd(':init1:cont off')
	a.send_cmd(':init1:cont on')
	a.send_cmd(':abor')
	a.send_cmd(':sens1:swe:poin 1601')
	
	#self.send_cmd('sens1:swe:poin 21; *wai')
	#self.send_cmd('sens1:swe:poin?')
	#points = int( self.read_data() )
	#self.send_cmd(':form:data asc,12')
	
	a.send_cmd(':form:data asc')
	a.send_cmd('*wai')

	a.send_cmd(':init1:cont off')
	#self.send_cmd(':disp:enab off')
	
	#self.send_cmd(':init1')#???
	a.send_cmd('*wai')

	a.send_cmd(':sens1:freq:span ' + ('%f' % 40000))

	a.send_cmd(':sens1:freq:cent ' + ('%f' % 7981000))

	a.send_cmd('*wai')

	print 'FREKV'

	a.send_cmd(':calc1:data:fdat?')# TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#self.send_cmd(':sens1:freq:data?')
	data = a.read_data()
	print data
	#printing to file 
        f = open('dataNEW.txt', 'w')
        f.write(str(data))
        f.close()
	
	a.send_cmd(':sens1:freq:star?')
	#self.frequency['start'] = float(self.read_data())
	print 'START',a.read_data()
	
	a.send_cmd(':sens1:freq:stop?')
	#self.frequency['stop'] = float(self.read_data())
	print 'STOP',a.read_data()
	
	a.send_cmd('*wai')

	a.send_cmd(':init1:cont on')
    
        del a

    novy_stroj()







 

