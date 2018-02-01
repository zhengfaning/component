组件模式
特点:

1.  	通过服务依赖与注入的方式解决耦合

1.  	定向消息处理

1.  	强约束性，防止错误使用

1.  	灵活多变，简单易用

核心思想是利用服务依赖与注入的方式解决耦合问题,让代码独立、可测试。同时具有定向消息的处理。
使用方法也是非常简单易用的，例：

#game.py

    class Game(Component):
    
	    @Require("GetUser")#需要一个名为GetUser的服务
	    def getUser(self, id):
	    	pass
    
	    def invoke(self):
	    	print self.getUser(1)

#userManager.py

    class UserManager(Component):
    
	    def initialize(self):													#初始化
	        self.user_list = {1: {"name":"zhengfaning", }}
	
	    @RegiserService("GetUser")                                             #注册了一个名为GetUser的服务
	    def getUser(self, id):
	        return self.user_list.get(id, None)

#start.py
    Game(UserManager)   #父组件为Game,子组件为UserManager
    Component.initComponent() #初始化所有组件
    Game().invoke()   #组件是唯一的,所以组件本身就是一个单例,可通过()调用
    
# 结果： #
    {'name': 'zhengfaning'}

上面的业务中，Game使用Require修饰符指明需要服务GetUser，而UserManager提供了服务GetUser。但Game与UserManager并没有直接关联，而需要的依赖则由组件的服务体系提供，所以不存在耦合，相互是独立的

定向消息处理，消息是由顶至下的：
#event.py
    class Event:
    	EXECUTE = 1

#dog.py
    class Dog(Component):

	    @RegiserEvent(Event.EXECUTE)                                     #注册消息execute
	    def onInvoke(self, info):
	        print "dog, info =",info

#cat.py
    class Cat(Component):
	
	    @RegiserEvent(Event.EXECUTE)                                      #注册消息execute
	    def onInvoke(self, info):
	        print "cat, info =",info

#root.py
    class Root(Component):
    	pass
    

#start.py
    Root(Dog,Cat) #父组件为Root,子组件为Dog,Cat
    Component.initComponent() #初始化所有组件
    Root().onEvent(Event.EXECUTE, {"goods": "food"})

# 结果: #
    dog, info = {'goods': 'food'}
    cat, info = {'goods': 'food'}

服务类:


Component接口：
initComponent(): 


修饰类：
RegiserEvent








	
	
