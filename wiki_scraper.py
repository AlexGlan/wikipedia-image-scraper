import os
import re
import requests
from bs4 import BeautifulSoup

SAVE_FOLDER = "wiki_images"

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}

def main():
    # Create folder to save files
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(os.path.join(".", SAVE_FOLDER))

    user_url = input("Enter your Wikipedia page: ").strip()

    if not is_valid_wikipedia_link(user_url):
        print("Incorrect Wikipedia link, please try again")
        return

    print("Start searching...", flush=True)
    image_urls = extract_image_urls(user_url)

    # Quit if no images are found
    if len(image_urls) == 0:
        print("No images found")
        return

    print("Start downloading...", flush=True)
    download_images(image_urls)

    print("Done")

def is_valid_wikipedia_link(user_url):
    """Wikipedia URL validation"""
    pattern = r"https://en\.wikipedia\.org/wiki/.+"
    return bool(re.match(pattern, user_url))

def extract_file_extension(img):
    """Extract supported file extensions"""
    file_extension = re.findall(r"\.jpg$|\.JPG$|\.png$|\.PNG$", img)[0]
    if img.endswith(".svg.png"):
        file_extension = ".svg"
    elif img.endswith(".webp.png"):
        file_extension = ".webp"
    elif img.endswith("tiff.jpg"):
        file_extension = ".tiff"
    elif img.endswith(".tif.jpg"):
        file_extension = ".tif"

    return file_extension

def extract_image_urls(user_url):
    """Parse, extract and store image URLs"""
    try:
        with requests.Session() as session:
            response = session.get(user_url, headers=usr_agent)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            image_tags = soup.find_all("img")
            image_urls = []

            for i in image_tags:
                img = i["src"]

                if re.search(r"\.jpg$|\.JPG$|\.png$|\.PNG$", img):
                    if "/commons/" not in img:
                        continue
                    
                    file_extension = extract_file_extension(img)
                    
                    # Modify URL
                    src = img.split(file_extension)[0].replace("thumb/", "").strip("//")
                    image_src = f"https://{src}{file_extension}"

                    image_urls.append(image_src)

            return image_urls
    except requests.exceptions.RequestException as error:
        print(f"Error occurred while downloading images: {error}", flush=True)

def download_images(image_urls):
    """Make HTTPS requests for images and save them"""
    try:
        with requests.Session() as session:  
            for url in image_urls:
                response = session.get(url, headers=usr_agent)
                response.raise_for_status()
                filename = os.path.join(SAVE_FOLDER, url.split("/")[-1])

                with open(filename, "wb") as file:
                    file.write(response.content)
                    print(f"Save {filename}", flush=True)
    except requests.exceptions.RequestException as error:
        print(f"Error occurred while downloading images: {error}", flush=True)

if __name__ == "__main__":
    main()