import json
import pprint
import random

text=["hack", "pennapps", "peter", "joe", "node.js", "rohan", "ryan"]

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
        div_string+="<img alt='cats are awesome' src=http://placekitten.com/"+str(rect['w'])+"/"+str(rect['h'])+" width="+str(rect['w'])+" height="+str(rect['h'])+"/>"

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
    			{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'type': '', 'glyph': '', 'children': [
    				{'x': 0, 'y': 0, 'w': 1000, 'h': 40, 'type': 'text', 'glyph': '1', 'children': []}, 
    				{'x': 400, 'y': 200, 'w': 200, 'h': 400, 'type': '', 'glyph': '', 'children': [
        				{'x': 0, 'y': 0, 'w': 100, 'h': 400, 'type': 'text', 'glyph': '', 'children': []}, 
        				{'x': 100, 'y': 0, 'w': 100, 'h': 400, 'type': 'image', 'glyph': '', 'children': []}
        			]}
        		]}, 
        		{'x': 0, 'y': 0, 'w': 1000, 'h': 900, 'type': '', 'glyph': '', 'children': [
					{'x': 0, 'y': 0, 'w': 1000, 'h': 100, 'type': 'text', 'glyph': '0', 'children': []}
        		]}]

    pp = pprint.PrettyPrinter(indent=3)

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
            filename="index.html"
        else :
            filename="page_"+str(pageNum)+".html"

        pp.pprint(html_page);
        f = open(filename,'w');
        f.write(html_page);
        pageNum+=1

