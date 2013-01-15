#coding=utf-8
#author:u'王健'
#Date: 11-12-20
#Time: 下午8:40
from mogu.models.model import ContentClass
from tools.page import Page

__author__ = u'王健'



class WeiboCheck(Page):
    def post(self, *args):
        usernamelist=self.request.get('username').split(',')
        do=self.request.get('do')
        web=self.request.get('web')
        for username in usernamelist:
            r =ContentClass.get_by_key_name(key_names='a999-2-s1-'+username)
            if r:
                if r.content.find('*;*')!=-1:
                    contentlist=r.content.split('*;*')
                else:
                    contentlist=r.content.split('**')
                dolist=contentlist[0].split('*')
                notdolist=contentlist[1].split('*')
                while '' in dolist:
                    dolist.remove('')
                while '' in notdolist:
                    notdolist.remove('')
                if not do:
                    l=dolist
                    dolist=notdolist
                    notdolist=l
                if 'sina'==web:
                    if '1' in dolist:
                        dolist.remove('1')
                    if '1' not in notdolist:
                        notdolist.append('1')
                if 'sohu'==web:
                    if '2' in dolist:
                        dolist.remove('2')
                    if '2' not in notdolist:
                        notdolist.append('2')
                if 'wy'==web:
                    if '3' in dolist:
                        dolist.remove('3')
                    if '3' not in notdolist:
                        notdolist.append('3')
                if 'teng'==web:
                    if '4' in dolist:
                        dolist.remove('4')
                    if '4' not in notdolist:
                        notdolist.append('4')
                if not do:
                    l=dolist
                    dolist=notdolist
                    notdolist=l
                r.content='*'+'*'.join(dolist)+'*;*'+'*'.join(notdolist)+'*'
                r.content=r.content
                r.put()