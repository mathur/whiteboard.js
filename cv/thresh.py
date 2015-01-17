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

def hsv(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

def blackThresh(img):
    channels = cv2.split(img)
    sat = channels[1]
    sat = cv2.threshold(sat,blackSThresh,255,
                        cv2.THRESH_BINARY_INV)[1]
    val = channels[2]
    val = cv2.threshold(val,blackVThresh,255,
                        cv2.THRESH_BINARY_INV)[1]
    return cv2.bitwise_and(sat,val)

def holeOpen(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel,
                            iterations=openSteps)

def holeClose(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel,
                            iterations=closeSteps)

def corners(img):
    corners = cv2.cornerHarris(img,10,5,cornerK/255.0)
    corners = cv2.threshold(corners,1,255, cv2.THRESH_BINARY)[1]
    # img = cv2.convertScaleAbs(img)
    return (img,corners)

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

def overlayCorners(pair):
    global x,y,coords,corners
    (img,corners) = pair
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

    x = np.asarray(range(corners.shape[0]))
    y = np.asarray(range(corners.shape[1]))
    coords = cartesian([x,y])
    for coord in coords[corners.flatten() > 1]:
        cv2.circle(img,(coord[1],coord[0]),20,(0,0,255))
    return img

def pipeline(fs):
    def fn(x):
        for f in fs:
            x = f(x)
        return x
    return fn

if __name__ == '__main__':
    import imstream
    process = [hsv,blackThresh,holeOpen,holeClose,corners,
               overlayCorners]
    imstream.runStream(pipeline(process), winName=winName, init=initGui)

