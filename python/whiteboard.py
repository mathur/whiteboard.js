import cv2
import numpy as np
import json

winName = 'threshold'

gaussianSize = 2

redSThresh = 55
redLowThresh = 151
redHighThresh = 8
yelLowThresh  = 15
yelHighThresh = 30
bluLowThresh  = 105
bluHighThresh = 120
grnLowThresh  = 75
grnHighThresh = 95

openSteps = 2
closeSteps = 5

harrisSize = 10
cornerK = 17

clusterSize = 9

polyApproxK = 40

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
    # makeTrackbar(winName,'gaussianSize')
    makeTrackbar(winName,'redSThresh')
    makeTrackbar(winName,'redLowThresh')
    makeTrackbar(winName,'redHighThresh')
    # makeTrackbar(winName,'openSteps')
    makeTrackbar(winName,'harrisSize')
    makeTrackbar(winName,'closeSteps')
    makeTrackbar(winName,'polyApproxK')
    # makeTrackbar(winName,'cornerK')
    # makeTrackbar(winName,'clusterSize')
    makeTrackbar(winName,'pipelineLen',pipelineSize)

def isHoriz(p1,p2):
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    return dy < 0.15*dx
def isVert(p1,p2):
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    return dx < 0.15*dy

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

def thresh(sThreshVar,lowHueVar,highHueVar):
    def threshold(orig,img):
        sThresh = globals()[sThreshVar]
        lowHue = globals()[lowHueVar]
        highHue = globals()[highHueVar]
        channels = cv2.split(img)
        sat = channels[1]
        sat = cv2.threshold(sat,sThresh,255,
                            cv2.THRESH_BINARY)[1]
        hue = channels[0]
        high,low = highHue,lowHue
        resultFn = cv2.bitwise_and if high > low else cv2.bitwise_or
        hLow  = cv2.threshold(hue,high,255,
                            cv2.THRESH_BINARY_INV)[1]
        hHigh = cv2.threshold(hue,low,255,
                            cv2.THRESH_BINARY)[1]
        return cv2.bitwise_and(sat,resultFn(hLow,hHigh))
    return threshold

def holeOpen(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel,
                            iterations=openSteps)

def holeClose(orig,img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    return cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel,
                            iterations=closeSteps)

def extractContours(orig,img):
    return (img,cv2.findContours(img,cv2.RETR_TREE,
                                 cv2.CHAIN_APPROX_SIMPLE))

def polyApprox(orig,pair):
    (img,(contours,hierarchy)) = pair
    hulls = (cv2.convexHull(c) for c in contours)
    polys = (cv2.approxPolyDP(c,polyApproxK,True) for c in hulls)
    contours = np.asarray(list(polys))
    return (img,(contours,hierarchy))

def buildHierarchy(orig,pair):
    (img,(contours,hierarchy)) = pair
    hierarchy = hierarchy[0]

    def readContentType(c):
        # print ("Contents of " + str(c))
        if c.shape[0] == 2:
            if abs(c[0,0,0]-c[1,0,0]) > abs(c[0,0,1]-c[1,0,1]) :
                return 'txt'
            else:
                return 'img'
        return ''

    def readGlyph(rect):
        bluProcess = [gaussian,hsv,
                      thresh('redSThresh','bluLowThresh','bluHighThresh'),
                      holeOpen,holeClose,extractContours,polyApprox]
        yelProcess = [gaussian,hsv,
                      thresh('redSThresh','yelLowThresh','yelHighThresh'),
                      holeOpen,holeClose,extractContours,polyApprox]
        grnProcess = [gaussian,hsv,
                      thresh('redSThresh','grnLowThresh','grnHighThresh'),
                      holeOpen,holeClose,extractContours,polyApprox]
        x = rect['x']
        y = rect['y']
        w = rect['w']
        h = rect['h']
        # print (str(x) + "," + str(y) + ": " + str(w) + ","  + str(h))
        img = orig[y:y+h,x:x+w]
        # cv2.imshow("img",img.copy())
        # print (img.shape)

        pipes = [bluProcess,yelProcess,grnProcess]
        for i in range(len(pipes)):
            conts = pipeline(pipes[i])(img)
            which = ["blu","yel","grn"][i]
            # cv2.imshow(which,conts[0])
            # print ("Trying " + which)
            conts = conts[1][0]
            if not (conts is None) and len(conts) != 0 \
               and conts[0].shape[0] in [2,4]:
                # print (conts)
                return (i,readContentType(conts[0]))
        return (None,'')

    def addGlyphs(rects,idGlyph = None):
        if rects == []:
            return ([],None)
        if idGlyph == None:
            print (rects)
            if not ('children' in rects[0]) or rects[0]['w'] < 10 or\
               rects[0]['h'] < 10:
                return addGlyphs(rects[1:])
            rects = sorted(rects[0]['children'],key=lambda x:x['y'])
            glyph = readGlyph(rects[0])[0]
            return (addGlyphs(rects[1:],glyph),glyph)
        else:
            for r in rects:
                if not ('children' in r) or len(r['children']) == 0:
                    r['glyph'],r['div_type'] = readGlyph(r)
                elif len(r['children']) == 1:
                    child = r['children'][0]
                    cont = contours[child['index']]
                    if cont.shape[0] == 2:
                        r['div_type'] = readContentType(cont);
                        del r['children']
                        # r['children'] = None
                    else:
                        r['children'] = addGlyphs(r['children'],idGlyph)
                else:
                    r['children'] = addGlyphs(r['children'],idGlyph)
            return rects

    def buildChildren(i):
        while hierarchy[i][1] >= 0:
            i = hierarchy[i][1]
        rects = []
        while i >= 0:
            (x,y,w,h) = cv2.boundingRect(contours[i])
            rect = {'index':i,'x':x,'y':y,'w':w,'h':h}
            rect['class'] = None
            rect['div_type'] = 'div' if contours[i].shape[0] == 4 else \
                            readContentType(contours[i])          
            rect['glyph'] = None
            j = hierarchy[i][2]
            if j >= 0:
                rect['children'] = buildChildren(j)
            rects.append(rect)
            i = hierarchy[i][0]
        return rects

    def prune(rects):
        if type(rects) != list:
            return (float('inf'),float('inf'),-float('inf'),
                    -float('inf'))
        l = float('inf')
        t = float('inf')
        b = -float('inf')
        r = -float('inf')
        for i in range(len(rects)):
            rect = rects[i]
            # print ("Pruning!")
            l1 = rect['x']
            t1 = rect['y']
            b1 = t1 + rect['h']
            r1 = l1 + rect['w']
            (l,t,b,r) = (min(l,l1),min(t,t1),max(b,b1),max(r,r1))

            if 'children' in rect and not (rect['children'] is None) \
               and len(rect['children']) == 1:
                child = rect['children'][0]
                if child['w']*child['h'] >= \
                   0.8*rect['w']*rect['h']:
                    rects[i] = child
                    (l2,t2,b2,r2) = prune(rects)
                    (l,t,b,r) = (min(l,l2),min(t,t2),
                                 max(b,b2),max(r,r2))
            if 'children' in rect:
                (l2,t2,b2,r2) = prune(rect['children'])
                (l,t,b,r) = (min(l,l2),min(t,t2),max(b,b2),max(r,r2))
        return (l,t,b,r)

    children = buildChildren(0)
    children = addGlyphs(children)
    (l,t,b,r) = prune(children[0])

    result = [{'glyph':children[1],'x':l,'y':t,'w':(r-l),
               'h':(b-t),'div_type':'div','class':None,
               'children':children[0]}]

    return (img,(contours,hierarchy,result))

