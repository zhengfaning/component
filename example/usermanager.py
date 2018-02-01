# coding: utf-8
from Component import *

#userManager.py
class UserManager(Component):
    
    def initialize(self):
        self.user_list = {1: {"name":"zhengfaning", }}

    @RegisterFlow("go", "Game")
    def Go(self, info, flow):
        print "UserManager Go",info["name"]
        return "UserManager Flow"

    @RegiserService("GetUser")
    def getUser(self, id):
        '''获取用户'''
        return self.user_list.get(id, None)