#!/usr/bin/python

import agilent_scpi
import string
import math

import Gnuplot

def _create_plot(self):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
        from matplotlib.numerix import arange, sin, pi

        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)  # a gtk.DrawingArea
        #win.add(canvas)

        axes = figure.add_subplot(111)
        x = arange(0.0, 30.0, 0.01)
        y = sin(2 * pi * x)
        line, = axes.plot(x, y)
        axes.set_title('hi mom')
        axes.grid(True)
        axes.set_xlabel('time')
        axes.set_ylabel('volts')



class Agilent (agilent_scpi.AgilentSCPI):

    gnuplot = None
    data = {}
    frequency = {}

    def __init__(self):
        agilent_scpi.AgilentSCPI.__init__(self)

        self.data['frequency'] = []
        self.data['Z'] = []
        self.data['impedance'] = []
        self.data['admitance'] = []
        self.data['phase'] = []

        #self.send_cmd('disp:form:expand on')
        self.send_cmd(':syst:pres')
        self.send_cmd(':calc1:form smit')
        #self.send_cmd(':init1:cont off')
        self.send_cmd(':init1:cont on')
        self.send_cmd(':abor')
        self.send_cmd(':sens1:swe:poin 1601')
        #self.send_cmd('sens1:swe:poin 21; *wai')
        #self.send_cmd('sens1:swe:poin?')
        #points = int( self.read_data() )
        #self.send_cmd(':form:data asc,12')
        self.send_cmd(':form:data asc')
        self.send_cmd('*wai')

        self.send_cmd(':sens1:freq:star?')
        self.frequency['start'] = float(self.read_data())
        self.send_cmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.read_data())

        self.gnuplot = Gnuplot.Gnuplot()
        self.gnuplot.clear()
        #self.gnuplot('set data style lines')
        self.gnuplot('set data style linespoints')
        self.gnuplot('set xtics border mirror norotate')
        self.gnuplot('set ytics border mirror norotate')
        self.gnuplot('set ztics border nomirror norotate')
        self.gnuplot('set nox2tics')
        self.gnuplot('set y2tics border mirror norotate')
        self.gnuplot('set xlabel "frequency, Hz"')
        #self.gnuplot('set ylabel "impedance, Ohm; admittance, Siemens"')
        self.gnuplot('set ylabel "admittance, Siemens"')
        self.gnuplot('set y2label "phase, rad"')
        self.gnuplot('set title "QCM"')


    def __del__(self):
        del self.gnuplot
        agilent_scpi.AgilentSCPI.__del__(self)


    def set_frequency(self, start='', stop='', center='', span=''):
        if start :
            self.send_cmd(':sens1:freq:star ' + start)
        if stop :
            self.send_cmd(':sens1:freq:stop ' + stop)
        if center :
            self.send_cmd(':sens1:freq:cent ' + center)
        if span :
            self.send_cmd(':sens1:freq:span ' + span)

        self.send_cmd('*wai')
        
        self.send_cmd(':sens1:freq:start?')
        self.frequency['start'] = float(self.read_data())
        
        self.send_cmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.read_data())


    def measure(self):
        self.data['frequency'] = []
        self.data['Z'] = []
        self.data['impedance'] = []
        self.data['admitance'] = []
        self.data['phase'] = []

        self.send_cmd(':init1:cont off')
        #self.send_cmd(':disp:enab off')
        
        #self.send_cmd(':init1')#???
        self.send_cmd('*wai')
        #self.send_cmd(':trac? ch1fdata')#???
        #self.send_cmd(':calc1:freq:data?')
        self.send_cmd(':calc1:data:fdat?')# TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #self.send_cmd(':sens1:freq:data?')
        data = self.read_data()
        #print data
        
        self.send_cmd(':sens1:freq:star?')
        self.frequency['start'] = float(self.read_data())
        
        self.send_cmd(':sens1:freq:stop?')
        self.frequency['stop'] = float(self.read_data())

        self.send_cmd('*wai')
        #self.send_cmd(':disp:upd')
        #self.send_cmd(':disp:enab on')
        self.send_cmd(':init1:cont on')

        data = string.split(data, ',')
        #print len(data)

        gamma = []    # agilent device output data
        for i in range(0, len(data), 2):
            #print data[i], float(data[i]), data[i+1], float(data[i+1])
            gamma.append(complex(float(data[i]), float(data[i+1])))
        
        frequency = self.frequency['start']
        step = (self.frequency['stop'] - self.frequency['start']) / (len(gamma)-1)
        for i in range(len(gamma)):
            self.data['frequency'].append(frequency)
            frequency += step

        for g in gamma:
            #z = 50 * ( (1 + g) / (1 - g) ) # old aggilent devices
            z = g
            self.data['Z'].append(z)
            self.data['impedance'].append(abs(z))
            y = 1 / z
            self.data['admitance'].append(abs(y))
            self.data['phase'].append(math.atan2(y.imag, y.real))

        return self.data


    def plot_data(self):
        self.gnuplot('set xrange [%f:%f]' % (self.frequency['start']-100, self.frequency['stop']+100))
        self.gnuplot.plot(
            #Gnuplot.Data(    self.data['frequency'],
            #        self.data['impedance'],
            #        title='impedance',
            #        axes='x1y1',
            #        inline=1
            #        ),
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


    def save_data(self, fileName=''):
        if not fileName :
            return -1

        datafile = open(fileName, 'a')
        datafile.write('\n\n')
        datafile.write('#' + '-'*140 + '\n')
        datafile.write('# frequency\t\t| Z.real\t\t| Z.imag\t\t| |Z|\t\t\t| phase\t\t\t| admitance\n')
        datafile.write('#' + '-'*140 + '\n')
        for i in range(len(self.data['Z'])) :
            datafile.write('%+.12e' % self.data['frequency'][i])
            datafile.write('\t')
            datafile.write('%+.12e' % self.data['Z'][i].real)
            datafile.write('\t')
            datafile.write('%+.12e' % self.data['Z'][i].imag)
            datafile.write('\t')
            datafile.write('%+.12e' % self.data['impedance'][i])
            datafile.write('\t')
            datafile.write('%+.12e' % self.data['phase'][i])
            datafile.write('\t')
            datafile.write('%+.12e' % self.data['admitance'][i])
            datafile.write('\n')
        datafile.close()



if __name__ == '__main__':

    a = Agilent()

    a.set_frequency(span = '%f' % 100000000)#40000
    a.set_frequency(center = '%f' % 700000000)#7981000

    a.measure()
    print a.read_err()
    a.save_data('x.dat')
    a.plot_data()
    raw_input('Press enter')

    #import sys
    #sys.exit()

    #for i in range(len(a.data['admitance'])):
    #    print a.data['frequency'][i], a.data['admitance'][i], a.data['phase'][i]
    #print '---------'

    max = max(a.data['admitance'])
    print max
    maxIndex = a.data['admitance'].index(max)
    print maxIndex, a.data['frequency'][maxIndex]
    a.set_frequency(center = '%f' % a.data['frequency'][maxIndex])
    print a.read_err()

    a.measure()
    a.plot_data()
    raw_input('Press enter')

    del a