def printHierarchy(orig,pair):
    (img,(contours,hierarchy,obj)) = pair
    print (repr(obj))
    return (img,(contours,hierarchy,obj))

def drawHierarchy(orig,pair):
    (img,(contours,hierarchy,obj)) = pair

    orig = orig.copy()

    colors = [(0,0,255),(255,0,255),(255,255,0),(0,0,0)]

    glyphs = [(255,0,0),(0,255,255),(0,255,0)]

    def draw(rects,i = 0):
        children = []
        for r in rects:
            x = r['x']
            y = r['y']
            w = r['w']
            h = r['h']
            cv2.rectangle(orig,(x,y),(x+w,y+h),colors[i],thickness=-1)
            if r['glyph'] != None:
                ind = r['glyph']%len(glyphs)
                cv2.rectangle(orig,(x,y),(x+w,y+h),glyphs[ind],thickness=30)
            if r['div_type'] == 'img':
                ind = (i+1)%len(colors)
                cv2.circle(orig,(x+w/2,y+h/2),int(0.25*min(w,h)),
                           colors[ind],thickness=30)
            elif r['div_type'] == 'txt':
                ind = (i+1)%len(colors)
                cv2.rectangle(orig,(x+w/4,y+h/4),
                              (x+(3*w)/4,y+(3*h)/4),
                              colors[ind],thickness=30)
            if 'children' in r and r['children'] != None:
                children += r['children']
        if len(children) > 0:
            draw(children,(i+1)%len(colors))

    draw(obj)

    # print (repr(obj))

    return orig

def drawContours(orig,pair):
    (img,(contours,hierarchy)) = pair
    orig = orig.copy()
    # print (hierarchy)
    cv2.drawContours(orig,contours,-1,(0,255,0),thickness=10)
    return orig

def pipeline(fs):
    def fn(x):
        x0 = x
        for f in fs:
            x = f(x0,x)
        return x
    return fn

def globPipeline(fs):
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

wholeProcess = [gaussian,hsv,
                thresh('redSThresh','redLowThresh','redHighThresh'),
                holeOpen,holeClose,extractContours,polyApprox,
                # drawContours]
                buildHierarchy] 

def extractStructure(img):
    return pipeline(wholeProcess)(img)[1][2]

def parseWhiteboard(filename):
    return extractStructure(cv2.imread(filename))

def swallow(f):
    def fn(x):
        try: 
            return f(x)
        except:
            import traceback
            print (sys.exc_info()[0])
            traceback.print_tb(sys.exc_info()[2])
            return x
    return fn

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print (repr([parseWhiteboard(f) for f in sys.argv[1:]]))
    else:
        import imstream
        pipe = globPipeline(wholeProcess + [printHierarchy,drawHierarchy])
        imstream.runStream(swallow(pipe), winName=winName,
                           init=initGui,filename='IMG_2.jpg')

