from rev_ai import apiclient, JobStatus
import os
import time

ACCESS_TOKEN = "02PbuL0oYTHS-EgNB8Ni5MOT9T4m1DAtPLhiu_SfCr0f1m60WTJmeCk_w2v52BtfEMm9YuqwVXivgyN8oXBBd3DWfbl9w"
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

# create your client
client = apiclient.RevAiAPIClient(ACCESS_TOKEN)

start_time = time.time()
# job = client.submit_job_local_file(f"{DOWNLOADS_DIR}/trump/videos/6.wav")  # upload audio file
end_time = time.time()
print(f"elapsed time: {end_time - start_time}")  # this takes time of approx the length of the audio file
# print(job.id)

JOB_ID = "zLtdnZ0feQqGtpJt"

# job_details = client.get_job_details(JOB_ID)  # get status of job

transcript_object = client.get_transcript_object(JOB_ID)  # get transcript
a = 1

