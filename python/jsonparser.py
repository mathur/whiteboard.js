import json
import sys
import sendgrid
import pprint
import random
from subprocess import call

api_user="rohan32"

api_key="hackru"

text=["hack", "pennapps", "cloud", "service", "node.js", "html5", "continuous integration",
#"I'd like to inteject, that thing you've been referring to as linux is actually GNU linux, or as I've taken to calling it, GNU + Linux",
"webscale","scalability","API","cross-platform","Rubber-Duck Debugging","dev-ops","github", "software", "programming", "is", "the", "cool",
 "doge", "bitcoin", "so", "very"]



def get_text_of_width(w,h):
    div_text=""
    for i in range(w*h/5000):
        div_text+=random.choice(text)+" "
    return div_text



def split(rect,dim):
    count=1 #how many rows/cols you've found
    dims=[] #list of rows or cols
    length = len(rect['children'])
    coord='0'
    dcoord='0'

    if (dim=='row'):
        cord='y'
        dcord='h'
    elif (dim=='col'):
        cord='x'
        dcord='w'

    rect['children'] = sorted(rect['children'], key=lambda k:k[coord])

    #iterate over all children
    for i in range(length):
        child=rect['children'][i]
    
        #add a new row or column if nessecary
        if (len(dims)<count):
            dims.append([])

        #add the child to a row/col
        dims[count-1].append(child)

        if (i<length-1):
            nextChild=rect['children'][i+1]
        
            #check for a gap
            if (child[coord]+child[dcoord]<nextChild[coord]):
                count+=1        

    #check if we found any gaps
    print rect,dim,count

    if (count>1):
        #how many cols it will span--not used for rows
        inc = 12/count
        newDims=[]
        for i in range(count):
            newDim={'x':0,'y':0,'w':0,'h':0,'div_type':'','glyph':None,'children':dims[i]}
            newDims.append(newDim)
            if (dim=='row'):
                newDim['class'] = "row"
            elif (dim=='col'):
                newDim['class'] = "col-md-"+str(inc)
        return newDims
    else:
        return False;


    

def subdivide(rect):
    """ returns to me the string of the html of the children with row and column classes
    """
    html=""

    #check if splittable into rows
    #rows is the list of rows
    rows=split(rect,"row")
    cols=split(rect,"cols")
    if (rows):
        for row in rows: #each row is a rect with the children added into it
            subdivide(row)
    elif (cols):
        for col in cols:
            subdivide(cols)
    else:
        create_div(rect)




def create_div(rect):
    
    div_string=("<div style='"+ 
                "width:"+str(rect['w'])+";"+         
                "height:"+str(rect['h'])+";'")

    #add class if it exists
    if (rect['class']!=None):
        div_string+=" class='"+rect['class']+"' "
    
    #close it
    div_string+=">"
        
    #add text or image
    if (rect['div_type']=='text'):
        div_string+=get_text_of_width(rect['w'],rect['h'])
    elif (rect['div_type']=='image'):
        div_string+="<img alt='cats are awesome' src='http://placekitten.com/g/"+   \
                str(rect['w'])+"/"+str(rect['h'])+"' width="+str(rect['w'])+" height="+str(rect['h'])+" >"

    #add hyperlink
    if (rect['glyph']!=None):
        div_string+="<a href='http://104.131.20.236/page_"+str(rect['glyph'])+"' alt='woah, a hyperlink'>go to page "+str(rect['glyph'])+"</a>"

    if (len(rect['children'])>1):
        #returns to me the string of the html of the children with row and column classes
        div_string+=subdivide(rect) 
    
    div_string+="</div>"

    return div_string

def parse_header(header):
    html_header="<div>"
    if (header!=""):
        html_header+=create_div(header)
    return html_header+"</div>"

def parse_body(body):
    html_body="<body>"
    for item in body:
        html_body+=create_div(item)
    return html_body+"</body>"

