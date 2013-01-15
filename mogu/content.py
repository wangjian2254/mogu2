#coding=utf-8
#
from datetime import datetime, timedelta

__author__ = u'王健'
import logging
import string
from mogu.login import login_required
from mogu.models.model import ContentClass
from google.appengine.ext import db
from tools.page import Page
from tools.util import replaceStr, getLevelByCode, AutoCode, getMainCode, getReplyCode, getPageing



class ContentAdd(Page):
  @login_required
  def get(self):
      father = self.request.get('father')
      prev = self.request.get('prev')
      next = self.request.get('next')
      prevValue = self.request.get('prevValue')
      page = self.request.get('page_id')
      if(prevValue != '' and prev==''):#分页后下一页调用
          prev = prevValue
      newAddCode = AutoCode(father,prev,next)
      if self.request.get('isReply'):
          newAddCode = getReplyCode(newAddCode)#为编号加特殊标记's'，newAddCode有's'则直接返回
      if int(getLevelByCode(newAddCode))==1:#父类层，maincode与code相同
          maincode = newAddCode
          father = ''
      if int(getLevelByCode(newAddCode))>=2:
          maincode = getMainCode(newAddCode)
      template_values = {"newAddCode":newAddCode,"maincode":maincode,"father":father,"page":page,'isReply':self.request.get('isReply')}
      self.render('template/content/contentAdd.html',template_values)

  @login_required
  def post(self):
      page = self.request.get('page_Id')
      father = replaceStr(self.request.get('father'))
      code=replaceStr(self.request.get('code'))
      if not ContentClass.get_by_key_name(code):
          content = ContentClass(key_name=code)
          content.maincode = replaceStr(self.request.get('maincode'))
          content.title = replaceStr(self.request.get('title'))
          content.content = replaceStr(self.request.get('content'),'[()]')
          content.updateSpanTime = replaceStr(self.request.get('updateSpanTime'))
          content.father = father
          content.userName = replaceStr(self.request.get('userName'))
          content.replyType = replaceStr(self.request.get('replyType'))
          content.level = getLevelByCode(code)
          content.status = "1"
          content.put()
          logging.info(content.key().name())
          self.redirect('/contentList/%s?father=%s' %(page,father))
      else:
          self.redirect(self.request.environ['HTTP_REFERER'])


class ContentUpdate(Page):
  @login_required
  def get(self):
      contentCode = self.request.get('contentCode')
      index = self.request.get('page_id')
      father = self.request.get('father')
      if index=="":
          index='0'
      index = string.atoi(index)

      contentList = []
      contents=ContentClass.get_by_key_name(contentCode)
      template_values={"cList":contents,"index":index,"father":father,}
      self.render('template/content/contentUpdate.html', template_values)
#      self.render('html/contentManage/contentUpdate.html', template_values)
  @login_required
  def post(self):
      pageId = self.request.get('page_id')
      father = self.request.get('father')
      code=self.request.get('code')
      content = ContentClass.get_by_key_name(code)
      if content:
              content.title = replaceStr(self.request.get('title'))
              content.content = replaceStr(self.request.get('content'),'[()]')
              content.updateSpanTime = replaceStr(self.request.get('updateSpanTime'))
              content.status = replaceStr(self.request.get('status'))
              content.userName = replaceStr(self.request.get('userName'))
              content.replyType = replaceStr(self.request.get('replyType'))
              content.put()
      self.redirect('/contentList/%s?father=%s' %(pageId,father))

class ContentDelete(Page):
  @login_required
  def get(self):
      contentCode = self.request.get('contentCode')
      pageId = self.request.get('page_id')
      father = self.request.get('father')
      content=ContentClass.get_by_key_name(contentCode)
      if content.status == '1':
            content.status = '0'
            content.put()
      contentList=findChildNodes(content.key().name())
      db.delete(contentList)
      self.redirect('/contentList/%s?father=%s' %(pageId,father))


def findChildNodes(code,status=None):
    if status:
        return ContentClass.all().filter('status =',status).filter('__key__ >',ContentClass(key_name=code+'-').key()).filter('__key__ <',ContentClass(key_name=code+u"-\ufffd").key())
    else:
        return ContentClass.all().filter('__key__ >',ContentClass(key_name=code+'-').key()).filter('__key__ <',ContentClass(key_name=code+u"-\ufffd").key())

