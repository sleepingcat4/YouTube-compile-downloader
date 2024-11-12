import os
import csv
import requests
import time
from pytubefix import YouTube
from pytubefix.cli import on_progress

proxies = {
    'https': 'proxy_url',
}

def download_video(url, save_folder, csv_writer, index):
    url = url.strip()
    try:
        session = requests.Session()
        session.proxies.update(proxies)
        
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Downloading video: {yt.title}")

        metadata = {
            'title': yt.title,
            'duration': yt.length,
            'author': yt.author,
            'view_count': yt.views,
            'likes': yt.likes,
        }

        ys = yt.streams.get_highest_resolution()
        video_file_name = f"video_file{index}.mp4"
        ys.download(output_path=save_folder, filename=video_file_name)
        print(f"Downloaded video: {yt.title} to {save_folder} as {video_file_name}")

        csv_writer.writerow([metadata['title'], video_file_name, metadata['duration'], metadata['author'], metadata['view_count'], metadata['likes']])

        return video_file_name
    except Exception as e:
        print(f"Failed to download video from {url}. Error: {e}")
        return None

def download_videos_from_txt():
    file_path = input("Enter the name of the .txt file containing video URLs: ")
    save_folder = input("Enter the folder name where videos will be saved: ")

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    failed_urls = []
    start_time = time.time()

    csv_file_name = f"video_mapping_{os.path.basename(file_path).replace('.txt', '.csv')}"
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Original Title', 'Video File Name', 'Duration (s)', 'Author', 'View Count', 'Likes'])

        with open(file_path, 'r') as file:
            urls = file.readlines()

        for index, url in enumerate(urls, start=1):
            video_file_name = download_video(url, save_folder, csv_writer, index)
            if not video_file_name:
                failed_urls.append(url)

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Total time taken: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")

    if failed_urls:
        failed_file = f"failed_{os.path.basename(file_path)}"
        with open(failed_file, 'w') as f:
            for url in failed_urls:
                f.write(url)
        print(f"Failed URLs have been saved to {failed_file}")

    print(f"Video mapping has been saved to {csv_file_name}")

download_videos_from_txt()
