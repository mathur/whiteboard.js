import cv2
import numpy as np

winName = 'threshold'

blackSThresh = 59
blackVThresh = 136

openSteps = 1
closeSteps = 13

cornerK = 26

def assignVarCallback(varName):
    def fn(x):
        globals()[varName] = x
        print (varName + " = " + str(globals()[varName]))
    return fn

def makeTrackbar(winName,var):
    cv2.createTrackbar(var, winName, globals()[var], 255, 
                       assignVarCallback(var))

def initGui():
    makeTrackbar(winName,'blackSThresh')
    makeTrackbar(winName,'blackVThresh')
    makeTrackbar(winName,'openSteps')
    makeTrackbar(winName,'closeSteps')
    makeTrackbar(winName,'cornerK')

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

def blackThresh(orig,img):
    channels = cv2.split(img)
    sat = channels[1]
    sat = cv2.threshold(sat,blackSThresh,255,
                        cv2.THRESH_BINARY_INV)[1]
    val = channels[2]
    val = cv2.threshold(val,blackVThresh,255,
                        cv2.THRESH_BINARY_INV)[1]
    return cv2.bitwise_and(sat,val)

def holeOpen(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel,
                            iterations=openSteps)

def holeClose(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel,
                            iterations=closeSteps)

def corners(orig,img):
    corners = cv2.cornerHarris(img,10,5,cornerK/255.0)
    corners = cv2.threshold(corners,1,255, cv2.THRESH_BINARY)[1]
    # img = cv2.convertScaleAbs(img)
    x = np.asarray(range(corners.shape[0]))
    y = np.asarray(range(corners.shape[1]))
    coords = cartesian([x,y])
    corners = [(coord[1],coord[0]) for coord in
                coords[corners.flatten() > 1]]
    return (img,corners)

def overlayCorners(orig,pair):
    (img,corners) = pair
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    for coord in corners:
        cv2.circle(img,(coord[0],coord[1]),20,(0,0,255))
    return img

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
    def rects():
        quads = cartesian(cartesian(corners,corners),
                          cartesian(corners,corners))
        quadsT = quads.transpose()
        inds = np.asarray(range(len(corners)))
        inds = cartesian(cartesian(inds,inds),cartesian(inds,inds))
        indsT = inds.transpose()
        validInds = np.asarray([True] * inds.shape[0])
        for i in range(4):
            for j in range(4):
                if i != j:
                    nextStep = (indsT[i] != indsT[j])
                    validInds = validInds.logical_and(nextStep)
        for i in xrange(len(corners)):
            for j in xrange(len(corners)):
                if i == j:
                    continue
                if corners[i][0] >= corners[j][0]:
                    continue
                if not isHoriz(corners[i],corners[j]):
                    continue
                for k in xrange(len(corners)):
                    if k in [i,j]:
                        continue
                    if corners[j][1] >= corners[k][1]:
                        continue
                    if not isVert(corners[j],corners[k]):
                        continue
                    for l in xrange(len(corners)):
                        if l in [i,j,k]:
                            continue
                        if corners[k][0] <= corners[l][0]:
                            continue
                        if not isHoriz(corners[k],corners[l]):
                            continue
                        if not isVert(corners[i],corners[l]):
                            continue
                        top   = (corners[i][1] + corners[j][1])/2.0
                        right = (corners[j][0] + corners[k][0])/2.0
                        bot   = (corners[k][1] + corners[l][1])/2.0
                        left  = (corners[l][0] + corners[i][0])/2.0
                        yield ((left,top),(right,bot))
    return (img,list(rects()))

def overlayRects(orig,pair):
    (img,rects) = pair
    orig = orig.copy()

    for rect in rects:
        cv2.rectangle(orig,rect[0],rect[1],(0,0,255))
    return orig

def pipeline(fs):
    def fn(x):
        x0 = x
        for f in fs:
            x = f(x0,x)
        return x
    return fn

if __name__ == '__main__':
    import imstream
    process = [hsv,blackThresh,holeOpen,holeClose,corners,
               overlayCorners]#extractRects,overlayRects]
    imstream.runStream(pipeline(process), winName=winName, init=initGui)

