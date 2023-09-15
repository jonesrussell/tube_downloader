# 21.08.2023 -> 15.09.2023

# Import
import requests, sys
from bs4 import BeautifulSoup
from util.m3u8 import download
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from rich.console import Console
from rich.prompt import Prompt

# Variable
console = Console()
msg = Prompt()

def get_fake_headers():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10)
    user_agent = user_agent_rotator.get_random_user_agent()
    return {"User-Agent" : user_agent}

def main(url):
    
    title = url.split("/")[-2].replace("_", " ").replace("-", " ")
    console.log(f"[blue]FIND: [purple]{title}")

    r = requests.get(url)
    console.log(f"[blue]RESPONSE SITE: [red]{r.status_code}")

    if r.ok:
        soup = BeautifulSoup(r.text, "lxml")

        m3u8_url_master = ""
        for script in soup.find_all("script"):
            if "hls" in str(script):
                
                json_hsl = str(script).split("mainRoll")[1].split("features")[0].replace("},", "}").replace(": {", "{")
                m3u8_url_master = json_hsl.split("videoUrl")[1].split("remote")[0].replace('":"', "").replace('","', "").replace("\/", "/")

        headers = {
            'authority': 'www.youporn.com',
            'accept': '*/*',
            'accept-language': 'it-IT,it;q=0.9',
            'dnt': '1',
            'referer': 'https://www.youporn.com/watch/15429442/brazzers-busty-stepmom-lexi-luna-fucks-stepson/',
            'user-agent': get_fake_headers()['User-Agent']
        }

        response = requests.get(m3u8_url_master, headers=headers)
        console.log(f"[blue]RESPONSE API: [red]{response.status_code}")

        if response.ok:
            master = response.json()[0]['videoUrl']
            m3u8_http_base = master.rstrip(master.split("/")[-1])
            
            console.log("[blue]GET CONTENT MASTER")
            m3u8_content = requests.get(master, headers=headers).text
            m3u8 = m3u8_content.split('\n')
            ts_names = []

            for i_str in range(len(m3u8)):
                line_str = m3u8[i_str]
                if line_str.startswith("#EXT-X"):
                    ts_url = m3u8[i_str+1]
                    ts_names.append([ts_url.split('/')[0].split("-")[1].replace("p", ""), ts_url.split('/')[0]])
            
            console.log(f"[blue]FIND MASTER BASE: [purple]{m3u8_http_base}")
            download(m3u8_http_base+ts_names[0][1], title+".mp4")

        else:
            console.log("[red]ERROR API")
            sys.exit(0)

    else:
        console.log("[red]ERROR SITE")
        sys.exit(0)

url = msg.ask("[blue]INSERT URL VIDEO")
if("www.youporn.com" in str(url)):
    main(url)
else:
    console.log("[red]ERROR URL")
