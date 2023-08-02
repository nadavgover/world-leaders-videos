import enum


class VideoTimes(enum.Enum):
    START_TIME = "start_time"
    END_TIME = "end_time"
    AVAILABLE_TIME_BEFORE = "available_time_before",
    AVAILABLE_TIME_AFTER = "available_time_after"


class Video(enum.Enum):
    VIDEO_ID = "video_id"
