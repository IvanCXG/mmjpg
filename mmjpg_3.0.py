# coding=utf-8
import re
import urllib.request
from bs4 import BeautifulSoup as bf
import os
import requests
import random
import logging
import threading

class MMJPG(object):
    #获取页面内容
    def get_html(self,url):
        # #模拟浏览器请求
        user_agent = [
            'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30',
            'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
            'Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)'
        ]
        header = {"User-Agent": random.choice(user_agent)}
        try:
            request = urllib.request.Request(url,headers=header)
            #发送请求，获取服务器响应回来的html页面
            html = urllib.request.urlopen(request, timeout=60).read()
            #html = urllib.urlopen(request).read()
            #使用beautifulSoup处理的html页面，类似dom
        except  Exception as e:
            print( "网络链接:" + url + " 错误" , logging.ERROR)
            return None
        except  BaseException as Argument:
            print( "打开连接:" + url + "异常，原因："+str(Argument) , logging.ERROR)
            return None
        html_text = html.decode('utf-8')
        return html_text

    #计算每个分类对应的tag的名称，如xiaoqingxin，用作文件夹名
    def get_tag(self,html_text):
        tag_reg = re.compile(r'<a href="http://www.mmjpg.com/tag/(\w+)">')
        tag1 = re.findall(tag_reg,html_text)
        tag = list(set(tag1))
        tag.sort(key=str.lower)#将tag从a-z进行升序排列
        return tag

    #判断文件夹路径是否存在，如不存在则创建，如存在则忽略
    def save_path(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            print(path + ' 文件夹已存在！')

    #判断每个分类有多少个page
    def get_page(self,html_text):
        page_reg = re.compile(r'class="info">[\u4e00-\u9fa5](\d+)[\u4e00-\u9fa5]')
        PN = re.findall(page_reg,html_text)
        page_num = int(PN[0])
        return page_num

    #下载文件并判断路径和文件是否存在！

    #设置线程全局锁
    thread_lock = threading.BoundedSemaphore(value=20)
    def download(self,img_link,tuce_path,img_name):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36',
            'Referer': url}
        url_response = requests.get(img_link, headers=header)
        img = url_response.content
        if not os.path.isfile(tuce_path + '/%s' % img_name):
            with open(tuce_path + '/%s' % img_name, 'wb') as f:
                f.write(img)
                print(img_name + '  已下载！')
                #释放现线程
                self.thread_lock.release()
        else:
            print(img_name + '  已存在！')
            # 释放现线程
            self.thread_lock.release()


if __name__ == '__main__':
    url = 'http://www.mmjpg.com'
    mj = MMJPG()#创建一个实例对象
    html_text = mj.get_html(url)#获取首页hmtl中的text
    #print(html_text)
    tag = mj.get_tag(html_text)#获取首页中包含的tag种类
    tag_num = len(tag)#获取tag个数

    root_path = 'E:/mmjpg.com'
    mj.save_path(root_path)#创建根目录路径

    for i in range(0,tag_num):
        tag_url = url + '/tag/' + tag[i]
        #print(tag_url)
        tag_path = root_path+'/'+tag[i]
        #print(tag_path)
        mj.save_path(tag_path)
        tag_html_text = mj.get_html(tag_url)
        tag_page_num = mj.get_page(tag_html_text)

        #print(tag_html_text)
        for j in range(1,tag_page_num+1):
            if j == 1:
                tag_page_url = tag_url
            if j>1:
                tag_page_url = tag_url+'/%d' %j
            #print(tag_page_url)
            #判断每个page中有多少个图册，并获取对应图册的名称，用作保存路径的名称
            each_page_html = mj.get_html(tag_page_url)
            each_page_reg = re.compile(r'height="330" alt="(.+?)"')
            each_tuce_name = re.findall(each_page_reg,each_page_html)
            each_tuce_num = len(each_tuce_name)

            #获取每个图册中有多少个图像，并获取每个图像买的名称，并存储在对应的路径中
            imgs_reg = re.compile(r'<li><a href="(http://www.mmjpg.com/mm/\d+)" target="_blank">')
            imgs_url = re.findall(imgs_reg,each_page_html)
            #print(imgs_url)
            each_page_tuce_num = (len(imgs_url))
            #imgs_html = mj.get_html(imgs_url)
            for l in range(0,each_page_tuce_num):
                tuce_img_html_text = mj.get_html(imgs_url[l])
                tuce_img_num_reg = re.compile(r'(\d+)</a><em class=')
                tuce_img_num1 = re.findall(tuce_img_num_reg,tuce_img_html_text)
                tuce_img_num = int(tuce_img_num1[0])
                print(tuce_img_num)
                tuce_path = tag_path + '/' + each_tuce_name[l]
                # print(tuce_path)
                mj.save_path(tuce_path)
                for m in range(1,tuce_img_num+1):
                    if m == 1:
                        each_img_url = imgs_url[l]
                    if m>1:
                        each_img_url = imgs_url[l]+'/%d' %m
                    #print(each_img_url)
                    img_html_text = mj.get_html(each_img_url)
                    img_reg = re.compile(r'data-img="(.+?)"')
                    img_real_link = re.findall(img_reg,img_html_text)
                    #jpg_name1 = img_real_link[7:]
                    #jpg_name = jpg_name1[0]
                    img_link = img_real_link[0]
                    img_name1 = img_link.replace('/','_')
                    img_name = img_name1[7:]

                    #获取线程
                    mj.thread_lock.acquire()
                    t = threading.Thread(target=mj.download,args=(img_link,tuce_path,img_name))
                    #启动线程
                    t.start()