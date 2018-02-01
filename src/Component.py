# coding: utf-8
import types
import sys
import uuid
import xml.etree.ElementTree as ET


'''
MIT License

Copyright (c) [2018] [zhengfaning]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

email: zhengfaning@hotmail.com
'''


class ComponentBase(object):
    """
    组件基类
    """
    '''跟踪模式,可跟踪消息处理路径'''
    track_mode = False



    def __init__(self):
        super(ComponentBase, self).__init__()
        self.childs = {}
        self.childs_order = []
        self.event_handler_dict = {}
        self.service_name_dict = {}
        self.parent = None
    

    def __addComponent(self, component):
        name = component.__name__
        if name in self.childs:
            raise SyntaxError("已经有同名的Component")
        instance = component()
        if instance.parent:
            raise SyntaxError("组件不允许2次加入")
        instance.parent = self
        self.childs[component.__name__] = instance
        self.childs_order.append(instance)
        
    
    def __addEventHandler(self, name, handler):
        self.event_handler_dict[name] = handler

    


class Component(ComponentBase):
    """
    组件类
    """
    __component_list__ = {}
    __component_order__ = []
    __component_info__ = {"require": {}, "service": {}, "event": {}, "flow": {}}
    __require_service_list__ = {}
    __register_service_list__ = {}
    __register_event_list__ = {}
    __register_flow_list__ = {}

    __class_id__ = {}
    __class_name__ = {}
    __class_id_count__ = 0
    __class_abandon__ = []

    
    def __new__(cls, *args, **kwargs):
        name = cls.__name__
        layer = cls.__mro__.index(Component)
        if layer > 2:
            raise SyntaxError("组件可继承层次不可超过2")

        if name not in Component.__component_list__:
            if layer == 2:
                if cls.__class_abandon__.__contains__(cls.__mro__[1]):
                    raise SyntaxError("此组件已被继承过")
                cls.__class_abandon__.append(cls.__mro__[1])
                cls.__extend__(cls.__mro__[1], cls.__mro__[0])
            instance = super(Component, cls).__new__(cls)
            super(Component, instance).__init__()
            #Component.__init__(instance)
            instance.init_component = False
            Component.__component_list__[name] = instance
            Component.__component_order__.append(name)
        instance = Component.__component_list__[name]
        if args.__len__() > 0:
            if instance.init_component:
                raise SyntaxError("组件只可初始化1次")
            for component in args:
                if isinstance(component, types.TypeType) and issubclass(component, Component):
                    cls.__addComponent(instance, component)
            instance.init_component = True

        return instance

    @classmethod
    def __extend__(cls, base_class, extend_class):
        extend_class_name = extend_class.__name__
        base_class_id = Component.__getClassID__(base_class.__name__)
        cls.__class_name__[base_class_id] = extend_class_name
        cls.__class_id__.pop(base_class.__name__)
        cls.__class_id__[extend_class_name] = base_class_id


    def __init__(self, *args, **kwargs):
        pass

    def initialize(self, *args, **kwargs):
        pass

    @classmethod
    def __getClassID__(cls, className):

        if className not in Component.__class_id__:
            Component.__class_id_count__ += 1
            Component.__class_id__[className] = Component.__class_id_count__
            Component.__class_name__[Component.__class_id_count__] = className


        return Component.__class_id__[className]

    @classmethod
    def __getClassNameForID__(cls, class_id):
        return Component.__class_name__[class_id]


    @classmethod
    def getComponent(cls, name):
        return cls.__component_list__[name]

    def __addComponent(self, component):
        '''加入组件,组名为类名,所以组件类不要有同名的'''
        ComponentBase._ComponentBase__addComponent(self, component)
        #super(Component, self).__addComponent(Component.__component_list__[name])

    
    def __addEventHandler(self, name, handler):
        '''加入事件句柄,可以是类函数,但必须是自身类函数'''
        if name in self.event_handler_dict:
            raise SyntaxError("已经有同名的事件句柄")
        ComponentBase._ComponentBase__addEventHandler(self, name, handler)

    def onEvent(self, event_name, info):
        '''事件处理'''
        if event_name in self.event_handler_dict:
            if self.track_mode:
                print "call the " + event_name + " event!"
            handler = self.event_handler_dict[event_name]
            handler(info)

        for child in self.childs_order:
            #child = self.childs[name]
            child.onEvent(event_name, info)

    class Flow:
        def __init__(self):
            self.stop_flow = False
            self.result_list = {}
            self.final_result = {}
            self.attr = {}
        
        def hasAttr(self, name):
            attr = self.attr.get(name)
            if not attr:
                return False

            if not attr.__len__() == 0:
                return False

            return True

        def __getitem__(self, name):
            if not self.attr.get(name):
                self.attr[name] = {}
            
            return self.attr[name]

        def isStop(self):
            return self.stop_flow
        
        def stop(self):
            self.stop_flow = True
        
        def finalResult(self):
            return self.final_result
        
    @classmethod
    def callFlow(cls, flow_name, info, flow = None):
        '''事件处理'''
        if not flow:
            flow = Component.Flow()

        flow_list = cls.__register_flow_list__[flow_name]

        #result = None
        for handler in flow_list:
            result = handler(info, flow)
            class_name = handler.im_class.__name__
            flow.result_list[class_name] = result
            if flow.isStop():
                flow.final_result = result
                return flow
        if result:
            flow.final_result = result
        return flow

    def onRootEvent(self, name, info):
        '''根事件,可能会造成消息死循环,请谨慎使用'''

        ancestor = self
        while (ancestor.parent != None):
            ancestor = ancestor.parent

        ancestor.onEvent(name, info)
    
    @classmethod
    def __serviceProcess(cls):
        class Adapter:
            def __init__(self, func):
                self.func = func

            def __call__(self, *args, **kwargs):
                result = self.func(*args, **kwargs)
                return result

        for require_class_id in cls.__require_service_list__:
            require_class_name = Component.__getClassNameForID__(require_class_id)
            require_info = cls.__require_service_list__[require_class_id]
            for require_service_name in require_info:
                require_func_name, require_service_len = require_info[require_service_name]
                if require_service_name not in cls.__register_service_list__:
                    raise SyntaxError(require_class_name+"请求的服务"+require_service_name+"不存在")
                target_class_id, target_func_name, target_func_len, target_handler = cls.__register_service_list__[require_service_name]
                target_class_name = Component.__getClassNameForID__(target_class_id)
                if require_service_len != target_func_len:
                    raise SyntaxError(require_class_name+"的虚函数"+require_func_name+ "与请求的服务"+require_service_name+"参数长度不一致")
                #require_func_name = require_info[require_service_name]
                require_instance = Component.__component_list__.get(require_class_name, None)
                if not require_instance:
                    raise SyntaxError(require_class_name+"组件没激活")
                target_instance = Component.__component_list__.get(target_class_name, None)
                if not target_instance:
                    raise SyntaxError(target_class_name+"组件没激活")
                target_func = getattr(target_instance, target_func_name)
                adapter = Adapter(target_func)
                setattr(require_instance, require_func_name, adapter)

    @classmethod
    def __eventProcess(cls):
        for class_id in cls.__register_event_list__:
            class_name = Component.__getClassNameForID__(class_id)
            instance = Component.__component_list__.get(class_name, None)
            if not instance:
                raise SyntaxError(class_name+"组件没激活")         
            event_name, func_name = cls.__register_event_list__[class_id]
            handler = getattr(instance, func_name)
            Component.__addEventHandler(instance, event_name, handler)

    @classmethod
    def __flowProcess(cls):

        def createFlow(class_name, handler):
            instance = Component.__component_list__.get(class_name, None)
            if not instance:
                raise SyntaxError(class_name + "组件没激活")
            func_name = handler.func_name
            return getattr(instance, func_name)


        for flow_name in cls.__register_flow_list__:
            flow_dict = cls.__register_flow_list__[flow_name]
            head_flow = flow_dict["head"]
            if not head_flow:
                raise SyntaxError(flow_name + "流程缺少起始点")
            flow_list = flow_dict["tail"]
            flow_order = []
            class_id, handler = head_flow
            class_name = Component.__getClassNameForID__(class_id)
            flow_instance = createFlow(class_name, handler)
            component_info = Component._Component__getComponentInfo("flow", class_id)
            component_info[flow_name] = [flow_name, handler, None, None]
            flow_order.append(flow_instance)
            pre = class_id
            num = len(flow_list)
            while num > 0:
                if not flow_list[pre]:
                    raise SyntaxError(flow_name + "流程缺少" + pre + "定义的句柄")
                #pre
                component_info = Component._Component__getComponentInfo("flow", class_id)
                component_info[flow_name][3] = flow_list[pre][0]
                #update
                class_id, handler = flow_list[pre]
                class_name = Component.__getClassNameForID__(class_id)
                #next
                component_info = Component._Component__getComponentInfo("flow", class_id)
                component_info[flow_name] = [flow_name, handler, pre, None]
                flow_instance = createFlow(class_name, handler)
                flow_order.append(flow_instance)
                pre = class_id
                num -= 1

            cls.__register_flow_list__[flow_name] = flow_order
            '''
            for depend_class in flow_list:
                handler, class_name  = flow_list[class_name]
                flow_order.append()
            class_name, handler, previous_flow = cls.__register_flow_list__[flow_name]
            cls.createFlow(class_name, handler)
            Component.__addFlowHandler(instance, flow_name, handler)
            '''


    @classmethod
    def __getComponentInfo(cls, type_name, class_name):
        if not cls.__component_info__[type_name].get(class_name):
            cls.__component_info__[type_name][class_name] = {}

        return cls.__component_info__[type_name][class_name]
        



    @classmethod
    def initializeComponent(cls):

        if cls != Component:
            raise SyntaxError("initializeComponent方法禁止在实例中使用")

        if not Component.__component_list__.__len__():
            return
        
        cls.__serviceProcess()
        cls.__eventProcess()
        cls.__flowProcess()
        top_component = []
        for component_name in cls.__component_order__:
            instance = Component.__component_list__[component_name]
            if hasattr(instance, "initialize"):
                initialize = getattr(instance, "initialize")
                initialize()
            if not instance.parent:
                top_component.append(instance)
        
        cc = top_component[0]
        
        info = cls.componentInfo(cc)

        #reload(sys)
        #sys.setdefaultencoding(encode_type)

        #print json.dumps(info)


        
    @classmethod
    def componentInfo(cls, component):
        info = ({},{})
        component_info = info[0]
        child_info = info[1]
        name = component.__class__.__name__
        component_info["name"] = name
        if name in cls.__component_info__["require"]:
            component_info["require"] = cls.__component_info__["require"][name]
        if name in cls.__component_info__["service"]:
            component_info["service"] = cls.__component_info__["service"][name]
        if name in cls.__component_info__["event"]:
            component_info["event"] = cls.__component_info__["event"][name]
        if name in cls.__component_info__["flow"]:
            component_info["flow"] = cls.__component_info__["flow"][name]
        for child_name in component.childs:
            child = component.childs[child_name]
            child_info[child_name] = {}
            child_info[child_name] = cls.componentInfo(child)
        return info
    



