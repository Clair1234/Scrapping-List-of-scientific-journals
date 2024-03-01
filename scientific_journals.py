'''
LIBRARY USED :
    requests  
    BeautifulSoup 
'''


'''
STEP 1 - SCRAPING THE LIST OF BATTLES
'''

import requests as rq
url = 'https://en.wikipedia.org/wiki/List_of_scientific_journals'
response = rq.get(url)

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

def get_dom(url): 
    '''
    Parameters
    ----------
    url : url of web page to get.

    Returns : .content gives you access to the raw bytes of the response payload
    -------
    TYPE
        We have a parsed Document Object Model (DOM)

    '''
    response = rq.get(url)    
    response.raise_for_status()    
    return BeautifulSoup(response.content, 'html.parser')

soup = get_dom(url)

'''
From the inspection of page, the text is stored in div element the with mw-content-text ID
'''

content = soup.select('div#mw-content-text',limit=1)[0]


'''
first nestling is in h2 element this gives the types info
The goal is to get all the types
The last h2 is See also (not relevant to scrapping)
'''

types = content.select('h2')[:-1]
for el in types:
    '''
    prints out with [edit] 
    so we remove the last 6 char
    '''
    #print(el.text[:-6])

def dictify(ul, level=0):
    '''
    Parameters
    ----------
    ul : ul of web page

    Returns : dict with the name of the page with a dict[url] = url of page to get
    -------
    TYPE
        We have a dict

    '''
    result = dict()
    for li in ul.find_all("li", recursive=False):
        text = li.stripped_strings
        key = next(text)
        ul, link = li.find("ul"), li.find("a")
        
        if link :
            link = 'https://en.wikipedia.org/' + (link.get('href'))
        
        r = {'url' : link,
             'level' : level}
        if ul:
            r['children'] = dictify(ul, level=(level+1))
        result[key] = r
    return result

magazines = {}

for type_ in types:
    list_element = type_.find_next_siblings("div", "div-col")[0].ul
    '''
    The last 6 char are [edit] so we can get ride of it
    '''
    magazines[type_.text[:-6]] = dictify(list_element)
    
import json

with open('all_journals.json', 'w') as f:
    json.dump(magazines, f)
    

'''
STEP 2 - SCRAPING INFORMATION FROM THE WIKI PAGE
'''
'''
Test on a specific page - Journal of Materials Chemistry A
url = 'https://en.wikipedia.org/wiki/Journal_of_Materials_Chemistry_A'
'''

url = 'https://en.wikipedia.org/wiki/Journal_of_Materials_Chemistry_A'
dom = get_dom(url)

'''
The information we are searching for is in the 
table with the class 'infobox hproduct'
'''
table = dom.find('table', 'infobox hproduct')

def _get_main_info(table):
    '''
    Parameters
    ----------
    table : bs4.element.Tag

    Returns : dict with the keys : 'Discipline', 'Language', 'History', 'Publisher', 'Frequency'
                and the respective info of the page in it
    -------
    TYPE
        We have a dict

    '''
    dict_ = {}
    for title in ['Discipline', 'Language', 'History', 'Publisher', 'Frequency']:
        main = [el for el in table.tbody.find_all('tr', recursive=False) if title in el.get_text()][0]
        key = main.th.get_text()
        value = main.td.get_text()
        dict_[key]=value
    return dict_

main = _get_main_info(table)

from warnings import warn
    
def parse_journals_page(url):
    '''
    Parameters
    ----------
    url : url of page to get to

    Returns : dict with url
    -------
    TYPE
        We have a dict
    -------
    DESCRIPTION
        main function to parse journals urls from wikipedia

    '''

    try :
        dom = get_dom(url) #dom
    except Exception as e:
        warn(str(e))
        return {}
    
    table = dom.find('table', 'infobox') #info table
    if table is None: #some journals dont have table
        return {}
    
    data = _get_main_info(table)
    data['url'] = url
    return data


'''
STEP 3 - SCRAPING DATA AS A WHOLE
'''

import json
import time

with open('./all_journals.json', 'r') as f:
    fields = json.load(f)
        
def _parse_in_depth(element, name):
    '''
    DESCRIPTION
        attempts to scrape data for every
        element with url attribute - and all the children
        if there are any

    '''
    
    if 'children' in element:
        for k, child in element['children'].items():
            parsed = _parse_in_depth(child, k)
            element['children'][k].update(parsed)
    
    if 'url' in element:
        try:
            element.update(parse_journals_page(element['url']))       
        except Exception as e:
            #raise Exception(name, e)
            warn(str(name))
            warn(str(e))
            
    time.sleep(.1)
    return element

parse_journals_page('https://en.wikipedia.org/wiki/Journal_of_Materials_Chemistry_A')


journals_parsed = {}

for fld_name, type_ in fields.items():
    #print(fld_name)
    journals_parsed[fld_name] = {}
    for cp_name, campaign in type_.items():
        #print(f'    {cp_name}')
        
        parsed = _parse_in_depth(campaign, cp_name)
        if parsed is not None:
            journals_parsed[fld_name][cp_name] = parsed
            
         
'''
Quality control
'''

'''
Define data structure to check that most page not empty
'''

STATISTICS = {
    'journals_checked':0,
    'discipline_null':0,
    'language_null':0,
    'history_null': 0,
    'publisher_null': 0,
    'frequency_null': 0,
}

def qa(mag, name='Unknown'):
    required = (
        'level',
    )
    for el in required:
        assert el in mag and mag[el] is not None, (name, el)

        
    STATISTICS['journals_checked'] +=1
    
    for el in 'Discipline', 'Language', 'History', 'Publisher', 'Frequency':
        if el not in mag or mag[el] is None:
            STATISTICS[f'{el.lower()}_null'] += 1
            
    if 'children' in mag:
         for name, child in mag['children'].items():
                qa(child, name)

for _, type_ in journals_parsed.items():
    for name, mag in type_.items():
        qa(mag, name)

with open('_all_journals_parsed.json', 'w') as f:    
    json.dump(journals_parsed, f)
