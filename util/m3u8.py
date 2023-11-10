# 4.08.2023 -> 15.09.2023

# Import
import os, re, glob, time, requests, subprocess, sys, shutil, ffmpeg
from tqdm.rich import tqdm
from rich import print as rprint
from functools import partial
from requests.models import Response
from multiprocessing.dummy import Pool
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# Disable warning
import warnings
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


def get_fake_headers():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10)
    user_agent = user_agent_rotator.get_random_user_agent()
    return {"User-Agent" : user_agent}

def get_custom_header():
    return  {
       'authority': 'www.youporn.com',
        'accept': '*/*',
        'accept-language': 'it-IT,it;q=0.9',
        'referer': 'https://www.youporn.com/watch/15429442/brazzers-busty-stepmom-lexi-luna-fucks-stepson/',
        'User-Agent': get_fake_headers()['User-Agent']
    }

def download_ts_file(ts_url: str, store_dir: str):
    ts_name = ts_url.split('/')[-1].split("?")[0]
    ts_dir = store_dir + "/" + ts_name
    if(not os.path.isfile(ts_dir)):
        ts_res = requests.get(ts_url, headers=get_custom_header())
        time.sleep(0.5)
        if isinstance(ts_res, Response) and ts_res.status_code == 200:
            with open(ts_dir, 'wb+') as f:
                f.write(ts_res.content)
        else:
            print(f"Failed to download streaming file: {ts_name}.")

def download(m3u8_link, merged_mp4):
    m3u8_http_base = m3u8_link.rstrip(m3u8_link.split("/")[-1])
    m3u8_content = requests.get(m3u8_link, headers=get_custom_header()).text

    # Print the m3u8 content
    print("M3U8 Content:")
    print(m3u8_content)
    
    m3u8 = m3u8_content.split('\n')
    ts_url_list = []
    ts_names = []
    for i_str in range(len(m3u8)):
        line_str = m3u8[i_str]
        if '.ts' in line_str:
            ts_url = m3u8[i_str]
            ts_names.append(ts_url.split('/')[-1])
            if not ts_url.startswith("http"):
                ts_url = m3u8_http_base + ts_url
            ts_url_list.append(ts_url)
    if(len(ts_url_list) != 0):
        os.makedirs("temp_ts", exist_ok=True)
        pool = Pool(15)
        gen = pool.imap(partial(download_ts_file, store_dir="temp_ts"), ts_url_list)
        for i in range(len(ts_url_list)):
            _ = ts_url_list[i]
            print(f"Downloaded: {_}")  # Print the name of the .ts file after it's downloaded
        pool.close()
        pool.join()
        time.sleep(1)

        # After downloading the .ts files
        downloaded_ts = sorted(glob.glob(os.path.join("temp_ts", "*.ts")), key=lambda x:float(re.findall("(\\d+)",x)[0]))
        files_str = "concat:"
        # Before calling ffmpeg
        for ts_filename in downloaded_ts:
            files_str += os.path.join(ts_filename)+'|'
        files_str.rstrip('|')

        try:
            ffmpeg.input(files_str).output(merged_mp4, c='copy', loglevel="quiet").run()
        except ffmpeg.Error as e:
            print(e.stderr, file=sys.stderr)
            sys.exit(1)
        rprint("[red]END")
        shutil.rmtree("temp_ts")
    else:
        print("No file to download")
