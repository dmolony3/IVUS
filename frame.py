# this class is an IVUS frame, can perform operations such as plaque burden
import os
import contour
import read_xml
import read_IVUS
import numpy as np
import PolarToIm as p2im
import matplotlib.pyplot as plt
from cv2 import drawContours, circle


class Frame:
    def __init__(self, path, filename):
        self.frameNo = 0
        self.resolution = 0.02
        self.filename = filename
        self.path = path
        self.thickness = 0

        self.read_IVUS()
        self.read_xml()
        #self.IVUS = read_IVUS(self)
       # define inner and outer contours instances
        self.inner = []
        self.outer = []
        self.centroid = []


    def read_IVUS(self):
        # read IVUS images
        # guess the file extension based on maximum
        exts = ['.tif',  '.jpg']
        files = os.listdir(self.path)
        tif_files = [file for file in files if file.endswith(exts[0])]
        jpg_files = [file for file in files if file.endswith(exts[1])]
        ext_idx = 1 if len(jpg_files) > len(tif_files) else 0
        IVUS = read_IVUS.read(self.path, exts[ext_idx])
        self.noImages = IVUS.shape[0]
        self.IVUS = IVUS

    def read_xml(self):
        # read xml file and obtain contours and resolution
        contours, x, y, resolution = read_xml.read(self.filename)

        # sort into inner and outer contours (list)
        xInner = [x[i] for i in range(0, len(x), 2)]
        yInner = [y[i] for i in range(0, len(y), 2)]
        xOuter = [x[i] for i in range(1, len(x), 2)]
        yOuter = [y[i] for i in range(1, len(y), 2)]

        self.xInner = xInner
        self.yInner = yInner
        self.xOuter = xOuter
        self.yOuter = yOuter
        self.resolution = float(resolution[0])

    def contour(self):
        # get IVUS image dimensions for finding image centroid
        image_centroid = [int(self.IVUS.shape[1]//2), int(self.IVUS.shape[2]//2)]

        # get contours for all images
        for i in range(0, len(self.xInner)):
            #self.inner[i] = contour.Contour(self.xInner[i], self.yInner[i])
            #self.outer[i] = contour.Contour(self.xOuter[i], self.yOuter[i])
            self.inner.append(contour.Contour(self.xInner[i], self.yInner[i], image_centroid))
            self.outer.append(contour.Contour(self.xOuter[i], self.yOuter[i], image_centroid))
            self.centroid.append(self.inner[i].centroid())
        print('Creating list of contours')

    def getthickness(self):
        thickness = np.zeros([len(self.inner), 360])
        # measure plaque thickness
        for i in range(0, len(self.inner)):
            # convert contours to polar coordinates and interpolate
            self.inner[i].cart2pol()
            self.inner[i].interp()
            self.outer[i].cart2pol()
            self.outer[i].interp()
            # get masks
            inner_mask = self.inner[i].maskImage()
            outer_mask = self.outer[i].maskImage()

            # sum masks
            thickness[i, :] = np.sum(outer_mask, axis=0) - np.sum(inner_mask, axis=0)

        thickness = thickness*self.resolution

        self.thickness = thickness

        return thickness

    def getarea(self):
        # determine lumen, plaque and vessel area of contours
        lumenArea = np.zeros([len(self.inner), 1])
        vesselArea = np.zeros([len(self.inner), 1])
        plaqueArea = np.zeros([len(self.inner), 1])

        for i in range(0, len(self.inner)):
            lumenArea[i] = self.inner[i].contourArea()
            vesselArea[i] = self.outer[i].contourArea()
            plaqueArea[i] = vesselArea[i] - lumenArea[i]

        self.lumenArea = plaqueArea*self.resolution**2
        self.vesselArea = vesselArea*self.resolution**2
        self.plaqueArea = plaqueArea*self.resolution**2

        return self.lumenArea, self.vesselArea, self.plaqueArea

    def plaqueDeprecated(self):
        # this function returns a masked frame of just the plaque and perivascular data (remaining pixels set to zero)

        # pre-allocate memory
        peri = np.zeros(self.IVUS.shape)
        plaque = np.zeros(self.IVUS.shape)

        for i in range(0, 1):
            # get masks
            lumenMask = self.inner[i].maskImage()
            vesselMask = self.outer[i].maskImage()
            periMask = vesselMask - np.ones(vesselMask.shape)

            periMask[periMask == - 1] = 1

            plaqueMask = vesselMask - lumenMask
            imMask = plaqueMask + periMask*2
            imshape = self.IVUS[i, :, :].shape
            cartmask = p2im.PolarToIm(imMask, 0, 1, imshape[0], imshape[1])

            cartmask = cartmask.astype(int)
            periMask = cartmask.copy()
            #periMask[periMask != 2] = 0
            #periMask[periMask == 2] = 1
            periMask[periMask < 127] = 0
            periMask[periMask >= 127] = 1

            plaqueMask = cartmask.copy()
            #plaqueMask[plaqueMask != 1] = 0
            plaqueMask[plaqueMask >= 127] = 0
            plaqueMask[plaqueMask < 127] = 1
            peri[i, :, :] = self.IVUS[i, :, :]*periMask
            plaque[i, :, :] = self.IVUS[i, :, :]*plaqueMask

        self.periMask = peri
        self.plaqueMask = plaque
        return peri, plaque

    def getplaque(self):

        plaque = np.zeros(self.IVUS.shape, dtype=np.int8)
        peri = np.zeros(self.IVUS.shape, dtype=np.int8)
        plaqueMask = np.zeros(self.IVUS.shape, dtype=np.uint8)
        periMask = np.zeros(self.IVUS.shape, dtype=np.uint8)
        centroid = [self.IVUS.shape[1], self.IVUS.shape[2]]
        # determine the number of images to process based on the minimum max of IVUS and xInner
        no_images = min(self.IVUS.shape[0], len(self.xInner))
        for i in range(0, no_images):
            # put contour in cv2 x, y format
            IVUS = self.IVUS[i, :, :].copy()
            contin = []
            for j in range(0, len(self.xInner[i])):
                contin.append((self.xInner[i][j], self.yInner[i][j]))

            contin = np.squeeze(np.asarray(contin, dtype=int))
            fill = -1 # value of -1 indicates contour will be filled
            value = -1 # intensity value

            mask = drawContours(np.zeros(IVUS.shape), [contin], 0, value, fill)
            lumenMask = np.array(mask, dtype=np.int8).copy()

            # repeat for outer contour
            contout = []

            for j in range(0, len(self.xOuter[i])):
                contout.append((self.xOuter[i][j], self.yOuter[i][j]))

            contout = np.squeeze(np.asarray(contout, dtype=int))

            mask = drawContours(np.zeros(IVUS.shape), [contout], 0, value, fill)
            vesselMask = np.array(mask, dtype=np.int8).copy()

            lumenMask[lumenMask >= 0] = 0
            lumenMask[lumenMask == - 1] = 1
            vesselMask[vesselMask >= 0] = 0
            vesselMask[vesselMask == - 1] = 1

            # create circle to define image boundary
            circ = circle(IVUS, (centroid[0], centroid[1]), centroid[0], 1, -1).astype(np.int8)
            circ[circ != 1] = 0

            plaqueMask[i, :, :] = vesselMask - lumenMask
            periMask[i, :, :] = circ - vesselMask

            #plaque[i, :, :] = np.multiply(IVUS,plaqueMask)
            #plaque = self.IVUS[i, :, ].astype(int)*plaqueMask.astype(int)
            #peri[i, :, :] = IVUS*periMask

        return periMask, plaqueMask