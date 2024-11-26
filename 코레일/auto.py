from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import telegram
import asyncio

# 코레일 로그인 정보
korail_id = '' # 회원번호
korail_pwd = '' # 비밀번호

# 예약 정보
adult = '2' # 성인
kid = '0' # 6세~12세
baby = '0' # 6세 미만
elder = '0' # 65세 이상
direction = '009' #(선택안함 빈칸 / 순방향석 009 / 역방향석 010)
departure_name = '행신' # 출발역
arrival_name = '여수EXPO' # 도착역

# 출발 날짜 선택
start_month = '09' 
start_day = '14'
start_time = '06'

password = ''
split_password = list(password)

#텔레그램 토큰
bot = telegram.Bot(token='')
chat_id = 6162713920

def setup_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(3)
    return driver

def login(driver):
    driver.get('https://www.letskorail.com/korail/com/login.do')
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/div[1]/div[1]/form[1]/fieldset/p/input[3]')
    driver.find_element(By.ID, 'txtMember').send_keys(korail_id) # 회원번호
    driver.find_element(By.ID, 'txtPwd').send_keys(korail_pwd) # 비밀번호
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/div[1]/div[1]/form[1]/fieldset/div[1]/ul/li[3]/a/img').click()
    driver.implicitly_wait(5)

# 메인페이지 팝업창이 뜰 경우 main()에 추가
def close_popup(driver):
    main = driver.window_handles
    for i in main:
        if i !=main[0]:
            driver.switch_to.window(i)
            driver.close()
    driver.switch_to.window(main[0])

def select_train_info(driver):
    driver.get('https://www.letskorail.com/ebizprd/EbizPrdTicketpr21100W_pr21110.do')
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/form/div/div[2]/ul/li[2]/input').click()
    # 인원정보 선택
    if int(adult) > 0:
        driver.find_element(By.ID, 'peop01').click()
        Select(driver.find_element(By.ID,'peop01')).select_by_value(adult)
    if int(kid) > 0:
        driver.find_element(By.ID, 'peop02').click()
        Select(driver.find_element(By.ID,'peop02')).select_by_value(kid)
    if int(baby) > 0 :
        driver.find_element(By.ID, 'peop04').click()
        Select(driver.find_element(By.ID,'peop04')).select_by_value(baby)
    if int(elder) > 0:
        driver.find_element(By.ID, 'peop03').click()
        Select(driver.find_element(By.ID,'peop03')).select_by_value(elder)
    if direction != '':
        driver.find_element(By.ID, 'seat02').click()
        Select(driver.find_element(By.ID,'seat02')).select_by_value(direction)
    # 출발역 및 도착역 입력
    dep_stn = driver.find_element(By.ID, 'start')
    dep_stn.clear()
    dep_stn.send_keys(departure_name)
    arr_stn = driver.find_element(By.ID, 'get')
    arr_stn.clear()
    arr_stn.send_keys(arrival_name)

    driver.find_element(By.ID, 's_month').click()
    Select(driver.find_element(By.ID,'s_month')).select_by_value(start_month)
    driver.find_element(By.ID, 's_day').click()
    Select(driver.find_element(By.ID,'s_day')).select_by_value(start_day)
    driver.find_element(By.ID, 's_hour').click()
    Select(driver.find_element(By.ID,'s_hour')).select_by_value(start_time)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/form/div/p/a/img').click()
    driver.implicitly_wait(2)

def reserv_ticket(driver):
    while True:
        # 확인할 스크립트 목록
        scripts = [
            "//a[contains(@href, 'infochk(1,0)')]",
            "//a[contains(@href, 'infochk(1,1)')]",
        ]
        for script_xpath in scripts:
            try:
                element = driver.find_element(By.XPATH, script_xpath)
                href = element.get_attribute("href")
                if href and "javascript:void(0);" not in href:
                    driver.execute_script(href)
                    print(f"{script_xpath} 스크립트 실행")
                    driver.switch_to.frame("embeded-modal-traininfo")
                    driver.find_element(By.XPATH, '/html/body/div/div[2]/p[3]/a').click()
                    return  # 실행 후 함수 종료
            except NoSuchElementException:
                print(f"{script_xpath} 요소를 찾을 수 없습니다.")
        # 스크립트를 실행하지 않은 경우 새로고침 버튼 클릭
        try:
            reload_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[3]/p/a/img')
            reload_button.click()
            print("새로고침 버튼 클릭")
        except NoSuchElementException:
            print("새로고침 버튼을 찾을 수 없습니다.")

async def send_start_message(driver):
    await bot.sendMessage(chat_id=chat_id, text="예매 완료됨 결제를 시작하겠음")
    
def close_alert(driver):
    try:
        alert = driver.switch_to.alert  # alert로 전환
        alert.accept()
        time.sleep(1)
        alert = driver.switch_to.alert
        alert.accept()
        driver.switch_to.default_content()
    except Exception as e:
        print(f"알림창을 닫는 중 오류 발생: {e}")

def pay_ticket(driver):
    driver.find_element(By. XPATH, '/html/body/div[1]/div[3]/div/div[1]/div[2]/form/div/p[1]/a[2]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div[2]/form/div[2]/div[2]/table/tbody/tr/td[3]/input').click()
    time.sleep(1)
    driver.find_element(By.ID, 'fnIssuing').click()
    time.sleep(1)
    window_handles = driver.window_handles
    print("현재 열린 윈도우 핸들 목록:")
    for handle in window_handles:
        print(handle)  # 각 핸들을 출력
    driver.switch_to.window(driver.window_handles[1])
    driver.execute_script(f"sbpaySelAcnt('081');")
    driver.find_element(By.ID, 'inputPwd1').send_keys(split_password[0]) # 회원번호
    driver.find_element(By.ID, 'inputPwd2').send_keys(split_password[1]) # 회원번호
    driver.find_element(By.ID, 'inputPwd3').send_keys(split_password[2]) # 회원번호
    driver.find_element(By.ID, 'inputPwd4').send_keys(split_password[3]) # 회원번호
    driver.find_element(By.ID, 'inputPwd5').send_keys(split_password[4]) # 회원번호
    driver.find_element(By.ID, 'inputPwd6').send_keys(split_password[5]) # 회원번호
    time.sleep(1)
    driver.execute_script(f"btnConfirm();")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframes[2])
    driver.find_element(By.ID, 'btn_next2').click()
    time.sleep(1)
    alert = driver.switch_to.alert  # alert로 전환
    alert.accept()

def main():
    driver = setup_driver()
    login(driver)
    select_train_info(driver)
    reserv_ticket(driver)
    asyncio.run(send_start_message(driver))
    close_alert(driver)
    pay_ticket(driver)

if __name__ == "__main__":
    main()

time.sleep(1000)