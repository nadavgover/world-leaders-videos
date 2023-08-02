from pytube import YouTube, Search
import os

import video_creator as vc


class Youtube(object):
    def __init__(self):
        self.downloads_dir = os.path.join(os.getcwd(), "downloads")
        self.video_creator = vc.VideoCreator()
        self.youtube_url = "https://www.youtube.com/watch?v={}"

    def get_next_file_name(self, videos_dir):
        filenames = next(os.walk(videos_dir), (None, None, []))[2]  # [] if no file
        file_numbers = list(map(lambda filename: int(filename.split(".")[0]), filenames))
        return str(max(file_numbers) + 1) if file_numbers else "1"

    def download_video_of_leader(self, video_url, leader_name, trims_list, filename=None, file_extension="mp4"):
        leader_dir = os.path.join(self.downloads_dir, leader_name)
        leader_videos_dir = os.path.join(leader_dir, "videos")
        if filename is None:
            filename = self.get_next_file_name(leader_videos_dir)
        for dir_name in [leader_dir, leader_videos_dir]:
            try:
                os.mkdir(dir_name)
            except FileExistsError:
                continue

        yt_streams = YouTube(video_url).streams
        yt_streams \
            .filter(file_extension=file_extension, progressive=True) \
            .order_by('resolution') \
            .desc() \
            .first() \
            .download(filename=f"{filename}.mp4", output_path=leader_videos_dir)

        if trims_list:
            self.make_all_trims(video_file=os.path.join(leader_videos_dir, f"{filename}.mp4"), trims_list=trims_list)

        print(f"Finished Downloading {video_url}")

    def download_all_videos_of_leader(self, video_urls, leader_name, trims_list, filename=None, file_extension="mp4"):
        for video_url in video_urls:
            self.download_video_of_leader(video_url, leader_name, trims_list, filename, file_extension)

    def make_all_trims(self, video_file, trims_list):
        videos_dir = "/".join(video_file.split("/")[:-1])
        for trim_dict in trims_list:
            video_number = self.get_next_file_name(videos_dir)
            self.video_creator.trim_video(trim_dict, video_file, os.path.join(videos_dir, video_number + ".mp4"))
        os.remove(video_file)

    def download_audio(self, video_id, leader_name):
        print(f"Started downloading audio. leader name: {leader_name}, video id: {video_id}")
        leader_dir = os.path.join(self.downloads_dir, leader_name)
        leader_audios_dir = os.path.join(leader_dir, "audios")
        for dir_name in [leader_dir, leader_audios_dir]:
            try:
                os.mkdir(dir_name)
            except FileExistsError:
                continue
        if not self.does_file_already_exist(leader_audios_dir, video_id):
            video_url = self.youtube_url.format(video_id)
            try:
                yt_streams = YouTube(video_url).streams
                yt_streams \
                    .filter(only_audio=True) \
                    .first() \
                    .download(filename_prefix=video_id, output_path=leader_audios_dir)
                print(f"Finished downloading audio. leader name: {leader_name}, video id: {video_id}")
            except Exception as e:
                print(f"Unable to download audio, leader name: {leader_name}, video id: {video_id}")
                print(e)

    def download_video(self, video_id, leader_name, file_extension="mp4"):
        print(f"Started downloading video. leader name: {leader_name}, video id: {video_id}")
        leader_dir = os.path.join(self.downloads_dir, leader_name)
        leader_videos_dir = os.path.join(leader_dir, "videos")
        for dir_name in [leader_dir, leader_videos_dir]:
            try:
                os.mkdir(dir_name)
            except FileExistsError:
                continue
        if not self.does_file_already_exist(leader_videos_dir, video_id):
            video_url = self.youtube_url.format(video_id)
            try:
                yt_streams = YouTube(video_url).streams
                yt_streams \
                    .filter(file_extension=file_extension, progressive=True) \
                    .order_by('resolution') \
                    .desc() \
                    .first() \
                    .download(filename_prefix=video_id, output_path=leader_videos_dir)
                print(f"Finished downloading video. leader name: {leader_name}, video id: {video_id}")
            except Exception as e:
                print(f"Unable to download video, leader name: {leader_name}, video id: {video_id}")
                print(e)

    def does_file_already_exist(self, directory, video_id):
        filenames = next(os.walk(directory), (None, None, []))[2]  # [] if no file
        filenames = list(filter(lambda name: name.startswith(video_id), filenames))
        return bool(filenames)


if __name__ == '__main__':
    yt = Youtube()
    # yt.download_audio("kOvd4h70PXw", "trump")
    yt.download_video("kOvd4h70PXw", "trump")
