#coding=utf-8
#
__author__ = u'王健'
import logging
from mogu.login import login_required
from mogu.models.model import User, ContentClass, Subscribe, UserUpdate, UserNameNumber
from tools.page import Page
from tools.util import getPageing
from google.appengine.api import memcache

class UserInfo(Page):
  @login_required
  def get(self):
    searchType = self.request.get('searchType')
    self.redirect("/userList/0?searchType=%s" %searchType)


class UserList(Page):
  @login_required
  def get(self,page):
    searchType = self.request.get('searchType')#'searchType‘不存在是返回的不是None，而是''空字符
    if searchType in ['userName','date']:
        greetings=User.all().order('-'+searchType)
    elif searchType=='':
        greetings=User.all()
    else:
        greetings=User.get_by_keyname('u'+searchType)
        if greetings:
            greetings=[greetings]
        else:
            greetings=[]

    index=0 if page=="" else int(page)
    if greetings and type(greetings) is not list:
        greetings = greetings.fetch(16,index*16)
    prev,next=getPageing(len(greetings), index)
    template_values = {'greetings':greetings,"prev":prev,"next":next,"index":index,}
    self.render('template/user/userinfo2.html',template_values)
#    self.render('html/userManage/userInfo.html',template_values)
  @login_required
  def post(self,page):
    searchType = self.request.get('searchType')
    self.redirect('/userInfo?searchType=%s' %searchType)

class UserAdd(Page):
  @login_required
  def get(self):
    url = self.request.url
    template_values = {'url':url,}
    self.render('template/user/userAdd.html',template_values)
#    self.render('html/userManage/userAdd.html',template_values)
  @login_required
  def post(self):
    #判断是否存在#
    newUser = self.request.get('username').strip('\n')
    try:
        int(newUser)
        int(self.request.get('password'))
    except :
        self.response.out.write("<script>alert('用户名和密码为数字!');</script>")
        url = self.request.url
        template_values = {'url':url,}
        self.render('template/user/userAdd.html',template_values)
        return
    if int(newUser)>999:
        self.response.out.write("<script>alert('用户名必须小于1000!');</script>")
        url = self.request.url
        template_values = {'url':url,}
        self.render('template/user/userAdd.html',template_values)
        return
    users=User.get_by_keyname('u'+newUser)
    if users:
        self.response.out.write("<script>alert('用户名已存在!');</script>")
        url = self.request.url
        template_values = {'url':url,}
        self.render('template/user/userAdd.html',template_values)
    else:
        user = User(key_name='u'+str(len(newUser))+'u'+newUser)
        user.userName = newUser
        user.passWord = self.request.get('password').strip('\n')
        repassWord = self.request.get('repassword').strip('\n')
        user.trueName = self.request.get('truename').strip('\n')
        user.tele = self.request.get('telephone').strip('\n')
        user.mobile = self.request.get('mobile').strip('\n')
        user.put()
        addInit(user.userName,user.trueName,user.tele,user.mobile)#默认初始化订阅
        self.redirect('/userInfo')

class UserDelete(Page):
  @login_required
  def get(self):
    userName = self.request.get('userName')
    if userName=='000':
        return
    index = self.request.get('index')
    user=User.get_by_keyname('u'+userName)
    if user:
        user.delete()
    sq=Subscribe.all().filter('userName =',userName)
    for s in sq:
        s.delete()
    u=UserUpdate.get_by_userName(userName)
    if u:
        u.delete()
    else:
        u=UserUpdate.get_by_userName('u'+userName)
        if u:
            u.delete()
    contentq=ContentClass.all().filter('userName =',userName)
    for c in contentq:
        c.delete()
    self.redirect('/userList/%s' %index)

class UserUpdatePage(Page):
  @login_required
  def get(self):
    userName = self.request.get('userName')
    index = self.request.get('index')
    users = User.get_by_keyname('u'+userName)
    template_values = {'user':users,"index":index,}
    self.render('template/user/userUpdate.html',template_values)
  @login_required
  def post(self):
    userName = self.request.get('username')
    index = self.request.get('index')
    user = User.get_by_keyname('u'+userName)
    if user:
        user.trueName = self.request.get('truename')
        user.tele = self.request.get('telephone')
        user.mobile = self.request.get('mobile')
        user.put()
        self.redirect('/userList/%s' %index)


class UserLogin(Page):
    def get(self):
        UserName = self.request.get('UserName')
        UserPwd = self.request.get('UserPwd')
        ulist=User.all().filter('userName =',UserName).filter("passWord =",UserPwd).fetch(1)
        if ulist:
            self.response.out.write('1')
        else:
            self.response.out.write('3')
        pass

class DeleteUserNameMemcache(Page):
    def get(self):
        memcache.delete('username')


def getUname():
#    memname=memcache.get('username')
    unn=UserNameNumber.get_by_key_name('userNameNumber')
