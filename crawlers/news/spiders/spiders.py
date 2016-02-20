# coding=utf-8

import scrapy

import urllib
import json
import time
import re
import os

from scrapy.spiders import CrawlSpider, Spider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from crawlers.news.items import NewsItem, SinaCaptchaItem, SinaStarItem

from datetime import datetime
from PIL import Image

from tools.tools import CaptchaHacker
from base.model import Star

cur_dir_path = os.path.dirname(__file__)


class SinaBaseSpider(Spider):

    allowed_domains = ['weibo.com',
                       'weibo.cn']

    captcha_try_count = 0

    has_saved_cookie_flag = False

    def __init__(self):
        super(SinaBaseSpider, self).__init__()
        self.sina_cookies = json.load(open(os.path.join(cur_dir_path, 'sina_cookie.json')))
        self.try_count = 0

    def login(self):
        return scrapy.Request('http://login.weibo.cn/login/', callback=self.parse_login_page, dont_filter=True)

    def parse_login_page(self, response):

        form = response.xpath("//form")

        password = form.xpath(".//input[contains(@name, 'password')]/@name").extract_first()

        captcha_url = response.xpath("//img[contains(@src, 'captcha')]/@src").extract_first()

        captchas = self.get_captcha(captcha_url)

        if len(captchas) < 4:

            SinaBaseSpider.captcha_try_count += 1

            # 如果识别算法失败超过 3 次, 则人工识别

            if SinaBaseSpider.captcha_try_count > 3:
                Image.open(urllib.urlopen(captcha_url)).convert('RGB').show()
                captchas = raw_input()
            else:
                time.sleep(3)
                return self.login()

        return scrapy.FormRequest.from_response(
            response,
            formdata={'mobile': 'ceruleanwang@163.com', password: '1597538426b', 'code': captchas},
            callback=self.parse_login_result
        )

    def parse_login_result(self, response):
        return True if response.url.find('PHPSESSID') > -1 else False

    def save_cookies_if_need(self, response):
        if SinaBaseSpider.has_saved_cookie_flag:
            return

        cookies = response.request.headers['Cookie'].split(';')
        cookies_dic = dict()

        for cookie in cookies:
            key = cookie.split('=')[0]
            value = cookie.split('=')[1]
            cookies_dic[key] = value

        if self.sina_cookies != cookies_dic:
            json.dump(cookies_dic, open(os.path.join(cur_dir_path, 'sina_cookie.json'), 'w'))
            SinaBaseSpider.has_saved_cookie_flag = True

    @staticmethod
    def get_captcha(captcha_url):

        captcha_images = []

        captchas = ""

        if captcha_url:
            captcha_images = CaptchaHacker.slice(Image.open(urllib.urlopen(captcha_url)).convert('RGB'))

        if captcha_images:
            captchas = CaptchaHacker.recognize(captcha_images)

        return captchas


class SinaFeedSpider(SinaBaseSpider):

    name = 'sina_feed'

    parms = {
        'profile_ftype': '1',
        'is_all': '1'
    }

    def generate_requests(self):
        stars = Star.objects()

        requests = []

        for star in stars:
            requests.append(scrapy.FormRequest(star.weibo_url,
                                               cookies=self.sina_cookies,
                                               method='GET',
                                               formdata=SinaFeedSpider.parms,
                                               callback=self.parse_feed))

        return requests

    def start_requests(self):
        return self.generate_requests()

    def parse_login_result(self, response):
        if not super(SinaFeedSpider, self).parse_login_result(response):
            return self.login()

        return self.generate_requests()

    def parse_feed(self, response):
        if response.url.find('passport') > -1:
            yield self.login()

        self.save_cookies_if_need(response)

        selector = self.get_feed_selector(response, 'WB_feed WB_feed_profile')

        if not selector:
            yield self.login()

        feed_selectors = selector.xpath(".//div[@class='WB_detail']")

        for feed_selector in feed_selectors:
            feed_url = "http://weibo.com" + feed_selector.xpath(".//div[@class='WB_from S_txt2']/a[1]/@href").extract_first()
            feed_type = 1
            feed_source = "微博"
            feed_title = "".join(feed_selector.xpath(".//div[@class='WB_text W_f14']/text()").extract())
            feed_image_urls = feed_selector.xpath(".//img[contains(@src, 'square')]/@src").extract()
            feed_article = ""
            feed_create_date = feed_selector.xpath(".//div[@class='WB_from S_txt2']/a[1]/@title").extract_first() + ":00"

            square_image_count = len(feed_image_urls)

            for index in xrange(square_image_count):
                feed_image_urls.append(feed_image_urls[index].replace("square", "bmiddle"))

            feed_title = feed_title.lstrip().rstrip()

            feed_item_loder = ItemLoader(item=NewsItem(), response=response)
            feed_item_loder.add_value('url', feed_url)
            feed_item_loder.add_value('type', feed_type)
            feed_item_loder.add_value('source', feed_source)
            feed_item_loder.add_value('title', feed_title)
            feed_item_loder.add_value('article', feed_article)
            feed_item_loder.add_value('create_date', datetime.strptime(feed_create_date, "%Y-%m-%d %H:%M:%S"))
            feed_item_loder.add_value('image_urls', feed_image_urls)

            item = feed_item_loder.load_item()

            yield item

    @staticmethod
    def get_feed_selector(response, content):
        scripts = response.xpath("//script").extract()

        for script in scripts:
            target_script = script
            if target_script.find(content) > -1:
                target_script = re.sub(r"^<script>FM.view\(", "", target_script)
                target_script = re.sub(r"\)</script>", "", target_script)

                model = json.loads(target_script)

                selector = scrapy.Selector(text=model['html'])

                return selector


