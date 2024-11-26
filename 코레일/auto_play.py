import schedule
import time
import os

def job():
    os.system('python 코레일/auto.py') # 실행할 파이썬 파일 경로

# 매일 특정 시간에 실행 (예: 매일 오전 9시)
schedule.every().day.at("04:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)