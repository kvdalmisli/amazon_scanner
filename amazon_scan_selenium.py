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
import telegram
from telegram import Bot
import asyncio
import ssl
import certifi
from telegram import Bot
from telegram.request import HTTPXRequest
import os

TOKEN = '7213780372:AAE80L2VoTM9jIkAjKwRljJl3CNOena0n9w'
OWNER_USER_ID = 5981525468  # Buraya kendi Telegram kullanıcı ID'nizi girin
CHAT_ID = '5981525468'
async def send_telegram_message(message):


    # HTTPX tabanlı bir istek nesnesi oluştur
    request = HTTPXRequest()

    # Botu oluştur
    bot = Bot(token=TOKEN, request=request)
    await bot.send_message(chat_id=CHAT_ID,text=message)


async def scan_on_amazon(urun_ismi,driver,productcode):
    driver.get("https://www.amazon.com.tr/dp/" + productcode)
    time.sleep(5)
    wait = WebDriverWait(driver, 10)
    #title = driver.find_element(By.XPATH, "//div[@id='titleSection']").text
    #print(title)
    #featured_price = driver.find_element(By.XPATH, "//div[@id='corePriceDisplay_desktop_feature_div']/.//span[@class='a-price-whole']").text
    #print("Amazondaki ilk fiyat" + featured_price)
    kampanya = ' '
    #amazon_satici_fiyati = 0
    driver.get("https://www.amazon.com.tr/dp/" + productcode + "?m=A1UNQM1SR2CHM")
    time.sleep(1)
    wait = WebDriverWait(driver, 20)
    try:
        amazon_satici_fiyati = driver.find_element(By.XPATH, "//div[@id='corePriceDisplay_desktop_feature_div']/.//span[@class='a-price-whole']").text
        print("Amazon saticisinin fiyati " + amazon_satici_fiyati + " TL")
    except NoSuchElementException as e:
        amazon_satici_fiyati = 0
        print("Amazon satıcısı satmıyor.")

    try:
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='promoPriceBlockMessage_feature_div']/.//span[@class='promoPriceBlockMessage']")))
        #kampanya= driver.find_element(By.XPATH, "//div[@id='promoPriceBlockMessage_feature_div']/.//label[contains(text(),'Kampanya')]/following-sibling::span").text
        kampanya = element.text
        print(kampanya)
        if amazon_satici_fiyati != 0:
            await send_telegram_message(productcode + " " + urun_ismi + " fiyatı " + str(amazon_satici_fiyati) + " TL  Kampanya var.")
    except (NoSuchElementException,TimeoutException) as e:
        print(str(productcode) + "Kampanya bulunamadi.")
        if amazon_satici_fiyati != 0:
            await send_telegram_message(productcode + " " + urun_ismi + " fiyatı " + str(amazon_satici_fiyati) + " TL Kampanya yok.")
    #return featured_price, kampanya, amazon_satici_fiyati,productcode
    return kampanya, productcode
#opts = FirefoxOptions()
#opts.add_argument("--headless")
#driver =  webdriver.Firefox(options=opts)
output_file = "amazon_scan_results.csv"
urun_cesidi = 0
with open(output_file, 'w', encoding = 'utf-8-sig' , newline='') as result_file:
    header = ['Tarih','ürün_ismi', 'Amazondaki_ilk_fiyat','Amazon_satici_fiyati','Kampanya Bilgisi']
    writer = csv.writer(result_file)
    writer.writerow(header)
    with open('product_codes.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        tarih = datetime.datetime.now()
        print(tarih)
        asyncio.run(send_telegram_message(str(tarih) + "inde script calistirildi..."))
        for row in reader:
            urun_cesidi += 1
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            driver =  webdriver.Firefox(options=opts)
            time.sleep(2)
            urun_ismi = row['Urun']
            urun_kodu = row['Farmazon Kodu']
            amazon_asin = row['Amazon ASIN']
            #amazon_fiyati,kampanya,amazon_seller_price,productcode = asyncio.run(scan_on_amazon(driver,amazon_asin))
            kampanya,productcode = asyncio.run(scan_on_amazon(urun_ismi,driver,amazon_asin))
            time.sleep(3)
            os.system("pkill -f firefox")
            #data = [tarih,urun_ismi,amazon_fiyati,amazon_seller_price,kampanya]
            #writer.writerow(data)
    tarih = datetime.datetime.now()

    asyncio.run(send_telegram_message('Toplam ' + str(urun_cesidi) + ' adet ürün tarandı.' + str(tarih) + "inde script tamamlandi..." ))