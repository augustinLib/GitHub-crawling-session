from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random
from urllib import request
import argparse
from tqdm import tqdm
import re


def define_argparse():
    p = argparse.ArgumentParser()

    p.add_argument("--file_name", required=True)

    config = p.parse_args()
    return config


# .py 버전에서 .sh와 연계하여 사용
config = define_argparse()
url = config.url
df = pd.read_csv(f"./data/{config.file_name}.csv")

url_list = df["product_num"]

options = webdriver.ChromeOptions()
# 탭 간 이동 활성화
options.add_argument("no-sandbox")
# options.add_argument("headless")


review_list = []
star_list = []
product_num_list = []


with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
    omitted_num = 0
    for num in tqdm(url_list):
        try:
            # 상품 고유번호 이용하여 url 생성
            url = f"https://www.musinsa.com/app/goods/{num}"
            driver.get(url)
            driver.implicitly_wait(5)
            
            # ()안에 존재하는 총 리뷰 개수 추출하기 위해 정규표현식 사용
            inside_bracket = re.compile('\((.*?)\)')
            print("loading complete")
            # 스타일 후기 개수
            style = driver.find_element(
                By.CSS_SELECTOR,
                "#estimate_style"
            )
            style_temp = inside_bracket.findall(style.text)[0]
            print(style_temp)
            style_temp = style_temp.replace(",", "")
            # 문자열이기 때문에 정수형으로 변환
            style_num = int(style_temp)

            # 상품 후기 개수
            photo = driver.find_element(
                By.CSS_SELECTOR,
                "#estimate_photo"
            )
            
            photo_temp = inside_bracket.findall(photo.text)[0]
            print(photo_temp)
            photo_temp = photo_temp.replace(",", "")
            # 문자열이기 때문에 정수형으로 변환
            photo_num = int(photo_temp)

            # 일반 후기 개수
            goods = driver.find_element(
                By.CSS_SELECTOR,
                "#estimate_goods"
            )
            goods_temp = inside_bracket.findall(goods.text)[0]
            print(goods_temp)
            goods_temp = goods_temp.replace(",", "")
            # 문자열이기 때문에 정수형으로 변환
            goods_num = int(goods_temp)
            print(goods_num)

            # 각 리뷰 타입
            review_type_list = [style, photo, goods]
            time.sleep(random.uniform(0,2))
            
            # 각 리뷰 20개씩 없으면 패스
            if style_num < 3 or photo_num < 3 or goods_num < 3:
                omitted_num += 1
                print("리뷰 부족")

                continue
            
            # 리뷰 정렬 조작하기 위해 정렬 요소 추출
            sort = driver.find_element(
                By.CSS_SELECTOR,
                ""
            )
            
            # 토글, 드롭다운 등 다양한 요소를 조작하기 위헤 
            #selenium.webdriver.support.ui.Select 사용
            sort_select = Select(sort)

            # 각 리뷰 종류 클릭으로 이동 (각 리뷰 당 40개 추출)
            # 리뷰 버튼에는 따로 자바스크립트 요소가 없기 때문에 click() 메소드로 조작
            for review_type in review_type_list:
                if review_type != style:
                    review_type.click()
                # IP 밴 방지
                time.sleep(random.uniform(0,1))
                
                # 높은 평점 순으로 정렬
                # 조작하고 싶은 값의 value를 찾은 뒤,
                # select_by_value() 메소드로 이를 조작
                sort_select.select_by_value("")
                
                # 각 리뷰 별 높은 평점 순 20개 추출
                for page in range(1, 3):
                    if page != 1:
                        driver.execute_script(f"ReviewPage.goPage({page});")
                    time.sleep(random.uniform(0,1))
                    for i in range(1,11):
                        
                        # 리뷰 텍스트 추출
                        review = driver.find_element(
                            By.CSS_SELECTOR,
                            f"#reviewListFragment > div:nth-child({i}) > div.review-contents > div.review-contents__text"
                        )
                        review_txt = review.text
                        review_txt = review_txt.replace("\n", " ")

                        # 별점 추출
                        # 이때, 별점이 그림으로만 있고 텍스트로 따로 보이지 않는다
                        # 이런 경우에는 텍스트로 전환할 수 있는 요소를 찾아서 해결해보자
                        star_raw = driver.find_element(
                            By.CSS_SELECTOR,
                            f"#reviewListFragment > div:nth-child({i}) > div.review-list__rating-wrap > span > span > span"
                        )
                        
                        # 해당 요소의 style 항목을 보면,
                        # 별 1개는 20, 2개는 40의 규칙이 보인다. (style="width: 100%")
                        # 이를 이용해보자
                        
                        # get_attribute()로 해당 요소의 style의 값 불러오기
                        star = star_raw.get_attribute("style")
                        
                        # width: 제거 위해 split
                        star_temp = star.split(": ")[-1]
                        
                        # %과 ; 제거
                        star_temp = star_temp.replace("%", "")
                        star_temp = star_temp.replace(";", "")
                        
                        # 남겨진 텍스트를 정수형으로 바꾼 뒤, 20으로 나눠준다
                        star_result = int(star_temp) / int(20)
                        product_num_list.append(num)
                        review_list.append(review_txt)
                        star_list.append(star_result)


                    time.sleep(random.uniform(0,1))
        


                # 낮은 평점 순으로 정렬
                # 조작하고 싶은 값의 value를 찾은 뒤,
                # select_by_value() 메소드로 이를 조작
                sort_select.select_by_value("goods_est_asc")
                
                # 각 리뷰 별 낮은 평점 순 20개 추출
                for page in range(1, 3):
                    if page != 1:
                        driver.execute_script(f"ReviewPage.goPage({page});")
                    time.sleep(random.uniform(0,1))
                    for i in range(1,11):
                        
                        # 리뷰 텍스트 추출
                        review = driver.find_element(
                            By.CSS_SELECTOR,
                            f"#reviewListFragment > div:nth-child({i}) > div.review-contents > div.review-contents__text"
                        )
                        review_txt = review.text
                        review_txt = review_txt.replace("\n", " ")

                        # 별점 추출
                        # 이때, 별점이 그림으로만 있고 텍스트로 따로 보이지 않는다
                        # 이런 경우에는 텍스트로 전환할 수 있는 요소를 찾아서 해결해보자
                        star_raw = driver.find_element(
                            By.CSS_SELECTOR,
                            f"#reviewListFragment > div:nth-child({i}) > div.review-list__rating-wrap > span > span > span"
                        )
                        
                        # 해당 요소의 style 항목을 보면,
                        # 별 1개는 20, 2개는 40의 규칙이 보인다. (style="width: 100%")
                        # 이를 이용해보자
                        
                        # get_attribute()로 해당 요소의 style의 값 불러오기
                        star = star_raw.get_attribute("style")
                        
                        # width: 제거 위해 split
                        star_temp = star.split(": ")[-1]
                        
                        # %과 ; 제거
                        star_temp = star_temp.replace("%", "")
                        star_temp = star_temp.replace(";", "")
                        
                        # 남겨진 텍스트를 정수형으로 바꾼 뒤, 20으로 나눠준다
                        star_result = int(star_temp) / int(20)
                        product_num_list.append(num)
                        review_list.append(review_txt)
                        star_list.append(star_result)


                    time.sleep(random.uniform(0,1))
                    

                product_df = pd.DataFrame({"product_num" :product_num_list,
                                            "review" : review_list,
                                            "star" : star_list
                                            })
                
                product_df.to_csv(f"./data/{config.file_name}_review.csv")
        except:
            omitted_num += 1
            continue
        
    print(f"{omitted_num} omitted!")
