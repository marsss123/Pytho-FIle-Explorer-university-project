from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.Qt import QKeySequence, QCursor, QDesktopServices
import shutil
import subprocess, os, platform , sys

class myWindow(QMainWindow):####O ARXIKOS KODIKA POY XERO APLA ME DIO KALSEIS COPY KAI PASTE
    def __init__(self):###O KANONIKOS EINAI O 4 
        super(myWindow, self).__init__()
        self.setWindowTitle("Filemanager")
        self.setWindowIcon(QIcon.fromTheme("system- file-manager"))
        self.process = QProcess()
        self.settings = QSettings("QFileManager", "QFileManager")
        self.clip = QApplication.clipboard()
        self.isInEditMode = False
        self.treeview = QTreeView()
        self.listview = QTreeView()
        self.cut = False
        self.hiddenEnabled = False
        self.folder_copied = ""
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)
        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)
        wid = QWidget()
        wid.setLayout(hlay)
        self.createStatusBar()
        self.setCentralWidget(wid)
        self.setGeometry(0, 26, 900,500)
        path = QDir.rootPath()
        self.copyPath = ""
        self.copyList = []
        self.copyListNew = ""
        self.createActions()
        self.findfield = QLineEdit()
        self.findfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(150)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        self.findfield.returnPressed.connect(self.findFiles)
        self.findfield.installEventFilter(self)
        self.tBar = self.addToolBar("Tools")
        self.tBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tBar.setMovable(False)
        self.tBar.setIconSize(QSize(16, 16))
        self.tBar.addAction(self.createFolderAction)
        self.tBar.addAction(self.copyFolderAction)
        self.tBar.addAction(self.pasteFolderAction)
        self.tBar.addSeparator()
        self.tBar.addAction(self.copyAction)
        self.tBar.addAction(self.pasteAction)
        self.tBar.addSeparator()
        self.tBar.addAction(self.findFilesAction)
        self.tBar.addSeparator()
        self.tBar.addAction(self.delActionTrash)
        self.tBar.addAction(self.delAction)
        self.tBar.addSeparator()
        self.tBar.addSeparator()
        empty = QWidget()
        empty.setMinimumWidth(60)
        self.tBar.addWidget(empty)
        self.tBar.addSeparator()
        self.tBar.addAction(self.btnHome)
        self.tBar.addAction(self.btnDocuments)
        self.tBar.addAction(self.btnDownloads)
        self.tBar.addSeparator()
        self.tBar.addAction(self.btnBack)
        self.tBar.addWidget(self.findfield)
        self.dirModel = QFileSystemModel()
        self.dirModel.setReadOnly(False)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives)
        self.dirModel.setRootPath(QDir.rootPath())
        self.fileModel = QFileSystemModel()
        self.fileModel.setReadOnly(False)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs  | QDir.Files)
        self.defNameFilters = self.fileModel.nameFilters()
        self.fileModel.setNameFilterDisables(False)
        self.fileModel.setResolveSymlinks(True)
        self.treeview.setModel(self.dirModel)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)
        self.listview.setModel(self.fileModel)
        self.treeview.setRootIsDecorated(True)
        self.listview.header().resizeSection(0, 320)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)
        self.listview.setSortingEnabled(True) 
        self.treeview.setSortingEnabled(True) 
        self.treeview.setRootIndex(self.dirModel.index(path))
        self.treeview.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        self.listview.doubleClicked.connect(self.list_doubleClicked)
        docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeview.setIndentation(12)
        self.treeview.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)
        self.splitter.setSizes([20, 160])
        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview.setDragDropMode(QAbstractItemView.DragDrop)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.setIndentation(10)
        self.listview.sortByColumn(0, Qt.AscendingOrder)
        print("Welcome to FileExplorer")
        self.readSettings()
        self.enableHidden()
        self.getRowCount()
        
    def getRowCount(self):
        count = 0
        index = self.treeview.selectionModel().currentIndex()
        path = QDir(self.dirModel.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QDir.Files))
        self.statusBar().showMessage("%s %s" % (count, "Files"), 0)
        return count
    
    def closeEvent(self, e):
        print("writing settings ...\nGoodbye ...")
        self.writeSettings()


    def readSettings(self):
        print("reading settings ...")
        if self.settings.contains("pos"):
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        else:
            self.move(0, 26)
        if self.settings.contains("size"):
            size = self.settings.value("size", QSize(800, 600))
            self.resize(size)
        else:
            self.resize(800, 600)
        if self.settings.contains("hiddenEnabled"):
            if self.settings.value("hiddenEnabled") == "false":
                self.hiddenEnabled = True
            else:
                self.hiddenEnabled = False

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        self.settings.setValue("hiddenEnabled", self.hiddenEnabled,)


    def enableHidden(self):
        if self.hiddenEnabled == False:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs)
            self.hiddenEnabled = True
            self.hiddenAction.setChecked(True)
            print("set hidden files to true")
        else:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.hiddenEnabled = False
            self.hiddenAction.setChecked(False)
            print("set hidden files to false")
            
    def openNewWin(self):
        self.copyListNew = ""
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        theApp =  sys.argv[0]
        if QDir(path).exists:
            print("open '", path, "' in new window")
            self.process.startDetached("python3", [theApp, path])

    def createActions(self):
        self.btnBack = QAction(QIcon.fromTheme("go-previous"),"go back",triggered = self.goBack)
        self.btnHome = QAction(QIcon.fromTheme("go-home"),"home folder",triggered = self.goHome)
        self.btnDocuments = QAction(QIcon.fromTheme("folder-documents"), "documents folder",triggered = self.goDocuments)
        self.btnDownloads = QAction(QIcon.fromTheme("folder-downloads"), "downloads folder",triggered = self.goDownloads)
        self.openAction = QAction(QIcon.fromTheme("system-run"), "open File",triggered=self.openFile)
        self.openAction.setShortcut(QKeySequence(Qt.Key_Return))
        self.openAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openAction) 
        self.newWinAction = QAction(QIcon.fromTheme("folder-new"),"open in new window",triggered=self.openNewWin)
        self.newWinAction.setShortcut(QKeySequence("Ctrl+n"))
        self.newWinAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.newWinAction) 
        self.openActionText = QAction(QIcon.fromTheme("system-run"),"open File with built-in Texteditor",triggered=self.openFileText)
        self.openActionText.setShortcut(QKeySequence(Qt.Key_F6))
        self.openActionText.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openActionText) 
        self.openActionTextRoot = QAction(QIcon.fromTheme("applications-system"),"edit as root",triggered=self.openFileTextRoot)
        self.listview.addAction(self.openActionTextRoot) 
        self.renameAction = QAction(QIcon.fromTheme("accessories-text-editor"),"rename File",triggered=self.renameFile) 
        self.renameAction.setShortcut(QKeySequence(Qt.Key_F2))
        self.renameAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.renameAction) 
        self.treeview.addAction(self.renameAction) 
        self.renameFolderAction = QAction(QIcon.fromTheme("accessories-text-editor"),"rename Folder",triggered=self.renameFolder) 
        self.treeview.addAction(self.renameFolderAction) 
        self.copyAction = QAction(QIcon.fromTheme("edit-copy"),"copy File(s)",triggered=self.copyFile) 
        self.copyAction.setShortcut(QKeySequence("Ctrl+c"))
        self.copyAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.copyAction) 
        self.copyFolderAction = QAction(QIcon.fromTheme("edit-copy"),"copy Folder",triggered=self.copyFolder) 
        self.treeview.addAction(self.copyFolderAction) 
        self.pasteFolderAction = QAction(QIcon.fromTheme("edit-paste"),"paste Folder",triggered=self.pasteFolder) 
        self.treeview.addAction(self.pasteFolderAction) 
        self.pasteAction = QAction(QIcon.fromTheme("edit-paste"),"paste File(s) / Folder",triggered=self.pasteFile) 
        self.pasteAction.setShortcut(QKeySequence("Ctrl+v"))
        self.pasteAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.pasteAction) 
        self.delAction = QAction(QIcon.fromTheme("edit-delete"),"delete File(s)",triggered=self.deleteFile)
        self.delAction.setShortcut(QKeySequence("Shift+Del"))
        self.delAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.delAction) 
        self.delFolderAction = QAction(QIcon.fromTheme("edit-delete"),"delete Folder",triggered=self.deleteFolder)
        self.treeview.addAction(self.delFolderAction) 
        self.delActionTrash = QAction(QIcon.fromTheme("user-trash"),"move to trash",triggered=self.deleteFileTrash)
        self.delActionTrash.setShortcut(QKeySequence("Del"))
        self.delActionTrash.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.delActionTrash) 
        self.py2Action=QAction(QIcon.fromTheme("python"),"run in python",triggered=self.runPy2)
        self.listview.addAction(self.py2Action) 
        self.py3Action=QAction(QIcon.fromTheme("python3"),"run in python3",triggered=self.runPy3)
        self.listview.addAction(self.py3Action) 
        self.findFilesAction = QAction(QIcon.fromTheme("edit-find"),"find in folder",triggered=self.findFiles)
        self.findFilesAction.setShortcut(QKeySequence("Ctrl+f"))
        self.findFilesAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.findFilesAction)
        self.refreshAction = QAction(QIcon.fromTheme("view-refresh"),"refresh View",triggered=self.refreshList, shortcut="F5")
        self.refreshAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.refreshAction) 
        self.hiddenAction = QAction("show hidden Files",triggered=self.enableHidden)
        self.hiddenAction.setShortcut(QKeySequence("Ctrl+h"))
        self.hiddenAction.setShortcutVisibleInContextMenu(True)
        self.hiddenAction.setCheckable(True)
        self.listview.addAction(self.hiddenAction)
        self.goBackAction = QAction(QIcon.fromTheme("go-back"), "go back",  triggered=self.goBack)
        self.goBackAction.setShortcut(QKeySequence(Qt.Key_Backspace))
        self.goBackAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.goBackAction) 
        self.terminalAction = QAction(QIcon.fromTheme("terminal"), "open folder in Terminal",  triggered=self.showInTerminal)
        self.terminalAction.setShortcut(QKeySequence(Qt.Key_F7))
        self.terminalAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.terminalAction) 
        self.listview.addAction(self.terminalAction) 
        self.startInTerminalAction = QAction(QIcon.fromTheme("terminal"), "execute in Terminal",  triggered=self.startInTerminal)
        self.startInTerminalAction.setShortcut(QKeySequence(Qt.Key_F8))
        self.startInTerminalAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.startInTerminalAction) 
        self.executableAction = QAction(QIcon.fromTheme("applications-utilities"), "make executable",  triggered=self.makeExecutable)
        self.listview.addAction(self.executableAction) 
        self.createFolderAction = QAction(QIcon.fromTheme("folder-new"), "create new Folder",  triggered=self.createNewFolder)
        self.createFolderAction.setShortcut(QKeySequence("Shift+Ctrl+n"))
        self.createFolderAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.createFolderAction) 
    
    def makeExecutable(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            print("set", path, "executable")
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)
            
    def showInTerminal(self):
        if self.treeview.hasFocus():
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
        elif self.listview.hasFocus():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.terminal = QTerminalFolder.MainWindow()
        self.terminal.show()
        if self.terminal.isVisible():
            os.chdir(path)
            self.terminal.shellWin.startDir = path
            self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                    + ":" + str(path) + "$ ")
            self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)
            
    def startInTerminal(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            filename = self.fileModel.fileInfo(index).fileName()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            folderpath = self.fileModel.fileInfo(index).path()
            if not self.fileModel.fileInfo(index).isDir():
                self.terminal = QTerminalFolder.MainWindow()
                self.terminal.show()
                if self.terminal.isVisible():
                    os.chdir(folderpath)
                    self.terminal.shellWin.startDir = folderpath
                    self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                            + ":" + str(folderpath) + "$ ")
                    self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)
                    self.terminal.shellWin.insertPlainText("./%s" % (filename))
            else:
                self.terminal = QTerminalFolder.MainWindow()
                self.terminal.show()
                if self.terminal.isVisible():
                    os.chdir(path)
                    self.terminal.shellWin.startDir = path
                    self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                            + ":" + str(path) + "$ ")
                    self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)

    def findFiles(self):
        print("find")
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        print("open findWindow")
        if self.findfield.text() != "":
            self.fileModel.setNameFilters([self.findfield.text()])
        else:
            self.fileModel.setNameFilters(self.defNameFilters)
        self.setWindowTitle("Search results in : " + path)
    def refreshList(self):
        print("refreshing view")
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.fileModel.index(path))
        self.treeview.setFocus()

    def on_clicked(self, index):
        if self.treeview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            if not(self.treeview.isExpanded(index)):
                self.treeview.setExpanded(index, True)
            else:
                self.treeview.setExpanded(index, False)

    def getFolderSize(self, path):
        size = sum(os.path.getsize(f) for f in os.listdir(folder) if os.path.isfile(f))
        return size
    
    def on_selectionChanged(self):
        self.fileModel.setNameFilters(self.defNameFilters)
        self.findfield.setText("")
        self.treeview.selectionModel().clearSelection()
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))
        self.currentPath = path
        self.setWindowTitle(path)
        self.getRowCount()

    def openFile(self):
        if self.listview.hasFocus():
            index = self.listview.selectionModel().currentIndex()
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', path))


    def openFileText(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.texteditor = QTextEdit.MainWindow()
            self.texteditor.show()
            self.texteditor.loadFile(path)

    def openFileTextRoot(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            file = sys.argv[0]
            mygksu = os.path.join(os.path.dirname(file), "mygksu")
            self.process.startDetached(mygksu, ["xed" , path])

    def list_doubleClicked(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        if not self.fileModel.fileInfo(index).isDir():
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', path))

        else:
            self.treeview.setCurrentIndex(self.dirModel.index(path))
            self.treeview.setFocus()
            self.setWindowTitle(path)

    def goBack(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.dirModel.index(path))
        
    def goHome(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDocuments(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDownloads(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()


    def createNewFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        dlg = QInputDialog(self)
        foldername, ok = dlg.getText(self, 'Folder Name', "Folder Name:", QLineEdit.Normal, "", Qt.Dialog)
        if ok:
            success = QDir(path).mkdir(foldername)

    def runPy2(self):################################
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()    
            self.process.startDetached("python", [path])

    def runPy3(self):################################
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()   
            error = QProcess.error(self.process)
            self.process.startDetached("python3", [path])
            if self.process.errorOccurred():
                self.infobox(error)

    def renameFile(self):
        if self.listview.hasFocus():
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath() 
                basepath = self.fileModel.fileInfo(index).path() 
                print(basepath)
                oldName = self.fileModel.fileInfo(index).fileName() 
                dlg = QInputDialog()
                newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
                if ok:
                    newpath = basepath + "/" + newName
                    QFile.rename(path, newpath)
        elif self.treeview.hasFocus():
            self.renameFolder()
            
    def renameFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        basepath = self.dirModel.fileInfo(index).path() 
        print("pasepath:", basepath)
        oldName = self.dirModel.fileInfo(index).fileName() 
        dlg = QInputDialog()
        newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
        if ok:
            newpath = basepath + "/" + newName
            print(newpath)
            nd = QDir(path)
            check = nd.rename(path, newpath)
            
    def copyFile(self):
        self.copyList = []
        selected = self.listview.selectionModel().selectedRows()
        count = len(selected)
        for index in selected:
            path = self.currentPath + "/" + self.fileModel.data(index,self.fileModel.FileNameRole)
            print(path, "copied to clipboard")
            self.copyList.append(path)
            self.clip.setText('\n'.join(self.copyList))
        print("%s\n%s" % ("filepath(s) copied:", '\n'.join(self.copyList)))

    def copyFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        folderpath = self.dirModel.fileInfo(index).absoluteFilePath()  
        print("%s\n%s" % ("folderpath copied:", folderpath))
        self.folder_copied = folderpath
        self.copyList = []

    def pasteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        target = self.folder_copied
        destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(self.folder_copied).fileName()
        print("%s %s %s" % (target, "will be pasted to", destination))
        try:
            shutil.copytree(target, destination)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(target, destination)
            else:
                self.infobox('Error', 'Directory not copied. Error: %s' % e)
                
    def pasteFile(self):
        if len(self.copyList) > 0:
            index = self.treeview.selectionModel().currentIndex()
            file_index = self.listview.selectionModel().currentIndex()
            for target in self.copyList:
                print(target)
                destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(target).fileName()
                print("%s %s" % ("pasted File to", destination))
                QFile.copy(target, destination)
                if self.cut == True:
                    QFile.remove(target)
                self.cut == False
        else:
            index = self.treeview.selectionModel().currentIndex()
            target = self.folder_copied
            destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(self.folder_copied).fileName()
            try:
                shutil.copytree(target, destination)
            except OSError as e:
                if e.errno == errno.ENOTDIR:
                    shutil.copy(target, destination)
                else:
                    print('Directory not copied. Error: %s' % e)
                    
    def deleteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        delFolder  = self.dirModel.fileInfo(index).absoluteFilePath()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally delete this Folder?\n" + delFolder, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            print('Deletion confirmed.')
            self.statusBar().showMessage("%s %s" % ("folder deleted", delFolder), 0)
            self.fileModel.remove(index)
            print("%s %s" % ("folder deleted", delFolder))
        else:
            print('No clicked.')

    def deleteFile(self):
        self.copyFile()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally delete this Files?\n" + '\n'.join(self.copyList), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            print('Deletion confirmed.')
            index = self.listview.selectionModel().currentIndex()
            self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()
            print("%s %s" % ("file deleted", self.copyPath))
            self.statusBar().showMessage("%s %s" % ("file deleted", self.copyPath), 0)
            for delFile in self.listview.selectionModel().selectedIndexes():
                self.fileModel.remove(delFile)
        else:
            print('No clicked.')
            
    def deleteFileTrash(self):
        index = self.listview.selectionModel().currentIndex()
        self.copyFile()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally move this Files to Trash\n" + '\n'.join(self.copyList), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            print('Deletion confirmed.')
            for delFile in self.copyList:
                try:
                    send2trash(delFile)
                except OSError as e:
                    self.infobox(str(e))
                print("%s %s" % ("file moved to trash:", delFile))
                self.statusBar().showMessage("%s %s" % ("file moved to trash:", delFile), 0)
        else:
            print('No clicked.')

    def createStatusBar(self):
        sysinfo = QSysInfo()
        myMachine = "current CPU Architecture: " + sysinfo.currentCpuArchitecture() + " *** " + sysinfo.prettyProductName() + " *** " + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        self.statusBar().showMessage(myMachine, 0)

    def contextMenuEvent(self, event,):

        contextMenu = QMenu(self)
        CreatFolderAct = contextMenu.addAction("New Folder")
        deletefileAct = contextMenu.addAction("Delete")
    #    deletefolderAct = contextMenu.addAction("Delete Folder")
        copyAct = contextMenu.addAction("Copy")
  #      copyfolderAct = contextMenu.addAction("Copy Folder")
        pasteAct = contextMenu.addAction("Paste")
        renameAct = contextMenu.addAction("Rename")
        #renamefolderAct =contextMenu.addAction("Rename Folder")
   #    pastefolderAct = contextMenu.addAction("Paste Folder")
    #  deletefolderAct = contextMenu.addAction("Quit")

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == CreatFolderAct:
            self.createNewFolder()
        elif action == deletefileAct :
            self.deleteFile()
      #  elif action == deletefolderAct:
        #    self.deleteFolder()
        elif action == copyAct:
            self.copyFile()
        #elif action == copyfolderAct:
         #   self.copyFolder()
        elif action == pasteAct :
            self.pasteFile()
      #  elif action == pastefolderAct:
       #     self.pasteFolder()
        elif action == renameAct:
            self.renameFile()
        #elif action == renamefolderAct:
         #   self.renameFolder()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = myWindow()
    w.show()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(path)
        w.listview.setRootIndex(w.fileModel.setRootPath(path))
        w.treeview.setRootIndex(w.dirModel.setRootPath(path))
        w.setWindowTitle(path)
    sys.exit(app.exec_())









