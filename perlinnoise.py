#!/usr/bin/python3.6
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import sys
from noise import pnoise1, pnoise3
import pygmsh
#Perlin noise is a random signal that is correlated over short time scales
# The number of octaves determines the time/length scales at which features in the signal are present
# The persistence determines the amplitude of the features
def createperlin(npoints, l, noct, pers, hmax):
    ran = int(random.random() * l)
    x = np.linspace(ran, ran + l, num = npoints)
    signal = np.zeros(npoints)
    for ctr, t in enumerate(x):
        signal[ctr] = pnoise1(t, octaves = noct, persistence = pers)
    scalefactor = hmax / max([max(signal), abs(min(signal))])
    return [[t - min(x), s * scalefactor] for t, s in zip(x, signal)]

class PerlinLaminate:
    def __init__(self, lowerinterface, upperinterface, h1, h2, filename):
        self.face1 = [[v[0], v[1] + h1] for v in lowerinterface]
        self.face2 = [[v[0], v[1] + h1 + h2] for v in upperinterface]
        self.file = filename
        self.pointid = 0
        self.lineid = 0
        self.loopid = 0
        self.surfaceid = 0
        self.mesh = 1.0

        with open(self.file, 'w') as o: o.write('//Perlin-Noise-Laminate\n')

        p1 = self.writepoint([self.face1[0][0], 0.0], self.mesh)
        p2 = self.writepoint([self.face1[-1][0], 0.0], self.mesh)
        interfacepoints1 = []
        interfacelines1 = []
        for i, p in enumerate(self.face1):
            interfacepoints1.append(self.writepoint(p, self.mesh))
            if i>0:
                interfacelines1.append(self.writeline(self.pointid - 1, self.pointid))
        l1 = self.writeline(p1, interfacepoints1[0])
        l2 = self.writeline(p1, p2)
        l3 = self.writeline(p2, interfacepoints1[-1])
        ll = self.writelineloop([-l1, l2, l3] + self.reverselines(interfacelines1))


        interfacepoints2 = []
        interfacelines2 = []
        for i, p in enumerate(self.face2):
            interfacepoints2.append(self.writepoint(p, self.mesh))
            if i>0:
                interfacelines2.append(self.writeline(self.pointid - 1, self.pointid))
        
        l1 = self.writeline(interfacepoints1[0], interfacepoints2[0])
        l2 = self.writeline(interfacepoints1[-1], interfacepoints2[-1])
        self.writelineloop([-l1] + interfacelines1 + [l2] + self.reverselines(interfacelines2))

        p1 = self.writepoint([self.face1[0][0], 2.0 * h1 + h2], self.mesh)
        p2 = self.writepoint([self.face1[-1][0], 2.0 * h1 + h2], self.mesh)
        l1 = self.writeline(interfacepoints2[0], p1)
        l2 = self.writeline(p1, p2)
        l3 = self.writeline(interfacepoints2[-1], p2)
        self.writelineloop(interfacelines2 + [l3, -l2, -l1])





    def reverselines(self, linelist):
        return [-l for l in linelist[::-1]]

    def writeline(self, p1, p2):
        with open(self.file, 'a') as o:
            self.lineid +=1
            o.write('Line(%i) = {%i, %i};\n' % (self.lineid, p1, p2) )
        return self.lineid

    def writelineloop(self, linelist):
        with open(self.file, 'a') as o:
            self.loopid += 1
            o.write('Line Loop(%i) = {%s};\n' % (self.loopid, ','.join([str(s) for s in linelist])))
        self.writeplanesurface(self.loopid)
        return self.loopid

    def writepoint(self, v, mesh):
        with open(self.file, 'a') as o:
            self.pointid +=1
            o.write('Point(%i) = {%f, %f, 0.0, %f};\n' % (self.pointid, v[0], v[1], mesh))
        return self.pointid

    def writeplanesurface(self, loopid):
        with open(self.file, 'a') as o:
            self.surfaceid += 1
            o.write('Plane Surface(%i) = {%i};\n' % (self.surfaceid, loopid))


signal1 = createperlin(1000, 10, 100, .25, .1)
signal2 = createperlin(100, 10, 50, .02, .1)
h1 = 2.0
h2 = 2.0
f1 = PerlinLaminate(signal1, signal2, h1, h2, 'test.geo')

