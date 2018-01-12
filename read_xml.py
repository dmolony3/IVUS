import numpy as np
import xml.etree.ElementTree as ET
def read(path):
    tree = ET.parse(path)
    root = tree.getroot()
    print(root.tag)
    root.attrib
    print(root[0].text)
    points = []
    no_points = []
    d={}
    for child in root:
        # use text to see the values in the tags
        #print(child.tag, child.text)
        for imageState in child.iter('ImageState'):
            xdim = imageState.find('Xdim').text
            ydim = imageState.find('Ydim').text
            zdim = imageState.find('NumberOfFrames').text
        for imageCalibration in child.iter('ImageCalibration'):
            xres = imageCalibration.find('XCalibration').text
            yres = imageCalibration.find('YCalibration').text
            pullbackSpeed = imageCalibration.find('PullbackSpeed').text
            frameTime = imageCalibration.find('FrameTimeInMs').text
        for frameState in child.iter('FrameState'):
            xOffSet = frameState.find('Xoffset').text
            yOffSet = frameState.find('Yoffset').text
            fm = frameState.find('Fm').iter('Num')
            for frame in child.iter('Fm'):
                frameNo = frame.find('Num').text
                print 'Reading frame no %s' % (frameNo)
                for pts in child.iter('Ctr'):
                    subpoints = []
                    for child in pts:
                        if child.tag == 'Npts':
                            no_points.append(child.text)
                        elif child.tag == 'p':
                            subpoints.append(child.text)

                    points.append(subpoints)
                    d[frameNo] = subpoints
                 #   points.append(frame.find('p').text)


    # determine length of each list in points
    lenPoints = [len(x) for x in points]

    pointsX = []
    pointsY = []
    # split the points string into x and y components
    for i in range(0, len(points)):
        pointsX.append(map(lambda x:int(x.split(',')[0]), points[i]))
        pointsY.append(map(lambda x:int(x.split(',')[1]), points[i]))

    # convert to dictionary
    d1={}
    for a in range(0,len(points)):
        d1[a] = points[a]

    print((xdim, ydim, zdim))
    print((xres, yres))

    return d1, pointsX, pointsY, [xres, yres]
