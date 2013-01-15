#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from mogu.login import login_required
from mogu.models.model import Subscribe, ContentClass, User
from google.appengine.ext import db
from tools.page import Page
from tools.util import getPageing, getLevelByCode
from google.appengine.api import memcache

__author__ = u'王健'

class SubscribeInfo(Page):
    @login_required
    def get(self):
        searchType = self.request.get('searchType')#'searchType‘不存在是返回的不是None，而是''空字符
        page_id = self.request.get('page_id')#'searchType‘不存在是返回的不是None，而是''空字符
#        template_values = {'searchType':searchType,}
        self.redirect("/subscribeList/%s?searchType=%s" %(page_id,searchType))
#        self.render('html/subscribeManage/subscribeInfo.html',template_values)#本地上运行用这个
    @login_required
    def post(self):
        searchType = self.request.get('searchType')
        page_id = self.request.get('page_id')
        self.redirect("/subscribeList/%s?searchType=%s" %(page_id,searchType))

class SubscribeList(Page):
    @login_required
    def get(self,page):
        searchType = self.request.get('searchType')#'searchType‘不存在是返回的不是None，而是''空字符
        father=self.request.get('father')
        subscribes=Subscribe.all()
        if father:
            subscribes=subscribes.filter('father =',father)
        if searchType=='':
            searchType=self.request.get('userName')
            subscribes=subscribes.filter('userName =',searchType).order('__key__')
        elif searchType=='userName':
            subscribes=subscribes.filter('father =','').order(searchType).order('__key__')
            searchType=''
        else:
            if not User.get_by_keyname('u'+searchType):
                searchType=''
            if father:
                subscribes=subscribes.filter('userName =',searchType).order('__key__')
            else:
                subscribes=subscribes.filter('level =','1').filter('userName =',searchType).order('__key__')
#        index=0 if page=="" else int(page)
#        if subscribes and type(subscribes) is not list:
#            subscribes = subscribes.fetch(16,index*16)
#        prevpage,nextpage=getPageing(len(subscribes), index)
        template_values = {'subscribes':subscribes,'searchType':searchType,'father':father}
        self.render('template/subscribe/subscribeInfo.html',template_values)#本地上运行用这个
#        self.render('html/subscribeManage/subscribeList.html',template_values)#本地上运行用这个


class SubscribeAdd(Page):
    @login_required
    def get(self):
        users = db.GqlQuery("SELECT * FROM User ORDER BY userName ASC")
        template_values = {'users':users,}
        self.render('template/subscribe/subscribeAdd.html',template_values)#本地上运行用这个
#        self.render('html/subscribeManage/subscribeAdd.html',template_values)#本地上运行用这个
    @login_required
    def post(self):
        subscribeType=self.request.get('subscribeType')
        if not subscribeType:
            self.redirect(self.request.environ['HTTP_REFERER'])
            return
        userName  = self.request.get('userName')
        maincode = self.request.get('maincode')
        code = self.request.get('code')
        greeting = Subscribe.get_by_key_name(code+'u'+userName)
        if not greeting:
            greeting = Subscribe(key_name=code+'u'+userName)
        greeting.maincode = maincode
        greeting.userName = userName
        if code.rfind('-')>-1:
            greeting.father = code[0:code.rfind('-')]
        else:
            greeting.father =''
        greeting.level = getLevelByCode(code)
        greeting.subscribeType = self.request.get('subscribeType')
        greeting.code = code
        greeting.status = '1'
        greeting.put()
        userSubChange(userName,code,greeting.subscribeType,True)
        self.redirect('/subscribeList/0?searchType=%s&father=%s' %(userName,greeting.father))

class SubscribeStatus(Page):
    @login_required
    def get(self):
        code = self.request.get('code')
        userName = self.request.get('userName')
        subscribes = Subscribe.all().filter('code =',code).filter('userName =',userName).fetch(1)
        if subscribes:
            for subscribe in subscribes:
                if subscribe.status=='1':
                    subscribe.status = '0'
                    subscribe.put()
                    slist=findChildrenSubscribe(userName,code)
                    for s in slist:
                        s.status='0'
                        s.put()
                    userSubChange(userName,code,'1',False)
                else:
                    subscribe.status = '1'
                    subscribe.put()
                    userSubChange(userName,code,'1',True)
        self.redirect('/subscribeList/0?searchType=%s' %userName)

class UserSubscribeAdd(Page):
    @login_required
    def get(self):
        userName = self.request.get('userName')
        father = self.request.get('father')
        code=self.request.get('code')
        if father:
            if code:
                contents=ContentClass.all().filter('father =',father).filter('status =','1').filter('__key__ >=',ContentClass(key_name=code).key()).filter('__key__ <=',ContentClass(key_name=code+u"\ufffd").key()).order('__key__')
            else:
                contents=ContentClass.all().filter('father =',father).filter('status =','1').order('__key__')
        else:
            if code:
                contents=ContentClass.all().filter('__key__ >=',ContentClass(key_name=code).key()).filter('__key__ <=',ContentClass(key_name=code+u"\ufffd").key()).filter('level =','1').filter('status =','1').order('__key__')
            else:
                contents = ContentClass.all().filter('level =','1').filter('status =','1').order('__key__')
        userMap=getUserSub(userName)
        template_values = {'userName':userName,"contents":contents,'father':father,'code':code,'userSub':userMap or {}}
        self.render('template/subscribe/userSubscribeAdd.html',template_values)#本地上运行用这个
#        self.render('html/subscribeManage/userSubscribeAdd.html',template_values)#本地上运行用这个

class SubscribeDelete(Page):
    @login_required
    def get(self):
        code = self.request.get('code')
        userName = self.request.get('userName')
        subscribe = Subscribe.get_by_key_name(code+'u'+userName)
        if subscribe:
            subscribe.delete()
            db.delete(findChildrenSubscribe(userName,code))
            userSubChange(userName,code,'1',False)
        self.redirect('/subscribeList/0?searchType=%s' %userName)

def findChildrenSubscribe(userName,code):
    return Subscribe.all().filter('userName =',userName).filter('code >=',code+'-').filter('code <=',code+u"-\ufffd")

def initUserSub(userName):
    memcache.delete_multi(userName+'a')
    userMap={}
    for sub in Subscribe.all().filter('userName =',userName).filter('status =','1'):
        userMap[sub.code]=sub.subscribeType
    memcache.set(userName+'a',userMap,36000)
def getUserSub(userName):
    userMap=memcache.get(userName+'a')
    if not userMap:
        initUserSub(userName)
    return memcache.get(userName+'a')
def userSubChange(userName,code,type,status=True):
    userMap=memcache.get(userName+'a')
    if not userMap:
        initUserSub(userName)
        return
    else:
        if status:
            userMap[code]=type
        else:
            k=code
            for ke in userMap.keys():
                if ke.find(k)==0:
                    del userMap[ke]
        memcache.set(userName+'a',userMap,36000)