class Require:
    def __init__(self, service_name):
        frame = sys._getframe()
        class_name = frame.f_back.f_code.co_name
        self.class_id = Component.__getClassID__(class_name)
        self.service_name = service_name
        

    def __call__(self, func):
        func_name = func.func_name
        len = func.func_code.co_varnames.__len__()
        if not Component.__require_service_list__.get(self.class_id, None):
            Component.__require_service_list__[self.class_id] = {}
        component_info = Component._Component__getComponentInfo("require", self.class_id)
        component_info[func_name] = (self.service_name,func)
        Component.__require_service_list__[self.class_id][self.service_name] = (func_name,len)
        return func


class RegiserService:
    def __init__(self, service_name):
        if service_name in Component.__register_service_list__:
            raise SyntaxError("已有同名的服务,请重新定义。")
        frame = sys._getframe()
        class_name = frame.f_back.f_code.co_name
        self.class_id = Component.__getClassID__(class_name)
        self.service_name = service_name
        
    def __call__(self, handler):
        if not handler.func_doc:
            raise SyntaxError("服务必须要有Doc String，即函数注释。")
        len = handler.func_code.co_varnames.__len__()
        component_info = Component._Component__getComponentInfo("service", self.class_id)
        component_info[self.service_name] = (handler.func_name, handler)
        Component.__register_service_list__[self.service_name] = (self.class_id, handler.func_name, len)
        
        return handler


