# coding: utf-8
from json import loads
from os.path import exists
from pickle import dump, load
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Concert(object):
    def __init__(self, date, session, price, real_name, nick_name, ticket_num, viewer_person, damai_url, target_url,
                 driver_path):
        self.date = date  # 日期序号
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.viewer_person = viewer_person  # 观影人序号优先级
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.driver_path = driver_path  # 浏览器驱动地址
        self.driver = None

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element(by=By.CLASS_NAME, value=name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    def login(self):
        self.driver.get(self.target_url)
        WebDriverWait(self.driver, 10, 0.1).until(EC.title_contains('购物车'))

    def enter_concert(self):
        print("###打开浏览器，进入购物车###")
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--log-level=3')
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        # 登录到具体抢购页面
        self.login()
        self.driver.refresh()

    # 实现购买函数

    def choose_ticket(self):
        print("###进入抢票界面###")
        # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
        while self.driver.title.find('购物车') == -1:
            self.num += 1  # 尝试次数加1

            if self.driver.current_url.find(".m.youzan.com") != -1:
                break

            # 判断页面加载情况 确保页面加载完成
            try:
                WebDriverWait(self.driver, 10, 0.1).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
            except:
                raise Exception(u"***Error: 页面加载超时***")

            # 判断root元素是否存在
            try:
                box = WebDriverWait(self.driver, 1, 0.1).until(
                    EC.presence_of_element_located((By.ID, 'app'))
                )
            except:
                raise Exception(u"***Error: 页面中ID为shop-switch-tools的整体布局元素不存在或加载超时***")

            try:
                buybutton = box.find_element(by=By.CLASS_NAME, value='pay-btn')
                buybutton_text = buybutton.text
            except Exception as e:
                raise Exception(f"***Error: 定位购买按钮失败***: {e}")
            sleep(0.1)
            # 点击购买按钮
            buybutton.click()
            print("###点击购买按钮###")
         # 判断页面加载情况 确保页面加载完成
        try:
            WebDriverWait(self.driver, 10, 0.1).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
        except:
            raise Exception(u"***Error: 页面加载超时***")
        try:
            box = WebDriverWait(self.driver, 1, 0.1).until(
            EC.presence_of_element_located((By.ID, 'app'))
            )
        except:
            raise Exception(u"***Error: 页面中ID为app的整体布局元素不存在或加载超时***")
        sleep(1)
        try:
            buybutton = box.find_element(by=By.CLASS_NAME, value='pay-btn')

        except Exception as e:
            raise Exception(f"***Error: 定位购买按钮失败***: {e}")
        buybutton.click()
        print("###点击提交订单###")
        while self.driver.title.find('确认订单') == -1:
            try:
                WebDriverWait(self.driver, 10, 0.1).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
            except:
                raise Exception(u"***Error: 页面加载超时***")
            try:
                box = WebDriverWait(self.driver, 1, 0.1).until(
                EC.presence_of_element_located((By.ID, 'app'))
                )
            except:
                raise Exception(u"***Error: 页面中ID为app的整体布局元素不存在或加载超时***")
        try:
            buybutton = self.driver.find_element(by=By.CLASS_NAME, value='t-button')

        except Exception as e:
            raise Exception(f"***Error: 定位提交按钮失败***: {e}")
        buybutton.click()

        sleep(2)
            # # 等待弹出框出现
        try:
            buybutton = box.find_element(by=By.CLASS_NAME, value='zan-pay-a__method-name')
        except Exception as e:
            raise Exception(f"***Error: 定位支付宝支付失败***: {e}")
        buybutton.click()
        input("按 Enter 键退出脚本")
        exit()


if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址, 浏览器驱动地址
        con = Concert(config['date'], config['sess'], config['price'], config['real_name'], config['nick_name'],
                      config['ticket_num'], config['viewer_person'], config['damai_url'], config['target_url'],
                      config['driver_path'])
        con.enter_concert()  # 进入到具体抢购页面
    except Exception as e:
        print(e)
        exit(1)

    retry_times = 0

    while True:
        try:
            if retry_times > 50: # 重试次数超过50次重新刷新页面，否则大麦会提示“在此页面停留时间过长”错误
                retry_times = 0
                con.enter_concert()
            con.choose_ticket()
            retry = con.check_order(retry_times > 0)
            if not retry:
                break
            retry_times += 1
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue