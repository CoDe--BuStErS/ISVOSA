#! /usr/bin/python

import math, time, string
import numpy
import Gnuplot

from Scientific.Functions.LeastSquares import leastSquaresFit



def func(params,x): # y=ax^2+bx+c
    return params[0]*x*x + params[1]*x + params[2]


def funcimag(params,x): # y=ax+b
    return params[0]*x + params[1]



class RLCparams:
    """
    Determine of RLC params of Equivalent circuit
    """

    def __init__(self):
        # input data
        self.frequency = []
        self.impedance = []

        self.admitance = []

        self.vyrez = []
        self.vyref = []
        self.vyrezimag = []
        self.vyref_fit = []

        self.yre_fit = []
        self.yim_fit = []

        self.R1 = None
        self.C0 = None
        self.C1 = None
        self.L1 = None
        self.fResonance = None
        self.fResonanceFit = None

        self.gnuplot = Gnuplot.Gnuplot()
        self.gnuplot1 = Gnuplot.Gnuplot()
        self.gnuplot2 = Gnuplot.Gnuplot()

        self.timeStart = None


    def data(self, frequency, impedance):
        """
        Load data from dataset
        """
        self.frequency = frequency
        self.impedance = impedance
        self.admitance = []
        for i in impedance:
            self.admitance.append(1 / i)

        self.vyrez = []
        self.vyref = []
        self.vyrezimag = []
        self.vyref_fit = []

        self.yre_fit = []
        self.yim_fit = []

        self.R1 = None
        self.C0 = None
        self.C1 = None
        self.L1 = None
        self.fResonance = None


    def fit(self):
        """
        Determine of data for optimal fit and fit
        """
        Yr = [x.real for x in self.admitance]
        maxYr = max(Yr)
        maxYrIndex = Yr.index(maxYr)
        fRes = self.frequency[maxYrIndex]

        # Hladanie P% +- bodov
        P = 10
        minYr = min(Yr)
        hod = maxYr - (((maxYr - minYr) / 100) * P)

        lava = maxYrIndex
        for i in range(maxYrIndex, 0, -1):
            if Yr[i] > hod:
                lava = i

        prava = maxYrIndex
        for i in range(maxYrIndex, len(self.frequency), 1):
            if Yr[i] > hod:
                prava = i

        #prava = maxYrIndex + (maxYrIndex - lava)

        # vyrez
        self.vyrez = Yr[lava:prava]
        self.vyref = self.frequency[lava:prava]

        self.vyref_fit = []
        for i in range(len(self.vyref)):
            self.vyref_fit.append(i)

        # Fitovanie Realnej zlozky admitancie
        datafit = []
        for i in range(len(self.vyref)):
            datafit.append((i, self.vyrez[i]))
        guess = (1, 1, 1)
        fit_params, fit_error = leastSquaresFit(func, guess, datafit)
        #print fit_params, fit_error
        self.fResonanceFit = (- fit_params[1] ) / (2 * fit_params[0]) * ((self.vyref[-1] - self.vyref[0]) / (len(self.vyref) - 1)) + self.vyref[0]
        #print self.fResonanceFit

    
        for i in range(len(self.vyref)):
            self.yre_fit.append(func(fit_params, i))

        maxY = max(self.yre_fit)
        indexmax = self.yre_fit.index(max(self.yre_fit))
        self.fResonance = self.vyref[indexmax]

        # fitovanie Imaginarnej zlozky admitancie
        Yi = [x.imag for x in self.admitance]
        self.vyrezimag = Yi[lava:prava]

        datafitimag = []

        for i in range(len(self.vyref)):
            datafitimag.append((i, self.vyrezimag[i]))

        guessimag = (-1.0, 1.0)

        fit_params, fit_error = leastSquaresFit(funcimag, guessimag, datafitimag)

        #print fit_params, fit_error
        xim = []
        for i in range(len(self.vyref)):
            xim.append(self.vyref[i])
            self.yim_fit.append(funcimag(fit_params, i))

        Yimag = self.yim_fit[indexmax]

        # Determine R1
        self.R1 = 1.0 / maxY

        # Determine C0
        w0 = 2 * math.pi * self.fResonance
        self.C0 = Yimag / w0

        # Find X1
        w = []
        for f in self.frequency[lava:prava]:
            w.append(2 * math.pi * f)

        Yinn = []           # z ofitovanych hodnot real a imag urobi komplexne cislo...
        for i in range(len(self.vyref)):
            Yinn.append(self.yre_fit[i] + 1j * self.yim_fit[i])

        X1 = []
        for i in range(len(self.frequency[lava:prava])):
            X1.append((1 / (Yinn[i] - 1j * w[i] * self.C0)).imag)

        # Determine C1
        C1 = []
        f1 = []
        for i in range(len(X1)):
            try:
                C1.append((((w[i] / w0) ** 2) - 1) / (w[i] * X1[i]))
                f1.append(self.frequency[lava + i])
            except ZeroDivisionError:
                pass

        self.C1 = numpy.average(C1)

        #Determine L1
        self.L1 = 1.0 / (self.C1 * (w0 ** 2))


    def plot(self):
        """
        Plot cela krivka + vyrez
        """
        Yr = [x.real for x in self.admitance]
        #self.gnuplot = Gnuplot.Gnuplot()
        #self.gnuplot.clear()
        self.gnuplot('set style data linespoints')
        self.gnuplot('set xtics border mirror norotate')
        self.gnuplot('set ytics border mirror norotate')
        self.gnuplot('set ztics border nomirror norotate')
        self.gnuplot('set nox2tics')
        self.gnuplot('set y2tics border mirror norotate')
        self.gnuplot('set xlabel "frequency, Hz"')
        self.gnuplot('set ylabel "impedance real, Ohm"')
        self.gnuplot('set y2label "impedance real, Ohm"')
        self.gnuplot('set title ""')
        self.gnuplot.plot(
                Gnuplot.Data(
                    self.frequency,
                    Yr,
                    title = 'Yr',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref,
                    self.vyrez,
                    title = 'Yr - vyrez',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.vyrez,
                    title = 'Yr - vyrez',
                    axes = 'x2y2',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.yre_fit,
                    title = 'Yr - fit',
                    axes = 'x2y2',
                    inline = 1)
                )
        self.gnuplot.replot()
        #raw_input('press enter')

    
   
    def plotParams(self, dataFile):
        """
        f/t, Rm/t
        """
        self.gnuplot1('set style data linespoints')
        self.gnuplot1('set xtics border mirror norotate')
        self.gnuplot1('set ytics border mirror norotate')
        self.gnuplot1('set ztics border nomirror norotate')
        self.gnuplot1('set nox2tics')
        self.gnuplot1('set y2tics border mirror norotate')
        self.gnuplot1('set xlabel "time [s]"')
        self.gnuplot1('set ylabel "f [Hz]"')
        self.gnuplot1('set y2label "Rm [Ohm]"')
        self.gnuplot1('set title ""')
        self.gnuplot1('plot [:] "' + dataFile + '" index 0 using 1:3 axes x1y2')
        self.gnuplot1.replot()

    def plotAll(self, dataFile):
        """
        f/t, Rm/t
        """ 
        Yr = [x.real for x in self.admitance]
        self.gnuplot2('set multiplot')
        self.gnuplot2('set size 1,1')
        self.gnuplot2('set origin 0,0')
        self.gnuplot2('set style data lines')
        self.gnuplot2('set xtics border mirror norotate')
        self.gnuplot2('set ytics border mirror norotate')
        self.gnuplot2('set ztics border nomirror norotate')
        self.gnuplot2('set nox2tics')
        self.gnuplot2('set y2tics border mirror norotate')
        self.gnuplot2('set xlabel "time [s]"')
        self.gnuplot2('set ylabel "f [Hz]"')
        self.gnuplot2('set y2label "Rm [Ohm]"')
        self.gnuplot2('set grid')
        self.gnuplot2('set format y "%.0f" ')
        self.gnuplot2('set size 1,0.5')
        self.gnuplot2('set origin 0,0.5')
        self.gnuplot2('plot [:] "' + dataFile + '" index 0 using 1:2 axes x1y1 title "fRes", "' + dataFile + '" index 0 using 1:3 axes x1y2 title "Rm"')
        self.gnuplot2('set xlabel "f [Hz]"')
        self.gnuplot2('set ylabel "admitance [Ohm]"')
        self.gnuplot2('set y2label "admitance [Ohm]"')
        self.gnuplot2('set xtics rotate')
        self.gnuplot2('set format x "%.0f" ')
        self.gnuplot2('set format y "%.3f" ')
        self.gnuplot2('set nogrid')
        self.gnuplot2('set size 0.5, 0.5')
        self.gnuplot2('set origin 0, 0')
        self.gnuplot2.plot(
                Gnuplot.Data(
                    self.frequency,
                    Yr,
                    title = 'Yr',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref,
                    self.vyrez,
                    title = 'Yr - select',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.vyrez,
                    title = 'Yr - select',
                    axes = 'x2y2',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.yre_fit,
                    title = 'Yr - fit',
                    axes = 'x2y2',
                    inline = 1)
                )
        self.gnuplot2('set ylabel "|Z| [Ohm]"')
        self.gnuplot2('set y2label "phase [rad]"')
        self.gnuplot2('set size 0.5, 0.5')
        self.gnuplot2('set origin 0.5, 0')
        self.gnuplot2('set style data lines')
        self.gnuplot2.plot(
                Gnuplot.Data(
                    self.frequency,
                    [abs(x) for x in self.admitance],
                    title = '|Z|',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.frequency,
                    [math.atan2(x.imag, x.real) for x in self.admitance],
                    title = 'phase',
                    axes = 'x1y2',
                    inline = 1)
                )
