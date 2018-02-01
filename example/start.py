# coding: utf-8
from Component import *
from game import *
from config import *
from usermanager import *

lol = {"ss": 11, "xx": 33, "fh": 99}
v1, v2, v3 = lol.values()

class Root(Component):
    pass

class FaceBook(Root):
    pass

class ConfigEx(Config):
    def config(self, *args):
        return {"port": 100, "maxUser": 10}

print Component.__dict__

print Component.__getClassID__(Root.__name__)
print Component.__getClassID__(Root.__name__)
print Component.__getClassID__(FaceBook.__name__)

Root(Game, ConfigEx)      #父组件为Root,子组件为Game,Config
Game(UserManager)       #父组件为Game,子组件为UserManager
UserManager(FaceBook)
xx = "dd"
yy = xx.encode("utf-8")


Component.initializeComponent()

Root().onEvent("invoke", {"data": "hello"})
result = Root().callFlow("go", {"name": "zfn"})
print "ok"
print result