import json
import pprint
import random

text=["hack", "pennapps", "cloud", "service", "node.js", "html5", "continuous integration","I'd like to inteject, that thing you've been referring to as linux is actually GNU linux, or as I've taken to calling it, GNU + Linux","webscale","scalability","API","cross-platform","Rubber-Duck Debugging","dev-ops","github", "software", "programming", "is", "the", "cool", "doge", "bitcoin", "so", "very"]

def get_text_of_width(w,h):
    div_text=""
    for i in range(w*h/5000):
        div_text+=random.choice(text)+" "
    return div_text

def create_div(rect, offset=(0,0)):
    div_string="<div>"
    if (rect['type']=='text'):
        div_string+=get_text_of_width(rect['w'],rect['h'])
    elif (rect['type']=='image'):
        div_string+="<img alt='cats are awesome' src='http://placekitten.com/g/"+str(rect['w'])+"/"+str(rect['h'])+"' width="+str(rect['w'])+" height="+str(rect['h'])+" >"

    if (rect['glyph']!=None):
        div_string+="<a href='http://104.131.20.236/page_"+str(rect['glyph'])+"' alt='woah, a hyperlink'>go to page "+str(rect['glyph'])+"</a>"

    for child in rect['children']:
        div_string+=create_div(child)
    return div_string+"</div>"

def parse_header(header):
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
    			{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'type': '', 'glyph': None, 'children': [
    				{'x': 0, 'y': 0, 'w': 1000, 'h': 40, 'type': 'text', 'glyph': 1, 'children': []}, 
    				{'x': 400, 'y': 200, 'w': 600, 'h': 400, 'type': '', 'glyph': None, 'children': [
        				{'x': 0, 'y': 0, 'w': 300, 'h': 400, 'type': 'text', 'glyph': None, 'children': []}, 
        				{'x': 300, 'y': 0, 'w': 300, 'h': 400, 'type': 'image', 'glyph': None, 'children': []}
        			]}
        		]}, 
        		{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'type': '', 'glyph': '', 'children': [
					{'x': 0, 'y': 0, 'w': 1000, 'h': 100, 'type': 'text', 'glyph': 0, 'children': []}
        		]}]

    pageNum = 0
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
            dust_filename="public/templates/index.dust"
            js_filename="controllers/index.js"
            js_path="/"
            render_path="index"
        else :
            dust_filename="public/templates/page_"+str(pageNum)+".dust"
            js_filename="controllers/page_"+str(pageNum)+".js"
            js_path="page_"+str(pageNum)
            render_path="page_"+str(pageNum)

        f_dust = open(dust_filename,'w')
        f_dust.write("{>'layouts/master' /}")
        f_dust.write("{<body}")
        f_dust.write(html_page)
        f_dust.write("{/body}")

        f_js = open(js_filename,'w')
        j_s.write("'use strict;'")
        j_s.write("module.exports = function (app) { app.get('" + js_path + "', function(req,res){ res.render('" + render_path +"');});};")

        pageNum+=1

