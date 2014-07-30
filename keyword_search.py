'''
This module is to search keywords in move subtitle.

Define Keyword: keyword is name or term relationship.
ex: Jack, Dad

Intput: -> 1 name_file 2. realationship_file 2. subtitle_file
Output: keyword to time in subtitle: keyword_time_csv_file
'''

import sys
import re

from module import csv_io

MAX_KEYWORDS_IN_ONE_INTERVAL = 3
OUTPUT_ROOT_PATH = 'output/'

def keyword_search(name_file, relationship_file, subtitle_file):

    name_list =  csv_io.read_csv(name_file)
    relation_list =  csv_io.read_csv(relationship_file)
    subtitle = read_subtitle_file(subtitle_file)

    name_patterns = {}
    for name in name_list:
        name_patterns[name] = '\\b' + name.lower() + '\\b' 
    
    relation_patterns = {}
    for relation in relation_list:
        relation_patterns[relation] = '\\b' + relation.lower() + '\\b' 
    
    time_to_keyword = []
    subtitle_interval = []
    keyword_number = 0
    for line in subtitle:
        if line.strip():
            if len(subtitle_interval) == 1:
                subtitle_time = line[:-2]
            for name in name_patterns:
                if keyword_number < MAX_KEYWORDS_IN_ONE_INTERVAL and re.search(name_patterns[name], line.lower()):
                   time_to_keyword.append([subtitle_time, name])
                   keyword_number += 1

            for relation in relation_patterns:
                if keyword_number < MAX_KEYWORDS_IN_ONE_INTERVAL and re.search(relation_patterns[relation], line.lower()):
                   time_to_keyword.append([subtitle_time, relation])
                   keyword_number += 1

            subtitle_interval.append(line)
        else:
            if keyword_number == MAX_KEYWORDS_IN_ONE_INTERVAL:
                for i in range(MAX_KEYWORDS_IN_ONE_INTERVAL):
                    time_to_keyword.pop()
            subtitle_interval = []
            keyword_number = 0
    
    csv_io.write_csv(OUTPUT_ROOT_PATH + 'keywordSearch.csv',time_to_keyword)


def read_subtitle_file(subtitle_file):

    with open(subtitle_file, 'r') as subtitle:
        subtitle = subtitle.readlines()
    return subtitle


if __name__=='__main__':
    keyword_search(sys.argv[1], sys.argv[2], sys.argv[3])
