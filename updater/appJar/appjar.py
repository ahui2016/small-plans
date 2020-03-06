# -*- coding: utf-8 -*-
""" appJar.py: Provides a GUI class, for making simple tkinter GUIs. """
# Nearly everything I learnt came from: http://effbot.org/tkinterbook/
# with help from: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
# with snippets from stackexchange.com

# make print & unicode backwards compatible
from __future__ import print_function
from __future__ import unicode_literals

# Import tkinter classes - handles python2 & python3
try:
    # for Python2
    from Tkinter import *
    import tkMessageBox as MessageBox
    import tkSimpleDialog as SimpleDialog
    from tkColorChooser import askcolor
    import tkFileDialog as filedialog
    import ScrolledText as scrolledtext
    import tkFont as tkFont
    # used to check if functions have a parameter
    from inspect import getargspec as getArgs
    PYTHON2 = True
    PY_NAME = "Python"
    UNIVERSAL_STRING = basestring
except ImportError:
    # for Python3
    from tkinter import *
    from tkinter import messagebox as MessageBox
    from tkinter import simpledialog as SimpleDialog
    from tkinter.colorchooser import askcolor
    from tkinter import filedialog
    from tkinter import scrolledtext
    from tkinter import font as tkFont
    # used to check if functions have a parameter
    from inspect import getfullargspec as getArgs
    PYTHON2 = False
    PY_NAME = "python3"
    UNIVERSAL_STRING = str

# import other useful classes
import os
import sys
import locale
import re
import imghdr  # images
import time  # splashscreen
import calendar  # datepicker
import datetime  # datepicker & image
import logging  # python's logger
import inspect  # for logging
from contextlib import contextmanager  # generators
try: import argparse   # argument parser
except ImportError: argparse = None

import __main__ as theMain
from platform import system as platform

# we need to import these too
# but will only import them when needed
random = None
ttk = ThemedStyle = None
hashlib = None
ToolTip = None
nanojpeg = PngImageTk = array = None  # extra image support
EXTERNAL_DND = None
INTERNAL_DND = None
types = None  # used to register dnd functions
winsound = None
PlotCanvas = PlotNav = PlotFig = None  # matplotlib
parseString = TreeItem = TreeNode = None  # AjTree
# GoogleMap
base64 = urlencode = urlopen = urlretrieve = quote_plus = json = None
ConfigParser = codecs = ParsingError = None  # used to parse language files
Thread = Queue = None
sqlite3 = None
turtle = None
webbrowser = None  # links
OrderedDict = None  # tabbedFrames

# to allow tkinter or ttk
frameBase = Frame
labelBase = Label
scaleBase = Scale
entryBase = Entry

# details
__author__ = "Richard Jarvis"
__copyright__ = "Copyright 2015-2018, Richard Jarvis"
__credits__ = ["Graham Turner", "Sarah Murch"]
__license__ = "Apache 2.0"
__version__ = "0.94.0"
__maintainer__ = "Richard Jarvis"
__email__ = "info@appJar.info"
__status__ = "Development"
__url__ = "http://appJar.info"
try:
    __locale__ = locale.getdefaultlocale()[0]
except ValueError:
    __locale__ = None

class Enum(object):
    """ class to emulate enum type - works in all python versions
        also provides some extra functions """

    __initialized = False
    def __init__(self, widgets, containers, excluded, keepers):
        self.widgets = widgets + containers
        self.containers = containers
        self.excluded = excluded
        self.keepers = []
        for k in keepers:
            self.keepers.append(self.get(k))
        self.funcList = []
        for w in self.widgets:
            if w not in self.excluded:
                self.funcList.append(w)
        self.__initialized = True

    def __getattr__(self, name):
        return self.get(name)

    def get(self, name):
        try: return self.widgets.index(name)
        except: raise KeyError("Invalid key: " + str(name))

    def getIgnoreCase(self, name):
        name = name.upper()
        for w in self.widgets:
            if w.upper() == name:
                return self.widgets.index(w)
        else:
            raise KeyError("Invalid key: " + str(name))

    def __setattr__(self, name, value):
        if self.__initialized: raise Exception("Unable to change Widget store")
        else: super(Enum, self).__setattr__(name, value)

    def __delattr__(self, name):
        raise Exception("Unable to delete from Widget store")

    def name(self, i):
        """Get the real name of the widget"""
        return self.widgets[i]

    def funcs(self):
        """ Get a list of names to use as functions """
        return self.funcList


# static list of widget names in an enum
WIDGET_NAMES = Enum(
    widgets=["Label", "Message", "Entry", "TextArea", "Button", "FileEntry",
        "DirectoryEntry", "Scale", "Link", "Meter", "Image", "CheckBox",
        "RadioButton", "ListBox", "SpinBox", "OptionBox", "TickOptionBox",
        "Map", "PieChart", "Properties", "Table", "Plot", "MicroBit",
        "Tree", "DatePicker", "Separator", "Turtle", "Canvas",
        "Menu", "Toolbar", "FlashLabel", "Widget", "RootPage",
        "ContainerLog", "AnimationID", "ImageCache", "Bindings"],
    containers=[
        "LabelFrame", "Frame", "TabbedFrame", "PanedFrame", "ToggleFrame",
        "FrameStack", "SubFrame", "FrameBox", "FrameLabel", "SubWindow", "Window",
        "ScrollPane", "PagedWindow", "Notebook", "Note", "Tab", "Page", "Pane"],
    excluded=["DatePicker", "SubWindow", "Window", "Toolbar",
        "Note", "Tab", "Page", "Pane", "RootPage", "FlashLabel",
        "AnimationID", "ImageCache", "TickOptionBox", "Bindings",
        "FileEntry", "DirectoryEntry",
        "FrameBox", "FrameLabel", "ContainerLog", "Menu"],
    keepers=["Bindings", "ImageCache", "Menu", "Toolbar"]
)



####################################################
# The main GUI class - this provides all functions
####################################################
class gui(object):
    """ Class to represent the GUI
        - Create one of these
        - add some widgets
        - call the go() function """

    # ensure only one instance of gui is created
    # set to True in constructor
    # set back to false in stop()
    instantiated = False
    built = False

    # static variables
    exe_file = None
    exe_path = None
    lib_file = None
    lib_path = None

    # globals for supported platforms
    WINDOWS = 1
    MAC = 2
    LINUX = 3

    # positioning
    N = N
    NE = NE
    E = E
    SE = SE
    S = S
    SW = SW
    W = W
    NW = NW
    CENTER = CENTER
    LEFT = LEFT
    RIGHT = RIGHT

    # reliefs
    SUNKEN = SUNKEN
    RAISED = RAISED
    GROOVE = GROOVE
    RIDGE = RIDGE
    FLAT = FLAT

    ###################################
    # Constants for music stuff
    ###################################
    BASIC_NOTES = {
        "A": 440,
        "B": 493,
        "C": 261,
        "D": 293,
        "E": 329,
        "F": 349,
        "G": 392,
    }

    NOTES = {'f8': 5587, 'c#6': 1108, 'f4': 349, 'c7': 2093,
             'd#2': 77, 'g8': 6271, 'd4': 293, 'd7': 2349,
            'd#7': 2489, 'g#4': 415, 'e7': 2637, 'd9': 9397,
            'b8': 7902, 'a#4': 466, 'b5': 987, 'b2': 123,
            'g#9': 13289, 'g9': 12543, 'f#2': 92, 'c4': 261,
            'e1': 41, 'e6': 1318, 'a#8': 7458, 'c5': 523,
            'd6': 1174, 'd3': 146, 'g7': 3135, 'd2': 73,
            'd#3': 155, 'g#6': 1661, 'd#4': 311, 'a3': 219,
            'g2': 97, 'c#5': 554, 'd#9': 9956, 'a8': 7040,
            'a#5': 932, 'd#5': 622, 'a1': 54, 'g#8': 6644,
            'a2': 109, 'g#5': 830, 'f3': 174, 'a6': 1760,
            'e8': 5274, 'c#9': 8869, 'f5': 698, 'b1': 61,
            'c#4': 277, 'f#9': 11839, 'e5': 659, 'f9': 11175,
            'f#5': 739, 'a#1': 58, 'f#8': 5919, 'b7': 3951,
            'c#8': 4434, 'g1': 48, 'c#3': 138, 'f#7': 2959,
            'c6': 1046, 'c#2': 69, 'c#7': 2217, 'c3': 130,
            'e9': 10548, 'c9': 8372, 'a#6': 1864, 'a#7': 3729,
            'g#2': 103, 'f6': 1396, 'b3': 246, 'g#3': 207,
            'b4': 493, 'a7': 3520, 'd#6': 1244, 'd#8': 4978,
            'f2': 87, 'd5': 587, 'f7': 2793, 'f#6': 1479,
            'g6': 1567, 'e3': 164, 'f#3': 184, 'g#1': 51,
            'd8': 4698, 'f#4': 369, 'f1': 43, 'c8': 4186,
            'g4': 391, 'g3': 195, 'a4': 440, 'a#3': 233,
            'd#1': 38, 'e2': 82, 'e4': 329, 'a5': 880,
            'a#2': 116, 'g5': 783, 'g#7': 3322, 'b6': 1975,
            'c2': 65, 'f#1': 46
    }

    DURATIONS = {"BREVE": 2000, "SEMIBREVE": 1000, "MINIM": 500,
                "CROTCHET": 250, "QUAVER": 125, "SEMIQUAVER": 63,
                "DEMISEMIQUAVER": 32, "HEMIDEMISEMIQUAVER": 16
    }

###############################################
# USEFUL STATIC METHODS
###############################################

    @staticmethod
    def CENTER(win, up=0):
        gui.SET_LOCATION("CENTER", win=win, up=up)

    @staticmethod
    def SET_LOCATION(x, y=None, ignoreSettings=None, win=None, up=0):
        if ignoreSettings is not None:
            win.ignoreSettings = ignoreSettings

        if gui.GET_PLATFORM() != gui.LINUX:
            trans = win.attributes('-alpha')
            win.attributes('-alpha', 0.0)

        win.update_idletasks()

        if isinstance(x, UNIVERSAL_STRING) and x.lower() in ['c', 'center', 'centre'] and y is None:
            x = y = 'c'
        else:
            x, y = gui.PARSE_TWO_PARAMS(x, y)
        gui.trace("Set location called with %s, %s", x, y)

        # get the window's dimensions
        dims = gui.GET_DIMS(win)

        # set any center positions
        if isinstance(x, UNIVERSAL_STRING) and x.lower() in ['c', 'center', 'centre']: x = dims["x"]
        if isinstance(y, UNIVERSAL_STRING) and y.lower() in ['c', 'center', 'centre']: y = dims["y"]

        # move the window up a bit if requested
        y = y - up if up < y else 0

        # fix any out of bounds positions
        if x < 0 or x > dims['s_width']: x = dims['x']
        if y < 0 or y > dims['s_height']: y = dims['y']

        gui.trace("Screen: %sx%s. Requested: %sx%s. Location: %s, %s",
                    dims["s_width"], dims["s_height"], dims["b_width"],
                    dims["b_height"], x, y)
        win.geometry("+%d+%d" % (x, y))
        win.locationSet = True

        if gui.GET_PLATFORM() != gui.LINUX:
            win.attributes('-alpha', trans)


    @staticmethod
    def CLEAN_CONFIG_DICTIONARY(**kw):
        """ Used by all Classes to tidy up dictionaries passed into config functions
            Allows us to more quickly process the dictionaries when overriding config """

        try: kw['bg'] = kw.pop('background')
        except: pass
        try: kw['fg'] = kw.pop('foreground')
        except: pass
        kw = dict((k.lower().strip(), v) for k, v in kw.items())
        return kw

    @staticmethod
    def GET_PLATFORM():
        """ returns one of the gui class's three static platform variables """
        if platform() in ["win32", "Windows"]:
            return gui.WINDOWS
        elif platform() == "Darwin":
            return gui.MAC
        elif platform() in ["Linux", "FreeBSD"]:
            return gui.LINUX
        else:
            raise Exception("Unknown platform: " + platform())

    @staticmethod
    def SHOW_VERSION():
        """ returns a printable string containing version information """
        verString = \
            "appJar: " + str(__version__) \
            + "\nPython: " + str(sys.version_info[0]) \
            + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]) \
            + "\nTCL: " + str(TclVersion) \
            + ", TK: " + str(TkVersion) \
            + "\nPlatform: " + str(platform()) \
            + "\npid: " + str(os.getpid()) \
            + "\nlocale: " + str(__locale__)

        return verString

    @staticmethod
    def SHOW_PATHS():
        """ returns a printable string containing path to libraries, etc """
        pathString = \
            "File Name: " + (gui.exe_file if gui.exe_file is not None else "") \
            + "\nFile Location: " + (gui.exe_path if gui.exe_path is not None else "") \
            + "\nLib Location: " + (gui.lib_path if gui.lib_path is not None else "")

        return pathString

    @staticmethod
    def GET_DIMS(container):
        """ returns a dictionary of dimensions for the supplied container """
        container.update()
        dims = {}
        # get the apps requested width & height
        dims["r_width"] = container.winfo_reqwidth()
        dims["r_height"] = container.winfo_reqheight()

        # get the current width & height
        dims["w_width"] = container.winfo_width()
        dims["w_height"] = container.winfo_height()

        # get the window's width & height
        dims["s_width"] = container.winfo_screenwidth()
        dims["s_height"] = container.winfo_screenheight()

        # determine best geom for OS
        # on MAC & LINUX, w_width/w_height always 1 unless user-set
        # on WIN, w_height is bigger then r_height - leaving empty space
        if gui.GET_PLATFORM() in [gui.MAC, gui.LINUX]:
            if dims["w_width"] != 1:
                dims["b_width"] = dims["w_width"]
                dims["b_height"] = dims["w_height"]
            else:
                dims["b_width"] = dims["r_width"]
                dims["b_height"] = dims["r_height"]
        else:
            dims["b_height"] = max(dims["r_height"], dims["w_height"])
            dims["b_width"] = max(dims["r_width"], dims["w_width"])

        # GUI's corner - widget's corner
        # widget's corner can be 0 on windows when size not set by user
        dims["outerFrameWidth"] = 0 if container.winfo_x() == 0 else container.winfo_rootx() - container.winfo_x()
        dims["titleBarHeight"] = 0 if container.winfo_rooty() == 0 else container.winfo_rooty() - container.winfo_y()

        # add it all together
        dims["actualWidth"] = dims["b_width"] + (dims["outerFrameWidth"] * 2)
        dims["actualHeight"] = dims["b_height"] + dims["titleBarHeight"] + dims["outerFrameWidth"]

        dims["x"] = (dims["s_width"] // 2) - (dims["actualWidth"] // 2)
        dims["y"] = (dims["s_height"] // 2) - (dims["actualHeight"] // 2)

        return dims

    @staticmethod
    def PARSE_TWO_PARAMS(x, y):
        """ used to convert different possible x/y params to a tuple
        """
        if y is not None:
            return (x,y)
        else:
            if isinstance(x, (list, tuple)):
                return (x[0], x[1])
            else:
                if isinstance(x, UNIVERSAL_STRING):
                    x=x.strip()
                    if "," in x:
                        return [int(w.strip()) for w in x.split(",")]
                return (x, x)

    @staticmethod
    def SPLIT_GEOM(geom):
        """ returns 2 lists made from the geom string
        :param geom: the geom string to parse
        :returns: a tuple containing a width/heiht tuple & a x/y position tuple
        """
        geom = geom.lower().split("x")
        width = int(float(geom[0]))
        height = int(float(geom[1].split("+")[0]))
        try:
            x = int(float(geom[1].split("+")[1]))
            y = int(float(geom[1].split("+")[2]))
        except IndexError:
            x = y = -1

        return (width, height), (x, y)

    @staticmethod
    def MOUSE_POS_IN_WIDGET(widget, event, findRoot=True):
        """ returns the mouse's relative position in a widget
        :param widget: the widget to look in
        :param event: the event containing the mouse coordinates
        :param findRoot: if we should make this relative to the parent
        """

        # first we have to get the real master
        master = widget
        while findRoot:
            if isinstance(master, (SubWindow, Tk)):
                findRoot = False
            else:
                master = master.master

        # subtract the widget's top left corner from the root window's top corner
        x = event.x_root - master.winfo_rootx()
        y = event.y_root - master.winfo_rooty()
        gui.trace("<<MOUSE_POS_IN_WIDGET>> %s %s,%s", widget, x, y)
        return (x, y)

#####################################
#####################################
# CONSTRUCTOR - creates the GUI
#####################################
    def __init__(
                    self, title=None, geom=None, handleArgs=True, language=None,
                    startWindow=None, useTtk=False, useSettings=False, showIcon=True, **kwargs
                ):
        """ constructor - sets up the empty GUI window, and inits the various properties """

        if self.__class__.instantiated:
            raise Exception("You cannot have more than one instance of gui, try using a subWindow.")
        else:
            self.__class__.instantiated = True

        self.alive = True

        # first up, set the logger
        def _logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(logging.DEBUG-5):
                self._log(logging.DEBUG-5, message, args, **kwargs)
        def _logToRoot(message, *args, **kwargs):
            logging.log(logging.DEBUG-5, message, *args, **kwargs)

        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)s:%(levelname)s %(message)s')
        logging.addLevelName(logging.DEBUG - 5, 'TRACE')
        setattr(logging, 'TRACE', logging.DEBUG -5)
        setattr(logging.getLoggerClass(), "trace", _logForLevel)
        setattr(logging, "trace", _logToRoot)

        logFile = kwargs.pop("file", kwargs.pop("logFile", None))
        logLevel = kwargs.pop("log", kwargs.pop("logLevel", None))

        self._language = language
        self.useSettings = useSettings
        self.settingsFile = "appJar.ini"
        self.externalSettings = {}

        self.startWindow = startWindow

        # check any command line arguments
        if argparse is None: handleArgs = False
        args = self._handleArgs() if handleArgs else None

        # warn if we're in an untested mode
        self._checkMode()
        # first out, verify the platform
        self.platform = gui.GET_PLATFORM()

        # process any command line arguments
        self.ttkFlag = False
        selectedTtkTheme = None
        if handleArgs:
            if args.f:
                gui.setLogFile(args.f)
                logFile = None # don't use any param logFile

            tmplevel, logLevel = logLevel, None
            if args.c: gui.setLogLevel("CRITICAL")
            elif args.e: gui.setLogLevel("ERROR")
            elif args.w: gui.setLogLevel("WARNING")
            elif args.i: gui.setLogLevel("INFO")
            elif args.d: gui.setLogLevel("DEBUG")
            elif args.t: gui.setLogLevel("TRACE")
            else: loglevel = tmplevel

        if logFile is not None: gui.setLogFile(logFile)
        if logLevel is not None: gui.setLogLevel(logLevel)

        if handleArgs:
            if args.l: self._language = args.l
            if args.ttk:
                useTtk = True
                if args.ttk is not True:
                    selectedTtkTheme = args.ttk

            if args.s:
                self.useSettings = True
                if args.s is not True:
                    self.settingsFile = args.s

        # configure as ttk
        if useTtk:
            self._useTtk()
            if useTtk is not True:
                selectedTtkTheme = useTtk

        # a stack to hold containers as being built
        # done here, as initArrays is called elsewhere - to reset the gubbins
        self.containerStack = []
        self.translations = {"POPUP":{}, "SOUND":{}, "EXTERNAL":{}}
        # first up, set up all the data stores
        self.widgetManager = WidgetManager()
        self.accessMade = False # accessibility subWindow
        self.splashConfig = None # splash screen?
        self.dnd = None # the dnd manager
        self.doFlash = False # set up flash variable
        self.hasTitleBar = True # used to hide/show title bar

        # validate function callbacks - used by numeric texts
        # created first time a widget is used
        self.validateNumeric = None
        self.validateSpinBox = None

        # dynamically create lots of functions for configuring stuff
        self._buildConfigFuncs()
        # language parser
        self.configParser = None

        # set up some default path locations
        # this fails if in interactive mode....
        try:
            gui.exe_file = str(os.path.basename(theMain.__file__))
            gui.exe_path = str(os.path.dirname(theMain.__file__))
        except:
            pass

        gui.lib_file = os.path.abspath(__file__)
        gui.lib_path = os.path.dirname(gui.lib_file)

        # location of appJar
        self.resource_path = os.path.join(gui.lib_path, "resources")
        self.icon_path = os.path.join(self.resource_path, "icons")
        self.sound_path = os.path.join(self.resource_path, "sounds")
        self.appJarIcon = os.path.join(self.icon_path, "favicon.ico")

        # user configurable
        self.userImages = gui.exe_path
        self.userSounds = gui.exe_path

        # create the main window - topLevel
        self.topLevel = Tk()
        self.topLevel.bind('<Configure>', self._windowEvent)

        def _setFocus(e):
            try: e.widget.focus_set()
            except: pass

        # these are specifically to make right-click menus disapear on linux
        self.topLevel.bind('<Button-1>', lambda e: _setFocus(e))
        self.topLevel.bind('<Button-2>', lambda e: _setFocus(e))
        self.topLevel.bind('<Button-3>', lambda e: _setFocus(e))
        # override close button
        self.topLevel.protocol("WM_DELETE_WINDOW", self.stop)
        # temporarily hide it
        self.topLevel.withdraw()

        # used to keep a handle on the last pop-up dialog
        # allows the dialog to be closed remotely
        # mainly for test-automation
        self.topLevel.POP_UP = None

        # create a frame to store all the widgets
        # now a canvas to allow animation...
        self.appWindow = CanvasDnd(self.topLevel)
        self.appWindow.pack(fill=BOTH, expand=True)
        self.topLevel.canvasPane = self.appWindow

        # set the windows title
        if title is None:
            title = "appJar" if gui.exe_file is None else gui.exe_file

        self.setTitle(title)
        self.topLevel.winIcon = None # will store the path to any icon

        # configure the geometry of the window
        self.topLevel.escapeBindId = None  # used to exit fullscreen
        self.topLevel.stopFunction = None  # used to exit fullscreen
        self.topLevel.startFunction = None

        # set the resize status - default to True
        self.topLevel.locationSet = False
        self.topLevel.ignoreSettings = False
        self.topLevel.isFullscreen = False # records if we're in fullscreen - stops hideTitle from breaking
        self.topLevel.displayed = True
        if geom is not None: self.setSize(geom)
        self.setResizable(True)

        self.Widgets = WIDGET_NAMES

        # 3 fonts used for most widgets
        self._buttonFont = tkFont.Font(family="Helvetica", size=12,)
        self._labelFont = tkFont.Font(family="Helvetica", size=12)
        self._inputFont = tkFont.Font(family="Helvetica", size=12)
        self._statusFont = tkFont.Font(family="Helvetica", size=12)

        # dedicated font for access widget
        self._accessFont = tkFont.Font(family="Arial", size=11,)
        # dedicated font for links - forces bold & underlined, but updated with label fonts
        self._linkFont = tkFont.Font(family="Helvetica", size=12, weight='bold', underline=1)

        self.tableFont = tkFont.Font(family="Helvetica", size=12)

        # create a menu bar - only shows if populated
        # now created in menu functions, as it generated a blank line...
        self.hasMenu = False
        self.hasStatus = False
        self.copyAndPaste = CopyAndPaste(self.topLevel, self)

        class Toolbar(frameBase, object):
            def __init__(self, master, **kwargs):
                super(Toolbar, self).__init__(master, **kwargs)
                self.BG_COLOR = None
                self.pinned = True
                self.pinBut = None
                self.inUse = False
                self.toolbarMin = None
                self.location = None

            def makeMinBar(self):
                if self.toolbarMin is None:
                    self.toolbarMin = Frame(self.master, bd=1, relief=RAISED)
                    self.toolbarMin.config(bg="gray", height=3)
                    self.bind("<Leave>", self._minToolbar)
                    self.toolbarMin.bind("<Enter>", self._maxToolbar)

            def hide(self):
                if self.inUse:
                    self.pack_forget()
                    if self.toolbarMin is not None:
                        self.toolbarMin.pack_forget()

            def show(self):
                if self.inUse:
                    self.pack(before=self.location, side=TOP, fill=X)
                    if self.toolbarMin is not None:
                        self.toolbarMin.pack_forget()

            def _minToolbar(self, e=None):
                if not self.pinned:
                    if self.toolbarMin is not None:
                        self.toolbarMin.config(width=self.winfo_reqwidth())
                        self.toolbarMin.pack(before=self.location, side=TOP, fill=X)
                    self.pack_forget()

            def _maxToolbar(self, e=None):
                self.pack(before=self.location, side=TOP, fill=X)
                if self.toolbarMin is not None:
                    self.toolbarMin.pack_forget()

        class WidgetContainer(frameBase, object):
            def __init__(self, master, **kwargs):
                super(WidgetContainer, self).__init__(master, **kwargs)

        # create the main container for this GUI
        container = WidgetContainer(self.appWindow)
        # container = Label(self.appWindow) # made as a label, so we can set an
        # image
        if not self.ttkFlag:
            container.config(padx=2, pady=2, background=self.topLevel.cget("bg"))
        container.pack(fill=BOTH, expand=True)
        self._addContainer("root", WIDGET_NAMES.RootPage, container, 0, 1)

        self.tb = Toolbar(self.appWindow)
        if not self.ttkFlag:
            self.tb.config(bd=1, relief=RAISED)
        else:
            self.tb.config(style="Toolbar.TFrame")


        # set up the main container to be able to host an image
        self._configBg(container)

        if self.platform == self.WINDOWS and showIcon:
            try:
                self.setIcon(self.appJarIcon)
            except: # file not found
                gui.trace("Error setting Windows default icon")

        # set the ttk theme
        if self.ttkFlag:
            self.setTtkTheme(selectedTtkTheme)

        # for configuting event processing
        self.EVENT_SIZE = 1000
        self.EVENT_SPEED = 100
        self.preloadAnimatedImageId = None
        self.processQueueId = None

        # an array to hold any threaded events....
        self.events = []
        self.pollTime = 250
        self._fastStop = False
        self.configure(**kwargs)

        # special bindings
        self._globalBindings()

        self.built = True

    def _globalBindings(self):
        def _selectEntry(event):
            event.widget.select_range(0, 'end')

        def _selectText(event):
            event.widget.tag_add("sel","1.0","end")

        def _scrollPaste(event):
            event.widget.event_generate('<<Paste>>')
            event.widget.see(END)

        if self.GET_PLATFORM() == self.MAC:
            self.topLevel.bind_class("Text", "<Command-a>", _selectText)
            self.topLevel.bind_class("Entry", "<Command-a>", _selectEntry)
            self.topLevel.bind_class("Text", "<Command-v>", _scrollPaste)
        else:
            self.topLevel.bind_class("Text", "<Control-a>", _selectText)
            self.topLevel.bind_class("Entry", "<Control-a>", _selectEntry)
            self.topLevel.bind_class("Text", "<Control-v>", _scrollPaste)

    def _handleArgs(self):
        """ internal function to handle command line arguments """
        parser = argparse.ArgumentParser(
            description="appJar - the easiest way to create GUIs in python",
            epilog="For more information, go to: http://appJar.info"
        )
        parser.add_argument("-v", "--version", action="version", version=gui.SHOW_VERSION(), help="show version information and exit")
        logGroup = parser.add_mutually_exclusive_group()
        logGroup.add_argument("-c", action="store_const", const=True, help="only log CRITICAL messages")
        logGroup.add_argument("-e", action="store_const", const=True, help="log ERROR messages and above")
        logGroup.add_argument("-w", action="store_const", const=True, help="log WARNING messages and above")
        logGroup.add_argument("-i", action="store_const", const=True, help="log INFO messages and above")
        logGroup.add_argument("-d", action="store_const", const=True, help="log DEBUG messages and above")
        logGroup.add_argument("-t", action="store_const", const=True, help="log TRACE messages and above")
        parser.add_argument("-l", metavar="LANGUAGE.ini", help="set a language file to use")
        parser.add_argument("-f", metavar="file.log", help="set a log file to use")
        parser.add_argument("-s", metavar="SETTINGS", const=True, nargs="?", help="load settings, from an optional file name")
        parser.add_argument("--ttk", metavar="THEME", const=True, nargs="?", help="enable ttk, with an optional theme")
        return parser.parse_args()

    # function to check on mode
    def _checkMode(self):
        """ internal function to warn about issues in certain modes """
        # detect if we're in interactive mode
        if hasattr(sys, 'ps1'):
            self.warn("Interactive mode is not fully tested, some features might not work.")
        else:
            if sys.flags.interactive:
                self.warn("Postmortem Interactive mode is not fully tested, some features might not work.")
        # also, check for iPython
        try:
            __IPYTHON__
        except NameError:
            #no iPython - ignore
            pass
        else:
            self.warn("iPython is not fully tested, some features might not work.")

    def _configBg(self, container):
        """ internal function to set up a label as the BG """
        # set up a background image holder
        # alternative to label option above, as label doesn't update widgets
        # properly

        class BgLabel(labelBase, object):
            def __init__(self, master, **kwargs):
                super(BgLabel, self).__init__(master, **kwargs)

        if not self.ttkFlag:
            self.bgLabel = BgLabel(container, anchor=CENTER, font=self._getContainerProperty('labelFont'), background=self._getContainerBg())
        else:
            self.bgLabel = ttk.Label(container)
        self.bgLabel.place(x=0, y=0, relwidth=1, relheight=1)
        container.image = None

#####################################
# TTK functions
#####################################

    def _useTtk(self):
        """ enables use of ttk """
        global ttk, frameBase, labelBase, scaleBase, entryBase
        try:
            import ttk
        except:
            try:
                from tkinter import ttk
            except:
                gui.error("ttk not available")
                return
        self.ttkFlag = True
        frameBase = ttk.Frame
        labelBase = ttk.Label
        scaleBase = ttk.Scale
        entryBase = ttk.Entry

        gui.trace("Mode switched to ttk")

    def _loadTtkThemes(self):
        global ThemedStyle
        if ThemedStyle is None:
            try:
                from ttkthemes import ThemedStyle
                self.ttkStyle = ThemedStyle(self.topLevel)
            except:
                ThemedStyle = False

    def getTtkThemes(self, loadThemes=False):
        if loadThemes:
            self._loadTtkThemes()
            if not ThemedStyle:
                self.error("Custom ttkThemes not available")

        return self.ttkStyle.theme_names()

    def getTtkTheme(self):
        return self.ttkStyle.theme_use()

    # only call this after the main tk has been created
    # otherwise we get two windows!
    def setTtkTheme(self, theme=None):
        """ sets the ttk theme to use """
        self.ttkStyle = ttk.Style()

        gui.trace("Switching ttk theme to: %s", theme)
        if theme is not None:
            try:
                self.ttkStyle.theme_use(theme)
            except:
                gui.trace("no basic ttk theme named %s found, searching for additional themes", theme)
                self._loadTtkThemes()
                if not ThemedStyle:
                    self.error("ttk theme: %s unavailable. Try one of: %s", theme, str(self.ttkStyle.theme_names()))
                else:
                    self.ttkStyle.set_theme(theme)

        # set up our ttk styles
        self.ttkStyle.configure("DefaultText.TEntry", foreground="grey")
        self.ttkStyle.configure("ValidationEntryValid.TEntry", foreground="#4CC417", highlightbackground="#4CC417", highlightcolor="#4CC417", highlightthickness='20')
        self.ttkStyle.configure("ValidationEntryInvalid.TEntry", foreground="#FF0000", highlightbackground="#FF0000", highlightcolor="#FF0000", highlightthickness='20')
        self.ttkStyle.configure("ValidationEntryWait.TEntry", foreground="#000000", highlightbackground="#000000", highlightcolor="#000000", highlightthickness='20')

        self.ttkStyle.configure("ValidationEntryValid.TLabel", foreground="#4CC417")
        self.ttkStyle.configure("ValidationEntryInvalid.TLabel", foreground="#FF0000")
        self.ttkStyle.configure("ValidationEntryWait.TLabel", foreground="#000000")

        self.ttkStyle.configure("Link.TLabel", foreground="#0000ff")
        self.ttkStyle.configure("LinkOver.TLabel", foreground="#3366ff")

        #toolbars
        self.ttkStyle.configure("Toolbar.TFrame")
        self.ttkStyle.configure("Toolbar.TLabel")
        self.ttkStyle.configure("Toolbar.TButton", compound=CENTER, padding=0, expand=0)

#        self.fgColour = self.topLevel.cget("foreground")
#        self.buttonFgColour = self.topLevel.cget("foreground")
#        self.labelFgColour = self.topLevel.cget("foreground")

    # set a property for ttk theme
    ttkTheme = property(getTtkTheme, setTtkTheme)

###############################################################
# library loaders - on demand loading of different classes
###############################################################

    def _loadRandom(self):
        """ loasd random libraries """
        global random
        if random is None:
            import random

    def _loadTurtle(self):
        """ loasd turtle libraries """
        global turtle
        try:
            import turtle
        except:
            turtle = False
            self.error("Turtle not available")

    def _loadConfigParser(self):
        """ loads the ConfigParser, used by internationalisation & settings """
        global ConfigParser, ParsingError, codecs
        if ConfigParser is None:
            try:
                from configparser import ConfigParser
                from configparser import ParsingError
                import codecs
            except:
                try:
                    from ConfigParser import ConfigParser
                    from ConfigParser import ParsingError
                    import codecs
                except:
                    ConfigParser = ParsingError = codecs = False
                    self.configParser = None
                    return
            self.configParser = ConfigParser()
            self.configParser.optionxform = str

    def _loadHashlib(self):
        """ loads hashlib - used by text area """
        global hashlib
        if hashlib is None:
            try:
                import hashlib
            except:
                hashlib = False

    def _loadTooltip(self):
        """ loads tooltips - used all over """
        global ToolTip
        if ToolTip is None:
            try:
                from appJar.lib.tooltip import ToolTip
            except:
                ToolTip = False

    def _loadMatplotlib(self):
        """ loads matPlotLib """
        global PlotCanvas, PlotNav, PlotFig

        if PlotCanvas is None:
            try:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as PlotCanvas
                try: from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as PlotNav
                except: from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as PlotNav
                from matplotlib.figure import Figure as PlotFig
            except:
                PlotCanvas = PlotNav = PlotFig = False

    def _loadExternalDnd(self):
        """ loads external dnd - from other applications """
        global EXTERNAL_DND
        if EXTERNAL_DND is None:
            try:
                tkdndlib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "tkdnd2.8")
                os.environ['TKDND_LIBRARY'] = tkdndlib
                from appJar.lib.TkDND_wrapper import TkDND as EXTERNAL_DND
                self.dnd = EXTERNAL_DND(self.topLevel)
            except:
                EXTERNAL_DND = False

    def _loadInternalDnd(self):
        """ loads the internal dnd libraries """
        global INTERNAL_DND, types
        if INTERNAL_DND is None:
            try:
                import Tkdnd as INTERNAL_DND
                import types as types
            except:
                try:
                    from tkinter import dnd as INTERNAL_DND
                    import types as types
                except:
                    INTERNAL_DND = False
                    types = False

    def _loadURL(self):
        """ loads ibraries used by googlemaps widget """
        global base64, urlencode, urlopen, urlretrieve, quote_plus, json, Queue
        self._loadThreading()
        if Queue:
            if urlencode is None:
                try: # python 2
                    from urllib import urlencode, urlopen, urlretrieve, quote_plus
                    import json
                    import base64
                except ImportError: # python 3
                    try:
                        from urllib.parse import urlencode
                        from urllib.parse import quote_plus
                        from urllib.request import urlopen
                        from urllib.request import urlretrieve
                        import json
                        import base64
                    except:
                        base64 = urlencode = urlopen = urlretrieve = quote_plus = json = Queue = False
        else:
            base64 = urlencode = urlopen = urlretrieve = quote_plus = json = Queue = False

    def _loadThreading(self):
        """ loads threading classes, and sets up queue """
        global Thread, Queue
        if Thread is None:
            try:
                from threading import Thread
                import Queue
            except ImportError: # python 3
                try:
                    from threading import Thread
                    import queue as Queue
                except:
                    Thread = Queue = False
                    return

            self.eventQueue = Queue.Queue(maxsize=self.EVENT_SIZE)
            self._processEventQueue()

    def _loadNanojpeg(self):
        """ loads jpeg support """
        global nanojpeg, array
        if nanojpeg is None:
            try:
                from appJar.lib import nanojpeg
                import array
            except:
                nanojpeg = False
                array = False

    def _loadWinsound(self):
        """ loads winsound support on Windows """
        global winsound
        if winsound is None:
            if platform() in ["win32", "Windows"]:
                import winsound
            else:
                winsound = False

    def _importPngimagetk(self):
        """ loads PNG support """
        global PngImageTk
        if PngImageTk is None:
            try:
                from appJar.lib.tkinter_png import PngImageTk
            except:
                PngImageTk = False

    def _importAjtree(self):
        """ loads tree support - and creates tree classes """
        global parseString, TreeItem, TreeNode

        if TreeNode is None:
            try:
                from idlelib.TreeWidget import TreeItem, TreeNode
            except:
                try:
                    from idlelib.tree import TreeItem, TreeNode
                except:
                    gui.warning("no trees")
                    TreeItem = TreeNode = parseString = False

            if TreeNode is not False:
                try:
                    from xml.dom.minidom import parseString
                except:
                    gui.warning("no parse string")
                    TreeItem = TreeNode = parseString = False
                    return

    def _importSqlite3(self):
        """ loads sqlite3 """
        global sqlite3
        if sqlite3 is None:
            try:
                import sqlite3
            except:
                sqlite3 = False

    def _importWebBrowser(self):
        """ loads webbrowser """
        global webbrowser
        if webbrowser is None:
            try:
                import webbrowser
            except:
                webbrowser = False

#####################################
# FUNCTIONS FOR UNIVERSAL DND
#####################################

    def _registerExternalDragSource(self, title, widget, function=None):
        """ register a widget to start external drag events """
        self._loadExternalDnd()

        if EXTERNAL_DND is not False:
            try:
                self.dnd.bindsource(widget, self._startExternalDrag, 'text/uri-list')
                self.dnd.bindsource(widget, self._startExternalDrag, 'text/plain')
                widget.dndFunction = function
                widget.dragData = None
            except:
                # dnd not working on this platform
                raise Exception("Failed to register external Drag'n Drop for: " + str(title))
        else:
            raise Exception("External Drag'n Drop not available on this platform")

    def _registerExternalDropTarget(self, title, widget, function=None, replace=True):
        """ register a widget to receive external drag events """
        self._loadExternalDnd()

        if EXTERNAL_DND is not False:
            try:
                self.dnd.bindtarget(widget, self._receiveExternalDrop, 'text/uri-list')
                self.dnd.bindtarget(widget, self._receiveExternalDrop, 'text/plain')
                # cater for new drop parameter in new setters
                if function == True: function = None
                widget.dndFunction = function
                widget.dropData = None
                widget.dropReplace = replace
            except:
                # dnd not working on this platform
                raise Exception("Failed to register external Drag'n Drop for: " + str(title))
        else:
            raise Exception("External Drag'n Drop not available on this platform")

    def _registerInternalDragSource(self, kind, title, widget, function=None):
        """ register a widget to start internal drag events """
        self._loadInternalDnd()

        name = None
        if kind == WIDGET_NAMES.Label:
            name = self.getLabel(title)

        if INTERNAL_DND is not False:
            try:
                widget.bind('<ButtonPress>', lambda e: self._startInternalDrag(e, title, name, widget))
                widget.dnd_canvas = self._getCanvas().canvasPane
                gui.trace("DND drag source created: %s on canvas %s", widget, widget.dnd_canvas)
            except:
                raise Exception("Failed to register internal Drag'n Drop for: " + str(title))
        else:
            raise Exception("Internal Drag'n Drop not available on this platform")

    def _registerInternalDropTarget(self, widget, function):
        """ register a widget to receive internal drag events """
        gui.trace("<<WIDGET._registerInternalDropTarget>> %s", widget)
        self._loadInternalDnd()
        if not INTERNAL_DND:
            raise Exception("Internal Drag'n Drop not available on this platform")

        # called by DND class, when looking for a DND target
        def dnd_accept(self, source, event):
            gui.trace("<<WIDGET.dnd_accept>> %s - %s", widget, self.dnd_canvas)
            return self

        # This is called when the mouse pointer goes from outside the
        # Target Widget to inside the Target Widget.
        def dnd_enter(self, source, event):
            gui.trace("<<WIDGET.dnd_enter>> %s", widget)
            XY = gui.MOUSE_POS_IN_WIDGET(self,event)
            source.appear(self, XY)

        # This is called when the mouse pointer goes from inside the
        # Target Widget to outside the Target Widget.
        def dnd_leave(self, source, event):
            gui.trace("<<WIDGET.dnd_leave>> %s", widget)
            # hide the dragged object
            source.vanish()

        #This is called if the DraggableWidget is being dropped on us.
        def dnd_commit(self, source, event):
            source.vanish(all=True)
            gui.trace("<<WIDGET.dnd_commit>> %s Object received=%s", widget, source)

        #This is called when the mouse pointer moves within the TargetWidget.
        def dnd_motion(self, source, event):
            gui.trace("<<WIDGET.dnd_motion>> %s", widget)
            XY = gui.MOUSE_POS_IN_WIDGET(self,event)
            # move the dragged object
            source.move(self, XY)

        def keepWidget(self, title, name):
            if self.drop_function is not None:
                return self.drop_function(title, name)
            else:
                self.configParser(text=name)
                return True

        widget.dnd_accept = types.MethodType(dnd_accept, widget)
        widget.dnd_enter = types.MethodType(dnd_enter, widget)
        widget.dnd_leave = types.MethodType(dnd_leave, widget)
        widget.dnd_commit = types.MethodType(dnd_commit, widget)
        widget.dnd_motion = types.MethodType(dnd_motion, widget)
        widget.keepWidget = types.MethodType(keepWidget, widget)
        # save the underlying canvas
        widget.dnd_canvas = self._getCanvas().canvasPane
        widget.drop_function = function

        gui.trace("DND target created: %s on canvas %s", widget, widget.dnd_canvas)

    def _startInternalDrag(self, event, title, name, widget):
        """ called when the user initiates an internal drag event """
        gui.trace("Internal drag started for %s on %s", title, widget)

        x, y = gui.MOUSE_POS_IN_WIDGET(widget, event, False)
        width = x / widget.winfo_width()
        height = y / widget.winfo_height()

        thingToDrag = DraggableWidget(widget.dnd_canvas, title, name, (width, height))
        INTERNAL_DND.dnd_start(thingToDrag, event)

    def _startExternalDrag(self, event):
        """ starts external drags - not yet supported """
        widgType = gui.GET_WIDGET_CLASS(event.widget)
        self.warn("Unable to initiate drag events: %s", widgType)

    def _receiveExternalDrop(self, event):
        """ receives external drag events """
        widgType = gui.GET_WIDGET_CLASS(event.widget)
        event.widget.dropData = event.data
        if not hasattr(event.widget, 'dndFunction'):
            self.warn("Error - external drop target not correctly configured: %s", widgType)
        elif event.widget.dndFunction is not None:
            event.widget.dndFunction(event.data)
        else:
            if widgType in ["Entry", "AutoCompleteEntry", "SelectableLabel"]:
                if widgType == "SelectableLabel": event.widget.configure(state="normal")
                if event.widget.dropReplace:
                    event.widget.delete(0, END)
                event.widget.insert(END, event.data)
                event.widget.focus_set()
                event.widget.icursor(END)
                if widgType == "SelectableLabel": event.widget.configure(state="readonly")
            elif widgType in ["TextArea", "AjText", "ScrolledText", "AjScrolledText"]:
                if event.widget.dropReplace:
                    event.widget.delete(1.0, END)
                event.widget.insert(END, event.data)
                event.widget.focus_set()
                event.widget.see(END)
            elif widgType in ["Label"]:
                for k, v in self.widgetManager.group(WIDGET_NAMES.Image).items():
                    if v == event.widget:
                        try:
                            imgTemp = self.userImages
                            image = self._getImage(event.data, False)
                            self._populateImage(k, image)
                            self.userImages = imgTemp
                        except:
                            self.errorBox("Error loading image", "Unable to load image: " + str(event.data))
                        return
                for k, v in self.widgetManager.group(WIDGET_NAMES.Label).items():
                    if v == event.widget:
                        self.setLabel(k, event.data)
                        return
            elif widgType in ["Listbox"]:
                for k, v in self.widgetManager.group(WIDGET_NAMES.ListBox).items():
                    if v == event.widget:
                        self.addListItem(k, event.data)
                        return
            elif widgType in ["Message"]:
                for k, v in self.widgetManager.group(WIDGET_NAMES.Message).items():
                    if v == event.widget:
                        self.setMessage(k, event.data)
                        return
            else:
                self.warn("Unable to receive drop events: %s", widgType)


#####################################
# Language/Translation functions
#####################################
    def translate(self, key, default=None):
        """ returns a translated version of the key, using the current language
            if none found, returns the default value """
        return self._translate(key, "EXTERNAL", default)

    def _translateSound(self, key):
        """ internal wrapper to translate sounds """
        return self._translate(key, "SOUND", key)

    def _translatePopup(self, key, value):
        """ internal wrapper to translate popups """
        pop = self._translate(key, "POPUP")
        if pop is None:
            return (key, value)
        else:
            return (pop[0], pop[1])

    def _translate(self, key, section, default=None):
        """ returns the relevant key from the relevant section in the internally
            held translation dictionary - prepopulated when language was set """
        if key in self.translations[section]:
            return self.translations[section][key]
        else:
            return default

    def getLanguage(self):
        ''' returns the current language '''
        return self._language

    def setLanguage(self, language):
        """ wrapper for changeLanguage() """
        self.changeLanguage(language)

    # function to update languages
    def changeLanguage(self, language):
        """ changes the language used by the GUI
            will iterate through all widgets and update their text
            as well as populate a translation dictionary for later lookups """
        self._loadConfigParser()
        if not ConfigParser:
            self.error("Internationalisation not supported")
            return

        fileName = language.upper() + ".ini"
        gui.trace("Loading language file: %s", fileName)
        if not PYTHON2:
            try:
                with codecs.open(fileName, "r", "utf8") as langFile:
                    self.configParser.read_file(langFile)
            except FileNotFoundError:
                self.error("Invalid language, file not found: %s", fileName)
                return
        else:
            try:
                try:
                    with codecs.open(fileName, "r", "utf8") as langFile:
                        self.configParser.read_file(langFile)
                except AttributeError:
                    with codecs.open(fileName, "r", "utf8") as langFile:
                        self.configParser.readfp(langFile)
            except IOError:
                self.error("Invalid language, file not found: %s", fileName)
                return
            except ParsingError:
                self.error("Translation failed - language file contains errors, ensure there is no whitespace at the beginning of any lines.")
                return

        gui.trace("Switching to: %s", language)
        self._language = language
        self.translations = {"POPUP":{}, "SOUND":{}, "EXTERNAL":{}}
        # loop through each section, get the relative set of widgets
        # change the text
        for section in self.configParser.sections():
            getWidgets = True
            section = section.upper()
            gui.trace("\tSection: %s", section)

            # convert the section title to its code
            if section == "CONFIG":
                # skip the config section (for now)
                gui.trace("\tSkipping CONFIG")
                continue
            elif section == "TITLE":
                kind = WIDGET_NAMES.SubWindow
            elif section.startswith("TOOLTIP-"):
                kind = "TOOLTIP"
                getWidgets = False
            elif section in ["SOUND", "EXTERNAL", "POPUP"]:
                for (key, val) in self.configParser.items(section):
                    if section == "POPUP": val = val.strip().split("\n")
                    self.translations[section][key] = val
                    gui.trace("\t\t%s: %s", key, val)
                continue
            elif section == "MENUBAR":
                for (key, val) in self.configParser.items(section):
                    key = key.strip().split("-")
                    gui.trace("\t\t%s: %s", key, val)
                    if len(key) == 1:
                        try:
                            self.renameMenu(key[0], val)
                        except:
                            self.warn("Invalid key")
                    elif len(key) == 2:
                        try:
                            self.renameMenuItem(key[0], key[1], val)
                        except:
                            self.warn("Invalid key")
                continue
            else:
                try:
                    kind = WIDGET_NAMES.getIgnoreCase(section)
                except Exception:
                    self.warn("Invalid config section: %s", section)
                    continue

            # if necessary, use the code to get the widget list
            if getWidgets:
                widgets = self.widgetManager.group(kind)

            if kind in [WIDGET_NAMES.Scale]:
                self.warn("No text is displayed in %s. Maybe it has a Label?", section)
                continue
            elif kind in [WIDGET_NAMES.TextArea, WIDGET_NAMES.Meter, WIDGET_NAMES.PieChart, WIDGET_NAMES.Tree]:
                self.warn("No text is displayed in %s", section)
                continue
            elif kind in [WIDGET_NAMES.name(WIDGET_NAMES.SubWindow)]:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)

                    if key.lower() == "appjar":
                        self.setTitle(val)
                    elif key.lower() == "splash":
                        if self.splashConfig is not None:
                            gui.trace("\t\t Updated SPLASH to: %s", val)
                            self.splashConfig['text'] = val
                        else:
                            gui.trace("\t\t No SPLASH to update")
                    elif key.lower() == "statusbar":
                        gui.trace("\tSetting STATUSBAR: %s", val)
                        self.setStatusbarHeader(val)
                    else:
                        try:
                            widgets[key].title(val)
                        except KeyError:
                            self.warn("Invalid SUBWINDOW: %s", key)

            elif kind in [WIDGET_NAMES.ListBox]:
                for k in widgets.keys():
                    lb = widgets[k]

                    # convert data to a list
                    if self.configParser.has_option(section, k):
                        data = self.configParser.get(section, k)
                    else:
                        data = lb.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.updateListBox(k, data)

            elif kind in [WIDGET_NAMES.SpinBox]:
                for k in widgets.keys():
                    sb = widgets[k]

                    # convert data to a list
                    if self.configParser.has_option(section, k):
                        data = self.configParser.get(section, k)
                    else:
                        data = sb.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.changeSpinBox(k, data)

            elif kind in [WIDGET_NAMES.OptionBox]:
                for k in widgets.keys():
                    ob = widgets[k]

                    # convert data to a list
                    if self.configParser.has_option(section, k):
                        data = self.configParser.get(section, k)
                    else:
                        data = ob.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.changeOptionBox(k, data)

            elif kind in [WIDGET_NAMES.RadioButton]:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid RADIOBUTTON key: %s", key)
                    else:
                        try:
                            rbs = self.widgetManager.get(WIDGET_NAMES.RadioButton, keys[0])
                        except KeyError:
                            self.warn("Invalid RADIOBUTTON key: %s", keys[0])
                            continue
                        for rb in rbs:
                            if rb.DEFAULT_TEXT == keys[1]:
                                rb["text"] = val
                                break

            elif kind in [WIDGET_NAMES.TabbedFrame]:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid TABBEDFRAME key: %s", key)
                    else:
                        try:
                            self.setTabText(keys[0], keys[1], val)
                        except ItemLookupError:
                            self.warn("Invalid TABBEDFRAME: %s with TAB: %s" , keys[0], keys[1])

            elif kind in [WIDGET_NAMES.Properties]:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid PROPERTIES key: %s", key)
                    else:
                        try:
                            self.setPropertyText(keys[0], keys[1], val)
                        except ItemLookupError:
                            self.warn("Invalid PROPERTIES: %s", keys[0])
                        except KeyError:
                            self.warn("Invalid PROPERTY: %s", keys[1])

            elif kind == WIDGET_NAMES.Tree:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid GRID key: %s", key)
                    else:
                        if keys[1] not in ["actionHeading", "actionButton", "addButton"]:
                            self.warn("Invalid GRID label: %s for GRID: %s", keys[1], keys[0])
                        else:
                            try:
                                self.confGrid(keys[0], keys[1], val)
                            except ItemLookupError:
                                self.warn("Invalid GRID: %s", keys[0])

            elif kind == self.PAGEDWINDOW:
                for (key, val) in self.configParser.items(section):
                    gui.trace("\t\t%s: %s", key, val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid PAGEDWINDOW key: %s", key)
                    else:
                        if keys[1] not in ["prevButton", "nextButton", "title"]:
                            self.warn("Invalid PAGEDWINDOW label: %s for PAGEDWINDOW: %s", keys[1], keys[0])
                        else:
                            try:
                                widgets[keys[0]].config(**{keys[1]:val})
                            except KeyError:
                                self.warn("Invalid PAGEDWINDOW: %s", keys[0])

            elif kind == WIDGET_NAMES.Entry:
                for k in widgets.keys():
                    ent = widgets[k]

                    if self.configParser.has_option(section, k):
                        data = self.configParser.get(section, k)
                    else:
                        data = ent.DEFAULT_TEXT

                    gui.trace("\t\t%s: %s", k, data)
                    self.setEntryDefault(k, data)

            elif kind in [WIDGET_NAMES.Image]:
                for k in widgets.keys():
                    if self.configParser.has_option(section, k):
                        data = str(self.configParser.get(section, k))

                        try:
                            self.setImage(k, data)
                            gui.trace("\t\t%s: %s", k, data)
                        except:
                            self.error("Failed to update image: %s to: %s", k, data)
                    else:
                        gui.trace("No translation for: %s", k)

            elif kind in [WIDGET_NAMES.Label, WIDGET_NAMES.Button, WIDGET_NAMES.CheckBox, WIDGET_NAMES.Message,
                            WIDGET_NAMES.Link, WIDGET_NAMES.LabelFrame, self.TOGGLEFRAME]:
                for k in widgets.keys():
                    widg = widgets[k]

                    # skip validation labels - we don't need to translate them
                    try:
                        if kind == WIDGET_NAMES.Label and widg.isValidation:
                            gui.trace("\t\t%s: skipping, validation label", k)
                            continue
                    except:
                        pass

                    if self.configParser.has_option(section, k):
                        data = str(self.configParser.get(section, k))
                    else:
                        data = widg.DEFAULT_TEXT

                    gui.trace("\t\t%s: %s", k, data)
                    widg.config(text=data)

            elif kind == WIDGET_NAMES.Toolbar:
                for k in widgets.keys():
                    but = widgets[k]
                    if but.image is None:
                        if self.configParser.has_option(section, k):
                            data = str(self.configParser.get(section, k))
                        else:
                            data = but.DEFAULT_TEXT

                        gui.trace("\t\t%s: %s", k, data)
                        but.config(text = data)

            elif kind == "TOOLTIP":
                try:
                    kind = WIDGET_NAMES.name(WIDGET_NAMES.getIgnoreCase(section.split("-")[1]))
                    func = getattr(self, "set"+kind+"Tooltip")
                except KeyError:
                    self.warn("Invalid config section: TOOLTIP-%s", section)
                    return
                gui.trace("Parsing TOOLTIPs for: %s", kind)

                for (key, val) in self.configParser.items(section):
                    try:
                        func(key, val)
                    except ItemLookupError:
                        self.warn("Invalid TOOLTIP for: %s, with key: %s", kind, key)
                        continue
            else:
                self.warn("Unsupported widget: %s", section)
                continue

    language = property(getLanguage, changeLanguage)

    def showSplash(self, text="appJar", fill="#FF0000", stripe="#000000", fg="#FFFFFF", font=44):
        """ creates a splash screen to show at start up """
        self.splashConfig= {'text':text, 'fill':fill, 'stripe':stripe, 'fg':fg, 'font':font}


##################################################
### Stuff for logging
##################################################

    @staticmethod
    def setLogFile(fileName):
        """ sets the filename for logging messages """
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO, filename=fileName, format='%(asctime)s %(name)s:%(levelname)s: %(message)s')
        gui.info("Switched to logFile: %s", fileName)

    def _setLogFile(self, fileName):
        ''' necessary so we can access this as a property '''
        gui.setLogFile(fileName)

    def getLogFile(self):
        return logging.root.handlers[0].baseFilename

    logFile = property(getLogFile, _setLogFile)

    @staticmethod
    def setLogLevel(level):
        """ main function for setting the logging level
            provide one of: INFO, DEBUG, WARNING, ERROR, CRITICAL, EXCEPTION, None """
        logging.getLogger("appJar").setLevel(getattr(logging, level.upper()))
        gui.info("Log level changed to: %s", level)


    def getLogLevel(self):
        return logging.getLevelName(logging.getLogger("appJar").getEffectiveLevel())

    def _setLogLevel(self, level):
        ''' necessary so we can access this as a property '''
        gui.setLogLevel(level)

    logLevel = property(getLogLevel, _setLogLevel)

    @staticmethod
    def exception(message, *args):
        """ wrapper for logMessage - setting level to EXCEPTION """
        gui.logMessage(message, "EXCEPTION", *args)

    @staticmethod
    def critical(message, *args):
        """ wrapper for logMessage - setting level to CRITICAL """
        gui.logMessage(message, "CRITICAL", *args)

    @staticmethod
    def error(message, *args):
        """ wrapper for logMessage - setting level to ERROR """
        gui.logMessage(message, "ERROR", *args)

    @staticmethod
    def warn(message, *args):
        """ wrapper for logMessage - setting level to WARNING """
        gui.logMessage(message, "WARNING", *args)

    @staticmethod
    def debug(message, *args):
        """ wrapper for logMessage - setting level to DEBUG """
        gui.logMessage(message, "DEBUG", *args)

    @staticmethod
    def trace(message, *args):
        """ wrapper for logMessage - setting level to TRACE """
        gui.logMessage(message, "TRACE", *args)

    @staticmethod
    def info(message, *args):
        """ wrapper for logMessage - setting level to INFO """
        gui.logMessage(message, "INFO", *args)

    @staticmethod
    def logMessage(msg, level, *args):
        """ allows user to log a message - provide a message and a log level
            any %s tags in the message will be replaced by the relevant positional *args """
        frames = inspect.stack()
        # try to ensure we only log extras if we're called from above functions
        if frames[1][3] in ("exception", "critical", "error", "warn", "debug", "trace", "info"):

            callFrame = ""
            try:
                progName = gui.exe_file
                for s in frames:
                    if progName in s[1]:
                        callFrame = s
                        break
            except: pass

            if callFrame != "":
                callFrame = "Line " + str(callFrame[2])

            # user generated call
            if "appjar.py" not in frames[2][1] or frames[2][3] == "handlerFunction":
                if callFrame != "":
                    msg = "[" + callFrame + "]: "+str(msg)

            # appJar logging
            else:
                if callFrame != "":
                    msg = "["+callFrame + "->" + str(frames[2][2]) +"/"+str(frames[2][3])+"]: "+str(msg)
                else:
                    msg = "["+str(frames[2][2]) +"/"+str(frames[2][3])+"]: "+str(msg)

        logger = logging.getLogger("appJar")
        level = level.upper()

        if level == "EXCEPTION": logger.exception(msg, *args)
        elif level == "CRITICAL": logger.critical(msg, *args)
        elif level == "ERROR": logger.error(msg, *args)
        elif level == "WARNING": logger.warning(msg, *args)
        elif level == "INFO": logger.info(msg, *args)
        elif level == "DEBUG": logger.debug(msg, *args)
        elif level == "TRACE": logger.trace(msg, *args)

##############################################################
# Event Loop - must always be called at end
##############################################################
    def __enter__(self):
        """ allows gui to be used as a ContextManager """
        gui.trace("ContextManager: initialised")
        return self

    def __exit__(self, eType, eValue, eTrace):
        """ allows gui to be used as a ContextManager
            - calls the go() function """
        if eType is not None:
            self.error("ContextManager failed: %s", eValue)
            return False
        else:
            gui.trace("ContextManager: starting")
            self.go(startWindow=self.startWindow)
            return True

    def go(self, language=None, startWindow=None):
        """ Most important function! starts the GUI """

        # check if we have a command line language
        if self._language is not None:
            language = self._language

        # if language is populated, we are in internationalisation mode
        # call the changeLanguage function - to re-badge all the widgets
        if language is not None:
            self.changeLanguage(language)

        if self.splashConfig is not None:
            gui.trace("SPLASH: %s", self.splashConfig)
            splash = SplashScreen(
                            self.topLevel,
                            self.splashConfig['text'],
                            self.splashConfig['fill'],
                            self.splashConfig['stripe'],
                            self.splashConfig['fg'],
                            self.splashConfig['font']
                            )
            self.topLevel.withdraw()
            self._bringToFront(splash)

        # check the containers have all been stopped
        if len(self.containerStack) > 1:
            for i in range(len(self.containerStack) - 1, 0, -1):
                kind = self.containerStack[i]['type']
                if kind != WIDGET_NAMES.Pane:
                    self.warn("No stopContainer called on: %s", WIDGET_NAMES.name(kind))

        # update any trees
        for k in self.widgetManager.group(WIDGET_NAMES.Tree):
            self.generateTree(k)

        # create appJar menu, if no menuBar created
        if not self.hasMenu:
            self.addAppJarMenu()

        if self.platform == self.WINDOWS:
            self.menuBar.add_cascade(menu=self.widgetManager.get(WIDGET_NAMES.Menu, "WIN_SYS"))
        self.topLevel.config(menu=self.menuBar)

        if startWindow is not None:
            self.startWindow = startWindow
            gui.trace("startWindow parameter: %s", startWindow)

        # pack it all in & make sure it's drawn
        self.appWindow.pack(fill=BOTH)
        if self.useSettings:
            self.loadSettings(self.settingsFile)
        self.topLevel.update_idletasks()

        # check geom is set and set a minimum size, also positions the window if necessary
        if not self.topLevel.locationSet:
            self.setLocation('CENTER')

        if not hasattr(self.topLevel, 'ms'):
            self.setMinSize()

        if self.splashConfig is not None:
            time.sleep(3)
            splash.destroy()

        # user hasn't specified anything
        if self.startWindow is None:
            if not self.topLevel.displayed:
                gui.trace("topLevel has been manually hidden - not showing in go()")
            else:
                gui.trace("Showing topLevel")
                self._bringToFront()
                self.topLevel.deiconify()
        else:
            gui.trace("hiding main window")
            self.hide()
            sw = self.widgetManager.get(WIDGET_NAMES.SubWindow, startWindow)
            if sw.blocking:
                raise Exception("Unable to start appjar with a blocking subWindow")

            self.showSubWindow(startWindow)

        # required to make the gui reopen after minimising
        if self.GET_PLATFORM() == self.MAC:self.topLevel.createcommand('tk::mac::ReopenApplication', self._macReveal)

        # start the call back & flash loops
        self._poll()
        self._flash()

        # register start-up function
        if self.topLevel.startFunction is not None:
            self.topLevel.after_idle(self.topLevel.startFunction)

        # start the main loop
        try:
            self.topLevel.mainloop()
        except(KeyboardInterrupt, SystemExit) as e:
            gui.trace("appJar stopped through ^c or exit()")
            self.stop()
        except Exception as e:
            self.exception(e)
            self.stop()

    def setStartFunction(self, func):
        f = self.MAKE_FUNC(func, "start")
        self.topLevel.startFunction = f

    startFunction = property(fset=setStartFunction)

    def _macReveal(self):
        """ internal function to deiconify GUIs on mac """
        if self.topLevel.state() != "withdrawn":
            self.topLevel.deiconify()
        for k, v in self.widgetManager.group(WIDGET_NAMES.SubWindow).items():
            if v.state() == "normal":
                self.showSubWindow(k)

    def setStopFunction(self, function):
        """ Set a function to call when the GUI is quit. Must return True or False """
        tl = self._getTopLevel()
        tl.stopFunction = function
        # link to exit item in topMenu
        # only if in root
        if self._getContainerProperty('type') != WIDGET_NAMES.SubWindow:
            tl.createcommand('exit', self.stop)

    stopFunction = property(fset=setStopFunction)

    def setSetting(self, name, value):
        """ adds a setting to the settings file """
        self.externalSettings[name] = value

    def getSetting(self, name, default=None):
        """ gets a setting form the settings file """
        try: return self.externalSettings[name]
        except: return default

    def saveSettings(self, fileName="appJar.ini"):
        """ saves the current settings to a file
            called automatically by stop() of settings were loaded at start """
        self._loadConfigParser()
        if not ConfigParser:
            self.error("Unable to save config file - no configparser")
            return

        settings = ConfigParser()
        settings.optionxform = str
        settings.add_section('GEOM')
        geom = self.topLevel.geometry()
        ms = self.topLevel.minsize()
        ms = "%s,%s" % (ms[0], ms[1])
        settings.set('GEOM', 'geometry', geom)
        gui.trace("Save geom as: %s", geom)
        settings.set('GEOM', 'minsize', ms)
        settings.set('GEOM', "fullscreen", str(self.topLevel.attributes('-fullscreen')))
        settings.set('GEOM', "state", str(self.topLevel.state()))

        # get toolbar setting
        if self.tb.inUse:
            gui.trace("Saving toolbar settings")
            settings.add_section("TOOLBAR")
            settings.set("TOOLBAR", "pinned", str(self.tb.pinned))

        # get container settings
        for k, v in self.widgetManager.group(WIDGET_NAMES.ToggleFrame).items():
            gui.trace("Saving toggle %s", k)
            if "TOGGLES" not in settings.sections(): settings.add_section("TOGGLES")
            settings.set("TOGGLES", k, str(v.isShowing()))

        for k, v in self.widgetManager.group(WIDGET_NAMES.TabbedFrame).items():
            gui.trace("Saving tab %s", k)
            if "TABS" not in settings.sections(): settings.add_section("TABS")
            settings.set("TABS", k, str(v.getSelectedTab()))

        for k, v in self.widgetManager.group(WIDGET_NAMES.PagedWindow).items():
            gui.trace("Saving page %s", k)
            if "PAGES" not in settings.sections(): settings.add_section("PAGES")
            settings.set("PAGES", k, str(v.getPageNumber()))

        for k, v in self.widgetManager.group(WIDGET_NAMES.SubWindow).items():
            if "SUBWINDOWS" not in settings.sections(): settings.add_section("SUBWINDOWS")
            if v.shown:
                v.update()
                settings.set("SUBWINDOWS", k, "True")
                settings.add_section(k)
                settings.set(k, "geometry", v.geometry())
                ms = v.minsize()
                settings.set(k, 'minsize', "%s,%s" % (ms[0], ms[1]))
                settings.set(k, "state", v.state())
                gui.trace("Saving subWindow %s: geom=%s, state=%s, minsize=%s", k, v.geometry(), v.state(), ms)
            else:
                settings.set("SUBWINDOWS", k, "False")
                gui.trace("Skipping subwindow: %s", k)

        for k, v in self.externalSettings.items():
            if "EXTERNAL" not in settings.sections(): settings.add_section("EXTERNAL")
            settings.set("EXTERNAL", k, str(v))

        # pane positions?
        # sub windows geom & visibility
        # scrollpane x & y positions
        # language
        # ttk
        # debug level

        with open(fileName, 'w') as theFile:
            settings.write(theFile)

    def loadSettings(self, fileName="appJar.ini", useSettings=True):
        """ loads setting from a settings file, and adjusts the GUI to match
            called by go() function, if user has requested settings """
        self._loadConfigParser()
        if not ConfigParser:
            self.error("Unable to save config file - no configparser")
            return

        self.useSettings = useSettings

        settings = ConfigParser()
        settings.optionxform = str
        settings.read(fileName)

        if settings.has_option("GEOM", "geometry"):
            geom = settings.get("GEOM", "geometry")
            if not self.topLevel.ignoreSettings:
                size, loc = gui.SPLIT_GEOM(geom)
                gui.trace("Setting topLevel geom: %s as size: %s, loc: %s", geom, size, loc)
                if size[0] > 1:
                    self.setSize(*size)
                if loc[0] != -1:
                    self.setLocation(*loc)
            else:
                gui.trace("Ignoring topLevel geom: %s", geom)

        # not finished
        if settings.has_option("GEOM", "fullscreen"):
            fs = settings.getboolean('GEOM', "fullscreen")
            gui.trace("Set fullscreen to: %s", fs)
            if fs: self.setFullscreen()
            else: self.exitFullscreen()

        if settings.has_option("GEOM", "minsize"):
            self.topLevel.ms = settings.get('GEOM', "minsize").split(",")
            self._getTopLevel().minsize(self.topLevel.ms[0], self.topLevel.ms[1])
            gui.trace("Set minsize to: %s", self.topLevel.ms)

        if settings.has_option("GEOM", "state"):
            state = settings.get('GEOM', "state")
            if state in ["withdrawn", "zoomed"]:
                self._getTopLevel().state(state)

        if settings.has_option("TOOLBAR", "pinned") and self.tb.inUse:
            tb = settings.getboolean("TOOLBAR", "pinned")
            self.setToolbarPinned(tb)
            gui.trace("Set toolbar to: %s", tb)

        if "TOGGLES" in settings.sections():
            for k in settings.options("TOGGLES"):
                try:
                    if self.getToggleFrameState(k) != settings.getboolean("TOGGLES", k):
                        self.toggleToggleFrame(k)
                except ItemLookupError:
                    gui.error("Settings error, invalid TOGGLES name: %s - discarding", k)

        if "TABS" in settings.sections():
            for k in settings.options("TABS"):
                try:
                    self.setTabbedFrameSelectedTab(k, settings.get("TABS", k))
                except ItemLookupError:
                    gui.error("Settings error, invalid TABS name: %s - discarding", k)

        if "PAGES" in settings.sections():
            for k in settings.options("PAGES"):
                try:
                    self.setPagedWindowPage(k, settings.getint("PAGES", k))
                except ItemLookupError:
                    gui.error("Settings error, invalid PAGES name: %s - discarding", k)

        if "SUBWINDOWS" in settings.sections():
            for k in settings.options("SUBWINDOWS"):
                if settings.getboolean("SUBWINDOWS", k):
                    gui.trace("Loading settings for %s", k)
                    try:
                        tl = self.widgetManager.get(WIDGET_NAMES.SubWindow, k)
                        # process the geom settings
                        if settings.has_option(k, "geometry"):
                            geom = settings.get(k, "geometry")
                            size, loc = gui.SPLIT_GEOM(geom)
                            if size[0] > 1:
                                gui.trace("Setting size: %s", size)
                                tl.geometry("%sx%s" % (size[0], size[1]))
                                tl.shown = True
                            else:
                                gui.trace("Skipping size: %s", size)
                            if loc[0] > -1:
                                gui.trace("Setting location: %s", loc)
                                self.setSubWindowLocation(k, *loc)
                            else:
                                gui.trace("Skipping location: %s", loc)
                        else:
                            gui.trace("No location found")

                        if settings.has_option(k, "minsize"):
                            ms = settings.get(k, "minsize").split(",")
                            self.setMinSize(tl, ms)

                        # set the state - if there' no startWindow
                        if self.startWindow is None:
                            try:
                                tl.state(settings.get(k, "state"))
                                gui.trace("Set state=%s", tl.state())
                            except: pass # no state found
                    except ItemLookupError:
                        gui.error("Settings error, invalid SUBWINDOWS name: %s - discarding.", k)
                else:
                    gui.trace("Skipping settings for %s", k)

        if "EXTERNAL" in settings.sections():
            for k in settings.options("EXTERNAL"):
                self.externalSettings[k] = settings.get("EXTERNAL", k)

    def stop(self, event=None):
        """ Closes the GUI. If a stop function is set, will only close the GUI if True """
        theFunc = self._getTopLevel().stopFunction
        if theFunc is None or theFunc():

            if self.useSettings:
                self.saveSettings(self.settingsFile)

            # stop the after loops
            self.alive = False
            self.topLevel.after_cancel(self.pollId)
            self.topLevel.after_cancel(self.flashId)
            if self.preloadAnimatedImageId:
                self.topLevel.after_cancel(self.preloadAnimatedImageId)
            if self.processQueueId:
                self.topLevel.after_cancel(self.processQueueId)

            # stop any animations
            for key in self.widgetManager.group(WIDGET_NAMES.AnimationID):
                self.topLevel.after_cancel(self.widgetManager.get(WIDGET_NAMES.AnimationID, key))

            # stop any maps
            for key in self.widgetManager.group(WIDGET_NAMES.Map):
                self.widgetManager.get(WIDGET_NAMES.Map, key).stopUpdates()

            # stop any sounds, ignore error when not on Windows
            try:
                self.stopSound()
            except:
                pass

            self.topLevel.quit()
            if not self.fastStop: self.topLevel.destroy()
            self.__class__.instantiated = False
            gui.info("--- GUI stopped ---")

    def setFastStop(self, fast=True):
        self._fastStop = fast

    def getFastStop(self):
        return self._fastStop

    fastStop = property(getFastStop, setFastStop)

#####################################
# Functions for configuring polling events
#####################################
    def setPollTime(self, time):
        """ Set a frequency for executing queued functions
            events will fire in order of being added, after sleeping for time """
        self.pollTime = time

    def registerEvent(self, func):
        """ Queue a function, to be executed every poll time """
        self.events.append(func)

    def after(self, delay_ms, callback=None, *args):
        """ wrapper for topLevel after function
            schedules the callback function to happen in x seconds
            returns an ID, allowing the event to be cancelled """
        return self.topLevel.after(delay_ms, callback, *args)

    def afterIdle(self, callback, *args):
        """ wrapper for topLevel after_idle function
            schedules the callback function to happen in x seconds
            returns an ID, allowing the event to be cancelled """
        return self.after_idle(callback, *args)

    def after_idle(self, callback, *args):
        """ wrapper for topLevel after_idle function
            schedules the callback function to happen in x seconds
            returns an ID, allowing the event to be cancelled """
        return self.topLevel.after_idle(callback, *args)

    def afterCancel(self, afterId):
        """ wrapper for topLevel after_cancel function
            tries to cancel the specified callback """
        return self.after_cancel(afterId)

    def after_cancel(self, afterId):
        """ wrapper for topLevel after_cancel function
            tries to cancel the specified callback """
        return self.topLevel.after_cancel(afterId)

    def queueFunction(self, func, *args, **kwargs):
        """ adds the specified function & arguments to the event queue
        Functions in the event queue are actioned by the gui's main thread

        :param func: the function to call
        :param *args: any number of ordered arguments
        :param **kwargs: any number of named arguments
        :raises Full: if unable to add the function to the queue
        """
        self._loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            self.eventQueue.put((5, func, args, kwargs), block=False)

    def queuePriorityFunction(self, func, *args, **kwargs):
        """ queues the function with a higher priority - not working yet """
        self._loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            self.eventQueue.put((1, func, args, kwargs), block=False)

    def _processEventQueue(self):
        """ internal function to process events in the event queue
            put there by queue function """
        if not self.alive: return
        if not self.eventQueue.empty():
            priority, func, args, kwargs = self.eventQueue.get()
            gui.trace("FUNCTION: %s(%s)", func, args)
            func(*args, **kwargs)

        self.processQueueId = self.after(self.EVENT_SPEED, self._processEventQueue)

    def thread(self, func, *args, **kwargs):
        """ will run the supplied function in a separate thread

        param func: the function to run
        """
        self._loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            t = Thread(group=None, target=func, name=None, args=args, kwargs=kwargs)
            t.daemon = True
            t.start()

    def callback(self, *args, **kwargs):
        """Shortner for threadCallback."""
        return self.threadCallback(*args, **kwargs)

    def threadCallback(self, func, callback, *args, **kwargs):
        """Run a given method in a new thread with passed arguments.
           When func completes call the callback with the result.

           :param func: Method that returns the result.
           :param callback: Method that receives the result.
           :param args: Positional arguments for func.
           :param kwargs: Keyword args for func.
        """
        def innerThread(func, callback, *args, **kwargs):
            result = func(*args, **kwargs)
            self.queueFunction(callback, result)

        if not callable(func) or not callable(callback):
            gui.error("Function (or callback) method isn't callable!")
            return
        self.thread(innerThread, func, callback, *args, **kwargs)

    # internal function, called by 'after' function, after sleeping
    def _poll(self):
        """ internal function, called by 'after' function, after sleeping """
        if not self.alive: return
        # run any registered actions
        for e in self.events:
            # execute the event
            e()
        self.pollId = self.topLevel.after(self.pollTime, self._poll)

    def _windowEvent(self, event):
        """ called whenever the GUI updates - does nothing """
        new_width = self.topLevel.winfo_width()
        new_height = self.topLevel.winfo_height()

    def enableEnter(self, func, replace=False):
        """ Binds <Return> to the specified function - all widgets """
        self.bindKey("Return", func, replace)

    def disableEnter(self):
        """ unbinds <Return> from all widgets """
        self.unbindKey("Return")

    def _enterWrapper(self, func):
        if func is None:
            self.disableEnter()
        else:
            self.enableEnter(func, replace=True)

    enterKey = property(fset=_enterWrapper)

    def bindKeys(self, keys, func):
        """ bind the specified keys, to the specified function, for all widgets """
        for key in keys:
            self.bindKey(key, func)

    def bindKey(self, key, func, replace=False):
        """ bind the specified key, to the specified function, for all widgets """
        if replace:
            try: self.unbindKey(key)
            except: pass
        # for now discard the Event...
        myF = self.MAKE_FUNC(func, key)
        binding = EventBinding(key, myF, self._getTopLevel(), menuBinding=False)
        try:
            self.widgetManager.add(WIDGET_NAMES.Bindings, binding.displayName, binding)
            binding.createBindings()
        except ItemLookupError:
            raise ItemLookupError('Unable to bind key ' + binding.displayName + ' - binding already exists')

    def unbindKeys(self, keys):
        """ unbinds the specified keys from whatever functions they are bound to """
        for key in keys:
            self.unbindKey(key)

    def unbindKey(self, key):
        """ unbinds the specified key from whatever functions it is bound to """
        if key[0] == "<":
            gui.warn("Shortcuts should not include chevrons: %s", key)
            key= key[1:-1]
        self.widgetManager.get(WIDGET_NAMES.Bindings, key).removeBindings()
        self.widgetManager.remove(WIDGET_NAMES.Bindings, key)

    def _isMouseInWidget(self, w):
        """ helper - returns True if the mouse is in the specified widget """
        l_x = w.winfo_rootx()
        l_y = w.winfo_rooty()

        if l_x <= w.winfo_pointerx() <= l_x + \
                w.winfo_width() and l_y <= w.winfo_pointery() <= l_y + w.winfo_height():
            return True
        else:
            return False

    # function to give a clicked widget the keyboard focus
    def _grabFocus(self, e):
        """ gives the specified widget the focus """
        e.widget.focus_set()


#####################################
# FUNCTIONS for configuring GUI settings
#####################################

    def setSize(self, geom, height=None, ignoreSettings=None):
        """ called to update screen geometry
            can take a geom string, or a width & height
            can override ignoreSettings if desired """
        container = self._getTopLevel()
        if ignoreSettings is not None:
            container.ignoreSettings = ignoreSettings

        try:
            geom = geom.lower()
        except:
            # ignore - other data types allowed
            pass

        if geom == "fullscreen":
            self.setFullscreen()
        elif geom is not None:
            if height is not None:
                geom=(geom, height)
            elif not isinstance(geom, list) and not isinstance(geom, tuple):
                geom, loc = gui.SPLIT_GEOM(geom)

            size = "%sx%s" % (int(geom[0]), int(geom[1]))
            gui.trace("Setting size: %s", size)

            # warn the user that their geom is not big enough
            dims = gui.GET_DIMS(container)
            if geom[0] < dims["b_width"] or geom[1] < dims["b_height"]:
                self.trace("Specified dimensions (%s, %s) less than requested dimensions (%s, %s)",
                        geom[0], geom[1], dims["b_width"], dims["b_height"])

            # and set it as the minimum size
            if not hasattr(container, 'ms'):
                self.setMinSize(container, geom)

            self.exitFullscreen()
            container.geometry(size)

    def getSize(self):
        container = self._getTopLevel()
        size, loc = gui.SPLIT_GEOM(container.geometry())
        return size

    size = property(getSize, setSize)

    def setMinSize(self, container=None, size=None):
        """ sets a minimum size for the specified container - defaults to the whole GUI """
        if container is None: container = self.topLevel
        if size is None: size = (gui.GET_DIMS(container)["r_width"], gui.GET_DIMS(container)["r_height"])
        container.ms = size
        container.minsize(size[0], size[1])
        gui.trace("Minsize set to: %s", size)

    def setLocation(self, x, y=None, ignoreSettings=None, win=None, up=0):
        """ called to set the GUI's position on screen """
        if win is None:
            win = self._getTopLevel()
        gui.SET_LOCATION(x, y, ignoreSettings, win, up)

    def getLocation(self):
        container = self._getTopLevel()
        size, loc = gui.SPLIT_GEOM(container.geometry())
        return loc

    location = property(getLocation, setLocation)

    def _bringToFront(self, win=None):
        """ called to make sure this window is on top of other windows """
        if win is None:
            win = self.topLevel
            top = self.top
        else:
            top = win.attributes('-topmost')

        if self.platform == self.MAC:
            import subprocess
            tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is {0} to true'
            script = tmpl.format(os.getpid())
            subprocess.check_call(['/usr/bin/osascript', '-e', script])
            win.after( 0, lambda: win.attributes("-topmost", top))
#            val=os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "''' + PY_NAME + '''" to true' ''')
            win.lift()
        elif self.platform == self.WINDOWS:
            win.lift()
        elif self.platform == self.LINUX:
            win.lift()

    def setFullscreen(self, title=None):
        """ sets the specified window to be fullscreen
            if no title, will set the main GUI """
        try:
            container = self.widgetManager.get(WIDGET_NAMES.SubWindow, title)
        except:
            container = self._getTopLevel()

        if not container.isFullscreen:
            container.isFullscreen = True
            container.attributes('-fullscreen', True)
            container.escapeBindId = container.bind('<Escape>', self.MAKE_FUNC(self.exitFullscreen, container), "+")

    def getFullscreen(self, title=None):
        if title is None:
            container = self._getTopLevel()
        else:
            container = self.widgetManager.get(WIDGET_NAMES.SubWindow, title)

        return container.isFullscreen

    def setOnTop(self, stay=True):
        self._getTopLevel().attributes("-topmost", stay)
        gui.trace("Staying on top set to: %s", stay)

    def getOnTop(self):
        return self._getTopLevel().attributes("-topmost") == 1

    top = property(getOnTop, setOnTop)

    def _changeFullscreen(self, flag):
        if flag: self.setFullscreen()
        else: self.exitFullscreen()

    fullscreen = property(getFullscreen, _changeFullscreen)

    def exitFullscreen(self, container=None):
        """ turns off fullscreen mode for the specified window """
        if container is None or isinstance(container, UNIVERSAL_STRING):
            try:
                container = self.widgetManager.get(WIDGET_NAMES.SubWindow, container)
            except:
                container = self._getTopLevel()

        if container.isFullscreen:
            container.isFullscreen = False
            container.attributes('-fullscreen', False)
            if container.escapeBindId is not None:
                container.unbind('<Escape>', container.escapeBindId)
            with PauseLogger():
                self._doTitleBar()
            return True
        else:
            return False

    def setPadX(self, x=0):
        """ set the current container's external grid padding """
        self.containerStack[-1]['padx'] = x

    def setPadY(self, y=0):
        """ set the current container's external grid padding """
        self.containerStack[-1]['pady'] = y

    def setPadding(self, x, y=None):
        """ sets the padding around the border of the current container """
        x, y = gui.PARSE_TWO_PARAMS(x, y)
        self.containerStack[-1]['padx'] = x
        self.containerStack[-1]['pady'] = y

    def getPadding(self):
        return self._getContainerProperty('padx'), self._getContainerProperty('pady')

    padding = property(getPadding, setPadding)

    def config(self, **kwargs):
        self.configure(**kwargs)

    def configure(self, **kwargs):
        title = kwargs.pop("title", None)
        icon = kwargs.pop("icon", None)
        transparency = kwargs.pop("transparency", None)
        visible = kwargs.pop("visible", None)
        top = kwargs.pop("top", None)

        padding = kwargs.pop("padding", None)
        inPadding = kwargs.pop("inPadding", None)
        guiPadding = kwargs.pop("guiPadding", None)

        size = kwargs.pop("size", None)
        location = kwargs.pop("location", None)
        fullscreen = kwargs.pop("fullscreen", None)
        resizable = kwargs.pop("resizable", None)

        sticky = kwargs.pop("sticky", None)
        stretch = kwargs.pop("stretch", None)
        expand = kwargs.pop("expand", None)
        row = kwargs.pop("row", None)
        colspan = kwargs.pop("colspan", None)
        rowspan = kwargs.pop("rowspan", None)

        fg = kwargs.pop("fg", None)
        bg = kwargs.pop("bg", None)
        font = kwargs.pop("font", None)
        buttonFont = kwargs.pop("buttonFont", None)
        labelFont = kwargs.pop("labelFont", None)
        inputFont = kwargs.pop("inputFont", None)
        statusFont = kwargs.pop("statusFont", None)
        ttkTheme = kwargs.pop("ttkTheme", None)

        editMenu = kwargs.pop("editMenu", None)
        # two possible names
        stopFunction = kwargs.pop("stop", kwargs.pop("stopFunction", None))
        startFunction = kwargs.pop("start", kwargs.pop("startFunction", None))
        fastStop = kwargs.pop("fastStop", None)
        enterKey = kwargs.pop("enterKey", None)
        logLevel = kwargs.pop("log", kwargs.pop("logLevel", None))
        logFile = kwargs.pop("file", kwargs.pop("logFile", None))
        language = kwargs.pop("language", None)

        for k, v in kwargs.items():
            gui.error("Invalid config parameter: %s, %s", k, v)

        if title is not None: self.title = title
        if icon is not None: self.icon = icon
        if transparency is not None: self.transparency = transparency
        if visible is not None: self.visible = visible
        if top is not None: self.top = top

        if padding is not None: self.padding = padding
        if inPadding is not None: self.inPadding = inPadding
        if guiPadding is not None: self.guiPadding = guiPadding

        if size is not None: self.size = size
        if location is not None: self.location = location
        if fullscreen is not None: self.fullscreen = fullscreen
        if resizable is not None: self.resizable = resizable

        if sticky is not None: self.sticky = sticky
        if expand is not None: self.expand = expand
        if stretch is not None: self.stretch = stretch
        if row is not None: self.row = row
        if rowspan is not None: self.rowspan = rowspan
        if colspan is not None: self.colspan = colspan

        if fg is not None: self.fg = fg
        if bg is not None: self.bg = bg

        if font is not None: self.font = font
        if labelFont is not None: self.labelFont = labelFont
        if buttonFont is not None: self.buttonFont = buttonFont
        if inputFont is not None: self.inputFont = inputFont
        if statusFont is not None: self.statusFont = statusFont
        if ttkTheme is not None: self.ttkTheme = ttkTheme

        if editMenu is not None: self.editMenu = editMenu
        if stopFunction is not None: self.stopFunction = stopFunction
        if startFunction is not None: self.startFunction = startFunction
        if fastStop is not None: self.fastStop = fastStop
        if enterKey is not None: self.enterKey = enterKey
        if logLevel is not None: self.logLevel = logLevel
        if logFile is not None: self.logFile = logFile
        if language is not None: self.language = language

    def setGuiPadding(self, x, y=None):
        """ sets the padding around the border of the GUI """
        x, y = gui.PARSE_TWO_PARAMS(x, y)
        self.containerStack[0]['container'].config(padx=x, pady=y)

    def getGuiPadding(self):
        return int(str(self.containerStack[0]['container'].cget('padx'))), int(str(self.containerStack[0]['container'].cget('pady')))

    guiPadding = property(getGuiPadding, setGuiPadding)

    # sets the current containers internal padding
    def setIPadX(self, x=0):
        self.setInPadX(x)

    def setIPadY(self, y=0):
        self.setInPadY(y)

    def setIPadding(self, x, y=None):
        self.setInPadding(x, y)

    def setInPadX(self, x=0):
        self.containerStack[-1]['ipadx'] = x

    def setInPadY(self, y=0):
        self.containerStack[-1]['ipady'] = y

    def setInPadding(self, x, y=None):
        x, y = gui.PARSE_TWO_PARAMS(x, y)
        self.containerStack[-1]['ipadx'] = x
        self.containerStack[-1]['ipady'] = y

    def getInPadding(self):
        return self._getContainerProperty('ipadx'), self._getContainerProperty('ipady')

    inPadding = property(getInPadding, setInPadding)

    # set an override sticky for this container
    def setSticky(self, sticky):
        self.containerStack[-1]['sticky'] = sticky

    def getSticky(self):
        return self._getContainerProperty('sticky')

    # property for setTitle
    sticky = property(getSticky, setSticky)

    # this tells widgets what to do when GUI is resized
    def setStretch(self, exp):
        self.setExpand(exp)

    def getStretch(self):
        return self.getExpand()

    stretch = property(getStretch, setStretch)

    def getExpand(self):
        return self._getContainerProperty('expand')

    def setExpand(self, exp):
        if exp is None or exp.lower() == "none":
            self.containerStack[-1]['expand'] = "NONE"
        elif exp.lower() == "row":
            self.containerStack[-1]['expand'] = "ROW"
        elif exp.lower() == "column":
            self.containerStack[-1]['expand'] = "COLUMN"
        else:
            self.containerStack[-1]['expand'] = "ALL"

    expand = property(getExpand, setExpand)

    def RANDOM_COLOUR(self):
        return self.getRandomColour()

    def getRandomColour(self):
        """ generates a random colour """
        self._loadRandom()
        de=("%02x"%random.randint(0,255))
        re=("%02x"%random.randint(0,255))
        we=("%02x"%random.randint(0,255))
        return "#"+de+re+we

    randomColour = property(getRandomColour)

    def getFonts(self):
        fonts = list(tkFont.families())
        fonts.sort()
        return fonts

    fonts = property(getFonts)

    def increaseFont(self):
        self.increaseLabelFont()
        self.increaseButtonFont()

    def decreaseFont(self):
        self.decreaseLabelFont()
        self.decreaseButtonFont()

    def increaseButtonFont(self):
        self.setButtonFont(size=self._buttonFont['size'] + 1)

    def decreaseButtonFont(self):
        self.setButtonFont(size=self._buttonFont['size'] - 1)

    def increaseLabelFont(self):
        self.setLabelFont(size=self._labelFont['size'] + 1)

    def decreaseLabelFont(self):
        self.setLabelFont(size=self._labelFont['size'] - 1)

    def setFont(self, *args, **kwargs):
        self.setInputFont(*args, **kwargs)
        self.setLabelFont(*args, **kwargs)
        self.setButtonFont(*args, **kwargs)

    def getFont(self):
        return self._getContainerProperty('labelFont').actual()

    font = property(getFont, setFont)

    def _fontHelper(self, font, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], int):
                kwargs={'size':args[0]}
            elif isinstance(args[0], dict):
                kwargs=args[0]
            elif isinstance(args[0], tkFont.Font):
                gui.trace("%s set to new object", font)
                if font != "statusFont": self.containerStack[-1][font]=args[0]
                else: self._statusFont=args[0]
                return None
        if font != "statusFont":
            self._getContainerProperty(font).config(**kwargs)
            f = self._getContainerProperty(font).actual()['family'].lower()
        else:
            self._statusFont.config(**kwargs)
            f = self._statusFont.actual()['family'].lower()

        if 'family' in kwargs and kwargs['family'].lower() != f:
            gui.error("Failed to adjust %s to %s.", font, kwargs['family'])
        return kwargs

    def setInputFont(self, *args, **kwargs):
        self._fontHelper('inputFont', *args, **kwargs)

    def getInputFont(self):
        return self._getContainerProperty('inputFont').actual()

    inputFont = property(getInputFont, setInputFont)

    def setStatusFont(self, *args, **kwargs):
        self._fontHelper('statusFont', *args, **kwargs)

    def getStatusFont(self):
        return self._statusFont.actual()

    statusFont = property(getStatusFont, setStatusFont)

    def setButtonFont(self, *args, **kwargs):
        self._fontHelper('buttonFont', *args, **kwargs)

    def getButtonFont(self):
        return self._getContainerProperty('buttonFont').actual()

    buttonFont = property(getButtonFont, setButtonFont)

    def setLabelFont(self, *args, **kwargs):
        kwargs = self._fontHelper('labelFont', *args, **kwargs)
        if kwargs is not None:
            self.tableFont.config(**kwargs)

            # need better way to register font change events on tables
            for k, v in self.widgetManager.group(WIDGET_NAMES.Table).items():
                v.config(font=self.tableFont)

            linkArgs = kwargs.copy()
            linkArgs['underline'] = True
            linkArgs['weight'] = 'bold'
            self._linkFont.config(**linkArgs)

    def getLabelFont(self):
        return self._getContainerProperty('labelFont').actual()

    labelFont = property(getLabelFont, setLabelFont)

    # need to set a default colour for container
    # then populate that field
    # then use & update that field accordingly
    # all widgets will then need to use it
    # and here we update all....
    def setFg(self, colour, override=False):
        if not self.ttkFlag:
            self.containerStack[-1]['fg']=colour
            gui.SET_WIDGET_FG(self._getContainerProperty('container'), colour, override)

            for child in self._getContainerProperty('container').winfo_children():
                if not self._isWidgetContainer(child):
                    gui.SET_WIDGET_FG(child, colour, override)
        else:
            gui.trace("In ttk mode - trying to set FG to %s", colour)
            self.ttkStyle.configure("TLabel", foreground=colour)
            self.ttkStyle.configure("TFrame", foreground=colour)

    def getBg(self):
        if self._getContainerProperty('type') == WIDGET_NAMES.RootPage:
            if not self.ttkFlag:
                return self.bgLabel.cget("bg")
            else:
                return self.bgLabel.cget("background")
        else:
            if not self.ttkFlag:
                return self._getContainerProperty('container').cget("bg")
            else:
                return None

    def getFg(self):
        return self._getContainerProperty("fg")

    fg = property(getFg, setFg)

    # self.topLevel = Tk()
    # self.appWindow = CanvasDnd, fills all of self.topLevel
    # self.tb = Frame, at top of appWindow
    # self.container = Frame, at bottom of appWindow => C_ROOT container
    # self.bglabel = Label, filling all of container
    def setBg(self, colour, override=False, tint=False):
        if not self.ttkFlag:
            if self._getContainerProperty('type') == WIDGET_NAMES.RootPage:
# removed this - it makes the screen do funny stuff
#                self.appWindow.config(background=colour)
                self.bgLabel.config(background=colour)

            self._getContainerProperty('container').config(background=colour)

            for child in self._getContainerProperty('container').winfo_children():
                if not self._isWidgetContainer(child):

                    # horrible hack to deal with weird ScrolledText
                    # winfo_children returns ScrolledText as a Frame
                    # therefore can't call some functions
                    # this gets the ScrolledText version
                    if gui.GET_WIDGET_CLASS(child) == "Frame":
                        for val in self.widgetManager.group(WIDGET_NAMES.TextArea).values():
                            if str(val) == str(child):
                                child = val
                                break

                    gui.SET_WIDGET_BG(child, colour, override, tint)
        else:
            gui.trace("In ttk mode - trying to set BG to %s", colour)
            self.ttkStyle.configure(".", background=colour)

    bg = property(getBg, setBg)

    @staticmethod
    def _isWidgetContainer(widget):
        try:
            if widget.isContainer:
                return True
        except:
            pass
        return False

    def setResizable(self, canResize=True):
        self._getTopLevel().isResizable = canResize
        if self._getTopLevel().isResizable:
            self._getTopLevel().resizable(True, True)
        else:
            self._getTopLevel().resizable(False, False)

    def getResizable(self):
        return self._getTopLevel().isResizable

    resizable = property(getResizable, setResizable)

    def _doTitleBar(self):
        if self.platform == self.MAC:
            self.warn("Title bar hiding doesn't work on MAC - app may become unresponsive.")
        elif self.platform == self.LINUX:
            self.warn("Title bar hiding doesn't work on LINUX - app may become unresponsive.")
        self._getTopLevel().overrideredirect(not self.hasTitleBar)

    def hideTitleBar(self):
        self.hasTitleBar = False
        self._doTitleBar()

    def showTitleBar(self):
        self.hasTitleBar = True
        self._doTitleBar()

    # function to set the window's title
    def setTitle(self, title):
        self._getTopLevel().title(title)

    # function to get the window title
    def getTitle(self):
        return self._getTopLevel().title()

    # property for setTitle
    title = property(getTitle, setTitle)

    # set an icon
    def setIcon(self, image):
        container = self._getTopLevel()
        container.winIcon = image
        if image.endswith('.ico'):
            container.wm_iconbitmap(image)
        else:
            icon = self._getImage(image)
            container.iconphoto(True, icon)

    def getIcon(self):
        container = self._getTopLevel()
        return container.winIcon

    # property for setTitle
    icon = property(getIcon, setIcon)

    def _getCanvas(self, param=-1):
        if len(self.containerStack) > 1 and self.containerStack[param]['type'] == WIDGET_NAMES.SubWindow:
            return self.containerStack[param]['container']
        elif len(self.containerStack) > 1:
            return self._getCanvas(param-1)
        else:
            return self.topLevel

    def _getTopLevel(self):
        if len(self.containerStack) > 1 and self._getContainerProperty('type') == WIDGET_NAMES.SubWindow:
            return self._getContainerProperty('container')
        else:
            return self.topLevel

    # make the window transparent (between 0 & 1)
    def setTransparency(self, percentage):
        if self.platform == self.LINUX:
            self.warn("Transparency not supported on LINUX")
        else:
            if percentage > 1:
                percentage = float(percentage) / 100
            self._getTopLevel().attributes("-alpha", percentage)

    def getTransparency(self):
        return self._getTopLevel().attributes("-alpha") * 100

    # property for setTransparency
    transparency = property(getTransparency, setTransparency)

##############################
# functions to deal with tabbing and right clicking
##############################
    def _focusNextWindow(self, event):
        event.widget.tk_focusNext().focus_set()
        nowFocus = self.topLevel.focus_get()
        if isinstance(nowFocus, Entry):
            nowFocus.select_range(0, END)
        return("break")

    def _focusLastWindow(self, event):
        event.widget.tk_focusPrev().focus_set()
        nowFocus = self.topLevel.focus_get()
        if isinstance(nowFocus, Entry):
            nowFocus.select_range(0, END)
        return("break")

    # creates relevant bindings on the widget
    def _addRightClickMenu(self, widget):
        if self.platform in [self.WINDOWS, self.LINUX]:
            widget.bind('<Button-3>', self._rightClick)
        else:
            widget.bind('<Button-2>', self._rightClick)

    def _rightClick(self, event, menu="EDIT"):
        event.widget.focus()
        if menu == "EDIT":
            if self._prepareCopyAndPasteMenu(event):
                self.widgetManager.get(WIDGET_NAMES.Menu, menu).focus_set()
                self.widgetManager.get(WIDGET_NAMES.Menu, menu).post(event.x_root - 10, event.y_root - 10)
        else:
            self.widgetManager.get(WIDGET_NAMES.Menu, menu).focus_set()
            self.widgetManager.get(WIDGET_NAMES.Menu, menu).post(event.x_root - 10, event.y_root - 10)
        return "break"

#####################################
# FUNCTION to configure widgets
#####################################

    def configureAllWidgets(self, kind, option, value):
        items = list(self.widgetManager.group(kind))
        self.configureWidgets(kind, items, option, value)

    def configureWidgets(self, kind, names, option, value):
        if not isinstance(names, list):
            self.configureWidget(kind, names, option, value)
        else:
            for widg in names:
                # incase 2D array, eg. buttons
                if isinstance(widg, list):
                    for widg2 in widg:
                        self.configureWidget(kind, widg2, option, value)
                else:
                    self.configureWidget(kind, widg, option, value)

    def getWidget(self, kind, name, val=None):
        # if val is set (RadioButtons) - append it
        if val is not None: name+= "-" + val
        return self.widgetManager.get(kind, name)

    def getWidgetProperty(self, kind, name, val, prop):
        return self.getWidget(kind, name, val).cget(prop)

    def addWidget(self, title, widg, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a generic widget to the appJar grid manager '''
        self.widgetManager.verify(WIDGET_NAMES.Widget, title)
        self._positionWidget(widg, row, column, colspan, rowspan)
        self.widgetManager.add(WIDGET_NAMES.Widget, title, widg)

    def _getWidgetList(self, kind, name, limit):
        # gets a list of items of this type
        # limit is used to only get a single radio button - for events
        if kind == WIDGET_NAMES.RadioButton:
            items = self.widgetManager.group(kind)
            new_items = []
            for k, v in items.items():
                if k.startswith(name+"-"):
                    new_items.append(v)

            if len(new_items) == 0:
                raise Exception("No RadioButtons found with that name " + name)
            else:
                items = new_items
                # stops multiple events...
                if limit: items = [items[0]]
        else:
            # get the list of items for this type, and validate the widget is in the list
            self.widgetManager.check(kind, name)
            items = self.widgetManager.group(kind)
            items = [items[name]]
        return items

    def configureWidget(self, kind, name, option, value, key=None, deprecated=False):
        gui.trace("Configuring: %s of %s with %s of %s", name, kind, option, value)
        # warn about deprecated functions
        if deprecated:
            self.warn("Deprecated config function (%s) used for %s -> %s use %s deprecated", option, WIDGET_NAMES.name(kind), name, deprecated)

        # will return multiple items if radio button...
        items = self._getWidgetList(kind, name, limit=option in ['change', 'command'])

        # loop through each item, and try to reconfigure it
        # this will often fail - widgets have varied config options
        for item in items:
            try:
                if option == 'background':
                    gui.SET_WIDGET_BG(item, value, True)
                elif option == 'foreground':
                    gui.SET_WIDGET_FG(item, value, True)
                elif option == 'disabledforeground':
                    item.config(disabledforeground=value)
                elif option == 'disabledbackground':
                    item.config(disabledbackground=value)
                elif option == 'activeforeground':
                    item.config(activeforeground=value)
                elif option == 'activebackground':
                    item.config(activebackground=value)
                elif option == 'inactiveforeground':
                    if kind in [WIDGET_NAMES.TabbedFrame, WIDGET_NAMES.Table]:
                        item.config(inactiveforeground=value)
                    else:
                        self.warn("Error configuring %s: can't set inactiveforeground", name )
                elif option == 'inactivebackground':
                    if kind in [WIDGET_NAMES.TabbedFrame, WIDGET_NAMES.Table]:
                        item.config(inactivebackground=value)
                    else:
                        self.warn("Error configuring %s: can't set inactivebackground", name)
                elif option == 'width':
                    item.config(width=value)
                elif option == 'height':
                    item.config(height=value)
                elif option == 'state':
                    # make entries readonly - can still copy/paste
                    but = None
                    if kind == WIDGET_NAMES.Entry:
                        if value == "disabled" and hasattr(item, 'but'):
                            but = item.but
                            item.unbind("<Button-1>")
                            value = "readonly"
                        elif value == 'normal' and hasattr(item, 'but') and item.cget('state') != 'normal':
                            but = item.but
                            item.bind("<Button-1>", item.click_command, "+")

                    if self.ttkFlag:
                        gui.trace("%s configured with ttk state %s", name, value)
                        item.state([value])
                        if but is not None: but.state([value])
                    else:
                        item.config(state=value)
                        if but is not None: but.config(state=value)

                elif option == 'relief':
                    item.config(relief=value)
                elif option == 'style':
                    if self.ttkFlag:
                        gui.trace("%s configured with ttk style %s", name, value)
                        item.config(style=value)
                    else:
                        self.warn("Error configuring %s: can't set ttk style, not in ttk mode.", name)
                elif option in ['align', 'anchor']:
                    if kind == WIDGET_NAMES.Entry or gui.GET_WIDGET_CLASS(item) == 'SelectableLabel':
                        if value == W: value = LEFT
                        elif value == E: value = RIGHT
                        item.config(justify=value)
                    elif kind == WIDGET_NAMES.LabelFrame:
                        item.config(labelanchor=value)
                    else:
                        if value == LEFT: value = "w"
                        elif value == RIGHT: value = "e"
                        item.config(anchor=value)
                elif option == 'cursor':
                    item.config(cursor=value)
                elif option == 'tooltip':
                    self._addTooltip(item, value)
                elif option == 'disableTooltip':
                    self._disableTooltip(item)
                elif option == 'enableTooltip':
                    self._enableTooltip(item)
                elif option == "focus":
                    item.focus_set()
                    if kind == WIDGET_NAMES.Entry:
                        if not self.ttkFlag:
                            item.icursor(END)
                            item.xview(END)
                        else:
                            item.icursor(END)
                            item.xview(len(item.get()))

                # event bindings
                elif option == 'over':
                    self._bindOverEvent(kind, name, item, value, option, key)
                elif option == 'drag':
                    self._bindDragEvent(kind, name, item, value, option, key)
                elif option in ['command', "change", "submit"]:
                    self._bindEvent(kind, name, item, value, option, key)

                elif option == 'sticky':
                    info = {}
                    # need to reposition the widget in its grid
                    if self._widgetHasContainer(kind, item):
                        # pack uses LEFT & RIGHT & BOTH
                        info["side"] = value
                        if value.lower() == "both":
                            info["expand"] = 1
                            info["side"] = "right"
                        else:
                            info["expand"] = 0
                    else:
                        # grid uses E+W
                        if value.lower() == "left":
                            side = W
                        elif value.lower() == "right":
                            side = E
                        elif value.lower() == "both":
                            side = W + E
                        else:
                            side = value.upper()
                        info["sticky"] = side
                    self._repackWidget(item, info)
                elif option == 'padding':
                    if value[1] is None:
                        item.config(padx=value[0][0], pady=value[0][1])
                    else:
                        item.config(padx=value[0], pady=value[1])
                elif option == 'ipadding':
                    if value[1] is None:
                        item.config(ipadx=value[0][0], ipady=value[0][1])
                    else:
                        item.config(ipadx=value[0], ipady=value[1])
                elif option == 'rightClick':
                    self._bindRightClick(item, value)

                elif option == 'internalDrop':
                    self._registerInternalDropTarget(item, value)

                elif option == 'internalDrag':
                    self._registerInternalDragSource(kind, name, item, value)

                elif option == 'externalDrop':
                    self._registerExternalDropTarget(name, item, value[0], value[1])

                elif option == 'externalDrag':
                    self._registerExternalDragSource(name, item, value)

            except TclError as e:
                self.warn("Error configuring %s: %s", name, str(e))

    # generic function for over events
    def _validateFunctionList(self, functions, mode):
        if type(functions) == tuple:
            functions = list(functions)
        elif type(functions) != list:
            functions = [functions]

        if len(functions) == 1:
            functions.append(None)
        if len(functions) != 2:
            raise Exception("Invalid arguments, set<widget> %s Function requires 1 or 2 functions to be passed in.", mode)

        return functions

    def _bindOverEvent(self, kind, name, widget, functions, eventType, key=None):
        functions = self._validateFunctionList(functions, "Over")

        if functions[0] is not None:
            widget.bind("<Enter>", self.MAKE_FUNC(functions[0], name), add="+")
        if functions[1] is not None:
            widget.bind("<Leave>", self.MAKE_FUNC(functions[1], name), add="+")

    # generic function for drag events
    def _bindDragEvent(self, kind, name, widget, functions, eventType, key=None):
        functions = self._validateFunctionList(functions, "Drag")

        if kind == WIDGET_NAMES.Label:
            widget.config(cursor="fleur")

            def getLabel(f):
                # loop through all labels
                items = self.widgetManager.group(kind)
                for key, value in items.items():
                    if self._isMouseInWidget(value):
                        self.MAKE_FUNC(f,key)()
                        return

            if functions[0] is not None:
                widget.bind("<ButtonPress-1>", self.MAKE_FUNC(functions[0], name), add="+")
            if functions[1] is not None:
                widget.bind("<ButtonRelease-1>", self.MAKE_FUNC(getLabel, functions[1]), add="+")
        else:
            self.error("Only able to bind drag events to labels")

    # generic function for change/submit/events
    def _bindEvent(self, kind, name, widget, function, eventType, key=None):
        # this will discard the scale value, as default function
        # can't handle it
        if kind == WIDGET_NAMES.Scale:
            cmd = self.MAKE_FUNC(function, name)
            widget.cmd_id = widget.var.trace('w', cmd)
            widget.cmd = cmd
        elif kind == WIDGET_NAMES.OptionBox:
            if widget.kind == "ticks":
                vals = self.widgetManager.get(WIDGET_NAMES.TickOptionBox, name, group=WidgetManager.VARS)
                for o in vals:
                    cmd = self.MAKE_FUNC(function, name)
                    vals[o].cmd_id = vals[o].trace('w', cmd)
                    vals[o].cmd = cmd
            else:
                cmd = self.MAKE_FUNC(function, name)
                # need to trace the variable??
                widget.cmd_id = widget.var.trace('w', cmd)
                widget.cmd = cmd
        elif kind in [WIDGET_NAMES.Entry, WIDGET_NAMES.FileEntry, WIDGET_NAMES.DirectoryEntry]:
            if eventType == "change":
                # not populated by change/submit
                if key is None:
                    key = name
                cmd = self.MAKE_FUNC(function, key)
                # get Entry variable
                var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
                var.cmd_id = var.trace('w', cmd)
                var.cmd = cmd
            else:
                # not populated by change/submit
                if key is None:
                    key = name
                sbm = self.MAKE_FUNC(function, key)
                widget.sbm_id = widget.bind('<Return>', sbm)
                widget.sbm = sbm
        elif kind == WIDGET_NAMES.TextArea:
            if eventType == "change":
                # get Entry variable
                cmd = self.MAKE_FUNC(function, name)
                widget.bindChangeEvent(cmd)
        elif kind == WIDGET_NAMES.Button:
            if eventType == "change":
                self.warn("Error configuring %s : can't set a change function", name)
            else:
                widget.config(command=self.MAKE_FUNC(function, name))
                widget.bind('<Return>', self.MAKE_FUNC(function, name))
        # make labels clickable, add a cursor, and change the look
        elif kind == WIDGET_NAMES.Label or kind == WIDGET_NAMES.Image:
            if eventType in ["command", "submit"]:
                if self.platform == self.MAC:
                    widget.config(cursor="pointinghand")
                elif self.platform in [self.WINDOWS, self.LINUX]:
                    widget.config(cursor="hand2")

                cmd = self.MAKE_FUNC(function, name)
                widget.bind("<Button-1>", cmd, add="+")
                widget.cmd = cmd
                # these look good, but break when dialogs take focus
                #up = widget.cget("relief").lower()
                # down="sunken"
                # make it look like it's pressed
                #widget.bind("<Button-1>",lambda e: widget.config(relief=down), add="+")
                #widget.bind("<ButtonRelease-1>",lambda e: widget.config(relief=up))
            elif eventType == "change":
                self.warn("Error configuring %s : can't set a change function", name)
        elif kind == WIDGET_NAMES.ListBox:
            cmd = self.MAKE_FUNC(function, name)
            widget.bind('<<ListboxSelect>>', cmd)
            widget.cmd = cmd
        elif kind in [WIDGET_NAMES.RadioButton]:
            cmd = self.MAKE_FUNC(function, name)
            # get rb variable
            var = self.widgetManager.get(WIDGET_NAMES.RadioButton, name, group=WidgetManager.VARS)

            # only allow one trace to be bound
            # users are more likely to call multiple binds on radios
            # because they all share one var
            if hasattr(var, "cmd_id"):
                var.trace_vdelete('w', var.cmd_id)

            var.cmd_id = var.trace('w', cmd)
            var.cmd = cmd
        elif kind in [WIDGET_NAMES.Properties, WIDGET_NAMES.FrameStack, WIDGET_NAMES.Table]:
            cmd = self.MAKE_FUNC(function, name)
            widget.setChangeFunction(cmd)
        elif kind == WIDGET_NAMES.SpinBox:
            widget.cmd = self.MAKE_FUNC(function, name)
            widget.cmd_id = widget.var.trace("w", widget.cmd)
        elif kind == WIDGET_NAMES.PanedFrame:
            widget.cmd = self.MAKE_FUNC(function, name)
            widget.bind("<Configure>", widget.cmd)
        else:
            if kind not in [WIDGET_NAMES.CheckBox]:
                self.warn("Unmanaged binding of %s to %s", eventType, name)
            cmd = self.MAKE_FUNC(function, name)
            widget.config(command=cmd)
            widget.cmd = cmd

    # dynamic way to create the configuration functions
    def _buildConfigFuncs(self):
        # loop through all the available widgets
        # and make all the below functons for each one
        for v in WIDGET_NAMES.funcs():
            k = WIDGET_NAMES.get(v)
            exec( "def set" + v +
                "Bg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'background', val)")
            exec("gui.set" + v + "Bg=set" + v + "Bg")
            exec( "def set" + v +
                "Fg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'foreground', val)")
            exec("gui.set" + v + "Fg=set" + v + "Fg")

            exec( "def set" + v +
                "DisabledFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'disabledforeground', val)")
            exec("gui.set" + v + "DisabledFg=set" + v + "DisabledFg")
            exec( "def set" + v +
                "DisabledBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'disabledbackground', val)")
            exec("gui.set" + v + "DisabledBg=set" + v + "DisabledBg")

            exec( "def set" + v +
                "ActiveFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'activeforeground', val)")
            exec("gui.set" + v + "ActiveFg=set" + v + "ActiveFg")
            exec( "def set" + v +
                "ActiveBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'activebackground', val)")
            exec("gui.set" + v + "ActiveBg=set" + v + "ActiveBg")

            exec( "def set" + v +
                "InactiveFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'inactiveforeground', val)")
            exec("gui.set" + v + "InactiveFg=set" + v + "InactiveFg")
            exec( "def set" + v +
                "InactiveBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'inactivebackground', val)")
            exec("gui.set" + v + "InactiveBg=set" + v + "InactiveBg")

            exec( "def set" + v +
                "Width(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'width', val)")
            exec("gui.set" + v + "Width=set" + v + "Width")
            exec( "def set" + v +
                "Height(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'height', val)")
            exec("gui.set" + v + "Height=set" + v + "Height")
            exec( "def set" + v +
                "State(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'state', val)")
            exec("gui.set" + v + "State=set" + v + "State")
            exec( "def set" + v +
                "Padding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'padding', [x, y])")
            exec("gui.set" + v + "Padding=set" + v + "Padding")

            exec( "def set" + v +
                "IPadding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'ipadding', [x, y])")
            exec("gui.set" + v + "IPadding=set" + v + "IPadding")

            exec( "def set" + v +
                "InPadding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'ipadding', [x, y])")
            exec("gui.set" + v + "InPadding=set" + v + "InPadding")

            # drag and drop stuff
            exec( "def set" + v +
                "DropTarget(self, name, function=None, replace=True): self.configureWidgets(" +
                str(k) + ", name, 'externalDrop', [function, replace])")
            exec("gui.set" + v + "DropTarget=set" + v + "DropTarget")

            exec( "def set" + v +
                "DragSource(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'externalDrag', function)")
            exec("gui.set" + v + "DragSource=set" + v + "DragSource")

            exec( "def register" + v +
                "Draggable(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'internalDrag', function)")
            exec("gui.register" + v + "Draggable=register" + v + "Draggable")

            exec( "def register" + v +
                "Droppable(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'internalDrop', function)")
            exec("gui.register" + v + "Droppable=register" + v + "Droppable")

            exec( "def set" + v +
                "Style(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'style', val)")
            exec("gui.set" + v + "Style=set" + v + "Style")

            # might not all be necessary, could make exclusion list
            exec( "def set" + v +
                "Relief(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'relief', val)")
            exec("gui.set" + v + "Relief=set" + v + "Relief")
            exec( "def set" + v +
                "Align(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'align', val)")
            exec("gui.set" + v + "Align=set" + v + "Align")
            exec( "def set" + v +
                "Anchor(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'anchor', val)")
            exec("gui.set" + v + "Anchor=set" + v + "Anchor")

            exec( "def set" + v +
                "Tooltip(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'tooltip', val)")
            exec("gui.set" + v + "Tooltip=set" + v + "Tooltip")

            exec( "def disable" + v +
                "Tooltip(self, name): self.configureWidget(" +
                str(k) + ", name, 'disableTooltip', None)")
            exec("gui.disable" + v + "Tooltip=disable" + v + "Tooltip")

            exec( "def enable" + v +
                "Tooltip(self, name): self.configureWidget(" +
                str(k) + ", name, 'enableTooltip', None)")
            exec("gui.enable" + v + "Tooltip=enable" + v + "Tooltip")

            # function setters
            exec( "def set" + v +
                "ChangeFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'change', val)")
            exec("gui.set" + v + "ChangeFunction=set" + v + "ChangeFunction")
            exec( "def set" + v +
                "SubmitFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'submit', val)")
            exec("gui.set" + v + "SubmitFunction=set" + v + "SubmitFunction")
            exec( "def set" + v +
                "DragFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'drag', val)")
            exec("gui.set" + v + "DragFunction=set" + v + "DragFunction")
            exec( "def set" + v +
                "OverFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'over', val)")
            exec("gui.set" + v + "OverFunction=set" + v + "OverFunction")

            # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/cursors.html
            exec( "def set" + v +
                "Cursor(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'cursor', val)")
            exec("gui.set" + v + "Cursor=set" + v + "Cursor")
            exec( "def set" + v +
                "Focus(self, name): self.configureWidget(" +
                str(k) + ", name, 'focus', None)")
            exec("gui.set" + v + "Focus=set" + v + "Focus")

            # change the stickyness
            exec( "def set" + v +
                "Sticky(self, name, pos): self.configureWidget(" +
                str(k) + ", name, 'sticky', pos)")
            exec("gui.set" + v + "Sticky=set" + v + "Sticky")

            # add right click
            exec( "def set" + v +
                "RightClick(self, name, menu): self.configureWidget(" +
                str(k) + ", name, 'rightClick', menu)")
            exec("gui.set" + v + "RightClick=set" + v + "RightClick")

            # functions to manage widgets
            exec( "def show" + v +
                "(self, name): self.showWidgetType(" +
                str(k) + ", name)")
            exec("gui.show" + v + "=show" + v)
            exec( "def hide" + v +
                "(self, name, collapse=False): self.hideWidgetType(" +
                str(k) + ", name, collapse)")
            exec("gui.hide" + v + "=hide" + v)
            exec( "def remove" + v +
                "(self, name, collapse=False): self.removeWidgetType(" +
                str(k) + ", name, collapse)")
            exec("gui.remove" + v + "=remove" + v)
            exec( "def move" + v +
                "(self, name, row=None, column=0, colspan=0, rowspan=0, sticky=W+E): self.moveWidgetType(" +
                str(k) + ", name, row, column, colspan, rowspan, sticky)")
            exec("gui.move" + v + "=move" + v)

            exec( "def empty" + v +
                "(self, name): self._emptyContainerType(" +
                str(k) + ", name)")
            exec("gui.empty" + v + "=empty" + v)

            # convenience functions for enable/disable
            # might not all be necessary, could make exclusion list
            exec( "def enable" + v +
                "(self, name): self.configureWidget(" +
                str(k) + ", name, 'state', 'normal')")
            exec("gui.enable" + v + "=enable" + v)
            exec( "def disable" + v +
                "(self, name): self.configureWidget(" +
                str(k) + ", name, 'state', 'disabled')")
            exec("gui.disable" + v + "=disable" + v)

            # group functions
            exec( "def set" + v +
                "Widths(self, names, val): self.configureWidgets(" +
                str(k) + ", names, 'width', val)")
            exec("gui.set" + v + "Widths=set" + v + "Widths")
            exec( "def setAll" + v +
                "Widths(self, val): self.configureAllWidgets(" +
                str(k) + ", 'width', val)")
            exec("gui.setAll" + v + "Widths=setAll" + v + "Widths")

            exec( "def set" + v +
                "Heights(self, names, val): self.configureWidgets(" +
                str(k) + ", names, 'height', val)")
            exec("gui.set" + v + "Heights=set" + v + "Heights")
            exec( "def setAll" + v +
                "Heights(self, val): self.configureAllWidgets(" +
                str(k) + ", 'height', val)")
            exec("gui.setAll" + v + "Heights=setAll" + v + "Heights")

            exec( "def get" + v +
                "Widget(self, name, val=None): return self.getWidget(" +
                str(k) + ", name, val)")
            exec("gui.get" + v + "Widget=get" + v + "Widget")

            exec( "def get" + v +
                "Bg(self, name, val=None): return self.getWidgetProperty(" +
                str(k) + ", name, val, 'bg')")
            exec("gui.get" + v + "Bg=get" + v + "Bg")

#####################################
#  FUNCTION to hide/show/remove widgets
#####################################
    def _widgetHasContainer(self, kind, item):
        if kind in (
            WIDGET_NAMES.Scale,
            WIDGET_NAMES.Entry,
            WIDGET_NAMES.SpinBox,
            WIDGET_NAMES.OptionBox,
            WIDGET_NAMES.Label) and item.inContainer:
            return True
        else:
            return False

    def _cloneWidget(self, widget, parent):
        clone = widget.__class__(parent)
        for key in widget.configure():
            clone.configure({key: widget.cget(key)})

        origProps = widget.__dict__
        for x in origProps:
            if x not in ['_w', '_tclCommands', '_name', 'master', 'tk']:
                setattr(clone, x, origProps[x])

        return clone

    def moveWidgetType(self, kind, name, row=None, column=0, colspan=0, rowspan=0, sticky=W+E):
        self.hideWidgetType(kind, name, collapse=True)
        widget = self.widgetManager.get(kind, name)

        container = self.getContainer()
        if container != widget.master:
            widget = self._cloneWidget(widget, container)
            self.widgetManager.update(kind, name, widget)

        self._positionWidget(widget, row, column, colspan, rowspan, sticky, updateBg=False)
        return widget


    def hideWidgetType(self, kind, name, collapse=False):
        items = self._getWidgetList(kind, name, limit=False)

        for item in items:
            if self._widgetHasContainer(kind, item):
                gui.trace("Hiding widget in container: %s", name)
                widget = item.master
                if hasattr(widget, "inContainer") and widget.inContainer:
                    gui.trace("Have container in container")
                    widget = widget.master
                try: self.widgetManager.get(WIDGET_NAMES.FrameLabel, name).hidden = True
                except: pass
            else:
                gui.trace("Hiding widget: %s", name)
#                if kind in [WIDGET_NAMES.RadioButton]:
#                    for rb in item:
#                        if rb.text == name:
#                            widget = rb
                widget = item

            if "in" in widget.grid_info():
                gui.trace("Widget hidden: %s", name)
                info = widget.grid_info()
                widget.grid_remove()

                if collapse:
                    widget.master.grid_rowconfigure(info["row"], minsize=0, weight=0)
            else:
                gui.trace("Hiding failed - %s not showing", name)

    def showWidgetType(self, kind, name):
        items = self._getWidgetList(kind, name, limit=False)

        for item in items:
            if self._widgetHasContainer(kind, item):
                gui.trace("Showing widget in container: %s", name)
                widget = item.master
                if hasattr(widget, "inContainer") and widget.inContainer:
                    gui.trace("Have container in container")
                    widget = widget.master
                try: self.widgetManager.get(WIDGET_NAMES.FrameLabel, name).hidden = False
                except: pass
            else:
                msg = "Showing widget"
                widget = item

            # only show the widget, if it's not already showing
            if "in" not in widget.grid_info():
                gui.trace("Widget shown: %s", name)
                widget.grid()
    #            self._updateLabelBoxes(name, widget.grid_info()['column'])
            else:
                gui.trace("Showing failed - %s already showing", name)

    def emptySubWindow(self, title):
        # not generated by function generator
        self._emptyContainerType(WIDGET_NAMES.SubWindow, title)

    def emptyCurrentContainer(self):
        cConf = self.containerStack[-1]
        kind = WIDGET_NAMES.name(cConf['type'])
        title = cConf['title']
        gui.trace('Emptying current container %s: %s', kind, title)

        if not self._emptyContainerObj(cConf['container']):
            gui.trace('No widgets found in current container %s: %s to empty', kind, title)

        cConf = self._prepContainer(cConf["title"], cConf["type"], cConf["container"], 0, 1)
        self.containerStack[-1] = cConf

    def _emptyContainerType(self, kind, title):
        kind = WIDGET_NAMES.name(kind)
        gui.trace('Emptying %s: %s', kind, title)
        cName = kind + "__" + title
        try:
            cConf = self.widgetManager.get(WIDGET_NAMES.ContainerLog, cName)
        except KeyError:
            raise Exception("Attempted to empty invalid " + kind + ": " + str(title))

        if not self._emptyContainerObj(cConf['container']):
            gui.trace('No widgets found in %s: %s to empty', kind, title)

    def removeAllWidgets(self, current=False, sub=False):
        if current:
            self.emptyCurrentContainer()
        else:
            gui.trace('Removing all widgets from appJar')

            if sub: self.destroyAllSubWindows()

            containerData = self.containerStack[0]
            container = containerData['container']
            self._emptyContainerObj(container)

            # reset container values
            containerData = self._prepContainer(containerData["title"], containerData["type"], containerData["container"], 0, 1)
            self.containerStack[0] = containerData

#            self.widgetManager.reset(WIDGET_NAMES.keepers)
#            self.setSize(None)

    def _emptyContainerObj(self, container):
        widgs = False
        for child in container.winfo_children():
            self.cleanseWidgets(child)
            widgs = True

        # reset the grid measurements
        for i in range(Grid.grid_size(container)[0]):
            container.columnconfigure(i, minsize=0, weight=0, pad=0)
        for i in range(Grid.grid_size(container)[1]):
            container.rowconfigure(i, minsize=0, weight=0, pad=0)

        return widgs

    def removeWidgetType(self, kind, name, collapse=False):
        if kind == WIDGET_NAMES.RadioButton:
            gui.error("Can't remove widget %s - %s", kind, name)
            return
            
        item = self.widgetManager.get(kind, name)

        # if it's a flasher, remove it
        if item in self.widgetManager.group(WIDGET_NAMES.FlashLabel):
            gui.trace("Remove flash label: %s", name)
            self.widgetManager.remove(WIDGET_NAMES.FlashLabel, item)
            if len(self.widgetManager.group(WIDGET_NAMES.FlashLabel)) == 0:
                self.doFlash = False

        # animated images...

        if self._widgetHasContainer(kind, item):
            gui.trace("Remove widget (%s) in container: %s", kind, name)
            parent = item.master

            # is it a container in a labelBox?
            # if so - remove & destroy the labelBox
            if hasattr(parent, "inContainer") and parent.inContainer:
                gui.trace("Container in container")
                labParent = parent.master

                self.widgetManager.remove(WIDGET_NAMES.FrameBox, labParent)
                self.widgetManager.remove(WIDGET_NAMES.Label, name)
                self.widgetManager.remove(WIDGET_NAMES.FrameLabel, name)
                labParent.grid_forget()
                labParent.destroy()
            # otherwise destroy this container & a label if we have one
            else:
                parent.grid_forget()
                parent.destroy()
                try:
                    self.widgetManager.remove(WIDGET_NAMES.Label, name)
                    self.widgetManager.remove(WIDGET_NAMES.FrameLabel, name)
                except: pass

            self.widgetManager.remove(WIDGET_NAMES.FrameBox, parent)
        else:
            gui.trace("Remove widget: %s", name)
            item.grid_forget()
            self.cleanseWidgets(item)

#####################################
# FUNCTION for managing commands
#####################################
    @staticmethod
    def MAKE_FUNC(funcName, param):
        ''' function to automate lambdas '''
        # make sure we get a function
        if not callable(funcName) and not hasattr(funcName, '__call__'):
            raise Exception("Invalid function: " + str(funcName))

        # check if the function requires arguments
        argsList = getArgs(funcName)
        # if no args, or 1 arg in a bound function
        noArgs = len(argsList[0])==0 or (len(argsList[0])==1 and inspect.ismethod(funcName))

        # if no args/varargs/kwargs then don't give the param
        if noArgs and argsList[1] is None and argsList[2] is None:
            return lambda *args: funcName()
        else:
            return lambda *args: funcName(param)

    def _checkFunc(self, names, funcs):
        singleFunc = None
        if funcs is None:
            return None
        elif callable(funcs):
            singleFunc = funcs
        elif len(names) != len(funcs):
            raise Exception("List sizes don't match")
        return singleFunc

#####################################
# FUNCTIONS to position a widget
#####################################

    # properties for setting container's default rowspan/colspan
    def setColspan(self, colspan):
        self.containerStack[-1]['colspan'] = colspan

    def getColspan(self):
        return self.containerStack[-1]['colspan']

    colspan = property(getColspan, setColspan)

    def setRowspan(self, rowspan):
        self.containerStack[-1]['rowspan'] = rowspan

    def getRowspan(self):
        return self.containerStack[-1]['rowspan']

    rowspan = property(getRowspan, setRowspan)

    def getRow(self):
        return self._getContainerProperty('emptyRow')

    def gr(self):
        return self.getRow()

    def setRow(self, row):
        self.containerStack[-1]['emptyRow'] = row

    row = property(getRow, setRow)

    def _repackWidget(self, widget, params):
        if widget.winfo_manager() == "grid":
            ginfo = widget.grid_info()
            ginfo.update(params)
            widget.grid(ginfo)
        elif widget.winfo_manager() == "pack":
            pinfo = widget.pack_info()
            pinfo.update(params)
            widget.pack(pinfo)
        else:
            raise Exception("Unknown geometry manager: " + widget.winfo_manager())

    # convenience function to set RCS, referencing the current container's
    # settings
    def _getRCS(self, row, column, colspan, rowspan):
        if row in[-1, 'previous', 'p', 'pr']:
            row = self._getContainerProperty('emptyRow') - 1
        else:
            # this is the default,
            if row is None or row in ['next', 'n']:
                row = self._getContainerProperty('emptyRow')
            self.containerStack[-1]['emptyRow'] = row + 1

        if column >= self._getContainerProperty('colCount'):
            self.containerStack[-1]['colCount'] = column + 1
        # if column == 0 and colspan == 0 and self._getContainerProperty('colCount') > 1:
        #      colspan = self._getContainerProperty('colCount')

        return row, column, colspan, rowspan

    @staticmethod
    def GET_WIDGET_CLASS(widget):
        return widget.__class__.__name__

    @staticmethod
    def SET_WIDGET_FG(widget, fg, external=False):
        widgType = gui.GET_WIDGET_CLASS(widget)
        gui.trace("SET_WIDGET_FG: %s - %s", widgType, fg)

        # only configure these widgets if external
        if widgType in ["Link", "Spinbox", "AjText", "AjScrolledText", "Button", "Entry", "AutoCompleteEntry"]:
            if external:
                try: # entry specific settings
                    if not widget.showingDefault:
                        widget.oldFg = fg
                        widget.config(fg=fg)
                    else:
                        widget.oldFg = fg
                except: # other widgets
                    widget.config(fg=fg)
        # handle flash labels
        elif widgType == "Label":
            widget.config(fg=fg)
            widget.origFg=fg
            try: widget.config(bg=widget.origBg)
            except: pass # not a flash label

        elif widgType == "OptionMenu":
            if external:
                widget.config(fg=fg)
                widget["menu"].config(fg=fg)

        # deal with generic groupers
        elif widgType in ["Frame", "LabelFrame", "PanedFrame", "Pane", "ajFrame"]:
            for child in widget.winfo_children():
                gui.SET_WIDGET_FG(child, fg, external)

        # deal with specific containers
        elif widgType == "LabelBox":
            try:
                if not widget.isValidation:
                    gui.SET_WIDGET_FG(widget.theLabel, fg, external)
            except Exception as e:
                gui.SET_WIDGET_FG(widget.theLabel, fg, external)
            gui.SET_WIDGET_FG(widget.theWidget, fg, external)
        elif widgType == "ButtonBox":
            gui.SET_WIDGET_FG(widget.theWidget, fg, external)
            gui.SET_WIDGET_FG(widget.theButton, fg, external)
        elif widgType == "WidgetBox":
            for child in widget.theWidgets:
                gui.SET_WIDGET_FG(child, fg, external)
        elif widgType == "ListBoxContainer":
            if external:
                gui.SET_WIDGET_FG(widget.lb, fg, external)

        # skip these widgets
        elif widgType in ["PieChart", "MicroBitSimulator", "Scrollbar"]:
            pass

        # always try these widgets
        else:
            try:
                widget.config(fg=fg)
            except Exception as e:
                pass

    @staticmethod
    def TINT(widget, colour):
        col = []
        for a, b in enumerate(widget.winfo_rgb(colour)):
            t = int(min(max(0, b / 256 + (255 - b / 256) * .3), 255))
            t = str(hex(t))[2:]
            if len(t) == 1:
                t = '0' + t
            elif len(t) == 0:
                t = '00'
            col.append(t)

        if int(col[0], 16) > 210 and int(col[1], 16) > 210 and int(col[2], 16) > 210:
            if gui.GET_PLATFORM() == gui.LINUX:
                return "#c3c3c3"
            else:
                return "systemHighlight"
        else:
            return "#" + "".join(col)

    # convenience method to set a widget's bg
    @staticmethod
    def SET_WIDGET_BG(widget, bg, external=False, tint=False):

        if bg is None: # ignore empty colours
            return

        widgType = gui.GET_WIDGET_CLASS(widget)
        isDarwin = gui.GET_PLATFORM() == gui.MAC
        isLinux = gui.GET_PLATFORM() == gui.LINUX

        gui.trace("Config %s BG to %s", widgType, bg)

        # these have a highlight border to remove
        hideBorders = [ "Text", "AjText",
            "ScrolledText", "AjScrolledText",
            "Scale", "AjScale",
            "OptionMenu",
            "Entry", "AutoCompleteEntry",
            "Radiobutton", "Checkbutton",
            "Button"]

        # these shouldn't have their BG coloured by default
        noBg = [ "Button",
            "Scale", "AjScale",
            "Spinbox", "Listbox", "OptionMenu",
            "SplitMeter", "DualMeter", "Meter",
            "Entry", "AutoCompleteEntry",
            "Text", "AjText",
            "ScrolledText", "AjScrolledText",
            "ToggleFrame"]

        # remove the highlight borders
        if widgType in hideBorders:
            if widgType == "Entry" and widget.isValidation:
                pass
            elif widgType == "OptionMenu":
                widget["menu"].config(borderwidth=0)
                widget.config(highlightbackground=bg)
                if isDarwin:
                    widget.config(background=bg)
            elif widgType in ["Radiobutton", "Checkbutton"]:
                widget.config(activebackground=bg, highlightbackground=bg)
            else:
                widget.config(highlightbackground=bg)

        # do some fancy tinting
        if external or tint:
            if widgType in ["Button", "Scale", "AjScale"]:
                widget.config(activebackground=gui.TINT(widget, bg))
            elif widgType in ["Entry", "Text", "AjText", "ScrolledText", "AjScrolledText", "AutoCompleteEntry", "Spinbox"]:
                widget.config(selectbackground=gui.TINT(widget, bg))
                widget.config(highlightcolor=gui.TINT(widget, bg))
                if widgType in ["Text", "AjText", "ScrolledText", "AjScrolledText"]:
                    widget.config(inactiveselectbackground=gui.TINT(widget, bg))
                elif widgType == "Spinbox":
                    widget.config(buttonbackground=bg)
            elif widgType == "Listbox":
                widget.config(selectbackground=gui.TINT(widget, bg))
            elif widgType == "OptionMenu":
                widget.config(activebackground=gui.TINT(widget, bg))
                widget["menu"].config(activebackground=gui.TINT(widget, bg))
            elif widgType in ["Radiobutton", "Checkbutton"]:
                widget.config(activebackground=gui.TINT(widget, bg))

        # if this is forced - change everything
        if external:
            widget.config(bg=bg)
            if widgType == "OptionMenu":
                widget["menu"].config(bg=bg)
        # otherwise only colour un-excluded widgets
        elif widgType not in noBg:
            widget.config(bg=bg)

        # deal with flash labels
        if widgType == "Label":
            widget.origBg=bg
            try: widget.config(fg=widget.origFg)
            except: pass # not a flash label

        # now do any of the below containers
        if widgType in ["LabelFrame", "PanedFrame", "Pane", "ajFrame"]:
            for child in widget.winfo_children():
                gui.SET_WIDGET_BG(child, bg, external, tint)
        elif widgType == "LabelBox": # widget with label, in frame
            if widget.theLabel is not None:
                gui.SET_WIDGET_BG(widget.theLabel, bg, external, tint)
            gui.SET_WIDGET_BG(widget.theWidget, bg, external, tint)
        elif widgType == "ButtonBox": # widget with button, in frame
            gui.SET_WIDGET_BG(widget.theWidget, bg, external, tint)
            gui.SET_WIDGET_BG(widget.theButton, bg, external, tint)
        elif widgType == "ListBoxContainer": # list box container
            gui.SET_WIDGET_BG(widget.lb, bg, external, tint)
        elif widgType == "WidgetBox": # group of buttons or labels
            for widg in widget.theWidgets:
                gui.SET_WIDGET_BG(widg, bg, external, tint)

    def _getContainerProperty(self, prop=None):
        if prop is not None:
            return self.containerStack[-1][prop]
        else:
            return self.containerStack[-1]

    def _getContainerBg(self):
        if not self.ttkFlag:
            return self.getContainer()["bg"]
        else:
            return None

    def _getContainerFg(self):
        try:
            return self._getContainerProperty('fg')
        except:
            return "#000000"

    # two important things here:
    # grid - sticky: position of widget in its space (side or fill)
    # row/columns configure - weight: how to grow with GUI
    def _positionWidget( self, widget, row, column=0, colspan=0, rowspan=0, sticky=W+E, updateBg=True):
        # allow item to be added to container
        container = self.getContainer()
        if updateBg and not self.ttkFlag:
            gui.SET_WIDGET_FG(widget, self._getContainerFg())
            gui.SET_WIDGET_BG(widget, self._getContainerBg())

        # alpha paned window placement
        if self._getContainerProperty('type') == WIDGET_NAMES.PanedFrame:
            container.add(widget)
            self.containerStack[-1]['widgets'] = True
            return

        # else, add to grid
        row, column, colspan, rowspan = self._getRCS(row, column, colspan, rowspan)

        # build a dictionary for the named params
        iX = self._getContainerProperty('ipadx')
        iY = self._getContainerProperty('ipady')
        cX = self._getContainerProperty('padx')
        cY = self._getContainerProperty('pady')
        params = {
            "row": row,
            "column": column,
            "ipadx": iX,
            "ipady": iY,
            "padx": cX,
            "pady": cY}

        # sort out rowspan & colspan
        cColspan = self._getContainerProperty("colspan")
        cRowspan = self._getContainerProperty("rowspan")

        if colspan != 0: params["columnspan"] = colspan
        elif cColspan != 0: params["columnspan"] = cColspan

        if rowspan != 0: params["rowspan"] = rowspan
        elif cRowspan != 0: params["rowspan"] = cRowspan

        # 1) if param has sticky, use that
        # 2) if container has sticky - override
        # 3) else, none
        if self._getContainerProperty("sticky") is not None:
            params["sticky"] = self._getContainerProperty("sticky")
        elif sticky is not None:
            params["sticky"] = sticky
        else:
            pass

        # make colspanned widgets expand to fill height of cell
        if rowspan != 0:
            if "sticky" in params:
                if "n" not in params["sticky"]:
                    params["sticky"] += "n"
                if "s" not in params["sticky"]:
                    params["sticky"] += "s"
            else:
                params["sticky"] = "ns"

        # expand that dictionary out as we pass it as a value
        widget.grid(**params)
        self.containerStack[-1]['widgets'] = True
        # if we're in a PANEDFRAME - we need to set parent...
        if self._getContainerProperty('type') == WIDGET_NAMES.Pane:
            self.containerStack[-2]['widgets'] = True

        # configure the row/column to expand equally
        if self._getContainerProperty('expand') in ["ALL", "COLUMN"]:
            Grid.columnconfigure(container, column, weight=1)
        else:
            Grid.columnconfigure(container, column, weight=0)
        if self._getContainerProperty('expand') in ["ALL", "ROW"]:
            Grid.rowconfigure(container, row, weight=1)
        else:
            Grid.rowconfigure(container, row, weight=0)

#        self._getContainerProperty('container').columnconfigure(0, weight=1)
#        self._getContainerProperty('container').rowconfigure(0, weight=1)

#####################################
# FUNCTION to manage containers
#####################################
    # prepares a new empty container dict
    def _prepContainer(self, cTitle, cType, container, row, col, sticky=None):
        containerData = {'type': cType,
                    'title': cTitle,
                    'container': container,
                    'emptyRow': row,
                    'colCount': col,
                    'sticky': sticky,
                    'padx': 0,
                    'pady': 0,
                    'ipadx': 0,
                    'ipady': 0,
                    'expand': "ALL",
                    'widgets': False,
                    'inputFont': self._inputFont,
                    'labelFont': self._labelFont,
                    'buttonFont': self._buttonFont,
                    "fg": self._getContainerFg(),
                    "colspan":0,
                    "rowspan":0,
                    }
        return containerData

    # adds the container to the container stack - makes this the current working container
    def _addContainer(self, cTitle, cType, container, row, col, sticky=None):
        containerData = self._prepContainer(cTitle, cType, container, row, col, sticky)
        self.containerStack.append(containerData)

    def openFrameStack(self, title):
        return self._openContainer(WIDGET_NAMES.FrameStack, title)

    def openSubFrame(self, frameTitle, frameNumber):
        return self._openContainer(WIDGET_NAMES.SubFrame, frameTitle+"__"+str(frameNumber))

    def openRootPage(self, title):
        return self._openContainer(WIDGET_NAMES.RootPage, title)

    def openLabelFrame(self, title):
        return self._openContainer(WIDGET_NAMES.LabelFrame, title)

    def openFrame(self, title):
        try: return self._openContainer(WIDGET_NAMES.Frame, title)
        except: return self._openContainer(WIDGET_NAMES.SubFrame, title)

    def openToggleFrame(self, title):
        return self._openContainer(WIDGET_NAMES.ToggleFrame, title)

    def openPagedWindow(self, title):
        return self._openContainer(WIDGET_NAMES.PagedWindow, title)

    def openPage(self, windowTitle, pageNumber):
        return self._openContainer(WIDGET_NAMES.Page, windowTitle+"__"+str(pageNumber))

    def openTabbedFrame(self, title):
        return self._openContainer(WIDGET_NAMES.TabbedFrame, title)

    def openTab(self, frameTitle, tabTitle):
        return self._openContainer(WIDGET_NAMES.Tab, frameTitle+"__"+tabTitle)

    def openNotebook(self, title):
        return self._openContainer(WIDGET_NAMES.Notebook, title)

    def openNote(self, frameTitle, tabTitle):
        return self._openContainer(WIDGET_NAMES.Notebook, frameTitle+"__"+tabTitle)

    def openPanedFrame(self, title):
        return self._openContainer(WIDGET_NAMES.PanedFrame, title)

    def openPane(self, title):
        return self._openContainer(WIDGET_NAMES.Pane, title)

    def openSubWindow(self, title):
        return self._openContainer(WIDGET_NAMES.SubWindow, title)

    def openScrollPane(self, title):
        return self._openContainer(WIDGET_NAMES.ScrollPane, title)

    # function to reload the specified container
    def _openContainer(self, kind, title):
        # get the cached container config for this container
        kind = WIDGET_NAMES.name(kind)
        cName = kind + "__" + title
        try:
            cConf = self.widgetManager.get(WIDGET_NAMES.ContainerLog, cName)
        except KeyError:
            raise Exception("Attempted to open invalid " + kind + ": " + str(title))

        self.containerStack.append(cConf)
        return cConf['container']

    # returns the current working container
    def getContainer(self):
        container = self._getContainerProperty('container')
        if self._getContainerProperty('type') == WIDGET_NAMES.ScrollPane:
            return container.interior
        elif self._getContainerProperty('type') == WIDGET_NAMES.PagedWindow:
            return container.getPage()
        elif self._getContainerProperty('type') == WIDGET_NAMES.ToggleFrame:
            return container.getContainer()
        elif self._getContainerProperty('type') == WIDGET_NAMES.SubWindow:
            return container.canvasPane
        else:
            return container

    # if possible, removes the current container
    def _removeContainer(self):
        if len(self.containerStack) == 1:
            raise Exception("Can't remove container, already in root window.")
        else:
            container = self.containerStack.pop()
            if not container['widgets']:
                self.warn("Closing empty container: %s", container['title'])

            # store the container so that it can be re-opened later
            name = WIDGET_NAMES.name(container["type"]) + "__" + container["title"]
            try:
                self.widgetManager.add(WIDGET_NAMES.ContainerLog, name, container)
            except:
                pass # we'll ignore, as that means we already added it...
            return container

    # functions to start the various containers
    def startContainer(self, fType, title, row=None, column=0, colspan=0, rowspan=0, sticky=None, name=None):
        if name is None: name = title
        if fType == WIDGET_NAMES.LabelFrame:
            # first, make a LabelFrame, and position it correctly
            self.widgetManager.verify(WIDGET_NAMES.LabelFrame, title)
            if not self.ttkFlag:
                container = LabelFrame(self.getContainer(), text=name, relief="groove")
                container.config(background=self._getContainerBg(), font=self._getContainerProperty('labelFont'))
            else:
                container = ttk.LabelFrame(self.getContainer(), text=name, relief="groove")

            container.DEFAULT_TEXT = name
            container.isContainer = True
            self.setPadX(5)
            self.setPadY(5)
            self._positionWidget(container, row, column, colspan, rowspan, "nsew")
            self.widgetManager.add(WIDGET_NAMES.LabelFrame, title, container)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.LabelFrame, container, 0, 1, sticky)
            return container
        elif fType == WIDGET_NAMES.Canvas:
            # first, make a canvas, and position it correctly
            self.widgetManager.verify(WIDGET_NAMES.Canvas, title)
            container = Canvas(self.getContainer())
            container.isContainer = True
            self._positionWidget(container, row, column, colspan, rowspan, "nsew")
            self.widgetManager.add(WIDGET_NAMES.Canvas, title, container)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.Canvas, container, 0, 1, "")
            return container
        elif fType == WIDGET_NAMES.TabbedFrame:
            self.widgetManager.verify(WIDGET_NAMES.TabbedFrame, title)
            tabbedFrame = self._tabbedFrameMaker(self.getContainer(), self.ttkFlag, font=self._getContainerProperty('labelFont'))
            if not self.ttkFlag:
                tabbedFrame.config(bg=self._getContainerBg())
#            tabbedFrame.isContainer = True
            self._positionWidget(
                tabbedFrame,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.widgetManager.add(WIDGET_NAMES.TabbedFrame, title, tabbedFrame)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.TabbedFrame, tabbedFrame, 0, 1, sticky)
            return tabbedFrame
        elif fType == WIDGET_NAMES.Tab:
            # add to top of stack
            self.containerStack[-1]['widgets'] = True
            tabTitle = self._getContainerProperty('title') + "__" + title
            tab = self._getContainerProperty('container').addTab(title)
            self._addContainer(tabTitle, WIDGET_NAMES.Tab, tab, 0, 1, sticky)
            return tab
        elif fType == WIDGET_NAMES.Notebook:
            if not self.ttkFlag:
                raise Exception("Cannot create a ttk Notebook, unless ttk is enabled.")
            self.widgetManager.verify(WIDGET_NAMES.Notebook, title)
            notebook = ttk.Notebook(self.getContainer())
#            tabbedFrame.isContainer = True
            self._positionWidget(
                notebook,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.widgetManager.add(WIDGET_NAMES.Notebook, title, notebook)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.Notebook, notebook, 0, 1, sticky)
            return notebook
        elif fType == WIDGET_NAMES.Note:
            # add to top of stack
            self.containerStack[-1]['widgets'] = True
            noteTitle = self._getContainerProperty('title') + "__" + title
            frame = ttk.Frame(self._getContainerProperty('container'))
            self._getContainerProperty('container').add(frame, text=title)
            self._addContainer(noteTitle, WIDGET_NAMES.Note, frame, 0, 1, sticky)
            return frame
        elif fType == WIDGET_NAMES.PanedFrame:
            # if we previously put a frame for widgets
            # remove it
            if self._getContainerProperty('type') == WIDGET_NAMES.Pane:
                self.stopContainer()

            # now, add the new pane
            self.widgetManager.verify(WIDGET_NAMES.PanedFrame, title)
            pane = PanedWindow(
                self.getContainer(),
                showhandle=True,
                sashrelief="groove",
                bg=self._getContainerBg())

            pane.isContainer = True
            self._positionWidget(
                pane, row, column, colspan, rowspan, sticky=sticky)
            self.widgetManager.add(WIDGET_NAMES.PanedFrame, title, pane)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.PanedFrame, pane, 0, 1, sticky)

            # now, add a frame to the pane
            self.startContainer(WIDGET_NAMES.Pane, title)
            return pane
        elif fType == WIDGET_NAMES.Pane:
            # create a frame, and add it to the pane
            pane = Pane(self.getContainer(), bg=self._getContainerBg())
            pane.isContainer = True
            self._getContainerProperty('container').add(pane)
            self.widgetManager.add(WIDGET_NAMES.Pane, title, pane)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.Pane, pane, 0, 1, sticky)
            return pane
        elif fType == WIDGET_NAMES.ScrollPane:
            self.widgetManager.verify(WIDGET_NAMES.ScrollPane, title)
            # naned used to diabled sctollbars
            if name not in ["horizontal", "vertical", ""]:
                gui.warn("ScrollPane %s: Invalid value for disabled, must be one of 'horizontal' or 'vertical'", title)
            scrollPane = ScrollPane(self.getContainer(), disabled=name)
            if not self.ttkFlag:
                scrollPane.config(bg=self._getContainerBg())
            scrollPane.isContainer = True
            self._positionWidget(
                scrollPane,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.widgetManager.add(WIDGET_NAMES.ScrollPane, title, scrollPane)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.ScrollPane, scrollPane, 0, 1, sticky)
            return scrollPane
        elif fType == WIDGET_NAMES.ToggleFrame:
            self.widgetManager.verify(WIDGET_NAMES.ToggleFrame, title)
            toggleFrame = ToggleFrame(self.getContainer(), title=title, bg=self._getContainerBg())
            toggleFrame.configure(font=self._getContainerProperty('labelFont'))
            toggleFrame.isContainer = True
            self._positionWidget(
                toggleFrame,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self._addContainer(title, WIDGET_NAMES.ToggleFrame, toggleFrame, 0, 1, "nw")
            self.widgetManager.add(WIDGET_NAMES.ToggleFrame, title, toggleFrame)
            return toggleFrame
        elif fType == WIDGET_NAMES.PagedWindow:
            # create the paged window
            pagedWindow = PagedWindow(self.getContainer(), title=title, bg=self._getContainerBg(), width=200, height=400, buttonFont=self._getContainerProperty('buttonFont'), titleFont=self._getContainerProperty('labelFont'))
            # bind events
            self.topLevel.bind("<Left>", pagedWindow.showPrev)
            self.topLevel.bind("<Control-Left>", pagedWindow.showFirst)
            self.topLevel.bind("<Right>", pagedWindow.showNext)
            self.topLevel.bind("<Control-Right>", pagedWindow.showLast)
            # register it as a container
            pagedWindow.isContainer = True
            self._positionWidget(pagedWindow, row, column, colspan, rowspan, sticky=sticky)
            self._addContainer(title, WIDGET_NAMES.PagedWindow, pagedWindow, 0, 1, "nw")
            self.widgetManager.add(WIDGET_NAMES.PagedWindow, title, pagedWindow)
            return pagedWindow
        elif fType == WIDGET_NAMES.Page:
            page = self._getContainerProperty('container').addPage()
            page.isContainer = True
            self._addContainer(title, WIDGET_NAMES.Page, page, 0, 1, sticky)
            self.containerStack[-1]['expand'] = "None"
            return page
        elif fType == WIDGET_NAMES.FrameStack:
            # create the paged window
            frameStack = FrameStack(self.getContainer(), bg=self._getContainerBg())
            self.widgetManager.add(WIDGET_NAMES.FrameStack, title, frameStack)
            # register it as a container
            frameStack.isContainer = True
            self._positionWidget(frameStack, row, column, colspan, rowspan, sticky=sticky)
            self._addContainer(title, WIDGET_NAMES.FrameStack, frameStack, 0, 1, "news")
            return frameStack
        elif fType == WIDGET_NAMES.Frame:
            # first, make a Frame, and position it correctly
            self.widgetManager.verify(WIDGET_NAMES.Frame, title)
            container = self._makeAjFrame()(self.getContainer())
            container.isContainer = True
            container.config(background=self._getContainerBg())
            self._positionWidget( container, row, column, colspan, rowspan, "nsew")
            self.widgetManager.add(WIDGET_NAMES.Frame, title, container)

            # now, add to top of stack
            self._addContainer(title, WIDGET_NAMES.Frame, container, 0, 1, sticky)
            return container
        elif fType == WIDGET_NAMES.SubFrame:
            subFrame = self._getContainerProperty('container').addFrame()
            subFrame.isContainer = True
            self._addContainer(title, WIDGET_NAMES.SubFrame, subFrame, 0, 1, "news")
            self.widgetManager.add(WIDGET_NAMES.Frame, title, subFrame)
            return subFrame
        else:
            raise Exception("Unknown container: " + fType)

#####################################
# Notebooks
#####################################

    @contextmanager
    def notebook(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        try:
            note = self.startNotebook(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            note = self.openNotebook(title)
        self.configure(**kwargs)
        try: yield note
        finally: self.stopNotebook()

    def startNotebook(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        return self.startContainer(WIDGET_NAMES.Notebook, title, row, column, colspan, rowspan, sticky)

    def stopNotebook(self):
        # auto close the existing TAB - keep it?
        if self._getContainerProperty('type') == WIDGET_NAMES.Note:
            self.warn("You didn't STOP the previous NOTE")
            self.stopContainer()
        self.stopContainer()

    @contextmanager
    def note(self, title, tabTitle=None, **kwargs):
        if tabTitle is None:
            note = self.startNote(title)
        else:
            note = self.openNote(title, tabTitle)
        self.configure(**kwargs)
        try: yield note
        finally: self.stopNote()

    def startNote(self, title):
        # auto close the previous TAB - keep it?
        if self._getContainerProperty('type') == WIDGET_NAMES.Note:
            self.warn("You didn't STOP the previous NOTE")
            self.stopContainer()
        elif self._getContainerProperty('type') != WIDGET_NAMES.Notebook:
            raise Exception(
                "Can't add a Note to the current container: ", self._getContainerProperty('type'))
        return self.startContainer(WIDGET_NAMES.Note, title)

    def stopNote(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.Note:
            raise Exception("Can't stop a NOTE, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()
    """
    def startCanvas(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="news"):
        return self.startContainer(WIDGET_NAMES.Canvas, title)

    def stopCanvas(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.Canvas:
            raise Exception("Can't stop a CANVAS, currently in:", self._getContainerProperty('type'))
        self.stopContainer()

    @contextmanager
    def canvas(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        try:
            canvas = self.startCanvas(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            canvas = self.openCanvas(title)
        try: yield canvas
        finally: self.stopCanvas()
    """

#####################################
# Tabbed Frames
#####################################

    #################################
    # TabbedFrame Class
    #################################
    def _tabbedFrameMaker(self, master, useTtk=False, **kwargs):
        global OrderedDict
        if OrderedDict is None:
            from collections import OrderedDict

        class TabBorder(Frame, object):
            def __init__(self, master, **kwargs):
                super(TabBorder, self).__init__(master, **kwargs)
                self.config(borderwidth=0, highlightthickness=0, bg='darkGray')

        class TabContainer(frameBase, object):
            def __init__(self, master, **kwargs):
                super(TabContainer, self).__init__(master, **kwargs)
                TabBorder(self, height=2).pack(side=TOP, expand=True, fill=X)
                TabBorder(self, width=2).pack(side=LEFT, fill=Y, expand=0)

        class TabText(labelBase, object):
            def __init__(self, master, func, text, **kwargs):
                super(TabText, self).__init__(master, text=text, **kwargs)
                self.disabled = False
                self.DEFAULT_TEXT = text
                self.hidden = False
                self.bind("<Button-1>", lambda *args: func(text))
                self.border = TabBorder(master, width=2)

            def rename(self, newName):
                # use the DEFAULT_TEXT if necessary
                if newName is None: newName = self.DEFAULT_TEXT
                self.config(text=newName)

            def hide(self):
                self.hidden = True
                self.border.pack_forget()
                self.pack_forget()

            def display(self, fill=False, beforeTab=None, afterTab=None):
                self.border.pack_forget()
                self.pack_forget()
                if not self.hidden:
                    if fill: self.pack(side=LEFT, ipady=4, ipadx=4, expand=True, fill=BOTH, before=beforeTab, after=afterTab)
                    else: self.pack(side=LEFT, ipady=4, ipadx=4, before=beforeTab, after=afterTab)
                    self.border.pack(side=LEFT, fill=Y, expand=0, before=beforeTab, after=afterTab)

        class TabbedFrame(frameBase, object):
            def __init__(self, master, fill=False, changeOnFocus=True, font=None, **kwargs):
                # main frame & tabContainer inherit BG colour
                super(TabbedFrame, self).__init__(master, **kwargs)
                self.fill = fill
                self.selectedTab = None
                self.changeOnFocus = changeOnFocus
                self.changeEvent = None
                self.beforeTab = None
                self.afterTab = None

                # layout the grid
                Grid.columnconfigure(self, 0, weight=1)
                Grid.rowconfigure(self, 1, weight=1)

                # create two containers
                self.tabContainer = TabContainer(self, **kwargs)
                self.panes = FrameStack(self)
                self.panes.SKIP_CLEANSE = True

                # now grid minimised or stretched
                if self.fill: self.tabContainer.grid(row=0, sticky=W + E)
                else: self.tabContainer.grid(row=0, sticky=W)
                self.panes.grid(row=1, sticky="NESW")
                self.EMPTY_PANE = self.panes.addFrame()

                # nain store dictionary: name = [tab, pane]
                self.widgetStore = OrderedDict()

                # looks
                self.tabFont = font
                if gui.GET_PLATFORM() == gui.MAC: self.inactiveCursor="pointinghand"
                elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]: self.inactiveCursor="hand2"
                # selected tab & all panes
                self.activeFg = "#000000"
                self.activeBg = "#F6F6F6"
                # other tabs
                self.inactiveFg = "#000000"
                self.inactiveBg = "#DADADA"
                # disabled tabs
                self.disabledFg = "gray"
                self.disabledBg = "darkGray"

                if useTtk:
                    self.ttkStyle = ttk.Style()
                    self.ttkStyle.configure("ActiveTab.TLabel", foreground=self.activeFg, background=self.activeBg)
                    self.ttkStyle.configure("InactiveTab.TLabel", foreground=self.inactiveFg, background=self.inactiveBg)
                    self.ttkStyle.configure("DisabledTab.TLabel", foreground=self.disabledFg, background=self.disabledBg)
                    self.ttkStyle.configure("DisabledTab.TFrame", background=self.disabledBg)
                    self.EMPTY_PANE.config(style="DisabledTab.TFrame")
                else:
                    self.EMPTY_PANE.config(bg=self.disabledBg)

            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def setBeforeTab(self, tab=None):
                if tab is not None:
                    self.beforeTab = self.widgetStore[tab][0]
                else:
                    self.beforeTab = None

            def setAfterTab(self, tab=None):
                if tab is not None:
                    self.afterTab = self.widgetStore[tab][0]
                else:
                    self.afterTab = None

            def configure(self, cnf=None, **kw):
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
                if "activeforeground" in kw: self.activeFg = kw.pop("activeforeground")
                if "activebackground" in kw: self.activeBg = kw.pop("activebackground")
                if "fg" in kw: self.inactiveFg = kw.pop("fg")
                if "inactivebackground" in kw: self.inactiveBg = kw.pop("inactivebackground")
                if "inactiveforeground" in kw: self.inactiveFg = kw.pop("inactiveforeground")
                if "disabledforeground" in kw: self.disabledFg = kw.pop("disabledforeground")
                if "disabledbackground" in kw: self.disabledBg = kw.pop("disabledbackground")
                if "bg" in kw: self.tabContainer.configure(bg=kw["bg"])
                if "font" in kw: self.tabFont.config(kw.pop("font"))
                if "command" in kw: self.changeEvent = kw.pop("command")

                # just in case
                if not useTtk:
                    self.EMPTY_PANE.config(bg=self.disabledBg)
                else:
                    self.ttkStyle.configure("ActiveTab.TLabel", foreground=self.activeFg, background=self.activeBg)
                    self.ttkStyle.configure("InactiveTab.TLabel", foreground=self.inactiveFg, background=self.inactiveBg)
                    self.ttkStyle.configure("DisabledTab.TLabel", foreground=self.disabledFg, background=self.disabledBg)
                    self.ttkStyle.configure("DisabledTab.TFrame", background=self.disabledBg)

                # update tabs if we have any
                self._configTabs()

                # propagate any left over confs
                super(TabbedFrame, self).config(cnf, **kw)

            def hideTab(self, title):
                if title not in self.widgetStore.keys(): raise ItemLookupError("Invalid tab name: " + title)
                self.widgetStore[title][0].hide()
                if self.selectedTab == title:
                    self.selectedTab = None
                    self._findNewTab()
                self._configTabs()

            def deleteTab(self, title):
                self.hideTab(title)

                tab = self.widgetStore[title][0]
                tab.border.destroy()
                tab.destroy()

                pane = self.widgetStore[title][1]
                pane.grid_forget()
                pane.destroy()

                del self.widgetStore[title]

            def showTab(self, title):
                if title not in self.widgetStore.keys(): raise ItemLookupError("Invalid tab name: " + title)
                self.widgetStore[title][0].hidden = False
                self.expandTabs(self.fill)
                if self.selectedTab == None:
                    self.changeTab(title)

            def disableAllTabs(self, disabled=True):
                for tab in self.widgetStore.keys():
                    self.disableTab(tab, disabled, refresh=False)
                self._configTabs()
                if disabled:
                    self.selectedTab = None
                    self.EMPTY_PANE.lift()

            def disableTab(self, tabName, disabled=True, refresh=True):
                if tabName not in self.widgetStore.keys(): raise ItemLookupError("Invalid tab name: " + tabName)

                tab = self.widgetStore[tabName][0]
                tab.disabled = disabled

                if not disabled and not tab.hidden and self.selectedTab is None:
                    self.selectedTab = tabName
                elif disabled and self.selectedTab == tabName:
                    self.selectedTab = None
                    if refresh: self._findNewTab()

                if refresh:
                    self._configTabs()

            def addTab(self, text, **kwargs):
                # check for duplicates
                if text in self.widgetStore: raise ItemLookupError("Duplicate tabName: " + text)

                tab = TabText(self.tabContainer, text=text, func=self.changeTab, font=self.tabFont, **kwargs)
                tab.display(self.fill, beforeTab=self.beforeTab, afterTab=self.afterTab)

                # create the pane
                pane = self.panes.addFrame()
                if not useTtk:
                    pane.config(bg=self.activeBg)

                # log the first tab as the selected tab
                if self.selectedTab is None:
                    self.selectedTab = text

                # log the widgets
                self.widgetStore[text] = [tab, pane]
                self._configTabs()

                return pane

            def getTab(self, title):
                if title not in self.widgetStore.keys(): raise ItemLookupError("Invalid tab name: " + title)
                else: return self.widgetStore[title][1]

            def expandTabs(self, fill=True):
                self.fill = fill

                # update the tabConatiner
                self.tabContainer.grid_forget()
                if self.fill: self.tabContainer.grid(row=0, sticky=W + E)
                else: self.tabContainer.grid(row=0, sticky=W)

                for key in list(self.widgetStore.keys()):
                    tab = self.widgetStore[key][0]
                    tab.display(self.fill)

            def renameTab(self, tabName, newName=None):
                if tabName not in self.widgetStore.keys():
                    raise ItemLookupError("Invalid tab name: " + tabName)

                self.widgetStore[tabName][0].rename(newName)

            def changeTab(self, tabName, callFunction=True):
                if tabName not in self.widgetStore.keys(): raise ItemLookupError("Invalid tab name: " + tabName)
                # stop if already selected or disabled
                if self.selectedTab == tabName or self.widgetStore[tabName][0].disabled or self.widgetStore[tabName][0].hidden:
                    return

                self.selectedTab = tabName
                self._configTabs()
                if self.changeEvent is not None and callFunction: self.changeEvent(tabName)

            def getSelectedTab(self):
                return self.selectedTab

            def setFont(self, **kwargs):
                self.tabFont.config(**kwargs)

            def _findNewTab(self):
                for key in list(self.widgetStore.keys()):
                    if not self.widgetStore[key][0].disabled and not self.widgetStore[key][0].hidden:
                        self.changeTab(key)
                        return

                # if we're here - all tabs are disabled
                self.selectedTab = None
                self.EMPTY_PANE.lift()

            def _configTabs(self):
                for key in list(self.widgetStore.keys()):
                    if self.widgetStore[key][0].disabled:
                        if not useTtk:
                            self.widgetStore[key][0].config(bg=self.disabledBg, fg=self.disabledFg, cursor="")
                        else:
                            self.widgetStore[key][0].config(style="DisabledTab.TLabel", cursor="")
                    else:
                        if key == self.selectedTab:
                            if not useTtk:
                                self.widgetStore[key][0].config(bg=self.widgetStore[key][1].cget('bg'), fg=self.activeFg, cursor="")
                            else:
                                self.widgetStore[key][0].config(style="SelectedTab.TLabel", cursor="")
                            self.widgetStore[key][1].lift()
                        else:
                            if not useTtk:
                                self.widgetStore[key][0].config(bg=self.inactiveBg, fg=self.inactiveFg, cursor=self.inactiveCursor)
                            else:
                                self.widgetStore[key][0].config(style="InactiveTab.TLabel", cursor=self.inactiveCursor)

        return TabbedFrame(master, **kwargs)

    @contextmanager
    def tabbedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        try:
            tabs = self.startTabbedFrame(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            tabs = self.openTabbedFrame(title)
        command = kwargs.pop("change", None)
        if command is not None: self.setTabbedFrameChangeCommand(title, command)
        self.configure(**kwargs)
        try: yield tabs
        finally: self.stopTabbedFrame()

    def startTabbedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        return self.startContainer(WIDGET_NAMES.TabbedFrame, title, row, column, colspan, rowspan, sticky)

    def stopTabbedFrame(self):
        # auto close the existing TAB - keep it?
        if self._getContainerProperty('type') == WIDGET_NAMES.Tab:
            self.warn("You didn't STOP the previous TAB")
            self.stopContainer()
        self.stopContainer()

    def setTabbedFrameChangeCommand(self, title, func):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        command = self.MAKE_FUNC(func, title)
        nb.config(command=command)

    def setTabbedFrameTabExpand(self, title, expand=True):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.expandTabs(expand)

    def setTabbedFrameSelectedTab(self, title, tab, callFunction=True):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        try:
            nb.changeTab(tab, callFunction)
        except KeyError:
            raise ItemLookupError("Invalid tab name: " + str(tab))

    def setTabbedFrameDisabledTab(self, title, tab, disabled=True):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.disableTab(tab, disabled)

    def setTabbedFrameDisableAllTabs(self, title, disabled=True):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.disableAllTabs(disabled)

    def deleteTabbedFrameTab(self, title, tab):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        self.cleanseWidgets(nb.getTab(tab))
        nb.deleteTab(tab)

    def showTabbedFrameTab(self, title, tab):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.showTab(tab)

    def hideTabbedFrameTab(self, title, tab):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.hideTab(tab)

    def setTabText(self, title, tab, newText=None):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.renameTab(tab, newText)

    def setTabFont(self, title, **kwargs):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        nb.setFont(**kwargs)

    def setTabBg(self, title, tab, colour):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        tab = nb.getTab(tab)
        gui.SET_WIDGET_BG(tab, colour)
        # tab.config(bg=colour)
        #gui.SET_WIDGET_BG(tab, colour)
        for child in tab.winfo_children():
            gui.SET_WIDGET_BG(child, colour)

    @contextmanager
    def tab(self, title, tabTitle=None, **kwargs):
        beforeTab = kwargs.pop("beforeTab", None)
        afterTab = kwargs.pop("afterTab", None)
        if tabTitle is None:
            try:
                tab = self.startTab(title, beforeTab, afterTab)
            except ItemLookupError:
                if self._getContainerProperty('type') != WIDGET_NAMES.TabbedFrame:
                    raise Exception("Can't open a Tab in the current container: ", self._getContainerProperty('type'))
                else:
                    tabTitle = self._getContainerProperty('title')
                    tab = self.openTab(tabTitle, title)
        else:
            tab = self.openTab(title, tabTitle)
        self.configure(**kwargs)
        try: yield tab
        finally: self.stopTab()

    def startTab(self, title, beforeTab=None, afterTab=None):

        if beforeTab is not None and afterTab is not None:
            self.warn("You can't specify a before and after value for tab: %s", title)
            beforeTab = afterTab = None

        # auto close the previous TAB - keep it?
        if self._getContainerProperty('type') == WIDGET_NAMES.Tab:
            self.warn("You didn't STOP the previous TAB")
            self.stopContainer()
        elif self._getContainerProperty('type') != WIDGET_NAMES.TabbedFrame:
            raise Exception("Can't add a Tab to the current container: ", self._getContainerProperty('type'))

        tf = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, self._getContainerProperty("title"))
        tf.setBeforeTab(beforeTab)
        tf.setAfterTab(afterTab)
        tab = self.startContainer(WIDGET_NAMES.Tab, title)
        tf.setBeforeTab()
        tf.setAfterTab()
        return tab

    def getTabbedFrameSelectedTab(self, title):
        nb = self.widgetManager.get(WIDGET_NAMES.TabbedFrame, title)
        return nb.getSelectedTab()

    def stopTab(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.Tab:
            raise Exception("Can't stop a TAB, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

#####################################
# Simple Tables
#####################################

    def _getDbTables(self, db):
        ''' query the specified database, and get a list of table names '''
        self._importSqlite3()
        if not sqlite3:
            self.error("Unable to load DB tables - can't load sqlite3")
            return []

        query = "SELECT DISTINCT tbl_name FROM sqlite_master ORDER BY tbl_name COLLATE NOCASE"
        data = []

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor:
                data.append(row[0])
        return data

    def replaceDbTable(self, title, db, table):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.db = db
        grid.dbTable = table
        self._importSqlite3()
        if not sqlite3:
            self.error("Unable to load DB data - can't load sqlite3")
            return

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            dataQuery = 'SELECT * from ' + table

            # select all data
            cursor.execute(dataQuery)
            self.setTableHeaders(title, cursor)
            self.replaceAllTableRows(title, cursor)
        self.topLevel.update_idletasks()

    def disableTableEntry(self, title, entryPos, disabled=True):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.disableEntry(entryPos, disabled=disabled)

    def refreshDbTable(self, title):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        self._importSqlite3()
        if not sqlite3:
            self.error("Unable to load DB data - can't load sqlite3")
            return

        with sqlite3.connect(grid.db) as conn:
            cursor = conn.cursor()
            dataQuery = 'SELECT * from ' + grid.dbTable

            # select all data
            cursor.execute(dataQuery)
            self.replaceAllTableRows(title, cursor)

    def refreshDbOptionBox(self, title, selected=None):
        opt = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)
        data = self._getDbTables(opt.db)
        self.changeOptionBox(title, data)
        if selected is not None:
            self.setOptionBox(title, selected)

    def table(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets tables all in one go """
        widgKind = WIDGET_NAMES.Table
        kind = kwargs.pop("kind", 'normal')

        action=kwargs.pop('action', None)
        addRow=kwargs.pop('addRow', None)
        actionHeading=kwargs.pop('actionHeading', "Action")
        actionButton=kwargs.pop('actionButton', "Press")
        addButton=kwargs.pop('addButton', "Add")
        showMenu=kwargs.pop('showMenu', False)
        horiz=kwargs.pop('horizontal', True)
        change=kwargs.pop('change', None)
        edit=kwargs.pop('edit', None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if value is not None: self.replaceAllTableRows(title, value)
            table = self.getTableEntries(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if kind == 'normal':
                table = self.addTable(title, value, *args,
                            action=action, addRow=addRow, actionHeading=actionHeading, actionButton=actionButton,
                            addButton=addButton, showMenu=showMenu, horizontal=horiz, **kwargs
                        )
            else:
                table = self.addDbTable(title, value, *args,
                            action=action, addRow=addRow, actionHeading=actionHeading, actionButton=actionButton,
                            addButton=addButton, showMenu=showMenu, horizontal=horiz, **kwargs
                        )
        if change is not None: self.setTableChangeFunction(title, change)
        if edit is not None: self.setTableEditFunction(title, edit)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return table

    def addDbTable(self, title, value, table, row=None, column=0, colspan=0, rowspan=0,
                action=None, addRow=None, actionHeading="Action", actionButton="Press",
                addButton="Add", showMenu=False, border="solid", **kwargs):
        ''' creates a new Table, displaying the specified database & table '''

        horiz=kwargs.pop('horizontal', True)

        self._importSqlite3()
        if not sqlite3:
            self.error("Unable to load DB data - can't load sqlite3")
            return

        with sqlite3.connect(value) as conn:
            cursor = conn.cursor()
            dataQuery = 'SELECT * from ' + table

            # select all data
            cursor.execute(dataQuery)

            grid = self.addTable(title, cursor, row, column, colspan, rowspan,
                        action, addRow, actionHeading, actionButton,
                        addButton, showMenu, border=border, horizontal=horiz
                    )
        grid.db = value
        grid.dbTable = table
        return grid

    def addTable(self, title, data, row=None, column=0, colspan=0, rowspan=0, action=None, addRow=None,
                actionHeading="Action", actionButton="Press", addButton="Add", showMenu=False, border="solid", **kwargs):
        ''' creates a new table, displaying the specified data '''
        self.widgetManager.verify(WIDGET_NAMES.Table, title)
        wrap=kwargs.pop('wrap', 250)
        horiz=kwargs.pop('horizontal', True)
        if not self.ttkFlag:
            grid = SimpleTable(self.getContainer(), title, data,
                        action, addRow,
                        actionHeading, actionButton, addButton,
                        showMenu, buttonFont=self._getContainerProperty('buttonFont'),
                        font=self.tableFont, background=self._getContainerBg(),
                        queueFunction=self.queueFunction, border=border, wrap=wrap, horizontal=horiz
                    )
        else:
            grid = SimpleTable(self.getContainer(), title, data,
                        action, addRow,
                        actionHeading, actionButton, addButton,
                        showMenu, buttonFont=self._getContainerProperty('buttonFont'),
                        queueFunction=self.queueFunction, border=border, wrap=wrap, horizontal=horiz
                    )
        self._positionWidget(grid, row, column, colspan, rowspan, N+E+S+W)
        self.widgetManager.add(WIDGET_NAMES.Table, title, grid)
        return grid

    def getTableEntries(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Table, title).getEntries()

    def getTableLastChange(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Table, title).getLastChange()

    def getTableSelectedCells(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Table, title).getSelectedCells()

    def selectTableRow(self, title, row, highlight=None):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.selectRow(row, highlight)

    def setTableEditFunction(self, title, func):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        cmd = self.MAKE_FUNC(func, title)
        grid.config(edit=cmd)

    def selectTableColumn(self, title, col, highlight=None):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.selectColumn(col, highlight)

    def addTableRow(self, title, data):
        ''' adds a new row of data to the specified table '''
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.addRow(data)

    def addTableRows(self, title, data):
        ''' adds multiple rows of data to the specified table '''
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.addRows(data, scroll=True)

    def addTableColumn(self, title, columnNumber, data):
        ''' adds a new column of data, in the specified position, to the specified table '''
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.addColumn(columnNumber, data)

    def deleteTableColumn(self, title, columnNumber):
        ''' deletes the specified column from the specified table '''
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.deleteColumn(columnNumber)

    def setTableHeaders(self, title, data):
        ''' change the headers in the specified table '''
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.setHeaders(data)

    def deleteTableRow(self, title, rowNum):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.deleteRow(rowNum)

    def deleteAllTableRows(self, title):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.deleteAllRows()

    def sortTable(self, title, columnNumber, descending=False):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.sort(columnNumber, descending)

    def getTableRowCount(self, title):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        return grid.getRowCount()

    def getTableRow(self, title, rowNumber):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        return grid.getRow(rowNumber)

    def confTable(self, title, field, value):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        kw = {field:value}
        grid.config(**kw)

    def replaceTableRow(self, title, rowNum, data):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.replaceRow(rowNum, data)

    def replaceAllTableRows(self, title, data, deleteHeader=True):
        grid = self.widgetManager.get(WIDGET_NAMES.Table, title)
        grid.deleteAllRows(deleteHeader=deleteHeader)
        grid.addRows(data, scroll=False)

    # temporary deprecated functions
    def addGrid(self, title, data, row=None, column=0, colspan=0, rowspan=0, action=None, addRow=None,
                actionHeading="Action", actionButton="Press", addButton="Add", showMenu=False):
        ''' DEPRECATED - adds a new grid widget with the specified data '''
        gui.warn("Deprecated - grids renamed to tables")
        return self.addTable(title, data, row, column, colspan, rowspan, action, addRow, actionHeading, actionButton, addButton, showMenu)
    def addDbGrid(self, title, db, table, row=None, column=0, colspan=0, rowspan=0, action=None, addRow=None,
                actionHeading="Action", actionButton="Press", addButton="Add", showMenu=False):
        ''' DEPRECATED - adds a new table widget, with the specified database and table '''
        gui.warn("Deprecated - grids renamed to tables")
        return self.addDbTable(title, db, table, row, column, colspan, rowspan, action, addRow, actionHeading, actionButton, addButton, showMenu)
    def replaceDbGrid(self, title, db, table):
        gui.warn("Deprecated - grids renamed to tables")
        return self.replaceDbTable(title, db, table)
    def refreshDbGrid(self, title):
        gui.warn("Deprecated - grids renamed to tables")
        return self.refreshDbTable(title)
    def selectGridRow(self, title, row, highlight=None):
        gui.warn("Deprecated - grids renamed to tables")
        return self.selectTableRow(title, row, highlight)
    def getGridEntries(self, title):
        gui.warn("Deprecated - grids renamed to tables")
        return self.getTableEntries(title)
    def getGridSelectedCells(self, title):
        gui.warn("Deprecated - grids renamed to tables")
        return self.getTableSelectedCells(title)
    def selectGridColumn(self, title, col, highlight=None):
        return self.selectTableColumn(title, col, highlight)
    def addGridRow(self, title, data):
        ''' DEPRECATED - adds a row of data to the specified grid '''
        return self.addTableRow(title, data)
    def addGridRows(self, title, data):
        ''' DEPRECATED - adds new rows of data to the specified grid '''
        return self.addTableRows(title, data)
    def addGridColumn(self, title, columnNumber, data):
        ''' DEPRECATED - adds a column of data to the specified grid '''
        return self.addTableColumn(title, columnNumber, data)
    def deleteGridColumn(self, title, columnNumber):
        return self.deleteTableColumn(title, columnNumber)
    def setGridHeaders(self, title, data):
        return self.setTableHeaders(title, data)
    def deleteGridRow(self, title, rowNum):
        return self.deleteTableRow(title, rowNum)
    def deleteAllGridRows(self, title):
        return self.deleteAllTableRows(title)
    def sortGrid(self, title, columnNumber, descending=False):
        return self.sortTable(title, columnNumber, descending)
    def getGridRowCount(self, title):
        return self.getTableRowCount(title)
    def getGridRow(self, title, rowNumber):
        return self.getTableRow(title, rowNumber)
    def confGrid(self, title, field, value):
        return self.confTable(title, field, value)
    def replaceGridRow(self, title, rowNum, data):
        return self.replaceTableRow(title, rowNum, data)
    def replaceAllGridRows(self, title, data):
        return self.replaceAllTableRows(title, data)

#####################################
# Paned Frames
#####################################

    @contextmanager
    def panedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        vertical = kwargs.pop("vertical", False)
        sash = kwargs.pop("sash", 50)
        reOpen = False
        try:
            pane = self.startPanedFrame(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            reOpen = True
            pane = self.openPane(title)
        if vertical: self.setPanedFrameVertical(title)
        self.configure(**kwargs)
        try: yield pane
        finally:
            if reOpen:
                self.stopContainer()
            else:
                self.stopPanedFrame()
                self.setPaneSashPosition(sash, pane)

    @contextmanager
    def panedFrameVertical(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        gui.warn('Setting panedFrameVertical(%s) is deprecated, please use panedFrame(vertical=True)', title)
        reOpen = False
        sash = kwargs.pop("sash", 50)
        try:
            pane = self.startPanedFrameVertical(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            reOpen = True
            pane = self.openPane(title)
        self.configure(**kwargs)
        try: yield pane
        finally:
            if reOpen:
                self.stopContainer()
            else:
                self.stopPanedFrame()
                self.setPaneSashPosition(sash, pane)

    def startPanedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        p = self.startContainer(WIDGET_NAMES.PanedFrame, title, row, column, colspan, rowspan, sticky)
        return p

    def startPanedFrameVertical( self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        p = self.startPanedFrame(title, row, column, colspan, rowspan, sticky)
        self.setPanedFrameVertical(title)
        return p

    def stopPanedFrame(self):
        if self._getContainerProperty('type') == WIDGET_NAMES.Pane:
            self.stopContainer()
        if self._getContainerProperty('type') != WIDGET_NAMES.PanedFrame:
            raise Exception("Can't stop a PANEDFRAME, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

    # make a PanedFrame align vertically
    def setPanedFrameVertical(self, window):
        pane = self.widgetManager.get(WIDGET_NAMES.PanedFrame, window)
        pane.config(orient=VERTICAL)

    def setPaneSashPosition(self, pos, pane=None):
        # convert to a percentage if needed
        if pos > 1: pos = pos / 100.0

        if pane is None:
            if self._getContainerProperty('type') == WIDGET_NAMES.PanedFrame:
                pane = self._getContainerProperty('container')
            elif self.containerStack[-2]['type'] == WIDGET_NAMES.PanedFrame:
                pane = self.containerStack[-2]['container']
            elif self._getContainerProperty('type') == WIDGET_NAMES.Pane:
                pane = self._getContainerProperty('container').parent
            else:
                gui.error("Unable to set sash position - can't find a pane")
                return
        elif type(pane) == str:
            pane = self.widgetManager.get(WIDGET_NAMES.PanedFrame, pane)

        if pane.cget('orient') == 'horizontal':
            w = int(pane.winfo_width() * pos)
            try:
                pane.sash_place(0, w, 0)
                gui.trace('Set horizontal pane: %s to position: %s', pane, pos)
            except TclError as e:
                # no sash to configure - last pane
                pass
        else:
            h = int(pane.winfo_height() * pos)
            try:
                pane.sash_place(0, 0, h)
                gui.trace('Set vertical pane: %s to position: %s', pane, pos)
            except TclError as e:
                # no sash to configure - last pane
                pass

#####################################
# Label Frames
#####################################

    @contextmanager
    def labelFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky=W, hideTitle=False, **kwargs):
        name = kwargs.pop("label", kwargs.pop("name", None))
        labelFg = kwargs.pop("labelFg", self.fg)
        try:
            lf = self.startLabelFrame(title, row, column, colspan, rowspan, sticky, hideTitle, name)
        except ItemLookupError:
            lf = self.openLabelFrame(title)
        self.configure(**kwargs)
        if not self.ttkFlag:
            lf.config(fg=labelFg)
        try: yield lf
        finally: self.stopLabelFrame()

    # sticky is alignment inside frame
    # frame will be added as other widgets
    def startLabelFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky=W, hideTitle=False, label=None, name=None):
        if label is not None: name = label
        if hideTitle: name = ''
        lf = self.startContainer(WIDGET_NAMES.LabelFrame, title, row, column, colspan, rowspan, sticky, name)
        return lf

    def stopLabelFrame(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.LabelFrame:
            raise Exception("Can't stop a LABELFRAME, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

    # function to set position of title for label frame
    def setLabelFrameTitle(self, title, newTitle):
        frame = self.widgetManager.get(WIDGET_NAMES.LabelFrame, title)
        frame.config(text=newTitle)

#####################################
# Toggle Frames
#####################################

    @contextmanager
    def toggleFrame(self, title, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        try:
            tog = self.startToggleFrame(title, row, column, colspan, rowspan)
        except ItemLookupError:
            tog = self.openToggleFrame(title)
        self.configure(**kwargs)
        try: yield tog
        finally: self.stopToggleFrame()

    ###### TOGGLE FRAMES #######
    def startToggleFrame(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.startContainer(WIDGET_NAMES.ToggleFrame, title, row, column, colspan, rowspan, sticky="new")

    def stopToggleFrame(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.ToggleFrame:
            raise Exception("Can't stop a TOGGLEFRAME, currently in:",
                            self._getContainerProperty('type'))
        self._getContainerProperty('container').stop()
        self.stopContainer()

    def toggleToggleFrame(self, title):
        toggle = self.widgetManager.get(WIDGET_NAMES.ToggleFrame, title)
        toggle.toggle()

    def setToggleFrameText(self, title, newText):
        toggle = self.widgetManager.get(WIDGET_NAMES.ToggleFrame, title)
        toggle.config(text=newText)

    def getToggleFrameState(self, title):
        toggle = self.widgetManager.get(WIDGET_NAMES.ToggleFrame, title)
        return toggle.isShowing()

#####################################
# Paged Windows
#####################################

    @contextmanager
    def pagedWindow(self, title, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        try:
            pw = self.startPagedWindow(title, row, column, colspan, rowspan)
        except ItemLookupError:
            pw = self.openPagedWindow(title)
        self.configure(**kwargs)
        try: yield pw
        finally: self.stopPagedWindow()

    ###### PAGED WINDOWS #######
    def startPagedWindow(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.startContainer( WIDGET_NAMES.PagedWindow, title, row, column, colspan, rowspan, sticky="nsew")

    def setPagedWindowPage(self, title, page):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        pager.showPage(page)

    def setPagedWindowButtonsTop(self, title, top=True):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        pager.setNavPositionTop(top)

    def setPagedWindowButtons(self, title, buttons):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        if not isinstance(buttons, list) or len(buttons) != 2:
            raise Exception(
                "You must provide a list of two strings for setPagedWinowButtons()")
        pager.setPrevButton(buttons[0])
        pager.setNextButton(buttons[1])

    def setPagedWindowFunction(self, title, func):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        command = self.MAKE_FUNC(func, title)
        pager.registerPageChangeEvent(command)

    def getPagedWindowPageNumber(self, title):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        return pager.getPageNumber()

    def showPagedWindowPageNumber(self, title, show=True):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        pager.showPageNumber(show)

    def showPagedWindowTitle(self, title, show=True):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        pager.showTitle(show)

    def setPagedWindowTitle(self, title, pageTitle):
        pager = self.widgetManager.get(WIDGET_NAMES.PagedWindow, title)
        pager.setTitle(pageTitle)

    @contextmanager
    def page(self, windowTitle=None, pageNumber=None, sticky="nw", **kwargs):
        if windowTitle is None:
            pg = self.startPage(sticky)
        else:
            pg = self.openPage(windowTitle, pageNumber)
        self.configure(**kwargs)
        try: yield pg
        finally: self.stopPage()


    def startPage(self, sticky="nw"):
        if self._getContainerProperty('type') == WIDGET_NAMES.Page:
            self.warn("You didn't STOP the previous PAGE")
            self.stopPage()
        elif self._getContainerProperty('type') != WIDGET_NAMES.PagedWindow:
            raise Exception("Can't start a PAGE, currently in:",
                            self._getContainerProperty('type'))

        self.containerStack[-1]['widgets'] = True

        # generate a page title
        pageNum = self._getContainerProperty('container').frameStack.getNumFrames() + 1
        pageTitle = self._getContainerProperty('title') + "__" + str(pageNum)

        return self.startContainer(WIDGET_NAMES.Page, pageTitle, row=None, column=None, colspan=None, rowspan=None, sticky=sticky)

    def stopPage(self):
        if self._getContainerProperty('type') == WIDGET_NAMES.Page:
            self.stopContainer()
        else:
            raise Exception("Can't stop PAGE, currently in:",
                            self._getContainerProperty('type'))

    def stopPagedWindow(self):
        if self._getContainerProperty('type') == WIDGET_NAMES.Page:
            self.warn("You didn't STOP the previous PAGE")
            self.stopPage()

        if self._getContainerProperty('type') != WIDGET_NAMES.PagedWindow:
            raise Exception("Can't stop a PAGEDWINDOW, currently in:",
                            self._getContainerProperty('type'))

        self._getContainerProperty('container').stopPagedWindow()
        self.stopContainer()

#####################################
# Scrolled Panes
#####################################

    @contextmanager
    def scrollPane(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        disabled = kwargs.pop("disabled", "")
        try:
            sp = self.startScrollPane(title, row, column, colspan, rowspan, sticky, disabled)
        except ItemLookupError:
            sp = self.openScrollPane(title)
        self.configure(**kwargs)
        try: yield sp
        finally: self.stopScrollPane()


    def startScrollPane(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", disabled=""):
        return self.startContainer(WIDGET_NAMES.ScrollPane, title, row, column, colspan, rowspan, sticky, disabled)

    # functions to stop the various containers
    def stopContainer(self): self._removeContainer()

    def stopScrollPane(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.ScrollPane:
            raise Exception("Can't stop a SCROLLPANE, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

    def stopAllPanedFrames(self):
        while True:
            try:
                self.stopPanedFrame()
            except:
                break

#####################################
# Frames
#####################################

    @contextmanager
    def frame(self, title=None, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        if title is None: # new subFrame
            fr = self.startFrame(title, row, column, colspan, rowspan, sticky)
        else:
            frameNumber = kwargs.pop('frameNumber', None)
            try:
                if frameNumber is not None: fr = self.openSubFrame(title, frameNumber)
                else: fr = self.openFrame(title)
            except: # no widget
                fr = self.startFrame(title, row, column, colspan, rowspan, sticky)
        self.configure(**kwargs)
        try: yield fr
        finally: self.stopFrame()

    def startFrame(self, title=None, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        frameType = WIDGET_NAMES.Frame
        if self._getContainerProperty('type') == WIDGET_NAMES.FrameStack:
            # generate a frame title
            frameNum = self._getContainerProperty('container').getNumFrames()
            title = self._getContainerProperty('title') + "__" + str(frameNum)
            gui.trace("Adding new subFrame: %s", title)

            self.containerStack[-1]['widgets'] = True
            frameType = WIDGET_NAMES.SubFrame
        else:
            if title is None:
                raise Exception("All frames must have a title")
            gui.trace("Adding new frame: %s", title)

        return self.startContainer(frameType, title, row, column, colspan, rowspan, sticky)

    def stopFrame(self):
        if self._getContainerProperty('type') not in [WIDGET_NAMES.Frame, WIDGET_NAMES.SubFrame]:
            raise Exception("Can't stop a FRAME, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

    def raiseFrame(self, title):
        ''' will bring the named frame in front of any others '''
        gui.trace("Raising frame: %s", title)
        self.widgetManager.get(WIDGET_NAMES.Frame, title).lift()

#####################################
# FrameStack
#####################################

    @contextmanager
    def frameStack(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW", **kwargs):
        change = kwargs.pop("change", None)
        start = kwargs.pop("start", -1)
        try:
            fr = self.startFrameStack(title, row, column, colspan, rowspan, sticky, change=change, start=start)
        except ItemLookupError:
            fr = self.openFrameStack(title)
        self.configure(**kwargs)
        try: yield fr
        finally:
            self.stopFrameStack()

    def startFrameStack(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="news", change=None, start=-1):
        fs = self.startContainer(WIDGET_NAMES.FrameStack, title, row, column, colspan, rowspan, sticky)
        fs.setChangeFunction(change)
        fs.setStartFrame(start)
        return fs

    def stopFrameStack(self):
        if self._getContainerProperty('type') != WIDGET_NAMES.FrameStack:
            raise Exception("Can't stop a FRAMESTACK, currently in:",
                            self._getContainerProperty('type'))
        self.stopContainer()

    def setStartFrame(self, title, num):
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).setStartFrame(num)

    def nextFrame(self, title, callFunction=True):
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).showNextFrame(callFunction)
    def prevFrame(self, title, callFunction=True):
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).showPrevFrame(callFunction)
    def firstFrame(self, title, callFunction=True):
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).showFirstFrame(callFunction)
    def lastFrame(self, title, callFunction=True):
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).showLastFrame(callFunction)
    def selectFrame(self, title, num, callFunction=True):
        if type(num) in (list, tuple): num = num[0]
        num = int(num)
        self.widgetManager.get(WIDGET_NAMES.FrameStack, title).showFrame(num, callFunction)

    def countFrames(self, title):
        return self.widgetManager.get(WIDGET_NAMES.FrameStack, title).getNumFrames()
    def getCurrentFrame(self, title):
        return self.widgetManager.get(WIDGET_NAMES.FrameStack, title).getCurrentFrame()
    def getPreviousFrame(self, title):
        return self.widgetManager.get(WIDGET_NAMES.FrameStack, title).getPreviousFrame()

    def frameStackAtStart(self, title):
        return self.widgetManager.get(WIDGET_NAMES.FrameStack, title).atStart()
    def frameStackAtEnd(self, title):
        return self.widgetManager.get(WIDGET_NAMES.FrameStack, title).atEnd()

#####################################
# SubWindows
#####################################

    @contextmanager
    def subWindow(self, name, title=None, modal=False, blocking=False, transient=False, grouped=True, **kwargs):
        visible = kwargs.pop("visible", None)
        try:
            sw = self.startSubWindow(name, title, modal, blocking, transient, grouped)
        except ItemLookupError:
            sw = self.openSubWindow(name)
        self.configure(**kwargs)

        try:
            yield sw
        finally:
            self.stopSubWindow()
        if visible is True: self.showSubWindow(name)

    def startSubWindow(self, name, title=None, modal=False, blocking=False, transient=False, grouped=True):
        self.widgetManager.verify(WIDGET_NAMES.SubWindow, name)
        gui.trace("Starting subWindow %s", name)

        top = SubWindow(self, self.topLevel, name, title=title, stopFunc = self.confirmHideSubWindow,
                        modal=modal, blocking=blocking, transient=transient, grouped=grouped)

        ico = self._getTopLevel().winIcon

        self.widgetManager.add(WIDGET_NAMES.SubWindow, name, top)

        # now, add to top of stack
        self._addContainer(name, WIDGET_NAMES.SubWindow, top, 0, 1, "")

        # add an icon if required
        if ico is not None:
            self.setIcon(ico)
        else:
            top.winIcon = None

        return top

    def stopSubWindow(self):
        container = self.containerStack[-1]
        if container['type'] == WIDGET_NAMES.SubWindow:
            if not hasattr(container["container"], 'ms'):
                self.setMinSize(container["container"])
            self.stopContainer()
        else:
            raise Exception("Can't stop a SUBWINDOW, currently in:",
                            self._getContainerProperty('type'))

    def setSubWindowLocation(self, title, x, y):
        self.widgetManager.get(WIDGET_NAMES.SubWindow, title).setLocation(x, y)

    def showAllSubWindows(self):
        for sub in self.widgetManager.group(WIDGET_NAMES.SubWindow):
            self.showSubWindow(sub)

    # functions to show/hide/destroy SubWindows
    def showSubWindow(self, title, hide=False, follow=False):
        tl = self.widgetManager.get(WIDGET_NAMES.SubWindow, title)
        if hide:
            self.hideAllSubWindows()
        gui.trace("Showing subWindow %s", title)

        tl.show()
        self._bringToFront(tl)
        tl.block()

        return tl

    def hideAllSubWindows(self, useStopFunction=False):
        for sub in self.widgetManager.group(WIDGET_NAMES.SubWindow):
            self.hideSubWindow(sub, useStopFunction)

    def hideSubWindow(self, title, useStopFunction=False):
        self.widgetManager.get(WIDGET_NAMES.SubWindow, title).hide(useStopFunction)

    def confirmHideSubWindow(self, title):
        self.hideSubWindow(title, True)

    def destroySubWindow(self, title):
        gui.trace("Destroying SubWindow %s", title)
        tl = self.widgetManager.get(WIDGET_NAMES.SubWindow, title)
        tl.prepDestroy()
        # get rid of all the kids!
        self.cleanseWidgets(tl)

    def destroyAllSubWindows(self):
        gui.trace("Destroying all SubWindows")
        keys = list(self.widgetManager.group(WIDGET_NAMES.SubWindow).keys())
        for k in keys:
            gui.trace("Destroying SubWindow: %s", k)
            wi = self.widgetManager.get(WIDGET_NAMES.SubWindow, k)
            self.cleanseWidgets(wi)

        # access has widgets stored in the standard widget store
        self.accessMade = False

#####################################
# END containers
#####################################

    # function to destroy widget & all children
    # will also attempt to remove all trace from config dictionaries
    def cleanseWidgets(self, widget):
        widgType = gui.GET_WIDGET_CLASS(widget)
        gui.trace("Attempting to cleanse: %s", widgType)

        # make sure we've cleansed any children first
        for child in widget.winfo_children():
            self.cleanseWidgets(child)


        if hasattr(widget, 'APPJAR_TYPE'):
            widgType = widget.APPJAR_TYPE
            widgName = WIDGET_NAMES.name(widgType)
            gui.trace("Cleansing: %s", widgName)

            if widgType not in [WIDGET_NAMES.Tab, WIDGET_NAMES.Page]:
                if not self.widgetManager.destroyWidget(widgType, widget):
                    self.warn("Unable to destroy %s, during cleanse - destroy returned False", widgName)

                # must clear the frameLabel's label as well
                if widgType == WIDGET_NAMES.FrameLabel:
                    gui.trace("Also Cleansing: %s", WIDGET_NAMES.name(WIDGET_NAMES.Label))
                    if not self.widgetManager.destroyWidget(WIDGET_NAMES.Label, widget):
                        self.warn("Unable to destroy %s, during cleanse - destroy returned False", WIDGET_NAMES.Label)
            else:
                self.trace("Skipped %s, cleansed by parent", widgType)

            # need to remove if a container
            if widgName in WIDGET_NAMES.containers:
                self.trace("Destroying container: %s", widgName)
                self.widgetManager.destroyContainer(WIDGET_NAMES.ContainerLog, widget)

#        elif widgType in ('CanvasDnd', 'ValidationLabel', 'TabBorder', 'TabContainer', 'TabText', 'BgLabel') or hasattr(widget, 'SKIP_CLEANSE'):
        elif widgType in ('CanvasDnd', 'ValidationLabel', 'Grip',
                            'TabBorder', 'TabContainer', 'TabText', 'BgLabel') \
                            or widget.__dict__.get('SKIP_CLEANSE', False):
            pass # not logged in WidgetManager
        else:
            self.warn("Unable to destroy %s, during cleanse - NO APPJAR TYPE", gui.GET_WIDGET_CLASS(widget))

    # functions to hide & show the main window
    def hide(self, btn=None):
        self._getTopLevel().displayed = False
        self._getTopLevel().withdraw()

    def show(self, btn=None):
        self._getTopLevel().displayed = True
        self._getTopLevel().deiconify()

    def setVisible(self, visible=True):
        if visible: self.show()
        else: self.hide()

    def getVisible(self):
        return self.topLevel.displayed

    visible = property(getVisible, setVisible)


#####################################
# warn when bad functions called...
#####################################
    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            self.warn("Unknown function: <%s> Check your spelling, do you need more camelCase?", name)
        return handlerFunction

    def __setattr__(self, name, value):
        # would this create a new attribute?
        if self.built and not hasattr(self, name):
            raise AttributeError("Creating new attributes is not allowed!")
        super(gui, self).__setattr__(name, value)

#####################################
# LabelBox Functions
#####################################

    # this will build a frame, with a label on the left hand side
    def _getLabelBox(self, title, **kwargs):
        self.widgetManager.verify(WIDGET_NAMES.Label, title)

        label = kwargs.pop('label', title)
        if label is True: label = title
        font = kwargs.pop('font', self._getContainerProperty('labelFont'))

        # first, make a frame
        frame = self._makeLabelBox()(self.getContainer())
        if not self.ttkFlag:
            frame.config(background=self._getContainerBg())
        self.widgetManager.log(WIDGET_NAMES.FrameBox, frame)

        # next make the label
        if self.ttkFlag:
            lab = ttk.Label(frame)
        else:
            lab = Label(frame, background=self._getContainerBg())

        frame.theLabel = lab
        lab.hidden = False
        lab.inContainer = True
        lab.config(
            text=label,
            anchor=W,
            justify=LEFT,
            font=font
        )

        if not self.ttkFlag:
            lab.config(background=self._getContainerBg())
        lab.DEFAULT_TEXT = label

        self.widgetManager.add(WIDGET_NAMES.Label, title, lab)
        self.widgetManager.add(WIDGET_NAMES.FrameLabel, title, lab)

        # now put the label in the frame
        lab.pack(side=LEFT, fill=Y)

        return frame

    # this is where we add the widget to the frame built above
    def _packLabelBox(self, frame, widget):
        widget.pack(side=LEFT, fill=BOTH, expand=True)
        widget.inContainer = True
        frame.theWidget = widget
        #widget.grid( row=0, column=1, sticky=W+E )
        #Grid.columnconfigure(frame, 1, weight=1)
        #Grid.rowconfigure(frame, 0, weight=1)

    # function to resize labels, if they are hidden or shown
    # not using this for two reasons:
    # - doesn't really work when font size changes
    # - breaks when things in containers

# this can be made into a container property

#    def _updateLabelBoxes(self, title, column):
#        if len(title) >= self.labWidth.get(column, -1):
#            self.labWidth[column] = len(title)
#            # loop through other labels and resize
#            for na, wi in self.widgetManager.group(WIDGET_NAMES.FrameLabel).items():
#                col = wi.master.grid_info().get("column", wi.master.master.grid_info().get("column", -1))
#                if int(col) == column:
#                    wi.config(width=self.labWidth[column])

#####################################
# FUNCTION for check boxes
#####################################

    def tick(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for checkBox() """
        return self.checkBox(title, value, *args, **kwargs)

    def check(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for checkBox() """
        return self.checkBox(title, value, *args, **kwargs)

    def checkBox(self, title, value=None, *args, **kwargs):
        """ adds, sets & gets checkBoxes all in one go """
        widgKind = WIDGET_NAMES.CheckBox
        callFunction = kwargs.pop("callFunction", True)
        text = kwargs.pop("text", None)

        try: self.widgetManager.verify(widgKind, title)
        except: #widget exists
            if value is not None: self.setCheckBox(title, ticked=value, callFunction=callFunction)
            check = self.getCheckBox(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            check = self._checkBoxMaker(title, *args, **kwargs)
            if value is not None: self.setCheckBox(title, value)
        if text is not None: self.setCheckBoxText(title, text)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return check

    def _checkBoxMaker(self, title, value=None, kind="cb", row=None, column=0, colspan=0, rowspan=0, **kwargs):
        """ internal wrapper to hide kwargs from original add functions """
        name = kwargs.pop("name", kwargs.pop('label', None))
        return self.addCheckBox(title, row, column, colspan, rowspan, name)

    def addCheckBox(self, title, row=None, column=0, colspan=0, rowspan=0, name=None):
        ''' adds a new check box, at the specified position '''
        self.widgetManager.verify(WIDGET_NAMES.CheckBox, title)
        var = IntVar(self.topLevel)
        if name is None:
            name = title

        if not self.ttkFlag:
            cb = Checkbutton(self.getContainer(), text=name, variable=var)
            cb.config(
                font=self._getContainerProperty('labelFont'),
                background=self._getContainerBg(),
                activebackground=self._getContainerBg(),
                anchor=W)
        else:
            cb = ttk.Checkbutton(self.getContainer(), text=name, variable=var)

        cb.DEFAULT_TEXT = name
        cb.bind("<Button-1>", self._grabFocus)
        self.widgetManager.add(WIDGET_NAMES.CheckBox, title, cb)
        self.widgetManager.add(WIDGET_NAMES.CheckBox, title, var, group=WidgetManager.VARS)
        self._positionWidget(cb, row, column, colspan, rowspan, EW)
        return cb

    def setCheckBoxText(self, title, text):
        cb = self.widgetManager.get(WIDGET_NAMES.CheckBox, title)
        cb.DEFAULT_TEXT = text
        cb.config(text=text)

    def addNamedCheckBox(self, name, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a new check box, at the specified position, with the name as the text '''
        return self.addCheckBox(title, row, column, colspan, rowspan, name)

    def getCheckBox(self, title):
        bVar = self.widgetManager.get(WIDGET_NAMES.CheckBox, title, group=WidgetManager.VARS)
        if bVar.get() == 1:
            return True
        else:
            return False

    def getAllCheckBoxes(self):
        cbs = {}
        for k in self.widgetManager.group(WIDGET_NAMES.CheckBox):
            cbs[k] = self.getCheckBox(k)
        return cbs

    def setCheckBox(self, title, ticked=True, callFunction=True):
        cb = self.widgetManager.get(WIDGET_NAMES.CheckBox, title)
        bVar = self.widgetManager.get(WIDGET_NAMES.CheckBox, title, group=WidgetManager.VARS)
        bVar.set(ticked)
        if ticked:
            if not self.ttkFlag:
                cb.select()
            else:
                cb.state(['selected'])
        else:
            if not self.ttkFlag:
                cb.deselect()
            else:
                cb.state(['!selected'])
        # now call function
        if callFunction:
            if hasattr(cb, 'cmd'):
                cb.cmd()

    def setCheckBoxBoxBg(self, title, newCol):
        self.setCheckBoxSelectColour(title, newCol)

    def setCheckBoxSelectColour(self, title, newCol):
        cb = self.widgetManager.get(WIDGET_NAMES.CheckBox, title)
        cb.config(selectcolor=newCol)

    def clearAllCheckBoxes(self, callFunction=False):
        for cb in self.widgetManager.group(WIDGET_NAMES.CheckBox):
            self.setCheckBox(cb, ticked=False, callFunction=callFunction)

#####################################
# FUNCTION for scales
#####################################

    def slider(self, title, *args, **kwargs):
        """ simpleGUI - alternative for scale() """
        return self.scale(title, *args, **kwargs)

    def scale(self, title, *args, **kwargs):
        """ simpleGUI - adds, sets & gets scales all in one go """
        widgKind = WIDGET_NAMES.Scale

        vert = kwargs.pop("direction", "horizontal").lower() == "vertical"
        increment = kwargs.pop("increment", None)
        value = kwargs.pop("value", None)
        interval = kwargs.pop("interval", None)
        show = kwargs.pop("show", False)
        _range = kwargs.pop("range", None)
        callFunction = kwargs.pop("callFunction", True)
        label = kwargs.pop("label", False)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            scale = self.getScale(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            scale = self._scaleMaker(title, label, *args, **kwargs)

        if _range is not None: self.setScaleRange(title, _range[0], _range[1])
        if vert: self.setScaleVertical(title)
        if increment is not None: self.setScaleIncrement(title, increment)
        if interval is not None: self.showScaleIntervals(title, interval)
        if show: self.showScaleValue(title)
        if value is not None: self.setScale(title, value, callFunction)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return scale

    def _buildScale(self, title, frame):
        self.widgetManager.verify(WIDGET_NAMES.Scale, title)
        var = DoubleVar(self.topLevel)
        if not self.ttkFlag:
            scale = self._makeAjScale()(frame, increment=10, variable=var, repeatinterval=10, orient=HORIZONTAL, font=self._getContainerProperty('inputFont'))
            scale.config(digits=1, showvalue=False, highlightthickness=1)
        else:
            scale = self._makeAjScale()(frame, increment=10, variable=var, orient=HORIZONTAL)

        scale.bind("<Button-1>", self._grabFocus, "+")
        scale.var = var
        scale.inContainer = False
        self.widgetManager.add(WIDGET_NAMES.Scale, title, scale)
        return scale

    def _scaleMaker(self, title, label, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        if label: return self.addLabelScale(title, row, column, colspan, rowspan, label)
        else: return self.addScale(title, row, column, colspan, rowspan)

    def addScale(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a slidable scale at the specified position '''
        scale = self._buildScale(title, self.getContainer())
        self._positionWidget(scale, row, column, colspan, rowspan)
        return scale

    def addLabelScale(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds a slidable scale, with a label showing the title  at the specified position '''
        frame = self._getLabelBox(title, label=label)
        scale = self._buildScale(title, frame)
        self._packLabelBox(frame, scale)
        self._positionWidget(frame, row, column, colspan, rowspan)
        return scale

    def getScale(self, title):
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        return sc.get()

    def getAllScales(self):
        scales = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Scale):
            scales[k] = self.getScale(k)
        return scales

    def setScale(self, title, pos, callFunction=True):
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        with PauseCallFunction(callFunction, sc):
            sc.set(pos)

    def clearAllScales(self, callFunction=False):
        for sc in self.widgetManager.group(WIDGET_NAMES.Scale):
            self.setScale(sc, self.widgetManager.get(WIDGET_NAMES.Scale, sc).cget("from"), callFunction=callFunction)

    def setScaleIncrement(self, title, increment):
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        sc.increment = increment

    def setScaleLength(self, title, length):
        if not self.ttkFlag:
            sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
            sc.config(sliderlength=length)
        else:
            self.warn("ttk: setScaleLength() not supported: %s", title)

    # this will make the scale show interval numbers
    # set to 0 to remove
    def showScaleIntervals(self, title, intervals):
        if not self.ttkFlag:
            sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
            sc.config(tickinterval=intervals)
        else:
            self.warn("ttk: showScaleIntervals() not supported: %s", title)

    # this will make the scale show its value
    def showScaleValue(self, title, show=True):
        if not self.ttkFlag:
            sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
            sc.config(showvalue=show)
        else:
            self.warn("ttk: showScaleValue() not supported: %s", title)

    # change the orientation (Hor or Vert)
    def setScaleVertical(self, title):
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        sc.config(orient=VERTICAL)

    def setScaleHorizontal(self, title):
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        sc.config(orient=HORIZONTAL)

    def setScaleRange(self, title, start, end, curr=None):
        if curr is None:
            curr = start
        sc = self.widgetManager.get(WIDGET_NAMES.Scale, title)
        sc.config(from_=start, to=end)
        self.setScale(title, curr)

        # set the increment as 10%
        try:
            res = sc.cget("resolution")
            diff = int((((end - start)/res)/10)+0.99) # add 0.99 to round up...
            sc.increment = diff
        except:
            pass # resolution not supported in ttk

#####################################
# FUNCTION for optionMenus
#####################################

    def combo(self, title, value=None, *args, **kwargs):
        """ shortner for optionBox() """
        return self.optionBox(title, value, *args, **kwargs)

    def option(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for optionBox() """
        return self.optionBox(title, value, *args, **kwargs)

    def optionbox(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for optionBox() """
        return self.optionBox(title, value, *args, **kwargs)

    def optionBox(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets optionBoxes all in one go """
        widgKind = WIDGET_NAMES.OptionBox
        kind = kwargs.pop("kind", "standard").lower().strip()
        label = kwargs.pop("label", False)
        callFunction = kwargs.pop("callFunction", True)
        override = kwargs.pop("override", False)
        checked = kwargs.pop("checked", True)
        selected = kwargs.pop("selected", None)
        disabled = kwargs.pop("disabled", "-")

        # select=set, replace=change, rename=rename, clear=clear, delete=delete
        if value is None: mode = 'get'
        else: mode = 'select'
        mode = kwargs.pop("mode", mode)
        index = kwargs.pop("index", None)
        newName = kwargs.pop("newName", None)

        try: self.widgetManager.verify(WIDGET_NAMES.OptionBox, title)
        except: # widget exists
            if mode == "select":
                if value is not None: self.setOptionBox(title, index=value, value=True, callFunction=callFunction, override=override)
                else: gui.error("No item specified to select in optionBox: %s", title)
            elif mode == "deselect":
                if value is not None: self.setOptionBox(title, index=value, value=False, callFunction=callFunction, override=override)
                else:
                    self.clearOptionBox(title, callFunction=callFunction)
                    gui.info("optionBox set back to its original state: %s", title)
            elif mode == "toggle":
                gui.error("Toggling optionboxes not supported: %s", title)
            elif mode == "clear":
                if value is not None: gui.error("No value should be specified wen clearing optionBox: %s", title)
                else: self.clearOptionBox(title, callFunction=callFunction)
            elif mode == "rename":
                if value is not None: self.renameOptionBox(title, item=value, newName=newName, callFunction=callFunction)
                else: gui.error("No item specified to rename in optionBox: %s", title)
            elif mode == "replace":
                if value is not None: self.changeOptionBox(title, options=value, index=index, callFunction=callFunction)
                else: gui.error("No values specified to replace in optionBox: %s", title)
            elif mode == "delete":
                if value is not None: self.deleteOptionBox(title, index=value)
                else: gui.error("No item specified to delete in optionBox: %s", title)
            elif mode == "get":
                pass
            else:
                gui.error("Invalid mode (%s) specified in optionBox: %s", mode, title)

            opt =  self.getOptionBox(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if kind == "ticks":
                if label: opt = self.addLabelTickOptionBox(title, value, *args, label=label, disabled=disabled, **kwargs)
                else: opt = self.addTickOptionBox(title, value, *args, disabled=disabled, **kwargs)
            else:
                if label: opt = self.addLabelOptionBox(title, value, *args, label=label, disabled=disabled, **kwargs)
                else: opt = self.addOptionBox(title, value, *args, disabled=disabled, **kwargs)
                if selected is not None: self.setOptionBox(title, selected)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return opt

    def addDbOptionBox(self, title, db, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        ''' adds an option box, with a list of tables form the specified database '''
        data = self._getDbTables(db)
        opt = self.option(title, data, row, column, colspan, rowspan, **kwargs)
        opt.db = db
        return opt

    def _buildOptionBox(self, frame, title, options, kind="normal", disabled='-'):
        """ Internal wrapper, used for building OptionBoxes.
        It will use the kind to choose either a standard OptionBox or a TickOptionBox.
        ref: http://stackoverflow.com/questions/29019760/how-to-create-a-combobox-that-includes-checkbox-for-each-item

        :param frame: this should be a container, used as the parent for the OptionBox
        :param title: the key used to reference this OptionBox
        :param options: a list of values to put in the OptionBox, can be len 0
        :param kind: the style of OptionBox: notmal or ticks
        :returns: the created OptionBox
        :raises ItemLookupError: if the title is already in use
        """
        self.widgetManager.verify(WIDGET_NAMES.OptionBox, title)

        # create a string var to hold selected item
        var = StringVar(self.topLevel)
        self.widgetManager.add(WIDGET_NAMES.OptionBox, title, var, group=WidgetManager.VARS)

        maxSize, options = self._configOptionBoxList(title, options, kind)

        if len(options) > 0 and kind == "normal":
            option = ajOption(frame, var, *options)
            var.set(options[0])
            option.kind = "normal"

        elif kind == "ticks":
            option = ajOption(frame, variable=var, value="")
            self._buildTickOptionBox(title, option, options)
        else:
            option = ajOption(frame, var, [])
            option.kind = "normal"

        option.config(
            justify=LEFT,
            font=self._getContainerProperty('inputFont'),
#            background=self._getContainerBg(),
            highlightthickness=0,
            width=maxSize,
            takefocus=1)
        option.bind("<Button-1>", self._grabFocus)

        # compare on windows & mac
        #option.config(highlightthickness=12, bd=0, highlightbackground=self._getContainerBg())
        option.var = var
        option.maxSize = maxSize
        option.inContainer = False
        option.options = options
        option.disabled = disabled

        option.DEFAULT_TEXT=""
        if options is not None:
            option.DEFAULT_TEXT='\n'.join(str(x) for x in options)

#        if self.platform == self.MAC:
#            option.config(highlightbackground=self._getContainerBg())

        option.bind("<Tab>", self._focusNextWindow)
        option.bind("<Shift-Tab>", self._focusLastWindow)

        # add a right click menu
        self._addRightClickMenu(option)

        # disable any separators
        self._disableOptionBoxSeparators(option)

        # add to array list
        self.widgetManager.add(WIDGET_NAMES.OptionBox, title, option)
        return option

    def _buildTickOptionBox(self, title, option, options):
        """ Internal wrapper, used for building TickOptionBoxes.
        Called by _buildOptionBox & changeOptionBox.
        Will add each of the options as a tick box, and use the title as a disabled header.

        :param title: the key used to reference this OptionBox
        :param option: an existing OptionBox that will be emptied & repopulated
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: None - the option param is modified
        :raises ItemLookupError: if the title can't be found
        """
        # delete any items - either the initial one when created, or any existing ones if changing
        option['menu'].delete(0, 'end')
        var = self.widgetManager.get(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS)
        var.set(title)
        vals = {}
        for o in options:
            vals[o] = BooleanVar()
            option['menu'].add_checkbutton( label=o, onvalue=True, offvalue=False, variable=vals[o])
        self.widgetManager.update(WIDGET_NAMES.TickOptionBox, title, vals, group=WidgetManager.VARS)
        option.kind = "ticks"

    def addOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0, disabled='-', **kwargs):
        """ Adds a new standard OptionBox.
        Simply calls internal function _buildOptionBox.

        :param title: the key used to reference this OptionBox
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: the created OptionBox
        :raises ItemLookupError: if the title is already in use
        """
        option = self._buildOptionBox(self.getContainer(), title, options, disabled=disabled)
        self._positionWidget(option, row, column, colspan, rowspan)
        return option

    def addLabelOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0, disabled="-", **kwargs):
        """ Adds a new standard OptionBox, with a Label before it.
        Simply calls internal function _buildOptionBox, placing it in a LabelBox.

        :param title: the key used to reference this OptionBox and text for the Label
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: the created OptionBox (not the LabelBox)
        :raises ItemLookupError: if the title is already in use
        """
        frame = self._getLabelBox(title, **kwargs)
        option = self._buildOptionBox(frame, title, options, disabled=disabled)
        self._packLabelBox(frame, option)
        self._positionWidget(frame, row, column, colspan, rowspan)
        return option

    def addTickOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0, disabled="-", **kwargs):
        """ Adds a new TickOptionBox.
        Simply calls internal function _buildOptionBox.

        :param title: the key used to reference this TickOptionBox
        :param options: a list of values to put in the TickOptionBox, can be len 0
        :returns: the created TickOptionBox
        :raises ItemLookupError: if the title is already in use
        """
        tick = self._buildOptionBox(self.getContainer(), title, options, kind="ticks", disabled=disabled)
        self._positionWidget(tick, row, column, colspan, rowspan)
        return tick

    def addLabelTickOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0, disabled="-", **kwargs):
        """ Adds a new TickOptionBox, with a Label before it
        Simply calls internal function _buildOptionBox, placing it in a LabelBox

        :param title: the key used to reference this TickOptionBox, and text for the Label
        :param options: a list of values to put in the TickOptionBox, can be len 0
        :returns: the created TickOptionBox (not the LabelBox)
        :raises ItemLookupError: if the title is already in use
        """
        frame = self._getLabelBox(title, **kwargs)
        tick = self._buildOptionBox(frame, title, options, kind="ticks", disabled=disabled)
        self._packLabelBox(frame, tick)
        self._positionWidget(frame, row, column, colspan, rowspan)
        return tick

    def getOptionBox(self, title):
        """ Gets the selected item from the named OptionBox

        :param title: the OptionBox to check
        :returns: the selected item in an OptionBox or a dictionary of all items and their status for a TickOptionBox
        :raises ItemLookupError: if the title can't be found
        """
        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)

        if box.kind == "ticks":
            val = self.widgetManager.get(WIDGET_NAMES.TickOptionBox, title, group=WidgetManager.VARS)
            retVal = {}
            for k, v in val.items():
                retVal[k] = bool(v.get())
            return retVal
        else:
            val = self.widgetManager.get(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS)
            val = val.get().strip()
            # set to None if it's a divider
            if val.startswith("-") or len(val) == 0:
                val = None
            return val

    def getAllOptionBoxes(self):
        """ Convenience function to get the selected items for all OptionBoxes in the GUI.

        :returns: a dictionary containing the result of calling getOptionBox for every OptionBox/TickOptionBox in the GUI
        """
        boxes = {}
        for k in self.widgetManager.group(WIDGET_NAMES.OptionBox):
            boxes[k] = self.getOptionBox(k)
        return boxes

    def _disableOptionBoxSeparators(self, box):
        """ Loops through all items in box and if they start with a dash, disables them

        :param box: the OptionBox to process
        :returns: None
        """
        for pos, item in enumerate(box.options):
            if item.startswith(box.disabled):
                box["menu"].entryconfigure(pos, state="disabled")
            else:
                box["menu"].entryconfigure(pos, state="normal")

    def _configOptionBoxList(self, title, options, kind):
        """ Tidies up the list provided when an OptionBox is created/changed

        :param title: the title for the OptionBox - only used by TickOptionBox to calculate max size
        :param options: the list to tidy
        :param kind: The kind of option box (normal or ticks)
        :returns: a tuple containing the maxSize (width) and tidied list of items
        """

        # deal with a dict_keys object - messy!!!!
        if not isinstance(options, list):
            options = list(options)

        # make sure all options are strings
        options = [str(i) for i in options]

        # check for empty strings, replace first with message, remove rest
        found = False
        newOptions = []
        for pos, item in enumerate(options):
            if str(item).strip() == "":
                if not found:
                    newOptions.append("- options -")
                    found = True
            else:
                newOptions.append(item)

        options = newOptions

        # get the longest string length
        try:
            maxSize = len(str(max(options, key=len)))
        except:
            try:
                maxSize = len(str(max(options)))
            except:
                maxSize = 0

        # increase if ticks
        if kind == "ticks":
            if len(title) > maxSize:
                maxSize = len(title)

        # new bug?!? - doesn't fit anymore!
        if self.platform == self.MAC:
            maxSize += 3
        return maxSize, options

    def changeOptionBox(self, title, options, index=None, callFunction=False):
        """ Changes the entire contents of the named OptionBox
        ref: http://www.prasannatech.net/2009/06/tkinter-optionmenu-changing-choices.html

        :param title: the OptionBox to change
        :param options: the new values to put in the OptionBox
        :param index: an optional initial value to select
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        # get the optionBox & associated var
        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)

        # tidy up list and get max size
        maxSize, options = self._configOptionBoxList(title, options, "normal")

        # warn if new options bigger
        if maxSize > box.maxSize:
            self.warn("The new options are wider then the old ones: %s > %s", maxSize, box.maxSize)

        if box.kind == "ticks":
            self._buildTickOptionBox(title, box, options)
        else:
            # delete the current options
            box['menu'].delete(0, 'end')

            # add the new items
            for option in options:
                box["menu"].add_command(
                    label=option, command=lambda temp=option: box.setvar(
                        box.cget("textvariable"), value=temp))

            with PauseCallFunction(callFunction, box):
                box.var.set(options[0])

        box.options = options

        # disable any separators
        self._disableOptionBoxSeparators(box)
        # select the specified option
        self.setOptionBox(title, index, callFunction=False, override=True)

    def deleteOptionBox(self, title, index):
        """ Deleted the specified item from the named OptionBox

        :param title: the OptionBox to change
        :param inde: the value to delete - either a numeric index, or the text of an item
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self.widgetManager.check(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS)
        self.setOptionBox(title, index, value=None, override=True)

    def renameOptionBoxItem(self, title, item, newName=None, callFunction=False):
        """ Changes the text of the specified item in the named OptionBox
        :param title: the OptionBox to change
        :param item: the item to rename
        :param newName: the value to rename it with
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self.widgetManager.check(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS)
        self.setOptionBox(title, item, value=newName, callFunction=callFunction)

    def clearOptionBox(self, title, callFunction=True):
        """ Deselects any items selected in the named OptionBox
        If a TickOptionBox, all items will be set to False (unticked)

        :param title: the OptionBox to change
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)
        if box.kind == "ticks":
            # loop through each tick, set it to False
            ticks = self.widgetManager.get(WIDGET_NAMES.TickOptionBox, title, group=WidgetManager.VARS)
            for k in ticks:
                self.setOptionBox(title, k, False, callFunction=callFunction)
        else:
            self.setOptionBox(title, 0, callFunction=callFunction, override=True)

    def clearAllOptionBoxes(self, callFunction=False):
        """ Convenience function to clear all OptionBoxes in the GUI
        Will simply call clearOptionBox on each OptionBox/TickOptionBox

        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        """
        for k in self.widgetManager.group(WIDGET_NAMES.OptionBox):
            self.clearOptionBox(k, callFunction)

    def setOptionBoxDisabledChar(self, title, disabled="-"):
        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)
        box.disabled = disabled
        self._disableOptionBoxSeparators(box)

    def setOptionBox(self, title, index, value=True, callFunction=True, override=False):
        """ Main purpose is to select/deselect the item at the specified position
        But will also: delete an item if value is set to None or rename an item if value is set to a String

        :param title: the OptionBox to change
        :param index: the position or value of the item to select/delete
        :param value: determines what to do to the item: if set to None, will delete the item, else it sets the items state
        :param callFunction: whether to generate an event to notify that the widget has changed
        :param override: if set to True, allows a disabled item to be selected
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title)

        if box.kind == "ticks":
            gui.trace("Updating tickOptionBox")
            ticks = self.widgetManager.get(WIDGET_NAMES.TickOptionBox, title, group=WidgetManager.VARS)
            if index is None:
                gui.trace("Index empty - nothing to update")
                return
            elif index in ticks:
                gui.trace("Updating: %s", index)

                tick = ticks[index]
                try:
                    index_num = box.options.index(index)
                except:
                    self.warn("Unknown tick: %s in OptionBox: %s", index, title)
                    return

                with PauseCallFunction(callFunction, tick, useVar=False):
                    if value is None: # then we need to delete it
                        gui.trace("Deleting tick: %s from OptionBox %s", index, title)
                        box['menu'].delete(index_num)
                        del(box.options[index_num])
                        self.widgetManager.remove(WIDGET_NAMES.TickOptionBox, title, index, group=WidgetManager.VARS)
                    elif isinstance(value, bool):
                        gui.trace("Updating tick: %s from OptionBox: %s to: %s", index, title, value)
                        tick.set(value)
                    else:
                        gui.trace("Renaming tick: %s from OptionBox: %s to: %s", index, title, value)
                        ticks = self.widgetManager.get(WIDGET_NAMES.TickOptionBox, title, group=WidgetManager.VARS)
                        ticks[value] = ticks.pop(index)
                        box.options[index_num] = value
                        self.changeOptionBox(title, box.options)
                        for tick in ticks:
                            self.widgetManager.get(WIDGET_NAMES.TickOptionBox, title, group=WidgetManager.VARS)[tick].set(ticks[tick].get())
            else:
                if value is None:
                    self.warn("Unknown tick in deleteOptionBox: %s in OptionBox: %s" , index, title)
                else:
                    self.warn("Unknown tick in setOptionBox: %s in OptionBox: %s", index, title)
        else:
            gui.trace("Updating regular optionBox: %s at: %s to: %s", title, index, value)
            count = len(box.options)
            if count > 0:
                if index is None:
                    index = 0
                if not isinstance(index, int):
                    try:
                        index = box.options.index(index)
                    except:
                        if value is None:
                            self.warn("Unknown option in deleteOptionBox: %s in OptionBox: %s", index, title)
                        else:
                            self.warn("Unknown option in setOptionBox: %s in OptionBox: %s", index, title)
                        return

                gui.trace("--> index now: %s", index)

                if index < 0 or index > count - 1:
                    self.warn("Invalid option: %s. Should be between 0 and %s." , count-1, index)
                else:
                    if value is None: # then we can delete it...
                        gui.trace("Deleting option: %s from OptionBox: %s", index, title)
                        box['menu'].delete(index)
                        del(box.options[index])
                        self.setOptionBox(title, 0, callFunction=False, override=override)
                    elif isinstance(value, bool):
                        gui.trace("Updating: OptionBox: %s to: %s", title, index)
                        with PauseCallFunction(callFunction, box):
                            if not box['menu'].invoke(index):
                                if override:
                                    gui.trace("Setting OptionBox: %s to disabled option: %s", title, index)
                                    box["menu"].entryconfigure(index, state="normal")
                                    box['menu'].invoke(index)
                                    box["menu"].entryconfigure(index, state="disabled")
                                else:
                                    self.warn("Unable to set disabled option: %s in OptionBox %s. Try setting 'override=True'", index, title)
                            else:
                                gui.trace("Invoked item: %s", index)
                    else:
                        gui.trace("Renaming: %s from OptionBox: %s to: %s", index, title, value)
                        pos = box.options.index(self.widgetManager.get(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS).get())
                        box.options[index] = value
                        self.changeOptionBox(title, box.options, pos)

            else:
                self.widgetManager.get(WIDGET_NAMES.OptionBox, title, group=WidgetManager.VARS).set("")
                self.warn("No items to select from: %s", title)

#####################################
# FUNCTION for GoogleMaps
#####################################

    def map(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets maps all in one go """
        widgKind = WIDGET_NAMES.Map
        zoom = kwargs.pop("zoom", None)
        size = kwargs.pop("size", None)
        terrain = kwargs.pop("terrain", None)
        proxy = kwargs.pop("proxy", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            gMap = self.getLabel(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            gMap = self.addGoogleMap(title, *args, **kwargs)

        if value is not None: self.setGoogleMapLocation(title, value)
        if zoom is not None: self.setGoogleMapZoom(title, zoom)
        if size is not None: self.setGoogleMapSize(title, size)
        if terrain is not None: self.setGoogleMapTerrain(title, terrain)
        if proxy is not None: self.setGoogleMapProxy(title, proxy)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return gMap

    def addGoogleMap(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a GoogleMap widget at the specified position '''
        self._loadURL()
        self._loadTooltip()
        if urlencode is False:
            raise Exception("Unable to load GoogleMaps - urlencode library not available")
        self.widgetManager.verify(WIDGET_NAMES.Map, title)
        gMap = GoogleMap(self.getContainer(), self, useTtk = self.ttkFlag, font=self._getContainerProperty('labelFont'))
        self._positionWidget(gMap, row, column, colspan, rowspan)
        self.widgetManager.add(WIDGET_NAMES.Map, title, gMap)
        return gMap

    def setGoogleMapProxy(self, title, proxyString):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        gMap.setProxyString(proxyString)

    def setGoogleMapLocation(self, title, location):
        self.searchGoogleMap(title, location)

    def searchGoogleMap(self, title, location):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        gMap.changeLocation(location)

    def setGoogleMapTerrain(self, title, terrain):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        if terrain not in gMap.TERRAINS:
            raise Exception("Invalid terrain. Must be one of " + str(gMap.TERRAINS))
        gMap.changeTerrain(terrain)

    def setGoogleMapZoom(self, title, mod):
        self. zoomGoogleMap(title, mod)

    def zoomGoogleMap(self, title, mod):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        if mod in ["+", "-"]:
            gMap.zoom(mod)
        elif isinstance(mod, int) and 0 <= mod <= 22:
            gMap.setZoom(mod)

    def setGoogleMapSize(self, title, size):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        gMap.setSize(size)

    def setGoogleMapMarker(self, title, location, size=None, colour=None, label=None, replace=False):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        if len(location) == 0:
            gMap.removeMarkers()
        else:
            gMap.addMarker(location, size, colour, label, replace)

    def removeGoogleMapMarker(self, title, label):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        if len(label) == 0:
            gMap.removeMarkers()
        else:
            gMap.removeMarker(label)

    def getGoogleMapZoom(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Map, title).params["zoom"]

    def getGoogleMapTerrain(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Map, title).params["maptype"].title()

    def getGoogleMapLocation(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Map, title).params["center"]

    def getGoogleMapSize(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Map, title).params["size"]

    def saveGoogleMap(self, title, fileLocation):
        gMap = self.widgetManager.get(WIDGET_NAMES.Map, title)
        return gMap.saveTile(fileLocation)

#####################################
# FUNCTION for matplotlib
#####################################

    def plot(self, title, t=None, s=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets plots all in one go """
        widgKind = WIDGET_NAMES.Plot
        nav = kwargs.pop("nav", kwargs.pop("showNav", False))

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            keepLabels = kwargs.pop("keepLabels", False)
            self.updatePlot(title, t, s, keepLabels=keepLabels)
            plot = self.widgetManager.get(WIDGET_NAMES.Plot, title).axes
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if t is not None:
                if s is not None:
                    plot = self.addPlot(title, t, s, *args, showNav=nav, **kwargs)
                else:
                    gui.warn("Invalid parameters for plot: must provide t & s")
                    return None
            else:
                plot = self.addPlotFig(title, *args, showNav=nav, **kwargs)

        return plot

    def addPlot(self, title, t, s, row=None, column=0, colspan=0, rowspan=0, width=None, height=None, showNav=False):
        ''' adds a MatPlotLib, with t/s plotted '''
        canvas, fig = self._addPlotFig(title, row, column, colspan, rowspan, width, height, showNav)
        axes = fig.add_subplot(111)
        axes.plot(t,s)
        canvas.axes = axes
        return axes

    def addPlotFig(self, title, row=None, column=0, colspan=0, rowspan=0, width=None, height=None, showNav=False):
        canvas, fig = self._addPlotFig(title, row, column, colspan, rowspan, width, height, showNav)
        return fig

    def _addPlotFig(self, title, row=None, column=0, colspan=0, rowspan=0, width=None, height=None, showNav=False):
        self.widgetManager.verify(WIDGET_NAMES.Plot, title)
        self._loadMatplotlib()
        if PlotCanvas is False:
            raise Exception("Unable to load MatPlotLib - plots not available")
        else:
            fig = PlotFig(tight_layout=True)

            if width is not None and height is not None:
                fig.set_size_inches(width,height,forward=True)

            frame = frameBase(self.getContainer())

            canvas = PlotCanvas(fig, frame)
            canvas._tkcanvas.config(background="#c0c0c0", borderwidth=0, highlightthickness=0)
            canvas.fig = fig
            canvas.draw()
            if showNav:
                navBar = PlotNav(canvas, frame)
                navBar.pack(side=TOP, fill=X, expand=0)
            canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

#            self._positionWidget(canvas.get_tk_widget(), row, column, colspan, rowspan)
            self._positionWidget(frame, row, column, colspan, rowspan, sticky='news')
            self.widgetManager.add(WIDGET_NAMES.Plot, title, canvas)
            return canvas, fig

    def refreshPlot(self, title):
        canvas = self.widgetManager.get(WIDGET_NAMES.Plot, title)
        canvas.draw()

    def updatePlot(self, title, t, s, keepLabels=False):
        axes = self.widgetManager.get(WIDGET_NAMES.Plot, title).axes

        if keepLabels:
            xLab = axes.get_xlabel()
            yLab = axes.get_ylabel()
            pTitle = axes.get_title()
            handles, legends = axes.get_legend_handles_labels()

        axes.clear()
        axes.plot(t, s)

        if keepLabels:
            axes.set_xlabel(xLab)
            axes.set_ylabel(yLab)
            axes.set_title(pTitle)
            axes.legend(handles, legends)

        self.refreshPlot(title)
        return axes


#####################################
# FUNCTION to manage Properties Widgets
#####################################

    def properties(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets properties all in one go """
        widgKind = WIDGET_NAMES.Properties
        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
#            if value is not None:
# need to work out args...
#                self.setProperty(title, prop=value)
            props = self.getProperties(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            props = self.addProperties(title, value, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return props

    def addProperties(self, title, values=None, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        ''' adds a new properties widget, displaying the dictionary of booleans as tick boxes '''
        self.widgetManager.verify(WIDGET_NAMES.Properties, title)
        haveTitle = True
        if self._getContainerProperty('type') == WIDGET_NAMES.ToggleFrame:
            self.containerStack[-1]['sticky'] = "ew"
            haveTitle = False

        props = Properties(self.getContainer(), title, values, haveTitle,
                            font=self._getContainerProperty('labelFont'), background=self._getContainerBg())
        self._positionWidget(props, row, column, colspan, rowspan)
        self.widgetManager.add(WIDGET_NAMES.Properties, title, props)
        return props

    def getProperties(self, title):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        return props.getProperties()

    def getAllProperties(self):
        props = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Properties):
            props[k] = self.getProperties(k)
        return props

    def getProperty(self, title, prop):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        return props.getProperty(prop)

    def setProperty(self, title, prop, value=False, callFunction=True):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.addProperty(prop, value, callFunction=callFunction)

    def setProperties(self, title, props, callFunction=True):
        p = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        p.addProperties(props, callFunction=callFunction)

    def deleteProperty(self, title, prop):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.addProperty(prop, None, callFunction=False)

    def setPropertyText(self, title, prop, newText=None):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.renameProperty(prop, newText)

    def setPropertiesBoxBg(self, title, newCol):
        self.setPropertiesSelectColour(title, newCol)

    def setPropertiesSelectColour(self, title, newCol):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.config(selectcolor=newCol)

    def clearProperties(self, title, callFunction=True):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.clearProperties(callFunction)

    def clearAllProperties(self, callFunction=False):
        props = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Properties):
            self.clearProperties(k, callFunction)

    def resetProperties(self, title, callFunction=True):
        props = self.widgetManager.get(WIDGET_NAMES.Properties, title)
        props.resetProperties(callFunction)

    def resetAllProperties(self, callFunction=False):
        props = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Properties):
            self.resetProperties(k, callFunction)

#####################################
# FUNCTION to add spin boxes
#####################################

    def spin(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for spinBox() """
        return self.spinBox(title, value, *args, **kwargs)

    def spinbox(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for spinBox() """
        return self.spinBox(title, value, *args, **kwargs)

    def spinBox(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets spinBoxes all in one go """
        widgKind = WIDGET_NAMES.SpinBox

        endValue = kwargs.pop("endValue", None)
        selected = kwargs.pop("selected", None)
        item = kwargs.pop("item", None)
        label = kwargs.pop("label", False)

        # select=select, deselect=<RESET>, toggle=<NONE>, clear=??, rename=set, replace=update, delete=remov
        if value is None: mode = 'get'
        else: mode = 'select'
        mode = kwargs.pop("mode", mode)
        callFunction = kwargs.pop("callFunction", True)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if mode == "select":
                if value is not None: self.setSpinBoxPos(title, value, *args, **kwargs)
                else: gui.error("No item specified to select in spinbox: %s", title)
            elif mode == "toggle":
                gui.error("%s not available on spinbox: %s", mode, title)
            elif mode in["clear", "deselect"]:
                self.clearSpinBox(title)
            elif mode == "rename":
                gui.error("%s not implemented yet in spinbox: %s", mode, title)
            elif mode == "replace":
                if value is not None: self.changeSpinBox(title, vals=value)
                else: gui.error("No values specified to replace in spinbox: %s", title)
            elif mode == "delete":
                gui.error("%s not implemented yet in spinbox: %s", mode, title)
            elif mode == "get":
                pass
            else:
                gui.error("Invalid mode (%s) specified in spinbox: %s", mode, title)

            spinBox =  self.getSpinBox(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if endValue is not None:
                if label: spinBox = self.addLabelSpinBoxRange(title, value, endValue, *args, label=label, **kwargs)
                else: spinBox = self.addSpinBoxRange(title, value, endValue, *args, **kwargs)
            else:
                if label: spinBox = self.addLabelSpinBox(title, value, *args, label=label, **kwargs)
                else: spinBox = self.addSpinBox(title, value, *args, **kwargs)

        if selected is not None: self.setSpinBoxPos(title, selected)
        if item is not None: self.setSpinBox(title, item)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return spinBox

    def _buildSpinBox(self, frame, title, vals):
        self.widgetManager.verify(WIDGET_NAMES.SpinBox, title)
        if type(vals) not in [list, tuple]:
            raise Exception("Can't create SpinBox " + title + ". Invalid values: " + str(vals))

        spin = Spinbox(frame)
        spin.var = StringVar(self.topLevel)
        spin.config(textvariable=spin.var)
        spin.inContainer = False
        spin.isRange = False
        spin.config(font=self._getContainerProperty('inputFont'), highlightthickness=0)

# adds bg colour under spinners
#        if self.platform == self.MAC:
#              spin.config(highlightbackground=self._getContainerBg())

        spin.bind("<Tab>", self._focusNextWindow)
        spin.bind("<Shift-Tab>", self._focusLastWindow)

        # store the vals in DEFAULT_TEXT
        spin.DEFAULT_TEXT=""
        if vals is not None:
            spin.DEFAULT_TEXT='\n'.join(str(x) for x in vals)

        self._populateSpinBox(spin, vals)

        # prevent invalid entries
        if self.validateSpinBox is None:
            self.validateSpinBox = (
                self.containerStack[0]['container'].register(
                    self._validateSpinBox), '%P', '%W')

        spin.config(validate='all', validatecommand=self.validateSpinBox)

        self.widgetManager.add(WIDGET_NAMES.SpinBox, title, spin)
        return spin

    def _populateSpinBox(self, spin, vals, reverse=True):
        # make sure it's a list
        # reverse it, so the spin box functions properly
        if reverse:
            vals = list(vals)
            vals.reverse()
        vals = tuple(vals)
        spin.config(values=vals)

    def _addSpinBox(self, title, values, row=None, column=0, colspan=0, rowspan=0):
        spin = self._buildSpinBox(self.getContainer(), title, values)
        self._positionWidget(spin, row, column, colspan, rowspan)
        self.setSpinBoxPos(title, 0)
        return spin

    def addSpinBox(self, title, values, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        ''' adds a spinbox, with the specified values '''
        return self._addSpinBox(title, values, row, column, colspan, rowspan)

    def addLabelSpinBox(self, title, values, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        ''' adds a spinbox, with the specified values, and a label displaying the title '''
        frame = self._getLabelBox(title, **kwargs)
        spin = self._buildSpinBox(frame, title, values)
        self._packLabelBox(frame, spin)
        self._positionWidget(frame, row, column, colspan, rowspan)
        self.setSpinBoxPos(title, 0)
        return spin

    def addSpinBoxRange(self, title, fromVal, toVal, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        ''' adds a spinbox, with a range of whole numbers '''
        vals = list(range(fromVal, toVal + 1))
        spin = self._addSpinBox(title, vals, row, column, colspan, rowspan)
        spin.isRange = True
        return spin

    def addLabelSpinBoxRange(self, title, fromVal, toVal, row=None, column=0, colspan=0, rowspan=0, label=True, **kwargs):
        ''' adds a spinbox, with a range of whole numbers, and a label displaying the title '''
        vals = list(range(fromVal, toVal + 1))
        spin = self.addLabelSpinBox(title, vals, row, column, colspan, rowspan, label=label)
        spin.isRange = True
        return spin

    def getSpinBox(self, title):
        spin = self.widgetManager.get(WIDGET_NAMES.SpinBox, title)
        return spin.get()

    def getAllSpinBoxes(self):
        boxes = {}
        for k in self.widgetManager.group(WIDGET_NAMES.SpinBox):
            boxes[k] = self.getSpinBox(k)
        return boxes

    # validates that an item in the named spinbox starts with the user_input
    def _validateSpinBox(self, user_input, widget_name):
        spin = self.containerStack[0]['container'].nametowidget(widget_name)

        vals = spin.cget("values")  # .split()
        vals = self._getSpinBoxValsAsList(vals)
        for i in vals:
            if i.startswith(user_input):
                return True

        self.containerStack[0]['container'].bell()
        return False

    # expects a valid spin box widget, and a valid value
    def _setSpinBoxVal(self, spin, val, callFunction=True):
        # now call function
        with PauseCallFunction(callFunction, spin):
            spin.var.set(val)

    # is it going to be a hash or list??
    def _getSpinBoxValsAsList(self, vals):
        vals.replace("{", "")
        vals.replace("}", "")
#        if "{" in vals:
#            vals = vals[1:-1]
#            vals = vals.split("} {")
#        else:
        vals = vals.split()
        return vals

    def setSpinBox(self, title, value, callFunction=True):
        spin = self.widgetManager.get(WIDGET_NAMES.SpinBox, title)
        vals = spin.cget("values")  # .split()
        vals = self._getSpinBoxValsAsList(vals)
        val = str(value)
        if val not in vals:
            raise Exception( "Invalid value: " + val + ". Not in SpinBox: " +
                        title + "=" + str(vals))
        self._setSpinBoxVal(spin, val, callFunction)

    def clearSpinBox(self, title, callFunction=False):
        self.setSpinBoxPos(title, 0, callFunction=callFunction)

    def clearAllSpinBoxes(self, callFunction=False):
        for sb in self.widgetManager.group(WIDGET_NAMES.SpinBox):
            self.setSpinBoxPos(sb, 0, callFunction=callFunction)

    def setSpinBoxPos(self, title, pos, callFunction=True):
        spin = self.widgetManager.get(WIDGET_NAMES.SpinBox, title)
        vals = spin.cget("values")  # .split()
        vals = self._getSpinBoxValsAsList(vals)
        pos = int(pos)
        if pos < 0 or pos >= len(vals):
            raise Exception( "Invalid position: " + str(pos) + ". No position in SpinBox: " +
                        title + "=" + str(vals))
        pos = len(vals) - 1 - pos
        val = vals[pos]
        self._setSpinBoxVal(spin, val, callFunction)

    def changeSpinBox(self, title, vals, reverse=True):
        spin = self.widgetManager.get(WIDGET_NAMES.SpinBox, title)
        if spin.isRange:
            self.warn("Can't convert %s RangeSpinBox to SpinBox", title)
        else:
            self._populateSpinBox(spin, vals, reverse)
            self.setSpinBoxPos(title, 0)

#####################################
# FUNCTION to add images
#####################################

    def image(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets images all in one go """

        widgKind = WIDGET_NAMES.Image
        kind = kwargs.pop("kind", "standard").lower().strip()
        speed = kwargs.pop("speed", None)
        drop = kwargs.pop("drop", None)
        over = kwargs.pop("over", None)
        submit = kwargs.pop("submit", None)
        _map = kwargs.pop("map", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # already exists
            if value is not None:
                if kind == "data":
                    self.setImageData(title, value, **kwargs)
                elif kind == "icon":
                    gui.warn("Changing image icons not yet supported: %s.", title)
                else:
                    self.setImage(title, value)
            image =  self.getImage(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if kind == "icon":
                image = self.addIcon(title, value, *args, **kwargs)
            elif kind == "data":
                image = self.addImageData(title, value, *args, **kwargs)
            else:
                image = self.addImage(title, value, *args, **kwargs)


        if speed is not None: self.setAnimationSpeed(title, speed)
        if over is not None: self.setImageMouseOver(title, over)
        if submit is not None:
            if _map is not None: self.setImageMap(title, submit, _map)
            else: self.setImageSubmitFunction(title, submit)
        elif submit is None and _map is not None:
            gui.warn("Must specify a submit function when setting an image map: %s", title)
        if drop is not None: self.setImageDropTarget(title, drop)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return image

    # looks up label containing image
    def _animateImage(self, title, firstTime=False):
        if not self.alive: return
        try:
            lab = self.widgetManager.get(WIDGET_NAMES.Image, title)
        except ItemLookupError:
            # image destroyed...
            try: self.widgetManager.remove(WIDGET_NAMES.AnimationID, title)
            except: pass
            return
        if not lab.image.animating:
            self.widgetManager.remove(WIDGET_NAMES.AnimationID, title)
            return
        if firstTime and lab.image.alreadyAnimated:
            return

        lab.image.alreadyAnimated = True
        try:
            if lab.image.cached:
                pic = lab.image.pics[lab.image.anim_pos]
            else:
                pic = PhotoImage(file=lab.image.path,
                                 format="gif - {0}".format(lab.image.anim_pos))
                lab.image.pics.append(pic)
            lab.image.anim_pos += 1
            lab.config(image=pic)
            anim_id = self.topLevel.after(int(lab.image.anim_speed), self._animateImage, title)
            self.widgetManager.update(WIDGET_NAMES.AnimationID, title, anim_id)
        except IndexError:
            # will be thrown when we reach end of anim images
            lab.image.anim_pos = 0
            lab.image.cached = True
            self._animateImage(title)
        except TclError:
            # will be thrown when all images cached
            lab.image.anim_pos = 0
            lab.image.cached = True
            self._animateImage(title)

    def _preloadAnimatedImage(self, img):
        if not self.alive: return
        if img.cached:
            return
        try:
            pic = PhotoImage(file=img.path,
                             format="gif - {0}".format(img.anim_pos))
            img.pics.append(pic)
            img.anim_pos += 1
            self.preloadAnimatedImageId = self.topLevel.after(
                0, self._preloadAnimatedImage, img)
        # when all frames have been processed
        except TclError as e:
            # expected - when all images cached
            img.anim_pos = 0
            img.cached = True

    def _configAnimatedImage(self, img):
        img.alreadyAnimated = False
        img.isAnimated = True
        img.pics = []
        img.cached = False
        img.anim_pos = 0
        img.anim_speed = 150
        img.animating = True

    # simple way to check if image is animated
    def _checkIsAnimated(self, name):
        if imghdr.what(name) == "gif":
            try:
                PhotoImage(file=name, format="gif - 1")
                return True
            except:
                pass
        return False

    def setAnimationSpeed(self, name, speed):
        img = self.widgetManager.get(WIDGET_NAMES.Image, name).image
        if speed < 1:
            speed = 1
            self.warn("Setting %s speed to 1. Minimum animation speed is 1.", name)
        img.anim_speed = int(speed)

    def stopAnimation(self, name):
        img = self.widgetManager.get(WIDGET_NAMES.Image, name).image
        img.animating = False

    def startAnimation(self, name):
        img = self.widgetManager.get(WIDGET_NAMES.Image, name).image
        if not img.animating:
            img.animating = True
            anim_id = self.topLevel.after(img.anim_speed, self._animateImage, name)
            self.widgetManager.update(WIDGET_NAMES.AnimationID, name, anim_id)

    # function to set an alternative image, when a mouse goes over
    def setImageMouseOver(self, title, overImg):
        lab = self.widgetManager.get(WIDGET_NAMES.Image, title)

        # first check over image & cache it
        fullPath = self.getImagePath(overImg)
        self.topLevel.after(0, self._getImage, fullPath)

        leaveImg = lab.image.path
        lab.bind("<Leave>", lambda e: self.setImage(title, leaveImg, True))
        lab.bind("<Enter>", lambda e: self.setImage(title, fullPath, True))
        lab.hasMouseOver = True

    # function to set an image location
    def setImageLocation(self, location):
        if os.path.isdir(location):
            self.userImages = location
        else:
            raise Exception("Invalid image location: " + location)

    # get the full path of an image (including image folder)
    def getImagePath(self, imagePath):
        if imagePath is None:
            return None

        if self.userImages is not None:
            imagePath = os.path.join(self.userImages, imagePath)

        absPath = os.path.abspath(imagePath)
        return absPath

    # function to see if an image has changed
    def hasImageChanged(self, originalImage, newImage):
        newAbsImage = self.getImagePath(newImage)

        if originalImage is None:
            return True

        # filename has changed
        if originalImage.path != newAbsImage:
            return True

        # modification time has changed
        if originalImage.modTime != os.path.getmtime(newAbsImage):
            return True

        # no changes
        return False

    # function to remove image objects form cache
    def clearImageCache(self):
        self.widgetManager.clear(WIDGET_NAMES.ImageCache)

    # internal function to build an image function from a string
    def _getImageData(self, imageData, fmt="gif"):
        if fmt=="png":
            self._importPngimagetk()
            if PngImageTk is False:
                raise Exception("TKINTERPNG library not found, PNG files not supported: imageData")
            if sys.version_info >= (2, 7):
                self.warn("Image processing for .PNGs is slow. .GIF is the recommended format")
#                png = PngImageTk(imagePath)
#                png.convert()
#                photo = png.image
            else:
                raise Exception("PNG images only supported in python 3: imageData")

        elif fmt == "gif":
            imgObj = PhotoImage(data=imageData)

        else:
            # expect we already have a PhotoImage object, for example created by PIL
            imgObj = imageData


        imgObj.path = None
        imgObj.modTime = datetime.datetime.now()
        imgObj.isAnimated = False
        imgObj.animating = False
        return imgObj

    # internal function to check/build image object
    def _getImage(self, imagePath, checkCache=True, addToCache=True):
        if imagePath is None:
            return None

        # get the full image path
        imagePath = self.getImagePath(imagePath)

        # if we're caching, and we have a non-None entry in the cache - get it...
        photo = None
        if checkCache and imagePath in self.widgetManager.group(WIDGET_NAMES.ImageCache) and self.widgetManager.get(WIDGET_NAMES.ImageCache, imagePath) is not None:
            photo = self.widgetManager.get(WIDGET_NAMES.ImageCache, imagePath)

        # if the image hasn't changed, use the cache
        if not self.hasImageChanged(photo, imagePath):
            pass
        # else load a new one
        elif os.path.isfile(imagePath):
            if os.access(imagePath, os.R_OK):
                imgType = imghdr.what(imagePath)
                if imgType is None:
                    raise Exception( "Invalid file: " + imagePath + " is not a valid image")
                elif not imagePath.lower().endswith(imgType) and not (
                        imgType == "jpeg" and imagePath.lower().endswith("jpg")):
                        # the image has been saved with the wrong extension
                    raise Exception(
                        "Invalid image extension: " +
                        imagePath +
                        " should be a ." +
                        imgType)
                elif imagePath.lower().endswith('.gif'):
                    photo = PhotoImage(file=imagePath)
                elif imagePath.lower().endswith('.ppm') or imagePath.lower().endswith('.pgm'):
                    photo = PhotoImage(file=imagePath)
                elif imagePath.lower().endswith('jpg') or imagePath.lower().endswith('jpeg'):
                    self.warn("Image processing for .JPGs is slow. .GIF is the recommended format")
                    photo = self.convertJpgToBmp(imagePath)
                elif imagePath.lower().endswith('.png'):
                    # known issue here, some PNGs lack IDAT chunks
                    # also, PNGs seem broken on python<3, maybe around the map
                    # function used to generate pixel maps
                    self._importPngimagetk()
                    if PngImageTk is False:
                        raise Exception(
                            "TKINTERPNG library not found, PNG files not supported: " + imagePath)
                    if sys.version_info >= (2, 7):
                        self.warn("Image processing for .PNGs is slow. .GIF is the recommended format")
                        png = PngImageTk(imagePath)
                        png.convert()
                        photo = png.image
                    else:
                        raise Exception("PNG images only supported in python 3: " + imagePath)
                else:
                    raise Exception("Invalid image type: " + imagePath)
            else:
                raise Exception("Can't read image: " + imagePath)
        else:
            raise Exception("Image " + imagePath + " does not exist")

        # store the full path to this image
        photo.path = imagePath
        # store the modification time
        photo.modTime = os.path.getmtime(imagePath)

        # sort out if it's an animated image
        if self._checkIsAnimated(imagePath):
            self._configAnimatedImage(photo)
            self._preloadAnimatedImage(photo)
        else:
            photo.isAnimated = False
            photo.animating = False
            if addToCache:
                self.widgetManager.update(WIDGET_NAMES.ImageCache, imagePath, photo)

        return photo

    def getImageDimensions(self, name):
        img = self.widgetManager.get(WIDGET_NAMES.Image, name).image
        return img.width(), img.height()

    # force replace the current image, with a new one
    def reloadImage(self, name, imageFile):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        image = self._getImage(imageFile, False)
        self._populateImage(name, image)

    def reloadImageData(self, name, imageData, fmt="gif"):
        self.setImageData(name, imageData, fmt)

    def setImageData(self, name, imageData, fmt="gif"):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        image = self._getImageData(imageData, fmt=fmt)
        self._populateImage(name, image)

    # replace the current image, with a new one
    def getImage(self, name):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        return label.image.path

    def setImage(self, name, imageFile, internal=False):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        imageFile = self.getImagePath(imageFile)

        # only set the image if it's different
        if label.image is not None and label.image.path == imageFile:
            self.warn("Not updating %s, %s hasn't changed." , name, imageFile)
            return
        elif imageFile is None:
            return
        else:
            image = self._getImage(imageFile)
            self._populateImage(name, image, internal)

    # internal function to update the image in a label
    def _populateImage(self, name, image, internal=False):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)

        if label.image is not None: label.image.animating = False
        label.config(image=image)
        label.config(anchor=CENTER, font=self._getContainerProperty('labelFont'))
        if not self.ttkFlag:
            label.config(background=self._getContainerBg())
        label.image = image  # keep a reference!

        if image.isAnimated:
            anim_id = self.topLevel.after(
                image.anim_speed + 100,
                self._animateImage,
                name,
                True)
            self.widgetManager.update(WIDGET_NAMES.AnimationID, name, anim_id)

        if not internal and label.hasMouseOver:
            leaveImg = label.image.path
            label.bind("<Leave>", lambda e: self.setImage(name, leaveImg, True))

        # removed - keep the label the same size, and crop images
        #h = image.height()
        #w = image.width()
        #label.config(height=h, width=w)
        self.topLevel.update_idletasks()

    # function to configure an image map
    def setImageMap(self, name, func, coords):
        self._setWidgetMap(name, WIDGET_NAMES.Image, func, coords)

    def _setWidgetMap(self, name, _type, func, coords):
        widget = self.widgetManager.get(_type, name)
        rectangles = []
        if len(coords) > 0:
            for k, v in coords.items():
                rect = AjRectangle(k, AjPoint(v[0], v[1]), v[2]-v[0], v[3]-v[1])
                rectangles.append(rect)

        widget.MAP_COORDS = rectangles
        widget.MAP_FUNC = func
        widget.bind("<Button-1>", lambda e: self._widgetMap(_type, name, e), add="+")

    # function called when an image map is clicked
    def _widgetMap(self, _type, name, event):
        widget = self.widgetManager.get(_type, name)
        for rect in widget.MAP_COORDS:
            if rect.contains(AjPoint(event.x, event.y)):
                widget.MAP_FUNC(rect.name)
                return

        widget.MAP_FUNC("UNKNOWN: " + str(event.x) + ", " + str(event.y))

    def addImage(self, name, imageFile, row=None, column=0, colspan=0, rowspan=0, compound=None):
        ''' Adds an image at the specified position '''
        self.widgetManager.verify(WIDGET_NAMES.Image, name)
        imgObj = self._getImage(imageFile)
        self._addImageObj(name, imgObj, row, column, colspan, rowspan, compound=compound)
        self.widgetManager.get(WIDGET_NAMES.Image, name).hasMouseOver = False
        return imgObj

    def addIcon(self, name, iconName, row=None, column=0, colspan=0, rowspan=0, compound=None):
        ''' adds one of the built-in  icons at the specified position '''
        icon = os.path.join(self.icon_path, iconName.lower()+".png")
        with PauseLogger():
            return self.addImage(name, icon, row, column, colspan, rowspan, compound=compound)

    def addImageData(self, name, imageData, row=None, column=0, colspan=0, rowspan=0, fmt="gif", compound=None):
        ''' load image from base-64 encoded GIF
            use base64 module to convert binary data to base64 '''
        self.widgetManager.verify(WIDGET_NAMES.Image, name)
        imgObj = self._getImageData(imageData, fmt)
        self._addImageObj(name, imgObj, row, column, colspan, rowspan, compound=compound)
        self.widgetManager.get(WIDGET_NAMES.Image, name).hasMouseOver = False
        return imgObj

    def _addImageObj(self, name, img, row=None, column=0, colspan=0, rowspan=0, compound=None):
        if not self.ttkFlag:
            label = Label(self.getContainer())
            label.config(background=self._getContainerBg())
        else:
            label = ttk.Label(self.getContainer())

        label.config(anchor=CENTER, font=self._getContainerProperty('labelFont'),image=img)
        label.image = img  # keep a reference!

        if compound is not None:
            label.config(text=name, compound=compound)

        if img is not None and compound is None and not self.ttkFlag:
            h = img.height()
            w = img.width()
            label.config(height=h, width=w)

        self.widgetManager.add(WIDGET_NAMES.Image, name, label)
        self._positionWidget(label, row, column, colspan, rowspan)
        if img is not None and img.isAnimated:
            anim_id = self.topLevel.after(
                img.anim_speed, self._animateImage, name, True)
            self.widgetManager.update(WIDGET_NAMES.AnimationID, name, anim_id)

    def setImageSize(self, name, width, height):
        img = self.widgetManager.get(WIDGET_NAMES.Image, name)
        img.config(height=height, width=width)

#      def rotateImage(self, name, image):
#            img = self.widgetManager.get(WIDGET_NAMES.Image, name)

    # if +ve then grow, else shrink...
    def zoomImage(self, name, x, y=''):
        if x <= 0:
            self.shrinkImage(name, x * -1, y * -1)
        else:
            self.growImage(name, x, y)

    # get every nth pixel (must be an integer)
    # 0 will return an empty image, 1 will return the image, 2 will be 1/2 the
    # size ...
    def shrinkImage(self, name, x, y=''):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        image = label.image.subsample(x, y)

        label.config(image=image)
        label.config(anchor=CENTER, font=self._getContainerProperty('labelFont'))

        if not self.ttkFlag:
            label.config(background=self._getContainerBg())
            label.config(width=image.width(), height=image.height())
        label.modImage = image  # keep a reference!

    # get every nth pixel (must be an integer)
    # 0 won't work, 1 will return the original size
    def growImage(self, name, x, y=''):
        label = self.widgetManager.get(WIDGET_NAMES.Image, name)
        image = label.image.zoom(x, y)

        label.config(image=image)
        label.config(anchor=CENTER, font=self._getContainerProperty('labelFont'))

        if not self.ttkFlag:
            label.config(background=self._getContainerBg())
            label.config(width=image.width(), height=image.height())
        label.modImage = image  # keep a reference!

    def convertJpgToBmp(self, image):
        self._loadNanojpeg()
        if nanojpeg is False:
            raise Exception(
                "nanojpeg library not found, unable to display jpeg files: " + image)
        elif sys.version_info < (2, 7):
            raise Exception(
                "JPG images only supported in python 2.7+: " + image)
        else:
            # read the image into an array of bytes
            with open(image, 'rb') as inFile:
                buf = array.array(str('B'), inFile.read())

            # init the translator, and decode the array of bytes
            nanojpeg.njInit()
            nanojpeg.njDecode(buf, len(buf))

            # determine a file name & type
            if nanojpeg.njIsColor():
#                fileName = image.split('.jpg', 1)[0] + '.ppm'
                param = 6
            else:
#                fileName = image.split('.jpg', 1)[0] + '.pgm'
#                fileName = "test3.pgm"
                param = 5

            # create a string, starting with the header
            val = "P%d\n%d %d\n255\n" % (
                param, nanojpeg.njGetWidth(), nanojpeg.njGetHeight())
            # append the bytes, converted to chars
            val = str(val) + str('').join(map(chr, nanojpeg.njGetImage()))

            # release any stuff
            nanojpeg.njDone()

            photo = PhotoImage(data=val)
            return photo

            # write the chars to a new file, if python3 we need to encode them first
#            with open(fileName, "wb") as outFile:
#                  if sys.version_info[0] == 2: outFile.write(val)
#                  else: outFile.write(val.encode('ISO-8859-1'))
#
#            return fileName

    # function to set a background image
    # make sure this is done before everything else, otherwise it will cover
    # other widgets
    def setBgImage(self, image):
        image = self._getImage(image, False, False)  # make sure it's not using the cache
        # self.containerStack[0]['container'].config(image=image) # window as a
        # label doesn't work...
        self.bgLabel.config(image=image)
        self.containerStack[0]['container'].image = image  # keep a reference!

    def removeBgImage(self):
        self.bgLabel.config(image="")
        # self.containerStack[0]['container'].config(image=None) # window as a
        # label doesn't work...
        # remove the reference - shouldn't be cached
        self.containerStack[0]['container'].image = None

    def resizeBgImage(self):
        if self.containerStack[0]['container'].image is None:
            return
        else:
            pass

#####################################
# FUNCTION to play sounds
#####################################

    # function to set a sound location
    def setSoundLocation(self, location):
        if os.path.isdir(location):
            self.userSounds = location
        else:
            raise Exception("Invalid sound location: " + location)

    # internal function to manage sound availability
    def _soundWrap(self, sound, isFile=False, repeat=False, wait=False):
        self._loadWinsound()
        if self.platform == self.WINDOWS and winsound is not False:
            sound = self._translateSound(sound)
            if self.userSounds is not None and sound is not None:
                sound = os.path.join(self.userSounds, sound)
            if isFile:
                if os.path.isfile(sound) is False:
                    raise Exception("Can't find sound: " + sound)
                if not sound.lower().endswith('.wav'):
                    raise Exception("Invalid sound format: " + sound)
                kind = winsound.SND_FILENAME
                if not wait:
                    kind = kind | winsound.SND_ASYNC
            else:
                if sound is None:
                    kind = winsound.SND_FILENAME
                else:
                    kind = winsound.SND_ALIAS
                    if not wait:
                        kind = kind | winsound.SND_ASYNC

            if repeat:
                kind = kind | winsound.SND_LOOP

            winsound.PlaySound(sound, kind)
        else:
            # sound not available at this time
            raise Exception(
                "Sound not supported on this platform: " +
                platform())

    def playSound(self, sound, wait=False):
        self._soundWrap(sound, True, False, wait)

    def stopSound(self):
        self._soundWrap(None)

    def loopSound(self, sound):
        self._soundWrap(sound, True, True)

    def soundError(self):
        self._soundWrap("SystemHand")

    def soundWarning(self):
        self._soundWrap("SystemAsterisk")

    def bell(self):
        self.containerStack[0]['container'].bell()

    def playNote(self, note, duration=200):
        self._loadWinsound()
        if self.platform == self.WINDOWS and winsound is not False:
            try:
                if isinstance(note, UNIVERSAL_STRING):
                    freq = self.NOTES[note.lower()]
                else:
                    freq = note
            except KeyError:
                raise Exception("Error: cannot play note - " + note)
            try:
                if isinstance(duration, UNIVERSAL_STRING):
                    length = self.DURATIONS[duration.upper()]
                else:
                    length = duration
            except KeyError:
                raise Exception("Error: cannot play duration - " + duration)

            try:
                winsound.Beep(freq, length)
            except RuntimeError:
                raise Exception(
                    "Sound not available on this platform: " +
                    platform())
        else:
            # sound not available at this time
            raise Exception(
                "Sound not supported on this platform: " +
                platform())

#####################################
# FUNCTION for radio buttons
#####################################

    def radio(self, title, name=None, *args, **kwargs):
        """ simpleGUI - shortner for radioButton() """
        return self.radioButton(title, name, *args, **kwargs)

    def radioButton(self, title, name=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets radioButtons all in one go """
        widgKind = WIDGET_NAMES.RadioButton
        selected = kwargs.pop("selected", False)
        callFunction = kwargs.pop("callFunction", True)
        change = kwargs.pop("change", None)
        kind = kwargs.pop('kind', 'standard')

        # need slightly different approach, as use two params
        if name is None: return self.getRadioButton(title) # no name = get
        else:
            ident = title + "-" + name
            try: self.widgetManager.verify(widgKind, ident)
            except:
                self.setRadioButton(title, name, callFunction=callFunction)
                rb = self.getRadioButton(title)
                selected = False
            else:
                kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
                rb = self._radioButtonMaker(title, name, *args, **kwargs)

            if selected: self.setRadioButton(title, name)
            if change is not None: self.setRadioButtonChangeFunction(title, change)
            if kind == "square":
                if self.platform == self.MAC:
                    gui.warn("Square radiobuttons not available on Mac, for radiobutton %s", title)
                elif not self.ttkFlag:
                    rb.config(indicatoron=0)
                else:
                    gui.warn("Square radiobuttons not available in ttk, for radiobutton %s", title)

            if len(kwargs) > 0:
                self._configWidget(ident, widgKind, **kwargs)

            return rb

    def _radioButtonMaker(self, title, name, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        return self.addRadioButton(title, name, row, column, colspan, rowspan)

    def addRadioButton(self, title, name, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a radio button, to thr group 'title' with the text 'name' '''
        ident = title + "-" + name
        self.widgetManager.verify(WIDGET_NAMES.RadioButton, ident)

        var = None
        newRb = False
        # title - is the grouper
        # so, if we already have an entry in n_rbVars - get it
        if (title in self.widgetManager.group(WIDGET_NAMES.RadioButton, group=WidgetManager.VARS)):
            var = self.widgetManager.get(WIDGET_NAMES.RadioButton, title, group=WidgetManager.VARS)
        else:
            # if this is a new grouper - set it all up
            var = StringVar(self.topLevel)
            self.widgetManager.add(WIDGET_NAMES.RadioButton, title, var, group=WidgetManager.VARS)
            newRb = True

        # finally, create the actual RadioButton
        if not self.ttkFlag:
            rb = Radiobutton(self.getContainer(), text=name, variable=var, value=name)
            rb.config(anchor=W, background=self._getContainerBg(), indicatoron=1,
                activebackground=self._getContainerBg(), font=self._getContainerProperty('labelFont')
            )
        else:
            rb = ttk.Radiobutton(self.getContainer(), text=name, variable=var, value=name)

        rb.bind("<Button-1>", self._grabFocus)
        rb.DEFAULT_TEXT = name

        self.widgetManager.add(WIDGET_NAMES.RadioButton, ident, rb)
        #rb.bind("<Tab>", self._focusNextWindow)
        #rb.bind("<Shift-Tab>", self._focusLastWindow)

        # and select it, if it's the first item in the list
        if newRb:
            rb.select() if not self.ttkFlag else rb.invoke()
            var.startVal = name # so we can reset it...
        self._positionWidget(rb, row, column, colspan, rowspan, EW)
        return rb

    def getRadioButton(self, title):
        var = self.widgetManager.get(WIDGET_NAMES.RadioButton, title, group=WidgetManager.VARS)
        return var.get()

    def getAllRadioButtons(self):
        rbs = {}
        for k in self.widgetManager.group(WIDGET_NAMES.RadioButton, group=WidgetManager.VARS):
            rbs[k] = self.getRadioButton(k)
        return rbs

    def setRadioButton(self, title, value, callFunction=True):
        ident = title + "-" + value
        self.widgetManager.get(WIDGET_NAMES.RadioButton, ident)

        # now call function
        var = self.widgetManager.get(WIDGET_NAMES.RadioButton, title, group=WidgetManager.VARS)
        with PauseCallFunction(callFunction, var, False):
            var.set(value)

    def clearAllRadioButtons(self, callFunction=False):
        for rb in self.widgetManager.group(WIDGET_NAMES.RadioButton, group=WidgetManager.VARS):
            self.setRadioButton(rb, self.widgetManager.get(WIDGET_NAMES.RadioButton, rb, group=WidgetManager.VARS).startVal, callFunction=callFunction)

    def setRadioTick(self, title, tick=True):
        self.warn("Deprecated function (%s) used for %s -> %s use %s instead", 'setRadioTick', 'radioButton', title, 'setRadioSquare')
        self.setRadioSquare(title, square=tick)

    def setRadioSquare(self, title, square=True):
        if self.platform == self.MAC:
            gui.warn("Square radiobuttons not available on Mac, for radiobutton %s", title)
        elif not self.ttkFlag:
            for k, v in self.widgetManager.group(WIDGET_NAMES.RadioButton).items():
                if k.startswith(title+"-"):
                    if square:
                        v.config(indicatoron=1)
                    else:
                        v.config(indicatoron=0)
        else:
            gui.warn("Square radiobuttons not available in ttk mode, for radiobutton %s", title)

#####################################
# FUNCTION for list box
#####################################

    def listbox(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for listBox() """
        return self.listBox(title, value, *args, **kwargs)

    def listBox(self, title, value=None, *args, **kwargs):
        """ simpleGUI -- adds, sets & gets listBoxes all in one go """
        widgKind = WIDGET_NAMES.ListBox

        rows = kwargs.pop("rows", None)
        multi = kwargs.pop("multi", False)
        group = kwargs.pop("group", False)
        selected = kwargs.pop("selected", None)
        first = kwargs.pop("first", False)
        callFunction = kwargs.pop("callFunction", True)

        # select=select, deselect=??, toggle=??, clear=??, rename=set, replace=update, delete=remove
        if value is None: mode = 'get'
        else: mode = 'select'
        mode = kwargs.pop("mode", mode)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if mode == "select":
                if value is not None:
                    if isinstance(value, int):
                        self.selectListItemAtPos(title, value, *args, **kwargs)
                    else:
                        self.selectListItem(title, value, *args, **kwargs)
                else: gui.error("No item specified to select in listbox: %s", title)
            elif mode == "deselect":
                if value is not None:
                    if isinstance(value, int):
                        self.deselectListItemAtPos(title, value, *args, **kwargs)
                    else:
                        self.deselectListItem(title, value, *args, **kwargs)
                else: gui.error("No item specified to deselect in listbox: %s", title)
            elif mode == "toggle":
                gui.error("%s not implemented yet in listbox: %s", mode, title)
            elif mode == "clear":
                self.deselectAllListItems(title)
            elif mode == "rename":
                gui.error("%s not implemented yet in listbox: %s", mode, title)
            elif mode == "replace":
                if value is not None: self.updateListBox(title, items=value, callFunction=callFunction)
                else: gui.error("No values specified to replace in listbox: %s", title)
            elif mode == "delete":
                if value is not None:
                    if isinstance(value, int):
                        self.removeListItemAtPos(title, value)
                    else:
                        self.removeListItem(title, value)
                else: gui.error("No value specified to delete in listbox: %s", title)
            elif mode == "add":
                if value is not None:
                    select = True if selected is None else selected
                    if type(value) in (list, tuple):
                        self.addListItems(title, items=value, select=select)
                    else:
                        self.addListItem(title, item=value, select=select)
                else: gui.error("No value specified to add in listbox: %s", title)
            elif mode == "get":
                pass
            else:
                gui.error("Invalid mode (%s) specified in listbox: %s", mode, title)

            listBox = self.getListBox(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            listBox = self._listBoxMaker(title, value, *args, **kwargs)

        if rows is not None: self.setListBoxRows(title, rows)
        if multi: self.setListBoxMulti(title)
        if group: self.setListBoxGroup(title)
        if selected is not None: self.selectListItemAtPos(title, selected, callFunction=False)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return listBox

    def _listBoxMaker(self, name, values=None, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        """ internal wrapper to hide kwargs from original add functions """
        return self.addListBox(name, values, row, column, colspan, rowspan)

    def addListBox(self, name, values=None, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a list box, with the the specified list of values '''
        self.widgetManager.verify(WIDGET_NAMES.ListBox, name)
        container = self.makeListBoxContainer()(self.getContainer())
        vscrollbar = AutoScrollbar(container)
        hscrollbar = AutoScrollbar(container, orient=HORIZONTAL)

        container.lb = Listbox(container,
            yscrollcommand=vscrollbar.set,
            xscrollcommand=hscrollbar.set)

        vscrollbar.grid(row=0, column=1, sticky=N + S)
        hscrollbar.grid(row=1, column=0, sticky=E + W)

        container.lb.grid(row=0, column=0, sticky=N + S + E + W)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        vscrollbar.config(command=container.lb.yview)
        hscrollbar.config(command=container.lb.xview)

        container.lb.config(font=self._getContainerProperty('inputFont'))
        self.widgetManager.add(WIDGET_NAMES.ListBox, name, container.lb)

        container.lb.DEFAULT_TEXT=""
        if values is not None:
            container.lb.DEFAULT_TEXT='\n'.join(str(x) for x in values)
            for name in values:
                container.lb.insert(END, name)

        self._positionWidget(container, row, column, colspan, rowspan)
        return container.lb

    # enable multiple listboxes to be selected at the same time
    def setListBoxGroup(self, name, group=True):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, name)
        group = not group
        lb.config(exportselection=group)

    # set how many rows to display
    def setListBoxRows(self, name, rows):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, name)
        lb.config(height=rows)

    # make the list single/multi select
    # default is single
    def setListBoxMulti(self, title, multi=True):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        if multi:
            lb.config(selectmode=EXTENDED)
        else:
            lb.config(selectmode=BROWSE)

    # select the specified item in the list
    def selectListItem(self, title, item, callFunction=True):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        positions = self._getListPositions(title, item)
        if len(positions) > 1 and lb.cget("selectmode") == EXTENDED:
            allOk = True
            for pos in positions:
                if not self.selectListItemAtPos(title, pos, callFunction):
                    allOk = False
            return allOk
        elif len(positions) > 1:
            gui.warn("Unable to select multiple items for list: %s. Selecting first item: %s", title, item[0])
            return self.selectListItemAtPos(title, positions[0], callFunction)
        elif len(positions) == 1:
            return self.selectListItemAtPos(title, positions[0], callFunction)
        else:
            gui.warn("Invalid list item(s): %s for list: %s", item, title)
            return False

    def deselectListItemAtPos(self, title, pos, callFunction=False):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        if lb.size() == 0:
            gui.warn("No items in list: %s, unable to deselect item at pos: %s", title, pos)
            return False
        if pos < 0 or pos > lb.size() - 1:
            gui.warn("Invalid list position: %s for list: %s (max: %s)", pos, title, lb.size()-1)
            return False

        lb.selection_clear(pos)
        if callFunction and hasattr(lb, 'cmd'):
            lb.cmd()
        self.topLevel.update_idletasks()
        return True

    def selectListItemAtPos(self, title, pos, callFunction=False):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        if lb.size() == 0:
            gui.warn("No items in list: %s, unable to select item at pos: %s", title, pos)
            return False
        if pos < 0 or pos > lb.size() - 1:
            gui.warn("Invalid list position: %s for list: %s (max: %s)", pos, title, lb.size()-1)
            return False

        # clear previous selection if we're not multi
        if lb.cget("selectmode") != EXTENDED:
            lb.selection_clear(0, END)

        # show & select this item
        lb.see(pos)
        lb.activate(pos)
        lb.selection_set(pos)
        # now call function
        if callFunction and hasattr(lb, 'cmd'):
            lb.cmd()
        self.topLevel.update_idletasks()
        return True

    # replace the list items in the list box
    def updateListBox(self, title, items, select=False, callFunction=True):
        self.clearListBox(title, callFunction=callFunction)
        self.addListItems(title, items, select=select)

    def addListItems(self, title, items, select=True):
        ''' adds the list of items to the specified list box '''
        for i in items:
            self.addListItem(title, i, select=select)

    def addListItem(self, title, item, pos=None, select=True):
        ''' add the item to the end of the specified list box '''
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        # add it at the end
        if pos is None: pos = END
        lb.insert(pos, item)

        # show & select the newly added item
        if select:
            # clear any selection
            items = lb.curselection()
            if len(items) > 0:
                lb.selection_clear(items)

            self.selectListItemAtPos(title, lb.size() - 1)

    def deselectAllListItems(self, title, callFunction=False):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        lb.selection_clear(0, END)

        if callFunction and hasattr(lb, 'cmd'):
            lb.cmd()

    # returns a list containing 0 or more elements
    # all that are in the selected range
    def getListBox(self, title):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        items = lb.curselection()
        values = []
        for loop in range(len(items)):
            values.append(lb.get(items[loop]))
        return values

    def getAllListBoxes(self):
        boxes = {}
        for k in self.widgetManager.group(WIDGET_NAMES.ListBox):
            boxes[k] = self.getListBox(k)
        return boxes

    def getAllListItems(self, title):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        items = lb.get(0, END)
        return list(items)

    def getListBoxPos(self, title):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        # bug in tkinter 1.160 returns these as strings
        items = [int(i) for i in lb.curselection()]

        return items

    def removeListItemAtPos(self, title, pos):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        items = lb.get(0, END)
        if pos >= len(items):
            raise Exception("Invalid position: " + str(pos) + " must be between 0 and " + str(len(items)-1))
        lb.delete(pos)

        # show & select this item
        if pos >= lb.size():
            pos -= 1
        self.selectListItemAtPos(title, pos)

    # remove a specific item from the listBox
    # will only remove the first item that matches the String
    def removeListItem(self, title, item):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        positions = self._getListPositions(title, item)
        if len(positions) > 0:
            lb.delete(positions[0])

        # show & select this item
        if positions[0] >= lb.size():
            positions[0] -= 1
        self.selectListItemAtPos(title, positions[0])

    def setListItemAtPos(self, title, pos, newVal):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        lb.delete(pos)
        lb.insert(pos, newVal)

    def setListItem(self, title, item, newVal, first=False):
        for pos in self._getListPositions(title, item):
            self.setListItemAtPos(title, pos, newVal)
            if first:
                break

    # functions to config
    def setListItemAtPosBg(self, title, pos, col):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        lb.itemconfig(pos, bg=col)

    def setListItemAtPosFg(self, title, pos, col):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        lb.itemconfig(pos, fg=col)

    def _getListPositions(self, title, item):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        if not isinstance(item, list):
            item = [item]
        vals = lb.get(0, END)
        positions = []
        for pos, val in enumerate(vals):
            if val in item:
                positions.append(pos)
        return positions

    def setListItemBg(self, title, item, col):
        for pos in self._getListPositions(title, item):
            self.setListItemAtPosBg(title, pos, col)

    def setListItemFg(self, title, item, col):
        for pos in self._getListPositions(title, item):
            self.setListItemAtPosFg(title, pos, col)

    def clearListBox(self, title, callFunction=True):
        lb = self.widgetManager.get(WIDGET_NAMES.ListBox, title)
        lb.selection_clear(0, END)
        lb.delete(0, END)  # clear
        if callFunction and hasattr(lb, 'cmd'):
            lb.cmd()

    def clearAllListBoxes(self, callFunction=False):
        for lb in self.widgetManager.group(WIDGET_NAMES.ListBox):
            self.clearListBox(lb, callFunction)

#####################################
# FUNCTION for buttons
#####################################

    def button(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets buttons all in one go """
        widgKind = WIDGET_NAMES.Button
        image = kwargs.pop("image", None)
        icon = kwargs.pop("icon", None)
        name = kwargs.pop("label", kwargs.pop("name", None))

        try: self.widgetManager.verify(WIDGET_NAMES.Button, title)
        except: # widget exists
            if value is not None: self.setButton(title, value)
            button = self.getButton(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if image is not None: button = self._buttonMaker(title, value, "image", image, *args, **kwargs)
            elif icon is not None: button = self._buttonMaker(title, value, "icon", icon, *args, **kwargs)
            elif name is not None: button = self._buttonMaker(title, value, "named", name, *args, **kwargs)
            else: button = self._buttonMaker(title, value, "button", None, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return button

    def _buttonMaker(self, title, func, kind, extra=None, row=None, column=0, colspan=0, rowspan=0, *args, **kwargs):
        """ internal wrapper to hide kwargs from original add functions """
        align = kwargs.pop("align", None)
        if kind == "button": return self.addButton(title, func, row, column, colspan, rowspan)
        elif kind == "named": return self.addNamedButton(extra, title, func, row, column, colspan, rowspan)
        elif kind == "image": return self.addImageButton(title, func, extra, row, column, colspan, rowspan, align=align)
        elif kind == "icon": return self.addIconButton(title, func, extra, row, column, colspan, rowspan, align=align)

    def _configWidget(self, title, kind, **kwargs):
        widget = self.widgetManager.get(kind, title)
        # remove any unwanted keys
        for key in ["row", "column", "colspan", "rowspan", "label", "name"]:
            kwargs.pop(key, None)

        # ignore these for now as well
        for key in ["pad", "inpad"]:
            val = kwargs.pop(key, None)
            if val is not None:
                gui.error("Invalid argument for %s %s - %s:%s", WIDGET_NAMES.name(kind), title, key, val)

        tooltip = kwargs.pop("tip", kwargs.pop("tooltip", None))
        change = kwargs.pop("change", None)
        submit = kwargs.pop("submit", None)
        over = kwargs.pop("over", None)
        drag = kwargs.pop("drag", None)
        drop = kwargs.pop("drop", None)
        right = kwargs.pop("right", None)
        focus = kwargs.pop('focus', False)
        _font = kwargs.pop('font', None)

        if tooltip is not None: self._addTooltip(widget, tooltip, None)
        if focus: widget.focus_set()

        if change is not None: self._bindEvent(kind, title, widget, change, "change", key=None)
        if submit is not None: self._bindEvent(kind, title, widget, submit, "submit", key=None)
        if over is not None: self._bindOverEvent(kind, title, widget, over, None, None)
        if drag is not None: self._bindDragEvent(kind, title, widget, drag, None, None)
        if drop is not None: self._registerExternalDropTarget(title, widget, drop)
        if right is not None: self._bindRightClick(widget, right)

        # allow fonts to be passed in as either a dictionary or a single integer or a font object
        if _font is not None:
            if isinstance(_font, tkFont.Font):
                widget.config(font=_font)
            else:
                if not isinstance(_font, dict): # assume int
                    _font = {"size":_font}
                custFont = tkFont.Font(**_font)
                widget.config(font=custFont)

        # now pass the kwargs to the config function, ignore any baddies
        errorMsg = ""
        while True:
            try: widget.config(**kwargs)
            except TclError as e:
                try:
                    key=str(e).split()[2][2:-1]
                    errorMsg = "".join([errorMsg, key, ":", kwargs.pop(key), ", "])
                except:
                    gui.error("Invalid argument for %s %s: %s", WIDGET_NAMES.name(kind), title, e)
                    break
            else:
                break
        if len(errorMsg) > 0:
            gui.error("Invalid arguments for %s %s - %s", WIDGET_NAMES.name(kind), title, errorMsg)


    def _buildButton(self, title, func, frame, name=None):
        if name is None:
            name = title
        if isinstance(title, list):
            raise Exception("Can't add a button using a list of names: " + str(title) + " - you should use .addButtons()")
        self.widgetManager.verify(WIDGET_NAMES.Button, title)
        if not self.ttkFlag:
            but = Button(frame, text=name)
            but.config(font=self._getContainerProperty('buttonFont'))
            if self.platform in [self.MAC, self.LINUX]:
                but.config(highlightbackground=self._getContainerBg())
        else:
            but = ttk.Button(frame, text=name)

        but.DEFAULT_TEXT = name

        if func is not None:
            command = self.MAKE_FUNC(func, title)
            but.config(command=command)

        #but.bind("<Tab>", self._focusNextWindow)
        #but.bind("<Shift-Tab>", self._focusLastWindow)
        self.widgetManager.add(WIDGET_NAMES.Button, title, but)

        return but

    def addNamedButton(self, name, title, func, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a button, displaying the name as its text '''
        but = self._buildButton(title, func, self.getContainer(), name)
        self._positionWidget(but, row, column, colspan, rowspan, None)
        return but

    def addButton(self, title, func, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a button with the title as its text '''
        but = self._buildButton(title, func, self.getContainer())
        self._positionWidget(but, row, column, colspan, rowspan, None)
        return but

    def addImageButton(self, title, func, imgFile, row=None, column=0, colspan=0, rowspan=0, align=None):
        ''' adds a button, displaying the specified image file '''
        but = self._buildButton(title, func, self.getContainer())
        self._positionWidget(but, row, column, colspan, rowspan, None)
        self.setButtonImage(title, imgFile, align)
        return but

    def addIconButton(self, title, func, iconName, row=None, column=0, colspan=0, rowspan=0, align=None):
        ''' adds a button displaying the specified icon '''
        icon = os.path.join(self.icon_path, iconName.lower()+".png")
        with PauseLogger():
            return self.addImageButton(title, func, icon, row, column, colspan, rowspan, align)

    def setButton(self, name, text):
        but = self.widgetManager.get(WIDGET_NAMES.Button, name)
        try: # try to bind a function
            command = self.MAKE_FUNC(text, name)
            but.config(command=command)
        except: # otherwise change the text
            but.config(text=text)

    def getButton(self, name):
        but = self.widgetManager.get(WIDGET_NAMES.Button, name)
        return but.cget("text")

    def setButtonImage(self, name, imgFile, align=None):
        but = self.widgetManager.get(WIDGET_NAMES.Button, name)
        image = self._getImage(imgFile)
        # works on Mac & Windows :)
        if align == None:
            but.config(image=image, text="")
            if not self.ttk:
                but.config(justify=LEFT, compound=TOP)
            else:
                but.config(compound=CENTER)
        else:
            but.config(image=image, compound=align)
        # but.config(image=image, compound=None, text="") # works on Windows, not Mac

        but.image = image

    # adds a set of buttons, in the row, spannning specified columns
    # pass in a list of names & a list of functions (or a single function to
    # use for all)
    def buttons(self, names, funcs, **kwargs):
        kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
        self._addButtons(names, funcs, **kwargs)
        kwargs.pop('fill', False)
        if not isinstance(names[0], list):
            names = [names]
        for row in names:
            for title in row:
                self._configWidget(title, WIDGET_NAMES.Button, **kwargs)

    def _addButtons(self, names, funcs, row=None, column=0, colspan=0, rowspan=0, fill=False, **kwargs):
        self.addButtons(names, funcs, row, column, colspan, rowspan, fill)

    def addButtons(self, names, funcs, row=None, column=0, colspan=0, rowspan=0, fill=False):
        ''' adds a 1D/2D list of buttons '''
        if not isinstance(names, list):
            raise Exception(
                "Invalid button: " +
                names +
                ". It must be a list of buttons.")

        singleFunc = self._checkFunc(names, funcs)

        frame = self._makeWidgetBox()(self.getContainer())
        if not self.ttk:
            frame.config(background=self._getContainerBg())

        # make them into a 2D array, if not already
        if not isinstance(names[0], list):
            names = [names]
            # won't be used if single func
            if funcs is not None:
                funcs = [funcs]

        sticky = None
        if fill: sticky=E+W

        for bRow in range(len(names)):
            for i in range(len(names[bRow])):
                t = names[bRow][i]
                if funcs is None:
                    tempFunc = None
                elif singleFunc is None:
                    tempFunc = funcs[bRow][i]
                else:
                    tempFunc = singleFunc
                but = self._buildButton(t, tempFunc, frame)

                but.grid(row=bRow, column=i, sticky=sticky)
                Grid.columnconfigure(frame, i, weight=1)
                Grid.rowconfigure(frame, bRow, weight=1)
                frame.theWidgets.append(but)

        self._positionWidget(frame, row, column, colspan, rowspan)
        self.widgetManager.log(WIDGET_NAMES.FrameBox, frame)

#####################################
# FUNCTIONS for links
#####################################

    def link(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets links all in one go """
        widgKind = WIDGET_NAMES.Link

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if value is not None: self.setLink(title, value)
            link = self.getLink(title)
        else: # new widget
            if value is None:
                gui.warn("Can't create link: %s, with no value", title)
                return None
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            link = self._linkMaker(title, value, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return link

    def _linkMaker(self, title, value, row=None, column=0, colspan=0, rowspan=0, *args, **kwargs):
        if not callable(value) and not hasattr(value, '__call__'):
            return self.addWebLink(title, value, row, column, colspan, rowspan)
        else:
            return self.addLink(title, value, row, column, colspan, rowspan)

    def _buildLink(self, title):
        self._importWebBrowser()
        if not webbrowser:
            self.error("Unable to load webbrowser - can't create links")
        link = self._makeLink()(self.getContainer(), useTtk=self.ttkFlag)
        link.config(text=title, font=self._linkFont)
        if not self.ttk:
            link.config(background=self._getContainerBg())
        self.widgetManager.add(WIDGET_NAMES.Link, title, link)
        return link

    # launches a browser to the specified page
    def addWebLink(self, title, page, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a hyperlink to the specified web page '''
        link = self._buildLink(title)
        link.registerWebpage(page)
        self._positionWidget(link, row, column, colspan, rowspan)
        return link

    # executes the specified function
    def addLink(self, title, func, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a hyperlink to the specified function '''
        link = self._buildLink(title)
        if func is not None:
            myF = self.MAKE_FUNC(func, title)
            link.registerCallback(myF)
        self._positionWidget(link, row, column, colspan, rowspan)
        return link

    def getLink(self, title):
        link = self.widgetManager.get(WIDGET_NAMES.Link, title)
        return link.cget("text")

    def setLink(self, title, func):
        link = self.widgetManager.get(WIDGET_NAMES.Link, title)
        if not callable(func) and not hasattr(func, '__call__'):
            link.registerWebpage(func)
        else:
            myF = self.MAKE_FUNC(func, title)
            link.registerCallback(myF)

#####################################
# FUNCTIONS for grips
#####################################

    def grip(self, *args, **kwargs):
        """ simpleGUI - adds grip """
        kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
        return self.addGrip(*args, **kwargs)

    # adds a simple grip, used to drag the window around
    def addGrip(self, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a grip, for dragging the GUI around '''
        grip = self._makeGrip()(self.getContainer())
        self._positionWidget(grip, row, column, colspan, rowspan)
        self._addTooltip(grip, "Drag here to move", True)
        return grip


#####################################
# FUNCTIONS for dnd
#####################################

    def addTrashBin(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' NOT IN USE - adds a trashbin, for discarding dragged items '''
        trash = TrashBin(self.getContainer())
        self._positionWidget(trash, row, column, colspan, rowspan)
        return trash

#####################################
# FUNCTIONS for turtle
#####################################

    def addTurtle(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a turtle widget at the specified position '''
        self._loadTurtle()
        if turtle is False:
            raise Exception("Unable to load turtle")
        self.widgetManager.verify(WIDGET_NAMES.Turtle, title)
        canvas = Canvas(self.getContainer())
        canvas.screen = turtle.TurtleScreen(canvas)
        self._positionWidget(canvas, row, column, colspan, rowspan)
        self.widgetManager.add(WIDGET_NAMES.Turtle, title, canvas)
        canvas.turtle = turtle.RawTurtle(canvas.screen)
        return canvas.turtle

    def getTurtleScreen(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Turtle, title).screen

    def getTurtle(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Turtle, title).turtle

#####################################
# FUNCTIONS for canvas
#####################################

    def addCanvas(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a canvas at the specified position '''
        self.widgetManager.verify(WIDGET_NAMES.Canvas, title)
        canvas = Canvas(self.getContainer())
        canvas.config(bd=0, highlightthickness=0)
        canvas.imageStore = []
        self._positionWidget(canvas, row, column, colspan, rowspan, "news")
        self.widgetManager.add(WIDGET_NAMES.Canvas, title, canvas)
        return canvas

    def getCanvas(self, title):
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title)

    def clearCanvas(self, title):
        self.widgetManager.get(WIDGET_NAMES.Canvas, title).delete("all")

    # function to configure a canvas map
    def setCanvasMap(self, name, func, coords):
        self._setWidgetMap(name, WIDGET_NAMES.Canvas, func, coords)

    def addCanvasCircle(self, title, x, y, diameter, **kwargs):
        ''' adds a circle to the specified canvas '''
        return self.addCanvasOval(title, x, y, diameter, diameter, **kwargs)

    def addCanvasOval(self, title, x, y, xDiam, yDiam, **kwargs):
        ''' adds a oval to the specified canvas '''
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title).create_oval(x, y, x+xDiam, y+yDiam, **kwargs)

    def addCanvasLine(self, title, x, y, x2, y2, **kwargs):
        ''' adds a line to the specified canvas '''
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title).create_line(x, y, x2, y2, **kwargs)

    def addCanvasRectangle(self, title, x, y, w, h, **kwargs):
        ''' adds a rectangle to the specified canvas '''
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title).create_rectangle(x, y, x+w, y+h, **kwargs)

    def addCanvasText(self, title, x, y, text=None, **kwargs):
        ''' adds text to the specified canvas '''
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title).create_text(x, y, text=text, **kwargs)

    def addCanvasImage(self, title, x, y, image=image, **kwargs):
        ''' adds an image to the specified canvas '''
        canv = self.widgetManager.get(WIDGET_NAMES.Canvas, title)
        if isinstance(image, UNIVERSAL_STRING):
            image = self._getImage(image)
        canv.imageStore.append(image)
        return self.widgetManager.get(WIDGET_NAMES.Canvas, title).create_image(x, y, image=image, **kwargs)

    def setCanvasEvent(self, title, item, event, function, add=None):
        canvas = self.widgetManager.get(WIDGET_NAMES.Canvas, title)
        canvas.tag_bind(item, event, function, add)

    def _canvasMaker(self, title, row=None, column=0, colspan=0, rowspan=0, **kwargs):
        return self.addCanvas(title, row, column, rowspan)

    def canvas(self, title, *args, **kwargs):
        """ simpleGUI - adds, sets & gets canases all in one go """
        widgKind = WIDGET_NAMES.Canvas
        submit = kwargs.pop("submit", None)
        _map = kwargs.pop("map", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            # NB. no SETTER
            canvas = self.getCanvas(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            canvas = self._canvasMaker(title, *args, **kwargs)

        if submit is not None and _map is not None:
            self.setCanvasMap(title, submit, _map)
        else:
            gui.warn("Must specify a submit function when setting a canvas map: %s", title)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        self._configWidget(title, widgKind, **kwargs)
        return canvas

#####################################
# FUNCTIONS for Microbits
#####################################

    def microbit(self, title, *args, **kwargs):
        '''simpleGUI - adds, sets & gets microbits all in one go'''
        widgKind = WIDGET_NAMES.MicroBit
        image = kwargs.pop("image", None)
        brightness = kwargs.pop("brightness", None)
        x = kwargs.pop("x", None)
        y = kwargs.pop("y", None)
        clear = kwargs.pop("clear", False)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            mb = self.getMicroBit(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            mb = self.addMicroBit(title, *args, **kwargs)

        if image is not None: self.setMicroBitImage(title, image)
        if brightness is not None: self.setMicroBitPixel(title, x, y, brightness)
        if clear: self.clearMicroBit(title)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return mb

    def addMicroBit(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a simple microbit widget
             used with permission from Ben Goodwin '''
        self.widgetManager.verify(WIDGET_NAMES.MicroBit, title)
        mb = MicroBitSimulator(self.getContainer())
        self._positionWidget(mb, row, column, colspan, rowspan)
        self.widgetManager.add(WIDGET_NAMES.MicroBit, title, mb)
        return mb

    def setMicroBitImage(self, title, image):
        self.widgetManager.get(WIDGET_NAMES.MicroBit, title).show(image)

    def setMicroBitPixel(self, title, x, y, brightness):
        self.widgetManager.get(WIDGET_NAMES.MicroBit, title).set_pixel(x, y, brightness)

    def clearMicroBit(self, title):
        self.widgetManager.get(WIDGET_NAMES.MicroBit, title).clear()

#####################################
# DatePicker Widget - using Form Container
#####################################

    def date(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for datePicker() """
        return self.datePicker(title, value, *args, **kwargs)

    def datePicker(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets datePickers all in one go """
        widgKind = WIDGET_NAMES.DatePicker
        change = kwargs.pop("change", None)
        toValue = kwargs.pop("toValue", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            dp = self.getDatePicker(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            dp = self.addDatePicker(title, *args, **kwargs)

        if value is not None:
            if toValue is None: self.setDatePicker(title, value)
            else: self.setDatePickerRange(title, startYear=value, endYear=toValue)
        if change is not None: self.setDatePickerChangeFunction(title, change)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return dp

    def addDatePicker(self, name, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a date picker at the specified position '''
        self.widgetManager.verify(WIDGET_NAMES.DatePicker, name)
        # initial DatePicker has these dates
        days = range(1, 32)
        self.MONTH_NAMES = calendar.month_name[1:]
        years = range(1970, 2021)

        # create a frame, and add the widgets
        frame = self.startFrame(name, row, column, colspan, rowspan)
        self.setExpand("none")
        self.addLabel(name + "_DP_DayLabel", "Day:", 0, 0)
        self.setLabelAlign(name + "_DP_DayLabel", "w")
        self.addOptionBox(name + "_DP_DayOptionBox", days, 0, 1)
        self.addLabel(name + "_DP_MonthLabel", "Month:", 1, 0)
        self.setLabelAlign(name + "_DP_MonthLabel", "w")
        self.addOptionBox(name + "_DP_MonthOptionBox", self.MONTH_NAMES, 1, 1)
        self.addLabel(name + "_DP_YearLabel", "Year:", 2, 0)
        self.setLabelAlign(name + "_DP_YearLabel", "w")
        self.addOptionBox(name + "_DP_YearOptionBox", years, 2, 1)
        self.setOptionBoxChangeFunction(
            name + "_DP_MonthOptionBox",
            self._updateDatePickerDays)
        self.setOptionBoxChangeFunction(
            name + "_DP_YearOptionBox",
            self._updateDatePickerDays)
        self.stopFrame()
        frame.isContainer = False
        self.widgetManager.add(WIDGET_NAMES.DatePicker, name, frame)

    def setDatePickerFg(self, name, fg):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, name)
        self.setLabelFg(name + "_DP_DayLabel", fg)
        self.setLabelFg(name + "_DP_MonthLabel", fg)
        self.setLabelFg(name + "_DP_YearLabel", fg)

    def setDatePickerChangeFunction(self, title, function):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, title)
        cmd = self.MAKE_FUNC(function, title)
        self.setOptionBoxChangeFunction(title + "_DP_DayOptionBox", cmd)
        self.widgetManager.get(WIDGET_NAMES.OptionBox, title + "_DP_DayOptionBox").function = cmd

    # function to update DatePicker dropDowns
    def _updateDatePickerDays(self, title):
        if title.find("_DP_MonthOptionBox") > -1:
            title = title.split("_DP_MonthOptionBox")[0]
        elif title.find("_DP_YearOptionBox") > -1:
            title = title.split("_DP_YearOptionBox")[0]
        else:
            self.warn("Can't update days in DatePicker:%s", title)
            return

        day = self.getOptionBox(title + "_DP_DayOptionBox")
        month = self.MONTH_NAMES.index(self.getOptionBox(title + "_DP_MonthOptionBox")) + 1
        year = int(self.getOptionBox(title + "_DP_YearOptionBox"))
        days = range(1, calendar.monthrange(year, month)[1] + 1)
        self.changeOptionBox(title + "_DP_DayOptionBox", days)

        # keep previous day if possible
        with PauseLogger():
            self.setOptionBox(title + "_DP_DayOptionBox", day, callFunction=False)

        box = self.widgetManager.get(WIDGET_NAMES.OptionBox, title + "_DP_DayOptionBox")
        if hasattr(box, 'function'):
            box.function()

    # set a date for the named DatePicker
    def setDatePickerRange(self, title, startYear, endYear=None):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, title)
        if endYear is None:
            endYear = datetime.date.today().year
        years = range(startYear, endYear + 1)
        self.changeOptionBox(title + "_DP_YearOptionBox", years)

    def setDatePicker(self, title, date="today"):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, title)
        if date == "today":
            date = datetime.date.today()
        self.setOptionBox(title + "_DP_YearOptionBox", str(date.year))
        self.setOptionBox(title + "_DP_MonthOptionBox", date.month - 1)
        self.setOptionBox(title + "_DP_DayOptionBox", date.day - 1)

    def clearDatePicker(self, title, callFunction=True):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, title)
        self.setOptionBox(title + "_DP_YearOptionBox", 0, callFunction)
        self.setOptionBox(title + "_DP_MonthOptionBox", 0, callFunction)
        self.setOptionBox(title + "_DP_DayOptionBox", 0, callFunction)

    def clearAllDatePickers(self, callFunction=False):
        for k in self.widgetManager.group(WIDGET_NAMES.DatePicker):
            self.clearDatePicker(k, callFunction)

    def getDatePicker(self, title):
        self.widgetManager.get(WIDGET_NAMES.DatePicker, title)
        day = int(self.getOptionBox(title + "_DP_DayOptionBox"))
        month = self.MONTH_NAMES.index(
            self.getOptionBox(
                title + "_DP_MonthOptionBox")) + 1
        year = int(self.getOptionBox(title + "_DP_YearOptionBox"))
        date = datetime.date(year, month, day)
        return date

    def getAllDatePickers(self):
        dps = {}
        for k in self.widgetManager.group(WIDGET_NAMES.DatePicker):
            dps[k] = self.getDatePicker(k)
        return dps

#####################################
# FUNCTIONS for ACCESSABILITY
#####################################

    def _makeAccess(self):
        if not self.accessMade:
            def _close(): self.hideSubWindow("access_access_subwindow")
            def _changeFg(): self.label("access_fg_colBox", bg=self.colourBox(self.getLabelBg("access_fg_colBox")))
            def _changeBg(): self.label("access_bg_colBox", bg=self.colourBox(self.getLabelBg("access_bg_colBox")))
            def _settings():
                font = {"underline":self.check("access_underline_check"), "overstrike":self.check("access_overstrike_check")}
                font["weight"] = "bold" if self.check("access_bold_check") is True else "normal"
                font["slant"] = "roman" if self.radio("access_italic_radio") == "Normal" else "italic"
                if len(self.listbox("access_family_listbox")) > 0: font["family"] = self.listbox("access_family_listbox")[0]
                if self.option("access_size_option") is not None: font["size"] = self.option("access_size_option")

                if self.check('access_label_check'): self.labelFont = font
                if self.check('access_input_check'): self.inputFont = font
                if self.check('access_button_check'): self.buttonFont = font

                self.bg = self.getLabelBg("access_bg_colBox")
                self.fg = self.getLabelBg("access_fg_colBox")

            self.accessOrigFont = self.accessOrigBg = self.accessOrigFg = None
            with self.subWindow("access_access_subwindow", sticky = "news", title="Accessibility", resizable=False) as sw:
                if not self.ttk:
                    sw.config(padx=5, pady=1)
                with self.labelFrame("access_font_labelframe", sticky="news", name="Font") as lf:
                    if not self.ttk:
                        lf.config(padx=5, pady=5, font=self._accessFont)

                    with self.frame("access_ticks_frame", colspan=2):
                        self.check("access_label_check", True, label="Labels", pos=(0,0), font=self._accessFont, tip="Set label fonts")
                        self.check("access_input_check", label="Inputs", pos=(0,1), font=self._accessFont, tip="Set input fonts")
                        self.check("access_button_check", label="Buttons", pos=(0,2), font=self._accessFont, tip="Set button fonts")

                    self.listbox("access_family_listbox", self.fonts, rows=6, tip="Choose a font", colspan=2, font=self._accessFont)
                    self.option("access_size_option", [7, 8, 9, 10, 12, 13, 14, 16, 18, 20, 22, 25, 29, 34, 40], label="Size:", tip="Choose a font size", font=self._accessFont)
                    self.check("access_bold_check", name="Bold", pos=('p',1), tip="Check this to make all font bold", font=self._accessFont)
                    self.radio("access_italic_radio", "Normal", tip="No italics", font=self._accessFont)
                    self.radio("access_italic_radio", "Italic", pos=('p',1), tip="Set font italic", font=self._accessFont)
                    self.check("access_underline_check", name="Underline", tip="Underline all text", font=self._accessFont)
                    self.check("access_overstrike_check", name="Overstrike", pos=('p',1), tip="Strike out all text", font=self._accessFont)
                with self.labelFrame("access_colour_labelframe", sticky="news", name="Colours") as lf:
                    if not self.ttk:
                        lf.config(padx=5, pady=5, font=self._accessFont)
                    self.label("access_fg_text", "Foreground:", sticky="ew", anchor="w", font=self._accessFont)
                    self.label("access_fg_colBox", "", pos=('p',1), sticky="ew", submit=_changeFg, relief="ridge", tip="Click here to set the foreground colour", font=self._accessFont, width=14)
                    self.label("access_bg_text", "Background:", sticky="ew", anchor="w", font=self._accessFont)
                    self.label("access_bg_colBox", "", pos=('p',1), sticky="ew", submit=_changeBg, relief="ridge", tip="Click here to set the background colour", font=self._accessFont, width=14)
                self.sticky="se"
                with self.frame("access_button_box"):
                    self.button("access_apply_button", _settings, name="Apply", pos=(0,0), font=self._accessFont)
                    self.button("access_reset_button", self._resetAccess, name="Reset", pos=(0,1), font=self._accessFont)
                    self.button("access_close_button", _close, name="Close", pos=(0,2), font=self._accessFont)
            self.accessMade = True

    def _resetAccess(self):
        if self.accessMade:
            self.check("access_label_check", True)
            self.check("access_input_check", False)
            self.check("access_button_check", False)

            self.listbox("access_family_listbox", self.accessOrigFont["family"])
            self.option("access_size_option", str(self.accessOrigFont["size"]))

            if self.accessOrigFont["weight"] == "normal": self.check("access_bold_check", False)
            else: self.check("access_bold_check", True)

            if self.accessOrigFont["slant"] == "roman": self.radio("access_italic_radio", "Normal")
            else: self.radio("access_italic_radio", "Italic")

            self.check("access_overstrike_check", self.accessOrigFont["overstrike"])
            self.check("access_underline_check", self.accessOrigFont["underline"])

            self.label("access_fg_colBox", bg=self.accessOrigFg)
            self.label("access_bg_colBox", bg=self.accessOrigBg)
        else:
            gui.warn("Accessibility not set up yet.")


    def showAccess(self, location=None):
        self._makeAccess()
        # update current settings
        self.accessOrigFont = self.font
        self.accessOrigBg = self.bg
        self.accessOrigFg = self.fg
        self._resetAccess()
        self.showSubWindow("access_access_subwindow")

#####################################
# FUNCTIONS for labels
#####################################

    def _parsePos(self, pos, kwargs):
        # alternative for specifying position
        if type(pos) != list and type(pos) != tuple: pos = (pos,)
        if len(pos) > 0: kwargs["row"] = pos[0]
        if len(pos) > 1: kwargs["column"] = pos[1]
        if len(pos) > 2: kwargs["colspan"] = pos[2]
        if len(pos) > 3: kwargs["rowspan"] = pos[3]

        # allow an alternative kwarg
        if "col" in kwargs: kwargs["column"]=kwargs.pop("col")

        # let user specify stickt/stretch/expan
        sticky = kwargs.pop("sticky", None)
        if sticky is not None: self.setSticky(sticky)
        stretch = kwargs.pop("stretch", None)
        if stretch is not None: self.setStretch(stretch)
        expand = kwargs.pop("expand", None)
        if expand is not None: self.setExpand(expand)

        return kwargs

    def label(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets labels all in one go """
        widgKind = WIDGET_NAMES.Label
        kind = kwargs.pop("kind", "standard").lower().strip()

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if value is not None: self.setLabel(title, value)
            label = self.getLabel(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if kind == "flash": label = self._labelMaker(title, value, kind, *args, **kwargs)
            elif kind == "selectable": label = self._labelMaker(title, value, kind, *args, **kwargs)
            else: label = self._labelMaker(title, value, "label", *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return label

    def _labelMaker(self, title, text=None, kind="label", row=None, column=0, colspan=0, rowspan=0, **kwargs):
        """ Internal wrapper, to hide kwargs from original add functions """
        if kind == "flash": return self.addFlashLabel(title, text, row, column, colspan, rowspan)
        elif kind == "selectable": return self.addSelectableLabel(title, text, row, column, colspan, rowspan)
        elif kind == "label": return self.addLabel(title, text, row, column, colspan, rowspan)

    def _flash(self):
        if not self.alive: return
        if self.doFlash:
            for lab in self.widgetManager.group(WIDGET_NAMES.FlashLabel):
                bg = lab.cget("background")
                fg = lab.cget("foreground")
                lab.config(background=fg, foreground=bg)
        self.flashId = self.topLevel.after(250, self._flash)

    def addFlashLabel(self, title, text=None, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a label with flashing text '''
        lab = self.addLabel(title, text, row, column, colspan, rowspan)
        self.widgetManager.log(WIDGET_NAMES.FlashLabel, lab)
        self.doFlash = True
        return lab

    def addSelectableLabel(self, title, text=None, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a label with selectable text '''
        return self.addLabel(title, text, row, column, colspan, rowspan, selectable=True)

    def addLabel(self, title, text=None, row=None, column=0, colspan=0, rowspan=0, selectable=False):
        """Add a label to the GUI.
        :param title: a unique identifier for the Label
        :param text: optional text for the Label
        :param row/column/colspan/rowspan: the row/column to position the label in & how many rows/columns to strecth across
        :raises ItemLookupError: raised if the title is not unique
        """
        self.widgetManager.verify(WIDGET_NAMES.Label, title)
        if text is None:
            gui.trace("Not specifying text for labels (%s) now uses the title for the text. If you want an empty label, pass an empty string ''", title)
            text = title

        if not selectable:
            if not self.ttkFlag:
                lab = Label(self.getContainer(), text=text)
                lab.config(justify=LEFT, font=self._getContainerProperty('labelFont'), background=self._getContainerBg())
                lab.origBg = self._getContainerBg()
            else:
                lab = ttk.Label(self.getContainer(), text=text)
        else:
            lab = SelectableLabel(self.getContainer(), text=text)
            lab.config(justify=CENTER, font=self._getContainerProperty('labelFont'), background=self._getContainerBg())
            lab.origBg = self._getContainerBg()

        lab.inContainer = False
        lab.DEFAULT_TEXT = text

        self.widgetManager.add(WIDGET_NAMES.Label, title, lab)
        self._positionWidget(lab, row, column, colspan, rowspan)
        return lab

    def addEmptyLabel(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an empty label '''
        return self.addLabel(title=title, text='', row=row, column=column, colspan=colspan, rowspan=rowspan)

    def addLabels(self, names, row=None, colspan=0, rowspan=0):
        ''' adds a set of labels, in the row, spannning specified columns '''
        frame = self._makeWidgetBox()(self.getContainer())
        if not self.ttkFlag:
            frame.config(background=self._getContainerBg())
        for i in range(len(names)):
            self.widgetManager.verify(WIDGET_NAMES.Label, names[i])
            if not self.ttkFlag:
                lab = Label(frame, text=names[i])
                lab.config(font=self._getContainerProperty('labelFont'), justify=LEFT, background=self._getContainerBg())
            else:
                lab = ttk.Label(frame, text=names[i])
            lab.DEFAULT_TEXT = names[i]
            lab.inContainer = False

            self.widgetManager.add(WIDGET_NAMES.Label, names[i], lab)
            lab.grid(row=0, column=i)
            Grid.columnconfigure(frame, i, weight=1)
            Grid.rowconfigure(frame, 0, weight=1)
            frame.theWidgets.append(lab)

        self._positionWidget(frame, row, 0, colspan, rowspan)
        self.widgetManager.log(WIDGET_NAMES.FrameBox, frame)

    def setLabel(self, name, text):
        lab = self.widgetManager.get(WIDGET_NAMES.Label, name)
        lab.config(text=text)

    def getLabel(self, name):
        lab = self.widgetManager.get(WIDGET_NAMES.Label, name)
        return lab.cget("text")

    def clearLabel(self, name):
        self.setLabel(name, "")

    def clearAllLabels(self):
        for lb in self.widgetManager.group(WIDGET_NAMES.Label):
            self.clearLabel(lb)

#####################################
# FUNCTIONS to add Text Area
#####################################

    def text(self, title, value=None, *args, **kwargs):
        """ simpleGUI - shortner for textArea() """
        return self.textArea(title, value, *args, **kwargs)

    def textArea(self, title, value=None, *args, **kwargs):
        """ adds, sets & gets textAreas all in one go """
        widgKind = WIDGET_NAMES.TextArea
        scroll = kwargs.pop("scroll", False)
        end = kwargs.pop("end", True)
        replace = kwargs.pop("replace", False)
        callFunction = kwargs.pop("callFunction", True)
        disabled = kwargs.pop("disabled", False)
        tag = kwargs.pop("tag", None)
        tags = kwargs.pop("tags", [])

        try: self.widgetManager.verify(WIDGET_NAMES.TextArea, title)
        except: # widget exists
            text = self.getTextArea(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if scroll: text = self._textMaker(title, "scroll", *args, **kwargs)
            else: text = self._textMaker(title, "text", *args, **kwargs)
            callFunction = False

        # create any tags
        for _tag in tags:
            self.textAreaCreateTag(title, _tag[0], **_tag[1])

        if replace: self.clearTextArea(title)
        if value is not None: self.setTextArea(title, value, end=end, callFunction=callFunction, tag=tag)
        if disabled: self.disableTextArea(title)
        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return text

    def _textMaker(self, title, kind="text", row=None, column=0, colspan=0, rowspan=0, *args, **kwargs):
        if kind == "scroll": return self.addScrolledTextArea(title, row, column, colspan, rowspan)
        elif kind == "text": return self.addTextArea(title, row, column, colspan, rowspan)

    def _buildTextArea(self, title, frame, scrollable=False):
        """ Internal wrapper, used for building TextAreas.

        :param title: the key used to reference this TextArea
        :param frame: this should be a container, used as the parent for the OptionBox
        :param scrollable: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        self.widgetManager.verify(WIDGET_NAMES.TextArea, title)
        if scrollable:
            text = AjScrolledText(frame)
        else:
            text = AjText(frame)
        text.config(width=20, height=10, undo=True, wrap=WORD)

        if not self.ttkFlag:
            if self.platform in [self.MAC, self.LINUX]:
                text.config(highlightbackground=self._getContainerBg())

        text.bind("<Tab>", self._focusNextWindow)
        text.bind("<Shift-Tab>", self._focusLastWindow)

        # add a right click menu
        text.var = None
        self._addRightClickMenu(text)

        self.widgetManager.add(WIDGET_NAMES.TextArea, title, text)
        self.logTextArea(title)

        return text

    def addTextArea(self, title, row=None, column=0, colspan=0, rowspan=0, text=None):
        """ Adds a TextArea with the specified title
        Simply calls internal _buildTextArea function before positioning the widget

        :param title: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        txt = self._buildTextArea(title, self.getContainer())
        self._positionWidget(txt, row, column, colspan, rowspan, N+E+S+W)
        if text is not None: self.setTextArea(title, text, callFunction=False)
        return txt

    def addScrolledTextArea(self, title, row=None, column=0, colspan=0, rowspan=0, text=None):
        """ Adds a Scrollable TextArea with the specified title
        Simply calls internal _buildTextArea functio, specifying a ScrollabelTextArea before positioning the widget

        :param title: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        txt = self._buildTextArea(title, self.getContainer(), True)
        self._positionWidget(txt, row, column, colspan, rowspan, N+E+S+W)
        if text is not None: self.setTextArea(title, text, callFunction=False)
        return txt

    def getTextArea(self, title):
        """ Gets the text in the specified TextArea

        :param title: the TextArea to check
        :returns: the text in the specified TextArea
        :raises ItemLookupError: if the title can't be found
        """
        return self.widgetManager.get(WIDGET_NAMES.TextArea, title).getText()

    def getAllTextAreas(self):
        """ Convenience function to get the text for all TextAreas in the GUI.

        :returns: a dictionary containing the result of calling getTextArea for every TextArea in the GUI
        """
        areas = {}
        for k in self.widgetManager.group(WIDGET_NAMES.TextArea):
            areas[k] = self.getTextArea(k)
        return areas

    def textAreaCreateTag(self, title, name, **kwargs):
        """ creates a new tag on the specified text area """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_config(name, **kwargs)

    def textAreaChangeTag(self, title, name, **kwargs):
        """ changes a tag on the specified text area """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_config(name, **kwargs)

    def textAreaDeleteTag(self, title, *tags):
        """ deletes the specified tag """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_delete(*tags)

    def textAreaTagPattern(self, title, tag, pattern, regexp=False):
        """ applies the tag to the specified text """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.highlightPattern(pattern, tag, regexp=regexp)

    def textAreaTagRange(self, title, tag, start, end=END):
        """ applies the tag to the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_add(tag, start, end)

    def textAreaTagSelected(self, title, tag):
        if self.widgetManager.get(WIDGET_NAMES.TextArea, title).tag_ranges(SEL):
            self.textAreaTagRange(title, tag, SEL_FIRST, SEL_LAST)
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).focus_set()

    def textAreaUntagRange(self, title, tag, start, end=END):
        """removes the tag from the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_remove(tag, start, end)

    def textAreaToggleFontRange(self, title, tag, start, end=END):
        """ will toggle the tag at the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        tag = ta.verifyFontTag(tag)

        if tag in ta.tag_names(start):
            ta.tag_remove("AJ_"+tag, start, end)
        else:
            self.textAreaApplyFontRange(title, tag, start, end)

    def textAreaToggleFontSelected(self, title, tag):
        if self.widgetManager.get(WIDGET_NAMES.TextArea, title).tag_ranges(SEL):
            self.textAreaToggleFontRange(title, tag, SEL_FIRST, SEL_LAST)
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).focus_set()

    def textAreaApplyFontSelected(self, title, tag):
        if self.widgetManager.get(WIDGET_NAMES.TextArea, title).tag_ranges(SEL):
            self.textAreaApplyFontRange(title, tag, SEL_FIRST, SEL_LAST)
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).focus_set()

    def textAreaApplyFontRange(self, title, tag, start, end=END):
        """removes the tag from the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        tag = ta.verifyFontTag(tag)
        if tag != "UNDERLINE":
            ta.tag_remove("AJ_BOLD", start, end)
            ta.tag_remove("AJ_ITALIC", start, end)
            ta.tag_remove("AJ_BOLD_ITALIC", start, end)
        ta.tag_add("AJ_" + tag, start, end)

    def textAreaUntagSelected(self, title, tag):
        if self.widgetManager.get(WIDGET_NAMES.TextArea, title).tag_ranges(SEL):
            self.textAreaUntagRange(title, tag, SEL_FIRST, SEL_LAST)
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).focus_set()

    def textAreaToggleTagRange(self, title, tag, start, end=END):
        """ will toggle the tag at the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        if tag in ta.tag_names(start): self.textAreaUntagRange(title, tag, start, end)
        else: self.textAreaTagRange(title, tag, start, end)

    def textAreaToggleTagSelected(self, title, tag):
        if self.widgetManager.get(WIDGET_NAMES.TextArea, title).tag_ranges(SEL):
            self.textAreaToggleTagRange(title, tag, SEL_FIRST, SEL_LAST)
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).focus_set()

    def searchTextArea(self, title, pattern, start=None, stop=None, nocase=True, backwards=False):
        """ will find and highlight the specified text, returning the position """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        if start is None: start = ta.index(INSERT)
        pos = ta.search(pattern, start, stopindex=stop, nocase=nocase, backwards=backwards)
        ta.focus_set()
        if pos == "":
            return None
        else:
            end = str(pos) + " + " + str(len(pattern)) + " c"
            ta.see(pos)
            ta.tag_add(SEL, pos, end)
            ta.mark_set("insert", pos)
            return pos

    def getTextAreaTag(self, title, tag):
        """ returns all details about the specified tag """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        return ta.tag_config(tag)

    def getTextAreaTags(self, title):
        """ returns a list of all tags in the text area """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        return ta.tag_names()

    def setTextAreaFont(self, title, **kwargs):
        """ changes the font of a text area """
        self.widgetManager.get(WIDGET_NAMES.TextArea, title).setFont(**kwargs)

    def setTextArea(self, title, text, end=True, callFunction=True, tag=None):
        """ Add the supplied text to the specified TextArea

        :param title: the TextArea to change
        :param text: the text to add to the TextArea
        :param end: where to insert the text, by default it is added to the end. Set end to False to add to the beginning.
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)

        ta.pauseCallFunction(callFunction)
        # in case it's disabled
        _state = ta.cget('state')
        ta.config(state='normal')

        if end:
            pos = ta.index('end -1c linestart')
            ta.insert(END, text)
            ta.see(END)
#            if tag is not None: self.textAreaTagRange(title, tag, pos)
        else:
            ta.insert('1.0', text)
            ta.see('1.0')
#            if tag is not None: ta.textAreaTagPattern(title, tag, text)

        ta.config(state=_state)
        ta.resumeCallFunction()

    def clearTextArea(self, title, callFunction=True):
        """ Removes all text from the specified TextArea

        :param title: the TextArea to change
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.pauseCallFunction(callFunction)
        # in case it's disabled
        _state = ta.cget('state')
        ta.config(state='normal')
        ta.delete('1.0', END)
        ta.config(state=_state)
        ta.resumeCallFunction()

    def clearAllTextAreas(self, callFunction=False):
        """ Convenience function to clear all TextAreas in the GUI
        Will simply call clearTextArea on each TextArea

        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        """
        for ta in self.widgetManager.group(WIDGET_NAMES.TextArea):
            self.clearTextArea(ta, callFunction=callFunction)

    def highlightTextArea(self, title, start, end=END):
        """ selects text in the specified range """
        ta = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
        ta.tag_add(SEL, start, end)

    def logTextArea(self, title):
        """ Creates an md5 hash - can be used later to check if the TextArea has changed
        The hash is stored in the widget

        :param title: the TextArea to hash
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self._loadHashlib()
        if hashlib is False:
            self.warn("Unable to log TextArea, hashlib library not available")
        else:
            text = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
            text.__hash = text.getTextAreaHash()

    def textAreaChanged(self, title):
        """ Creates a temporary md5 hash - and compares it with a previously generated & stored hash
        The previous hash has to be generated manually, by calling logTextArea

        :param title: the TextArea to hash
        :returns: bool - True if the TextArea has changed or False if it hasn't
        :raises ItemLookupError: if the title can't be found
        """
        self._loadHashlib()
        if hashlib is False:
            self.warn("Unable to log TextArea, hashlib library not available")
        else:
            text = self.widgetManager.get(WIDGET_NAMES.TextArea, title)
            return text.__hash != text.getTextAreaHash()

#####################################
# FUNCTIONS to add Tree Widgets
#####################################

    def tree(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets trees all in one go """
        widgKind = WIDGET_NAMES.Tree

        click = kwargs.pop("click", None)
        dblClick = kwargs.pop("dbl", None)
        edit = kwargs.pop("edit", None)
        editable = kwargs.pop("editable", None)
        showAttr = kwargs.pop("attributes", None)
        showMenu = kwargs.pop("menu", None)

        fg = kwargs.pop("fg", None)
        bg = kwargs.pop("bg", None)
        fgH = kwargs.pop("fgH", None)
        bgH = kwargs.pop("bgH", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            tree = self.getTree(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            tree = self.addTree(title, value, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        self.setTreeColours(title, fg, bg, fgH, bgH)

        if click is not None: self.setTreeClickFunction(title, click)
        if edit is not None: self.setTreeEditFunction(title, edit)
        if dblClick is not None: self.setTreeDoubleClickFunction(title, dblClick)
        if editable is not None: self.setTreeEditable(title, editable)
        if showAttr is not None: self.showTreeAttributes(title, showAttr)
        if showMenu is not None: self.showTreeMenu(title, showMenu)
        return tree

    def addTree(self, title, data, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a navigatable tree, displaying the specified xml text '''
        self.widgetManager.verify(WIDGET_NAMES.Tree, title)
        self._importAjtree()
        if parseString is False:
            self.warn("Unable to parse xml files. .addTree() not available")
            return

        if isinstance(data, UNIVERSAL_STRING):
            data = parseString(data)
        else:
            pass # assume xml object
            
        return self._buildTree(title, data, row, column, colspan, rowspan)

    def _buildTree(self, title, xmlDoc, row=None, column=0, colspan=0, rowspan=0):
        self.widgetManager.verify(WIDGET_NAMES.Tree, title)

        frame = ScrollPane(
            self.getContainer(),
            relief=RAISED,
            borderwidth=2,
            bg="#FFFFFF",
            highlightthickness=0,
            takefocus=1)
        self._positionWidget(frame, row, column, colspan, rowspan, "NSEW")

        treeData = self._makeAjTreeData()(xmlDoc)
        gui.trace("TreeData populated: %s", title)

        treeNode = self._makeAjTreeNode()(frame.getPane(), None, treeData)
        gui.trace("TreeNode created: %s", title)

        self.widgetManager.add(WIDGET_NAMES.Tree, title, treeNode)
        # update() & expand() called in go() function
        return treeNode

    # not complete yet...
    def clearTree(self, title):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.destroy()
        tree.update()

    def showTreeAttributes(self, title, show=True):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        self._loadTooltip()
        tree.showAttributes(show)

    # not complete yet...
    def showTreeMenu(self, title, show=True):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.showMenu(show)

    # not complete yet...
    def addTreeChild(self, title, data):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        if isinstance(data, UNIVERSAL_STRING):
            data = parseString(data)
        treeData = self._makeAjTreeData()(data)
        tree.addChild(treeData)

    def setTreeEditable(self, title, value=True):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.item.setCanEdit(value)

    def setTreeBg(self, title, colour):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.setBgColour(colour)

    def setTreeFg(self, title, colour):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.setFgColour(colour)

    def setTreeHighlightBg(self, title, colour):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.setBgHColour(colour)

    def setTreeHighlightFg(self, title, colour):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.setFgHColour(colour)

    def setTreeColours(self, title, fg=None, bg=None, fgH=None, bgH=None):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        tree.setAllColours(bg, fg, bgH, fgH)

    def setTreeDoubleClickFunction(self, title, func):
        if func is not None:
            tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
            tree.item.registerDblClick(title, func)

    def setTreeClickFunction(self, title, func):
        if func is not None:
            tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
            tree.item.registerClick(title, func)

    def setTreeEditFunction(self, title, func):
        if func is not None:
            tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
            command = self.MAKE_FUNC(func, title)
            tree.registerEditEvent(command)

    # get whole tree as XML
    def getTreeXML(self, title):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        return tree.item.node.toxml()

    # get selected node as a string
    def getTreeSelected(self, title):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        return tree.getSelectedText()

    # get selected node (and children) as XML
    def getTreeSelectedXML(self, title):
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        item = tree.getSelected()
        if item is not None:
            return item.node.toxml()
        else:
            return None

    def generateTree(self, title):
        """ displays data inside tree """
        tree = self.widgetManager.get(WIDGET_NAMES.Tree, title)
        gui.trace("Generating Tree: %s", title)
        tree.update()
        gui.trace("Tree updated: %s", title)
        tree.expand()
        gui.trace("Tree expanded: %s", title)

#####################################
# FUNCTIONS to add Message Box
#####################################

    def message(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets messages all in one go """
        widgKind = WIDGET_NAMES.Message

        try: self.widgetManager.verify(WIDGET_NAMES.Message, title)
        except: # widget exists
            if value is not None: self.setMessage(title, value)
            msg = self.getMessage(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            msg = self._messageMaker(title, value, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return msg

    def _messageMaker(self, title, text, row=None, column=0, colspan=0, rowspan=0, *args, **kwargs):
        return self.addMessage(title, text, row, column, colspan, rowspan)

    def addMessage(self, title, text=None, row=None, column=0, colspan=0, rowspan=0):
        ''' adds a message box, to display text across multiple lines '''
        self.widgetManager.verify(WIDGET_NAMES.Message, title)

        if text is None:
            text = title
            gui.trace("Not specifying text for messages (%s) now uses the title for the text. If you want an empty message, pass an empty string ''", title)
        mess = Message(self.getContainer())
        mess.config(text=text)
        mess.config(font=self._getContainerProperty('labelFont'))
        mess.config(justify=LEFT, background=self._getContainerBg())
        mess.DEFAULT_TEXT = text

        if self.platform in [self.MAC, self.LINUX]:
            mess.config(highlightbackground=self._getContainerBg())

        self.widgetManager.add(WIDGET_NAMES.Message, title, mess)

        self._positionWidget(mess, row, column, colspan, rowspan)
#            mess.bind("<Configure>", lambda e: mess.config(width=e.width-10))
        return mess

    def addEmptyMessage(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an empty message box '''
        return self.addMessage(title, "", row, column, colspan, rowspan)

    def setMessage(self, title, text):
        mess = self.widgetManager.get(WIDGET_NAMES.Message, title)
        mess.config(text=text)

    def setMessageAspect(self, title, aspect):
        """ set a new aspect ratio for the text in this widget """
        mess = self.widgetManager.get(WIDGET_NAMES.Message, title)
        mess.config(aspect=aspect)

    def clearMessage(self, title):
        self.setMessage(title, "")

    def getMessage(self, title):
        mess = self.widgetManager.get(WIDGET_NAMES.Message, title)
        return mess.cget("text")

#####################################
# FUNCTIONS for entry boxes
#####################################

    def entry(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets entries all in one go """
        widgKind = WIDGET_NAMES.Entry
        default = kwargs.pop("default", None)
        limit = kwargs.pop("limit", None)
        case = kwargs.pop("case", None)
        rows = kwargs.pop("rows", None)
        secret = kwargs.pop("secret", False)
        kind = kwargs.pop("kind", "standard").lower().strip()
        labBg = kwargs.pop("labBg", None)

        try: self.widgetManager.verify(WIDGET_NAMES.Entry, title)
        except: # widget exists
            if value is not None: self.setEntry(title, value, *args, **kwargs)
            ent = self.getEntry(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            # create the entry widget
            if kind == "auto":
                if value is None: value = []
                ent = self._entryMaker(title, *args, secret=secret, kind=kind, words=value, **kwargs)
            else:
                ent = self._entryMaker(title, *args, secret=secret, kind=kind, **kwargs)
                if not ent: return

        # apply any setter values
        if limit is not None: self.setEntryMaxLength(title, limit)
        if case == "upper": self.setEntryUpperCase(title)
        elif case == "lower": self.setEntryLowerCase(title)

        if default is not None: self.setEntryDefault(title, default)

        if kind != "auto":
            if value is not None: self.setEntry(title, value)
        else:
            if rows is not None: self.setAutoEntryNumRows(title, rows)

        if labBg is not None and self.widgetManager.get(WIDGET_NAMES.Entry, title).isValidation:
            self.setValidationEntryLabelBg(title, labBg)

        # used by file entries
        kwargs.pop("text", None)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return ent

    def setValidationEntryLabelBg(self, title, bg):
        ent = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        if not ent.isValidation:
            raise Exception("You can only set label BGs on validation entries")
        ent.lab.config(bg=bg)

    def _entryMaker(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False, label=False, kind="standard", words=None, **kwargs):
        # used by file entries
        text = kwargs.pop("text", None) 
        default = kwargs.pop("default", None) 

        if not label:
            frame = self.getContainer()
        else:
            frame = self._getLabelBox(title, label=label, **kwargs)

        if kind == "standard":
            ent = self._buildEntry(title, frame, secret)
        elif kind == "numeric":
            ent = self._buildEntry(title, frame, secret)
            if self.validateNumeric is None:
                self.validateNumeric = (self.containerStack[0]['container'].register(
                    self._validateNumericEntry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

            ent.isNumeric = True
            ent.config(validate='key', validatecommand=self.validateNumeric)
            self.setEntryTooltip(title, "Numeric data only.")
        elif kind == "auto":
            ent = self._buildEntry(title, frame, secret=False, words=words)
        elif kind in ["file", "open", "save", "directory"]:
            ent = self._buildFileEntry(title, frame, kind=kind, text=text, default=default)
        elif kind == "validation":
            ent = self._buildValidationEntry(title, frame, secret)
        else:
            raise Exception("Invalid entry kind: %s", kind)

        if not label:
            self._positionWidget(ent, row, column, colspan, rowspan)
        else:
            self._packLabelBox(frame, ent)
            self._positionWidget(frame, row, column, colspan, rowspan)
        return ent

    def addEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False):
        ''' adds an entry box for capturing text '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=secret, label=False, kind="standard")

    def addLabelEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False, label=True):
        ''' adds an entry box for capturing text, with the title as a label '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret, label=label)

    def addSecretEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an entry box for capturing text, where the text is displayed as stars '''
        return self._entryMaker(title, row, column, colspan, rowspan, True)

    def addLabelSecretEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds an entry box for capturing text, where the text is displayed as stars, with the title as a label '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=True, label=label)

    def addSecretLabelEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds an entry box for capturing text, where the text is displayed as stars, with the title as a label '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=True, label=label)

    def addFileEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an entry box with a button, that pops-up a file dialog '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="file")

    def addLabelFileEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds an entry box with a button, that pops-up a file dialog, with a label that displays the title '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="file")

    def addOpenEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an entry box with a button, that pops-up a open dialog '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="open")

    def addLabelOpenEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds an entry box with a button, that pops-up a open dialog, with a label that displays the title '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="open")

    def addSaveEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ''' adds an entry box with a button, that pops-up a save dialog '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="save")

    def addLabelSaveEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        ''' adds an entry box with a button, that pops-up a save dialog, with a label that displays the title '''
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="save")

    def addDirectoryEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="directory")

    def addLabelDirectoryEntry(self, title, row=None, column=0, colspan=0, rowspan=0, label=True):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="directory")

    def addValidationEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="validation")

    def addLabelValidationEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False, label=True):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="validation")

    def addAutoEntry(self, title, words, row=None, column=0, colspan=0, rowspan=0):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=False, kind="auto", words=words)

    def addLabelAutoEntry(self, title, words, row=None, column=0, colspan=0, rowspan=0, secret=False, label=True):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=False, label=label, kind="auto", words=words)

    def addNumericEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=secret, label=False, kind="numeric")

    def addLabelNumericEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False, label=True):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=secret, label=label, kind="numeric")

    def addNumericLabelEntry(self, title, row=None, column=0, colspan=0, rowspan=0, secret=False, label=True):
        return self._entryMaker(title, row, column, colspan, rowspan, secret=secret, label=label, kind="numeric")

    def _getDirName(self, title):
        self._getFileName(title, kind='directory')

    def _getSaveName(self, title):
        self._getFileName(title, kind='save')

    def _getFileName(self, title, kind='open'):
        if kind in ['open', 'file']:
            fileName = self.openBox()
        elif kind == 'save':
            fileName = self.saveBox()
        elif kind == 'directory':
            fileName = self.directoryBox()

        if fileName is not None and fileName != "":
            self.setEntry(title, fileName)

        self.topLevel.after(250, self.setEntryFocus, title)

    def _checkDirName(self, title):
        if len(self.getEntry(title)) == 0:
            self._getFileName(title, kind='directory')

    def _checkSaveName(self, title):
        if len(self.getEntry(title)) == 0:
            self._getFileName(title, kind='save')

    def _checkFileName(self, title):
        if len(self.getEntry(title)) == 0:
            self._getFileName(title, kind='open')

    def _buildEntry(self, title, frame, secret=False, words=[]):
        self.widgetManager.verify(WIDGET_NAMES.Entry, title)
        # if we are an autocompleter
        if len(words) > 0:
            ent = self._makeAutoCompleteEntry()(words, self._getTopLevel(), frame)
        else:
            var = StringVar(self.topLevel)
            ent = entryBase(frame, textvariable=var)
            ent.var = var
            ent.var.auto_id = None

            # for now - suppress UP/DOWN arrows
            if self.platform in [self.MAC]:
                def suppress(event):
                    if event.keysym == "Up":
                        # move home
                        event.widget.icursor(0)
                        event.widget.xview(0)
                        return "break"
                    elif event.keysym == "Down":
                        # move end
                        if not self.ttkFlag:
                            event.widget.icursor(END)
                            event.widget.xview(END)
                        else:
                            event.widget.icursor(END)
                            event.widget.xview(len(event.widget.get()))
                        return "break"

                ent.bind("<Key>", suppress)

        if not self.ttkFlag:
            ent.config(font=self._getContainerProperty('inputFont'))
            if self.platform in [self.MAC, self.LINUX]:
                ent.config(highlightbackground=self._getContainerBg())

        # vars to store any limit traces
        ent.var.uc_id = None
        ent.var.lc_id = None
        ent.var.ml_id = None

        ent.inContainer = False
        ent.showingDefault = False  # current status of entry
        ent.default = ""  # the default value to show (if set)
        ent.DEFAULT_TEXT = ""  # the default value for language support
        ent.myTitle = title  # the title of the entry
        ent.isNumeric = False  # if the entry is numeric
        ent.isValidation = False  # if the entry is validation
        ent.isSecret = False  # if the entry is secret

        # configure it to be secret
        if secret:
            ent.config(show="*")
            ent.isSecret = True

        ent.bind("<Tab>", self._focusNextWindow)
        ent.bind("<Shift-Tab>", self._focusLastWindow)

        # add a right click menu
        self._addRightClickMenu(ent)

        self.widgetManager.add(WIDGET_NAMES.Entry, title, ent)
        self.widgetManager.add(WIDGET_NAMES.Entry, title, ent.var, group=WidgetManager.VARS)
        return ent

    def _buildFileEntry(self, title, frame, kind='save', text=None, default=None):

        vFrame = self._makeButtonBox()(frame)
        self.widgetManager.log(WIDGET_NAMES.FrameBox, vFrame)

        if not self.ttkFlag:
            vFrame.config(background=self._getContainerBg())

        vFrame.theWidget = self._buildEntry(title, vFrame)
        vFrame.theWidget.inContainer = True
        vFrame.theWidget.pack(expand=True, fill=X, side=LEFT)

        if kind in ['open', "file"]:
            command = self.MAKE_FUNC(self._getFileName, title)
            vFrame.theWidget.click_command = self.MAKE_FUNC(self._checkFileName, title)
            if text is None: text = "File"
            if default is None: default = "-- enter a filename --"
        elif kind == 'save':
            command = self.MAKE_FUNC(self._getSaveName, title)
            vFrame.theWidget.click_command = self.MAKE_FUNC(self._checkSaveName, title)
            if text is None: text = "File"
            if default is None: default = "-- enter a filename --"
        else:
            command = self.MAKE_FUNC(self._getDirName, title)
            vFrame.theWidget.click_command = self.MAKE_FUNC(self._checkDirName, title)
            if text is None: text = "Directory"
            if default is None: default = "-- enter a directory --"

        self.setEntryDefault(title, default)
        vFrame.theWidget.bind("<Button-1>", vFrame.theWidget.click_command, "+")

        if not self.ttkFlag:
            vFrame.theButton = Button(vFrame, font=self._getContainerProperty('buttonFont'))
        else:
            vFrame.theButton = ttk.Button(vFrame)

        vFrame.theButton.config(text=text)
        vFrame.theButton.config(command=command)
        vFrame.theButton.pack(side=RIGHT, fill=X)
        vFrame.theButton.inContainer = True
        vFrame.theButton.SKIP_CLEANSE = True
        vFrame.theWidget.but = vFrame.theButton

        if not self.ttkFlag and self.platform in [self.MAC, self.LINUX]:
            vFrame.theButton.config(highlightbackground=self._getContainerBg())

        return vFrame

    def _buildValidationEntry(self, title, frame, secret):
        vFrame = self._makeLabelBox()(frame)
        self.widgetManager.log(WIDGET_NAMES.FrameBox, vFrame)
        vFrame.isValidation = True

        ent = self._buildEntry(title, vFrame, secret)
        if not self.ttkFlag:
            vFrame.config(background=self._getContainerBg())
            ent.config(highlightthickness=2)
        ent.pack(expand=True, fill=X, side=LEFT)
        ent.isValidation = True
        ent.inContainer = True

        class ValidationLabel(labelBase, object):
            def __init__(self, parent, *args, **options):
                super(ValidationLabel, self).__init__(parent, *args, **options)

        lab = ValidationLabel(vFrame)
        lab.pack(side=RIGHT, fill=Y)
        lab.config(font=self._getContainerProperty('labelFont'))
        if not self.ttkFlag:
            lab.config(background=self._getContainerBg())
        lab.inContainer = True
        lab.isValidation = True
        ent.lab = lab

        vFrame.theWidget = ent
        vFrame.theLabel = lab
        self.setEntryWaitingValidation(title)

        return vFrame

    def setEntryValid(self, title):
        self.setValidationEntry(title, "valid")

    def setEntryInvalid(self, title):
        self.setValidationEntry(title, "invalid")

    def setEntryWaitingValidation(self, title):
        self.setValidationEntry(title, "wait")

    def setValidationEntry(self, title, state="valid"):

        entry = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        if not entry.isValidation:
            self.warn("Entry %s is not a validation entry. Unable to set WAITING VALID.", title)
            return

        if state == "wait":
            col = "#000000"
            text = '\u2731'
            eStyle="ValidationEntryWaiting.TEntry"
            lStyle="ValidationEntryWaiting.TLabel"
        elif state == "invalid":
            col = "#FF0000"
            text = '\u2716'
            eStyle="ValidationEntryInvalid.TEntry"
            lStyle="ValidationEntryInvalid.TLabel"
        elif state == "valid":
            col = "#4CC417"
            text = '\u2714'
            eStyle="ValidationEntryValid.TEntry"
            lStyle="ValidationEntryValid.TLabel"
        else:
            self.warn("Invalid validation state: %s", state)
            return

        if not self.ttkFlag:
            if not entry.showingDefault:
                entry.config(fg=col)
            entry.config(highlightbackground=col, highlightcolor=col)
            entry.config(highlightthickness=1)
            entry.lab.config(text=text, fg=col)
            entry.oldFg = col
        else:
            if not entry.showingDefault:
                entry.configure(style=eStyle)
            entry.lab.config(text=text, style=lStyle)
            entry.oldFg = eStyle

        entry.lab.DEFAULT_TEXT = entry.lab.cget("text")

    def appendAutoEntry(self, title, value):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        try:
            entry.addWords(value)
        except AttributeError:
            gui.error("You can only append items to an AutoEntry, %s is not an AutoEntry.", title)

    def removeAutoEntry(self, title, value):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        try:
            entry.removeWord(value)
        except AttributeError:
            gui.error("You can only remove items from an AutoEntry, %s is not an AutoEntry.", title)

    def changeAutoEntry(self, title, value):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        try:
            entry.changeWords(value)
        except AttributeError:
            gui.error("You can only change items in an AutoEntry, %s is not an AutoEntry.", title)

    def setAutoEntryNumRows(self, title, rows):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, title)
        try:
            entry.setNumRows(rows)
        except AttributeError:
            gui.error("You can only change the number of rows in an AutoEntry, %s is not an AutoEntry.", title)

    def _validateNumericEntry(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if action == "1":
            if str(text) in '0123456789.-+':
                try:
                    if len(str(value_if_allowed)) == 1 and str(value_if_allowed) in '.-':
                        return True
                    elif len(str(value_if_allowed)) == 2 and str(value_if_allowed) == '-.':
                        return True
                    else:
                        float(value_if_allowed)
                        return True
                except ValueError:
                    self.containerStack[0]['container'].bell()
                    return False
            else:
                self.containerStack[0]['container'].bell()
                return False
        else:
            return True

    def getEntry(self, name):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, name)
        if entry.showingDefault:
            if entry.isNumeric:
                return None
            else:
                return ""
        else:
            val = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS).get()
            if entry.isNumeric:
                if len(val) == 0 or (len(val) == 1 and val in '.-') or (len(val) == 2 and val == "-."):
                    return None
                else:
                    return float(val)
            else:
                return val

    def getAllEntries(self):
        entries = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Entry):
            entries[k] = self.getEntry(k)
        return entries

    def setEntry(self, name, text, callFunction=True):
        ent = self.widgetManager.get(WIDGET_NAMES.Entry, name)
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        self._updateEntryDefault(name, mode="set")

        # now call function
        with PauseCallFunction(callFunction, var, False):
            if not ent.isNumeric or self._validateNumericEntry("1", None, text, None, "1", None, None, None):
                var.set(text)

    def setEntryMaxLength(self, name, length):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        var.maxLength = length
        if var.ml_id is not None:
            var.trace_vdelete('w', var.ml_id)
        var.ml_id = var.trace('w', self.MAKE_FUNC(self._limitEntry, name))

    def setEntryUpperCase(self, name):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        if var.uc_id is not None:
            var.trace_vdelete('w', var.uc_id)
        var.uc_id = var.trace('w', self.MAKE_FUNC(self._upperEntry, name))

    def setEntryLowerCase(self, name):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        if var.lc_id is not None:
            var.trace_vdelete('w', var.lc_id)
        var.lc_id = var.trace('w', self.MAKE_FUNC(self._lowerEntry, name))

    def _limitEntry(self, name):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        if len(var.get()) > var.maxLength:
            self.containerStack[0]['container'].bell()
            var.set(var.get()[0:var.maxLength])

    def _upperEntry(self, name):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        chars = var.get().upper()
        var.set(chars)

    def _lowerEntry(self, name):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        chars = var.get().lower()
        var.set(chars)

    def _entryIn(self, name):
        self._updateEntryDefault(name, "in")

    def _entryOut(self, name):
        self._updateEntryDefault(name, "out")

    def _updateEntryDefault(self, name, mode=None):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, name)

        # ignore this if no default to apply
        if entry.default == "":
            return

        # disable any limits
        if var.lc_id is not None:
            var.trace_vdelete('w', var.lc_id)
        if var.uc_id is not None:
            var.trace_vdelete('w', var.uc_id)
        if var.ml_id is not None:
            var.trace_vdelete('w', var.ml_id)

        # disable any auto completion
        if var.auto_id is not None:
            var.trace_vdelete('w', var.auto_id)

        current = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS).get()

        # disable any change function
        with PauseCallFunction(False, var, False):

            # clear & remove default
            if mode == "set" or (mode in [ "in", "clear"] and entry.showingDefault):
                var.set("")
                entry.showingDefault = False
                entry.config(justify=entry.oldJustify)
                if not self.ttkFlag:
                    entry.config(foreground=entry.oldFg)
                else:
                    entry.configure(style=entry.oldFg)
                if entry.isSecret:
                    entry.config(show="*")
            elif mode == "out" and (current == "" or entry.showingDefault):
                if entry.isSecret:
                    entry.config(show="")
                var.set(entry.default)
                entry.config(justify='center')
                if not self.ttkFlag:
                    entry.config(foreground='grey')
                else:
                    entry.configure(style="DefaultText.TEntry")

                entry.showingDefault = True
            elif mode == "update" and entry.showingDefault:
                if entry.isSecret:
                    entry.config(show="")
                var.set(entry.default)

        # re-enable any limits
        if var.lc_id is not None:
            var.lc_id = var.trace('w', self.MAKE_FUNC(self._lowerEntry, name))
        if var.uc_id is not None:
            var.uc_id = var.trace('w', self.MAKE_FUNC(self._upperEntry, name))
        if var.ml_id is not None:
            var.ml_id = var.trace('w', self.MAKE_FUNC(self._limitEntry, name))

        # re-enable auto completion
        if var.auto_id is not None:
            var.auto_id = var.trace('w', entry.textChanged)

    def setEntryDefault(self, name, text="default"):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, name)
        self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)

        # remember current settings - to return to
        if not hasattr(entry, "oldJustify"):
            entry.oldJustify = entry.cget('justify')
        if not hasattr(entry, "oldFg"):
            if not self.ttkFlag:
                entry.oldFg = entry.cget('foreground')
            else:
                entry.oldFg = entry.cget("style")

        # configure default stuff
        entry.default = text
        entry.DEFAULT_TEXT = text

        # only show new text if empty
        self._updateEntryDefault(name, "out")

        # bind commands to show/remove the default
        if hasattr(entry, "defaultInEvent"):
            entry.unbind(entry.defaultInEvent)
            entry.unbind(entry.defaultOutEvent)

        in_command = self.MAKE_FUNC(self._entryIn, name)
        out_command = self.MAKE_FUNC(self._entryOut, name)
        entry.defaultInEvent = entry.bind("<FocusIn>", in_command, add="+")
        entry.defaultOutEvent = entry.bind("<FocusOut>", out_command, add="+")

    def clearEntry(self, name, callFunction=True, setFocus=True):
        var = self.widgetManager.get(WIDGET_NAMES.Entry, name, group=WidgetManager.VARS)

        # now call function
        with PauseCallFunction(callFunction, var, False):
            var.set("")

        self._updateEntryDefault(name, mode="clear")
        if setFocus: self.setFocus(name)

    def clearAllEntries(self, callFunction=False):
        for entry in self.widgetManager.group(WIDGET_NAMES.Entry, group=WidgetManager.VARS):
            self.clearEntry(entry, callFunction=callFunction, setFocus=False)

    def setFocus(self, name):
        entry = self.widgetManager.get(WIDGET_NAMES.Entry, name)
        entry.focus_set()

    def getFocus(self):
        widg = self.topLevel.focus_get()
        return self.widgetManager.getName(widg)

####################################
## Functions to get widget details
####################################

    def _lookupValue(self, myDict, val):
        for name in myDict:
            if isinstance(myDict[name], type([])):  # array of cbs
                for rb in myDict[name]:
                    if rb == val:
                        return name
            else:
                if myDict[name] == val:
                    return name
        return None


#####################################
# FUNCTIONS for progress bars (meters)
#####################################

    def meter(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets meters all in one go """
        widgKind = WIDGET_NAMES.Meter
        kind = kwargs.pop("kind","'meter")
        fill = kwargs.pop("fill", None)
        text = kwargs.pop("text", None)

        try: self.widgetManager.verify(WIDGET_NAMES.Meter, title)
        except: # widget exists
            meter =  self.getMeter(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            if kind == "split": meter = self._addMeter(title, "SPLIT", **kwargs)
            elif kind == "dual":  meter = self._addMeter(title, "DUAL", **kwargs)
            else: meter = self._addMeter(title, "METER", **kwargs)

        if value is not None: self.setMeter(title, value, text=text)
        if fill is not None: self.setMeterFill(title, fill)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)

        return meter

    def _addMeter(self, name, kind="METER", row=None, column=0, colspan=0, rowspan=0, **kwargs):
        self.widgetManager.verify(WIDGET_NAMES.Meter, name)

        if kind == "SPLIT":
            meter = SplitMeter(self.getContainer(), font=self._getContainerProperty('labelFont'))
        elif kind == "DUAL":
            meter = DualMeter(self.getContainer(), font=self._getContainerProperty('labelFont'))
        else:
            meter = Meter(self.getContainer(), font=self._getContainerProperty('labelFont'))

        self.widgetManager.add(WIDGET_NAMES.Meter, name, meter)
        self._positionWidget(meter, row, column, colspan, rowspan)
        return meter

    def addMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self._addMeter(name, "METER", row, column, colspan, rowspan)

    def addSplitMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self._addMeter(name, "SPLIT", row, column, colspan, rowspan)

    def addDualMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self._addMeter(name, "DUAL", row, column, colspan, rowspan)

    # update the value of the specified meter
    # note: expects a value between 0 (-100 for split/dual) & 100
    def setMeter(self, name, value=0.0, text=None):
        item = self.widgetManager.get(WIDGET_NAMES.Meter, name)
        item.set(value, text)

    def getMeter(self, name):
        item = self.widgetManager.get(WIDGET_NAMES.Meter, name)
        return item.get()

    def getAllMeters(self):
        meters = {}
        for k in self.widgetManager.group(WIDGET_NAMES.Meter):
            meters[k] = self.getMeter(k)
        return meters

    # a single colour for meters, a list of 2 colours for splits & duals
    def setMeterFill(self, name, colour):
        item = self.widgetManager.get(WIDGET_NAMES.Meter, name)
        item.configure(fill=colour)

#####################################
# FUNCTIONS for seperators
#####################################

    def separator(self, *args, **kwargs):
        """ simpleGUI - adds horizontal/vertical separators """
        direction = kwargs.pop("direction", "horizontal").lower()
        kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)

        if direction == "vertical":
            return self.addVerticalSeparator(*args, **kwargs)
        else:
            return self.addHorizontalSeparator(*args, **kwargs)

    def addHorizontalSeparator(self, row=None, column=0, colspan=0, rowspan=0, colour=None):
        return self._addSeparator("horizontal", row, column, colspan, rowspan, colour)

    def addVerticalSeparator(self, row=None, column=0, colspan=0, rowspan=0, colour=None):
        return self._addSeparator("vertical", row, column, colspan, rowspan, colour)

    def _addSeparator(self, orient, row=None, column=0, colspan=0, rowspan=0, colour=None):
        sep = self._makeSeparator()(self.getContainer(), orient)
        if colour is not None:
            sep.configure(fg=colour)
        self.widgetManager.log(WIDGET_NAMES.Separator, sep)
        self._positionWidget(sep, row, column, colspan, rowspan)
        return sep

#####################################
# FUNCTIONS for pie charts
#####################################
    def pie(self, title, value=None, *args, **kwargs):
        """ simpleGUI - adds, sets & gets pies all in one go """
        widgKind = WIDGET_NAMES.PieChart
        name = kwargs.pop("name", None)

        try: self.widgetManager.verify(widgKind, title)
        except: # widget exists
            if name is not None: self.setPieChart(title, name, value)
            pie = self.getPieChart(title)
        else: # new widget
            kwargs = self._parsePos(kwargs.pop("pos", []), kwargs)
            pie = self.addPieChart(title, value, *args, **kwargs)

        if len(kwargs) > 0:
            self._configWidget(title, widgKind, **kwargs)
        return pie

    def addPieChart(self, name, fracs, row=None, column=0, colspan=0, rowspan=0):
        self.widgetManager.verify(WIDGET_NAMES.PieChart, name)
        self._loadTooltip()
        pie = PieChart(self.getContainer(), fracs, self._getContainerBg())
        self.widgetManager.add(WIDGET_NAMES.PieChart, name, pie)
        self._positionWidget(pie, row, column, colspan, rowspan, sticky=None)
        return pie

    def setPieChart(self, title, name, value):
        pie = self.widgetManager.get(WIDGET_NAMES.PieChart, title)
        pie.setValue(name, value)

#####################################
# FUNCTIONS for toolbar
#####################################
    # adds a list of buttons along the top - like a tool bar...
    def addToolbarButton(self, name, func, findIcon=False):
        self.addToolbar([name], func, findIcon)

    def toolbar(self, names, funcs, **kwargs):
        """ simpleGUI - shortener for toolbar """
        icons = kwargs.pop('icons', kwargs.pop('findIcon', False))
        pinned = kwargs.pop('pinned', None)
        disabled = kwargs.pop('disabled', None)
        hidden = kwargs.pop('hidden', None)
        status = kwargs.pop('status', None)

        bg = kwargs.pop('bg', None)
        if bg is not None:
            self.setToolbarBg(bg)

        self.addToolbar(names, funcs, findIcon=icons is not False)

        # allow status and icon name to be passed in a list
        for x, n in enumerate(names):
            if icons is not None:
                try: self.setToolbarIcon(n, icons[x])
                except: pass
            if status is not None:
                try: self.setToolbarButtonDisabled(n, not status[x])
                except: pass

        if pinned is not None: self.setToolbarPinned(pinned=pinned)
        if disabled is not None: self.setToolbarDisabled(disabled=disabled)
        if hidden is True: self.hideToolbar()

    def addToolbar(self, names, funcs, findIcon=False, **kwargs):
        # hide the toolbarMin bar
        if self.tb.toolbarMin is not None:
            self.tb.toolbarMin.pack_forget()
        # make sure the toolbar is showing
        try:
            self.tb.pack_info()
        except:
            self.tb.location = self.containerStack[0]['container']
            self.tb.pack(before=self.tb.location, side=TOP, fill=X)
        if not self.tb.inUse:
            self.tb.inUse = True

        image = None
        singleFunc = self._checkFunc(names, funcs)
        if not isinstance(names, list):
            names = [names]

        for i in range(len(names)):
            t = names[i]
            if (t in self.widgetManager.group(WIDGET_NAMES.Toolbar)):
                raise Exception(
                    "Invalid toolbar button name: " +
                    t +
                    " already exists")

            if findIcon:
                # turn off warnings about PNGs
                with PauseLogger():
                    imgFile = os.path.join(self.icon_path, t.lower() + ".png")
                    try:
                        image = self._getImage(imgFile)
                    except Exception as e:
                        image = None

            if not self.ttkFlag:
                but = Button(self.tb)
                but.config(relief=FLAT, font=self._buttonFont)
                if gui.GET_PLATFORM() == gui.MAC and self.tb.BG_COLOR is not None:
                    but.config(highlightbackground=self.tb.BG_COLOR)
            else:
                but = ttk.Button(self.tb)
            self.widgetManager.add(WIDGET_NAMES.Toolbar, t, but)

            if singleFunc is not None:
                u = self.MAKE_FUNC(singleFunc, t)
            else:
                u = self.MAKE_FUNC(funcs[i], t)

            but.config(command=u)
            if image is not None:
                # works on Mac & Windows :)
                but.config(image=image)
                but.image = image
                if not self.ttkFlag:
                    but.config(justify=LEFT, compound=TOP)
                else:
                    but.config(style="Toolbar.TButton")
            else:
                but.config(text=t)
            but.pack(side=LEFT, padx=2, pady=2)
            but.tt_var = self._addTooltip(but, t.title(), True)
            but.DEFAULT_TEXT=t

    def _setPinBut(self):

        # only call this once
        if self.tb.pinBut is not None:
            return

        # try to get the icon, if none - then set but to None, and ignore from now on
        imgFile = os.path.join(self.icon_path, "pin.gif")
        try:
            imgObj = self._getImage(imgFile)
            if not self.ttkFlag:
                self.tb.pinBut = Label(self.tb)
                if self.tb.BG_COLOR is not None:
                    self.tb.pinBut.config(bg=self.tb.BG_COLOR)
            else:
                self.tb.pinBut = ttk.Label(self.tb)
                self.tb.pinBut.config(style="Toolbar.TLabel")
        except:
            return

        # if image found, then set up the label
        if self.tb.pinBut is not None:
            self.tb.pinBut.config(image=imgObj)#, compound=TOP, text="", justify=LEFT)
            self.tb.pinBut.image = imgObj  # keep a reference!
            self.tb.pinBut.pack(side=RIGHT, anchor=NE, padx=0, pady=0)

            if gui.GET_PLATFORM() == gui.MAC:
                self.tb.pinBut.config(cursor="pointinghand")
            elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                self.tb.pinBut.config(cursor="hand2")

            self.tb.pinBut.eventId = self.tb.pinBut.bind("<Button-1>", self._toggletb)
            self._addTooltip(self.tb.pinBut, "Click here to pin/unpin the toolbar.", True)

    # called by pinBut, to toggle the pin status of the toolbar
    def _toggletb(self, event=None):
        self.setToolbarPinned(not self.tb.pinned)

    def setToolbarPinned(self, pinned=True):
        self.tb.pinned = pinned
        self._setPinBut()
        if not self.tb.pinned:
            if self.tb.pinBut is not None:
                try:
                    self.tb.pinBut.image = self._getImage(os.path.join(self.icon_path, "unpin.gif"))
                except:
                    pass
            self.tb.makeMinBar()
            self.tb._minToolbar()
        else:
            if self.tb.pinBut is not None:
                try:
                    self.tb.pinBut.image = self._getImage(os.path.join(self.icon_path, "pin.gif"))
                except:
                    pass
            self.tb._maxToolbar()

        if self.tb.pinBut is not None:
            self.tb.pinBut.config(image=self.tb.pinBut.image)

    def setToolbarIcon(self, name, icon):
        if (name not in self.widgetManager.group(WIDGET_NAMES.Toolbar)):
            raise Exception("Unknown toolbar name: " + name)
        imgFile = os.path.join(self.icon_path, icon.lower() + ".png")
        with PauseLogger():
            self.setToolbarImage(name, imgFile)
#        self.widgetManager.get(WIDGET_NAMES.Toolbar, name).tt_var.set(icon)

    def setToolbarBg(self, bg):
        self.tb.BG_COLOR = bg
        if not self.ttkFlag:
            self.tb.config(bg=self.tb.BG_COLOR)
            if gui.GET_PLATFORM() == gui.MAC:
                for name, val in self.widgetManager.group(WIDGET_NAMES.Toolbar).items():
                    val.config(highlightbackground=self.tb.BG_COLOR)
            # config the pin button if exists
            if self.tb.pinBut is not None:
                self.tb.pinBut.config(bg=self.tb.BG_COLOR)
        else:
            self.ttkStyle.configure("Toolbar.TFrame", background=self.tb.BG_COLOR)
            self.ttkStyle.configure("Toolbar.TLabel", background=self.tb.BG_COLOR)

    def setToolbarImage(self, name, imgFile):
        if (name not in self.widgetManager.group(WIDGET_NAMES.Toolbar)):
            raise Exception("Unknown toolbar name: " + name)
        image = self._getImage(imgFile)
        self.widgetManager.get(WIDGET_NAMES.Toolbar, name).config(image=image)
        self.widgetManager.get(WIDGET_NAMES.Toolbar, name).image = image

    def removeToolbarButton(self, name, hide=True):
        if (name not in self.widgetManager.group(WIDGET_NAMES.Toolbar)):
            raise Exception("Unknown toolbar name: " + name)
        self.widgetManager.get(WIDGET_NAMES.Toolbar, name).destroy()
        self.widgetManager.remove(WIDGET_NAMES.Toolbar, name)
        if hide:
            if len(self.widgetManager.group(WIDGET_NAMES.Toolbar)) == 0:
                self.tb.pack_forget()
                self.tb.inUse = False
            if self.tb.toolbarMin is not None:
                self.tb.toolbarMin.pack_forget()

    def removeToolbar(self, hide=True):
        while len(self.widgetManager.group(WIDGET_NAMES.Toolbar)) > 0:
            self.removeToolbarButton(list(self.widgetManager.group(WIDGET_NAMES.Toolbar))[0], hide)

    def setToolbarButtonEnabled(self, name):
        self.setToolbarButtonDisabled(name, False)

    def setToolbarButtonDisabled(self, name, disabled=True):
        if (name not in self.widgetManager.group(WIDGET_NAMES.Toolbar)):
            raise Exception("Unknown toolbar name: " + name)
        if disabled:
            self.widgetManager.get(WIDGET_NAMES.Toolbar, name).config(state=DISABLED)
        else:
            self.widgetManager.get(WIDGET_NAMES.Toolbar, name).config(state=NORMAL)

    def setToolbarEnabled(self):
        self.setToolbarDisabled(False)

    def setToolbarDisabled(self, disabled=True):
        for but in self.widgetManager.group(WIDGET_NAMES.Toolbar).keys():
            if disabled:
                self.widgetManager.get(WIDGET_NAMES.Toolbar, but).config(state=DISABLED)
            else:
                self.widgetManager.get(WIDGET_NAMES.Toolbar, but).config(state=NORMAL)

        if self.tb.pinBut is not None:
            if disabled:
                # this fails if not bound
                if self.tb.pinBut.eventId:
                    self.tb.pinBut.unbind("<Button-1>", self.tb.pinBut.eventId)
                self.tb.pinBut.eventId = None
                self._disableTooltip(self.tb.pinBut)
                self.tb.pinBut.config(cursor="")
            else:
                if gui.GET_PLATFORM() == gui.MAC:
                    self.tb.pinBut.config(cursor="pointinghand")
                elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                    self.tb.pinBut.config(cursor="hand2")

                self.tb.pinBut.eventId = self.tb.pinBut.bind("<Button-1>", self._toggletb)
                self._enableTooltip(self.tb.pinBut)

    # functions to hide & show the toolbar
    def hideToolbar(self):
        self.tb.hide()

    def showToolbar(self):
        self.tb.show()

    # Method to get all inputs.
    def getAllInputs(self, **kwargs):
        """Get all values, merge & return as a single dictionary.

        :param kwargs: will be _appended_ to the input list.

        Note, empty pairs from each input is stripped, existing keys
        will not be overridden!
        """

        # used to stop removal of empty inputs
        includeEmptyInputs = kwargs.pop('includeEmptyInputs', False)

        # All available inputs.
        inputs = filter(None, [
                  self.getAllEntries(),
                  self.getAllOptionBoxes(),
                  self.getAllSpinBoxes(),
                  self.getAllListBoxes(),
                  self.getAllProperties(),
                  self.getAllCheckBoxes(),
                  self.getAllRadioButtons(),
                  self.getAllScales(),
                  self.getAllMeters(),
                  self.getAllDatePickers(),
                  kwargs,
        ])
        result = data = dict()
        for pairs in inputs:
            for key, val in pairs.items():
                # Try and strip values.
                try:
                    val = val.strip()
                except AttributeError:
                    pass
                try:
                    # Skip if value is empty or if key already exists.
                    if (not includeEmptyInputs and not val) or result[key]:
                        continue
                except KeyError:
                    pass
                result[key] = val
        return result

#####################################
# FUNCTIONS for menu bar
#####################################
    def _initMenu(self):
        # create a menu bar - only shows if populated
        if not self.hasMenu:
            #            self.topLevel.option_add('*tearOff', FALSE)
            self.hasMenu = True
            self.menuBar = Menu(self.topLevel)
            if self.platform == self.MAC:
                appmenu = Menu(self.menuBar, name='apple')
                self.menuBar.add_cascade(menu=appmenu)
                self.widgetManager.add(WIDGET_NAMES.Menu, "MAC_APP", appmenu)
            elif self.platform == self.WINDOWS:
                # sysMenu must be added last, otherwise other menus vanish
                sysMenu = Menu(self.menuBar, name='system', tearoff=False)
                self.widgetManager.add(WIDGET_NAMES.Menu, "WIN_SYS", sysMenu)

    # add a parent menu, for menu items
    def createMenu(self, title, tearable=False, showInBar=True):
        self.widgetManager.verify(WIDGET_NAMES.Menu, title)
        self._initMenu()

        if title == "WIN_SYS" and self.platform != self.WINDOWS:
            self.warn("The WIN_SYS menu is specific to Windows")
            return None

        if self.platform == self.MAC and tearable:
            self.warn("Tearable menus (%s) not supported on MAC", title)
            tearable = False
        theMenu = Menu(self.menuBar, tearoff=tearable)
        if showInBar:
            self.menuBar.add_cascade(label=title, menu=theMenu)
        self.widgetManager.add(WIDGET_NAMES.Menu, title, theMenu)
        return theMenu

    def createRightClickMenu(self, title, showInBar=False):
        men = self.createMenu(title, False, showInBar)
        men.bind("<FocusOut>", lambda e: men.unpost())
        return men

    def _bindRightClick(self, item, value):
        if self.platform in [self.WINDOWS, self.LINUX]:
            item.bind('<Button-3>', lambda e, menu=value: self._rightClick(e, menu))
        else:
            item.bind('<Button-2>', lambda e, menu=value: self._rightClick(e, menu))

    # add items to the named menu
    def addMenuItem(self, title, item, func=None, kind=None, shortcut=None, underline=-1, rb_id=None, createBinding=True):
        # set the initial menubar
        self._initMenu()

        # get or create an initial menu
        if title is not None:
            try:
                theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
            except:
                theMenu = self.createMenu(title)
                if theMenu is None:
                    gui.warn('Unable to create menu: %s', title)
                    return

        if underline > -1 and self.platform == self.MAC:
            gui.warn("Underlining menu items not available on MAC")

        if func is not None:
            func = self.MAKE_FUNC(func, item)

        acc = None

        if shortcut is not None:
            if kind == 'cb':
                f = lambda e: self._menuCheckButtonBind(title, item, func)
                binding = EventBinding(shortcut, f, self._getTopLevel(), menuBinding=True)
            else:
                binding = EventBinding(shortcut, func, self._getTopLevel(), menuBinding=True)

            try:
                self.widgetManager.add(WIDGET_NAMES.Bindings, binding.displayName, binding)
                if createBinding: binding.createBindings()
                acc = binding.displayName
            except ItemLookupError:
                raise ItemLookupError('Unable to bind menu ' + item + ' to ' + binding.displayName + ' - binding already exists')

        # now, let's create the actual menu item
        if item == "-" or kind == "separator":
            theMenu.add_separator()
        elif kind == "topLevel" or title is None:
            if self.platform == self.MAC:
                self.warn("Unable to make topLevel menus (%s) on Mac", item)
            else:
                self.menuBar.add_command(
                    label=item, command=func, accelerator=acc, underline=underline)
        elif kind == "rb":
            varName = title + "rb" + item
            newRb = False
            if (varName in self.widgetManager.group(WIDGET_NAMES.Menu, group=WidgetManager.VARS)):
                var = self.widgetManager.get(WIDGET_NAMES.Menu, varName, group=WidgetManager.VARS)
            else:
                newRb = True
                var = StringVar(self.topLevel)
                self.widgetManager.add(WIDGET_NAMES.Menu, varName, var, group=WidgetManager.VARS)
            theMenu.add_radiobutton(label=rb_id, command=func, variable=var, value=rb_id, accelerator=acc, underline=underline)
            if newRb:
                self.setMenuRadioButton(title, item, rb_id)
        elif kind == "cb":
            varName = title + "cb" + item
            self.widgetManager.verify(WIDGET_NAMES.Menu, varName, group=WidgetManager.VARS)
            var = BooleanVar(self.topLevel)
            var.set(False)
            self.widgetManager.add(WIDGET_NAMES.Menu, varName, var, group=WidgetManager.VARS)
            theMenu.add_checkbutton(label=item, command=func, variable=var, onvalue=True, offvalue=False, accelerator=acc, underline=underline)
        elif kind == "sub":
            self.widgetManager.verify(WIDGET_NAMES.Menu, item)
            subMenu = Menu(theMenu, tearoff=False)
            self.widgetManager.add(WIDGET_NAMES.Menu, item, subMenu)
            theMenu.add_cascade(label=item, menu=subMenu)
        else:
            theMenu.add_command(label=item, command=func, accelerator=acc, underline=underline)

    # used to wrap check button bindings, so can also toggle
    def _menuCheckButtonBind(self, title, item, func):
        self.setMenuCheckBox(title, item)
        func(item)

    #################
    # wrappers for other menu types

    def addMenuList(self, menuName, names, funcs):
        # deal with a dict_keys object - messy!!!!
        if not isinstance(names, list):
            names = list(names)

        # append some Nones, if it's a list and contains separators
        if funcs is not None:
            if not callable(funcs):
                seps = names.count("-")
                for i in range(seps):
                    funcs.append(None)
            singleFunc = self._checkFunc(names, funcs)

        # add menu items
        for t in names:
            if funcs is None:
                u = None
            elif singleFunc is not None:
                u = singleFunc
            else:
                u = funcs.pop(0)

            self.addMenuItem(menuName, t, u)

    def _prepareCopyAndPasteMenu(self, event, widget=None):
        if self.copyAndPaste.inUse:
            if event is not None:
                widget = event.widget
            self._changeMenuState(self.widgetManager.get(WIDGET_NAMES.Menu, "EDIT"), DISABLED, 'Disabling', 10)
            self.copyAndPaste.setUp(widget)
            if self.copyAndPaste.canCopy:
                self.enableMenuItem("EDIT", "Copy")
            if self.copyAndPaste.canCut:
                self.enableMenuItem("EDIT", "Cut")
            if self.copyAndPaste.canPaste:
                self.enableMenuItem("EDIT", "Paste")
                self.enableMenuItem("EDIT", "Clear Clipboard")
            if self.copyAndPaste.canSelect:
                self.enableMenuItem("EDIT", "Select All")
                self.enableMenuItem("EDIT", "Clear All")
            if self.copyAndPaste.canUndo:
                self.enableMenuItem("EDIT", "Undo")
            if self.copyAndPaste.canRedo:
                self.enableMenuItem("EDIT", "Redo")
            if self.copyAndPaste.canFont:
                self.enableMenuItem("EDIT", "Bold")
                self.enableMenuItem("EDIT", "Italic")
                self.enableMenuItem("EDIT", "Bold & Italic")
                self.enableMenuItem("EDIT", "Underline")
            return True
        else:
            return False

    # called when copy/paste menu items are clicked
    def _copyAndPasteHelper(self, menu):
        if menu == "Cut":
            self.copyAndPaste.cut()
        elif menu == "Copy":
            self.copyAndPaste.copy()
        elif menu == "Paste":
            self.copyAndPaste.paste()
        elif menu == "Select All":
            self.copyAndPaste.selectAll()
        elif menu == "Clear Clipboard":
            self.copyAndPaste.clearClipboard()
        elif menu == "Clear All":
            self.copyAndPaste.clearText()
        elif menu == "Undo":
            self.copyAndPaste.undo()
        elif menu == "Redo":
            self.copyAndPaste.redo()
        elif menu in ["BOLD", "ITALIC", "UNDERLINE", "BOLD_ITALIC"]:
            self.copyAndPaste.font("AJ_"+menu)

    # add a single entry for a menu
    def addSubMenu(self, menu, subMenu):
        self.addMenuItem(menu, subMenu, func=None, kind="sub")

    def addMenu(self, name, func, shortcut=None, underline=-1):
        self.addMenuItem(None, name, func=func, kind="topLevel", shortcut=shortcut, underline=underline)

    def addMenuSeparator(self, menu):
        self.addMenuItem(menu, "-")

    def addMenuCheckBox(self, menu, name, func=None, shortcut=None, underline=-1):
        self.addMenuItem(menu, name, func, "cb", shortcut, underline)

    def addMenuRadioButton(self, menu, name, value, func=None, shortcut=None, underline=-1):
        self.addMenuItem(menu, name, func, "rb", shortcut, underline, value)

    def menu(self, menu, name=None, func=None, **kwargs):
        # kind: menu, sub, button, sep, check/tick, radio
        kind = kwargs.pop('kind', 'button')
        group = kwargs.pop('group', None)
        shortcut = kwargs.pop('shortcut', None)
        underline = kwargs.pop('underline', -1)

        tear = kwargs.pop('tear', False)
        state = kwargs.pop('state', None)
        image = kwargs.pop('image', None)
        icon = kwargs.pop('icon', None)
        align = kwargs.pop('align', 'left')

        if kind == 'menu':
            self.createMenu(menu, tearable=tear, showInBar=True)
        elif kind.startswith('sub'):
            self.addSubMenu(menu, name)
        elif kind.startswith('radio') or group is not None:
            self.addMenuRadioButton(menu, group, value=name, func=func, shortcut=shortcut, underline=underline)
        elif kind == 'button':
            if name is None and func is not None:
                self.addMenu(menu, func=func, shortcut=shortcut, underline=underline)
            elif name is None:
                self.createMenu(menu, tearable=tear, showInBar=True)
            elif isinstance(name, (list, tuple)):
                self.addMenuList(menu, name, func)
            else:
                self.addMenuItem(menu, name, func=func, kind=None, shortcut=shortcut, underline=underline)
        elif kind.startswith('sep'):
            self.addMenuSeparator(menu)
        elif kind.startswith('check') or kind.startswith('tick'):
            self.addMenuCheckBox(menu, name, func=func, shortcut=shortcut, underline=underline)

        if state is not None:
            if kind == 'menu' or kind.startswith('sub'):
                if state == 'disabled': self.disableMenu(menu, name)
                elif state == 'enabled': self.enableMenu(menu, name)
            else:
                if state == 'disabled': self.disableMenuItem(menu, name)
                elif state == 'enabled': self.enableMenuItem(menu, name)

        if image is not None: self.setMenuImage(menu, name, image, align=align)
        if icon is not None: self.setMenuIcon(menu, name, icon, align=align)

    #################
    # wrappers for setters

    def _setMenu(self, menu, title, value, kind):
        title = menu + kind + title
        var = self.widgetManager.get(WIDGET_NAMES.Menu, title, group=WidgetManager.VARS)
        if kind == "rb":
            var.set(value)
        elif kind == "cb":
            if value is None:
                var.set(not var.get())
            else:
                var.set(value)

    def setMenuCheckBox(self, menu, name, value=None):
        self._setMenu(menu, name, value, "cb")

    def setMenuRadioButton(self, menu, name, value):
        self._setMenu(menu, name, value, "rb")

    # set align = "none" to remove text
    def setMenuImage(self, menu, title, image, align="left"):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, menu)
        imageObj = self._getImage(image)
        if 16 != imageObj.width() or imageObj.width() != imageObj.height():
            self.warn("Invalid image resolution for menu item %s (%s) - should be 16x16", title, image)
            #imageObj = imageObj.subsample(2,2)
        try: theMenu.entryconfigure(title, image=imageObj, compound=align)
        except TclError: gui.error("Unable to set image for menu item: %s, in menu: %s - item not found", title, menu)

    def setMenuIcon(self, menu, title, icon, align="left"):
        image = os.path.join(self.icon_path, icon.lower() + ".png")
        with PauseLogger():
            self.setMenuImage(menu, title, image, align)

    def disableMenubar(self):
        gui.trace('Disabling toplevel menubar')
        self._disableMenu(self.menuBar)

    def enableMenubar(self):
        gui.trace('Enabling toplevel menubar')
        self._enableMenu(self.menuBar)

    def disableMenu(self, title):
        gui.trace('Disabling submenu: %s', title)
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        self._disableMenu(theMenu)

    def enableMenu(self, title):
        gui.trace('Enabling submenu: %s', title)
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        self._enableMenu(theMenu)

    def disableMenuItem(self, title, item):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        try:
            gui.trace("Disabling menu item: %s, in menu: %s", item, title)
            self._changeMenuItemState(theMenu, item, DISABLED) 
        except TclError:
            gui.error("Unable to disable menu item: %s, in menu: %s - item not found", item, title)

    def enableMenuItem(self, title, item):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        try:
            gui.trace("Enabling menu item: %s, in menu: %s", item, title)
            self._changeMenuItemState(theMenu, item, NORMAL) 
        except TclError:
            gui.error("Unable to enable menu item: %s, in menu: %s - item not found", item, title)

    def _disableMenu(self, menu): self._changeMenuState(menu, DISABLED, 'Disabling')
    def _enableMenu(self, menu): self._changeMenuState(menu, NORMAL, 'Enabling')

    def _changeMenuState(self, menu, state, text, limit=None):
        # changes the specified menu object's state to the new state, using the specified text for logging
        numMenus = menu.index("end")
        if numMenus is not None: # MAC_APP (and others?) returns None
            for item in range(numMenus+1):
                # we can cut-off early if requested internally
                if limit is not None and limit == item:
                    break
                if menu.type(item) == 'cascade':
                    label = menu.entrycget(item, 'label')
                    if len(label) == 0: label = 'SPECIAL MENU'
                    gui.trace('%s submenu: %s', text, label)
                    subMenu = self.topLevel.nametowidget(menu.entrycget(item, 'menu'))
                    self._changeMenuState(subMenu, state, text)
                    menu.entryconfig(item, state=state)
                elif menu.type(item) in ['separator', 'tearoff']:
                    gui.trace('Skipping separator/tearoff')
                else:
                    label = menu.entrycget(item, 'label')
                    gui.trace('%s item: %s', text, label)
                    # use the position - if the label is a number it breaks...
                    self._changeMenuItemState(menu, item, state)

    def _changeMenuItemState(self, menu, item, state):
        menu.entryconfigure(item, state=state)
        bindingName = menu.entrycget(item, 'accelerator')
        if bindingName is not None and len(bindingName) > 0:
            self.widgetManager.get(WIDGET_NAMES.Bindings, bindingName).changeBindings(state)

    def renameMenu(self, title, newName):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        try:
            self.menuBar.entryconfigure(title, label=newName)
        except TclError:
            gui.error("Unable to rename menu: %s - item not found", title)

    def renameMenuItem(self, title, item, newName):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        try:
            theMenu.entryconfigure(item, label=newName)
        except TclError:
            gui.error("Unable to rename menu item: %s, in menu: %s - item not found", item, title)

    def deleteMenuItem(self, title, item):
        theMenu = self.widgetManager.get(WIDGET_NAMES.Menu, title)
        try:
            bindingName = theMenu.entrycget(item, 'accelerator')
            theMenu.delete(item)
            self.widgetManager.get(WIDGET_NAMES.Bindings, bindingName).removeBindings()
            self.widgetManager.remove(WIDGET_NAMES.Bindings, bindingName)
        except TclError:
            gui.error("Unable to delete menu item: %s, in menu: %s - item not found", item, title)

    #################
    # wrappers for getters

    def _getMenu(self, menu, title, kind):
        title = menu + kind + title
        var = self.widgetManager.get(WIDGET_NAMES.Menu, title, group=WidgetManager.VARS)
        if kind == 'rb': return var.get()
        else:
            if var.get(): return True
            else: return False

    def getMenuCheckBox(self, menu, title):
        return self._getMenu(menu, title, "cb")

    def getMenuRadioButton(self, menu, title):
        return self._getMenu(menu, title, "rb")

    #################
    # wrappers for platform specific menus

    # enables the preferences item in the app menu
    def addMenuPreferences(self, func):
        if self.platform == self.MAC:
            self._initMenu()
            u = self.MAKE_FUNC(func, "preferences")
            self.topLevel.createcommand('tk::mac::ShowPreferences', u)
        else:
            self.warn("The Preferences Menu is specific to Mac OSX")

    # MAC help menu
    def addMenuHelp(self, func):
        if self.platform == self.MAC:
            self._initMenu()
            helpMenu = Menu(self.menuBar, name='help')
            self.menuBar.add_cascade(menu=helpMenu, label='Help')
            u = self.MAKE_FUNC(func, "help")
            self.topLevel.createcommand('tk::mac::ShowHelp', u)
            self.widgetManager.add(WIDGET_NAMES.Menu, "MAC_HELP", helpMenu)
        else:
            self.warn("The Help Menu is specific to Mac OSX")

    # Shows a Window menu
    def addMenuWindow(self):
        if self.platform == self.MAC:
            self._initMenu()
            windowMenu = Menu(self.menuBar, name='window')
            self.menuBar.add_cascade(menu=windowMenu, label='Window')
            self.widgetManager.add(WIDGET_NAMES.Menu, "MAC_WIN", windowMenu)
        else:
            self.warn("The Window Menu is specific to Mac OSX")

    def disableMenuEdit(self):
        self.copyAndPaste.inUse = False

    # adds an edit menu - by default only as a pop-up
    # if inMenuBar is True - then show in menu too
    def addMenuEdit(self, inMenuBar=False):
        self._initMenu()
        self.copyAndPaste.inUse = True

        # in case we already made the menu - just return
        try: self.widgetManager.verify(WIDGET_NAMES.Menu, "EDIT")
        except: return

        editMenu = Menu(self.menuBar, tearoff=False)
        editMenu.bind("<FocusOut>", lambda e: editMenu.unpost())
        if inMenuBar:
            self.menuBar.add_cascade(menu=editMenu, label='Edit ')
        self.widgetManager.add(WIDGET_NAMES.Menu, "EDIT", editMenu)

        if gui.GET_PLATFORM() == gui.MAC:
            shortcut = "Command-"
        else:
            shortcut = "Control-"

        eList = [
            ('Cut', lambda e: self._copyAndPasteHelper("Cut"), "X", False),
            ('Copy', lambda e: self._copyAndPasteHelper("Copy"), "C", False),
            ('Paste', lambda e: self._copyAndPasteHelper("Paste"), "V", False),
            ('Select All', lambda e: self._copyAndPasteHelper("Select All"), "A", True if gui.GET_PLATFORM() == gui.MAC else False),
            ('Clear Clipboard', lambda e: self._copyAndPasteHelper("Clear Clipboard"), None, False)
            ]

        for (txt, cmd, sc, bind) in eList:
            acc = None if sc is None else shortcut + sc
            self.addMenuItem("EDIT", txt, cmd, shortcut=acc, createBinding=bind)

        # add a clear option
        self.addMenuSeparator("EDIT")
        self.addMenuItem("EDIT", "Clear All", lambda e: self._copyAndPasteHelper("Clear All"))

        self.addMenuSeparator("EDIT")
        self.addMenuItem("EDIT", 'Undo', lambda e: self._copyAndPasteHelper("Undo"), shortcut=shortcut + "Z", createBinding=False)
        self.addMenuItem("EDIT", 'Redo', lambda e: self._copyAndPasteHelper( "Redo"), shortcut=shortcut+"Shift-Z", createBinding=True)

        self.addMenuSeparator("EDIT")
        self.addMenuItem("EDIT", "Bold", lambda e: self._copyAndPasteHelper("BOLD"), shortcut=shortcut+"B")
        self.addMenuItem("EDIT", "Italic", lambda e: self._copyAndPasteHelper("ITALIC"), shortcut=shortcut+"I")
        self.addMenuItem("EDIT", "Underline", lambda e: self._copyAndPasteHelper("UNDERLINE"), shortcut=shortcut+"U")
        self.addMenuItem("EDIT", "Bold & Italic", lambda e: self._copyAndPasteHelper("BOLD_ITALIC"), shortcut=shortcut+"Shift-B")

        self.disableMenu("EDIT")

    def _editMenuSetter(self, enabled=True):
        if enabled:
            self.addMenuEdit()
        else:
            self.disableMenuEdit()

    def _editMenuGetter(self):
        return self.copyAndPaste.inUse

    editMenu = property(_editMenuGetter, _editMenuSetter)

    def appJarAbout(self, menu=None):
        self.infoBox("About appJar",
                        "---\n" +
                        __copyright__ + "\n" +
                        "---\n\t" +
                        gui.SHOW_VERSION().replace("\n", "\n\t") + "\n" +
                        "---\n" +
                        gui.SHOW_PATHS() + "\n" +
                        "---")

    def appJarHelp(self, menu=None):
        self.infoBox("appJar Help", "For help, visit " + __url__)

    def addAppJarMenu(self):
        if self.platform == self.MAC:
            self.addMenuItem("MAC_APP", "About appJar", self.appJarAbout)
            self.addMenuWindow()
            self.addMenuHelp(self.appJarHelp)
        elif self.platform == self.WINDOWS:
            self.addMenuSeparator('WIN_SYS')
            self.addMenuItem("WIN_SYS", "About appJar", self.appJarAbout)
            self.addMenuItem("WIN_SYS", "appJar Help", self.appJarHelp)

#####################################
# FUNCTIONS for status bar
#####################################

    def removeStatusbarField(self, field):
        if self.hasStatus and field < len(self._statusFields):
            self._statusFields[field].pack_forget()
            self._statusFields[field].destroy()
            del self._statusFields[field]
        else:
            raise ItemLookupError("Invalid field number for statusbar: " + str(field))

    def removeStatusbar(self):
        if self.hasStatus:
            while len(self._statusFields) > 0:
                self.removeStatusbarField(0)

            self.statusFrame.pack_forget()
            self.statusFrame.destroy()

            self.hasStatus = False
            self.header = ""

    def status(self, *args, **kwargs):
        self.statusbar(*args, **kwargs)

    def statusbar(self, *args, **kwargs):
        """ simpleGUI - shortener for statusbar """
        bg = kwargs.pop('bg', None)
        fg = kwargs.pop('fg', None)
        width = kwargs.pop('width', None)

        text = kwargs.pop('text', "")
        header = kwargs.pop('header', None)
        fields = kwargs.pop('fields', 1)
        field = kwargs.pop('field', 0)
        side = kwargs.pop('side', None)

        if not self.hasStatus:
            self.addStatusbar(header=header, fields=fields, side=side)
            self.setStatusbar(text=text)
        else:
            if len(args) > 0: text = args[0]
            if len(args) > 1: field = args[1]

            if header is not None: self.setStatusbarHeader(header)
            self.setStatusbar(text=text, field=field)

        if bg is not None: self.setStatusbarBg(bg)
        if fg is not None: self.setStatusbarFg(fg)
        if width is not None: self.setStatusbarWidth(width)

    def addStatusbar(self, header="", fields=1, side=None):
        if not self.hasStatus:
            class Statusbar(Frame, object):
                def __init__(self, master, **kwargs):
                    super(Statusbar, self).__init__(master, **kwargs)

            self.hasStatus = True
            self.header = header
            self.statusFrame = Statusbar(self.appWindow)
            self.statusFrame.config(bd=1, relief=SUNKEN)
            self.statusFrame.pack(side=BOTTOM, fill=X, anchor=S)

            self._statusFields = []
            for i in range(fields):
                self._statusFields.append(Label(self.statusFrame))
                self._statusFields[i].config(
                    bd=1,
                    relief=SUNKEN,
                    anchor=W,
                    font=self._statusFont,
                    width=10)
                self._addTooltip(self._statusFields[i], "Status bar", True)

                if side == "LEFT":
                    self._statusFields[i].pack(side=LEFT)
                elif side == "RIGHT":
                    self._statusFields[i].pack(side=RIGHT)
                else:
                    self._statusFields[i].pack(side=LEFT, expand=1, fill=BOTH)
        else:
            self.error("Statusbar already exists - ignoring")

    def setStatusbarHeader(self, header):
        if self.hasStatus:
            self.header = header

    def setStatusbar(self, text, field=0):
        if self.hasStatus:
            if field is None:
                for status in self._statusFields:
                    status.config(text=self._getFormatStatus(text))
            elif field >= 0 and field < len(self._statusFields):
                self._statusFields[field].config(text=self._getFormatStatus(text))
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self._statusFields) - 1))

    def setStatusbarBg(self, colour, field=None):
        if self.hasStatus:
            if field is None:
                for status in self._statusFields:
                    status.config(background=colour)
            elif field >= 0 and field < len(self._statusFields):
                self._statusFields[field].config(background=colour)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self._statusFields) - 1))

    def setStatusbarFg(self, colour, field=None):
        if self.hasStatus:
            if field is None:
                for status in self._statusFields:
                    status.config(foreground=colour)
            elif field >= 0 and field < len(self._statusFields):
                self._statusFields[field].config(foreground=colour)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self._statusFields) - 1))

    def setStatusbarWidth(self, width, field=None):
        if self.hasStatus:
            if field is None:
                for status in self._statusFields:
                    status.config(width=width)
            elif field >= 0 and field < len(self._statusFields):
                self._statusFields[field].config(width=width)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self._statusFields) - 1))

    def clearStatusbar(self, field=None):
        if self.hasStatus:
            if field is None:
                for status in self._statusFields:
                    status.config(text=self._getFormatStatus(""))
            elif field >= 0 and field < len(self._statusFields):
                self._statusFields[field].config(text=self._getFormatStatus(""))
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self._statusFields) - 1))

    # formats the string shown in the status bar
    def _getFormatStatus(self, text):
        text = str(text)
        if len(text) == 0:
            return ""
        elif self.header is None or len(self.header) == 0:
            return text
        else:
            return self.header + ": " + text

#####################################
# TOOLTIPS
#####################################

    def _addTooltip(self, item, text, hideWarn=False):
        self._loadTooltip()
        if not ToolTip:
            if not hideWarn:
                self.warn("ToolTips unavailable - check tooltip.py is in the lib folder")
        elif text == "":
            self._disableTooltip(item)
        else:
            # turn off warnings about tooltips
            with PauseLogger():
                # if there's already  tt, just change it
                if hasattr(item, "tt_var"):
                    item.tt_var.set(text)
                # otherwise create one
                else:
                    var = StringVar(self.topLevel)
                    var.set(text)
                    tip = ToolTip(item, delay=500, follow_mouse=1, textvariable=var)
                    item.tooltip = tip
                    item.tt_var = var

            return item.tt_var

    def _enableTooltip(self, item):
        if hasattr(item, "tooltip"):
            item.tooltip.configure(state="normal")
        else:
            self.warn("Unable to enable tooltip - none present.")

    def _disableTooltip(self, item):
        if hasattr(item, "tooltip"):
            item.tooltip.configure(state="disabled")
        else:
            self.warn("Unable to disable tooltip - none present.")

#####################################
# FUNCTIONS to show pop-up dialogs
#####################################

    def popUp(self, title, message=None, kind="info", parent=None):
        """ simpleGUI - shortener for the various popUps """

        if message is None:
            message = title
            title = kind.capitalize() + " Dialog"

        if kind == "info": return self.infoBox(title, message, parent)
        elif kind == "error": return self.errorBox(title, message, parent)
        elif kind == "warning": return self.warningBox(title, message, parent)
        elif kind == "yesno": return self.yesNoBox(title, message, parent)
        elif kind == "question": return self.questionBox(title, message, parent)
        elif kind == "ok": return self.okBox(title, message, parent)
        elif kind == "retry": return self.retryBox(title, message, parent)
        elif kind == "string": return self.stringBox(title, message, parent)
        elif kind == "integer": return self.integerBox(title, message, parent)
        elif kind == "float": return self.floatBox(title, message, parent)
        elif kind == "text": return self.textBox(title, message, parent)
        elif kind == "number": return self.numberBox(title, message, parent)
        else: gui.error("Invalid popUp kind: %s, with title: %s", kind, title)

    def prompt(self, title, message, kind="string", parent=None):
        return self.popUp(title, message, kind, parent)

    # function to access the last made pop_up
    def getPopUp(self):
        return self.topLevel.POP_UP

    def infoBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showinfo(title, message)
            if self.topLevel.displayed:
                self._bringToFront()
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            MessageBox.showinfo(title, message, **opts)
            self._bringToFront(parent)


    def errorBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showerror(title, message)
            if self.topLevel.displayed:
                self._bringToFront()
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            MessageBox.showerror(title, message, **opts)
            self._bringToFront(parent)

    def warningBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showwarning(title, message)
            if self.topLevel.displayed:
                self._bringToFront()
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            MessageBox.showwarning(title, message, **opts)
            self._bringToFront(parent)

    def yesNoBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return MessageBox.askyesno(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return MessageBox.askyesno(title=title, message=message, **opts)

    def stringBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return SimpleDialog.askstring(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return SimpleDialog.askstring(title=title, message=message, **opts)

    def integerBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return SimpleDialog.askinteger(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return SimpleDialog.askinteger(title=title, message=message, **opts)

    def floatBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return SimpleDialog.askfloat(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return SimpleDialog.askfloat(title=title, message=message, **opts)

    def questionBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return True if MessageBox.askquestion(title, message).lower() == "yes" else False
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return True if MessageBox.askquestion(title, message, **opts).lower() == "yes" else False

    def okBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        title, message = self._translatePopup(title, message)
        if parent is None:
            return MessageBox.askokcancel(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return MessageBox.askokcancel(title, message, **opts)

    def retryBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return MessageBox.askretrycancel(title, message)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            return MessageBox.askretrycancel(title, message, **opts)

    def openBox(self, title=None, dirName=None, fileTypes=None, asFile=False, parent=None, multiple=False, mode='r'):

        self.topLevel.update_idletasks()

        # define options for opening
        options = {}

        if title is not None:
            options['title'] = title
        if dirName is not None:
            options['initialdir'] = dirName
        if fileTypes is not None:
            options['filetypes'] = fileTypes
        if parent is not None:
            options["parent"] = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)

        if asFile:
            options["mode"] = mode
            if multiple: files = list(filedialog.askopenfiles(**options))
            else: files = filedialog.askopenfile(**options)

            return files
        # will return "" if cancelled
        else:
            if multiple: files = list(self.topLevel.tk.splitlist(filedialog.askopenfilenames(**options)))
            else: files = filedialog.askopenfilename(**options)

            return files

    def saveBox( self, title=None, fileName=None, dirName=None, fileExt=".txt",
            fileTypes=None, asFile=False, parent=None):
        self.topLevel.update_idletasks()
        if fileTypes is None:
            fileTypes = [('all files', '.*'), ('text files', '.txt')]
        # define options for opening
        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = fileTypes
        options['initialdir'] = dirName
        options['initialfile'] = fileName
        options['title'] = title
        if parent is not None:
            options["parent"] = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)

        if asFile:
            return filedialog.asksaveasfile(mode='w', **options)
        # will return "" if cancelled
        else:
            return filedialog.asksaveasfilename(**options)

    def directoryBox(self, title=None, dirName=None, parent=None):
        self.topLevel.update_idletasks()
        options = {}
        options['initialdir'] = dirName
        options['title'] = title
        options['mustexist'] = False
        if parent is not None:
            options["parent"] = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)

        fileName = filedialog.askdirectory(**options)

        if fileName == "":
            return None
        else:
            return fileName

    def colourBox(self, colour='#ff0000', parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            col = askcolor(colour)
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)
            opts = {"parent": parent}
            col = askcolor(colour, **opts)

        if col[1] is None:
            return None
        else:
            return col[1]

    def textBox(self, title="Text Box", question="Enter text", defaultValue=None, parent=None):
        self.topLevel.update_idletasks()
        if defaultValue is not None:
            defaultVar = StringVar(self.topLevel)
            defaultVar.set(defaultValue)
        else:
            defaultVar = None
        if parent is None:
            parent = self.topLevel
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)

        return TextDialog(parent, title, question, defaultVar=defaultVar).result

    def numberBox(self, title="Number Box", question="Enter a number", parent=None):
        return self.numBox(title, question, parent)

    def numBox(self, title="Number Box", question="Enter a number", parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            parent = self.topLevel
        else:
            parent = self.widgetManager.get(WIDGET_NAMES.SubWindow, parent)

        return NumDialog(parent, title, question).result

############################################################################
####     ******* ------ CLASS MAKERS FROM HERE ------ ***********  #########
############################################################################

    #####################################
    # Named classes for containing groups
    #####################################
    def _makeParentBox(self):
        class ParentBox(frameBase, object):

            def __init__(self, parent, **opts):
                super(ParentBox, self).__init__(parent, **opts)
                self.setup()

            def setup(self):
                pass

            # customised config setters
            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def configure(self, cnf=None, **kw):
                # properties to propagate to CheckBoxes
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

                if "bg" in kw:
                    for child in self.winfo_children():
                        gui.SET_WIDGET_BG(child, kw["bg"])

                kw = self.processConfig(kw)

                # propagate anything left
                super(ParentBox, self).config(cnf, **kw)

            def processConfig(self, kw):
                return kw
        return ParentBox

    def _makeLabelBox(self):
        ParentBox = self._makeParentBox()
        class LabelBox(ParentBox):
            def setup(self):
                self.theLabel = None
                self.theWidget = None
        return LabelBox

    def _makeButtonBox(self):
        ParentBox = self._makeParentBox()
        class ButtonBox(ParentBox):
            def setup(self):
                self.theWidget = None
                self.theButton = None
        return ButtonBox

    def _makeWidgetBox(self):
        ParentBox = self._makeParentBox()
        class WidgetBox(ParentBox):
            def setup(self):
                self.theWidgets = []
        return WidgetBox

    def makeListBoxContainer(self):
        ParentBox = self._makeParentBox()
        class ListBoxContainer(Frame, object):

            def __init__(self, parent, **opts):
                super(ListBoxContainer, self).__init__(parent)

            # customised config setters
            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def configure(self, cnf=None, **kw):
                # properties to propagate to CheckBoxes
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
                # propagate anything left
                super(ListBoxContainer, self).config(cnf, **kw)
        return ListBoxContainer

    #####################################
    # Simple Separator
    #####################################
    def _makeSeparator(self):
        class Separator(frameBase, object):

            def __init__(self, parent, orient="horizontal", *args, **options):
                super(Separator, self).__init__(parent, *args, **options)
                self.line = frameBase(self)
                self.line.SKIP_CLEANSE = True
                if orient == "horizontal":
                    self.line.config(relief="ridge", height=2, width=100, borderwidth=1)
                    self.line.pack(padx=5, pady=5, fill="x", expand=1)
                else:
                    self.line.config(relief="ridge", height=100, width=2, borderwidth=1)
                    self.line.pack(padx=5, pady=5, fill="y", expand=1)

            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def configure(self, cnf=None, **kw):
                if "fg" in kw:
                    self.line.config(bg=kw.pop("fg"))

                super(Separator, self).config(cnf, **kw)

        return Separator

    #####################################
    # Drag Grip Label Class
    #####################################

    def _makeGrip(self):
        class Grip(labelBase, object):
            gray25 = BitmapImage(data="""
            #define im_width 16
            #define im_height 16
            static char im_bits[] = {
                0x88, 0x88, 0x22, 0x22, 0x88, 0x88, 0x22, 0x22,
                0x88, 0x88, 0x22, 0x22, 0x88, 0x88, 0x22, 0x22,
                0x88, 0x88, 0x22, 0x22, 0x88, 0x88, 0x22, 0x22,
                0x88, 0x88, 0x22, 0x22, 0x88, 0x88, 0x22, 0x22,
            };
            """)

            def __init__(self, *args, **kwargs):
                super(Grip, self).__init__(image=self.gray25, *args, **kwargs)
                self.config(cursor="fleur", anchor=CENTER)
                self.bind("<ButtonPress-1>", self.StartMove)
                self.bind("<ButtonRelease-1>", self.StopMove)
                self.bind("<B1-Motion>", self.OnMotion)

            def StartMove(self, event):
                self.x = event.x
                self.y = event.y

            def StopMove(self, event):
                self.x = None
                self.y = None

            def OnMotion(self, event):
                parent = self.winfo_toplevel()
                deltax = event.x - self.x
                deltay = event.y - self.y
                x = parent.winfo_x() + deltax
                y = parent.winfo_y() + deltay

                parent.geometry("+%s+%s" % (x, y))
        return Grip

    #####################################
    # Hyperlink Class
    #####################################
    @staticmethod
    def _makeLink():
        class Link(labelBase, object):

            def __init__(self, *args, **kwargs):
                self.useTtk = kwargs.pop('useTtk',False)
                super(Link, self).__init__(*args, **kwargs)
                self.fg = "#0000ff"
                self.overFg="#3366ff"

                if not self.useTtk:
                    self.config(fg=self.fg, takefocus=1)#, highlightthickness=0)
                else:
                    self.config(style="Link.TLabel")

                self.DEFAULT_TEXT = ""

                if gui.GET_PLATFORM() == gui.MAC:
                    self.config(cursor="pointinghand")
                elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                    self.config(cursor="hand2")

                self.bind("<Enter>", self.enter)
                self.bind("<Leave>", self.leave)

            def enter(self, e):
                if self.useTtk:
                    self.config(style="LinkOver.TLabel")
                else:
                    super(Link, self).config(fg=self.overFg)

            def leave(self, e):
                if self.useTtk:
                    self.config(style="Over.TLabel")
                else:
                    super(Link, self).config(fg=self.fg)

            def registerCallback(self, callback):
                self.bind("<Button-1>", callback)
                self.bind("<Return>", callback)
                self.bind("<space>", callback)

            def launchBrowser(self, event):
                webbrowser.open_new(r"" + self.page)
                # webbrowser.open_new_tab(self.page)

            def registerWebpage(self, page):
                if not page.startswith("http"):
                    raise InvalidURLError("Invalid URL: " + page + " (it should begin as http://)")

                self.page = page
                self.bind("<Button-1>", self.launchBrowser)
                self.bind("<Return>", self.launchBrowser)
                self.bind("<space>", self.launchBrowser)

            def config(self, **kw):
                self.configure(**kw)

            def configure(self, **kw):
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
                if "text" in kw:
                    self.DEFAULT_TEXT = kw["text"]
                if 'fg' in kw:
                    self.fg = kw['fg']
                    self.overFg = gui.TINT(self, self.fg)

                super(Link, self).config(**kw)

            def cget(self, option):
                if option == "text" and hasattr(self, 'page'):
                    return self.page

                return super(Link, self).cget(option)

        return Link


    #######################
    # Upgraded scale - http://stackoverflow.com/questions/42843425/change-trough-increment-in-python-tkinter-scale-without-affecting-slider/
    #######################
    def _makeAjScale(self):
        class AjScale(scaleBase, object):
            '''a scale where a trough click jumps by a specified increment instead of the resolution'''
            def __init__(self, master=None, **kwargs):
                self.increment = kwargs.pop('increment',1)
                super(AjScale, self).__init__(master, **kwargs)
                self.bind('<Button-1>', self.jump)

            def jump(self, event):
                clicked = self.identify(event.x, event.y)
                return self._jump(clicked)

            def _jump(self, clicked):
                if clicked == 'trough1':
                    self.set(self.get() - self.increment)
                elif clicked == 'trough2':
                    self.set(self.get() + self.increment)
                else:
                    return None
                return 'break'

        return AjScale

    #####################################
    # appJar Frame
    #####################################

    def _makeAjFrame(self):
        class ajFrame(frameBase, object):
            def __init__(self, parent, *args, **options):
                super(ajFrame, self).__init__(parent, *args, **options)

        return ajFrame

    #########################
    # Class to provide auto-completion on Entry boxes
    # inspired by: https://gist.github.com/uroshekic/11078820
    #########################
    def _makeAutoCompleteEntry(self):
        ### Create the dynamic class
        class AutoCompleteEntry(entryBase, object):

            def __init__(self, words, tl, *args, **kwargs):
                super(AutoCompleteEntry, self).__init__(*args, **kwargs)
                self.allWords = words
                self.allWords.sort()
                self.topLevel = tl

                # store variable - so we can see when it changes
                self.var = self["textvariable"] = StringVar()
                self.var.auto_id = self.var.trace('w', self.textChanged)

                # register events
                self.bind("<Right>", self.selectWord)
                self.bind("<Return>", self.selectWord)
                self.bind("<Up>", self.moveUp)
                self.bind("<Down>", self.moveDown)
                self.bind("<FocusOut>", self.closeList, add="+")
                self.bind("<Escape>", self.closeList, add="+")

                # no list box - yet
                self.listBoxShowing = False
                self.rows = 10

            # customised config setters
            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def configure(self, cnf=None, **kw):
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

                if "font" in kw:
                    self.listFont = kw["font"]

                # propagate anything left
                super(AutoCompleteEntry, self).config(cnf, **kw)

            def removeWord(self, word):
                if word in self.allWords:
                    self.allWords.remove(word)

            def addWords(self, words):
                if not hasattr(words, "__iter__"):
                    words = [words]
                for word in words:
                    if word not in self.allWords:
                        self.allWords.append(word)
                self.allWords.sort()

            def changeWords(self, words):
                self.allWords = words
                self.allWords.sort()

            def setNumRows(self, rows):
                self.rows = rows

            # function to see if words match
            def checkMatch(self, fieldValue, acListEntry):
                pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)

            # function to get all matches as a list
            def getMatches(self):
                return [w for w in self.allWords if self.checkMatch(self.var.get(), w)]

            # called when typed in entry
            def textChanged(self, name, index, mode):
                # if no text - close list
                if self.var.get() == '':
                    self.closeList()
                else:
                    if not self.listBoxShowing:
                        self.makeListBox()
                    self.popListBox()

            # add words to the list
            def popListBox(self):
                if self.listBoxShowing:
                    self.listbox.delete(0, END)
                    shownWords = self.getMatches()
                    if shownWords:
                        for w in shownWords:
                            self.listbox.insert(END, w)
                        self.selectItem(0)

            # function to create & show an empty list box
            def makeListBox(self):
                self.listbox = Listbox(self.topLevel, width=self["width"]-8, height=8)
                self.listbox.config(height=self.rows)
#                self.listbox.config(bg=self.cget("bg"), selectbackground=self.cget("selectbackground"))
#                self.listbox.config(fg=self.cget("fg"))
                if hasattr(self, "listFont"):
                    self.listbox.config(font=self.listFont)
                self.listbox.bind("<Button-1>", self.mouseClickBox)
                self.listbox.bind("<Right>", self.selectWord)
                self.listbox.bind("<Return>", self.selectWord)

                x = self.winfo_rootx() - self.topLevel.winfo_rootx()
                y = self.winfo_rooty() - self.topLevel.winfo_rooty() + self.winfo_height()

                self.listbox.place(x=x, y=y)
                self.listBoxShowing = True

            # function to handle a mouse click in the list box
            def mouseClickBox(self, e=None):
                self.selectItem(self.listbox.nearest(e.y))
                self.selectWord(e)

            # function to close/delete list box
            def closeList(self, event=None):
                if self.listBoxShowing:
                    self.listbox.destroy()
                    self.listBoxShowing = False

            # copy word from list to entry, close list
            def selectWord(self, event):
                if self.listBoxShowing:
                    self.var.set(self.listbox.get(ACTIVE))
                    self.icursor(END)
                    self.closeList()
                return "break"

            # wrappers for up/down arrows
            def moveUp(self, event):
                return self.arrow("UP")

            def moveDown(self, event):
                return self.arrow("DOWN")

            # function for handling up/down keys
            def arrow(self, direction):
                if not self.listBoxShowing:
                    self.makeListBox()
                    self.popListBox()
                    curItem = 0
                    numItems = self.listbox.size()
                else:
                    numItems = self.listbox.size()
                    curItem = self.listbox.curselection()

                    if curItem == ():
                        curItem = -1
                    else:
                        curItem = int(curItem[0])

                    if direction == "UP" and curItem > 0:
                        curItem -= 1
                    elif direction == "UP" and curItem <= 0:
                        curItem = numItems - 1
                    elif direction == "DOWN" and curItem < numItems - 1:
                        curItem += 1
                    elif direction == "DOWN" and curItem == numItems - 1:
                        curItem = 0

                self.selectItem(curItem)

                # stop the event propgating
                return "break"

            # function to select the specified item
            def selectItem(self, position):
                numItems = self.listbox.size()
                self.listbox.selection_clear(0, numItems - 1)
                self.listbox.see(position)  # Scroll!
                self.listbox.selection_set(first=position)
                self.listbox.activate(position)

        # return the dynamic class
        return AutoCompleteEntry

    #####################################
    # Tree Widget Class
    # https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch11s11.html
    # idlelib -> TreeWidget.py
    # https://svn.python.org/projects/python/trunk/Lib/idlelib/TreeWidget.py
    # modify minidom - https://wiki.python.org/moin/MiniDom
    #####################################
    def _makeAjTreeNode(self):
        class AjTreeNode(TreeNode, object):

            def __init__(self, canvas, parent, item):
                super(AjTreeNode, self).__init__(canvas, parent, item)

                self.hasAttr = False
                self.showAttr = False
                self.bgColour = None
                self.fgColour = None
                self.bgHColour = None
                self.fgHColour = None
                # called (if set) when a leaf is edited
                self.editEvent = None

                if self.parent:
                    self.bgColour = self.parent.bgColour
                    self.fgColour = self.parent.fgColour
                    self.bgHColour = self.parent.bgHColour
                    self.fgHColour = self.parent.fgHColour
                    self.editEvent = self.parent.editEvent
                    self.showAttr = self.parent.showAttr
                else:
                    # set this once, in parent
                    self.canvas.menu = None
                    self.canvas.lastSelected = None

                self.menuBound = False

            # customised config setters
            def config(self, cnf=None, **kw):
                self.configure(cnf, **kw)

            def configure(self, cnf=None, **kw):
                # properties to propagate to CheckBoxes
                kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

                if "bg" in kw:
                    self.setBgColour(kw.pop("bg"))
                if "fg" in kw:
                    self.setFgColour(kw.pop("fg"))

#                # propagate anything left
#                super(AjTreeNode, self).config(cnf, **kw)

            # NOT COMPLETE
            def addChild(self, child):
                child = self.__class__(self.canvas, self, child)
                self.children.append(child)
                self.update()

            def registerEditEvent(self, func):
                self.editEvent = func
                for c in self.children:
                    c.registerEditEvent(func)

            def showAttributes(self, show):
                self.showAttr = show
                for c in self.children:
                    c.showAttributes(show)
                self.update()

            def showMenu(self, show):
                if show:
                    if self.canvas.menu is None:
                        self.canvas.menu = Menu(self.canvas, tearoff=0)
                        self.canvas.menu.add_command(label="delete", command=self._delete)
                        self.canvas.menu.bind("<FocusOut>", lambda e: self.canvas.menu.unpost())
                    self._bindMenu()
                else:
                    # need to go through and unbind...
                    pass

            def setBgColour(self, colour):
                self.canvas.config(background=colour)
                self.bgColour = colour
                self._doUpdateColour()

            def setFgColour(self, colour):
                self.fgColour = colour
                self._doUpdateColour()

            def setBgHColour(self, colour):
                self.bgHColour = colour
                self._doUpdateColour()

            def setFgHColour(self, colour):
                self.fgHColour = colour
                self._doUpdateColour()

            def setAllColours(self, bg=None, fg=None, bgH=None, fgH=None):
                if bg is not None:
                    self.canvas.config(background=bg)
                    self.bgColour = bg
                if fg is not None: self.fgColour = fg
                if bgH is not None: self.bgHColour = bgH
                if fgH is not None: self.fgHColour = fgH
                self._doUpdateColour()

            def _doUpdateColour(self):
                self._updateColours(self.bgColour, self.bgHColour, self.fgColour, self.fgHColour)
                self.update()

            def _updateColours(self, bgCol, bgHCol, fgCol, fgHCol):
                self.bgColour = bgCol
                self.fgColour = fgCol
                self.bgHColour = bgHCol
                self.fgHColour = fgHCol
                for c in self.children:
                    c._updateColours(bgCol, bgHCol, fgCol, fgHCol)

            def draw(self, x, y):
                cy = super(AjTreeNode, self).draw(x, y)
                self._bindMenu()
                return cy

            # override parent function, so that we can change the label's background colour
            def drawtext(self):
                attr=self.item.node.attributes
                self.hasAttr = self.showAttr and attr is not None and len(attr) > 0

                if self.hasAttr:
                    self.attrId = self.canvas.create_text(self.x+20-1, self.y-1, anchor="nw", text='*')
                    self.x += 7
                super(AjTreeNode, self).drawtext()
                if self.hasAttr: self.x -= 7
                self.colourLabels()

                # add a tooltip for attributes
                if ToolTip is not False and self.hasAttr:
                    text = "Attributes\n"
                    for key, val in attr.items():
                        text += "  " + key + ":" + val + "\n"
                    text = text[:-1]
                    ToolTip(self.label, text, delay=500, follow_mouse=1)
                    ToolTip(self.canvas, text, specId=self.attrId, delay=500, follow_mouse=1)

            def _bindMenu(self):
                if self.canvas.menu is not None and not self.menuBound:
                    self.menuBound = True
                    if gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                        self.canvas.tag_bind(self.image_id, "<Button-3>", self._showMenu)
                        if self.hasAttr: self.canvas.tag_bind(self.attrId, "<Button-3>", self._showMenu)
                        self.label.bind("<Button-3>", self._showMenu)
                    else:
                        self.canvas.tag_bind(self.image_id, "<Button-2>", self._showMenu)
                        if self.hasAttr: self.canvas.tag_bind(self.attrId, "<Button-2>", self._showMenu)
                        self.label.bind("<Button-2>", self._showMenu)

            # override parent function, so that we can change the label's background colour
            def drawicon(self):
                super(AjTreeNode, self).drawicon()

            def _showMenu(self, event=None):
                self.canvas.lastSelected = event.widget
                self.canvas.menu.focus_set()
                self.canvas.menu.post(event.x_root - 10, event.y_root - 10)
                return "break"

            def _delete(self):
                self.update()
                self.canvas.lastSelected.destroy()

            # override parent function, so that we can generate an event on finish editing
            def edit_finish(self, event=None):
                super(AjTreeNode, self).edit_finish(event)
                if self.editEvent is not None:
                    self.editEvent()

            def colourLabels(self):
                if self.showAttr and self.hasAttr:
                    self.canvas.itemconfigure(self.attrId, fill=self.fgColour)
                try:
                    if not self.selected:
                        self.label.config(background=self.bgColour, fg=self.fgColour)
                    else:
                        self.label.config(background=self.bgHColour, fg=self.fgHColour)
                except:
                    pass

            def getSelectedText(self):
                item = self.getSelected()
                if item is not None:
                    return item.GetText(), item.getAttribute()
                else:
                    return None

            def getSelected(self):
                if self.selected:
                    return self.item
                else:
                    for c in self.children:
                        val = c.getSelected()
                        if val is not None:
                            return val
                    return None

        return AjTreeNode

    def _makeAjTreeData(self):
        # implementation of container for XML data
        # functions implemented as specified in skeleton
        class AjTreeData(TreeItem, object):

            def __init__(self, document):
                # handle root node
                try: self.node = document.documentElement
                except AttributeError: self.node = document

                self.dblClickFunc = None
                self.clickFunc = None
                self.treeTitle = None
                self.canEdit = True

        # REQUIRED FUNCTIONS

            # called whenever the tree expands
            def GetText(self):
                node = self.node
                if node.nodeType == node.ELEMENT_NODE:
                    return node.nodeName
                elif node.nodeType == node.TEXT_NODE:
                    return node.nodeValue

            def getAttribute(self, att='id'):
                try: return self.node.attributes[att].value
                except: return None

            def IsEditable(self):
                return self.canEdit and not self.node.hasChildNodes()

            def SetText(self, text):
                self.node.replaceWholeText(text)

            def IsExpandable(self):
                return self.node.hasChildNodes()

            def GetIconName(self):
                if self.clickFunc is not None:
                    self.clickFunc(self.treeTitle, self.getAttribute())
                if not self.IsExpandable():
                    return "python"  # change to file icon

            def GetSubList(self):
                children = self.node.childNodes
                prelist = [AjTreeData(node) for node in children]
                itemList = [item for item in prelist if item.GetText().strip()]
                for item in itemList:
                    item.registerDblClick(self.treeTitle, self.dblClickFunc)
                    item.registerClick(self.treeTitle, self.clickFunc)
                    item.canEdit = self.canEdit
                return itemList

            def OnDoubleClick(self):
                if self.IsEditable():
                    # TO DO: start editing this node...
                    pass
                if self.dblClickFunc is not None:
                    self.dblClickFunc(self.treeTitle, self.getAttribute())

        #  EXTRA FUNCTIONS

            # TODO: can only set before calling go()
            def setCanEdit(self, value=True):
                self.canEdit = value

            # TODO: can only set before calling go()
            def registerDblClick(self, title, func):
                self.treeTitle = title
                self.dblClickFunc = func

            # TODO: can only set before calling go()
            def registerClick(self, title, func):
                self.treeTitle = title
                self.clickFunc = func

            # not used - for DEBUG
            def getSelected(self, spaces=1):
                if spaces == 1:
                    gui.trace("%s", self.node.tagName)
                for c in self.node.childNodes:
                    if gui.GET_WIDGET_CLASS(c) == "Element":
                        gui.trace("%s >> %s", " "*spaces, c.tagName)
                        node = AjTreeData(c)
                        node.getSelected(spaces + 2)
                    elif gui.GET_WIDGET_CLASS(c) == "Text":
                        val = c.data.strip()
                        if len(val) > 0:
                            gui.trace("%s >>>> %s", " "*spaces, val)
        return AjTreeData

############################################################################
#### ******* ------ CLASS DEFINITIONS FROM HERE ------ *********** #########
############################################################################

#####################################
# appJar OptionMenu
# allows dropDown to be configure at the same time
#####################################
class ajOption(OptionMenu, object):
    def __init__(self, parent, *args, **options):
        super(ajOption, self).__init__(parent, *args, **options)
        self.dropDown = self.nametowidget(self.menuname)
        self.dropDown.configure(font=options.pop('font', None))

    def config(self, **args):
        super(ajOption, self).config(**args)
        self.dropDown.configure(font=args.pop('font', None))

#####################################
# ProgressBar Class
# from: http://tkinter.unpythonic.net/wiki/ProgressMeter
# A gradient fill will be applied to the Meter
#####################################
class Meter(Frame, object):

    def __init__(self, master, width=100, height=20,
            bg='#FFFFFF', fillColour='orchid1',
            value=0.0, text=None, font=None,
            fg='#000000', *args, **kw):

        # call the super constructor
        super(Meter, self).__init__(master, bg=bg,
            width=width, height=height, relief='ridge', bd=3, *args, **kw)

        # remember the starting value
        self._value = value
        self._colour = fillColour
        self._midFill = fg

        # create the canvas
        self._canv = Canvas(self, bg=self['bg'],
            width=self['width'], height=self['height'],
            highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)
        self._canv.SKIP_CLEANSE = True

        # create the text
        width, height = self.getWH(self._canv)
        self._text = self._canv.create_text(
            width / 2, height / 2, text='', fill=fg)

        if font:
            self._canv.itemconfigure(self._text, font=font)

        self.set(value, text)
        self.moveText()

        # bind refresh event
        self.bind('<Configure>', self._update_coords)

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "fill" in kw:
            self._colour = kw.pop("fill")
        if "fg" in kw:
            col = kw.pop("fg")
            self._canv.itemconfigure(self._text, fill=col)
            self._midFill = col
        if "bg" in kw:
            self._canv.config(bg=kw.pop("bg"))

        if "width" in kw:
            self._canv.config(width=kw.pop("width"))
        if "height" in kw:
            self._canv.config(height=kw.pop("height"))
        if "font" in kw:
            self._canv.itemconfigure(self._text, font=kw.pop("fillColour"))

        super(Meter, self).config(cnf, **kw)

        self.makeBar()

    # called when resized
    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas
            when the size of the widget gets changed.'''
        self.makeBar()
        self.moveText()

    # getter
    def get(self):
        val = self._value
        try:
            txt = self._canv.itemcget(self._text, 'text')
        except:
            txt = None
        return val, txt

    # update the variables, then call makeBar
    def set(self, value=0.0, text=None):
        # make the value failsafe:
        value = value / 100.0
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value

        # if no text is specified use the default percentage string:
        if text is None:
            text = str(int(round(100 * value))) + ' %'

        # set the new text
        self._canv.itemconfigure(self._text, text=text)
        self.makeBar()

    # draw the bar
    def makeBar(self):
        width, height = self.getWH(self._canv)
        start = 0
        fin = width * self._value

        self.drawLines(width, height, start, fin, self._value, self._colour)
        self._canv.update_idletasks()

    # move the text
    def moveText(self):
        width, height = self.getWH(self._canv)
        if hasattr(self, "_text"):
            self._canv.coords( self._text, width/2, height/2)

    # draw gradated lines, in given coordinates
    # using the specified colour
    def drawLines(self, width, height, start, fin, val, col, tags="gradient"):
        '''Draw a gradient'''
        # http://stackoverflow.com/questions/26178869/is-it-possible-to-apply-gradient-colours-to-bg-of-tkinter-python-widgets

        # remove the lines & midline
        self._canv.delete(tags)
        self._canv.delete("midline")

        # determine start & end colour
        (r1, g1, b1) = self.tint(col, -30000)
        (r2, g2, b2) = self.tint(col, 30000)

        # determine a direction & range
        if val < 0:
            direction = -1
            limit = int(start - fin)
        else:
            direction = 1
            limit = int(fin - start)

        # if lines to draw
        if limit != 0:
            # work out the ratios
            r_ratio = float(r2 - r1) / limit
            g_ratio = float(g2 - g1) / limit
            b_ratio = float(b2 - b1) / limit

            # loop through the range of lines, in the right direction
            modder = 0
            for i in range(int(start), int(fin), direction):
                nr = int(r1 + (r_ratio * modder))
                ng = int(g1 + (g_ratio * modder))
                nb = int(b1 + (b_ratio * modder))

                colour = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
                self._canv.create_line(
                    i, 0, i, height, tags=(tags,), fill=colour)
                modder += 1
            self._canv.lower(tags)

        # draw a midline
        self._canv.create_line(start, 0, start, height,
            fill=self._midFill, tags=("midline",))

        self._canv.update_idletasks()

    # function to calculate a tint
    def tint(self, col, brightness_offset=1):
        ''' dim or brighten the specified colour by the specified offset '''
        # http://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
        rgb_hex = self._canv.winfo_rgb(col)
        new_rgb_int = [hex_value + brightness_offset for hex_value in rgb_hex]
        # make sure new values are between 0 and 65535
        new_rgb_int = [min([65535, max([0, i])]) for i in new_rgb_int]
        return new_rgb_int

    def getWH(self, widg):
        # ISSUES HERE:
        # on MAC & LINUX, w_width/w_height always 1
        # on WIN, w_height is bigger then r_height - leaving empty space

        self._canv.update_idletasks()

        r_width = widg.winfo_reqwidth()
        r_height = widg.winfo_reqheight()
        w_width = widg.winfo_width()
        w_height = widg.winfo_height()

        max_height = max(r_height, w_height)
        max_width = max(r_width, w_width)

        return (max_width, max_height)


#####################################
# SplitMeter Class extends the Meter above
# Will fill in the empty space with a second fill colour
# Two colours should be provided - left & right fill
#####################################
class SplitMeter(Meter):

    def __init__(self, master, width=100, height=20,
            bg='#FFFFFF', leftfillColour='#FF0000', rightfillColour='#0000FF',
            value=0.0, text=None, font=None, fg='#000000', *args, **kw):

        self._leftFill = leftfillColour
        self._rightFill = rightfillColour

        super(SplitMeter, self).__init__(master, width=width, height=height,
                    bg=bg, value=value, text=text, font=font,
                    fg=fg, *args, **kw)

    # override the handling of fill
    # list of two colours
    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "fill" in kw:
            cols = kw.pop("fill")
            if not isinstance(cols, list):
                raise Exception("SplitMeter requires a list of two colours")
            else:
                self._leftFill = cols[0]
                self._rightFill = cols[1]

        # propagate any left over confs
        super(SplitMeter, self).configure(cnf, **kw)

    def set(self, value=0.0, text=None):
        # make the value failsafe:
        value = value / 100.0
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value
        self.makeBar()

    # override the makeBar function
    def makeBar(self):
        width, height = self.getWH(self._canv)
        mid = width * self._value

        self.drawLines(width, height, 0, mid, self._value, self._leftFill, tags="left")
        self.drawLines(width, height, mid, width, self._value, self._rightFill, tags="right")


#####################################
# SplitMeter Class extends the Meter above
# Used to allow bi-directional metering, starting from a mid point
# Two colours should be provided - left & right fill
# A gradient fill will be applied to the Meter
#####################################
class DualMeter(SplitMeter):

    def __init__(self, master, width=100, height=20, bg='#FFFFFF',
            leftfillColour='#FFC0CB', rightfillColour='#00FF00',
            value=None, text=None,
            font=None, fg='#000000', *args, **kw):

        super(DualMeter, self).__init__(master, width=width, height=height,
                    bg=bg, leftfillColour=leftfillColour,
                    rightfillColour=rightfillColour,
                    value=value, text=text, font=font,
                    fg=fg, *args, **kw)

    def set(self, value=[0,0], text=None):
        if value is None:
            value=[0,0]
        if not hasattr(value, "__iter__"):
            raise Exception("DualMeter.set() requires a list of two arguments")

        # make copy, and reduce to decimal
        vals = [value[0]/100.0, value[1]/100.0]

        # normalise
        if vals[0] < -1: vals[0] = -1.0
        elif vals[0] > 0: vals[0] = vals[0] * -1

        if vals[1] > 1.0: vals[1] = 1.0
        elif vals[1] < 0: vals[1] = 0
        elif vals[1] < -1: vals[1] = -1.0

        self._value = vals

        # if no text is specified use the default percentage string:
        if text is not None:
            # set the new text
            self._canv.itemconfigure(self._text, text=text)

        self.makeBar()

    def makeBar(self):
        # get range to draw lines
        width, height = self.getWH(self._canv)

        start = width / 2
        l_fin = start + (start * self._value[0])
        r_fin = start + (start * self._value[1])

        self.drawLines(width, height, start, l_fin, self._value[0], self._leftFill, tags="left")
        self.drawLines(width, height, start, r_fin, self._value[1], self._rightFill, tags="right")

#####################################
# Properties Widget
#####################################

class Properties(LabelFrame, object):

    def __init__(self, parent, text, props=None, haveLabel=True, *args, **options):

        if haveLabel: theText=text
        else: theText=""

        super(Properties, self).__init__(parent, text=theText, *args, **options)

        self.parent = parent
        self.config(relief="groove")
        self.props = {}
        self.cbs = {}
        self.title = text
        self.cmd = None
        self.changingProps = False
        self.addProperties(props)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        cbVals = ['activebackground', 'activeforeground',
                  'highlightcolor', 'highlightbackground',
                  'indicatoron', 'state', 'selectcolor',
                  'disabledforeground', 'command']
        vals = ["bg", "fg", "font"]

        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        try: kw['selectcolor'] = kw.pop('boxbg')
        except: pass

        # loop through all kw properties received
        for k, v in kw.items():
            if k in vals+cbVals:
                # and set them on all CheckBoxes if desired
                for prop_key in self.cbs:
                    self.cbs[prop_key][k] = v
                    if k == "bg":# and gui.GET_PLATFORM() == gui.LINUX:
                        gui.SET_WIDGET_BG(self.cbs[prop_key], v, True)

        # remove any props the LabelFrame can't handle
        for k in cbVals:
            kw.pop(k, None)

        super(Properties, self).config(cnf, **kw)

    def addProperties(self, props, callFunction=True):

        if props is not None:
            for k in sorted(props):
                self.addProperty(k, props[k], callFunction=False)

        if self.cmd is not None and callFunction:
            self.cmd()

    def renameProperty(self, prop, newName=None):
        if newName is None:
            newName = prop
        if prop in self.cbs:
            self.cbs[prop].config(text=newName)
        else:
            gui.warn("Unknown property: %s", prop)

    def addProperty(self, prop, value=False, callFunction=True):
        self.changingProps = True
        if prop in self.props:
            if value is None:
                del self.props[prop]
                self.cbs[prop].pack_forget()
                del self.cbs[prop]
            else:
                self.props[prop].set(value)
                self.cbs[prop].defaultValue = value
        elif prop is not None:
            var = BooleanVar()
            var.set(value)
            var.trace('w', self._propChanged)
            cb = Checkbutton(self)
            cb.config(
                anchor=W,
                text=prop,
                variable=var,
                bg=self.cget("bg"),
                font=self.cget("font"),
                fg=self.cget("fg"))
            cb.defaultValue = value
            cb.pack(fill="x", expand=1)
            self.props[prop] = var
            self.cbs[prop] = cb
        else:
            self.changingProps = False
            raise Exception("Can't add a None property to: ", prop)
        # if text is not None: lab.config ( text=text )

        if self.cmd is not None and callFunction:
            self.cmd()
        self.changingProps = False

    def _propChanged(self, a,b,c):
        if self.cmd is not None and not self.changingProps:
            self.cmd()

    def getProperties(self):
        vals = {}
        for k, v in self.props.items():
            vals[k] = bool(v.get())
        return vals

    def clearProperties(self, callFunction=False):
        for k, cb in self.cbs.items():
            cb.deselect()

        if self.cmd is not None and callFunction:
            self.cmd()

    def resetProperties(self, callFunction=False):
        for k, cb in self.cbs.items():
            if cb.defaultValue:
                cb.select()
            else:
                cb.deselect()

        if self.cmd is not None and callFunction:
            self.cmd()

    def getProperty(self, prop):
        if prop in self.props:
            return bool(self.props[prop].get())
        else:
            raise Exception("Property: " + str(prop) + " not found in Properties: " + self.title)

    def setChangeFunction(self, cmd):
        self.cmd = cmd

#####################################
# Pie Chart Class
#####################################

class PieChart(Canvas, object):
    # constant for available colours
    COLOURS = [
        "#023fa5", "#7d87b9", "#bec1d4",
        "#d6bcc0", "#bb7784", "#8e063b",
        "#4a6fe3", "#8595e1", "#b5bbe3",
        "#e6afb9", "#e07b91", "#d33f6a",
        "#11c638", "#8dd593", "#c6dec7",
        "#ead3c6", "#f0b98d", "#ef9708",
        "#0fcfc0", "#9cded6", "#d5eae7",
        "#f3e1eb", "#f6c4e1", "#f79cd4"]

    def __init__(self, container, fracs, bg="#00FF00"):
        super(PieChart, self).__init__(container, bd=0, highlightthickness=0, bg=bg)
        self.fracs = fracs
        self.arcs = []
        self._drawPie()
        self.bind("<Configure>", self._drawPie)

    def _drawPie(self, event=None):
        # remove the existing arcs
        for arc in self.arcs:
            self.delete(arc)
        self.arcs = []

        # get the width * height
        w = self.winfo_width()
        h = self.winfo_height()

        # scale h&w - so they don't hit the edges
        min_w = w * .05
        max_w = w * .95
        min_h = h * .05
        max_h = h * .95

        # if we're not in a square
        # adjust them to make sure we get a circle
        if w > h:
            extra = (w * .9 - h * .9) / 2.0
            min_w += extra
            max_w -= extra
        elif h > w:
            extra = (h * .9 - w * .9) / 2.0
            min_h += extra
            max_h -= extra

        coord = min_w, min_h, max_w, max_h

        pos = col = 0
        for key, val in self.fracs.items():
            sliceId = "slice" + str(col)
            arc = self.create_arc(
                coord,
                fill=self.COLOURS[col % len(self.COLOURS)],
                start=self.frac(pos),
                extent=self.frac(val),
                activedash=(3, 5),
                activeoutline="grey",
                activewidth=3,
                tag=(sliceId,),
                width=1)

            self.arcs.append(arc)

            # generate a tooltip
            if ToolTip is not False:
                frac = int(float(val) / sum(self.fracs.values()) * 100)
                tip = key + ": " + str(val) + " (" + str(frac) + "%)"
                tt = ToolTip(self, tip, delay=500, follow_mouse=1, specId=sliceId)

            pos += val
            col += 1

    def frac(self, curr):
        return 360. * curr / sum(self.fracs.values())

    def setValue(self, name, value):
        if value == 0 and name in self.fracs:
            del self.fracs[name]
        else:
            self.fracs[name] = value

        self._drawPie()

#####################################
# errors
#####################################

class ItemLookupError(LookupError):
    '''raise this when there's a lookup error for my app'''
    pass


class InvalidURLError(ValueError):
    '''raise this when there's a lookup error for my app'''
    pass

#####################################
# ToggleFrame - collapsable frame
# http://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
#####################################

class ToggleFrame(Frame, object):

    def __init__(self, parent, title="", *args, **options):
        super(ToggleFrame, self).__init__(parent, *args, **options)

        self.config(relief="raised", borderwidth=2, padx=2, pady=2)
        self.showing = True

        self.titleFrame = Frame(self)
        self.titleFrame.config(bg="DarkGray")
        self.titleFrame.SKIP_CLEANSE = True

        self.titleLabel = Label(self.titleFrame, text=title)
        self.DEFAULT_TEXT = title
        self.titleLabel.config(font="-weight bold")
        self.titleLabel.SKIP_CLEANSE = True

        self.toggleButton = Button(self.titleFrame, width=2, text='-', command=self.toggle)
        self.toggleButton.SKIP_CLEANSE = True

        self.subFrame = Frame(self, relief="sunken", borderwidth=2)
        self.subFrame.SKIP_CLEANSE = True

        self.configure(bg="DarkGray")

        self.grid_columnconfigure(0, weight=1)
        self.titleFrame.grid(row=0, column=0, sticky=EW)
        self.titleFrame.grid_columnconfigure(0, weight=1)
        self.titleLabel.grid(row=0, column=0)
        self.toggleButton.grid(row=0, column=1)
        self.subFrame.grid(row=1, column=0, sticky=EW)
        self.firstTime = True

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "font" in kw:
            self.titleLabel.config(font=kw["font"])
            self.toggleButton.config(font=kw["font"])
            del(kw["font"])
        if "bg" in kw:
            self.titleFrame.config(bg=kw["bg"])
            self.titleLabel.config(bg=kw["bg"])
            self.subFrame.config(bg=kw["bg"])
            if gui.GET_PLATFORM() == gui.MAC:
                self.toggleButton.config(highlightbackground=kw["bg"])
        if "state" in kw:
            if kw["state"] == "disabled":
                if self.showing:
                    self.toggle()
            self.toggleButton.config(state=kw["state"])
            del(kw["state"])

        if "text" in kw:
            self.titleLabel.config(text=kw.pop("text"))

        super(ToggleFrame, self).config(cnf, **kw)


    def cget(self, option):
        if option == "text":
            return self.titleLabel.cget(option)

        return super(ToggleFrame, self).cget(option)

    def toggle(self):
        if not self.showing:
            self.subFrame.grid()
            self.toggleButton.configure(text='-')
        else:
            self.subFrame.grid_remove()
            self.toggleButton.configure(text='+')
        self.showing = not self.showing

    def getContainer(self):
        return self.subFrame

    def stop(self):
        self.update_idletasks()
        self.titleFrame.config(width=self.winfo_reqwidth())
        if self.firstTime:
            self.firstTime = False
            self.toggle()

    def isShowing(self):
        return self.showing

#####################################
# Frame Stack
#####################################
class FrameStack(Frame, object):

    def __init__(self, parent, beep=True, **opts):
        self._change = opts.pop("change", None)
        self._start = opts.pop("start", -1)
        super(FrameStack, self).__init__(parent, **opts)
        # the list of frames
        self._frames = []
        self._prevframe = -1
        self._currFrame = -1
        self._beep = beep

        Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

    def showFrame(self, num, callFunction=True):
        if num < 0 or num >= len(self._frames):
            raise IndexError("The selected frame does not exist")
        tmp = self._prevFrame
        self._prevFrame = self._currFrame
        self._currFrame = num

        if callFunction and self._change is not None:
            if self._change() is False:
                self._currFrame = self._prevFrame
                self._prevFrame = tmp
                return
        self._frames[self._currFrame].lift()

    def atStart(self):
        return self._currFrame == 0

    def atEnd(self):
        return self._currFrame == len(self._frames)-1

    def setStartFrame(self, num):
        self._start = num

    def setChangeFunction(self, func):
        self._change = func

    def showNextFrame(self, callFunction=True):
        if self._currFrame < len(self._frames) - 1:
            self.showFrame(self._currFrame + 1, callFunction)
        else:
            if self._beep: self.bell()

    def showPrevFrame(self, callFunction=True):
        if self._currFrame > 0:
            self.showFrame(self._currFrame - 1, callFunction)
        else:
            if self._beep: self.bell()

    def showFirstFrame(self, callFunction=True):
        if self._currFrame == 0:
            if self._beep: self.bell()
        else:
            self.showFrame(0, callFunction)

    def showLastFrame(self, callFunction=True):
        if self._currFrame == len(self._frames)-1:
            if self._beep: self.bell()
        else:
            self.showFrame(len(self._frames) - 1, callFunction)

    def addFrame(self):
        frame = frameBase(self)
        frame.SKIP_CLEANSE = True
        self._frames.append(frame)
        self._prevFrame = self._currFrame
        self._currFrame = len(self._frames) - 1
        self._frames[self._currFrame].grid(row=0, column=0, sticky=N+S+E+W, padx=0, pady=0)

        if self._start > -1 and self._start < len(self._frames):
            tmp = self._beep
            self._beep = False
            self.showFrame(self._start, callFunction=False)
            self._beep = tmp

        return self._frames[-1]

    def getFrame(self, num=None):
        if num is None: num = self._currFrame
        return self._frames[num]

    def getNumFrames(self):
        return len(self._frames)
    def getCurrentFrame(self):
        return self._currFrame
    def getPreviousFrame(self):
        return self._prevFrame

#####################################
# Paged Window
#####################################

class PagedWindow(Frame, object):

    def __init__(self, parent, title=None, **opts):
        # get the fonts
        buttonFont = opts.pop('buttonFont', None)
        titleFont = opts.pop('titleFont', None)

        # call the super constructor
        super(PagedWindow, self).__init__(parent, **opts)
        self.config(width=300, height=400)

        # globals to hold list of frames(pages) and current page
        self.frameStack = FrameStack(self)
        self.shouldShowPageNumber = True
        self.shouldShowTitle = True
        self.title = title
        self.navPos = 1

        # create the 3 components, including a default container frame
        self.titleLabel = Label(self, font=titleFont)
        self.prevButton = Button(self, text="PREVIOUS", command=self.showPrev, state="disabled", width=10, font=buttonFont)
        self.nextButton = Button(self, text="NEXT", command=self.showNext, state="disabled", width=10, font=buttonFont)
        self.prevButton.bind("<Control-Button-1>", self.showFirst)
        self.nextButton.bind("<Control-Button-1>", self.showLast)
        self.posLabel = Label(self, width=8, font=titleFont)

        # to hide warnings on cleanse
        self.frameStack.SKIP_CLEANSE = True
        self.titleLabel.SKIP_CLEANSE = True
        self.prevButton.SKIP_CLEANSE = True
        self.nextButton.SKIP_CLEANSE = True
        self.posLabel.SKIP_CLEANSE = True

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # grid the navigation components
        self.frameStack.grid(row=int(not self.navPos) + 1, column=0, columnspan=3, sticky=N + S + E + W, padx=5, pady=5)
        self.prevButton.grid(row=self.navPos + 1, column=0, sticky=N + S + W, padx=5, pady=(0, 5))
        self.posLabel.grid(row=self.navPos + 1, column=1, sticky=N + S + E + W, padx=5, pady=(0, 5))
        self.nextButton.grid(row=self.navPos + 1, column=2, sticky=N + S + E, padx=5, pady=(0, 5))

        # show the title
        if self.title is not None and self.shouldShowTitle:
            self.titleLabel.config(text=self.title)
            self.titleLabel.grid(row=0, column=0, columnspan=3, sticky=N + W + E)

        self._updatePageNumber()

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "bg" in kw:
            if gui.GET_PLATFORM() == gui.MAC:
                self.prevButton.config(highlightbackground=kw["bg"])
                self.nextButton.config(highlightbackground=kw["bg"])
            self.posLabel.config(bg=kw["bg"])
            self.titleLabel.config(bg=kw["bg"])
        if "fg" in kw:
            self.posLabel.config(fg=kw["fg"])
            self.titleLabel.config(fg=kw["fg"])
            kw.pop("fg")

        if "prevbutton" in kw:
            self.prevButton.config(text=kw.pop("prevbutton"))

        if "nextbutton" in kw:
            self.nextButton.config(text=kw.pop("nextbutton"))

        if "title" in kw:
            self.title = kw.pop("title")
            self.showTitle()

        if "showtitle" in kw:
            kw.pop("showtitle")

        if "showpagenumber" in kw:
            self.shouldShowPageNumber = kw.pop("showpagenumber")
            self._updatePageNumber()

        if "command" in kw:
            self.registerPageChangeEvent(kw.pop("command"))

        super(PagedWindow, self).config(cnf, **kw)

    # functions to change the labels of the two buttons
    def setPrevButton(self, title):
        self.prevButton.config(text=title)

    def setNextButton(self, title):
        self.nextButton.config(text=title)

    def setNavPositionTop(self, top=True):
        oldNavPos = self.navPos
        pady = (0, 5)
        if top: self.navPos = 0
        else: self.navPos = 1
        if oldNavPos != self.navPos:
            if self.navPos == 0:
                self.grid_rowconfigure(1, weight=0)
                self.grid_rowconfigure(2, weight=1)
                pady = (5, 0)
            else:
                self.grid_rowconfigure(1, weight=1)
                self.grid_rowconfigure(2, weight=0)
            # grid the navigation components
            self.frameStack.grid_remove()
            self.prevButton.grid_remove()
            self.posLabel.grid_remove()
            self.nextButton.grid_remove()

            self.frameStack.grid(row=int(not self.navPos) + 1, column=0, columnspan=3, sticky=N + S + E + W, padx=5, pady=5)
            self.prevButton.grid( row=self.navPos + 1, column=0, sticky=S + W, padx=5, pady=pady)
            self.posLabel.grid( row=self.navPos + 1, column=1, sticky=S + E + W, padx=5, pady=pady)
            self.nextButton.grid( row=self.navPos + 1, column=2, sticky=S + E, padx=5, pady=pady)

    # whether to showPageNumber
    def showPageNumber(self, val=True):
        self.shouldShowPageNumber = val
        self._updatePageNumber()

    def setTitle(self, title):
        self.title = title
        self.showTitle()

    def showTitle(self, val=True):
        self.shouldShowTitle = val
        if self.title is not None and self.shouldShowTitle:
            self.titleLabel.config(text=self.title, font="-weight bold")
            self.titleLabel.grid(row=0, column=0, columnspan=3, sticky=N + W + E)
        else:
            self.titleLabel.grid_remove()

    # function to update the contents of the label
    def _updatePageNumber(self):
        if self.shouldShowPageNumber:
            self.posLabel.config(
                text=str(self.frameStack.getCurrentFrame() + 1) + "/" + str(self.frameStack.getNumFrames()))
        else:
            self.posLabel.config(text="")

        # update the buttons
        if self.frameStack.getNumFrames() == 1:   # only 1 page - no buttons
            self.prevButton.config(state="disabled")
            self.nextButton.config(state="disabled")
        elif self.frameStack.getCurrentFrame() == 0:
            self.prevButton.config(state="disabled")
            self.nextButton.config(state="normal")
        elif self.frameStack.getCurrentFrame() == self.frameStack.getNumFrames() - 1:
            self.prevButton.config(state="normal")
            self.nextButton.config(state="disabled")
        else:
            self.prevButton.config(state="normal")
            self.nextButton.config(state="normal")

    # get current page number
    def getPageNumber(self):
        return self.frameStack.getCurrentFrame() + 1

    # register a function to call when the page changes
    def registerPageChangeEvent(self, event):
        self.frameStack.setChangeFunction(event)

    # adds a new page, making it visible
    def addPage(self):
        f = self.frameStack.addFrame()
        return f

    def stopPagedWindow(self):
        self.showPage(1)


    # function to display the specified page
    def showPage(self, page):
        try:
            self.frameStack.showFrame(page-1)
            self._updatePageNumber()
        except:
            raise Exception("Invalid page number: " + str(page) + ". Must be between 1 and " + str(self.frameStack.getNumFrames()))

    def showFirst(self, event=None):
        self.frameStack.showFirstFrame()
        self._updatePageNumber()

    def showLast(self, event=None):
        self.frameStack.showLastFrame()
        self._updatePageNumber()

    def showPrev(self, event=None):
        self.frameStack.showPrevFrame()
        self._updatePageNumber()

    def showNext(self, event=None):
        self.frameStack.showNextFrame()
        self._updatePageNumber()

class Page(Frame, object):
    def __init__(self, parent, **opts):
        super(Page, self).__init__(parent)
        self.config(relief=RIDGE, borderwidth=2)
        self.container = parent

#########################
# Pane class - used in PanedWindows
#########################

class Pane(Frame, object):

    def __init__(self, parent, **opts):
        super(Pane, self).__init__(parent)
        self.parent = parent

#####################################
# scrollable frame...
# http://effbot.org/zone/tkinter-autoscrollbar.htm
#####################################


class AutoScrollbar(Scrollbar, object):

    def __init__(self, parent, **opts):
        super(AutoScrollbar, self).__init__(parent, **opts)
        self.hidden = None

    # a scrollbar that hides itself if it's not needed
    # only works if you use the grid geometry manager
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
            self.hidden = True
        else:
            self.grid()
            self.hidden = False
        super(AutoScrollbar, self).set(lo, hi)

    def pack(self, **kw):
        raise Exception("cannot use pack with this widget")

    def place(self, **kw):
        raise Exception("cannot use place with this widget")

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "fg" in kw:
            kw.pop("fg")

        # propagate anything left
        super(AutoScrollbar, self).config(cnf, **kw)

#######################
# Widget to give TextArea extra functionality
# http://code.activestate.com/recipes/464635-call-a-callback-when-a-tkintertext-is-modified/
#######################


class TextParent(object):
    def _init(self):
        self.clearModifiedFlag()
        self.bind('<<Modified>>', self._beenModified)
        self.__hash = None
        self.callFunction = True
        self.oldCallFunction = True
        self.TAGS = ["UNDERLINE", "BOLD", "ITALIC", "BOLD_ITALIC"]

        # create default fonts, and assign to tags
        self._normalFont = tkFont.Font(family="Helvetica", size=12, slant="roman", weight="normal")
        self._boldFont = tkFont.Font(family="Helvetica", size=12, weight="bold")
        self._italicFont = tkFont.Font(family="Helvetica", size=12, slant="italic")
        self._boldItalicFont = tkFont.Font(family="Helvetica", size=12, weight="bold", slant="italic")
        self.tag_config("AJ_BOLD", font=self._boldFont)
        self.tag_config("AJ_ITALIC", font=self._italicFont)
        self.tag_config("AJ_BOLD_ITALIC", font=self._boldItalicFont)
        self.tag_config("AJ_UNDERLINE", underline=True)

        self.configure(font=self._normalFont)

    def verifyFontTag(self, tag):
        tag = tag.upper().strip()
        if tag not in self.TAGS:
            raise Exception("Invalid tag: " + tag + ". Must be one of: " + str(self.TAGS))
        else:
            return tag

    def setFont(self, **kwargs):
        """ only looking for size & family params """
        self._normalFont.config(**kwargs)
        self._boldFont.config(**kwargs)
        self._italicFont.config(**kwargs)
        self._boldItalicFont.config(**kwargs)

    def pauseCallFunction(self, callFunction=False):
        self.oldCallFunction = self.callFunction
        self.callFunction = callFunction

    def resumeCallFunction(self):
        self.callFunction = self.oldCallFunction

    def _beenModified(self, event=None):
        # stop recursive calls
        if self._resetting_modified_flag: return
        self.clearModifiedFlag()
        self.beenModified(event)

    def bindChangeEvent(self, function):
        self.function = function

    def beenModified(self, event=None):
        # call the user's function
        if hasattr(self, 'function') and self.callFunction:
            self.function()

    def clearModifiedFlag(self):
        self._resetting_modified_flag = True
        try:
            # reset the modified flag (this raises a modified event!)
            self.tk.call(self._w, 'edit', 'modified', 0)
        finally:
            self._resetting_modified_flag = False

    def getText(self):
        return self.get('1.0', END + '-1c')

    def getTextAreaHash(self):
        text = self.getText()
        m = hashlib.md5()
        if PYTHON2:
            m.update(text)
        else:
            m.update(str.encode(text))
        md5 = m.digest()
#        md5 = hashlib.md5(str.encode(text)).digest()
        return md5

    def highlightPattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        '''Apply the given tag to all text that matches the given pattern
        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit", count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

# uses multiple inheritance
class AjText(Text, TextParent):
    def __init__(self, parent, **opts):
        super(AjText, self).__init__(parent, **opts)
        self._init()    # call TextParent initialiser

class AjScrolledText(scrolledtext.ScrolledText, TextParent):
    def __init__(self, parent, **opts):
        super(AjScrolledText, self).__init__(parent, **opts)
        self._init()    # call TextParent initialiser


#######################
# Widget to look like a label, but allow selection...
#######################

class SelectableLabel(Entry, object):
    def __init__(self, parent, **opts):
        super(SelectableLabel, self).__init__(parent)
        self.configure(relief=FLAT, state="readonly", readonlybackground='#FFFFFF', fg='#000000', highlightthickness=0)
        self.var = StringVar(parent)
        self.configure(textvariable=self.var)
        self.configure(**opts)

    def cget(self, kw):
        if kw == "text":
            return self.var.get()
        else:
            return super(SelectableLabel, self).cget(kw)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "text" in kw:
            self.var.set(kw.pop("text"))

        if "bg" in kw:
            kw["readonlybackground"] = kw.pop("bg")

        # propagate anything left
        super(SelectableLabel, self).config(cnf, **kw)

#######################
# Frame with built in scrollbars and canvas for placing stuff on
# http://effbot.org/zone/tkinter-autoscrollbar.htm
# Modified with help from idlelib TreeWidget.py
#######################

class ScrollPane(frameBase, object):
    def __init__(self, parent, resize=False, disabled=None, **opts):
        super(ScrollPane, self).__init__(parent)
#        self.config(padx=1, pady=1, bd=0)
        self.resize = resize

        self.hDisabled = disabled == "horizontal"
        self.vDisabled = disabled == "vertical"

        # make the ScrollPane expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if not self.vDisabled:
            self.vscrollbar = AutoScrollbar(self)
            opts['yscrollcommand'] = self.vscrollbar.set
            self.vscrollbar.grid(row=0, column=1, sticky=N + S + E)
            self.vscrollbar.SKIP_CLEANSE = True

        if not self.hDisabled:
            self.hscrollbar = AutoScrollbar(self, orient=HORIZONTAL)
            opts['xscrollcommand'] = self.hscrollbar.set
            self.hscrollbar.grid(row=1, column=0, sticky=E + W + S)
            self.hscrollbar.SKIP_CLEANSE = True

        self.canvas = Canvas(self, **opts)
        self.canvas.config(highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.canvas.SKIP_CLEANSE = True

        if not self.vDisabled:
            self.vscrollbar.config(command=self.canvas.yview)
        if not self.hDisabled:
            self.hscrollbar.config(command=self.canvas.xview)

        self.canvas.bind("<Enter>", self._mouseEnter)
        self.canvas.bind("<Leave>", self._mouseLeave)

        self.b_ids = []
        self.canvas.focus_set()

        self.interior = frameBase(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
        self.interior.SKIP_CLEANSE = True

        if self.resize:
            self.canvas.bind('<Configure>', self._updateWidth)
        else:
            self.interior.bind('<Configure>', self._updateWidth)

    def _updateWidth(self, event):
        if self.resize:
            canvas_width = event.width
            if canvas_width == 0:
                canvas_width = self.canvas.winfo_width()

            interior_width = self.interior.winfo_reqwidth()
            if canvas_width < interior_width: canvas_width = interior_width
            self.canvas.itemconfig(self.interior_id, width=canvas_width)
        else:
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)

    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "bg" in kw:
            self.canvas.config(bg=kw["bg"])
            self.interior.config(bg=kw["bg"])

        if "width" in kw:
            self.canvas.config(width=kw["width"])

        if "height" in kw:
            self.canvas.config(height=kw["height"])

        super(ScrollPane, self).configure(**kw)

    # unbind any saved bind ids
    def _unbindIds(self):
        if len(self.b_ids) == 0:
            return

        if gui.GET_PLATFORM() == gui.LINUX:
            self.canvas.unbind("<4>", self.b_ids[0])
            self.canvas.unbind("<5>", self.b_ids[1])
            self.canvas.unbind("<Shift-4>", self.b_ids[2])
            self.canvas.unbind("<Shift-5>", self.b_ids[3])
        else:  # Windows and MacOS
            self.canvas.unbind("<MouseWheel>", self.b_ids[0])
            self.canvas.unbind("<Shift-MouseWheel>", self.b_ids[1])

        self.canvas.unbind("<Key-Prior>", self.b_ids[4])
        self.canvas.unbind("<Key-Next>", self.b_ids[5])
        self.canvas.unbind("<Key-Up>", self.b_ids[6])
        self.canvas.unbind("<Key-Down>", self.b_ids[7])
        self.canvas.unbind("<Key-Left>", self.b_ids[8])
        self.canvas.unbind("<Key-Right>", self.b_ids[9])
        self.canvas.unbind("<Home>", self.b_ids[10])
        self.canvas.unbind("<End>", self.b_ids[11])

        self.b_ids = []

    # bind mouse scroll to this widget only when mouse is over
    def _mouseEnter(self, event):
        self._unbindIds()
        if gui.GET_PLATFORM() == gui.LINUX:
            self.b_ids.append(self.canvas.bind_all("<4>", self._vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<5>", self._vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-4>", self._horizMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-5>", self._horizMouseScroll))
        else:  # Windows and MacOS
            self.b_ids.append(self.canvas.bind_all("<MouseWheel>", self._vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-MouseWheel>", self._horizMouseScroll))
            self.b_ids.append(None)
            self.b_ids.append(None)

        self.b_ids.append(self.canvas.bind_all("<Key-Prior>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Next>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Up>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Down>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Left>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Right>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Home>", self._keyPressed))
        self.b_ids.append(self.canvas.bind_all("<End>", self._keyPressed))

    # remove mouse scroll binding, when mouse leaves
    def _mouseLeave(self, event):
        self._unbindIds()

    def _horizMouseScroll(self, event):
        if not self.hDisabled and not self.hscrollbar.hidden:
            self._mouseScroll(True, event)

    def _vertMouseScroll(self, event):
        if not self.vDisabled and not self.vscrollbar.hidden:
            self._mouseScroll(False, event)

    def _mouseScroll(self, horiz, event):
        direction = 0

        # get direction
        if event.num == 4:
            direction = -1
        elif event.num == 5:
            direction = 1
        elif event.delta > 100:
            direction = int(-1 * (event.delta/120))
        elif event.delta > 0:
            direction = -1 * event.delta
        elif event.delta < -100:
            direction = int(-1 * (event.delta/120))
        elif event.delta < 0:
            direction = -1 * event.delta
        else:
            return  # shouldn't happen

        if horiz:
            self.xscroll(direction, "units")
        else:
            self.yscroll(direction, "units")

    def getPane(self):
        return self.canvas

    def _keyPressed(self, event):
        # work out if alt/ctrl/shift are pressed
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
        state = event.state
        ctrl  = (state & 0x4) != 0
        alt   = (state & 0x8) != 0 or (state & 0x80) != 0 # buggy
        shift = (state & 0x1) != 0

        if event.type == "2":
            # up and down arrows
            if event.keysym == "Up": # event.keycode == 38
                if ctrl:
                    self.yscroll(-1, "pages")
                else:
                    self.yscroll(-1, "units")
            elif event.keysym == "Down": # event.keycode == 40
                if ctrl:
                    self.yscroll(1, "pages")
                else:
                    self.yscroll(1, "units")

            # left and right arrows
            elif event.keysym == "Left": # event.keycode == 37
                if ctrl:
                    self.xscroll(-1, "pages")
                else:
                    self.xscroll(-1, "units")
            elif event.keysym == "Right": # event.keycode == 39
                if ctrl:
                    self.xscroll(1, "pages")
                else:
                    self.xscroll(1, "units")

            # page-up & page-down keys
            elif event.keysym == "Prior": # event.keycode == 33
                if ctrl:
                    self.xscroll(-1, "pages")
                else:
                    self.yscroll(-1, "pages")
            elif event.keysym == "Next": # event.keycode == 34
                if ctrl:
                    self.xscroll(1, "pages")
                else:
                    self.yscroll(1, "pages")

            # home & end keys
            elif event.keysym == "Home": # event.keycode == 36
                if ctrl:
                    self.scrollLeft()
                else:
                    self.scrollTop()
            elif event.keysym == "End": # event.keycode == 35
                if ctrl:
                    self.scrollRight()
                else:
                    self.scrollBottom()

            return "break"
        else:
            pass # shouldn't happen

    def xscroll(self, direction, value=None):
        if not self.hDisabled and not self.hscrollbar.hidden:
            if value is not None: self.canvas.xview_scroll(direction, value)
            else: self.canvas.xview_moveto(direction)

    def yscroll(self, direction, value=None):
        if not self.vDisabled and not self.vscrollbar.hidden:
            if value is not None: self.canvas.yview_scroll(direction, value)
            else: self.canvas.yview_moveto(direction)

    # functions to scroll to the beginning or end
    def scrollLeft(self):
        self.xscroll(0.0)
    def scrollRight(self):
        self.xscroll(1.0)

    def scrollTop(self):
        self.yscroll(0.0)
    def scrollBottom(self):
        self.yscroll(1.0)


#################################
# Additional Dialog Classes
#################################
# the main dialog class to be extended

class Dialog(Toplevel, object):

    def __init__(self, parent, title=None):
        super(Dialog, self).__init__(parent)
        self.transient(parent)
        self.withdraw()
        parent.POP_UP = self

        if title:
            self.title(title)
        self.parent = parent
        self.result = None

        # create a frame to hold the contents
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        # create the buttons
        self.buttonbox()
        gui.SET_LOCATION(x="CENTER", up=150, win=self)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.deiconify()

        self.initial_focus.focus_set()
        self.wait_window(self)

    # override to create the contents of the dialog
    # should return the widget to give focus to
    def body(self, master):
        pass

    # add standard buttons
    # override if you don't want the standard buttons
    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # called when ok button pressed
    def ok(self, event=None):
        # only continue if validate() returns True
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        # call the validate function before calling the cancel function
        self.apply()
        self.cancel()

    # called when cancel button pressed
    def cancel(self, event=None):
        self.grab_release()
        self.parent.focus_set()  # give focus back to the parent
        self.destroy()

    # override this to cancel closing the form
    def validate(self):
        return True

    # override this to do something before closing
    def apply(self):
        pass


class SimpleEntryDialog(Dialog):
    """ a base class for a simple data capture dialog """

    def __init__(self, parent, title, question, defaultvar=None):
        self.error = False
        self.question = question
        self.defaultVar=defaultvar
        super(SimpleEntryDialog, self).__init__(parent, title)

    def clearError(self, e):
        if self.error:
            self.error = False
            self.l1.config(text="")

    def setError(self, message):
        self.parent.bell()
        self.error = True
        self.l1.config(text=message)

    # a label for the question, an entry for the answer
    # a label for an error message
    def body(self, master):
        Label(master, text=self.question).grid(row=0)
        self.e1 = Entry(master)
        if self.defaultVar is not None:
            self.e1.var = self.defaultVar
            self.e1.config(textvariable=self.e1.var)
            self.e1.var.auto_id = None
            self.e1.icursor("end")
        self.l1 = Label(master, fg="#FF0000")
        self.e1.grid(row=1)
        self.l1.grid(row=2)
        self.e1.bind("<Key>", self.clearError)
        return self.e1


class TextDialog(SimpleEntryDialog):
    """ captures a string - must not be empty """

    def __init__(self, parent, title, question, defaultVar=None):
        super(TextDialog, self).__init__(parent, title, question, defaultVar)

    def validate(self):
        res = self.e1.get()
        if len(res.strip()) == 0:
            self.setError("Invalid text.")
            return False
        else:
            self.result = res
            return True

class NumDialog(SimpleEntryDialog):
    """ captures a number - must be a valid float """

    def __init__(self, parent, title, question):
        super(NumDialog, self).__init__(parent, title, question)

    def validate(self):
        res = self.e1.get()
        try:
            self.result = float(res) if '.' in res else int(res)
            return True
        except ValueError:
            self.setError("Invalid number.")
            return False

#####################################
# Toplevel Stuff
#####################################

class SubWindow(Toplevel, object):
    def __init__(self, win, parent, name, title=None, stopFunc=None, modal=False, blocking=False, transient=False, grouped=True):
        super(SubWindow, self).__init__()
        if title is None: title = name
        self.win = self
        self.title(title)
        self._parent = parent
        self.withdraw()
        self.escapeBindId = None  # used to exit fullscreen
        self.stopFunction = None  # used to stop
        self.shown = False
        self.locationSet = False
        self.isFullscreen = False
        self.modal = modal
        self.protocol("WM_DELETE_WINDOW", gui.MAKE_FUNC(stopFunc, name))

        # have this respond to topLevel window style events
        if transient: self.transient(self._parent)

        # group this with the topLevel window
        if grouped: self.group(self._parent)

        self.blocking = blocking
        if self.blocking: self.killLab = None

        self.canvasPane = CanvasDnd(self)
        self.canvasPane.pack(fill=BOTH, expand=True)

    def setLocation(self, x, y):
        x, y = gui.PARSE_TWO_PARAMS(x, y)
        self.geometry("+%d+%d" % (x, y))
        self.locationSet = True

    def hide(self, useStopFunction=False):
        if useStopFunction:
            if self.stopFunction is not None and not self.stopFunction():
                return

        self.withdraw()
        if self.blocking and self.killLab is not None:
            self.killLab.destroy()
            self.killLab = None
        if self.modal:
            self.grab_release()
            self._parent.focus_set()

    def prepDestroy(self):
        if self.stopFunction is None or self.stopFunction():
            if self.blocking and self.killLab is not None:
                self.killLab.destroy()
                self.killLab = None
            self.withdraw()
            self.grab_release()
            self._parent.focus_set()

    def show(self):
        self.shown = True
        if not self.locationSet:
            gui.SET_LOCATION('c', win=self)
            self.locationSet = True
        else:
            gui.trace("Using previous position")

        self.deiconify()
        self.config(takefocus=True)

        # stop other windows receiving events
        if self.modal:
            self.grab_set()
            gui.trace("%s set to MODAL", self.title)

        self.focus_set()

    def block(self):
        # block here - wait for the subwindow to close
        if self.blocking and self.killLab is None:
            gui.trace("%s set to BLOCK", self.title)
            self.killLab = Label(self)
            self._parent.wait_window(self.killLab)

#####################################
# SimpleTable Stuff
#####################################

class GridCell(Label, object):
    def __init__(self, parent, fonts, isHeader=False, wrap=0, **opts):
        super(GridCell, self).__init__(parent, **opts)
        self.selected = False
        self.isHeader = isHeader
        self.config(borderwidth=1, highlightthickness=0, padx=0, pady=0, wraplength=wrap)
        self.updateFonts(fonts)

        if not self.isHeader:
            self.bind("<Enter>", self.mouseEnter)
            self.bind("<Leave>", self.mouseLeave)
            self.bind("<Button-1>", self.toggleSelection)

    def updateFonts(self, fonts):
        self.fonts = fonts
        if self.isHeader:
            self.config(font=self.fonts["headerFont"], background=self.fonts["headerBg"], fg=self.fonts['headerFg'], relief=self.fonts['border'])
        else:
            if self.selected:
                self.config(font=self.fonts["dataFont"], background=self.fonts["selectedBg"], fg=self.fonts['selectedFg'], relief=self.fonts['border'])
            else:
                self.config(font=self.fonts["dataFont"], background=self.fonts["inactiveBg"], fg=self.fonts['inactiveFg'], relief=self.fonts['border'])

    def setText(self, text):
        self.config(text=text)

    def clear(self):
        self.config(text="")

    def mouseEnter(self, event=None):
        self.config(background=self.fonts["overBg"], fg=self.fonts["overFg"])

    def mouseLeave(self, event=None):
        if self.selected:
            self.config(background=self.fonts["selectedBg"], fg=self.fonts["selectedFg"])
        else:
            self.config(background=self.fonts["inactiveBg"], fg=self.fonts["inactiveFg"])

    def select(self):
        self.config(background=self.fonts["selectedBg"], fg=self.fonts["selectedFg"])
        self.selected = True

    def deselect(self):
        self.config(background=self.fonts["inactiveBg"], fg=self.fonts["inactiveFg"])
        self.selected = False

    def toggleSelection(self, event=None):
        if self.selected:
            self.deselect()
        else:
            self.select()

# first row is used as a header
# SimpleTable is a ScrollPane, where a Frame has been placed on the canvas - called GridContainer
class SimpleTable(ScrollPane):

    def __init__(self, parent, title, data, action=None, addRow=None,
                    actionHeading="Action", actionButton="Press",
                    addButton="Add", showMenu=False, queueFunction=None, border='solid', **opts):

        self.title = title
        self.fonts = {
            "dataFont": tkFont.Font(family="Arial", size=11),
            "headerFont": tkFont.Font(family="Arial", size=13, weight='bold'),
            "buttonFont": tkFont.Font(family="Arial", size=10),
            "headerBg": "#6e7274",
            "headerFg": "#FFFFFF",
            "selectedBg": "#D3D3D3",
            "selectedFg": "#000000",
            "inactiveBg": "#FFFFFF",
            "inactiveFg":"#000000",
            "overBg": "#E0E9EE",
            "overFg": "#000000",
            "border": border.lower()
        }

        super(SimpleTable, self).__init__(parent, resize=True, **{})

        # actions
        self.addRowEntries = addRow
        self.action = action
        self.queueFunction = queueFunction
        self.changeFunction = opts.pop("change", None)
        self.editFunction = opts.pop("edit", None)

        # lists to store the data in
        self.cells = []
        self.entries = []
        self.entryProps = []
        self.rightColumn = []

        # database stuff
        self.db = None
        self.dbTable = None

        # to wrap text in cells
        self.wrap = opts.pop("wrap", 0)
        # how do we align buttons in the action box?
        self.horizontalButtons = opts.pop("horizontal", True)

        self.config(**opts)

        # menu stuff
        self.showMenu = showMenu
        self.lastSelected = None
        self.lastAction = None
        self.newText = None
        if self.showMenu: self._buildMenu()

        # how many rows & columns
        self.numColumns = 0
        # find out the max number of cells in a row
        if sqlite3 is not None and sqlite3 is not False and isinstance(data, sqlite3.Cursor):
            self.numColumns = len([description[0] for description in data.description])
        else:
            self.numColumns = len(max(data, key=len))

        # headings
        self.actionHeading = actionHeading
        if type(actionButton) in (list, tuple):
            self.actionButton = actionButton
        else:
            self.actionButton = [actionButton]

        self.addButton= addButton

        # add the grid container to the frame
        self.interior.bind("<Configure>", self._refreshGrids)

        gui.trace("SimpleTable %s constructed, adding rows", title)
        self.addRows(data, scroll=False)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        updateCells = False

        if "disabledentries" in kw:
            entries = kw.pop("disabledentries")
            list(map(self.disableEntry, entries))

        if "change" in kw:
            self.changeFunction = kw.pop("change")

        if "edit" in kw:
            self.editFunction = kw.pop("edit")

        if "bg" in kw:
            bg = kw.pop("bg")
            self.canvas.config(bg=bg)
            self.interior.config(bg=bg)

        if "activebg" in kw or "activebackground" in kw:
            self.fonts["selectedBg"] = kw.pop("activebg", kw.pop("activebackground", self.fonts['selectedBg']))
            updateCells = True
        if "activefg" in kw or "activeforeground" in kw:
            self.fonts["selectedFg"] = kw.pop("activefg", kw.pop("activeforeground", self.fonts['selectedFg']))
            updateCells = True

        if "inactivebg" in kw or "inactivebackground" in kw:
            self.fonts["inactiveBg"] = kw.pop("inactivebg", kw.pop("inactivebackground", self.fonts['inactiveBg']))
            updateCells = True
        if "inactivefg" in kw or "inactiveforeground" in kw:
            self.fonts["inactiveFg"] = kw.pop("inactivefg", kw.pop("inactiveforeground", self.fonts['inactiveFg']))
            updateCells = True

        if "font" in kw:
            font = kw.pop("font")
            self.fonts["headerFont"].configure(family=font.actual("family"), size=font.actual("size") + 2, weight="bold")
            updateCells = True

        if "buttonfont" in kw:
            buttonFont = kw.pop("buttonfont")
            self.fonts["buttonFont"].configure(family=buttonFont.actual("family"), size=buttonFont.actual("size")-2)
            updateCells = True

        if "border" in kw:
            self.fonts["border"]=kw.pop("border").lower().strip()
            updateCells = True

        if updateCells: self._configCells()

        # allow labels to be updated
        if "actionheading" in kw:
            self.actionHeading = kw.pop("actionheading")
            if len(self.rightColumn) > 0:
                self.rightColumn[0].config(text=self.actionHeading)
        if "actionbutton" in kw:
            self.actionButton = kw.pop("actionbutton")
            if len(self.rightColumn) > 1:
                for pos in range(1, len(self.rightColumn)):
                    self.rightColumn[pos].config(text=self.actionButton)
        if "addbutton" in kw:
            self.addButton = kw.pop("addbutton")
            self.ent_but.config(text=self.addButton)

        super(SimpleTable, self).configure(**kw)

    def setChangeFunction(self, func):
        self.changeFunction = func

    def setEditFunction(self, func):
        self.editFunction = func

    def _configCells(self):
        gui.trace("Config all cells")
        for row in self.cells:
            for cell in row:
                gui.trace("Update Fonts: %s, %s", row, cell)
                cell.updateFonts(self.fonts)

    def addRow(self, rowData, scroll=True):
        self.queueFunction(self._hideEntryBoxes)
        self.queueFunction(self._addRow, rowData)
        self.queueFunction(self._showEntryBoxes)
        self.queueFunction(self.canvas.event_generate, "<Configure>")
        if scroll:
            self.queueFunction(self.scrollBottom)

    def addRows(self, data, scroll=True):
        self._hideEntryBoxes()
        if self.numColumns == -1:
            if sqlite3 is not None and sqlite3 is not False and isinstance(data, sqlite3.Cursor):
                gui.trace('No header exists, using cursor description as header')
                self.numColumns = len([description[0] for description in data.description])
                self._addRow([description[0] for description in data.description])
            else:
                gui.trace('No header exists, using first row of data as header')
                self.numColumns = len(data[0])

        try: gui.trace("Adding %s rows in addRows()", len(data))
        except: gui.trace("Adding cursor in addRows()")
        list(map(self._addRow, data))
        self._showEntryBoxes()
        self.canvas.event_generate("<Configure>")
        if scroll:
            self.scrollBottom()

    # this will include the header row
    def getRowCount(self):
        return len(self.cells)-1

    def getRow(self, rowNumber):
        if 0 > rowNumber >= len(self.cells):
            raise Exception("Invalid row number.")
        else:
            data = []
            for cell in self.cells[rowNumber+1]:
                data.append(str(cell.cget('text')))
            return data

    def setHeaders(self, data):
        if sqlite3 is not None and sqlite3 is not False and isinstance(data, sqlite3.Cursor):
            data = [description[0] for description in data.description]

        cellsLen = len(self.cells[0])
        newCols = len(data) - cellsLen
        if newCols > 0:
            for pos in range(cellsLen, cellsLen + newCols):
                self.addColumn(pos, [])
        elif newCols < 0:
            for pos in range(newCols*-1):
                cellsLen = len(self.cells[0])
                self.deleteColumn(cellsLen-1)

        dataLen = len(data)
        cellsLen = len(self.cells[0])
        for count in range(cellsLen):
            cell = self.cells[0][count]
            if count < dataLen:
                cell.setText(data[count])
            else:
                cell.clear()

    def replaceRow(self, rowNum, data):
        if 0 > rowNum >= len(self.cells):
            raise Exception("Invalid row number.")
        else:
            dataLen = len(data)
            for count in range(len(self.cells[rowNum+1])):
                cell = self.cells[rowNum+1][count]
                if count < dataLen:
                    cell.setText(data[count])
                else:
                    cell.clear()
            self.canvas.event_generate("<Configure>")

    def deleteAllRows(self, deleteHeader=False):
        if deleteHeader:
            end = -2
            gui.trace('Deleting %s rows', len(self.cells))
        else:
            end = -1
            gui.trace('Deleting %s rows', len(self.cells)-1)
        list(map(self._quickDeleteRow, range(len(self.cells)-2, end, -1)))
        self.canvas.event_generate("<Configure>")
        self._deleteEntryBoxes()
        self.numColumns = -1

    def _quickDeleteRow(self, position):
        self.deleteRow(position, True)

    def deleteRow(self, position, pauseUpdate=False, callFunction=False):
        if 0 > position >= len(self.cells):
            raise Exception("Invalid row number.")
        else:
            # forget the specified row & button
            for cell in self.cells[position+1]:
                cell.grid_forget()
            if self.action is not None:
                self.rightColumn[position+1].grid_forget()

            # loop through all rows after, forget them, move them, grid them
            butCount = len(self.actionButton)
            for loop in range(position+1, len(self.cells)-1):
                # forget the next row
                for cell in self.cells[loop+1]:
                    cell.grid_forget()

                # move data
                self.cells[loop] = self.cells[loop+1]

                # add its button
                if self.action is not None:
                    self.rightColumn[loop+1].grid_forget()
                    self.rightColumn[loop] = self.rightColumn[loop+1]
                    self.rightColumn[loop+1].grid(row=loop, column=self.numColumns, sticky=N+E+S+W)

                # update its button
                for but in self.rightColumn[loop].but:
                    if butCount == 1:
                        command=lambda row=loop, *args: self.action(row)
                    else:
                        command=lambda name=but.cget['text'], row=loop, *args: self.action(name, row)

                    but.config(command=command)

                # re-grid them
                for cellNum in range(len(self.cells[loop])):
                    self.cells[loop][cellNum].grid(row=loop, column=cellNum, sticky=N+E+S+W)

            # lose last item from lists
            self.cells = self.cells[:-1]
            self.rightColumn = self.rightColumn[:-1]
            self._updateButtons(position)
            if not pauseUpdate: self.canvas.event_generate("<Configure>")
            if self.changeFunction is not None and callFunction:
                self.changeFunction()

    def _addRow(self, rowData):
        if self.numColumns == 0:
            raise Exception("No columns to add to.")
        else:
            gui.trace(rowData)
            rowNum = len(self.cells)
            numCols = len(rowData)
            newRow = []
            if numCols > self.numColumns:
                gui.warn("New data has more columns (%s) than the table (%s), some columns will be discarded.", numCols, self.numColumns)
            for cellNum in range(self.numColumns):

                # get a val ("" if no val)
                if cellNum >= numCols:
                    val = ""
                else:
                    val = rowData[cellNum]

                lab = self._createCell(rowNum, cellNum, val)
                newRow.append(lab)
            self.cells.append(newRow)

            # add some buttons for each row
            if self.action is not None:
                # add the title
                if rowNum == 0:
                    widg = GridCell(self.interior, self.fonts, isHeader=True, text=self.actionHeading)
                # add a button
                else:
                    widg = GridCell(self.interior, self.fonts, isHeader=True)
                    widg.config(borderwidth=0, bg=self.fonts['headerBg'])
                    widg.but=[]

                    val = rowNum - 1

                    butCount = len(self.actionButton)
                    for row, text in enumerate(self.actionButton):
                        if butCount == 1:
                            command=lambda row=val, *args: self.action(row)
                        else:
                            command=lambda name=text, row=val, *args: self.action(name, row)

                        but = Button(widg, font=self.fonts["buttonFont"], text=text,
                                        bd=0, highlightthickness=0, command=command)

                        if gui.GET_PLATFORM() in [gui.MAC, gui.LINUX]:
                            but.config(highlightbackground=widg.cget("bg"))
                        if self.horizontalButtons:
                            but.grid(row=0, column=row, sticky=N+E+S+W, pady=1)
                            widg.grid_columnconfigure(row, weight=1)
                        else:
                            but.grid(column=0, row=row, sticky=N+E+S+W, pady=1)
                            widg.grid_columnconfigure(0, weight=1)
                        widg.but.append(but)
                self.rightColumn.append(widg)
                widg.grid(row=rowNum, column=cellNum + 1, sticky=N+E+S+W)

    def _updateButtons(self, position=0):
        butCount = len(self.actionButton)
        for pos in range(position+1, len(self.rightColumn)):
            for but in self.rightColumn[pos].but:
                if butCount == 1:
                    command=lambda row=pos-1, *args: self.action(row)
                else:
                    command=lambda name=but.cget['text'], row=pos-1, *args: self.action(name, row)

                but.config(command=command)

    def _createCell(self, rowNum, cellNum, val):
        if rowNum == 0: # adding title row
            lab = GridCell(self.interior, self.fonts, isHeader=True, text=val)
            lab.gridPos = ''.join(["h-", str(cellNum)])
            lab.bind("<Button-1>", self._selectColumn)
        else:
            lab = GridCell(self.interior, self.fonts, text=val, wrap=self.wrap)
            lab.gridPos = ''.join([str(rowNum - 1), "-", str(cellNum)])

        if self.showMenu:
            if gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                lab.bind('<Button-3>', self._rightClick)
            else:
                lab.bind('<Button-2>', self._rightClick)

        lab.grid(row=rowNum, column=cellNum, sticky=N+E+S+W)
        self.interior.columnconfigure(cellNum, weight=1)
        self.interior.rowconfigure(rowNum, weight=1)
        return lab

    def _selectColumn(self, event=None):
        columnNumber = int(event.widget.gridPos.split("-")[1])
        self.selectColumn(columnNumber)

    def selectColumn(self, columnNumber, highlight=None):
        if columnNumber < 0 or columnNumber >= self.numColumns:
            raise Exception("Invalid column number.")
        else:
            try:
                selected = self.cells[1][columnNumber].selected
            except IndexError:
                # no rows to select
                return
            for rowCount in range(1, len(self.cells)):
                if highlight is None:
                    if selected:
                        self.cells[rowCount][columnNumber].deselect()
                    else:
                        self.cells[rowCount][columnNumber].select()
                else:
                    if highlight:
                        self.cells[rowCount][columnNumber].mouseEnter()
                    else:
                        self.cells[rowCount][columnNumber].mouseLeave()

    def _selectRow(self, event=None):
        rowNumber = event.widget.gridPos.split("-")[0]
        self.selectRow(rowNumber)

    def selectRow(self, rowNumber, highlight=None):

        if rowNumber == "h": rowNumber = 0
        else: rowNumber = int(rowNumber) + 1

        if 1 > rowNumber >= len(self.cells)+1:
            raise Exception("Invalid row number.")
        else:
            selected = self.cells[rowNumber][0].selected
            for cell in self.cells[rowNumber]:
                if highlight is None:
                    if selected: cell.deselect()
                    else: cell.select()
                else:
                    if highlight: cell.mouseEnter()
                    else: cell.mouseLeave()

    def _buildMenu(self):
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Copy", command=lambda: self._menuHelper("copy"))
        self.menu.add_command(label="Paste", command=lambda: self._menuHelper("paste"))
        self.menu.add_command(label="Edit", command=lambda: self._menuHelper("edit"))
        self.menu.add_command(label="Clear", command=lambda: self._menuHelper("clear"))
        self.menu.add_separator()
        self.menu.add_command(label="Delete Column", command=lambda: self._menuHelper("deleteColumn"))
        self.menu.add_command(label="Delete Row", command=lambda: self._menuHelper("deleteRow"))
        self.menu.add_separator()
        self.menu.add_command(label="Sort Ascending", command=lambda: self._menuHelper("sortAscending"))
        self.menu.add_command(label="Sort Descending", command=lambda: self._menuHelper("sortDescending"))
        self.menu.add_separator()
        self.menu.add_command(label="Insert Before", command=lambda: self._menuHelper("columnBefore"))
        self.menu.add_command(label="Insert After", command=lambda: self._menuHelper("columnAfter"))
        self.menu.add_separator()
        self.menu.add_command(label="Select Cell", command=lambda: self._menuHelper("selectCell"))
        self.menu.add_command(label="Select Row", command=lambda: self._menuHelper("selectRow"))
        self.menu.add_command(label="Select Column", command=lambda: self._menuHelper("selectColumn"))
        self.menu.bind("<FocusOut>", lambda e: self.menu.unpost())

    def _configMenu(self, isHeader=False):
        if isHeader:
            self.menu.entryconfigure("Delete Row", state=DISABLED)
            self.menu.entryconfigure("Select Cell", state=DISABLED)
            self.menu.entryconfigure("Select Row", state=DISABLED)
        else:
            self.menu.entryconfigure("Delete Row", state=NORMAL)
            self.menu.entryconfigure("Select Cell", state=NORMAL)
            self.menu.entryconfigure("Select Row", state=NORMAL)

    def _rightClick(self, event):
        if self.lastSelected is None or not self.lastSelected.isHeader == event.widget.isHeader:
            self._configMenu(event.widget.isHeader)
        self.lastSelected = event.widget
        self.menu.focus_set()
        self.menu.post(event.x_root - 10, event.y_root - 10)
        return "break"

    def getLastChange(self):
        data = {
            'title':self.title,
            'gridPos':self.lastSelected.gridPos,
            'action':self.lastAction,
            'cellText':self.lastSelected.cget("text"),
            'newText':self.newText,
            'widget':self.lastSelected,
        }
        return data

    def _menuHelper(self, action):
        self.update_idletasks()
        self.lastAction = action
        vals=self.lastSelected.gridPos.split("-")
        gui.trace('Table Menu Helper: %s-%s', action, vals)

        if action == "deleteColumn":
            if self.editFunction is not None: self.editFunction()
            else: self.deleteColumn(int(vals[1]), callFunction=True)
        elif action == "deleteRow" and vals[0] != "h":
            if self.editFunction is not None: self.editFunction()
            else: self.deleteRow(int(vals[0]), callFunction=True)
        elif action == "columnBefore":
            if self.editFunction is not None: self.editFunction()
            else: self.addColumn(int(vals[1]), [], callFunction=True)
        elif action == "columnAfter":
            if self.editFunction is not None: self.editFunction()
            else: self.addColumn(int(vals[1])+1, [], callFunction=True)
        elif action == "selectCell" and vals[0] != "h":
            self.lastSelected.toggleSelection()
        elif action == "selectRow":
            self.selectRow(int(vals[0]))
        elif action == "selectColumn":
            self.selectColumn(int(vals[1]))
        if action == "sortAscending":
            if self.editFunction is not None:
                self.editFunction()
            else:
                self.sort(int(vals[1]))
        if action == "sortDescending":
            if self.editFunction is not None:
                self.editFunction()
            else:
                self.sort(int(vals[1]), descending=True)
        elif action == "copy":
            val=self.lastSelected.cget("text")
            self.clipboard_clear()
            self.clipboard_append(val)
        elif action == "paste":
            self.newText = None
            try: self.newText = self.clipboard_get()
            except: pass
            self._updateCell()
        elif action == "clear":
            self.newText = ""
            self._updateCell()
        elif action == "edit":
            val=self.lastSelected.cget("text")
            defaultVar = StringVar(self)
            defaultVar.set(val)
            self.newText =  TextDialog(self, "Edit", "Enter the new text", defaultVar=defaultVar).result
            self._updateCell()

    def _updateCell(self):
        if self.newText is not None:
            if self.editFunction is not None:
                self.editFunction()
            else:
                self.lastSelected.config(text=self.newText)
                if self.changeFunction is not None: self.changeFunction()

    def addColumn(self, columnNumber, data, callFunction=False):
        if columnNumber < 0 or columnNumber > self.numColumns:
            raise Exception("Invalid column number.")
        else:
            self._hideEntryBoxes()

            gui.trace('Adding column: %s', columnNumber)
            cellCount = len(self.cells)

            # move the right column, if necessary
            if self.action is not None:
                for rowPos in range(cellCount):
                    self.rightColumn[rowPos].grid_forget()
                    self.rightColumn[rowPos].grid(row=rowPos, column=self.numColumns+1, sticky=N+E+S+W)
                    self.interior.grid_columnconfigure(self.numColumns+1, weight=1)

                # move the button
                self.ent_but.lab.grid_forget()
                self.ent_but.lab.grid(row=cellCount, column=self.numColumns+2, sticky=N+E+S+W)

                # add another entry
                ent = self._createEntryBox(self.numColumns)
                self.entries.append(ent)
                self.entryProps.append({'disabled':False})

            # move all columns including this position right one
            for colPos in range(self.numColumns-1, columnNumber-1, -1):
                gui.trace("Moving col %s right with %s cells", colPos, cellCount)
                for rowPos in range(cellCount):
                    cell = self.cells[rowPos][colPos]
                    cell.grid_forget()
                    cell.grid(row=rowPos, column=colPos+1, sticky=N+E+S+W)
                    self.interior.grid_columnconfigure(colPos+1, weight=1)
                    val = rowPos-1
                    if val == -1: val ='h'
                    else: val = str(val)
                    cell.gridPos = ''.join([val, "-", str(colPos+1)])

            # then add this column
            dataLen = len(data)
            for rowPos in range(cellCount):
                if rowPos < dataLen:
                    val = data[rowPos]
                else:
                    val = ""
                lab = self._createCell(rowPos, columnNumber, val)
                self.cells[rowPos].insert(columnNumber, lab)

            self.numColumns += 1
            self._showEntryBoxes()
            self.canvas.event_generate("<Configure>")
            if self.changeFunction is not None and callFunction:
                self.changeFunction()

    def deleteColumn(self, columnNumber, callFunction=False):

        if columnNumber < 0 or columnNumber >= self.numColumns:
            raise Exception("Invalid column number: %s.", columnNumber)
        else:
            # hide the entries
            self._hideEntryBoxes()
            cellCount = len(self.cells)

            # delete the column
            for row in self.cells:
                row[columnNumber].grid_forget()
                del row[columnNumber]

            # update the entry boxes
            if self.addRowEntries is not None and len(self.entries) >= columnNumber:
                self.entries[columnNumber].grid_forget()
                del self.entries[columnNumber]
                del self.entryProps[columnNumber]

            # move the remaining columns
            for rowCount in range(cellCount):
                row = self.cells[rowCount]
                for colCount in range(columnNumber, len(row)):
                    cell = row[colCount]
                    cell.grid_forget()
                    cell.grid(row=rowCount, column=colCount, sticky=N+E+S+W)

                    # update the cells
                    val = rowCount -1
                    if val == -1: val = 'h'
                    else: val = str(val)
                    cell.gridPos = ''.join([val, "-", str(colCount)])

            # move the buttons
            if self.action is not None:
                for rowPos in range(cellCount):
                    self.rightColumn[rowPos].grid_forget()
                    self.rightColumn[rowPos].grid(row=rowPos, column=self.numColumns-1, sticky=N+E+S+W)

            self.numColumns -= 1
            # show the entry boxes
            self._showEntryBoxes()
            self.canvas.event_generate("<Configure>")
            if self.changeFunction is not None and callFunction:
                self.changeFunction()

    def sort(self, columnNumber, descending=False):
        order = self._getSortedData(columnNumber, descending)
        for k, val in enumerate(order):
            for c, cell in enumerate(self.cells[k+1]):
                cell.config(text=val[c])
                cell.selected=False
                cell.mouseLeave()

    def _getSortedData(self, columnNumber, descending=False):
        data = []
        for pos in range(len(self.cells)-1):
            row = self.getRow(pos)
            data.append(row)
        return  sorted(data,key=lambda l:l[columnNumber], reverse=descending)

    def _hideEntryBoxes(self):
        if self.addRowEntries is None or len(self.entries) == 0:
            return
        for e in self.entries:
            e.lab.grid_forget()
        self.ent_but.lab.grid_forget()

    def _deleteEntryBoxes(self):
        self._hideEntryBoxes()
        self.entries = []
        self.entryProps = []

    def _showEntryBoxes(self):
        if self.addRowEntries is None: return
        if len(self.entries) > 0:
            cellCount = len(self.cells)
            for pos in range(len(self.entries)):
                self.entries[pos].lab.grid(row=cellCount, column=pos, sticky=N+E+S+W)
            self.ent_but.lab.grid(row=cellCount, column=len(self.entries), sticky=N+E+S+W)
        else:
            self._createEntryBoxes()

    def _configEntryBoxes(self):
        if self.addRowEntries is None: return
        # config the entries
        for cellNum in range(self.numColumns):
            if self.entryProps[cellNum]['disabled']:
                self.entries[cellNum].config(state='readonly')

    def disableEntry(self, pos, disabled=True):
        self.entryProps[pos]['disabled'] = disabled
        self._configEntryBoxes()

    def _createEntryBoxes(self):
        if self.addRowEntries is None: return
        # add the entries
        for cellNum in range(self.numColumns):
            ent = self._createEntryBox(cellNum)
            self.entries.append(ent)
            self.entryProps.append({'disabled':False})

        # add a button
        lab = GridCell(self.interior, self.fonts, isHeader=True)
        lab.grid(row=len(self.cells), column=self.numColumns, sticky=N+E+S+W)
        self.ent_but = Button(
            lab, font=self.fonts["buttonFont"],
            text=self.addButton,
            command=gui.MAKE_FUNC(self.addRowEntries, "newRow")
        )
        if gui.GET_PLATFORM() in [gui.MAC, gui.LINUX]:
            self.ent_but.config(highlightbackground=lab.cget("bg"))
        self.ent_but.lab = lab
        self.ent_but.pack(expand=True, fill='both')

    def _createEntryBox(self, cellNum):
        # create the container
        lab = GridCell(self.interior, self.fonts, isHeader=True)
        lab.grid(row=len(self.cells), column=cellNum, sticky=N + E + S + W)

        # create the entry
        ent = Entry(lab, relief=FLAT, borderwidth=1, highlightbackground='black', highlightthickness=1, width=6, disabledbackground='grey')
        ent.pack(expand=True, fill='both')
        ent.lab = lab
        return ent

    def getEntries(self):
        return [e.get() for e in self.entries]

    def getSelectedCells(self):
        selectedCells = []
        for row in self.cells:
            for cell in row:
                if cell.selected:
                    selectedCells.append(cell.gridPos)

        return selectedCells

    def _refreshGrids(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

##########################
# MicroBit Simulator
##########################


class MicroBitSimulator(Frame, object):

    COLOURS = {0:'#000000',1:'#110000',2:'#220000',3:'#440000',4:'#660000',5:'#880000',6:'#aa0000',7:'#cc0000',8:'#ee0000',9:'#ff0000'}
    SIZE = 5
    HEART = "09090:90909:90009:09090:00900"

    def __init__(self, parent, **opts):
        super(MicroBitSimulator, self).__init__(parent, **opts)

        self.matrix = []
        for i in range(self.SIZE):
            self.matrix.append([])
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                self.matrix[i].append('')

        for y in range(self.SIZE):
            for x in range(self.SIZE):
                self.matrix[x][y] = Label(self, bg='#000000', width=5, height=2)
                self.matrix[x][y].grid(column=x, row=y, padx=5, pady=5)

        self.update_idletasks()

    def set_pixel(self, x, y, brightness):
        self.matrix[x][y].config(bg=self.COLOURS[brightness])
        self.update_idletasks()

    def show(self, image):
        rows = image.split(':')
        for y in range(len(rows)):
            for x in range(len(rows[0])):
                self.matrix[x][y].config(bg=self.COLOURS[int(rows[y][x])])
        self.update_idletasks()

    def clear(self):
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                self.matrix[x][y].config(bg='#000000')
        self.update_idletasks()


##########################
# Simple SplashScreen
##########################


class SplashScreen(Toplevel, object):
    def __init__(self, parent, text="appJar", fill="#FF0000", stripe="#000000", fg="#FFFFFF", font=44):
        super(SplashScreen, self).__init__(parent)

        lab = Label(self, bg=stripe, fg=fg, text=text, height=3, width=50)
        lab.config(font=("Courier", font))
        lab.place(relx=0.5, rely=0.5, anchor=CENTER)

        width = str(self.winfo_screenwidth())
        height = str(self.winfo_screenheight())
        self.geometry("%sx%s" % (width, height))
        self.config(bg=fill)

        self.attributes("-alpha", 0.95)
        self.attributes("-fullscreen", True)
        self.overrideredirect(1)

        self.update()

##########################
# CopyAndPaste Organiser
##########################


class CopyAndPaste():

    def __init__(self, topLevel, gui):
        self.topLevel = topLevel
        self.inUse = False
        self.gui = gui

    def setUp(self, widget):
        self.inUse = True
        # store globals
        w = widget
        wt = gui.GET_WIDGET_CLASS(widget)

        if wt != "Menu":
            self.widget = w
            self.widgetType = wt

        # query widget
        self.canCut = False
        self.canCopy = False
        self.canSelect = False
        self.canUndo = False
        self.canRedo = False
        self.canFont = False

        try:
            self.canPaste = len(self.topLevel.clipboard_get()) > 0
        except:
            self.canPaste = False

        try:
            if self.widgetType in ["Entry", "AutoCompleteEntry"]:
                if widget.selection_present():
                    self.canCut = self.canCopy = True
                if not self.widget.showingDefault and widget.index(END) > 0:
                    self.canSelect = True
            elif self.widgetType in ["ScrolledText", "Text", "AjText", "AjScrolledText"]:
                if widget.tag_ranges("sel"):
                    self.canCut = self.canCopy = True
                    self.canFont = True
                if widget.index("end-1c") != "1.0":
                    self.canSelect = True
#                if widget.edit_modified():
                self.canUndo = True
                self.canRedo = True
            elif self.widgetType == "OptionMenu":
                self.canCopy = True
                self.canPaste = False
        except Exception as e:
            gui.warn("Error in EDIT menu: %s", self,widgetType)
            gui.exception(e)

    def copy(self):
        if self.widgetType == "OptionMenu":
            self.topLevel.clipboard_clear()
            self.topLevel.clipboard_append(self.widget.var.get())
        else:
            self.widget.event_generate('<<Copy>>')
            self.widget.selection_clear()

    def cut(self):
        if self.widgetType == "OptionMenu":
            self.topLevel.bell()
        else:
            self.widget.event_generate('<<Cut>>')
            self.widget.selection_clear()

    def paste(self):
        if self.widgetType in ["Entry", "AutoCompleteEntry"]:
            # horrible hack to clear default text
            name = self.gui.widgetManager.getName(self.widget)
            self.gui._updateEntryDefault(name, mode="in")
        self.widget.event_generate('<<Paste>>')
        self.widget.selection_clear()

    def undo(self):
        self.widget.event_generate("<<Undo>>")

    def redo(self):
        self.widget.event_generate("<<Redo>>")

    def clearClipboard(self):
        self.topLevel.clipboard_clear()

    def font(self, tag):
        if tag in self.widget.tag_names(SEL_FIRST):
            self.widget.tag_remove(tag, SEL_FIRST, SEL_LAST)
        else:
            self.widget.tag_add(tag, SEL_FIRST, SEL_LAST)

    def clearText(self):
        try:
            self.widget.delete(0.0, END)  # TEXT
        except:
            try:
                self.widget.delete(0, END)  # ENTRY
            except:
                self.topLevel.bell()

    def selectAll(self):
        try:
            self.widget.select_range(0, END)  # ENTRY
        except:
            try:
                self.widget.tag_add("sel", "1.0", "end")  # TEXT
            except:
                self.topLevel.bell()

    # clear the undo/redo stack
    def resetStack(self):
        self.widget.edit_reset()

#####################################
# class to temporarily pause logging
#####################################
# usage:
# with PauseLogger():
#   doSomething()
#####################################
class PauseLogger():
    def __enter__(self):
        # disable all warning of CRITICAL & below
        logging.disable(logging.CRITICAL)
    def __exit__(self, a, b, c):
        logging.disable(logging.NOTSET)


#####################################
# class to temporarily pause function calling
#####################################
# usage:
# with PauseCallFunction(callFunction, widg):
#   doSomething()
# relies on 3 variables in widg:
# var - the thing being traced
# cmd_id - linking to the trace
# cmd - the function called by the trace
#####################################
class PauseCallFunction():
    def __init__(self, callFunction, widg, useVar=True):
        self.callFunction = callFunction
        self.widg = widg
        if useVar:
            self.tracer = self.widg.var
        else:
            self.tracer = self.widg
        gui.trace("PauseCallFunction: callFunction=%s, useVar=%s", callFunction, useVar)

    def __enter__(self):
        if not self.callFunction and hasattr(self.widg, 'cmd'):
            self.tracer.trace_vdelete('w', self.widg.cmd_id)
            gui.trace("callFunction paused")

    def __exit__(self, a, b, c):
        if not self.callFunction and hasattr(self.widg, 'cmd'):
            self.widg.cmd_id = self.tracer.trace('w', self.widg.cmd)
            gui.trace("callFunction resumed")

#####################################
# classes to work with image maps
#####################################
class AjPoint(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({},{})".format(self.x, self.y)

class AjRectangle(object):
    def __init__(self, name, posn, w, h):
        self.name = name
        self.corner = posn
        self.width = w
        self.height = h

    def __str__(self):
        return "{3}:({0},{1},{2})".format(self.corner, self.width, self.height, self.name)

    def contains(self, point):
        return (self.corner.x <= point.x <= self.corner.x + self.width and
                    self.corner.y <= point.y <= self.corner.y + self.height)

class GoogleMap(LabelFrame, object):
    """ Class to wrap a GoogleMap tile download into a widget"""

    def __init__(self, parent, app, defaultLocation="Marlborough, UK", proxyString=None, useTtk=False, font=None):
        super(GoogleMap, self).__init__(parent, text="GoogleMaps")
        self.alive = True
        self.API_KEY = ""
        self.parent = parent
        self.imageQueue = Queue.Queue()
        self.defaultLocation = defaultLocation
        self.currentLocation = None
        self.app = app
        self.proxyString = proxyString
        if font is not None:
            self.config(font=font)

        self.TERRAINS = ("Roadmap", "Satellite", "Hybrid", "Terrain")
        self.MAP_URL =  "http://maps.google.com/maps/api/staticmap?"
        self.GEO_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
        self.LOCATION_URL = "http://freegeoip.net/json/"
#        self.LOCATION_URL = "http://ipinfo.io/json"
        self.setCurrentLocation()

        # the parameters that we store
        # keeps getting updated, then sent to GoogleMaps
        self.params = {}
        self._setMapParams()

        imgObj = None
        self.rawData = None
        self.mapData = None
        self.request = None
        self.app.thread(self.getMapData)

        self.updateMapId = self.parent.after(500, self.updateMap)

        # if we got some map data then load it
        if self.mapData is not None:
            try:
                imgObj = PhotoImage(data=self.mapData)
                self.h = imgObj.height()
                self.w = imgObj.width()
            # python 3.3 fails to load data
            except Exception as e:
                gui.exception(e)

        if imgObj is None:
            self.w = self.params['size'].split("x")[0]
            self.h = self.params['size'].split("x")[1]

        self.canvas = Canvas(self, width=self.w, height=self.h)
        self.canvas.pack()#expand = YES, fill = BOTH)
        self.image_on_canvas = self.canvas.create_image(1, 1, image=imgObj, anchor=NW)
        self.canvas.img = imgObj

        # will store the 3 buttons in an array
        # they are actually labels - to hide border
        # maes it easier to configure them
        self.buttons = [
                    Label(self.canvas, text="-"),
                    Label(self.canvas, text="+"),
                    Label(self.canvas, text="H"),
                    gui._makeLink()(self.canvas, text="@", useTtk=useTtk)
                        ]
        B_FONT = tkFont.Font(family='Helvetica', size=10)

        for b in self.buttons:
            b.configure(width=3, relief=GROOVE, font=B_FONT)
            if not useTtk:
                b.configure(width=3, activebackground="#D2D2D2", relief=GROOVE, font=B_FONT)

            if gui.GET_PLATFORM() == gui.MAC:
                b.configure(cursor="pointinghand")
            elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                b.configure(cursor="hand2")

        #make it look like it's pressed
        self.buttons[0].bind("<Button-1>",lambda e: self.buttons[0].config(relief=SUNKEN), add="+")
        self.buttons[0].bind("<ButtonRelease-1>",lambda e: self.buttons[0].config(relief=GROOVE), add="+")
        self.buttons[0].bind("<ButtonRelease-1>",lambda e: self.zoom("-"), add="+")

        self.buttons[1].bind("<Button-1>",lambda e: self.buttons[1].config(relief=SUNKEN), add="+")
        self.buttons[1].bind("<ButtonRelease-1>",lambda e: self.buttons[1].config(relief=GROOVE), add="+")
        self.buttons[1].bind("<ButtonRelease-1>",lambda e: self.zoom("+"), add="+")

        self.buttons[2].bind("<Button-1>",lambda e: self.buttons[2].config(relief=SUNKEN), add="+")
        self.buttons[2].bind("<ButtonRelease-1>",lambda e: self.buttons[2].config(relief=GROOVE), add="+")
        self.buttons[2].bind("<ButtonRelease-1>",lambda e: self.changeLocation(""), add="+")

        # an optionMenu of terrains
        self.terrainType = StringVar(self.parent)
        self.terrainType.set(self.TERRAINS[0])
        self.terrainOption = OptionMenu(self.canvas, self.terrainType, *self.TERRAINS, command=lambda e: self.changeTerrain(self.terrainType.get().lower()))
        self.terrainOption.config(highlightthickness=0)

        self.terrainOption.config(font=B_FONT)

        # an entry for searching locations
        self.locationEntry = Entry(self.canvas)
        self.locationEntry.bind('<Return>', lambda e: self.changeLocation(self.location.get()))
        self.location = StringVar(self.parent)
        self.locationEntry.config(textvariable=self.location)
        self.locationEntry.config(highlightthickness=0)

        self._placeControls()

    def setProxyString(self, proxyString):
        self.proxyString = proxyString

    def destroy(self):
        self.stopUpdates()
        super(GoogleMap, self).destroy()

    def _removeControls(self):
        self.locationEntry.place_forget()
        self.terrainOption.place_forget()
        self.buttons[0].place_forget()
        self.buttons[1].place_forget()
        self.buttons[2].place_forget()
        self.buttons[3].place_forget()

    def stopUpdates(self):
        self.alive = False
        self.parent.after_cancel(self.updateMapId)

    def _placeControls(self):
        self.locationEntry.place(rely=0, relx=0, x=8, y=8, anchor=NW)
        self.terrainOption.place(rely=0, relx=1.0, x=-8, y=8, anchor=NE)
        self.buttons[0].place(rely=1.0, relx=1.0, x=-5, y=-20, anchor=SE)
        self.buttons[1].place(rely=1.0, relx=1.0, x=-5, y=-38, anchor=SE)
        self.buttons[2].place(rely=1.0, relx=1.0, x=-5, y=-56, anchor=SE)
        self.buttons[3].place(rely=1.0, relx=1.0, x=-5, y=-74, anchor=SE)

        if self.request is not None:
            self.buttons[3].registerWebpage(self.request)
            self._addTooltip(self.buttons[3], self.request)

    def _addTooltip(self, but, text):
        # generate a tooltip
        if ToolTip is not False:
            tt = ToolTip(
                but,
                text,
                delay=1000,
                follow_mouse=1)

    def _setMapParams(self):
        if "center" not in self.params or self.params["center"] is None or self.params["center"] == "":
            self.params["center"] = self.currentLocation
        if "zoom" not in self.params:
            self.params["zoom"] = 16
        if "size" not in self.params:
            self.params["size"] = "500x500"
        if "format" not in self.params:
            self.params["format"] = "gif"
        if "maptype" not in self.params:
            self.params["maptype"] = self.TERRAINS[0]

#        self.params["mobile"] = "true" # optional: mobile=true will assume the image is shown on a small screen (mobile device)
        self.params["sensor"] = "false"  # must be given, deals with getting loction from mobile device

        self.markers = []

    def removeMarkers(self):
        self.markers = []
        self.app.thread(self.getMapData)

    def removeMarker(self, label):
        for p, v in enumerate(self.markers):
            if v.get("label") == label:
                del self.markers[p]
                self.app.thread(self.getMapData)
                return

    def addMarker(self, location, size=None, colour=None, label=None, replace=False):
        """ function to add markers, format:
            &markers=color:blue|label:Z|size:tiny|location_string
        """
        if size is not None:
            size = size.lower().strip()
            if size not in ["tiny", "mid", "small"]:
                gui.warn("Invalid size: %s, for marker %s, ignoring", size, location)
                size = None

        if label is not None:
            label = label.upper().strip()
            if label not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                gui.warn("Invalid label: %s, for marker %s, must be a single character.", label, location)
                label = None

        if len(self.markers) == 0 or not replace:
            self.markers.append( {"location":location, "size":size, "colour":colour, "label":label} )
        else:
            self.markers[-1] = {"location":location, "size":size, "colour":colour, "label":label}

        self.app.thread(self.getMapData)

    def saveTile(self, location):
        if self.rawData is not None:
            try:
                with open(location, "wb") as fh:
                    fh.write(self.rawData)
                gui.info("Map data written to file: %s", location)
                return True
            except  Exception as e:
                gui.exception(e)
                return False
        else:
            gui.error("Unable to save map data - no data available")
            return False

    def setSize(self, size):
        if size != self.params["size"]:
            self.params["size"] = str(size).lower()
            self.app.thread(self.getMapData)

    def changeTerrain(self, terrainType):
        terrainType = terrainType.title()
        if terrainType in self.TERRAINS:
            self.terrainType.set(terrainType)
            if self.params["maptype"] != self.terrainType.get().lower():
                self.params["maptype"] = self.terrainType.get().lower()
                self.app.thread(self.getMapData)

    def changeLocation(self, location):
        self.location.set(location) # update the entry
        if self.params["center"] != location:
            self.params["center"] = location
            self.app.thread(self.getMapData)

    def setZoom(self, zoom):
        if 0 <= zoom <= 22:
            self.params["zoom"] = zoom
            self.app.thread(self.getMapData)

    def zoom(self, mod):
        if mod == "+" and self.params["zoom"] < 22:
            self.params["zoom"] += 1
            self.app.thread(self.getMapData)
        elif mod == "-" and self.params["zoom"] > 0:
            self.params["zoom"] -= 1
            self.app.thread(self.getMapData)

    def updateMap(self):
        if not self.alive: return
        if not self.imageQueue.empty():
            self.rawData = self.imageQueue.get()
            self.mapData = base64.encodestring(self.rawData)
            try:
                imgObj = PhotoImage(data=self.mapData)
            except:
                gui.error("Error parsing image data")
            else:
                self.canvas.itemconfig(self.image_on_canvas, image=imgObj)
                self.canvas.img = imgObj

                h = imgObj.height()
                w = imgObj.width()

                if h != self.h or w != self.w:
                    self._removeControls()
                    self.h = h
                    self.w = w
                    self.canvas.config(width=self.w, height=self.h)
                    self._placeControls()
                if self.request is not None:
                    self.buttons[3].registerWebpage(self.request)
                    self._addTooltip(self.buttons[3], self.request)
        self.updateMapId = self.parent.after(200, self.updateMap)

    def _buildQueryURL(self):
        self.request = self.MAP_URL + urlencode(self.params)
        if len(self.markers) > 0:
            m = ""
            for mark in self.markers:
                if mark["colour"] is not None: m += "color:" + str(mark["colour"])
                if mark["size"] is not None: m += "|size:" + str(mark["size"])
                if mark["label"] is not None: m += "|label:" + str(mark["label"])
                m += "|" + str(mark["location"])
                m = quote_plus(m)
                self.request += "&markers=" + m

        gui.trace("GoogleMap search URL: %s", self.request)

    def _buildGeoURL(self, location):
        """ for future use - gets the location
        """
        p = {}
        p["address"] = location
        p["key"] = self.API_KEY
        req = self.GEO_URL + urlencode(p)
        return req

    def getMapData(self):
        """ will query GoogleMaps & download the image data as a blob """
        if self.params['center'] == "":
            self.params["center"] = self.currentLocation
        self._buildQueryURL()
        gotMap = False
        while not gotMap:
            if self.request is not None:
                if self.proxyString is not None:
                    gui.error("Proxy set, but not enabled.")

                try:
                    u = urlopen(self.request)
                    rawData = u.read()
                    u.close()
                    self.imageQueue.put(rawData)
                    gotMap = True
                except Exception as e:
                    gui.error("Unable to contact GoogleMaps")
                    time.sleep(1)
            else:
                gui.trace("No request")
                time.sleep(.25)

    def getMapFile(self, fileName):
        """ will query GoogleMaps & download the image into the named file """
        self._buildQueryURL()
        self.buttons[3].registerWebpage(self.request)
        try:
            urlretrieve(self.request, fileName)
            return fileName
        except Exception as e:
            gui.error("Unable to contact GoogleMaps")
            return None

    def setCurrentLocation(self):
        gui.trace("Location request URL: %s", self.LOCATION_URL)
        try:
            self.currentLocation = self._locationLookup()
        except Exception as e:
            gui.error("Unable to contact location server, using default: %s", self.defaultLocation)
            self.currentLocation = self.defaultLocation

    def _locationLookup(self):
        u =  urlopen(self.LOCATION_URL)
        data = u.read().decode("utf-8")
        u.close()
        gui.trace("Location data: %s", data)
        data = json.loads(data)
#        location = data["loc"]
        location = str(data["latitude"]) + "," + str(data["longitude"])
        return location


#####################################
class CanvasDnd(Canvas, object):
    """
    A canvas to which we have added those methods necessary so it can
        act as both a TargetWidget and a TargetObject.

    Use (or derive from) this drag-and-drop enabled canvas to create anything
        that needs to be able to receive a dragged object.
    """
    def __init__(self, Master, cnf={}, **kw):
        if cnf:
            kw.update(cnf)
        super(CanvasDnd, self).__init__(Master,  kw)
        self.config(bd=0, highlightthickness=0)

    #----- TargetWidget functionality -----

    def dnd_accept(self, source, event):
        #Tkdnd is asking us (the TargetWidget) if we want to tell it about a
        #    TargetObject. Since CanvasDnd is also acting as TargetObject we
        #    return 'self', saying that we are willing to be the TargetObject.
        gui.trace("<<%s .dnd_accept>> %s", type(self), source)
        return self

    #----- TargetObject functionality -----

    # This is called when the mouse pointer goes from outside the
    # Target Widget to inside the Target Widget.
    def dnd_enter(self, source, event):
        gui.trace("<<%s .dnd_enter>> %s", type(self), source)
        XY = gui.MOUSE_POS_IN_WIDGET(self, event)
        # show the dragged object
        source.appear(self ,XY)

    # This is called when the mouse pointer goes from inside the
    # Target Widget to outside the Target Widget.
    def dnd_leave(self, source, event):
        gui.trace("<<%s .dnd_leave>> %s", type(self), source)
        # hide the dragged object
        source.vanish()

    #This is called when the mouse pointer moves withing the TargetWidget.
    def dnd_motion(self, source, event):
        gui.trace("<<%s .dnd_motion>> %s", type(self), source)
        XY = gui.MOUSE_POS_IN_WIDGET(self,event)
        # move the dragged object
        source.move(self, XY)

    #This is called if the DraggableWidget is being dropped on us.
    def dnd_commit(self, source, event):
        gui.trace("<<%s .dnd_commit>> %s", type(self), source)

# A canvas specifically for deleting dragged objects.
class TrashBin(CanvasDnd, object):
    def __init__(self, master, **kw):
        if "width" not in kw:
            kw['width'] = 150
        if "height" not in kw:
            kw['height'] = 25

        super(TrashBin, self).__init__(master, kw)
        self.config(relief="sunken", bd=2)
        x = kw['width'] / 2
        y = kw['height'] / 2
        self.textId = self.create_text(x, y, text='TRASH', anchor="center")

    def dnd_commit(self, source, event):
        gui.trace("<<TRASH_BIN.dnd_commit>> vanishing source")
        source.vanish(True)

    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "fg" in kw:
            fg=kw.pop('fg')
            self.itemconfigure(self.textId, fill=fg)

        super(TrashBin, self).config(**kw)

# This is a prototype thing to be dragged and dropped.
class DraggableWidget(object):
    discardDragged = False

    def dnd_accept(self, source, event):
        return None

    def __init__(self, parent, title, name, XY, widg=None):
        self.parent = parent
        gui.trace("<<DRAGGABLE_WIDGET.__init__>>")

        #When created we are not on any canvas
        self.Canvas = None
        self.OriginalCanvas = None
        self.widg = widg

        #This sets where the mouse cursor will be with respect to our label
        self.OffsetCalculated = False
        self.OffsetX = XY[0]
        self.OffsetY = XY[1]

        # give ourself a name
        self.Name = name
        self.Title = title

        self.OriginalID = None
        self.dropTarget = None

    # this gets called when we are dropped
    def dnd_end(self, target, event):
        gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> %s target=%s", self.Name, target)

        # from somewhere, dropped nowhere - self destruct, or put back
        if self.Canvas is None:
            gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> dropped with Canvas (None)")
            if DraggableWidget.discardDragged:
                gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> DISCARDING under order")
            else:
                if self.OriginalCanvas is not None:
                    gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> RESTORING")
                    self.restoreOldData()
                    self.Canvas.dnd_enter(self, event)
                else:
                    gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> DISCARDING as nowhere to go")

        # have been dropped somewhere
        else:
            gui.trace("<<DRAGGABLE_WIDGET.dnd_end>> dropped with Canvas(%s) Target=%s", self.Canvas, self.dropTarget)
            if not self.dropTarget:
                # make the dragged object re-draggable
                self.Label.bind('<ButtonPress>', self.press)
            else:
                if self.dropTarget.keepWidget(self.Title, self.Name):
                    self.Label.bind('<ButtonPress>', self.press)
                else:
                    self.vanish(True)

            # delete any old widget
            if self.OriginalCanvas:
                self.OriginalCanvas.delete(self.OriginalID)
                self.OriginalCanvas = None
                self.OriginalID = None
                self.OriginalLabel = None

    # put a label representing this DraggableWidget instance on Canvas.
    def appear(self, canvas, XY):

        if not isinstance(canvas, CanvasDnd):
            self.dropTarget = canvas
            canvas = canvas.dnd_canvas
#        else:
#            self.dropTarget = None

        if self.Canvas:
            gui.trace("<<DRAGGABLE_WIDGET.appear> - ignoring, as we already exist?: %s %s", canvas, XY)
            return
        else:
            gui.trace("<<DRAGGABLE_WIDGET.appear> - appearing: %s %s", canvas, XY)

            self.Canvas = canvas
            self.X, self.Y = XY
            self.Label = Label(self.Canvas, text=self.Name, borderwidth=2, relief=RAISED)

            # Offsets are received as percentages from initial button press
            # so calculate Offset from a percentage
            if not self.OffsetCalculated:
                self.OffsetX = self.Label.winfo_reqwidth() * self.OffsetX
                self.OffsetY = self.Label.winfo_reqheight() * self.OffsetY
                self.OffsetCalculated = True

            self.ID = self.Canvas.create_window(self.X-self.OffsetX, self.Y-self.OffsetY, window=self.Label, anchor="nw")
            gui.trace("<<DRAGGABLE_WIDGET.appear> - created: %s %s", self.Label, self.Canvas)

    # if there is a label representing us on a canvas, make it go away.
    def vanish(self, all=False):
        # if we had a canvas, delete us
        if self.Canvas:
            gui.trace("<<DRAGGABLE_WIDGET.vanish> - vanishing")
            self.storeOldData()
            self.Canvas.delete(self.ID)
            self.Canvas = None
            del self.ID
            del self.Label
        else:
            gui.trace("<<DRAGGABLE_WIDGET.vanish>> ignoring")

        if all and self.OriginalCanvas:
            gui.trace("<<DRAGGABLE_WIDGET.vanish>> restore original")
            self.OriginalCanvas.delete(self.OriginalID)
            self.OriginalCanvas = None
            del self.OriginalID
            del self.OriginalLabel

    # if we have a label on a canvas, then move it to the specified location.
    def move(self, widget, XY):
        gui.trace("<<DRAGGABLE_WIDGET.move>> %s %s", self.Canvas, XY)
        if self.Canvas:
            self.X, self.Y = XY
            self.Canvas.coords(self.ID, self.X-self.OffsetX, self.Y-self.OffsetY)
        else:
            gui.error("<<DRAGGABLE_WIDGET.move>> unable to move - NO CANVAS!")

    def press(self, event):
        gui.trace("<<DRAGGABLE_WIDGET.press>>")
        self.storeOldData()

        self.ID = None
        self.Canvas = None
        self.Label = None

        #Ask Tkdnd to start the drag operation
        if INTERNAL_DND.dnd_start(self, event):
            self.OffsetX, self.OffsetY = gui.MOUSE_POS_IN_WIDGET(self.OriginalLabel, event, False)
            XY = gui.MOUSE_POS_IN_WIDGET(self.OriginalCanvas, event, False)
            self.appear(self.OriginalCanvas, XY)

    def storeOldData(self, phantom=False):
        gui.trace("<<DRAGGABLE_WIDGET.storeOldData>>")
        self.OriginalID = self.ID
        self.OriginalLabel = self.Label
        self.OriginalText = self.Label['text']
        self.OriginalCanvas = self.Canvas
        if phantom:
            gui.trace("<<DRAGGABLE_WIDGET.storeOldData>> keeping phantom")
            self.OriginalLabel["text"] = "<Phantom>"
            self.OriginalLabel["relief"] = RAISED
        else:
            gui.trace("<<DRAGGABLE_WIDGET.storeOldData>> hiding phantom")
            self.OriginalCanvas.delete(self.OriginalID)

    def restoreOldData(self):
        if self.OriginalID:
            gui.trace("<<DRAGGABLE_WIDGET.restoreOldData>>")
            self.ID = self.OriginalID
            self.Label = self.OriginalLabel
            self.Label['text'] = self.OriginalText
            self.Label['relief'] = RAISED
            self.Canvas = self.OriginalCanvas
            self.OriginalCanvas.itemconfigure(self.OriginalID, state='normal')
            self.Label.bind('<ButtonPress>', self.press)
        else:
            gui.trace("<<DRAGGABLE_WIDGET.restoreOldData>> unable to restore - NO OriginalID")

#########################################
# Enum & WidgetManager - used to store widget lists
#########################################

class WidgetManager(object):
    """ used to keep track of all widgets in the GUI
        creates a dictionary for each widget type on demand
        provides functions for accessing widgets """

    WIDGETS = "widgets"
    VARS = "vars"

    def __init__(self):
        self.widgets = {}
        self.vars = {}

    def reset(self, keepers):
        newWidg = {}
        newVar = {}

        gui.trace('Resetting WidgetManager')

        for key in keepers:
            if key in self.widgets:
                newWidg[key] = self.widgets[key]
            if key in self.vars:
                newVar[key] = self.vars[key]

        self.widgets = newWidg
        self.vars = newVar

    def group(self, widgetType, group=None, array=False):
        """
        returns the list/dictionary containing the specified widget type
        will create a new group if none exists
        """
        if group is None: container = self.widgets
        elif group == WidgetManager.VARS: container = self.vars

        try:
            widgGroup = container[widgetType]
        except KeyError:
            if array: widgGroup = []
            else: widgGroup = {}
            container[widgetType] = widgGroup

        return widgGroup

    def add(self, widgetType, widgetName, widget, group=None):
        """ adds items to the specified dictionary """
        widgGroup = self.group(widgetType, group)
        if widgetName in widgGroup:
            raise ItemLookupError("Duplicate key: '" + widgetName + "' already exists")
        else:
            widgGroup[widgetName] = widget

        widget.APPJAR_TYPE = widgetType

    def getName(self, widget):
        if widget is not None and hasattr(widget, 'APPJAR_TYPE'):
            widgetType = widget.APPJAR_TYPE
            widgGroup = self.group(widgetType, None)
            if widgGroup is not None:
                for name, obj in widgGroup.items():
                    if obj == widget:
                        return name
        return None

    def log(self, widgetType, widget, group=None):
        """ Used for adding items to an array """
        widgGroup = self.group(widgetType, group, array=True)
        widgGroup.append(widget)

        try: widget.APPJAR_TYPE = widgetType
        except AttributeError: pass # not available on some classes

    def verify(self, widgetType, widgetName, group=None, array=False):
        """ checks for duplicatres """
        if widgetName in self.group(widgetType, group, array):
            raise ItemLookupError("Duplicate widgetName: " + widgetName)

    def get(self, widgetType, widgetName, group=None):
        """ gets the specified item """
        try:
            return self.group(widgetType, group)[widgetName]
        except KeyError:
            raise ItemLookupError("Invalid widgetName: " + widgetName)

    def update(self, widgetType, widgetName, widget, group=None):
        """ replaces the specified item """
        try:
            self.group(widgetType, group)[widgetName] = widget
        except KeyError:
            raise ItemLookupError("Invalid widgetName: '" + widgetName)

    def check(self, widgetType, widgetName, group=None):
        """ used for arrays - checks if the item is in the array """
        try:
            if widgetName in self.group(widgetType, group): return True
            else: raise ItemLookupError("Invalid widgetName: '" + widgetName)
        except KeyError:
            raise ItemLookupError("Invalid widgetName: '" + widgetName)

    def remove(self, widgetType, widgetName, group=None):
        widgGroup = self.group(widgetType, group)
        if type(widgGroup) == list:
            widgGroup.remove(widgetName)
        else:
            del widgGroup[widgetName]
            # delete a linked var
            if group != self.VARS:
                try: del self.group(widgetType, self.VARS)[widgetName]
                except: pass

    def clear(self, widgetType, group=None):
        if group is None: container = self.widgets
        elif group == WidgetManager.VARS: container = self.vars

        if isinstance(self.group(widgetType, group), dict):
            container[widgetType] = {}
        else:
            container[widgetType] = []

    def destroyContainer(self, widgType, widget):
        widgets = self.widgets[widgType]
        for name, obj in widgets.items():
            if widget == obj['container']:
                obj['container'].destroy()
                del widgets[name]
                gui.trace('Matched and destroyed')
                return
        gui.trace('Failed to match and destroy - not a container?')

    # function to loop through a config dict/list and remove matching object
    def destroyWidget(self, widgType, widget):
        widgets = self.widgets[widgType]
        # just a list, remove matching obj - no vars
        if type(widgets) in (list, tuple):
            gui.trace('Removing widget: %s, %s', widgType, widget)
            for obj in widgets:
                if widget == obj:
                    obj.destroy()
                    widgets.remove(obj)
                    gui.trace("Matched and removed")
                    return True
        else:
            gui.trace('Destroying widget: %s, %s', widgType, widget)
            for name, obj in widgets.items():
                if type(obj) in (list, tuple):
                    if self.destroyWidget(widget, obj):
                        if len(obj) == 0:
                            del widgets[name]
                            try: del self.vars[widgType][name]
                            except: pass # no var
                        return True
                elif widget == obj:
                    obj.destroy()
                    del widgets[name]
                    try: del self.vars[widgType][name]
                    except: pass # no var
                    gui.trace("Matched and destroyed")
                    return True

        gui.trace("Failed to destory widget")
        return False

#########################################
# Class for storing a shortcut
#########################################

class EventBinding(object):
    # MODIFIERS=["Control", "Ctrl", "Option", "Opt", "Alt", "Shift", "Command", "Cmd", "Meta"]
    def __init__(self, keyMap, func, win, menuBinding=False):
        gui.trace('Binding %s', keyMap)
        keyMap = self._cleanKeyMap(keyMap)

        self.func = func
        self.win = win
        self.menuBinding = menuBinding
        self.displayName = self._createDisplayName(keyMap)
        self.shortcuts = self._createShortcuts(keyMap)

    def _cleanKeyMap(self, keyMap):
        keyMap = keyMap.title()

        if keyMap[0] == "<":
            gui.warn("Shortcuts should not include chevrons: %s", keyMap)
            keyMap = keyMap[1:-1]

        if gui.GET_PLATFORM() != gui.MAC and 'Command' in keyMap:
            gui.warn("Shortcuts containing <Command> only supported on Mac")
            keyMap = keyMap.replace("Command", "Control")

        if gui.GET_PLATFORM() == gui.MAC and 'Alt' in keyMap:
            keyMap = keyMap.replace("Alt", "Option")
        elif gui.GET_PLATFORM() != gui.MAC and 'Option' in keyMap:
            keyMap = keyMap.replace("Option", "Alt")

        # fix any broken events from calling title... hacky!
        keyMap = keyMap.replace("Buttonpress", "ButtonPress")
        keyMap = keyMap.replace("Buttonrelease", "ButtonRelease")
        keyMap = keyMap.replace("Focusin", "FocusIn")
        keyMap = keyMap.replace("Focusout", "FocusOut")
        keyMap = keyMap.replace("Backspace", "BackSpace")

        gui.trace('Cleaned up to: %s', keyMap)
        return keyMap

    def _createDisplayName(self, keyMap):
        # create a shrunk-down display name (accelerator)
        acc = keyMap.replace("Control", "Ctrl")
        acc = acc.replace("Command", "Cmd")
        acc = acc.replace("Option", "Opt")
        acc = acc.replace("Key-", "")
        acc = acc.replace("-", "+")
        gui.trace('DisplayName made: %s', acc)
        return acc

    def _createShortcuts(self, shortcut):
        # try to fix numerics
        if self.menuBinding and shortcut[-1] in "0123456789" and "Key" not in shortcut:
            shortcut = shortcut[:-1] + "Key-" + shortcut[-1]

        # create two bindings if it ends in a single letter
        bits = shortcut.split('-')
        shortcuts = ['<'+shortcut+'>']

        # create both cases of the shortcut
        if bits[-1].upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            bits[-1] = bits[-1].swapcase()
            shortcuts.append('<'+'-'.join(bits)+'>')

        gui.trace('Shortcuts made: %s', shortcuts)
        return shortcuts

    def createBindings(self):
        if self.func is not None:
            for s in self.shortcuts:
                # auto created on Mac, so ignore ?!?
                if gui.GET_PLATFORM() == gui.MAC and self.menuBinding and 'Control' in s and 'Shift' in s:
                    gui.trace("Mac - skipping binding: %s", s)
                else:
                    gui.trace("Binding: %s to %s", s, self.func)
                    self.win.bind_all(s, self.func)

    def removeBindings(self):
        for s in self.shortcuts:
            gui.trace('Removing binding: %s', s)
            self.win.unbind_all(s)

    def changeBindings(self, state):
        if state.lower() == 'disabled': self.removeBindings()
        else: self.createBindings()

#####################################
# MAIN - for testing
#####################################
if __name__ == "__main__":
    print("This is a library class and cannot be executed.")
    sys.exit()
