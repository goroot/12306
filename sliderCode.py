#coding:utf-8
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#破解滑动验证
#账户名
EMAIL = 'https://github.com/Clay97'
#密码
PASSWORD = 'https://clay97.github.io/'

def main():
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 20)
    driver.get('https://account.cnblogs.com/signin?returnUrl=https%3A%2F%2Fwww.cnblogs.com%2F')
    print(driver.title)
    # 1、输入用户名与密码，并点击登录
    email = wait.until(EC.presence_of_element_located((By.ID, 'LoginName')))
    password = wait.until(EC.presence_of_element_located((By.ID, 'Password')))
    email.send_keys(EMAIL)
    time.sleep(0.2)
    password.send_keys(PASSWORD)
    time.sleep(2)
    submit = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
    submit.click()
    while(driver.title == '用户登录 - 博客园'):
        time.sleep(3)
        # 2、获取有缺口图片
        image1 = getImage(driver)
        # 3、获取完整图片
        image2 = getFullImage(driver)
        # 4、比对两张图片，获取滑动距离
        distance = get_distance(image1, image2)
        print(distance)
        if distance == None :
            return
        # 5、根据偏移量获取移动轨迹
        tracks = get_track(distance)
        print(tracks)
        # 拖动滑块
        move_to_gap(driver, tracks)

# 截取图片
def cut_image(driver, name):
    #保存页面截图
    driver.save_screenshot(name)
    #获取滑动的图片
    image = driver.find_element_by_class_name('geetest_canvas_bg')
    #获取滑动图片的左 上 右 下的位置
    left = image.location['x']
    top = image.location['y']
    right = left + image.size['width']
    buttom = top + image.size['height']
    image_obj = Image.open(name)
    #截图
    img = image_obj.crop((left, top, right, buttom))
    return img

# 获取有缺口的图片
def getImage(driver):
    #影藏滑块
    js_code = '''
           var x = document.getElementsByClassName("geetest_canvas_slice")[0].style.display = "none";
       '''
    driver.execute_script(js_code)
    image = cut_image(driver,'img01.png')
    return image

#获得完整的图片
def getFullImage(driver):
    #显示完整的图片
    js = '''
                var x = document.getElementsByClassName("geetest_canvas_fullbg")[0].style.display = "block";
        '''
    driver.execute_script(js)
    image= cut_image(driver,'img02.png')
    return image

def get_distance(image1, image2):
    # 比较的起始位置，从小滑块右侧开始比较
    start = 55
    # 像素差
    num = 60
    for x in range(start, image1.size[0]):
        for y in range(image1.size[1]):
            # 获取image1完整图片每一个坐标的像素点
            rgb1 = image1.load()[x, y]

            # 获取image2缺口图片每一个坐标的像素点
            rgb2 = image2.load()[x, y]
            r = abs(rgb1[0] - rgb2[0])
            g = abs(rgb1[1] - rgb2[1])
            b = abs(rgb1[2] - rgb2[2])
            if not (r < num and g < num and b < num):
                # 有误差 -7 像素
                return x - 7

def get_track(distance):
    # 移动轨迹
    track = []
    # 当前位移
    curremt = 0
    # 减速阈值
    mid = distance* 3 / 5
    #计算间隔
    t = 0.2
    # 初速度
    v = 0

    while curremt < distance:
        if curremt <mid:
            # 加速度 +6
            a = 6
        else:
            #加速度 -7
            a = -8
        # 初速度 v0
        v0 = v
        # 当前速度 v = v0 + at
        v = v0 +a * t
        #移动距离 x = v0t + 1/2 * a * t * t
        move = v0 * t+1/2 * a * t * t
        #当前位移
        curremt +=move
        #加入轨迹
        track.append(round(move))
    return track

def move_to_gap(driver, tracks):
    slider = driver.find_element_by_class_name('geetest_slider_button')
    # 为了观察移动轨迹,显示滑块
    js_code = '''
               var x = document.getElementsByClassName("geetest_canvas_slice")[0].style.display = "block";
           '''
    driver.execute_script(js_code)
    time.sleep(2)
    # 点击摁住滑动按钮
    ActionChains(driver).click_and_hold(slider).perform()
    # 根据轨迹移动滑块
    for x in tracks:
        ActionChains(driver).move_by_offset(xoffset=x,yoffset=0).perform()
    # 释放滑块
    ActionChains(driver).release().perform()
    time.sleep(6)

if __name__ == '__main__':
    main()
