#coding=utf-8
#
import json

__author__ = u'王健'

import os
from google.appengine.ext import db

class Users(db.Model):
    name=db.StringProperty()#本站昵称
    username=db.EmailProperty()
    password=db.StringProperty()
    auth=db.StringProperty()

class Images(db.Model):
    photoCode = db.StringProperty(multiline=True)#//图片编码
    name = db.StringProperty(multiline=True)
    mime = db.StringProperty(multiline=True)
    size = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    description = db.StringProperty(multiline=True)
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    filetype=db.StringProperty(multiline=True)

    bf = db.BlobProperty() #binary file

    ##另一个应用的id
    otherId=db.IntegerProperty()
    isDown=db.BooleanProperty()
    updataTime=db.DateTimeProperty()
    appname=db.StringProperty()

    @property
    def id(self):
        return str(self.key().id())

    @property
    def imgurl(self):
        return "http://%s/image/%s" %(os.environ['HTTP_HOST'],self.key().id())

#记录最新的用户名
class UserNameNumber(db.Model):
    userName=db.IntegerProperty(indexed=False)

class User(db.Model): #//用户表
    userName = db.StringProperty() #//用户名
    passWord = db.StringProperty()  #//密码
    trueName = db.StringProperty()  #//姓名
    tele = db.StringProperty()      #//电话号码
    mobile = db.StringProperty()    #//手机
    date = db.DateTimeProperty(auto_now_add=True)  #//注册时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True) #//最后一次修改时间
    appData=db.TextProperty()#记录应用的必要数据gae端事json格式，传输时用urlprams的方式传输

    __appinit=False
    __appParms={}
    def getParms(self):
        if not self.__appinit:
            self.__appParms=json.loads(self.appData or '{}')
            self.__appinit=True
        return self.__appParms
    def put(self, **kwargs):
        if self.__appinit:
            self.appData=json.dumps(self.__appParms)
        super(User,self).put(**kwargs)

    @classmethod
    def get_by_keyname(cls, key_names, parent=None, **kwargs):
        n='u'+str(len(key_names)-1)+key_names
        u=cls.get_by_key_name(key_names=n,parent=parent,**kwargs)
        if not u:
            return cls.get_by_key_name(key_names=key_names,parent=parent,**kwargs)
        else:
            return u



class UserUpdate(db.Model):
    lastUpdateTime=db.DateTimeProperty(indexed=False)
    updateContent=db.StringListProperty(indexed=False)
    updateSubscribe=db.StringListProperty(indexed=False)

    @classmethod
    def get_by_userName(cls,username):
        us='u'+username
        u=cls.get_by_key_name(us)
        if not u:
            user=User.get_by_keyname(us)
            if user:
                u=cls(key_name=us)

        return u

class Subscribe(db.Model):#//用户订阅表,其它层
    userName = db.StringProperty()#//订阅人
    maincode  = db.StringProperty() #存第一级内容编号，后面的表都加上
    code = db.StringProperty()#//订阅内容编号
    father = db.StringProperty()#//上一级内容编号
    level = db.StringProperty()#// 级别 2-5
    subscribeType = db.StringProperty()#//0 表示下面的全要。  1 表示下面的另外订阅说明。
    status=db.StringProperty()#//0 取消订阅了，还没真正物理删除。1 订阅
    updataTime=db.DateTimeProperty(auto_now=True)

    def put(self, **kwargs):
        super(Subscribe,self).put(**kwargs)
        if self.userName:
            userUpdate=UserUpdate.get_by_userName(self.userName)
            if userUpdate:
                userUpdate.updateSubscribe.append(self.key().name())
                userUpdate.lastUpdateTime=self.updataTime
                userUpdate.put()

class ContentClass(db.Model):       #咨询表（包含级别和内容）
    maincode  = db.StringProperty() #存第一级内容编号，后面的表都加上
    content = db.TextProperty()   #内容
    title = db.StringProperty(indexed=False,default='')   #抬头标题
    father = db.StringProperty(default='')    #//父级内容编码，当父级为空时level为0
    level= db.StringProperty()      #//级别 从上到下分别0、1-5，level为0是唯一
    lastUpdateTime = db.DateTimeProperty(auto_now=True)  #//上次更新时间
    updateSpanTime = db.StringProperty(indexed=False,default='')  #//更新间隔时间
    replyType = db.StringProperty(indexed=False) #//回复类别 1：文本回复  2、单选选择回复 3、多选选择回复
    status = db.StringProperty()       #//状态
    userName=db.StringProperty(default='')

    def put(self, **kwargs):
        super(ContentClass,self).put(**kwargs)
        if self.userName:
            userUpdate=UserUpdate.get_by_userName(self.userName)
            if userUpdate:
                userUpdate.updateContent.append(self.key().name())
                userUpdate.lastUpdateTime=self.lastUpdateTime
                userUpdate.put()







