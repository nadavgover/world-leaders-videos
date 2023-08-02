import random

from db import DB2
from speech_to_text import SpeechToText2
from enums import VideoTimes, Video


class TextSearch(object):
    def __init__(self):
        self.db = DB2()
        self.stt = SpeechToText2()

    def _get_saved_documents_of_leader(self, leader):
        return self.db.get_documents({"name": leader})

    def _get_transcriptions_of_leader(self, documents_from_db):
        videos_and_transcriptions = {}
        for doc in documents_from_db:
            rev_job_id = doc["rev_job_id"]
            video_id = doc["video_id"]
            transcript = self.stt.get_transcript(rev_job_id)
            videos_and_transcriptions[video_id] = transcript
        return videos_and_transcriptions

    def _filter_by_speaker(self, videos_and_transcriptions_dict, speaker_num=0, assume_speaker=True):
        """Sometimes the transcription recognizes there is more than one speaker, but we only care about the leader.
        The first speaker is speaker 0 and the second speaker is speaker 1 etc.
        Usually the leader will be speaker 0, but in some cases the video starts with somebody else talking.
        assume_speaker is an automatic speaker selection,
        based on the fact that most of the times the leader is the main speaker of the video.
        If assume_speaker is set to True then speaker_num does not matter
        """
        filtered_videos_and_transcriptions_dict = {}
        for video_id in videos_and_transcriptions_dict:
            monologues = videos_and_transcriptions_dict[video_id]["monologues"]
            if assume_speaker:
                speakers_histogram = {}
                for monologue in monologues:
                    speaker = monologue["speaker"]
                    speakers_histogram[speaker] = speakers_histogram.get(speaker, 0) + 1
                max_appearances = -1
                assumed_speaker = 0
                for speaker, appearances in speakers_histogram.items():
                    if appearances > max_appearances:
                        max_appearances = appearances
                        assumed_speaker = speaker
                filtered_monologues = list(filter(lambda monologue: monologue["speaker"] == assumed_speaker, monologues))
                filtered_videos_and_transcriptions_dict[video_id] = {"monologues": filtered_monologues}
            else:
                filtered_monologues = list(filter(lambda monologue: monologue["speaker"] == speaker_num, monologues))
                filtered_videos_and_transcriptions_dict[video_id] = {"monologues": filtered_monologues}

        return filtered_videos_and_transcriptions_dict

    def _filter_by_punctuation_and_confidence(self, videos_and_transcriptions_dict, confidence=0.9):
        """Filter all punctuations and transcriptions that Rev AI has low confidence in it"""
        filtered_videos_and_transcriptions_dict = {}
        for video_id in videos_and_transcriptions_dict:
            monologues = videos_and_transcriptions_dict[video_id]["monologues"]
            filtered_monologues = []
            for monologue in monologues:
                filtered_monologue = {**monologue}
                elements = monologue["elements"]
                filtered_elements = list(filter(lambda element: element["type"] == "text" and element["confidence"] >= confidence, elements))
                filtered_monologue["elements"] = filtered_elements
                filtered_monologues.append(filtered_monologue)
            filtered_videos_and_transcriptions_dict[video_id] = {"monologues": filtered_monologues}

        return filtered_videos_and_transcriptions_dict

    def _get_available_words_and_timestamps(self, videos_and_transcriptions_dict):
        available_words_and_timestamps = {}
        for video_id in videos_and_transcriptions_dict:
            monologues = videos_and_transcriptions_dict[video_id]["monologues"]
            for monologue in monologues:
                elements = monologue["elements"]
                for i, element in enumerate(elements):
                    word = element["value"].lower()
                    start_time = element["ts"]
                    end_time = element["end_ts"]
                    if i == 0:
                        available_time_before = 0
                    else:
                        available_time_before = start_time - elements[i - 1]["end_ts"]
                    if i == len(elements) - 1:
                        available_time_after = 0
                    else:
                        available_time_after = elements[i + 1]["ts"] - end_time
                    word_histogram = available_words_and_timestamps.get(word, [])
                    word_histogram.append({
                        Video.VIDEO_ID: video_id,
                        VideoTimes.START_TIME: start_time,
                        VideoTimes.END_TIME: end_time,
                        VideoTimes.AVAILABLE_TIME_BEFORE: available_time_before,
                        VideoTimes.AVAILABLE_TIME_AFTER: available_time_after
                    })
                    available_words_and_timestamps[word] = word_histogram

        return available_words_and_timestamps


    def _get_vocabulary_and_timestamps(self, leader, confidence=0.9):
        documents_from_db = self._get_saved_documents_of_leader(leader)
        videos_and_transcriptions_dict = self._get_transcriptions_of_leader(documents_from_db)
        transcriptions_filtered_by_speaker = self._filter_by_speaker(videos_and_transcriptions_dict, assume_speaker=True)
        transcriptions_filtered_by_punctuation = self._filter_by_punctuation_and_confidence(transcriptions_filtered_by_speaker, confidence=confidence)
        available_words_and_timestamps = self._get_available_words_and_timestamps(transcriptions_filtered_by_punctuation)
        return available_words_and_timestamps

    def get_not_existing_words(self, vocabulary, text_to_find):
        """Return a list of words that are in the text_to_find but we don't have them in the vocabulary
        (the leader never said them)"""
        words = text_to_find.lower().split(" ")
        not_found_words = []
        for word in words:
            if word not in vocabulary:
                not_found_words.append(word)
        return not_found_words

    def is_text_possible(self, text_to_find, vocabulary=None, leader="", confidence=0.9):
        if vocabulary is None:
            vocabulary = self._get_vocabulary_and_timestamps(leader, confidence)
        return not bool(self.get_not_existing_words(vocabulary, text_to_find))

    def _pick_random_video_and_timestamp_of_word(self, vocabulary_and_timestamps, word):
        all_possibilities = vocabulary_and_timestamps[word]
        return {**random.choice(all_possibilities), "word": word}

    def get_videos_and_timestamps_that_put_together_text(self, text_to_find, leader, confidence=0.9):
        vocabulary = self._get_vocabulary_and_timestamps(leader, confidence)
        if self.is_text_possible(text_to_find, vocabulary):
            words = text_to_find.lower().split(" ")
            videos_and_timestamps = []
            for word in words:
                videos_and_timestamps.append(self._pick_random_video_and_timestamp_of_word(vocabulary, word))

            return videos_and_timestamps
        print("******")
        print("Could not find words:")
        print(self.get_not_existing_words(vocabulary, text_to_find))
        print("******")
        return False


if __name__ == '__main__':
    text_search = TextSearch()
    videos_and_timestamps_that_put_together_the_text = text_search.get_videos_and_timestamps_that_put_together_text(
        text_to_find="I love democrats",
        leader="trump",
        confidence=0.9
    )
    a = 1