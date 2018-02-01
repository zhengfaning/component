# coding: utf-8
from Component import *


def test(*args):
    for arg in args:
        print arg

#config.py
class Config(Component):

    @RegisterFlow("go")             
    def Go(self, info, flow):
        print "Config Go",info["name"]
        return "Config Flow"


    @RegiserService("GetConfig")    
    def config(self, *args):
        '''注册了一个名为GetConfig的服务'''
        test(*args)
        return {"port": 10033, "maxUser": 10000}