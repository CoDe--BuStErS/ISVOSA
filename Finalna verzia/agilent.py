#!/usr/bin/python


import agilent_SCPI
import string
import math
import Gnuplot



class agilent (agilent_SCPI.agilent_SCPI) :
        
    gnuplot = None
    data = {}
    frequency = {}

    def __init__(self) :
        agilent_SCPI.agilent_SCPI.__init__(self)

        self.data['frequency'] = []
        self.data['Z'] = []
        self.data['impedance'] = []
        self.data['admitance'] = []
        self.data['phase'] = []

        #self.sendCmd('disp:form:expand on')
        self.sendCmd(':sys:pres') # ISVOSA
        self.sendCmd(':calc1:form smit')
        self.sendCmd(':init1:cont off')

        #self.sendCmd(':init1:cont on') # ISVOSA
        #self.sendCmd(':abor')  # ISVOSA
        
        self.sendCmd(':sens1:swe:poin 1601; *wai')
        #self.sendCmd(':sens1:swe:poin 1601') # ISVOSA
        
        #self.sendCmd('sens1:swe:poin 21; *wai')
        #self.sendCmd('sens1:swe:poin?')
        #points = int( self.readData() )
        #self.sendCmd('form:data asc,12')
        self.sendCmd(':form:data asc')

        self.sendCmd('*wai') # ISVOSA
           
        self.sendCmd(':sens1:freq:star?')
        self.frequency['start'] = float(self.readData())
        self.sendCmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.readData())

        

        self.gnuplot = Gnuplot.Gnuplot()
        self.gnuplot.clear()
        #self.gnuplot('set data style lines')
        self.gnuplot('set style data lines')
        #self.gnuplot('set data style linespoints') # ISVOSA
        self.gnuplot('set xtics border mirror norotate')
        self.gnuplot('set ytics border mirror norotate')
        self.gnuplot('set ztics border nomirror norotate')
        self.gnuplot('set nox2tics')
        self.gnuplot('set y2tics border mirror norotate')
        self.gnuplot('set xlabel "frequency, Hz"')
        #self.gnuplot('set ylabel "impedance, Ohm; admittance, Siemens"')
        self.gnuplot('set ylabel "admittance, Siemens"')
        self.gnuplot('set y2label "phase, rad"')
        #self.gnuplot('set title "QCM"')


    def __del__(self) :
        del self.gnuplot
        agilent_SCPI.agilent_SCPI.__del__(self)


    def setFrequency(self, start = '', stop = '', center = '', span = '') :
        if start :
            self.sendCmd(':sens1:freq:star ' + start)
        if stop :
            self.sendCmd(':sens1:freq:stop ' + stop)
        if center :
            self.sendCmd(':sens1:freq:cent ' + center)
        if span :
            self.sendCmd(':sens1:freq:span ' + span)

        self.sendCmd('*wai')
        
        self.sendCmd(':sens1:freq:start?')
        self.frequency['start'] = float(self.readData())
        
        self.sendCmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.readData())



    def measure(self) :
        self.data['frequency'] = []
        self.data['Z'] = []
        self.data['impedance'] = []
        self.data['admitance'] = []
        self.data['phase'] = []

        self.sendCmd(':init1:cont off')

        # self.sendCmd(':init1')
        self.sendCmd('*wai')
        #self.sendCmd(':trac? ch1fdata') # ISVOSA

        self.sendCmd(':calc1:data:fdat?')
        data = self.readData()
        
        self.sendCmd(':sens1:freq:star?')
        self.frequency['start'] = float(self.readData())
        
        self.sendCmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.readData())

        self.sendCmd('*wai')

        self.sendCmd(':init1:cont on')

        data = string.split(data, ',')

        gamma = []    # agilent device output data
        for i in range(0, len(data), 2) :
            gamma.append(complex(float(data[i]), float(data[i+1])))
        
        frequency = self.frequency['start']
        step = (self.frequency['stop'] - self.frequency['start'])/(len(gamma)-1)
        for i in range(len(gamma)) :
            self.data['frequency'].append(frequency)
            frequency += step

        for g in  gamma :
            #z = 50 * ( (1 + g) / (1 - g) ) # ISVOSA
            z = g
            self.data['Z'].append(z)
            self.data['impedance'].append(abs(z))
            y = 1 / z
            self.data['admitance'].append(abs(y))
            self.data['phase'].append(math.atan2(y.imag, y.real))

        return self.data


    def plotData(self) :
        #x = Numeric.arange(len(self.data['Z']))
        self.gnuplot('set xrange [%f:%f]' % (self.frequency['start']-100, self.frequency['stop']+100))
        self.gnuplot.plot(
#            Gnuplot.Data(    self.data['frequency'],
#                    self.data['impedance'],
#                    title='impedance',
#                    axes='x1y1',
#                    inline=1
#                    ),
            Gnuplot.Data(    self.data['frequency'],
                    self.data['admitance'],
                    title='admitance',
                    axes='x1y1',
                    inline=1
                    ),
            Gnuplot.Data(    self.data['frequency'],
                    self.data['phase'],
                    title='phase',
                    axes='x1y2',
                    inline=1
                    )
            )
        self.gnuplot.replot()


    def saveData(self, fileName = '') :
        if not fileName :
            return -1

        dataFile = open(fileName, 'a')
        dataFile.write('\n\n')
        dataFile.write('#' + '-'*140 + '\n')
        dataFile.write('# frequency\t\t| Z.real\t\t| Z.imag\t\t| |Z|\t\t\t| phase\t\t\t| admitance\n')
        dataFile.write('#' + '-'*140 + '\n')
        for i in range(len(self.data['Z'])) :
            dataFile.write('%+.12e' % self.data['frequency'][i])
            dataFile.write('\t')
            dataFile.write('%+.12e' % self.data['Z'][i].real)
            dataFile.write('\t')
            dataFile.write('%+.12e' % self.data['Z'][i].imag)
            dataFile.write('\t')
            dataFile.write('%+.12e' % self.data['impedance'][i])
            dataFile.write('\t')
            dataFile.write('%+.12e' % self.data['phase'][i])
            dataFile.write('\t')
            dataFile.write('%+.12e' % self.data['admitance'][i])
            dataFile.write('\n')
        dataFile.close()



###############################################################################


if __name__ == '__main__':

    a = agilent()
    
    a.setFrequency(span = '%f' % 100000000)
    a.setFrequency(center = '%f' % 700000000)
    
    a.measure()
    a.saveData('x.dat')
    a.plotData()
    raw_input('Press enter')
    
    #import sys
    #sys.exit()
    
    max = max(a.data['admitance'])
    print max
    maxIndex = a.data['admitance'].index(max)
    print maxIndex, a.data['frequency'][maxIndex]
    a.setFrequency(center = '%f' % a.data['frequency'][maxIndex]) # ISVOSA
    print a.readErr()
    
    a.measure()
    a.plotData()
    raw_input('Press enter')

    del a

