#!/usr/bin/env python

import ow  # @UnresolvedImport

from caravan.base import VanSession, VanDevice, VanModule, deviceCommand, Str, Int, Bool, Decimal



class OWEntry(VanDevice):
    list = None

    def __init__(self, parent, name):
        self.path = parent.path + name
        structure = ow.owfs_get(parent.structure_path + name)
        entryType, index, arraySize, accessMode, size, changebility = structure.split(',')[:-1]
        index = int(index)
        if index != 0:
            self.stateType = Str()
        elif entryType in ('i', 'u'):
            self.stateType = Int()
        elif entryType in ('f', 't', 'g', 'p'):
            self.stateType = Decimal()
        elif entryType == 'y':
            self.stateType = Bool()
        else:
            self.stateType = Str()
        if accessMode in ('ro', 'oo'):
            self.set = None
        if accessMode in ('wo', 'oo'):
            self.get = None
        super(OWEntry, self).__init__(parent, name.replace('.', '_'))

    def set(self, value):
        self.changeState(value)
        if self.stateType.__class__ == Bool:
            value = int(value)
        ow.owfs_put(self.path, str(value))

    @deviceCommand()
    def get(self):
        try:
            value = ow.owfs_get(self.path)
        except ow.exUnknownSensor:
            value = None
        value = self.stateType.reduce(value)  
        return self.changeState(value)


class OWDevice(VanDevice):
    def __init__(self, parent, name):
        super(OWDevice, self).__init__(parent, name.strip('/').replace('.', '_'))
        self.path = parent.path + name
        if parent.path == '/':
            self.structure_path = '/structure/%s/' % name.split('.')[0]
        else:
            self.structure_path = self.parent.structure_path + name

        for n in ow.owfs_get(self.path).split(','):
            if n.endswith('/'):
                if n.startswith('bus.'):
                    continue
                OWDevice(self, n)
            else:
                OWEntry(self, n)

    @deviceCommand()
    def list(self):
        for d in self.children.values():
            get = getattr(d, 'get', None)
            if get: get()
        return super(OWDevice, self).list()


class AppSession(VanSession):
    def start(self):
        OWRoot(self)


class OWRoot(VanModule):
    path = '/'
    def __init__(self, session):
        ow.init('core2:4304')
        super(OWRoot, self).__init__(session, 'owfs')
        for sensor in ow.Sensor('/').sensors():
            OWDevice(self, sensor._path.lstrip('/') + '/')



if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(AppSession)
