#coding=utf-8
#author:u'王健'
#Date: 12-12-25
#Time: 下午10:21
from mogu.login import login_required
from mogu.models.model import Subscribe
from tools.page import Page

__author__ = u'王健'

class refershUserA4(Page):
  @login_required
  def get(self):
      sublist= Subscribe.all().filter('subscribeType =','1').filter('code =','a4')
      self.response.out.write('total:%s'%sublist.count())
      num=1
      for sub in sublist.fetch(50):
          sub.subscribeType='0'
          sub.put()
          self.response.out.write('%s:%s\n'%(num,sub.userName))
          num+=1


  