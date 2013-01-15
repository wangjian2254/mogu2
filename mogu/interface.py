#coding=utf-8
#author:u'王健'
#Date: 11-12-12
#Time: 下午7:31
import logging
from xml.dom.minidom import Document
from mogu.content import findChildNodes
from mogu.models.model import Subscribe, ContentClass, UserUpdate, User
from setting import WEBURL, AppPhoneVerson, AppPhoneUri
from tools.page import Page
from tools.util import checkUser

__author__ = u'王健'

def infoallxmldic(contents,xml=None,datas=None,delete=None):
    if not xml:
        xml=Document()
        datas=xml.createElement('datas')
        #datas.setAttribute('time','%s' %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
#        datas.setAttribute('type','infoall')
        xml.appendChild(datas)
    for c in contents:
        if not c:
            continue
        data=xml.createElement('data')
        if not delete and c.status=='1':
            data.setAttribute('code',c.key().name() or '')
            data.setAttribute('father',c.father or '')
            if c.title:
                data.setAttribute('title',c.title or '')
            if c.updateSpanTime:
                data.setAttribute('updateSpanTime',c.updateSpanTime or '')
            if c.replyType:
                data.setAttribute('replyType',c.replyType or '')
            data.setAttribute('maincode',c.maincode or '')
            data.setAttribute('level',c.level or '')
            data.appendChild(xml.createTextNode(c.content or ''))
            data.setAttribute('status',c.status or '')
            data.setAttribute('lastUpdateTime',str(c.lastUpdateTime) or '')
        else:
            if type(c) is str or type(c) is unicode:
                data.setAttribute('code',c)
            else:
                data.setAttribute('code',c.key().name() or '')
            data.setAttribute('status','0' or '')
        datas.appendChild(data)
    return (xml,datas)

def userAppData(userName,datas):
    str='&'
    user=User.get_by_keyname('u'+userName)
    appmap=user.getParms()
    ######
    #把用户跟应用相关的参数，比如微博的token和socket都按照urlparms的格式组装好
    #
    #
    #
    #另外还缺少一个写应用参数的接口
    ######
    for k in appmap.keys():
        for p in appmap[k].keys():
            str+="%s=%s&" %(p,appmap[k][p])
    if datas:
        datas.setAttribute('appdata',str[:-1])
class ChangeAppData(Page):
    def post(self):
        '''
        根据应用的请求把相关用户的应用参数记录下来
        '''
        app=self.request.get('appid')
        userName=self.request.get("UserName")
        user=User.get_by_keyname('u'+userName)
        if user:
            appmap=user.getParms()
            if not appmap.has_key(app):
                appmap[app]={}
            for i in range(10):
                key=self.request.get('key'+str(i))
                value=self.request.get('value'+str(i))
                if key and value:
                    appmap[app][key]=value
            user.put()
        pass
class InfoAll(Page):
    def get(self):
        if not checkUser(self):
            self.response.out.write('1')
            return
        userName=self.request.get('UserName').strip()
        xml=None
        datas=None
        codeListAll=[]#全要型的订阅
        codeListPart=[]#只要本层订阅方式
        deleteListCode=[]
        for sub in Subscribe.all().filter('userName in',[userName,'000']).filter('status =','1'):
            if '0'==sub.subscribeType:
                codeListAll.append(sub.code)
            codeListPart.append(sub.code)


        xml,datas=infoallxmldic(ContentClass.get_by_key_name(codeListPart),xml,datas)
        for c in codeListAll:
            xml,datas=infoallxmldic(findChildNodes(c).filter('userName =',''),xml,datas)
        xml,datas=infoallxmldic(ContentClass.all().filter('userName =',userName).filter('status =','1'),xml,datas)
        datas.setAttribute('type','infoall')
        datas.setAttribute('code','main')
        datas.setAttribute('verson',AppPhoneVerson)
        datas.setAttribute('download',AppPhoneUri)
        userAppData(userName,datas)
        self.response.out.write(xml.toxml('utf-8'))
        return