#        self.gnuplot2.replot()

    def plot_re(self):
        """
        Plot real + fit
        """
        #self.gnuplot = Gnuplot.Gnuplot()
        #self.gnuplot.clear()
        self.gnuplot('set style data linespoints')
        self.gnuplot('set xtics border mirror norotate')
        self.gnuplot('set ytics border mirror norotate')
        self.gnuplot('set ztics border nomirror norotate')
        self.gnuplot('set nox2tics')
        self.gnuplot('set y2tics border mirror norotate')
        self.gnuplot('set xlabel "frequency, Hz"')
        self.gnuplot('set ylabel "impedance real, Ohm"')
        self.gnuplot('set y2label "phase, rad"')
        self.gnuplot('set title ""')
        self.gnuplot.plot(
                Gnuplot.Data(
                    self.vyref_fit,
                    self.vyrez,
                    title = 'Yr - vyrez',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.yre_fit,
                    title = 'Yr - fit',
                    axes = 'x1y1',
                    inline = 1)
                )
        #self.gnuplot.replot()
        #raw_input('press enter')


    def plot_im(self):
        """
        Plot imag + fit
        """
        self.gnuplot = Gnuplot.Gnuplot()
        self.gnuplot.clear()
        self.gnuplot('set style data linespoints')
        self.gnuplot('set xtics border mirror norotate')
        self.gnuplot('set ytics border mirror norotate')
        self.gnuplot('set ztics border nomirror norotate')
        self.gnuplot('set nox2tics')
        self.gnuplot('set y2tics border mirror norotate')
        self.gnuplot('set xlabel "frequency, Hz"')
        self.gnuplot('set ylabel "impedance imag, Ohm"')
        self.gnuplot('set y2label "phase, rad"')
        self.gnuplot('set title ""')
        self.gnuplot.plot(
                Gnuplot.Data(
                    self.vyref_fit,
                    self.vyrezimag,
                    title = 'Yimag - vyrez',
                    axes = 'x1y1',
                    inline = 1),
                Gnuplot.Data(
                    self.vyref_fit,
                    self.yim_fit,
                    title = 'Yimag - fit',
                    axes = 'x1y1',
                    inline = 1)
                )
        #raw_input('press enter')

    def saveParams(self, fileName = ''):
        if not fileName :
            return -1

        dataFile = open(fileName, 'a')
        if not self.timeStart:
            self.timeStart = time.time()
            dataFile.write('# t\t\tf\t\tR1\t\tC0\t\t\tC1\t\t\tL1\n')
            dataFile.write('#' + ('-' * 111) + '\n')
        dataFile.write(string.rjust('%.2f' % (time.time() - self.timeStart), 9) + '\t'
                       + str(self.fResonanceFit) + '\t'
                       + str(self.R1) + '\t'
                       + str(self.C0) + '\t'
                       + str(self.C1) + '\t'
                       + str(self.L1) + '\n')
        dataFile.close()

    def __del__(self):
        self.timeStart = None



def load(filename):
    """
    Load of data from file  (freq, real, imag)
    """
    f = file(filename)
    frequency = []
    impedance = []
    for line in f:
        if line[0] == '\n' or line[0] == '#':
            if len(frequency) != 0:
                yield frequency, impedance
                frequency = []
                impedance = []
            continue
        numbers = line.split('\t')
        frequency.append(float(numbers[0]))
        impedance.append(float(numbers[1]) + 1j * float(numbers[2]))
    if len(frequency) != 0:
        yield frequency, impedance



if __name__ == '__main__':

    import sys

    p = RLCparams()
    for frequency, impedance in load(sys.argv[1]):
        print len(frequency), '----------'
        p.data(frequency, impedance)
        p.fit()
        p.plot()
        #p.plot_re()
        #p.plot_im()
        p.saveParams('y.dat')
        print 'R1 =', p.R1
        print 'C0 =', p.C0
        print 'C1 =', p.C1
        print 'L1 =', p.L1
        print 'Fres =', p.fResonance

