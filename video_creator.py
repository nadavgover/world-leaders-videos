import db
import random
import os
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from datetime import datetime

import speech_to_text
import youtube
from enums import Video, VideoTimes


class VideoCreator(object):
    def __init__(self, text="", leader_name=""):
        self.db = db.DB()
        self.leader_dataset = self.db.load_dataset_specific_leader(leader_name)
        self.text = text
        self.leader_name = leader_name
        self.chars_dont_care = ["?", "!", ",", ".", ":", ";"]
        self.downloaded_videos_dir = os.path.join(os.getcwd(), "downloads", leader_name, "videos")
        self.created_videos_dir = os.path.join(os.getcwd(), "created", leader_name)
        self.tmp_created_file = os.path.join(self.created_videos_dir, "tmp_files_to_concat.txt")

        try:
            os.mkdir(self.created_videos_dir)
        except FileExistsError:
            pass

    def get_full_matches(self, word, dataset=None):
        if dataset:
            return dataset.get(word)
        return self.leader_dataset.get(word)

    def get_contained_matches(self, word, dataset=None):
        if dataset is None:
            dataset = self.leader_dataset
        matches = []
        for _word, timestamps in dataset.items():
            if word in _word:
                matches.extend(timestamps)
        return matches

    def get_all_words_matches(self, words=None, dataset=None):
        if words is None:
            words = self.text.split()
        words_matches = []
        for word in words:
            word_clean = "".join(filter(lambda char: char not in self.chars_dont_care, word)).lower()
            full_word_matches = self.get_full_matches(word_clean, dataset)
            if full_word_matches:
                words_matches.append(full_word_matches)
                continue
            contained_matches = self.get_contained_matches(word_clean, dataset)
            if contained_matches:
                words_matches.append(contained_matches)
                continue

            # no match
            words_matches.append([])

        return words_matches

    def pick_random_match_for_each_word(self, matches):
        return [random.choice(match) if match else None for match in matches]

    def __convert_seconds_to_hhmmss(self, time_seconds):
        # return time.strftime('%H:%M:%S', time.gmtime(time_seconds))
        return datetime.utcfromtimestamp(time_seconds).strftime('%H:%M:%S.%f')[:-4]

    def trim_video(self, start_time, end_time, video_file, output_file):
        trim_cmdline = ["/usr/local/bin/ffmpeg",
                        "-ss",
                        self.__convert_seconds_to_hhmmss(start_time),
                        "-to",
                        self.__convert_seconds_to_hhmmss(end_time),
                        "-i",
                        video_file,
                        "-c",
                        "copy",
                        output_file]
        subprocess.call(trim_cmdline)

    def concat_video(self, output_file):
        concat_cmdline = ["/usr/local/bin/ffmpeg",
                          "-f",
                          "concat", "-safe",
                          "0",
                          "-i",
                          self.tmp_created_file,
                          "-c",
                          "copy",
                          output_file]
        subprocess.call(concat_cmdline)

    def get_filter_complex(self, input_files):
        complexes = []
        for i in range(len(input_files)):
            complexes.append(f"[{i}:v] [{i}:a]")
        return " ".join(complexes) + " " + f"concat=n={len(input_files)}:v=1:a=1 [v] [a]"

    def get_input_files_ffmpeg_format(self, input_files):
        formatted_input = []
        for input_file in input_files:
            formatted_input.append("-i")
            formatted_input.append(input_file)
        return formatted_input

    def concat_video2(self, input_files, output_file):
        concat_cmdline = ["/usr/local/bin/ffmpeg",
                          *self.get_input_files_ffmpeg_format(input_files),
                          "-filter_complex",
                          "{}".format(self.get_filter_complex(input_files)),
                          "-map",
                          "[v]",
                          "-map",
                          "[a]",
                          output_file]
        print(concat_cmdline)
        subprocess.call(concat_cmdline)
