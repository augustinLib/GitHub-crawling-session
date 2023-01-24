from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import argparse
import random


def define_argparse():
    p = argparse.ArgumentParser()

    p.add_argument("--url", required=True)
    p.add_argument("--pages", type=int)
    p.add_argument("--type", required=True)

    config = p.parse_args()
    return config


#.py 버전에서 .sh와 연계하여 사용
config = define_argparse()
url = config.url


options = webdriver.ChromeOptions()
# 탭 간 이동 활성화
options.add_argument("no-sandbox")

# 아무것도 안뜨게 조용하게 크롤링하기를 원할 때
options.add_argument("headless")

links = []


# with as 구문
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
    driver.get(url)
    driver.implicitly_wait(5)
    # 추후 누락된 친구들을 파악하기 위해 선언 후 초기화
    error_num = 0
    
    # css selector는 보통 1부터 시작하기 때문에 0이 아닌 1로 시작
    for page_num in range(1, config.pages):
        
        # execute_script() : 인자로 받은 자바스크립트 코드를 웹브라우저에서 실행
        # 각 page_num의 페이지 번호로 이동
        driver.execute_script(f"switchPage(document.f1,{page_num});")
        
        # 웹페이지의 모든 요소가 로딩될때까지 기다림
        # 모든 요소가 로딩되면 넘어가고, 인자로 받은 숫자의 초 만큼 기다렸는데도 로딩이 안되면 그냥 go
        driver.implicitly_wait(5)
        
        # 한 페이지에 있는 90개의 옷 크롤링
        for item_num in range(1,91):
            # 크롤링하다보면 에러가 많이 발생함
            # 이에 대처하기 위해 try-except 구문을 애용하면 좋다.
            try:
                # find_element()
                # 인자로 받은 조건에 알맞은 html 요소 중 첫 번째 1개만 가져온다
                # return type : webelement (셀레니움 패키지 안에 정의되어있는 객체)
                
                # find_elements()
                # 인자로 받은 조건에 알맞은 html 요소 모든 것을 가져온다.
                # return type : list (list의 각 요소들은 webelement)
                
                link= driver.find_element(
                By.CSS_SELECTOR,
                f"#searchList > li:nth-child({item_num}) > div.li_inner > div.article_info > p.list_info > a")

                # get_attribute()
                # webelement 메소드로, 해당 html 요소의 href 요소를 긁어온다.
                # href : 하이퍼링크
                temp_link = link.get_attribute("href")
                links.append(temp_link)
                
            except:
                print(f"{page_num}page {item_num}th error!")
                error_num += 1
                continue
        
        # time.sleep()
        # 크롤링 프로그램을 잠깐 정지시킨다.
        # 이걸 안하면 IP 밴먹을 수 있음
        # 또한, 같은 주기로 계속 정지시켜도 IP 밴을 먹으니
        # random하게 정지시키는 주기를 변화해준다.
        time.sleep(random.randint(2,6))
            
        

print(f"{error_num} items omitted!")
link_df= pd.DataFrame(links)
link_df.to_csv(f"./data/{config.type}.csv")