class RegisterEvent:
    def __init__(self, event_name):
        frame = sys._getframe()
        class_name = frame.f_back.f_code.co_name
        self.class_id = Component.__getClassID__(class_name)
        self.event_name = event_name
        
    def __call__(self, handler):
        if not Component.__register_event_list__.get(self.class_id, None):
            Component.__register_event_list__[self.class_id] = {}
        component_info = Component._Component__getComponentInfo("event", self.class_id)
        component_info[self.event_name] = (self.event_name,handler.func_name,handler)
        Component.__register_event_list__[self.class_id] = (self.event_name,handler.func_name)
        return handler

class RegisterFlow:
    def __init__(self, flow_name, depend_class = None):
        frame = sys._getframe()
        class_name = frame.f_back.f_code.co_name
        self.class_id = Component.__getClassID__(class_name)
        self.flow_name = flow_name
        if depend_class:
            self.depend_class_id = Component.__getClassID__(depend_class)
        else:
            self.depend_class_id = None
        
    def __call__(self, handler):

        if not Component.__register_flow_list__.get(self.flow_name, None):
            Component.__register_flow_list__[self.flow_name] = { "head": None, "tail": {}}
        flow_dict = Component.__register_flow_list__[self.flow_name]
        #component_info = Component._Component__getComponentInfo("flow", self.class_name)
        #component_info[self.flow_name] = (self.flow_name,handler.func_name,handler, self.previous_flow)
        if not self.depend_class_id:
            if flow_dict["head"]:
                raise SyntaxError("流程不可拥有2个起始点。")
            flow_dict["head"] = (self.class_id, handler)
            return handler
        if flow_dict["tail"].get(self.depend_class_id):
            raise SyntaxError("流程重复依赖同一个点。")

        flow_dict["tail"][self.depend_class_id] = ((self.class_id, handler))
        return handler
        #Component.__register_event_list__[self.service_name] = handler.func_name


