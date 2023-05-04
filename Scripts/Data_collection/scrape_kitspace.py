import time, datetime, os
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_license(gh):
    license_names = ['MIT', 'CERN', 'Creative Commons', 'Apache', 'Zlib', 'GPL', 'GNU', 'TAPR', 'BSD']
    license_list = []
    results = search_repo(gh, 'licen')
    for res in results[0:5]:
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
                if soup(text=lambda t: name + ' ' in t.text[0:min(200,len(t.text))]):
                    license['name'] = name
                    license['link'] = file_link
                    license_list.append(license)
                    license_names.remove(name)
    if not license_list:
        dict={"name":'License not found', "link":''}
        license_list.append(dict)
    return license_list

def get_meta(source, path, dir, ext, license):
    board = {}
    if ext == ('.kicad_pro'):
        try:
            with open(f"{path}\\metadata.json") as f:
                board = json.load(f)
                board['supplementary files'] = [dir + '/raw' + ext]
                meta = json.dumps(board, indent=2)
            with open(f"{path}\\metadata.json","w", encoding='utf-8') as f:
                f.write(meta)
        except Exception as e:
            print(f"Error for file {path}\\metadata.json from {source}:\n{e}")
    else:
        board['org'] = URL
        board['source'] = source
        board['author'] = ''
        board['retrieved at'] = str(datetime.datetime.now())
        board['raw'] = dir + '/raw' + ext
        board['cleaned'] = dir + '/processed' + ext
        board['json'] = dir + '/final.json'
        board['supplementary files'] = ''
        board['licenses'] = license
        board['layers'] = ''
        board['CAD version'] = ''

        with open(f"{path}\\metadata.json","w", encoding='utf-8') as f:
            meta = json.dumps(board, indent=2)
            f.write(meta)

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

def write_files(source, gh, results, term, count, license):
    for res in results:            
        f = res.get_attribute('href').split('blob')[1]
        if term.startswith('.') and not f.endswith(term):
            continue
        file_link = RAW + gh.split('.com')[1].split('/find')[0] + f
        data = requests.get(file_link)
        # Write data to folder
        if data.ok:
            ext = file_link[file_link.rindex('.') :]
            filename = file_link[file_link.rindex('/') + 1: file_link.rindex('.')]
            dir = "kitspace_" + filename
            path = PATH + '\\PCBs\\'+ dir
            if not os.path.exists(path) and ext == '.kicad_pcb':
                os.makedirs(path)
            try:
                with open(f"{path}\\raw{ext}","w", encoding='utf-8') as f:
                    (f.write(bytes.decode(data.content)))
                    f.flush()
                    count += 1
                get_meta(source, path, dir, ext, license)
            except Exception as e:
                    print(f"Error for file {filename}\nfrom {file_link}:\n{e}")
    return count

### MAIN
# Configure Web Driver
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options = options, service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com")
driver.implicitly_wait(0.1)
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
PATH = os.path.abspath(__file__ + "/../../../")
seen_repos = set()
repo_count = 0
file_count = i = 0
start = time.time()

for card in cards:
    # if i > 5:      # Temp break to test functionality
    #     break       #
    # i+=1            #
    source, gh = get_repo(card)
    if gh != False:
        if gh in seen_repos:
            continue
        seen_repos.add(gh)
        repo_count += 1
        license = get_license(gh)
        for term in search_terms:
            results = search_repo(gh, term)
            file_count = write_files(source, gh, results, term, file_count, license)
            
print(f'Repos found: {repo_count}')
print(f'Files found: {file_count}')
print(f'Time: {round((time.time()-start)/60,2)} mins')