class InfoUpdate(Page):
    def get(self):
        if not checkUser(self):
            self.response.out.write('1')
            return
        userName=self.request.get('UserName').strip()
        xml=None
        datas=None
        userUpdate=UserUpdate.get_by_userName(userName)
        codeListPart=userUpdate.updateContent#只要本层订阅方式
        codeListAll=[]#全要型的订阅
        codeListDelete=[]
        for sub in Subscribe.get_by_key_name(userUpdate.updateSubscribe):
            if '0'==sub.status:
                codeListDelete.append(sub.code)
            else:
                if '0'==sub.subscribeType:
                    codeListAll.append(sub.code)
                codeListPart.append(sub.code)
        xml,datas=infoallxmldic(ContentClass.get_by_key_name(codeListPart),xml,datas)
        for c in codeListAll:
            xml,datas=infoallxmldic(findChildNodes(c,'1').filter('userName =',''),xml,datas)
        xml,datas=infoallxmldic(codeListDelete,xml,datas,True)
        datas.setAttribute('type','infoupdate')
        userAppData(userName,datas)
        self.response.out.write(xml.toxml('utf-8'))
        userUpdate.updateSubscribe=[]
        userUpdate.updateContent=[]
        userUpdate.put()
        return

class AddReply(Page):
    def get(self):
        try:
            m=self.request.get('MainCode')
            code=self.request.get('Code')
            c=code.split('-')
            if len(c)==0 or c[0]!=m:
                self.response.out.write('1')
                return
            if not checkUser(self):
                self.response.out.write('1')
                return
#            try:
            if 'a999-9-s1-1' == code:
                return doRePassWord(self)
            if 'a999-2-s1' == code:
                return doShouQuan(self)
            if 'a888' ==m:
                return doDingYue(self)
#            if 'a999-2-s1' == code:
#                return doShouQuan(self)
#                if 'a1'==self.request.get('MainCode'):
#                    return ToA1(self)
#                if 'a3'==self.request.get('MainCode') or 'a33'==self.request.get('MainCode'):
#                    return A3replay(self)#对微博的回复处理，
#                    self.redirect('/RssChangeScribe'+parm,permanent=True)
        except Exception,e:
            logging.error('reply:'+str(e))
            self.response.out.write('1')
            return

def doRePassWord(self):
    username=self.request.get('UserName')
    pas=[]
    for p in self.request.get('Content').split('**'):
        if p:
            pas.append(p)
    if len(pas)>=2 :
        u=User.get_by_keyname('u'+username)
        #u=db.GqlQuery("SELECT * FROM User where userName=:1 AND passWord=:2 ",self.request.get('UserName'),pas[0]).fetch(1)
        if u:
            u.passWord=pas[1]
            u.put()
            self.response.out.write('0')
            return
        else:
            self.response.out.write('1')
            return
#    if len(pas)>=3 and pas[1]!=pas[2]:
#        self.response.out.write('2')
#        return
    self.response.out.write('1')
    return

def doShouQuan(self):
    userName = self.request.get('UserName')
    content=self.request.get('Content').replace('*','')
    if '1'==content:
        content='sina'
    if '2'==content:
        content='sohu'
    if '3'==content:
        content='wy'
    if '4'==content:
        content='teng'
    c =ContentClass.get_by_key_name(key_names="a888-s1-3")
    if c:
        self.redirect(str('http://'+c.title.split(';')[1].split(',')[0].split(':')[1]+'/login'+'?username='+userName+'&website='+content))
    return

def doDingYue(self):
    username=self.request.get('UserName')
    docontent=self.request.get('Content')
