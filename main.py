#coding=utf-8
#
from mogu.dataDo import refershUserA4
from mogu.interface import InfoAll, InfoUpdate, InitApp, ChangeAppData, AddReply
from mogu.subscribe import SubscribeList, SubscribeAdd, SubscribeInfo, UserSubscribeAdd, SubscribeDelete, SubscribeStatus
from mogu.users import UserInfo, UserAdd, UserDelete, UserUpdatePage, UserList, UserLogin, UserRegister, DeleteUserNameMemcache
from mogu.weibo import WeiboCheck

__author__ = u'王健'
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
#from google.appengine.ext.webapp import util
from mogu.content import ContentList, ContentAdd, ContentUpdate, ContentDelete, DeleteContentTimeOut
from mogu.login import Login, Top, Menu

app = webapp2.WSGIApplication([
    ('/', Login),
    ('/login', Login),
    ('/top',Top),
    ('/menu',Menu),
    ('/contentList/(?P<page>[0-9]*)',ContentList),
    ('/contentAdd',ContentAdd),
    ('/contentUpdate',ContentUpdate),
    ('/contentDelete',ContentDelete),
    ('/userList/(?P<page>[0-9]*)',UserList),
    ('/userInfo',UserInfo),
    ('/userAdd',UserAdd),
    ('/userDelete',UserDelete),
    ('/userUpdate',UserUpdatePage),
    ('/subscribeInfo', SubscribeInfo),
    ('/subscribeList/(?P<page>[0-9]*)', SubscribeList),
    ('/subscribeAdd', SubscribeAdd),
    ('/userSubscribeAdd', UserSubscribeAdd),
    ('/subscribeDelete',SubscribeDelete),
    ('/subscribeStatus',SubscribeStatus),

    ('/init',InitApp),
    ('/refershUserA4',refershUserA4),

    ('/InfoAll',InfoAll),
    ('/InfoUpdate',InfoUpdate),
    ('/UserLogin', UserLogin),
    ('/UserRegister', UserRegister),
    ('/DeleteUserNameMemcache', DeleteUserNameMemcache),
    ('/AddReply', AddReply),

    #改变应用的配置
    ('/changeAppData',ChangeAppData),
    ('/WeiboCheck',WeiboCheck),
    ('/DeleteContentTimeOut',DeleteContentTimeOut),

                              ],
                                         debug=True)
def main():
    pass

#    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
