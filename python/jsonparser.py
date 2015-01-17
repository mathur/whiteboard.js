import json
import sendgrid
import pprint
import random
from subprocess import call

api_user="rohan32"
api_key="hackru"

text=["hack", "pennapps", "cloud", "service", "node.js", "html5", "continuous integration","I'd like to inteject, that thing you've been referring to as linux is actually GNU linux, or as I've taken to calling it, GNU + Linux","webscale","scalability","API","cross-platform","Rubber-Duck Debugging","dev-ops","github", "software", "programming", "is", "the", "cool", "doge", "bitcoin", "so", "very"]

def get_text_of_width(w,h):
    div_text=""
    for i in range(w*h/5000):
        div_text+=random.choice(text)+" "
    return div_text

def create_div(rect, offset=(0,0)):
    div_string="<div>"
    if (rect['div_type']=='text'):
        div_string+=get_text_of_width(rect['w'],rect['h'])
    elif (rect['div_type']=='image'):
        div_string+="<img alt='cats are awesome' src='http://placekitten.com/g/"+str(rect['w'])+"/"+str(rect['h'])+"' width="+str(rect['w'])+" height="+str(rect['h'])+" >"

    if (rect['glyph']!=None):
        div_string+="<a href='http://104.131.20.236/page_"+str(rect['glyph'])+"' alt='woah, a hyperlink'>go to page "+str(rect['glyph'])+"</a>"

    for child in rect['children']:
        div_string+=create_div(child)
    return div_string+"</div>"

def parse_header(header):]''
    html_header="<header>"
    if (header!=""):
        html_header+=create_div(header)
    return html_header+"</header>"

def parse_body(body):
    html_body="<body>"
    for item in body:
        html_body+=create_div(item)
    return html_body+"</body>"

def parse_footer(footer):
    html_footer="<footer>"
    if (footer!=''):
        html_footer+=create_div(footer)
    return html_footer+"</footer>"



if __name__ == "__main__":
    # call opencv program to analyze images

    # read python output of opencv

    pages = [
    			{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'div_type': '', 'glyph': 0, 'children': [
    				{'x': 0, 'y': 0, 'w': 1000, 'h': 40, 'div_type': 'text', 'glyph': 1, 'children': []}, 
    				{'x': 400, 'y': 200, 'w': 600, 'h': 400, 'div_type': '', 'glyph': None, 'children': [
        				{'x': 0, 'y': 0, 'w': 300, 'h': 400, 'div_type': 'text', 'glyph': None, 'children': []}, 
        				{'x': 300, 'y': 0, 'w': 300, 'h': 400, 'div_type': 'image', 'glyph': None, 'children': []}
        			]}
        		]}, 
        		{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'div_type': '', 'glyph': 1, 'children': [
					{'x': 0, 'y': 0, 'w': 1000, 'h': 100, 'div_type': 'text', 'glyph': 0, 'children': []}
        		]}]

    
    dir_name="/var/www/html/"+str(sys.argv[1]) #str(int(time.time()))
    print "Saving files in",dir_name

    call(["mkdir",dir_name])
    call(["cp","-r /root/nodejs/* "+dir_name])
    print "Copying node..."

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

    print "restarting nodemon..."
    os.chdir(dir_name)
    call(["killall","node"])
    call(["npm","install"])
    call(["nodemon","index.js"])

    print "sending email..."
    sg = sendgrid.SendGridClient(api_user,api_key)
    message = sendgrid.Mail()
    message.add_to("petermitrano@gmail.edu")
    message.add_to("rohan@rmathur.com")
    message.set_from("board@whiteboardjs.me")
    message.set_subject("Your New Website")
    message.set_html("Here's your new website, it's live <a href='104.131.20.236/"+dir_name+"/'>here</a>")
    sg.send(message)