#    m=self.request.get('MainCode')
    code=self.request.get('Code')
    c=code.split('-')
    if '3'==c[-1]:
        if '1'==docontent:
            content =ContentClass.get_by_key_name(key_names='a999-2-s1-'+username)
            if not content:
                content = ContentClass(key_name='a999-2-s1-'+username)
            content.maincode = 'a999'#主编号
            content.father = 'a999-2-s1'#父级
            content.content = '*;*1*2*3*4*'#内容
            content.replyType = '15'
            content.status = '1'
            content.level='101'
            content.userName=username
            content.put()
            content =ContentClass.get_by_key_name(key_names=code+'-'+username)
            if not content:
                content = ContentClass(key_name=code+'-'+username)
            content.maincode = 'a888'#主编号
            content.father = code#父级
            content.content = '1'#内容
            content.replyType = '16'
            content.status = '1'
            content.level='102'
            content.userName=username
            content.put()
            s=Subscribe.get_by_key_name(key_names='a999-2u'+username)
            if not s:
                s=Subscribe(key_name='a999-2u'+username)
            s.userName=username
            s.code='a999-2'
            s.level='2'
            s.father='a999'
            s.maincode='a999'
            s.subscribeType='0'
            s.status='1'
            s.put()
            s=Subscribe.get_by_key_name(key_names='a3u'+username)
            if not s:
                s=Subscribe(key_name='a3u'+username)
            s.userName=username
            s.code='a3'
            s.level='1'
            s.maincode='a3'
            s.subscribeType='1'
            s.status='1'
            s.put()
            self.response.out.write(WEBURL[7:]+'/InfoUpdate;')
            content =ContentClass.get_by_key_name(key_names=code)
            if content:
                try:
                    self.response.out.write(content.title.split(';')[1].split(',')[0].split(':')[1]+'/InfoAll;')
                    self.response.out.write(content.title.split(';')[1].split(',')[0].split(':')[1]+'/InfoUpdate')
                except Exception,e:
                    logging.info('error:'+content.title)
            return
        else:
            content =ContentClass.get_by_key_name(key_names='a999-2-s1-'+username)
            if content:
                content.status='0'
                content.put()
            user=User.get_by_keyname('u'+username)
            if user:
                appmap=user.getParms()
                if appmap.has_key('a3'):
                    del appmap['a3']
                user.put()
            content =ContentClass.get_by_key_name(key_names=code+'-'+username)
            if content:
                content.content='0'
                content.put()
            s=Subscribe.get_by_key_name(key_names='a999-2u'+username)
            if s:
                s.status='0'
                s.put()
            s=Subscribe.get_by_key_name(key_names='a3u'+username)
            if s:
                s.status='0'
                s.put()
            self.response.out.write(WEBURL[7:]+'/InfoUpdate')
            return
    self.response.out.write('0')
    return

class InitApp(Page):
    def get(self, *args):
        fromurl='/top'
        if not ContentClass.get_by_key_name("a3"):
            content=ContentClass(key_name='a3')
            content.maincode="a3"
            content.level="1"
            content.title=u'微博'
            content.content=u'[*sys/001/a777_1*]微博'
            content.status='1'
            content.updateSpanTime='100'
            content.put()
        if not ContentClass.get_by_key_name("a4"):
            content=ContentClass(key_name='a4')
            content.maincode="a4"
            content.level="1"
            content.title=u'即时通讯'
            content.content=u'[*sys/002/a777_1*]即时通讯'
            content.status='1'
            content.updateSpanTime='100'
            content.put()
        if not ContentClass.get_by_key_name("a777"):
            content=ContentClass(key_name='a777')
            content.maincode="a777"
            content.level="1"
            content.title=u'系统图库'
            content.content=u'[*sys/003/a777_1*]系统图库'
            content.status='1'
            content.updateSpanTime='100'
            content.put()
        if not ContentClass.get_by_key_name("a888"):
            content=ContentClass(key_name='a888')
            content.maincode="a888"
            content.level="1"
            content.title=u'应用列表'
            content.content=u'[*sys/004/a777_1*]应用列表'
            content.status='1'
            content.updateSpanTime='100'
            content.put()
        if not ContentClass.get_by_key_name("a888-s1"):
            content=ContentClass(key_name='a888-s1')
            content.maincode="a888"
            content.father='a888'
            content.level="100"
            content.content=u'应用列表'
            content.status='1'
            content.replyType='16'
            content.put()
        if not ContentClass.get_by_key_name("a888-s1-3"):
            content=ContentClass(key_name='a888-s1-3')
            content.maincode="a888"
            content.father='a888-s1'
            content.level="101"
            content.title='a3;a3_1:weibo.zxxsbook.com,a3_2:weibo.zxxsbook.com'
            content.content=u'微博应用这是微博应用的简介'
            content.status='1'
            content.replyType='16'
            content.put()
        if not ContentClass.get_by_key_name("a888-s1-4"):
            content=ContentClass(key_name='a888-s1-4')
            content.maincode="a888"
            content.father='a888-s1'
            content.level="101"
            content.title='a4;a4_1:im.zxxsbook.com'
            content.content=u'即时通讯应用，这是即时通讯应用的简介'
            content.status='1'
            content.replyType='16'
            content.put()
        if not ContentClass.get_by_key_name("a888-s1-777"):
            content=ContentClass(key_name='a888-s1-777')
            content.maincode="a888"
            content.father='a888-s1'
            content.level="101"
            content.title='a777;a777_1:imglib.zxxsbook.com'
            content.content=u'系统图库的简介'
            content.status='1'
            content.replyType='16'
            content.put()
        if not ContentClass.get_by_key_name("a999"):
            contentclass=ContentClass(key_name='a999')
            contentclass.title=u'系统设置'
            contentclass.content=u'[*sys/005/a777_1*]系统设置'
            contentclass.maincode='a999'
            contentclass.level='1'
            contentclass.status='1'
            contentclass.updateSpanTime='100'
            contentclass.put()

        if not ContentClass.get_by_key_name("a999-2"):
            contentclass=ContentClass(key_name='a999-2')
            contentclass.title=u'微博授权'
            contentclass.content=u'微博授权'
            contentclass.maincode='a999'
            contentclass.father='a999'
            contentclass.level='2'
            contentclass.status='1'
            contentclass.updateSpanTime='100'
            contentclass.put()
        if not ContentClass.get_by_key_name("a999-2-s1"):
            contentclass=ContentClass(key_name='a999-2-s1')
            contentclass.content=u'微博授权'
            contentclass.maincode='a999'
            contentclass.father='a999-2'
            contentclass.level='100'
            contentclass.status='1'
            contentclass.replyType='15'
            contentclass.put()
