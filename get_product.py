from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random
from urllib import request
import argparse
from tqdm import tqdm

def define_argparse():
    p = argparse.ArgumentParser()

    p.add_argument("--file_name", required=True)

    config = p.parse_args()
    return config

# .py 버전에서 .sh와 연계하여 사용
config = define_argparse()
url = config.url
df = pd.read_csv(f"./data/{config.file_name}.csv")


url_list = df.iloc[:,1]
options = webdriver.ChromeOptions()
# 탭 간 이동 활성화
options.add_argument("no-sandbox")
# options.add_argument("headless")



product_num_list = []
product_name_list = []
brand_list = []
year_sold_list = []
like_list = []
rate_list = []
price_list = []
tag_list = []


with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
    omitted_num = 0
    # 테스트를 위해 3개만 뽑아봅시다
    for url in tqdm(url_list[3:6]):
        
        # 크롤링을 진행하다보면 어떤 상품에는 해당 요소가 존재하지 않을 수 있음
        # 이런 경우에는 존재하지 않는 요소를 None값 취급하고 뽑을지,
        # 아예 해당 상품을 뽑지 않을지를 선택해야함
        # 본 예제에서는 뽑지 않고 지나가는것을 선택함
        # 이를 위해 try-except 구문 활용
        try:
                driver.get(url)
                driver.implicitly_wait(5)
                
                # https://www.musinsa.com/app/goods/2096933
                # url의 규칙에 따라 맨 마지막에는 해당 상품의 고유 번호가 담겨있음 
                product_num = url.split("/")[-1]
                
                # 상품 이름
                product_name =  driver.find_element(
                        By.CSS_SELECTOR,
                        "")
                
                # 상품 브랜드
                brand = driver.find_element(
                        By.CSS_SELECTOR,
                        "")
                
                # 1년 판매량
                year_sold = driver.find_element(
                        By.CSS_SELECTOR,
                        "#sales_1y_qty")

                # 좋아요 개수
                like = driver.find_element(
                        By.CSS_SELECTOR,
                        f"")

                # 평점
                rate = driver.find_element(
                        By.CSS_SELECTOR,
                        "")
                
                # 가격
                price = driver.find_element(
                        By.CSS_SELECTOR,
                        "")
                
                # 이미지를 뽑기 위해 이미지 링크 추출
                image_url = driver.find_element(
                        By.CSS_SELECTOR,
                        "#detail_bigimg > div > img").get_attribute("src")
                
                # 해당 상품의 태그 추출
                # 여기서는 태그가 여러개이기 때문에 find elements
                # 즉, return은 list의 형태(혹은 iterable)
                tags = driver.find_elements(
                    By.CSS_SELECTOR,
                    ""
                )
                
                temp_tag_list = []
                # tags에 list의 형태(혹은 iterable)가 담겨있으므로, 반복문을 돌려서 하나씩 추출
                for tag in tags:
                # tag 맨 앞에 있는 # 제거
                    temp_tag_list.append(tag.text[1:])

                # temp_tag_list에 들어있는 해체된 태그들을
                # 추후 다루기 쉽게 문자열로 변환
                tag_str = ",".join(temp_tag_list)
                

        # 위 과정에서 문제가 발생했을 경우 (특정 요소가 해당 상품에 존재하지 않을 경우)
        # 예외 처리 한 다음 누락된 개수 count 추가
        # 이후 continue로 다음 상품
        except:
            omitted_num +=1
            continue
        
        # 상품에서 추출한 요소들을 리스트에 append
        # (단, 이 과정은 with as 구문으로 파일 입출력으로 대체해도 무방함)
        # 저는 이게 편해서...ㅎㅎ
        
        product_num_list.append(product_num)
        product_name_list.append(product_name.text)
        brand_list.append(brand.text)
        year_sold_list.append(year_sold.text)
        like_list.append(like.text)
        rate_list.append(rate.text)
        price_list.append(price.text)
        tag_list.append(tag_str)
        
        # 아까 추출해놓은 이미지 url을 이용하여
        # request.urlretrieve() 메소드를 이용하여 이미지 저장
        # 이때 이미지 파일 이름은 상품에 부여된 고유 번호로 설정
        request.urlretrieve(image_url, f"./data/image/{product_num}.jpg")
        
        # ip 밴 방지
        time.sleep(random.uniform(0,1))

        # 매 반복마다 csv를 새로 만드는 이유
        # 다 끝나고 csv를 만들면, 예상치 못한 오류 (보통은 각 리스트마다 길이가 다른 경우 -> 이 경우 추출이 잘못된거에요)로 인해
        # 뽑긴 뽑았는데 그걸 저장을 못하는 매우 슬픈 일이 발생할 수 있음
        # 따라서, 매 반복마다 csv를 저장하도록 하면 중간에 끊기더라도 이전까지 뽑은 정보들을 살릴 수 있다는 이점이 존재함
        # 다만, 이 방법은 시스템에 매우 큰 부하를 불러일으킨다는 단점이 있음
        
        product_df = pd.DataFrame({"product_num" :product_num_list,
                            #main_category_list,
                            #sub_category_list,
                            "product_name" : product_name_list,
                            "brand" : brand_list,
                            "year_sold" : year_sold_list,
                            "like" : like_list,
                            "rate" : rate_list,
                            "price" : price_list,
                            "tag" : tag_list
                            })
    
        product_df.to_csv(f"./data/{config.file_name}_info.csv")
        

    print()
    print(f"top_sweatshirt : {omitted_num} omitted!")
