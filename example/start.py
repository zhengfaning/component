# coding: utf-8
from Component import *
from game import *
from config import *
from usermanager import *

class Root(Component):
    pass

class FaceBook(Root):
    pass

class ConfigEx(Config):
    def config(self, *args):
        return {"port": 100, "maxUser": 10}

Root(Game, ConfigEx)      #父组件为Root,子组件为Game,Config
Game(UserManager)       #父组件为Game,子组件为UserManager
UserManager(FaceBook)


Component.initializeComponent()

Root().onEvent("invoke", {"data": "hello"})
result = Root().callFlow("go", {"name": "zfn"})