class SinaStarSpider(SinaBaseSpider):

    name = 'sina_star'

    def start_search_requst(self, key_word):
        return scrapy.FormRequest('http://s.weibo.com/user/' + key_word,
                                  method='GET',
                                  cookies=self.sina_cookies,
                                  formdata={'gender': 'women', 'auth': 'per_vip'},
                                  callback=self.parse_star_result)

    def start_requests(self):
        return [self.start_search_requst('人气偶像团体SNH48成员')]

    def parse_login_result(self, response):
        if not super(SinaStarSpider, self).parse_login_result(response):
            return self.login()

        return self.start_search_requst('人气偶像团体SNH48成员')

    def parse_star_result(self, response):
        if response.url.find('passport') > -1:
            yield self.login()

        self.save_cookies_if_need(response)

        selector = self.get_star_selector(response, 'pl_personlist')

        star_selectors = selector.xpath("//div[@class='list_person clearfix']")

        items = []

        for star_selector in star_selectors:
            star_name = star_selector.xpath(".//a[@class='W_texta W_fb']/@title").extract_first()
            star_avatar_url = star_selector.xpath(".//div[@class='person_pic']/a/img/@src").extract_first()
            star_weibo_url = star_selector.xpath(".//a[@class='W_texta W_fb']/@href").extract_first()

            print star_name, star_avatar_url

            star_item_loader = ItemLoader(item=SinaStarItem(), response=response)
            star_item_loader.add_value('name', star_name)
            star_item_loader.add_value('avatar_url', star_avatar_url)
            star_item_loader.add_value('weibo_url', star_weibo_url)

            items.append(star_item_loader.load_item())

        for item in items:
            yield item

        next_selector = self.get_star_selector(response, 'WB_cardwrap S_bg2 relative')

        next_url = next_selector.xpath("//a[contains(@class, 'page next')]/@href").extract_first()

        if next_url:
            yield scrapy.Request('http://s.weibo.com' + next_url, callback=self.parse_star_result)

    @staticmethod
    def get_star_selector(response, content):

        scripts = response.xpath("//script").extract()

        for script in scripts:
            target_script = script
            if target_script.find(content) > -1:
                target_script = re.sub(r"^<script>STK && STK.pageletM && STK.pageletM.view\(", "", target_script)
                target_script = re.sub(r"\)</script>$", "", target_script)

                model = json.loads(target_script)

                selector = scrapy.Selector(text=model['html'])

                return selector


class SibaNewsSpider(CrawlSpider):

    name = 'siba_news'
    allowed_domains = ['snh48.com']
    start_urls = ['http://www.snh48.com/html/allnews/']

    parse_regex = '(gongyan|woshouhui|cd|zixun|activity)/201[3-6]/(\d){4}/(.)+'
    follow_regex = '[1].html'

    parse_rule = Rule(
        LinkExtractor(allow=[parse_regex]),
        callback='parse_news'
    )

    follow_rule = Rule(
        LinkExtractor(allow=[follow_regex])
    )

    rules = [parse_rule, follow_rule]

    def parse_news(self, response):
        xpaths = response.xpath("//div[contains(@class, 's_new_detail')]")
        target = xpaths[0] if len(xpaths) > 0 else None

        if target:
            news_url = response.url
            news_type = 0
            news_title = target.xpath(".//div[@class='s_nt_txt']/text()").extract_first()
            news_article = target.xpath(".//div[@class='s_new_con']/div/span/span/text()").extract()
            news_image_urls = target.xpath(".//img[contains(@src, 'newsimg')]/@src").extract()

            news_create_year = news_url.split('/')[-3]
            news_create_month = news_url.split('/')[-2][0:2]
            news_create_day = news_url.split('/')[-2][2:4]

            news_create_date = news_create_year + '-' + news_create_month + '-' + news_create_day + ' ' + '00:00:00'

            news_title = news_title.strip()

            articles = []

            for article in news_article:
                articles.append(article.strip())

            siba_item_loder = ItemLoader(item=NewsItem(), response=response)
            siba_item_loder.add_value('url', news_url)
            siba_item_loder.add_value('type', news_type)
            siba_item_loder.add_value('source', "官网")
            siba_item_loder.add_value('title', news_title)
            siba_item_loder.add_value('article', articles)
            siba_item_loder.add_value('create_date', datetime.strptime(news_create_date, "%Y-%m-%d %H:%M:%S"))
            siba_item_loder.add_value('image_urls', news_image_urls)

            return siba_item_loder.load_item()


class CaptchaSpider(Spider):
    name = 'sina_captcha'
    allowed_domains = ['weibo.cn']
    start_urls = ["http://login.weibo.cn/login/"]

    request_count = 0

    def parse(self, response):
        return self.parse_login_page(response)

    def parse_login_page(self, response):

        captcha_item_loader = ItemLoader(item=SinaCaptchaItem(), response=response)

        captcha_image_url = response.xpath("//img[contains(@src, 'captcha')]/@src").extract_first()

        captcha_item_loader.add_value('image_urls', captcha_image_url)

        yield captcha_item_loader.load_item()

        CaptchaSpider.request_count += 1

        if CaptchaSpider.request_count < 100:
            yield scrapy.Request("http://login.weibo.cn/login/", callback=self.parse, dont_filter=True)
