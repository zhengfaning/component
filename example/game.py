# coding: utf-8
from Component import *


#game.py
class Game(Component):

    @Require("GetConfig")           #需要一个名为GetConfig的服务
    def getConfig(self, *args):
        pass

    @Require("GetUser")             #需要一个名为GetUser的服务
    def getUser(self, id):
        pass

    @RegisterFlow("go", "Config")             #需要一个名为GetUser的服务
    def Go(self, info, flow):
        print "Game Go",info["name"]
        #flow.stop()
        return "Game Flow"

    @RegisterEvent("invoke")
    def onExecute(self, info):
        config = self.getConfig(1,3,4,5)   #此处的getConfig将会被相连组件提供
        print "config =",config
        config[100] = 10
        user = self.getUser(1)      #此处的getUser将会被相连组件提供
        print "user =",user
        print "info =",info