def findFather(father):
    fatherCodeList = []
    fList = ''
    father_list = father.split('-')
    for i in range(len(father_list)):
      fList = fList + father_list[i]
      fatherCodeList.append(fList)
      fList = fList+"-"
    if father and  fatherCodeList:
        return ContentClass.get_by_key_name(fatherCodeList)
    else:
        return []
#    for i in range(len(fatherCodeList)):
#      if ( fatherCodeList[i].find('s')!=-1):
#        replyContents = db.GqlQuery("SELECT * FROM ReplyContent WHERE code=:1 ",fatherCodeList[i])
#        for replyContent in replyContents:
#          fatherList.append(replyContent)
#      else:
#        contents = db.GqlQuery("SELECT * FROM ContentClass WHERE code=:1 ",fatherCodeList[i])
#        for content in contents:
#          fatherList.append(content)
#    return fatherList

class ContentList(Page):
  @login_required
  def get(self,page):
      prevValue = self.request.get('prevValue')
      father = self.request.get('father')
      if father =='':
          level = '1'
          contents=ContentClass.all().filter('level =',level).order('__key__')
          #contents = db.GqlQuery("SELECT * FROM ContentClass WHERE level = :1 ORDER BY code ASC", level)
          totalcount=contents.count(limit=1000000)
      else:
          level = str(int(getLevelByCode(father))+1)
          contents=ContentClass.all().filter('father =',father).order('__key__')
          #contents = db.GqlQuery("SELECT * FROM ContentClass WHERE father=:1 ORDER BY code ASC",father)
          totalcount=contents.count(limit=1000000)
      if level=='5':
          level = None
      fatherList = findFather(father)
      index=0 if page=="" else int(page)
      num=0 if index==0 else 1
      contents = contents.fetch(16+2^num,index*16-num)
      count=len(contents)
      for i in range(count):
          p,n=None,None
          c=contents[i]
          if i<count-1:
              n=contents[i+1]
          if i!=0:
              p=contents[i-1]
          if p:
              c.prev=p.key().name()
          if n:
              c.next=n.key().name()
      if num==1:
          contents=contents[1:17]
      else:
          contents=contents[0:16]
      if index!=0:
          if len(contents)==0:
              self.redirect('/contentList/%s?father=%s' %(index-1,father))
      prev,next=None,None
      if len(contents)>0:
          if contents[0].__dict__.has_key('prev') :
              prev=contents[0].prev
          else:
              prev=None
          next=str(contents[0].key().name())
      prevpage,nextpage=getPageing(len(contents), index)
      template_values = {"contents":contents,"contentlength":len(contents),"fatherList":fatherList,"prev":prev,"next":next,"prevpage":prevpage,"nextpage":nextpage,"index":index,"father":father,"level":level,"prevValue":prevValue,'lastpage':totalcount/16}
      self.render('template/content/zxlist.html',template_values)
      #self.render('html/contentManage/contentList.html',template_values)
  @login_required
  def post(self,page):
      father = self.request.get('hidden')
      prev = self.request.get('prev')
      code = self.request.get('code')
      next = self.request.get('next')
      prevValue = self.request.get('prevValue')
      if self.request.get('do')==u'插入':
          next=code
      if self.request.get('do')==u'添加':
          prev=code
      if not code:
          prev=self.request.get('prevcode')
          next=self.request.get('nextcode')
      self.redirect('/contentAdd?father=%s&prev=%s&next=%s&prevValue=%s&page_id=%s' %(father,prev,next,prevValue,page))


class DeleteContentTimeOut(Page):
    def get(self):
        #datetime.now()+timedelta(hours=-10)
        t1=datetime.now()+timedelta(hours=-241)
        for con in ContentClass.all().filter('status =','0').fetch(60):
            if (t1-con.lastUpdateTime).days>=10:
                con.delete()
#            pass
#        db.delete(ContentClass.all().filter('status =','0').filter('lastUpdateTime <',datetime.now()+timedelta(hours=-240)).fetch(30))
#        t1=timedelta(9, 86383, 314441).
#        t1