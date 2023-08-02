from youtube import Youtube
from speech_to_text import SpeechToText


def download_videos(leaders_and_videos_dict):
    yt = Youtube()
    for leader_name, video_list in leaders_and_videos_dict.items():
        for video_dict in video_list:
            if not video_dict.get("already_done"):
                yt.download_video_of_leader(video_dict["url"], leader_name, video_dict.get("trims"))


def analyze_videos_and_save_to_db():
    stt = SpeechToText()
    stt.analyze_all_downloaded_files()


def main(leaders_and_videos):
    download_videos(leaders_and_videos)
    analyze_videos_and_save_to_db()


if __name__ == '__main__':
    leaders_and_videos = {
        "trump": [
            {
                "url": "https://www.youtube.com/watch?v=kOvd4h70PXw",
                "already_done": True
            },
            {
                "url": "https://www.youtube.com/watch?v=sE55ZBJV0Ug",
                "already_done": True
            },
            {
                "url": "https://www.youtube.com/watch?v=Gx76TtLYRwI",
                "trims": [
                    {
                        "start": "00:00:00",
                        "end": "01:10:00"
                    }
                ],
                "already_done": True
            },
            {
                "url": "https://www.youtube.com/watch?v=QGpmnA2JJ4U",
                "trims": [
                    {
                        "start": "00:00:30",
                        "end": "00:04:34"
                    }
                ],
                "already_done": True
            },
            {
                "url": "https://www.youtube.com/watch?v=81eWnIOLyAc",
                "trims": [
                    {
                        "start": "00:00:30",
                        "end": "00:13:50"
                    }
                ],
                "already_done": True
            }
        ]
    }

    main(leaders_and_videos)
