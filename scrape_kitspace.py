import time, datetime
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_license(gh):
    license_names = ['MIT', 'CERN', 'CC', 'Creative Commons', 'Apache', 'Zlib', 'GPL', 'GNU']
    license_list = []
    results = search_repo(gh, 'licen')
    for res in results:
        license = {}
        f = res.get_attribute('href').split('blob')[1]
        file_link = RAW + gh.split('.com')[1].split('/find')[0] + f
        data = requests.get(file_link)
        for name in license_names:
            if file_link.lower().__contains__(name.lower()):
                license['name'] = name
                license['link'] = file_link
                license_list.append(license)
                license_names.remove(name)
            elif file_link.endswith(('.txt', '.md')) or file_link.lower().__contains__('licen'):
                soup = BeautifulSoup(data.content, features='lxml')
                if soup(text=lambda t: name + ' ' in t.text):
                    license['name'] = name
                    license['link'] = file_link
                    license_list.append(license)
                    license_names.remove(name)
    if not license_list:
        dict={"name":'', "link":''}
        license_list.append(dict)
    return license_list

def get_version(source):
    page = requests.get(source + '/tags')
    s = BeautifulSoup(page.content, features='lxml')   
    if s.find(class_="Box-body") is not None:
        version = s.find(class_="Box-body").find(class_='Link--primary')
        if version is not None:
            return version.get_text()
    return ''

def get_meta(metadata, source, filename, version, license):
    board = {}
    board['source'] = source
    board['name'] = filename.split('.kicad')[0]
    board['version'] = version
    board['license'] = license
    board['made_in'] = ''
    board['authors'] = ''
    board['retrieved_at'] = str(datetime.datetime.now())
    board['layers'] = ''
    board['comments'] = ''
    metadata.append(board)
    return metadata

def get_repo(card):
    # Get project github URL and check
    project_URL = card.find("a")['href']
    proj = requests.get(URL + project_URL)
    soup = BeautifulSoup(proj.content, features='lxml')
    source = soup.find(class_="subtitleText").find('a')['href']
    if "github" not in source:
        print("Bad URL: " + source)
        return False, False
    # Go to repo search page
    r = requests.get(source)
    s = BeautifulSoup(r.content, features='lxml')   
    t = s.find(id="branch-select-menu")
    b = t.find(attrs={'class':'css-truncate-target','data-menu-button':""}).get_text()
    gh = source + "/find/" + b
    return source, gh

def search_repo(URL, search_term):
    driver.get(URL)
    sbox = driver.find_element(By.ID,"tree-finder-field")
    sbox.send_keys(search_term)
    time.sleep(1)
    results = driver.find_elements(By.CLASS_NAME, "tree-browser-result")
    return results

def write_files(source, gh, results, term, count, version, license, write_kicad=True):
    if not write_kicad:
        print("WARNING: write_kicad is set to False")
    for res in results:            
        f = res.get_attribute('href').split('blob')[1]
        if term.startswith('.') and not f.endswith(term):
            continue
        file_link = RAW + gh.split('.com')[1].split('/find')[0] + f
        data = requests.get(file_link)
        # Write data to folder
        if data.ok:
            filename = file_link[file_link.rindex('/') + 1:]
            count += 1
            if write_kicad == True:
                with open(f"kicad files/{filename}","w", encoding='utf-8') as f:
                    try:
                        (f.write(bytes.decode(data.content)))
                        f.flush()
                    except Exception as e:
                        print(f"Error for file {filename}\nfrom {file_link}:\n{e}")
                        continue
            get_meta(metadata, source, filename, version, license)
    return count

### MAIN
# Configure Web Driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com")
driver.implicitly_wait(0.5)
headers = {'User-Agent': 'Mozilla/5.0'}
# Scraper Supplementary Info
URL = "https://kitspace.org"
RAW = "https://raw.githubusercontent.com"
search_terms = ['.kicad_pcb', '.kicad_pro']
# Get project cards from Kitspace
page = requests.get(URL)
soup = BeautifulSoup(page.content, features='lxml')
cards = soup.find_all(class_="boardCard")
# Global variables
seen_repos = set()
repo_count = 0
file_count = i = 0
metadata = []
start = time.time()

for card in cards:
    # if i > 15:      # Temp break to test functionality
    #     break       #
    # i+=1            #
    source, gh = get_repo(card)
    if gh != False:
        if gh in seen_repos:
            continue
        seen_repos.add(gh)
        repo_count += 1
        version = get_version(source)
        license = get_license(gh)
        for term in search_terms:
            results = search_repo(gh, term)
            file_count = write_files(source, gh, results, term, file_count, version, license, False) # write_kicad = False

with open("metadata.json","w", encoding='utf-8') as f:
    data = json.dumps(metadata, indent=2)
    f.write(data)
            
print(f'Repos found: {repo_count}')
print(f'Files found: {file_count}')
print(f'Time: {round((time.time()-start)/60,2)} mins')