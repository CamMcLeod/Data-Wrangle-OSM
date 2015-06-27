"""
Cam Mcleod - June 24th / 2015

- This code audits the OSMFILE

  The function takes a string with street name, city name and postal code as 
  an argument and returns the fixed value

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
from collections import OrderedDict
from collections import Counter
import re
import pprint

OSMFILE = "vancouver_canada.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
postal_code_re = re.compile(r'^(?!.*[DFIOQU])[V][0-9][A-Z] ?[0-9][A-Z][0-9]$')
street_types = defaultdict(int)

expected_street = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
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
            
            
def print_sorted_dict(d):
    ordered_d = OrderedDict(sorted(d.viewitems(), key=lambda x: len(x[1]), reverse=True))
    for k in ordered_d:
        v = ordered_d[k]
        print '{}: {}'.format(k, len(v))
            
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

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")
    
def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    city_names = []
    post_codes = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_abbreviations(street_types, tag.attrib['v'])
                    audit_street_type(street_types, tag.attrib['v'])
                elif is_city_name(tag):
                    audit_city(city_names, tag.attrib['v'])
                elif is_postal_code(tag):
                    audit_postal_code(post_codes, tag.attrib['v'])
    return street_types, city_names, post_codes

def update_name(name, mapping):
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
    
def test():
    st_types, city_names, post_codes = audit(OSMFILE)
    
    #use the following line to see what values may need cleaning in terms of street type
    print_sorted_dict(st_types)
    
    #use this line to see what city names may need to be cleaned
    print Counter(city_names)
    
    #print the changed city names
    for name in city_names:
        if name != "Vancouver" and name != "North Vancouver": 
            better_name = update_city_name(name, city_mapping)
            print name, "=>", better_name     
    
    #print the changed postal codes        
    for code in post_codes:
        fixed_code = update_post_code(code)
        print code, "=>", fixed_code
    
    #print the changed street names      
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, street_mapping)
            print name, "=>", better_name     
            
if __name__ == '__main__':
    test()