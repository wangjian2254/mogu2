#coding=utf-8
#
from setting import ImageLibUri, RssGroup, imGroup

__author__ = u'王健'
from models.model import Users
from tools.page import Page



import urllib



__author__ = 'wangjian2254'

loginurl='/login'

def login_required(fn):
    def auth(*arg):
        web=arg[0]
        user=get_current_user(web)
        if user:
            arg=arg[1:]
            if len(arg)==0:
                fn(web)
            elif len(arg)==1:
                fn(web,arg[0])
            elif len(arg)==2:
                fn(web,arg[0],arg[1])
#            fn(web,arg)
        else:
#            web.redirect('/paper/234.html','post')
            if web.request.method=='GET':
                web.redirect(loginurl+'?fromurl='+web.request.path_url)
            else:
                web.redirect(loginurl+'?fromurl='+web.request.environ['HTTP_REFERER'])
    return auth

def setLogin(web,user):
    setCookie='webusername='+user.username.encode("utf-8")+';'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')
    if user.name:
        setCookie='webnickname='+urllib.quote(user.name.encode("utf-8"))+';'
        web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')
    setCookie='auth='+user.auth.encode("utf-8") or ''+';'
    #setCookie=str(setCookie)
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')

def setLogout(web):
    setCookie='webusername=;'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')
    setCookie='webnickname=;'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')
    setCookie='auth=;'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')



def get_current_user(web):
    guist={}
    Cookies = {}  # tempBook Cookies
    Cookies['request_cookie_list'] = [{'key': cookie_key, 'value': cookie_value} for cookie_key, cookie_value in web.request.cookies.iteritems()]
    for c in Cookies['request_cookie_list']:
        if c['key']=='webusername':
                    guist["username"]=c['value']
        if c['key']=='webnickname':
                    guist["name"]=urllib.unquote(c['value'].encode("utf-8"))
        if c['key']=='auth':
                    guist["auth"]=c['value']
    if guist and guist.has_key('username'):
        user=Users.all().filter('username =',guist['username']).fetch(1)
        if user:
            return user[0]
    return False

class Login(Page):
    def get(self, *args):
        fromurl=self.request.get('fromurl','/')
        self.render('template/login.html', {'fromurl':fromurl})

    def post(self, *args):
        username=self.request.get('username')
        password=self.request.get('password')
        fromurl=self.request.get('fromurl',None)
        if Users.all().count()==0:
            u=Users()
            u.name='admin'
            u.username='admin@gmail.com'
            u.password='admin'
            u.auth='admin'
            u.put()
        user=Users.all().filter('username =',username).filter('password =',password).fetch(1)
        if user:
            user=user[0]
            setLogin(self,user)
#            if fromurl:
#                self.redirect(fromurl)
#            else:
            
            self.render('template/workframe.html', {})
        else:
            self.redirect('/')


class Logout(Page):
    def get(self, *args):
        fromurl='/'
        setLogout(self)
        self.redirect(fromurl)


class Top(Page):
  @login_required
  def get(self):
      self.render('template/topnav.html',{})
class Menu(Page):
  @login_required
  def get(self):
      self.render('template/menu.html',{'imgliburi':ImageLibUri,'rssgroupuri':RssGroup,'groupuri':imGroup})
  