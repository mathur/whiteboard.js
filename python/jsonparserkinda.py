import json
import whiteboard
import sys
#import sendgrid
import pprint
import random
from subprocess import call
import os

folder = "/"

api_user="rohan32"
api_key="hackru"

text=["hack", "pennapps", "cloud", "service", "node.js", "html5", "continuous integration","I'd like to inteject, that thing you've been referring to as linux is actually GNU linux, or as I've taken to calling it, GNU + Linux","webscale","scalability","API","cross-platform","Rubber-Duck Debugging","dev-ops","github", "software", "programming", "is", "the", "cool", "doge", "bitcoin", "so", "very"]

def get_text_of_width(w,h):
    div_text=""
    for i in range(w*h/5000):
        div_text+=random.choice(text)+" "
    return div_text

def create_div(rect, offset = (0,0), containerSize = (0,0)):
    #print rect
    loc = (int(rect['x']/2.5-offset[0]/2.5),int(rect['y']/2.5-offset[1]/2.5))
    size = (int(rect['w']/2.5),int(rect['h']/2.5))
    loc = (loc[0] + size[0]/5,loc[1] + size[1]/5)
    size = ((4*size[0])/5,(4*size[1])/5)
#    if containerSize[0] == 0:
#        containerSize = (size[0],containerSize[1])
#    if containerSize[1] == 0:
#        containerSize = (containerSize[0],size[1])
    #percentSize = (int(size[0]/float(containerSize[0])*100),
                   #int(size[1]/float(containerSize[1])*100))
    #div_string="<div style='width:"+str(percentSize[0]) + "%;height:"   \
    #           + str(percentSize[1]) + "%'>"
    div_string="<div style='position:absolute;top:" + str(loc[1]) + "px;left:" \
               + str(loc[0]) + "px;width:"+str(size[0]) + "px;height:"   \
               + str(size[1]) + "px'>"
    if (rect['div_type']=='txt'):
        div_string+=get_text_of_width(size[0],size[1])
    elif (rect['div_type']=='img'):
        div_string+="<img alt='cats are awesome' src='http://placekitten.com/g/"+str(rect['w'])+"/"+str(rect['h'])+"' width="+str(size[0])+"px height="+str(size[1])+"px >"

    if (rect['glyph']!=None):
        div_string+="<a href='./page_"+str(rect['glyph'])+".html' alt='woah, a hyperlink'>go to page "+str(rect['glyph'])+"</a>"
    div_string += "</div>" 
    if 'children' in rect:
        children = sorted(rect['children'], key=lambda k: (k['y'],k['x']))
        for child in children:
            div_string+=create_div(child,offset)
    return div_string

def parse_body(body,loc,size):
    print body
    html_body="<body>"
    for item in body:
        html_body+=create_div(item,loc)
    return html_body+"</body>"

if __name__ == "__main__":
    print sys.argv[2:]
    pages = map(whiteboard.parseWhiteboard,sys.argv[2:])
    dir_name=sys.argv[1]
    print "Saving files in",dir_name

    call(["mkdir",dir_name])
    os.system("rm -r " + dir_name + "/*")
    os.system("cp -r /root/whiteboardjs/nodejs/* " + dir_name + "/")
    #print "Copying node..."
    for page in pages:
	page = page[0]
        name = dir_name + "/page_" + str(page['glyph']) + '.html'
        page['children'] = sorted(page['children'], key=lambda k: (k['y'],k['x']))
        children = page['children']
	body = children

        html_page = "<html>" + parse_body(body,(page['x'],page['y']),
					       (page['w'],page['h'])) \
			     + "</html>"
        with open(name,"w") as f:
            f.write(html_page)
	continue

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
        continue

	print "restarting nodemon..."
	os.chdir(dir_name)
    	call(["killall","node"])
    	call(["npm","install"])
    	call(["nodemon","index.js"])
        #print "sending email..."
        #sg = sendgrid.SendGridClient(api_user,api_key)
        #message = sendgrid.Mail()
        #message.add_to("petermitrano@gmail.edu")
        #message.add_to("rohan@rmathur.com")
        #message.set_from("board@whiteboardjs.me")
        #message.set_subject("Your New Website")
        #message.set_html("Here's your new website, it's live <a href='104.131.20.236/"+dir_name+"/'>here</a>")
        #sg.send(message)

