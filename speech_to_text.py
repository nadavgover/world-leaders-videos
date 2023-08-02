import speech_recognition as sr
import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip
# from pocketsphinx import AudioFile, Pocketsphinx
from rev_ai import apiclient, JobStatus

import db


def get_duration(input_audio):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_audio], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return int(float(result.stdout))


def convert_to_wav(input_file, wav_output, fps=44100):
    # convert_to_wav_cmdline = ["ffmpeg",
    #                           "-y",
    #                           "-i",
    #                           input_file,
    #                           "-vn",
    #                           "-f",
    #                           "wav",
    #                           wav_output]
    # subprocess.call(convert_to_wav_cmdline)
    clip = VideoFileClip(input_file)
    clip.audio.write_audiofile(wav_output, fps=fps)


def get_fps(wav_file):
    clip = AudioFileClip(wav_file)


class SpeechToText(object):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.google_cloud_speech_to_text_credentials = r'{"type": "service_account","project_id": "single-healer-324920","private_key_id": "4f5254574211cdc876967b0ef95e25810c73e832","private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCZkbDJBz711fB1\nKTHGicjHl6WuQmbgy3PanGaBNwVAOtNZmWYN2cyufwM1fE76rDG5jWt/HX7szq1v\n7F8/L0htoEjADN/0wQKIxo0Je7/9M0Lv5OTIJ0muEbQ0tKhduSfRzLw5x12bKbbe\nlX4yGAZ0TmjYWaTi/aVzXGniTBwFMC95bcE7I1+5cNeXJjtzKy4qtuffHYlJoyqc\nfHjHZhaVxAKWfX3oWcdHL7667Wy7gaPAdxhalujtRwrwNaccY7zVjtFbAoTMGDs/\nU3WXQqK8u6GtRUMDfMxNUG4Rc14Xz4dV+HJtifRSfVrBFDeZt4Pb378PPEPuYYU9\nwAwMI3sVAgMBAAECggEAAO+MU41BwEm6GgdS5ad38Q9m07WqiXrJN+8gCMWHDf8j\nGTaqvTGIjRT6YLG4jCUkdcGmLV4b+eFrLnVoQdWjQVfABGY6Wclwny4RNJpBGeUy\nu+IkgBENN+GlEXUlrtHZVkPtxFmx+Py7aoZ1Vbojv+2tDInEoXAeOU0PhXDP8uV3\n2e2a5Gmnk6PiIoZf3eHwIK+3gkz+sGYxAaFXUMPQLOj1lAFSgQx7NrUXuhiAxL2Y\nCAN6PIgAl53I3uPbwujfvdEdSiizzqQ7BfJ4S/69/NJZwpl9CHMCgH3FKsrSi+32\nC+QwFfBXQ1tGfsKR7JrcvwJaPPBXyIMjs2MAKQfpOQKBgQDJatA/IKMYil7E98vv\nb4JwHPijkpBIBFD5ZpgUeY4bcJ5I72lh+vBNjMZpqkWn6WjRSq+U/Uhj4JuvPKlQ\nWcoma2vOxV2zsRTp/xStRKNRclU07wt7dWyLgJ4AK9i0/GULtCl+kS6XaKqOovht\nZKLtcSbcNul0wH2lSIRg49Es8wKBgQDDL3HRKEEIYkZbcUvxPsM7uu5vc/maIG3s\n8bdWj10l2MYbVN83CrJjmOEluApd4UAS0Y2oHQv7rYyzvHuuTsziC5CQg0WIcb8m\n05aqiRaRP+0agSozuMYiWSFW4p6A4PeIjEoNbBwx8SvJh9fTSKm7QP1SavgrX01N\nB5aQNmEZ1wKBgCK105ltaG3sOpS7F1v13Yawl3Co61Bd3g58zayJniHAcKalC4Yl\nFpBmuDKxczuSj8uxkTydwYHkzS+PxqXgM2QXkwaZIKK825vPp6KMd5CroV9z6oim\nHcSUr6Xb6IaYEFnJ/HShVGQnV20pTKKdey5sF4RPuj+yhHSdYKLJ39xdAoGAHn9L\nSWMAxk6Ur7UEKK2l069hkgiM94gZpOwfuWatJzy3t42LUw5Y0TcR9tLKy+BmIoqb\nl6jyNmDnmy3YJWQqnycvb2UTeD5Nn8NvxzWkUQ2r/ngwH+S/EJ7clrbSDVEZXDyP\nVYmO3j7QmKyhDGJOIvQEoNwV6rD5Yw/MdrwIcAECgYBTQeF8rIQWiCKGNHL3gda1\ni5lsUULzXoImwWztSyZELn+R0I2E7hkanYVxzdbWIde3CZ+GYcpaBYWgSbMSggro\n7VGBYyX3VaL8SesJdAbYFDSCH4kZ9gMrP+XddjpaUj2oF4Tn6CcK7taX2GpQYnrJ\nMmGMI1Fyfg4OilGsJ+ZcKw==\n-----END PRIVATE KEY-----\n","client_email": "world-leaders-shorts@single-healer-324920.iam.gserviceaccount.com","client_id": "106687491323728067699","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/world-leaders-shorts%40single-healer-324920.iam.gserviceaccount.com"}'
        self.max_length_allowed_by_google = 45
        self.db = db.DB()
        self.downloads_dir = os.path.join(os.getcwd(), "downloads")

    def extract_words_and_timestamps_from_speech_to_text_api(self, texts, video_num, i):
        try:
            results = texts["results"]
        except KeyError:
            return None
        words_and_timestamps_dict = {}
        for result in results:
            best_alternative = result["alternatives"][0]
            words_and_timestamps_list = best_alternative["words"]

            for word_dict in words_and_timestamps_list:
                cur_word = word_dict["word"].lower()
                existing_timestamps = words_and_timestamps_dict.get(cur_word, [])
                start_time = str(float(word_dict["startTime"].split("s")[0]) + i) + "s"
                end_time = str(float(word_dict["endTime"].split("s")[0]) + i) + "s"
                cur_timestamps = {"startTime": start_time, "endTime": end_time, "videoNumber": video_num}
                existing_timestamps.append(cur_timestamps)
                words_and_timestamps_dict[cur_word] = existing_timestamps

        return words_and_timestamps_dict

    def save_to_db_speech_to_text_with_timestamps(self, video_file=None, leader_name=None, save=True, wav_file=None):
        fps = 44100
        if wav_file is None:
            wav_file = f"{video_file.split('.')[0]}.wav"
            convert_to_wav(video_file, wav_file, fps=fps)
            video_num = int(video_file.split(".")[0].split("/")[-1])
        else:
            video_num = 0

        # ps = Pocketsphinx()
        # ps.decode(
        #     audio_file=wav_file,
        #     buffer_size=2048,
        #     no_search=False,
        #     full_utt=False
        # )
        # a = ps.segments()

        # audio = AudioFile(lm=False, keyphrase='america', kws_threshold=1e-20, audio_file=wav_file, frate=fps)
        # for phrase in audio:
        #     word, prob, start_frame, end_frame = phrase.segments(detailed=True)[0]
        #     start_time_seconds = start_frame / fps
        #     end_time_seconds = end_frame / fps
        #     print(phrase.segments(detailed=True))  # => "[('forward', -617, 63, 121)]"
        duration_in_seconds = get_duration(wav_file)
        with sr.AudioFile(wav_file) as source:
            for i in range(0, duration_in_seconds, self.max_length_allowed_by_google):
                audio = self.recognizer.record(source, duration=self.max_length_allowed_by_google)
                try:
                    # texts = self.recognizer.recognize_google_cloud(audio, credentials_json=self.google_cloud_speech_to_text_credentials, show_all=True)
                    texts = self.recognizer.recognize_google(audio, show_all=False)
                    a = 1
                except Exception:
                    continue
                # words_and_timestamps = self.extract_words_and_timestamps_from_speech_to_text_api(texts,
                #                                                                                  video_num=video_num,
                #                                                                                  i=i)
                # if words_and_timestamps is not None and save:
                #     self.db.merge_with_existing_dataset(words_and_timestamps, leader_name, save=True)
                # if not save:
                #     os.remove(wav_file)
                #     return words_and_timestamps

        os.remove(wav_file)

    def analyze_all_downloaded_files(self):
        leader_names = next(os.walk(self.downloads_dir, (None, [], None)))[1]
        for leader_name in leader_names:
            video_files = next(os.walk(os.path.join(self.downloads_dir, leader_name, "videos")), (None, None, []))[2]
            for video_file in video_files:
                full_video_path = f"{self.downloads_dir}/{leader_name}/videos/{video_file}"
                if self.db.is_already_done(full_video_path):
                    self.save_to_db_speech_to_text_with_timestamps(video_file=full_video_path, leader_name=leader_name)
                    # self.db.save_to_done_list(full_video_path)
                    print(f"Finished analyzing {full_video_path}")


