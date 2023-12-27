import sys
from lib.msgSender import send_webhook

import sys

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
# selenium으로 키를 조작하기 위한 import
from selenium.webdriver.common.keys import Keys
# 페이지 로딩을 기다리는데에 사용할 time 모듈 import
import time

def login(driver, std_id, passwd):
    #크롬 드라이버에 url 주소 넣고 실행
    driver.get('https://dap.deu.ac.kr/')

    # 페이지가 완전히 로딩되도록 3초동안 기다림
    time.sleep(1)

    # 아이디와 비밀번호를 입력할 수 있는 input 태그를 찾음
    input_id = driver.find_element(By.CSS_SELECTOR, '#txt_id')
    input_passwd = driver.find_element(By.CSS_SELECTOR, '#txt_password')
    login_btn = driver.find_element(By.CSS_SELECTOR, '#BtnLogIn')

    # 아이디와 비밀번호를 입력하고 로그인 버튼을 누름
    input_id.send_keys(std_id)
    input_passwd.send_keys(passwd)
    login_btn.send_keys(Keys.ENTER)

    # 페이지가 로딩될 때까지 기다림
    time.sleep(5)

def del_other_pages(driver):
    # 팝업으로 뜬 다른 창들을 지웁니다
    for window_handle in driver.window_handles[1:]:
        driver.switch_to.window(window_handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

def get_grade(driver):
    # 학생 성적 조회 페이지로 이동
    driver.get('https://dap.deu.ac.kr/Student/USB/USB0301Q.aspx?mcd=111999&pid=Usb0301q')
    table = driver.find_element(By.CSS_SELECTOR, '#CP1_dt_result > tbody')

    rows = table.find_elements(By.CSS_SELECTOR, 'tr')  # 테이블의 모든 행을 가져옵니다.
    result = []  # 결과를 저장할 리스트를 초기화합니다.


    for row in rows:
        cols = row.find_elements(By.CSS_SELECTOR, 'td')  # 각 행의 모든 열을 가져옵니다.
        course_name = cols[2].text  # 3번째 열(교과목명)을 가져옵니다.
        grade = cols[6].text  # 7번째 열(성적)을 가져옵니다.
        
        # 각 행의 정보를 딕셔너리로 만들고 리스트에 추가합니다.
        result.append({'교과목명': course_name, '성적': grade})

    return result   


if __name__ == "__main__":
    argv = sys.argv
    
    if len(argv)!= 4:
        print("Usage: python main.py <WEBHOOK_URI> <STD_ID> <PASSWD>")
        exit(1)

    url = argv[1]
    std_id = argv[2]
    passwd = argv[3]

    try:
        driver = webdriver.Chrome() 

        login(driver, std_id=std_id, passwd=passwd)
        del_other_pages(driver)
        result = get_grade(driver)    
    except:
        print("조회에 실패하였습니다.")
        exit(1)
    
    result = [course['교과목명'] for course in result if course['성적'] != ' ']

    embed = {
        "title": "점수가 공개된 과목이 있습니다.",
        "description": f"dap 시스템을 확인해주세요.\n공개된 과목{result}",
        }

    data = {
        "content": "새로운 성적이 기입되었습니다\ndap.deu.ac.kr",
        "username": "성적 알리미",
        "embeds": [
            embed
            ],
    }
    
    send_webhook(url, data)
    