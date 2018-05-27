import csv
from pprint import *
from random import *
from .utility import *
from .row import *
from .rows import *
from .keymap import *
from .groupmap import *


###############################################################

class Table:
    coding = "utf-8"

    def see(self):
        pprint(self.__dict__)

    # ===========================global function setting===================================
    def _destripC(s, n):
        dis = n - len(s)
        front = dis // 2
        back = dis - front
        space = " "
        return front * space + s + back * space

    def _destripL(s, n):
        return s + " " * (n - len(s))

    spacing = _destripC

    def shift():
        if Table.spacing == Table._destripC:
            Table.spacing = Table._destripL
        elif Table.spacing == Table._destripL:
            Table.spacing = Table._destripC

    """ initialize the class """

    def __init__(self, array2d=None, name=None):
        # index for iterator
        self.imax = -1
        self.imap = []
        self.name = name
        self.array2d = []
        self.lenmap = []
        self.sepmap = []  # track seperate seperate symbol
        self.colmap = {}
        self.keymap = None
        self.groupmap = None
        self.bindmap = None  # new class

        if not array2d:
            pass
        elif isinstance(array2d, list):
            good = True
            for v in array2d:
                if not isinstance(v, list):
                    good = False
            if good:
                self.array2d = array2d
            else:
                raise Exception("array2d should be 2D-list")
            self.setsepmap()
            self.setlenmap()
            self.setcolmap()

        else:
            raise Exception("array2d should be 2D-list")

    def setsepmap(self, j=None, sep='\n'):
        if j is None:
            n = wid(self)
            self.sepmap = inilist(n, '\n')
        else:
            self.sepmap[j] = sep
            self.setlenmapj(j)

    def init(head, i, name=None):
        # error!!!!
        if isinstance(head, str) or isinstance(head, list):
            if isinstance(head, str):
                head = slist(head)
            array2d = inilist2d(i, len(head))
            result = Table([head] + array2d)
            if name:
                result.name = name
            return result
        else:
            raise Exception("head must be init")

    def recapcolindex(self, j):
        j = wid(self) + j if j < 0 else j
        if j < 0 or j > wid(self):
            raise Exception("invalid col index")
        return j

    def addcol(self, j=-1):

        j = self.recapcolindex(j) + 1 if j < 0 else j
        # track colmap
        top = self.array2d[0]
        for i in range(j, wid(self)):

            key = top[i]
            if key != None:
                self.colmap[key] += 1
        # track bindmap
        # track array2d
        for i in range(0, len(self) + 1):
            self.array2d[i].insert(j, None)
        # track lenmap
        self.lenmap.insert(j, 4)

    def addcols(self, n, i=-1):
        for x in range(n):
            self.addcol(i)

    def delcol(self, j=-1):
        j = self.recapcolindex(j)
        if self.keymap is not None and self.array2d[0][j] in self.keymap.key:
            self.keymap = None
        if self.groupmap is not None and self.array2d[0][j] in self.groupmap.group:
            self.groupmap = None

        # track colmap
        top = self.array2d[0]
        for i in range(j, wid(self)):
            # print("j=", j)
            key = top[i]
            # print("key = ", key)
            self.colmap[key] -= 1
        del self.colmap[top[j]]
        # tack bindmap

        # actually delete
        for i in range(0, len(self) + 1):
            del self.array2d[i][j]
        # track lenmap
        del self.lenmap[j]

    def recaprowindex(self, i):
        i = len(self) + 1 + i if i < 0 else i
        if i < 0 or i > len(self) + 1:
            raise Exception("invalid row index")
        return i

    def addrow(self, i=-1):
        i = self.recaprowindex(i) + 1 if i < 0 else i
        if i == 0:
            raise Exception("invalid row index")
        if self.keymap is not None:
            self.keymap.trackaddrow(i)
        if self.groupmap is not None:
            self.groupmap.trackaddrow(i)
        # track bindmap
        newrow = inilist(wid(self), None)
        self.array2d.insert(i, newrow)
        self.setlenmapi(i)

    def addrows(self, n, i=-1):
        for x in range(n):
            self.addrow(i)

    def delrow(self, i=-1):
        i = self.recaprowindex(i)
        if i == 0:
            raise Exception("invalid row index")
        if self.keymap is not None:
            self.keymap.trackdelrow(i)
        if self.groupmap is not None:
            self.groupmap.trackdelrow(i)
        # track bindmap
        row = self.array2d.pop(i)
        self.recaplenmap(row)

    def setentry(self, i, j, value):
        i = len(self) + 1 + i if i < 0 else i
        j = wid(self) + 1 + j if j < 0 else j
        if self.array2d[i][j] == value:
            return
        # print("i,j = ",i,j)
        if i == 0:
            # set the head
            if value in self.colmap:
                raise Exception("such attribute already exist in colmap")
            else:
                oldatt = self.array2d[i][j]
                if oldatt in self.colmap:
                    del self.colmap[oldatt]
                self.colmap[value] = j
                # track keymap
                if self.keymap is not None and oldatt in self.keymap.key:
                    self.keymap.updatekey(oldatt, value)
                # track groupmap
                if self.groupmap is not None and oldatt in self.groupmap.group:
                    self.groupmap.updategroup(oldatt, value)
                # track bindmap
        else:
            if self.keymap is not None:
                self.keymap.tracksetentry(i, j, value)
            if self.groupmap is not None:
                self.groupmap.tracksetentry(i, j, value)
            # track bindmap set all in bindmap to such value
        # actually set entry
        self.array2d[i][j] = value
        self.setlenmapij(i, j)

    def shuffle(self):
        if self.bindmap is not None:
            raise Exception("debind self all for shuffle")
        groupmap = self.groupmap
        keymap = self.keymap
        head = self.array2d.pop(0)
        shuffle(self.array2d)
        self.array2d.insert(0, head)
        if groupmap is not None:
            self.setgroup(groupmap.group)
        if keymap is not None:
            self.setkey(keymap.key)

    def setkey(self, s):
        self.delkey()
        self.keymap = Keymap.make(self, s)

    def delkey(self):
        if self.keymap is not None:
            del self.keymap
        self.keymap = None

    def setgroup(self, s):
        self.delgroup()
        self.groupmap = Groupmap.make(self, s)

    def delgroup(self):
        if self.groupmap is not None:
            del self.groupmap
        self.groupmap = None

    # ====================buildin method part====================
    def __len__(self):
        return len(self.array2d) - 1

    def setlenmap(self):
        lenmap = []
        for i in range(wid(self)):
            lenmap.append(max([maxlen(v[i], self.sepmap[i]) for v in self.array2d]))
        self.lenmap = lenmap

    def recaplenmap(self, row):
        # recap lenmap by delete row
        for j in range(wid(self)):
            if maxlen(row[j], self.sepmap[j]) == self.lenmap[j]:
                self.lenmap[j] = max([maxlen(v[j], self.sepmap[j]) for v in self.array2d])

    def setlenmapj(self, j):
        # set lenmap by col
        self.lenmap[j] = max([maxlen(v[j], self.sepmap[j]) for v in self.array2d])

    def setlenmapi(self, i):
        # set lenmap by row
        row = self.array2d[i]
        for j in range(wid(self)):
            self.lenmap[j] = max(self.lenmap[j], maxlen(row[j], self.sepmap[j]))

    def setlenmapij(self, i, j):
        # refresh entry i,j
        self.lenmap[j] = max(self.lenmap[j], maxlen(self.array2d[i][j], self.sepmap[j]))

    def setcolmap(self):
        head = self.gethead()
        for i in range(wid(self)):
            self.colmap[head[i]] = i

    def __next__(self):
        if self.imap[self.imax] == len(self):
            self.imap.pop()
            self.imax -= 1
            raise StopIteration
        self.imap[self.imax] += 1
        return self.array2d[self.imap[self.imax]]

    def __iter__(self):
        self.imax += 1
        self.imap.append(0);
        return self

    def modicolinput(self, key):
        if isinstance(key, int) or isinstance(key, str):
            index = None
            if isinstance(key, int):
                index = self.recapcolindex(key)
            elif isinstance(key, str):
                index = self.colmap[key]
        return index

    def apply(self, key, f, *args, para=False):
        j = self.modicolinput(key)
        if para:
            for i in range(1, len(self) + 1):
                self[i][j] = f(self[i][j], *args)
        else:
            for i in range(1, len(self) + 1):
                self[i][j] = f(*args)
        self.setlenmapj(j)

    def check(self, a):
        return a in self.colmap

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, str):
            index = None
            if isinstance(key, int):
                index = self.recaprowindex(key)
            elif isinstance(key, str):
                index = self.str2index(key)
            # return a Row
            return Row(self, index)

        elif isinstance(key, slice) or isinstance(key, tuple) or isinstance(key, list):
            ls = None
            if isinstance(key, slice):
                sindex = 1 if key.start is None else key.start
                eindex = len(self) if key.stop is None else key.stop
                sindex = self.recaprowindex(sindex)
                eindex = self.recaprowindex(eindex)
                ls = list(range(sindex, eindex + 1))
            elif isinstance(key, tuple) or isinstance(key, list):
                ls = []
                for v in key:
                    if isinstance(v, str):
                        ls.append(self.str2index(v))
                    elif isinstance(v, int):
                        ls.append(self.recaprowindex(v))
            # ls done start make a Rows
            return Rows(self, ls)

        pass

    def __setitem__(self, key, value):
        # need to implement！！！
        if isinstance(key, int) or isinstance(key, str):
            index = None
            if isinstance(key, int):
                index = self.recaprowindex(key)
            elif isinstance(key, str):
                index = self.str2index(key)
            if isinstance(value, tuple) or isinstance(value, list):
                # check length
                if len(value) == wid(self):
                    for j in range(wid(self)):
                        self.setentry(index, j, value[j])
                else:
                    raise Exception("width not mapping")
            else:
                for j in range(wid(self)):
                    self.setentry(index, j, value)

        # do something
        # slice, list of int list of str
        elif isinstance(key, slice) or isinstance(key, tuple) or isinstance(key, list):
            ls = None
            if isinstance(key, slice):
                sindex = 1 if key.start is None else key.start
                eindex = len(self) if key.stop is None else key.stop
                sindex = self.recaprowindex(sindex)
                eindex = self.recaprowindex(eindex)
                ls = list(range(sindex, eindex + 1))
            elif isinstance(key, tuple) or isinstance(key, list):
                ls = []
                for v in key:
                    if isinstance(v, str):
                        ls.append(self.str2index(v))
                    elif isinstance(v, int):
                        ls.append(self.recaprowindex(v))
            # start assign
            if isinstance(value, list) or isinstance(value, tuple):

                if isinstance(value[0], list) or isinstance(value[0], tuple):
                    # 2D - array
                    # check length
                    if len(value) != len(ls):
                        raise Exception("length not mapping")
                    # check length
                    for v in value:
                        if len(v) != wid(self):
                            raise Exception("width not mapping")
                    vindex = 0
                    for index in ls:
                        for j in range(wid(self)):
                            self.setentry(index, j, value[vindex][j])
                        vindex += 1
                else:
                    # 1D - array
                    # check width
                    if (len(value)) != wid(self):
                        raise Exception("width not mapping")
                    for index in ls:
                        for j in range(wid(self)):
                            self.setentry(index, j, value[j])
            else:
                # single value
                for index in ls:
                    for j in range(wid(self)):
                        self.setentry(index, j, value)

            pass

    def __delitem__(self, key):
        # start for testing!!!
        if isinstance(key, int):
            index = self.recapcolindex(key)
            self.delrow(index)
        elif isinstance(key, str):
            index = self.str2index(key)
            self.delrow(index)
        elif isinstance(key, slice):
            sindex = 1 if key.start is None else key.start
            eindex = len(self) if key.stop is None else key.stop
            sindex = self.recaprowindex(sindex)
            eindex = self.recaprowindex(eindex)

            for i in range(eindex, sindex - 1, -1):
                self.delrow(sindex)
        elif isinstance(key, tuple) or isinstance(key, list):
            ls = []
            for v in key:
                if isinstance(v, str):
                    ls.append(self.str2index(v))
                elif isinstance(v, int):
                    ls.append(self.recaprowindex(v))
            ls.sort(reverse=True)
            for index in ls:
                self.delrow(index)
        pass

    def str2index(self, key):
        if self.keymap is None:
            raise Exception("No keymap")
        else:
            key = slist(key)
            t = tuple([valueof(v) for v in key])
            index = self.keymap.map[t]
            return index

    def checklist(self, lst):
        l = []
        result = True
        for v in lst:
            if v not in self.colmap:
                result = False
                l.append(v)
        if not result:
            raise Exception("No Attribute(s): {}".format(",".join(l)))
        return result

    def getlist(self, i, ls):
        """
        print("i = ",i)
        r = []
        for v in ls:
            print("v=",v)
            j = self.colmap[v]
            print("j = ", j)

            row = self.array2d[i]
            print("row = ",row)
            value = row[j]
            print("value = ",value)
            r.append(value)
        print("r = ",r)
        """

        return [self.array2d[i][self.colmap[v]] for v in ls]

    def getsearchmap(self, ls):
        if isinstance(ls, str):
            ls = slist(ls, ",")
        self.checklist(ls)  # check attributes valid
        result = {}
        for i in range(1, len(self) + 1):
            t = tuple(self.getlist(i, ls))
            if t in result:
                result[t].append(i)
            else:
                result[t] = [i]
        return result

    def row2str(self, v, sep="|"):

        seplist = inilist(wid(self), None)
        for j in range(wid(self)):
            seplist[j] = strsep2list(str(v[j]), self.sepmap[j], self.lenmap[j])

        m = max(len(v) for v in seplist)

        for j in range(wid(self)):
            dis = m - len(seplist[j])
            seplist[j] += inilist(dis, "")


        for j in range(wid(self)):
            for i in range(m):
                seplist[j][i] = Table.spacing(seplist[j][i], self.lenmap[j])

        ls = []
        for i in range(m):
            ls.append(sep.join([seplist[j][i] for j in range(wid(self))]))

        return '\n'.join(ls)

    def head2str(self, sep="|"):
        head = self.gethead()

        ls = []
        for i in range(len(head)):
            s = str(head[i])
            if self.keymap is not None and head[i] in self.keymap.key:
                s += Keymap.symbol
            if self.groupmap is not None and head[i] in self.groupmap.group:
                s += Groupmap.symbol
            ls.append(s)
        return self.row2str(ls, sep)

    def __str__(self):
        s = ""
        s += self.head2str() + '\n'
        for v in self:
            s += self.row2str(v) + "\n"
        s += str(len(self)) + " row(s)"
        return s

    def p(self):
        for v in self.array2d:
            s = self.row2str(v)
            command = input(s)
            if command == "exit":
                break
        print(str(len(self.array2d)) + " row(s)", end="")

    def printi(self):
        itable = list(range(len(self) + 1))
        itable = Table(rotlist12(itable))
        jtable = [[self.name] + list(range(0, wid(self)))]
        jtable = Table(jtable)
        first = max(jtable.lenmap[0], itable.lenmap[0])
        jtable.lenmap[0] = first
        itable.lenmap[0] = first
        for i in range(1, len(jtable.lenmap)):
            jtable.lenmap[i] = max(jtable.lenmap[i], self.lenmap[i - 1])

        sep = ":"
        s = ""
        s += jtable.head2str(sep) + "\n"
        s += itable.head2str() + sep + self.head2str() + "\n"
        for i in range(1, len(self) + 1):
            s += itable.row2str(itable.array2d[i]) + sep
            s += self.row2str(self.array2d[i]) + "\n"
        s = s[:-1]
        print(s)

    def __repr__(self):

        # return self.row2str(self.row(0)) +"\n"+str(len(self.array2d)-1)+" row(s)"
        return str(self)

    def getcolindex(self, key):
        # for Row and Rows usage
        if isinstance(key, int):
            if key >= 0 and key < len(self):
                return key
            else:
                raise Exception("index out of range")
        elif isinstance(key, str):
            if self.check(key):
                return self.colmap[key]
            else:
                raise Exception("attribute name not exist")
        else:
            raise KeyError("only int or str is supported")

    def getrowindex(self, key):
        if self.keymap is not None:
            return self.keymap.map[key]
        else:
            raise Exception("please use setkeymap to set keymap")

    def read(name):
        result = []
        fname = name + ".csv"
        file = open(fname, "r", encoding=Table.coding, newline='')
        lines = csv.reader(file, delimiter=',', quotechar='"')
        for row in lines:
            vlist = [valueof(s) for s in row]
            result.append(vlist)
        file.close()
        print("READ <{}> FROM {}".format(name, fname))
        return Table(result, name=name)

    def save(self, name=None):
        # ask for ensure!!!
        if self.name is None and name is None:
            raise Exception("give a name for the array2d to save")
        elif self.name is None and isinstance(name, str):
            self.name = name
        fname = self.name + ".csv"
        file = open(fname, "w", encoding=Table.coding, newline='')
        lines = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in self.array2d:
            lines.writerow(row)
        file.close()
        print("SAVE <{}> TO {}".format(self.name, fname))

    def select(self, s="*", mod=all):
        # using string to input all fix!!!
        ls = None
        if s == "*":
            ls = self.gethead()
        else:
            if isinstance(s, str):
                ls = slist(s)
        self.checklist(ls)
        result = [ls]
        if mod == any:
            s = set()
            for i in range(1, len(self) + 1):
                sub = tuple(self.getlist(i, ls))
                s.add(sub)
            for r in s:
                result.append(list(r))
        elif mod == all:
            for i in range(1, len(self) + 1):
                result.append(self.getlist(i, ls))
        result = Table(result)
        print("SELECT {} from <{}>".format(",".join(result.gethead()), self.name))
        return result

    def rename(self, s):
        s = decomp(s)
        self.checklist(s[0])
        for i in range(len(s[0])):
            self.colmap[s[1][i]] = self.colmap[s[0][i]]
            del self.colmap[s[0][i]]
            self.array2d[0][self.colmap[s[1][i]]] = s[1][i]
            self.lenmap[self.colmap[s[1][i]]] = max(self.lenmap[self.colmap[s[1][i]]], len(s[1][i]))
            print("RENAME {} TO {}".format(s[0][i], s[1][i]))

    def getLMR(self, other):
        rdict = {}
        for key in self.colmap:
            rdict[key] = 0
        for key in other.colmap:
            if key in rdict:
                rdict[key] = 1
            else:
                rdict[key] = 2

        rlist = [[], [], []]
        for key in rdict:
            rlist[rdict[key]].append(key)
        return rlist

    def gethead(self):
        return self.array2d[0].copy()

    def _join(self, other, on=None, mod="natural"):
        if mod not in {"natural", "left", "right", "full"}:
            raise Exception("invalid mod")
        # check mod valid
        if on is None:
            lmr = self.getLMR(other)
            lmrm = lmr + [lmr[1]]
        else:
            mm = decomp(on)
            self.checklist(mm[0])
            other.checklist(mm[1])
            l = list(set(self.colmap) - set(mm[0]))
            r = list(set(other.colmap) - set(mm[1]))
            lmrm = [l, mm[0], r, mm[1]]
        selfsmap = self.getsearchmap(lmrm[1])
        othersmap = other.getsearchmap(lmrm[3])
        selfset = set(selfsmap)
        otherset = set(othersmap)
        sharedentry = selfset & otherset
        if on is None:
            result = [lmrm[0] + lmrm[1] + lmrm[2]]
        else:
            result = [self.gethead() + other.gethead()]
        for t in sharedentry:
            mid = list(t)
            for i in selfsmap[t]:
                left = self.getlist(i, lmrm[0])
                for j in othersmap[t]:

                    right = other.getlist(j, lmrm[2])
                    if on is None:
                        sub = left + mid + right
                    else:
                        sub = self[i] + other[j]
                    result.append(sub)
        if (mod == "natural"):
            print("<{}> {} JOIN <{}> ".format(self.name, mod.upper(), other.name), end="")
            if on is None:
                print()
            else:
                print("ON {}".format(on.replace(" ", "")))
            return Table(result)
        if (mod == "left" or mod == "full"):
            leftentry = selfset - otherset
            if on is None:
                right = inilist(len(lmrm[2]))
            else:
                right = inilist(len(lmrm[2]) + len(lmrm[3]))
            for t in leftentry:
                mid = list(t)
                for i in selfsmap[t]:
                    left = self.getlist(i, lmrm[0])
                    if on is None:
                        sub = left + mid + right
                    else:
                        sub = self[i] + right
                    result.append(sub)
        if (mod == "right" or mod == "full"):
            rightentry = otherset - selfset
            if on is None:
                left = inilist(len(lmrm[0]))
            else:
                left = inilist(len(lmrm[0]) + len(lmrm[1]))
            for t in rightentry:
                mid = list(t)
                for j in othersmap[t]:
                    right = other.getlist(j, lmrm[2])
                    if on is None:
                        sub = left + mid + right
                    else:
                        sub = left + other[j]
                    result.append(sub)

        print("<{}> {} JOIN <{}> ".format(self.name, mod.upper(), other.name), end="")
        if on is None:
            print()
        else:
            print("ON {}".format(on.replace(" ", "")))
        return Table(result)

    def __matmul__(self, other):
        return self._join(other)

    def __mul__(self, other):
        result = [self.gethead() + other.gethead()]
        for i in range(1, len(self) + 1):
            for j in range(1, len(other) + 1):
                sub = self[i] + other[j]
                result.append(sub)
        print("<{}> CROSS <{}> ".format(self.name, other.name))
        return Table(result)

    cross = __mul__

    def copy(self, name=None):
        result = Table([r for r in self.array2d])
        return result

    def __pow__(self, power, modulo=None):
        if power < 0:
            return None
        if power == 0:
            return Table(self.gethead())
        r = self.copy()
        for i in range(power - 1):
            r = r * self
        return r

    def getset(self):
        return set([tuple(r) for r in self])

    def __or__(self, other):
        selfset = self.getset()
        otherset = other.getset()
        sss = selfset | otherset
        result = [self.gethead()]
        for v in sss:
            result.append(list(v))
        return Table(result)

    def __and__(self, other):
        selfset = self.getset()
        otherset = other.getset()
        sss = selfset & otherset
        result = [self.gethead()]
        for v in sss:
            result.append(list(v))
        return Table(result)

    def __xor__(self, other):
        selfset = self.getset()
        otherset = other.getset()
        sss = selfset ^ otherset
        result = [self.gethead()]
        for v in sss:
            result.append(list(v))
        return Table(result)

    def __sub__(self, other):
        selfset = self.getset()
        otherset = other.getset()
        sss = selfset - otherset
        result = [self.gethead()]
        for v in sss:
            result.append(list(v))
        return Table(result)

    def union(self, other):
        pass

    def orderby(self, s):
        # this should be done at origin vaiable not output another new
        s = slist(s)
        for v in s:
            if not self.check(v):
                raise Exception("no attribute {} in {}".format(v, self.name))
        else:
            array = []
            for i in range(1, len(self) + 1):
                array.append([[self.get(i, v) for v in s], i])
            array.sort()
            result = [self.gethead()]
            for v in array:
                result.append(self.array2d[v[1]].copy())
            return Table(result)
        pass

    def setlib():
        s = """
try:
    import matplotlib.pyplot as plot
    global plt
    plt = plot
except Exception:
    print("can not import matplotlib!")
try:
    from mpl_interaction import PanAndZoom
    global PAZ
    PAZ = PanAndZoom
except:
    print("please download mpl_interaction.py")
"""
        return exec(s, globals(), locals())

    def bar(self, label, value):
        Table.setlib()
        self.orderby(label)
        fig, ax = plt.subplots()
        ax.bar([str(v) for v in self.col(label)], self.col(value))
        plt.xlabel(label)
        plt.ylabel(value)
        pan_zoom = PAZ(fig)
        plt.show()

    def pie(self, label, value):
        Table.setlib()
        fig, ax = plt.subplots()
        ax.pie(self.col(value), labels=self.col(label), autopct='%1.1f%%')
        pan_zoom = PAZ(fig)
        plt.show()

    def hist(self, value, low, up, num):
        Table.setlib()
        fig, ax = plt.subplots()
        amount = up - low
        block = amount / num
        bins = [low + i * block for i in range(num + 2)]
        ax.hist(self.col(value), bins, facecolor='green', edgecolor="yellowgreen")
        plt.xlabel(value)
        plt.ylabel("number")
        pan_zoom = PAZ(fig)
        plt.show()

    def plot(self, x, y, line="."):
        # add polar coord
        # add multiple and lines
        # add spline
        Table.setlib()
        fig, ax = plt.subplots()
        ax.plot(self.col(x), self.col(y), line)
        plt.xlabel(x)
        plt.ylabel(y)
        pan_zoom = PAZ(fig)
        plt.show()

    def union(self, other):
        # if one have more attributes include less one with None
        pass

    def intersect(self, other):
        pass

    def minus(self, other):
        pass

    def radar(self):
        # multiple in one graph
        pass

    def polar_radar(self):
        pass

    def hist2d(self):
        pass

    def bar2d(self):
        pass

    def scatter(self):
        pass

    def classify(self):
        # classify the value
        pass

    def groupby(self, s):
        # group array2d by attributes in s
        # form a subtable in groupby dictionary
        pass