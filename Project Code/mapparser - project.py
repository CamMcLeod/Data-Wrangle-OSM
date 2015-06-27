#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Use iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

"""
import xml.etree.cElementTree as ET
import pprint
import collections

def count_tags(filename):
    # YOUR CODE HERE
    all_tags = collections.Counter()
    for event, element in ET.iterparse(filename, events=("start","end")):
        if event == "start":
            all_tags[element.tag] += 1          
    return all_tags

def test():

    tags = count_tags('vancouver_canada.osm')
    pprint.pprint(tags)    

if __name__ == "__main__":
    test()