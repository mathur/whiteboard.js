import cv2
import numpy as np

winName = 'threshold'

gaussianSize = 2

redSThresh = 59
redLowThresh = 151
redHighThresh = 8

openSteps = 0
closeSteps = 11

harrisSize = 10
cornerK = 17

clusterSize = 9

pipelineLen = 0
pipelineSize = 0

def assignVarCallback(varName):
    def fn(x):
        globals()[varName] = x
        print (varName + " = " + str(globals()[varName]))
    return fn

def makeTrackbar(winName,var,maxVal=255):
    cv2.createTrackbar(var, winName, globals()[var], maxVal, 
                       assignVarCallback(var))

def initGui():
    makeTrackbar(winName,'gaussianSize')
    makeTrackbar(winName,'redSThresh')
    makeTrackbar(winName,'redLowThresh')
    makeTrackbar(winName,'redHighThresh')
    # makeTrackbar(winName,'openSteps')
    makeTrackbar(winName,'harrisSize')
    makeTrackbar(winName,'closeSteps')
    makeTrackbar(winName,'cornerK')
    makeTrackbar(winName,'clusterSize')
    makeTrackbar(winName,'pipelineLen',pipelineSize)

# From http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out

def hsv(orig,img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

def gaussian(orig,img):
    return cv2.GaussianBlur(img, (2*gaussianSize+1,2*gaussianSize+1), 
                            50)

def redThresh(orig,img):
    channels = cv2.split(img)
    sat = channels[1]
    sat = cv2.threshold(sat,redSThresh,255,
                        cv2.THRESH_BINARY)[1]
    hue = channels[0]
    high,low = redHighThresh,redLowThresh
    resultFn = cv2.bitwise_and if high > low else cv2.bitwise_or
    hLow  = cv2.threshold(hue,high,255,
                          cv2.THRESH_BINARY_INV)[1]
    hHigh = cv2.threshold(hue,low,255,
                          cv2.THRESH_BINARY)[1]
    return cv2.bitwise_and(sat,resultFn(hLow,hHigh))

def holeOpen(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel,
                            iterations=openSteps)

def holeClose(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel,
                            iterations=closeSteps)

def corners(orig,img):
    dim = (img.shape[0] + img.shape[1])/2.0
    corners = cv2.cornerHarris(img,
                               max(1,int(harrisSize/255.0*dim/5.0)),7,
                               cornerK/255.0)
    corners = cv2.threshold(corners,1,255, cv2.THRESH_BINARY)[1]
    # img = cv2.convertScaleAbs(img)
    x = np.asarray(range(corners.shape[0]))
    y = np.asarray(range(corners.shape[1]))
    coords = cartesian([x,y])
    corners = np.asarray([(coord[1],coord[0]) for coord in
                          coords[corners.flatten() > 1]])
    def distSq(p1,p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx*dx + dy*dy

    print (img.shape)
    maxDist = clusterSize/255.0 * (img.shape[0]+img.shape[1])/2.0
    print (maxDist)

    i = 0
    while i < len(corners):
        thisInd = np.asarray([j <= i for j in
                                range(len(corners))])
        pt = corners[[i]*len(corners)].transpose()
        noCluster = distSq(pt,corners.transpose()) > maxDist*maxDist
        corners = corners[np.logical_or(thisInd,noCluster)]

        i += 1
    return (img,corners)

def overlayCorners(orig,pair):
    orig = orig.copy()
    (img,corners) = pair
    orig[img > 100] = [0,0,255]
    for coord in corners:
        cv2.circle(orig,(coord[0],coord[1]),20,(255,0,0),-1)
    print(len(corners))
    return orig

def extractRects(orig,pair):
    (img,corners) = pair
    def isHoriz(p1,p2):
        dx = abs(p2[0] - p1[0])
        dy = abs(p2[1] - p1[1])
        return dy < 0.1*dx
    def isVert(p1,p2):
        dx = abs(p2[0] - p1[0])
        dy = abs(p2[1] - p1[1])
        return dx < 0.1*dy

    def rects(corners):
        corners = np.asarray(corners)

        inds = np.asarray(range(len(corners)))
        print (str(len(inds)) + ": " + str(inds))
        inds = cartesian([inds]*3)
        indsT = inds.transpose()
        validInds = np.asarray([True] * inds.shape[0])
        for i in range(4):
            for j in range(i+1,4):
                nextStep = (indsT[i] != indsT[j])
                validInds = np.logical_and(validInds,nextStep)
        quads = corners[inds][validInds]
        quadsT = quads.transpose()
        validQuads = np.asarray([True] * quads.shape[0])
        horiz = True
        for i in range(4):
            nxt = (i+1)%4
            fn = isHoriz if horiz else isVert
            ind = 0 if horiz else 1
            compare = (lambda a,b: a >= b) if (i < 2) else \
                      (lambda a,b: a <= b)
            validEdge = np.logical_and(fn(quadsT[:,i],quadsT[:,nxt]),
                                       compare(quadsT[ind,i],
                                               quadsT[ind,nxt]))
            validQuads = np.logical_and(validQuads,validEdge)
            horiz = not horiz
        return quads[validQuads]

        # for i in xrange(len(corners)):
        #     for j in xrange(len(corners)):
        #         if i == j:
        #             continue
        #         if corners[i][0] >= corners[j][0]:
        #             continue
        #         if not isHoriz(corners[i],corners[j]):
        #             continue
        #         for k in xrange(len(corners)):
        #             if k in [i,j]:
        #                 continue
        #             if corners[j][1] >= corners[k][1]:
        #                 continue
        #             if not isVert(corners[j],corners[k]):
        #                 continue
        #             for l in xrange(len(corners)):
        #                 if l in [i,j,k]:
        #                     continue
        #                 if corners[k][0] <= corners[l][0]:
        #                     continue
        #                 if not isHoriz(corners[k],corners[l]):
        #                     continue
        #                 if not isVert(corners[i],corners[l]):
        #                     continue
        #                 top   = (corners[i][1] + corners[j][1])/2.0
        #                 right = (corners[j][0] + corners[k][0])/2.0
        #                 bot   = (corners[k][1] + corners[l][1])/2.0
        #                 left  = (corners[l][0] + corners[i][0])/2.0
        #                 yield ((left,top),(right,bot))
    return (img,list(rects(corners)))

def overlayRects(orig,pair):
    (img,rects) = pair
    orig = orig.copy()

    for rect in rects:
        cv2.rectangle(orig,rect[0],rect[1],(0,0,255))
    return orig

def pipeline(fs):
    global pipelineLen,pipelineSize
    def fn(x):
        x0 = x
        i = 0
        for f in fs:
            if i >= pipelineLen:
                break
            x = f(x0,x)
            i += 1
        if type(x) == tuple:
            x = x[0]
        return x
    pipelineLen = pipelineSize = len(fs)
    return fn

if __name__ == '__main__':
    import imstream
    process = [gaussian,hsv,redThresh,holeOpen,holeClose,corners,
               # extractRects,overlayRects]
               overlayCorners]
    imstream.runStream(pipeline(process), winName=winName,
                       init=initGui,filename='whiteboard.jpg')