#    if not memname:
    if not unn:
        unn=UserNameNumber(key_name='userNameNumber')
        ul=User.all().order('-__key__').fetch(1)
        if ul:
            u=ul[0]
            uname=u.key().name()
            unames=uname.split('u')
            if len(unames)>=3:
                uname=unames[2]
            else:
                uname='1000'
            if len(uname)<=3:
                uname='1000'
            else:
                uname=str(int(uname)+1)
        else:
            uname='1000'
    else:
        uname=str(unn.userName+1)
#    else:
#        uname=str(int(memname)+1)
#    memcache.set('username',uname,3600)
    unn.userName=int(uname)
    unn.put()
    if User.get_by_keyname('u'+str(len(uname))+'u'+uname):
        return getUname()
    else:
#        u=User(key_name='u'+str(len(uname))+'u'+uname)
#        u.userName=uname
#        u.passWord=uname
#        u.trueName=''
#        u.tele=''
#        u.mobile=''
#        u.put()
        return uname


class UserRegister(Page):
    def get(self):
        try:


            UserName = self.request.get('UserName')
            UserPwd = self.request.get('UserPwd')
            if not UserName:
                self.response.out.write(getUname())
                return
            try:
                int(UserName)
                int(UserPwd)
            except :
                self.response.out.write('2')
                return
            #没有进行参数正确验证
            if UserName=='' or UserPwd=='':
                self.response.out.write('2')
                return


            user = User.get_by_keyname('u'+UserName)
            if not user:
                user = User(key_name='u'+str(len(UserName))+'u'+UserName)
                user.userName = self.request.get('UserName').strip('\n')
                user.passWord = self.request.get('UserPwd').strip('\n')
                user.trueName = self.request.get('trueName').strip('\n')
                user.tele = self.request.get('tele').strip('\n')
                user.mobile = self.request.get('mobile').strip('\n')
                user.put()
                addInit(user.userName,user.trueName,user.tele,user.mobile)#默认初始化订阅
                self.response.out.write('1')
            else:
                self.response.out.write('2')

        except Exception,e:
            logging.error('user:'+str(e))
            self.response.out.write('2')





def addInit(username,realName='',tel='',mtel=''):

#    content = ContentClass(key_name='a999-1-s1-'+username)
#    content.maincode = 'a999'#主编号
#    content.father = 'a999-1-s1'#父级
#    content.content = '****'#内容
#    content.replyType = '1'
#    content.status = '1'
#    content.level='101'
#    content.userName=username
#    content.put()

    content =ContentClass.get_by_key_name(key_names='a999-1-s1-'+username)
    if not content:
        content = ContentClass(key_name='a999-1-s1-'+username)
    content.maincode = 'a999'#主编号
    content.father = 'a999-1-s1'#父级
    content.content = '****'#内容
    content.replyType = '1'
    content.status = '1'
    content.level='101'
    content.userName=username
    content.put()
    
#    s=Subscribe.get_by_key_name(key_names='a888u'+username)
#    if not s:
#        s=Subscribe(key_name='a888u'+username)
#    s.userName=username
#    s.code='a888'
#    s.level='1'
#    s.maincode='a888'
#    s.subscribeType='0'
#    s.status='1'
#    s.put()
    content =ContentClass.get_by_key_name(key_names='a999-2-s1-'+username)
    if not content:
        content = ContentClass(key_name='a999-2-s1-'+username)
    content.maincode = 'a999'#主编号
    content.father = 'a999-2-s1'#父级
    content.content = '*;*1*3*4*'#内容
    content.replyType = '15'
    content.status = '1'
    content.level='101'
    content.userName=username
    content.put()
    code='a888-s1-3'
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
    code='a888-s1-4'
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
    code='a888-s1-777'
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
    #默认订阅微博
#    s=Subscribe.get_by_key_name(key_names='a999-2u'+username)
#    if not s:
#        s=Subscribe(key_name='a999-2u'+username)
#    s.userName=username
#    s.code='a999-2'
#    s.level='2'
#    s.father='a999'
#    s.maincode='a999'
#    s.subscribeType='0'
#    s.status='1'
#    s.put()
#    s=Subscribe.get_by_key_name(key_names='a3u'+username)
#    if not s:
#        s=Subscribe(key_name='a3u'+username)
#    s.userName=username
#    s.code='a3'
#    s.level='1'
#    s.maincode='a3'
#    s.subscribeType='1'
#    s.status='1'
#    s.put()
    s=Subscribe.get_by_key_name(key_names='a4u'+username)
    if not s:
        s=Subscribe(key_name='a4u'+username)
    s.userName=username
    s.code='a4'
    s.level='1'
    s.maincode='a4'
    s.subscribeType='0'
    s.status='1'
    s.put()
    s=Subscribe.get_by_key_name(key_names='a777u'+username)
    if not s:
        s=Subscribe(key_name='a777u'+username)
    s.userName=username
    s.code='a777'
    s.level='1'
    s.maincode='a777'
    s.subscribeType='1'
    s.status='1'
    s.put()




  