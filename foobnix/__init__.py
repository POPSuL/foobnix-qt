
__author__ = "popsul"


class Savable():

    def save(self):
        raise NotImplementedError()


class Loadable():

    def load(self):
        raise NotImplementedError()
