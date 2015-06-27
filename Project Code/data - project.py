#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict

"""
This code wrangles the data and transform the shape of the data
into the model decided in the class exercise. The output is a list of 
dictionaries in the JSON format

The function 'shape_element' transforms the data shape into a more MongoDB 
friendly format (JSON).

A function will parse the map file, and call the function with the element
as an argument. 
The data will be saved in a file, so mongoimport can be used later on to import
 the shaped data into MongoDB. 

Procedures from the audit-project.py file are added to audit the street name,
postal code, and city name data.

"""

"""
Below the mapping and regular expressions for the data audit are included
"""
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
postal_code_re = re.compile(r'^(?!.*[DFIOQU])[V][0-9][A-Z] ?[0-9][A-Z][0-9]$')
street_types = defaultdict(int)

expected_street = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# the following variables are the mappings for streets and city
street_mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "W.": "West",
            "W": "West",
            "E.": "West",
            "E": "West",
            "N.": "North",
            "N": "North",
            "S.": "South",
            "S": "South",
            }
            
city_mapping = { "vancouver" : "Vancouver",
                 "Vancouver, BC" : "Vancouver",
                 "Vancovuer" : "Vancouver",
                 "North Vancouver City" : "North Vancouver",
                 "north vancouver" : "North Vancouver"}

# the following variables are used to pass over data which may not be 
#suitable for MongoDB

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


"""
The 'shape_element' section is below, which reshapes the data and calls audit procedures
"""

def shape_element(element):
    node = {}
    street_types = defaultdict(set)
    city_names = []
    post_codes = []
    
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        
        node["id"] = element.get('id')
        node["type"] = element.tag
        node["visible"] = element.get('visible')
        
        if element.get('lat') != None:
            if element.get('lon') != None:
                node["pos"] = [float(element.get('lat')) , float(element.get('lon'))]
            else:
                node["pos"] = [float(element.get('lat')) , None]
        elif element.get('lon') != None:
            node["pos"] = [None , float(element.get('lon'))]
        
        node["created"] = {
                        CREATED[0] : element.get('version'),
                        CREATED[1] : element.get('changeset'),
                        CREATED[2] : element.get('timestamp'),
                        CREATED[3] : element.get('user'),
                        CREATED[4] : element.get('uid')}

        address = {}
        for tag in element.iter('tag'):
            if problemchars.search(tag.get("k")):
                continue
            if "addr:" in tag.get("k"):
                if ":" in tag.get("k")[5:]:
                    continue
                else:
                    if is_street_name(tag.get("k")):
                        audit_street_abbreviations(street_types, tag.get("v"))
                        audit_street_type(street_types, tag.get("v"))
                        if tag.get("v") in street_mapping:
                            address[tag.get("k")[5:]] = update_street_name(tag.get("v"), street_mapping)
                        else:
                            address[tag.get("k")[5:]] = tag.get("v")
                            
                    elif is_postal_code(tag.get("k")):
                        audit_postal_code(post_codes, tag.get("v"))
                        if tag.get("v") in post_codes:
                            if update_post_code(tag.get("v")) != None:
                                address[tag.get("k")[5:]] = update_post_code(tag.get("v"))
                        else:
                            address[tag.get("k")[5:]] = tag.get("v")
                            
                    elif is_city_name(tag.get("k")):
                        audit_city(city_names, tag.get("v"))
                        address[tag.get("k")[5:]] = update_city_name(tag.get("v"), city_mapping)
                            
                        
                    else:
                       address[tag.get("k")[5:]] = tag.get("v")
            else:
                node[tag.get("k")] = tag.get("v")
                
        if address:
            node["address"] = address
        
        node_refs = []
        for new_node in element.iter('nd'):
            node_refs.append(new_node.get("ref"))
        if node_refs:
            node["node_refs"] = node_refs
        
        return node
    else:
        return None

"""
below we have the audit procedures which are called to fix incorrect values in the database
"""

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_street:
            street_types[street_type].add(street_name)

def audit_city(city_names, name):
    city_names.append(name)

def audit_postal_code(post_codes, code):
    m = postal_code_re.search(code)
    if m:
        pass
    else:
        post_codes.append(code)
        

def audit_street_abbreviations(street_types, street_name):
    name = street_name.split()
    for word in name:
        if word in street_mapping:
            m = street_type_re.search(street_name)
            if m:
                street_type = m.group()
                street_types[street_type].add(street_name)
            break
        
"""
below we have the update procedures which update incorrect values in the database
"""
        
def update_street_name(name, mapping):
    name = name.split()
    
    #remove the unneccessary "Vancouver" string from some road names
    if name[-1] in "Vancouver":
        name = name[:-1]
    
    #apply changes to orientation abbreviations "W" for "West"
    if name[0] in mapping:
        if name[0] == ["St", "St."]:
            pass
        else:
            name[0] = mapping[name[0]]
    
    #change the street type to the mapped type 
    if name[-1] in mapping:
        name[-1] = mapping[name[-1]]
    name = " ".join(name)
    return name

def update_city_name(name, mapping):
    if name != "Vancouver" and name != "North Vancouver": 
        name = mapping[name]
    return name
    
def update_post_code(name):
    name = name.upper()
    name = name.split()
    if len(name) != 2:
        #remove redundant "BC" in postal code
        if name[0] == "BC":
            name = name[1:]
        #fix codes without spaces
        if len(name) == 1:
            if len(name[0]) == 6:
                name = name[0][:3] , name[0][3:]
    #parse first string length down to 3 digits
    if len(name[0]) > 3:
        name[0] = name[0][:3]
        
    if len(name) > 1:
        #parse second string length down to 3 digits
        if len(name[1]) > 3:
           name[1] = name[1][:3]
        #change "O" occurences mistyped in second string to "0"
        if name[1][0] == "O":
            name[1] = "".join(["0", name[1][1:3]])
    
    if len(name) != 2:
        name = None
    elif len(name[0]) != 3:
        name = None
    else:
        name = " ".join(name)
    return name
    
""" the procedures below check the element is the correct type"""

def is_street_name(elem):
    return (elem == "addr:street")

def is_city_name(elem):
    return (elem == "addr:city")
    
def is_postal_code(elem):
    return (elem == "addr:postcode")
    
""" this procedure reads in the .OSM data and writes out the .JSON data """

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significanetttly larger.
    data = process_map('vancouver_canada.osm', pretty=False)
    
if __name__ == "__main__":
    test()