#         asd = 'ffmpeg -i opening.mkv -i episode.mkv -i ending.mkv \
# -filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] \
# concat=n=3:v=1:a=1 [v] [a]" \
# -map "[v]" -map "[a]" output.mkv'

    def get_next_file_name(self, videos_dir):
        filenames = next(os.walk(videos_dir), (None, None, []))[2]  # [] if no file
        filenames = list(filter(lambda name: name[:3] not in ["tmp", ], filenames))
        file_numbers = list(map(lambda filename: int(filename.split(".")[0]), filenames))
        return str(max(file_numbers) + 1) if file_numbers else "1"

    def minimize_timestamp_error(self, clip, i):
        word = self.text.split()[i]
        word_clean = "".join(filter(lambda char: char not in self.chars_dont_care, word)).lower()
        wav_file = "tmp-minimize.wav"
        clip.audio.write_audiofile(wav_file)
        stt = speech_to_text.SpeechToText()
        timestamps = stt.save_to_db_speech_to_text_with_timestamps(wav_file=wav_file, save=False)
        word_matches = self.get_all_words_matches(words=[word_clean], dataset=timestamps)
        random_match = self.pick_random_match_for_each_word(word_matches)[0]
        start_time = float(random_match["startTime"].replace("s", ""))
        end_time = float(random_match["endTime"].replace("s", ""))
        word_clip = clip.subclip(t_start=self.__convert_seconds_to_hhmmss(start_time), t_end=self.__convert_seconds_to_hhmmss(end_time))
        try:
            os.remove(wav_file)
        except FileNotFoundError:
            pass
        return word_clip

    def create(self, tolerance_seconds=5):
        words_matches = self.get_all_words_matches()
        random_matches = self.pick_random_match_for_each_word(words_matches)
        if None in random_matches:
            raise ValueError("Unable to create the video, there are words that don't exist")
        # tmp_created = []
        clips_list = []
        for i, match in enumerate(random_matches):
            start_time_original = float(match["startTime"].replace("s", ""))
            start_time = start_time_original - tolerance_seconds if start_time_original - tolerance_seconds >= 0 else 0
            end_time = float(match["endTime"].replace("s", "")) + tolerance_seconds
            trim_dict = {"start": self.__convert_seconds_to_hhmmss(start_time),
                         "end": self.__convert_seconds_to_hhmmss(end_time)}
            video_file = os.path.join(self.downloaded_videos_dir, str(match["videoNumber"]) + ".mp4")
            # output_file = os.path.join(self.created_videos_dir, f"tmp{i}.mp4")

            clip = VideoFileClip(video_file)
            clip = clip.subclip(t_start=trim_dict["start"], t_end=trim_dict["end"] if end_time < clip.duration else clip.duration)
            minimized_clip = self.minimize_timestamp_error(clip, i)
            clips_list.append(minimized_clip)
            # self.trim_video(trim_dict, video_file, output_file)
            # tmp_created.append(output_file)

        # with open(self.tmp_created_file, "w") as f:
        #     content = "\n".join([f"file {tmp_video}" for tmp_video in tmp_created])
        #     f.write(content)
        video_number = self.get_next_file_name(self.created_videos_dir)
        final_clip = concatenate_videoclips(clips_list)
        output_file = os.path.join(self.created_videos_dir, f"{video_number}.mp4")
        tmp_audio_file = "temp-audio.mp3"
        final_clip.write_videofile(output_file, temp_audiofile=tmp_audio_file, remove_temp=False)
        # command = ['ffmpeg',
        #            '-y',  # approve output file overwite
        #            '-i', output_file,
        #            '-i', tmp_audio_file,
        #            '-c:v', 'copy',
        #            '-c:a', 'copy',
        #            '-shortest',
        #            f"{output_file.split('.')[0]}_final.mp4"]
        # subprocess.call(command)

        # os.remove(tmp_audio_file)
        # os.remove(output_file)

        # self.concat_video(output_file)
        #
        # for tmp_file in tmp_created:
        #     os.remove(tmp_file)
        # os.remove(self.tmp_created_file)

    def does_word_exists(self, word):
        return self.get_full_matches(word) is not None

    def is_word_contained(self, word):
        return bool(self.get_contained_matches(word))

    def get_possible_text(self, text):
        words = text.lower().split()
        possible_text = []
        for word in words:
            if not self.does_word_exists(word):
                if not self.is_word_contained(word):
                    possible_text.append("-")
                    continue
                else:
                    possible_text.append(word)
            else:
                possible_text.append(word)
        return " ".join(possible_text)

    def get_video_file(self, directory, video_id):
        filenames = next(os.walk(directory), (None, None, []))[2]  # [] if no file
        filenames = list(filter(lambda name: name.startswith(video_id), filenames))
        return os.path.join(directory, filenames[0])

    def create_full_video(self, videos_and_timestamps_that_put_together_the_text, leader_name):
        yt = youtube.Youtube()
        downloaded_videos_dir = os.path.join(yt.downloads_dir, leader_name, "videos")
        trim_files = []
        sub_clips = []
        for video_and_timestamp in videos_and_timestamps_that_put_together_the_text:
            yt.download_video(video_and_timestamp[Video.VIDEO_ID], leader_name)
            video_file = self.get_video_file(downloaded_videos_dir, video_and_timestamp[Video.VIDEO_ID])
            random_trim_filename = str(random.random())[2:] + ".mp4"
            random_trim_filename = os.path.join(downloaded_videos_dir, random_trim_filename)
            self.trim_video(start_time=video_and_timestamp[VideoTimes.START_TIME],
                            end_time=video_and_timestamp[VideoTimes.END_TIME],
                            # start_time=video_and_timestamp[VideoTimes.START_TIME] - video_and_timestamp[
                            #     VideoTimes.AVAILABLE_TIME_BEFORE] if video_and_timestamp[VideoTimes.START_TIME] -
                            #                                          video_and_timestamp[
                            #                                              VideoTimes.AVAILABLE_TIME_BEFORE] > 0 else
                            # video_and_timestamp[VideoTimes.START_TIME],
                            # end_time=video_and_timestamp[VideoTimes.END_TIME] + video_and_timestamp[
                            #     VideoTimes.AVAILABLE_TIME_AFTER],
                            video_file=video_file,
                            output_file=random_trim_filename
                            )
            video_clip = VideoFileClip(random_trim_filename)
            print("************")
            print(video_and_timestamp["word"])
            print(video_clip.duration)
            print("************")
            text_clip = TextClip(video_and_timestamp["word"], fontsize=70, color='white').set_pos('bottom').set_duration(video_clip.duration)
            sub_clip = CompositeVideoClip([video_clip, text_clip])
            sub_clips.append(sub_clip)
            # trim_files.append(random_trim_filename)
        # with open(self.tmp_created_file, "w") as f:
        #     content = "\n".join([f"file {tmp_video}" for tmp_video in trim_files])
        #     f.write(content)
        # video_clips = [VideoFileClip(trim_file) for trim_file in trim_files]
        final_clip = concatenate_videoclips(sub_clips)
        output_file = os.path.join(downloaded_videos_dir, "output.mp4")
        tmp_audio_file = "temp-audio.mp3"
        final_clip.write_videofile(output_file, temp_audiofile=tmp_audio_file, remove_temp=False, codec="libx264")
        command = ["/usr/local/bin/ffmpeg",
                   # '-y',  # approve output file overwrite
                   '-i', str(output_file),
                   '-i', str(tmp_audio_file),
                   '-c:v', 'copy',
                   '-c:a', 'copy',
                   '-shortest',
                   '-y'
                   "delete-me.mp4"]
        subprocess.call(command)
        # self.concat_video2(trim_files, os.path.join(downloaded_videos_dir, "magnus.mp4"))
        for trim_file in trim_files:
            os.remove(trim_file)
        os.remove("temp-audio.mp3")
        os.remove("delete-me.mp4")

if __name__ == '__main__':
    vc = VideoCreator("I am a great husband of hillary clinton", "trump")
    # print(vc.get_possible_text("I am a great husband of hillary clinton"))
    # vc.create()
    vc.concat_video2(["qwe.mp4", "asd.mp4"], "output.mp4")