def parse_footer(footer):
    html_footer="<div>"
    if (footer!=''):
        html_footer+=create_div(footer)
    return html_footer+"</div>"

def parse_pages():
    pages = [
            {'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'class': None,'div_type': '', 'glyph': 0, 'children': [ #page 1
                {'x': 0, 'y': 0, 'w': 1000, 'h': 40, 'class': None,'div_type': 'text', 'glyph': 1, 'children': []},  #header
                {'x': 400, 'y': 200, 'w': 600, 'h': 400,'class': None, 'div_type': '', 'glyph': None, 'children': [ #body
                    {'x': 0, 'y': 0, 'w': 300, 'h': 400,'class': None,'div_type': 'text', 'glyph': None, 'children': []}, 
                    {'x': 350, 'y': 0, 'w': 300, 'h': 400,'class': None,'div_type': 'image', 'glyph': None, 'children': []}, 
                    {'x': 700, 'y': 450, 'w': 300, 'h': 200,'class': None, 'div_type': 'text', 'glyph': None, 'children': []}, 
                    {'x': 700, 'y': 450, 'w': 300, 'h': 200, 'class': None, 'div_type': 'image', 'glyph': None, 'children': []}
                ]}
            ]}, 
            {'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'div_type': '', 'glyph': 1, 'children': [ #page 2
                {'x': 0, 'y': 0, 'w': 1000, 'h': 100, 'div_type': 'text', 'glyph': 0, 'children': []} #body
            ]}]


    for page in pages:
        page['children'] = sorted(page['children'], key=lambda k: k['y'])
        children = page['children']
        if (len(children) == 1):
            body = [children[0]]
            header=""
            footer=""
        elif (len(children) == 2):
            header = children[0]
            body = [children[1]]
            footer=""
        else:
            header = children[0]
            body = [children[1:len(children) - 1]]
            footer = children[len(children) - 1]

        html_page = "<html>" + parse_header(header) + parse_body(body) + parse_footer(footer) + "</html>"

        f = open("page_"+str(page['glyph'])+".html",'w')
        f.write(html_page)
        f.close()


        
def dostuff():
    # call opencv program to analyze images

    # read python output of opencv    
    
    dir_name="/var/www/html/"+str(sys.argv[1]) #str(int(time.time()))
    print "Saving files in",dir_name

    call(["mkdir",dir_name])
    call(["cp","-r /root/nodejs/* "+dir_name])
    print "Copying node..."

    parse_pages()

    print "restarting nodemon..."
    os.chdir(dir_name)
    call(["killall","node"])
    call(["npm","install"])
    call(["nodemon","index.js"])

    if (page == pages[0]):
        dust_filename=dir_name+"public/templates/index.dust"
        js_filename=dir_name+"controllers/index.js"
        js_path="/"
        render_path="index"
    else :
        dust_filename=dir_name+"public/templates/page_"+str(page['glyph'])+".dust"
        js_filename=dir_name+"controllers/page_"+str(page['glyph'])+".js"
        js_path="page_"+str(page['glyph'])
        render_path="page_"+str(page['glyph'])

    f_dust = open(dust_filename,'w')
    f_dust.write("{>'layouts/master' /}")
    f_dust.write("{<body}")
    f_dust.write(html_page)
    f_dust.write("{/body}")

    f_js = open(js_filename,'w')
    j_s.write("'use strict;'")
    j_s.write("module.exports = function (app) { app.get('" + js_path + "', function(req,res){ res.render('" + render_path +"');});};")

    print "sending email..."
    sg = sendgrid.SendGridClient(api_user,api_key)
    message = sendgrid.Mail()
    message.add_to("petermitrano@gmail.edu")
    message.add_to("rohan@rmathur.com")
    message.set_from("board@whiteboardjs.me")
    message.set_subject("Your New Website")
    message.set_html("Here's your new website, it's live <a href='104.131.20.236/"+dir_name+"/'>here</a>")
    sg.send(message)

if __name__ == "__main__":
    parse_pages()