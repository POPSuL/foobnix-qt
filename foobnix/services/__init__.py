# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore


class BaseService(QtCore.QObject):

    activated = QtCore.pyqtSignal(name="activated")
    deactivated = QtCore.pyqtSignal(name="deactivated")


class ServiceController(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def attachService(self, service, serviceId):
        """
        @type service: BaseService
        @type serviceId: str
        """
        assert isinstance(service, BaseService), "service must be an instance of BaseService"
        assert isinstance(serviceId, str), "serviceId must be str"

    def deattachService(self, serviceId):
        """
        @type serviceId: str
        @rtype BaseService
        """
        assert isinstance(serviceId, str), "serviceId must be str"

    def provideService(self, serviceId):
        """
        @type serviceId: str
        @rtype BaseService
        """
        assert isinstance(serviceId, str), "serviceId must be str"

    def requestAsyncData(self, serviceId, dataId, callback, *args, **kwargs):
        """
        @type serviceId: str
        @type dataId: str
        @type callback: function
        @type args: any arguments passed to function
        """
        assert isinstance(serviceId, str), "serviceId must be str"
        assert isinstance(dataId, str), "dataId must be str"

    def runAsyncTask(self, serviceId, taskId, callback, *args, **kwargs):
        """
        @type serviceId: str
        @type taskId: str
        @type callback: function
        """
        assert isinstance(serviceId, str), "serviceId must be str"
        assert isinstance(taskId, str), "taskId must be str"