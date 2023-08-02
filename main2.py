from youtube import Youtube
from speech_to_text import SpeechToText2
from db import DB2
from text_search import TextSearch
from video_creator import VideoCreator


def download_audios(leaders_and_videos_dict):
    print("Started downloading all audios")
    yt = Youtube()
    for leader_name, video_list in leaders_and_videos_dict.items():
        for video_dict in video_list:
            yt.download_audio(video_dict["video_id"], leader_name)
    print("Finished downloading all audios")


def analyze_audios_and_save_to_db(leaders_and_videos_dict):
    """Save documents to Mongo DB
    With the job id of each document we can later get the transcript of the audio file"""
    print("Started submitting files for transcriptions")
    stt = SpeechToText2()
    db = DB2()
    for leader_name, video_list in leaders_and_videos_dict.items():
        for video_dict in video_list:
            video_id = video_dict["video_id"]
            # this takes time of approximately the length of the audio file
            job_id = stt.submit_file_for_analyzing(video_id, leader_name)
            if job_id:
                document = db.build_document(leader_name, job_id, video_id)
                db.insert_document(document)
    print("Finished submitting files for transcriptions. Wait ~1 minute until transcriptions are ready to use")


def remove_audios_that_were_already_transcribed(leaders_and_videos_dict):
    db = DB2()
    leaders_and_videos_dict_filtered = {}
    for leader_name, video_list in leaders_and_videos_dict.items():
        video_list_filtered = list(filter(lambda video_dict: not db.does_exist({"video_id": video_dict["video_id"]}), video_list))
        leaders_and_videos_dict_filtered[leader_name] = video_list_filtered
    return leaders_and_videos_dict_filtered


def download_audios_and_transcribe(leaders_and_videos_dict):
    leaders_and_videos_dict_no_duplicates = remove_audios_that_were_already_transcribed(leaders_and_videos_dict)
    download_audios(leaders_and_videos_dict_no_duplicates)
    analyze_audios_and_save_to_db(leaders_and_videos_dict_no_duplicates)


def get_videos_and_timestamps_that_put_together_the_text(text_to_find, leader_name, confidence=0.9):
    text_search = TextSearch()
    videos_and_timestamps_that_put_together_the_text = text_search.get_videos_and_timestamps_that_put_together_text(
        text_to_find=text_to_find,
        leader=leader_name,
        confidence=confidence
    )
    return videos_and_timestamps_that_put_together_the_text


def create_full_video(videos_and_timestamps_that_put_together_the_text, leader_name):
    print("Started creating the full video")
    vc = VideoCreator()
    vc.create_full_video(videos_and_timestamps_that_put_together_the_text, leader_name)


if __name__ == '__main__':
    leaders_and_videos = {
        "trump": [
            {
                "video_id": "kOvd4h70PXw"
            },
            {
                "video_id": "sE55ZBJV0Ug"
            },
            {
                "video_id": "Gx76TtLYRwI"
            },
            {
                "video_id": "81eWnIOLyAc"
            }
        ],
        "gotham": [
            {
                "video_id": "X1oIG9sWRbk"
            }
        ]
    }

    download_audios_and_transcribe(leaders_and_videos)
    text_to_find = "magnus magnus beats hikaru"
    leader_name = "gotham"
    videos_and_timestamps_that_put_together_the_text = get_videos_and_timestamps_that_put_together_the_text(text_to_find, leader_name)
    create_full_video(videos_and_timestamps_that_put_together_the_text, leader_name)
