try:
    from uos import stat, remove
except:
    from os import stat, remove
import source # ignore this error
#from . import source # ignore this error


class Loader(source.Loader):

    def load(self, name):
        o_path = self.pkg_path + self.compiled_path(name)
        i_path = self.pkg_path + self.dir + "/" + name
        try:
            o_stat = stat(o_path)
            i_stat = stat(i_path)
            if i_stat[8] > o_stat[8]:
                # input file is newer, remove output to force recompile
                remove(o_path)
        finally:
            return super().load(name)
