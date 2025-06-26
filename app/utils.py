import threading
import time
import shutil
import os

def schedule_deletion(folder_path, delay=600):
    def delete_later():
        time.sleep(delay)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    threading.Thread(target=delete_later, daemon=True).start()