class SpeechToText2(object):
    """Use Rev AI for speech to text"""
    def __init__(self):
        access_token = "02PbuL0oYTHS-EgNB8Ni5MOT9T4m1DAtPLhiu_SfCr0f1m60WTJmeCk_w2v52BtfEMm9YuqwVXivgyN8oXBBd3DWfbl9w"
        self.client = apiclient.RevAiAPIClient(access_token)
        self.downloads_dir = os.path.join(os.getcwd(), "downloads")

    def submit_file_for_analyzing(self, video_id, leader_name, delete_file_after_done=False):
        leader_audios_dir = os.path.join(self.downloads_dir, leader_name, "audios")
        all_files = next(os.walk(leader_audios_dir), (None, None, []))[2]  # [] if no file
        try:
            filename = list(filter(lambda file: file.startswith(video_id), all_files))[0]
        except IndexError as e:
            print(f"No file found. leader_name: {leader_name}, video id: {video_id}")
            print(e)
            return
        filepath = os.path.join(leader_audios_dir, filename)

        print(f"started uploading audio file, video id: {video_id}")
        # this takes time of approximately the length of the audio file
        job = self.client.submit_job_local_file(filepath)
        print(f"finished uploading audio file, video id: {video_id}")
        if delete_file_after_done:
            print(f"deleting audio file, video id: {video_id}")
            os.remove(filepath)
        return job.id  # with the job id we can get the transcript

    def get_transcript(self, job_id):
        job_details = self.client.get_job_details(job_id)  # get status of job
        if job_details.status != JobStatus.TRANSCRIBED:
            raise ValueError(f"job is not transcribed yet, "
                             f"make sure you wait a ~minute after uploading the file is completed. job id {job_id}")

        transcript_json = self.client.get_transcript_json(job_id)
        return transcript_json


if __name__ == '__main__':
    stt = SpeechToText2()
    # job_id = stt.submit_file_for_analyzing("kOvd4h70PXw", "trump")
    job_ids = ["YOcelkutAnUNEKkx", "l9yBw7R4gOM9ADVs", "nuWb7ulRUP8u0xew", "9W3kvzvQwkvEMWz4"]
    transcript = stt.get_transcript("9W3kvzvQwkvEMWz4")
    a = 1