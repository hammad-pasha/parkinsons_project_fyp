from config import create_app
from celery import shared_task
import time

app, mysql = create_app()  #-Line 2
celery_app = app.extensions["celery"]



@shared_task(ignore_result=False, bind=True, name="tasks.process_video", base=celery_app.Task)
def process_video(self, file_data):
    with open("UPLOAD_FOLDER/result.txt", "a") as f:
        f.write("\n\n" + str("res"))
    print("Processing Started")
    print("File Data is ",file_data)
    time.sleep(60)
    print("Processing Completed")
    return file_data