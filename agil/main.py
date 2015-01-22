#!/usr/bin/python


import string
import sys
import math
import time

import agilent, rlcparams

from Scientific.Functions.LeastSquares import leastSquaresFit

def lorentz(params, x): #(y0, A, w, xc) -> y0 + (2*A/math.pi)*(w/(4*(x-xc)**2 + w**2))
    return params[0] + (2.0*params[1]/math.pi) * ( params[2]/(4.0*(x-params[3])**2 + params[2]**2) )


def main(args) :

    saveParamsFile = None
    saveDataFile = None
    if len(args) == 2:
        saveParamsFile = args[1]
    if len(args) == 3:
        saveParamsFile = args[1]
        saveDataFile = args[2]

    a = agilent.agilent()
    p = rlcparams.RLCparams()
    
    a.setFrequency(center = '8 MHz', span = '3 MHz')
    a.measure()
    a.plotData()
    #a.saveData('x.dat')

    m = max(a.data['admitance'])
    maxIndex = a.data['admitance'].index(m)
    a.setFrequency(center = '%f Hz' % a.data['frequency'][maxIndex])

    a.setFrequency(span = '1 MHz')

    a.measure()
    a.plotData()
    #a.saveData('x.dat')

    m = max(a.data['admitance'])
    maxIndex = a.data['admitance'].index(m)
    a.setFrequency(center = '%f Hz' % a.data['frequency'][maxIndex])

    a.setFrequency(span = '40 KHz')
    #a.setFrequency(span = '25 KHz')
    #a.setFrequency(span = '10 KHz')

#    timeStart = time.time()


    print 'f\t\tR1\t\tC0\t\t\tC1\t\t\tL1'
    print 90 * '-'

    while 1 :
        a.measure()
        #a.plotData() # plot spectrum
        if saveDataFile:
            a.saveData(saveDataFile)

        p.data(a.data['frequency'], a.data['Z'])
        p.fit()
        #p.plot() # plot fit

        print str(p.fResonanceFit) + '\t' + str(p.R1) + '\t' + str(p.C0) + '\t' + str(p.C1) + '\t' + str(p.L1)
        if saveParamsFile:
            p.saveParams(saveParamsFile)
            #p.plotParams(saveParamsFile)
            p.plotAll(saveParamsFile)
        
        
        #print 'C0 =', p.C0
        #print 'C1 =', p.C1
        #print 'L1 =', p.L1
        #print 'Fres =', p.fResonance


    del a


