from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from csv import DictReader
import time
import csv 
from functools import partial
import datetime


def scan_on_amazon(driver,productcode):
    driver.get("https://www.amazon.com.tr/dp/" + productcode)
    title = driver.find_element(By.XPATH, "//div[@id='titleSection']").text
    print(title)
    featured_price = driver.find_element(By.XPATH, "//div[@id='corePriceDisplay_desktop_feature_div']/.//span[@class='a-price-whole']").text
    print("Amazondaki ilk fiyat" + featured_price)
    time.sleep(1)
    kampanya = ' '
    amazon_satici_fiyati = 0
    driver.get("https://www.amazon.com.tr/dp/" + productcode + "?m=A1UNQM1SR2CHM")
    time.sleep(1)
    wait = WebDriverWait(driver, 10)
    try:
        amazon_satici_fiyati = driver.find_element(By.XPATH, "//div[@id='corePriceDisplay_desktop_feature_div']/.//span[@class='a-price-whole']").text
        print("Amazon saticisinin fiyati " + str(amazon_satici_fiyati))
    except NoSuchElementException as e:
        print("Amazon satıcısı satmıyor.")
        
    try:
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='promoPriceBlockMessage_feature_div']/.//span[@class='promoPriceBlockMessage']")))
        #kampanya= driver.find_element(By.XPATH, "//div[@id='promoPriceBlockMessage_feature_div']/.//label[contains(text(),'Kampanya')]/following-sibling::span").text
        kampanya = element.text
        print(kampanya)
        
    except (NoSuchElementException,TimeoutException) as e:
        print("Kampanya bulunamadi.")
        
    return featured_price, kampanya, amazon_satici_fiyati,title

opts = FirefoxOptions()   
driver =  webdriver.Firefox()
output_file = "amazon_scan_results.csv"

with open(output_file, 'w', encoding = 'utf-8-sig' , newline='') as result_file:
        header = ['Tarih','ürün_ismi', 'Amazondaki_ilk_fiyat','Amazon_satici_fiyati','Kampanya Bilgisi']
        writer = csv.writer(result_file)
        writer.writerow(header)
        while True:
            with open('product_codes.csv', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                tarih = datetime.datetime.now()
                print(tarih)
                for row in reader:
                    urun_ismi = row['Urun']
                    urun_kodu = row['Farmazon Kodu']
                    amazon_asin = row['Amazon ASIN']
                    amazon_fiyati,kampanya,amazon_seller_price,title = scan_on_amazon(driver,amazon_asin)
                    data = [tarih,urun_ismi,amazon_fiyati,amazon_seller_price,kampanya]
                    writer.writerow(data)
                time.sleep(20)