#        if not ContentClass.get_by_key_name("a9999"):
#            contentclass=ContentClass(key_name='a9999')
#            contentclass.code='a9999'
#            contentclass.title=u'系统消息'
#            contentclass.content=u'系统消息'
#            contentclass.maincode='a9999'
##            contentclass.father='a999'
#            contentclass.level='1'
#            contentclass.status='1'
#            contentclass.updateSpanTime='100'
#            contentclass.put()
        if not ContentClass.get_by_key_name("a999-9"):
            contentclass=ContentClass(key_name='a999-9')
            contentclass.title=u'修改密码'
            contentclass.content=u'修改密码'
            contentclass.maincode='a999'
            contentclass.father='a999'
            contentclass.level='2'
            contentclass.status='1'
            contentclass.updateSpanTime='100'
            contentclass.put()
        if not ContentClass.get_by_key_name("a999-9-s1"):
            contentclass=ContentClass(key_name='a999-9-s1')
#            contentclass.title=u'修改密码'
            contentclass.content=u'修改密码'
            contentclass.maincode='a999'
            contentclass.father='a999-9'
            contentclass.level='100'
            contentclass.replyType='5'
            contentclass.status='1'
#            contentclass.updateSpanTime='100'
            contentclass.put()
        if not ContentClass.get_by_key_name("a999-9-s1-1"):
            contentclass=ContentClass(key_name='a999-9-s1-1')
            contentclass.content=u'**原始密码#10#**新密码#10#**'
            contentclass.maincode='a999'
            contentclass.father='a999-9-s1'
            contentclass.level='101'
            contentclass.replyType='5'
            contentclass.status='1'
            contentclass.put()
        if not User.get_by_keyname(key_names='u000'):
            u=User(key_name='u3u000')
            u.userName='000'
            u.passWord='000'
            u.put()
        if not Subscribe.get_by_key_name(key_names='a999u000'):
            s=Subscribe(key_name='a999u000')
            s.userName='000'
            s.code='a999'
            s.level='1'
            s.father=''
            s.maincode='a999'
            s.subscribeType='1'
            s.status='1'
            s.put()
#        if not Subscribe.get_by_key_name(key_names='a9999u000'):
#            s=Subscribe(key_name='a9999u000')
#            s.userName='000'
#            s.code='a9999'
#            s.level='1'
#            s.father=''
#            s.maincode='a9999'
#            s.subscribeType='0'
#            s.status='1'
#            s.put()
        if not Subscribe.get_by_key_name(key_names='a888u000'):
            s=Subscribe(key_name='a888u000')
            s.userName='000'
            s.code='a888'
            s.level='1'
            s.father=''
            s.maincode='a888'
            s.subscribeType='0'
            s.status='1'
            s.put()
        if not Subscribe.get_by_key_name(key_names='a999-9u000'):
            s=Subscribe(key_name='a999-9u000')
            s.status='1'
            s.subscribeType='0'
            s.userName='000'
            s.maincode='a999'
            s.code='a999-9'
            s.father='a999'
            s.level='2'
            s.put()
        self.redirect(fromurl)


  