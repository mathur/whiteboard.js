import json
import pprint

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

    for page in pages:
        page['children'] = sorted(page['children'], key=lambda k: k['y'])
        children = page['children']
        if (len(children) == 1):
            body = [children[0]]
        elif (len(children) == 2):
            header = [children[0]]
            body = [children[1]]
        else:
            header = [children[0]]
            body = children[1:len(children) - 1]
            footer = children[len(children) - 1]