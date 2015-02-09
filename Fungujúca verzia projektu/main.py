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

    a = agilent.Agilent()
    p = rlcparams.RLCparams()
    
    a.set_frequency(center = '8000000', span = '2000000')
    a.measure()
    
    #return
    a.plot_data()
    #a.save_data('x.dat')
    #raw_input('Press enter')

    #print 'ADMITANCIA', a.data['admitance']
    m = max(a.data['admitance'])
    maxIndex = a.data['admitance'].index(m)
    a.set_frequency(center = '%f' % a.data['frequency'][maxIndex])
    
    print m
    print maxIndex
    #print a.data

    a.set_frequency(span = '1000000')
    #a.set_frequency(span = '2000000')

    a.measure()
    a.plot_data()
    #a.save_data('x.dat')
    #raw_input('Press enter')

    m = max(a.data['admitance'])
    maxIndex = a.data['admitance'].index(m)
    a.set_frequency(center = '%f' % a.data['frequency'][maxIndex])

    a.set_frequency(span = '40000')

#    timeStart = time.time()


    print 'f\t\tR1\t\tC0\t\t\tC1\t\t\tL1'
    #print 'f\t\t\tR1\t\t\tC0\t\t\tC1\t\t\tL1'
    print 100 * '-'
    #print 120 * '-'

    while 1 :
        a.measure()
        #a.plot_data() # plot spectrum
        if saveDataFile:
            a.save_data(saveDataFile)

        p.data(a.data['frequency'], a.data['Z'])
        #print a.data['frequency']
        p.fit()
        #p.plot() # plot fit

        print str(p.fResonanceFit) + '\t' + str(p.R1) + '\t' + str(p.C0) + '\t' + str(p.C1) + '\t' + str(p.L1)
        #print '%+.12e' % p.fResonanceFit + '\t' + '%+.12e' % p.R1 + '\t' + '%+.12e' % p.C0 + '\t' + '%+.12e' % p.C1 + '\t' + '%+.12e' % p.L1
        if saveParamsFile:
            p.saveParams(saveParamsFile)
            #p.plotParams(saveParamsFile)
            p.plotAll(saveParamsFile)
        
        
        #print 'C0 =', p.C0
        #print 'C1 =', p.C1
        #print 'L1 =', p.L1
        #print 'Fres =', p.fResonance


    del a

