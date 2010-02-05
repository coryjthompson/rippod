#Import needed Modules
try:
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
except:
    print "Mutagen modules not found"
    sys.exit(1)

try:
    import os, sys, shutil, unicodedata
except:
    print "Common python modules not found"
    sys.exit(1)

try:
	import wx
	from wx.lib.mixins.listctrl import CheckListCtrlMixin
	from wx.lib.mixins.listctrl import ColumnSorterMixin
except:
    print "WXpython was not found"
    sys.exit(1)


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        #ColumnSorterMixin.__init__(self,len(self.test))
        #ListCtrlAutoWidthMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)



class MainWindow(wx.App):
    def OnInit(self):
        """Initialize the application"""
        
        #If no ipod is detected, warn the user.
        if (len(self.scanForIpod()) < 1):
            wx.MessageBox('No Ipod was detected! Please connect your Ipod now', 'Info')
        
        self.startFrame = wx.Frame(None, -1, "RipPod", size =(400,400))
        self.createStartInterface()
        self.startFrame.Show()
        return True


    def createStartInterface(self):
        """Creates the interface"""
	   #Create Widget
        self.btRipPodImage = wx.StaticBitmap(self.startFrame, -1, wx.Bitmap("rippod.gif", wx.BITMAP_TYPE_ANY))
        self.lblRipPod = wx.StaticText(self.startFrame, -1, "Welcome to RipPod")
        self.lblGetStarted = wx.StaticText(self.startFrame, -1, "To get started select iPod")
        self.cbSelectIpod = wx.Choice(self.startFrame, -1, choices=[])
        foundIpods = self.scanForIpod()
        self.cbSelectIpod.Bind(wx.EVT_CHOICE, self.onIpodSelected)
        self.cbSelectIpod.AppendItems(strings=foundIpods)
        self.lblCreatedBy = wx.StaticText(self.startFrame, -1, "Created by Cory Thompson")

	    #Set properties
        self.lblRipPod.SetMinSize((148, 25))
        self.lblRipPod.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lblGetStarted.SetMinSize((165, 25))
        self.cbSelectIpod.SetMinSize((300, 28))

	    #Set Layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.btRipPodImage, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        mainSizer.Add((20, 40), 0, 0, 0)
        mainSizer.Add(self.lblRipPod, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        mainSizer.Add(self.lblGetStarted, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        mainSizer.Add(self.cbSelectIpod, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        mainSizer.Add((20, 20), 1, 0, 0)
        mainSizer.Add(self.lblCreatedBy, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.startFrame.SetSizer(mainSizer)
        mainSizer.Fit(self.startFrame)

    def createMainInterface(self):
        """Create Main interface"""
    
        #Create Widgets
        self.lblOutput = wx.StaticText(self.mainFrame, -1, "Output Folder:")
        self.txtOutput = wx.TextCtrl(self.mainFrame, -1, "")
        self.btnOutputDirectorySelect = wx.Button(self.mainFrame, -1, "...")
        self.btnStart = wx.Button(self.mainFrame, -1, "Start")        
        self.lstMain=CheckListCtrl(self.mainFrame)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.lstMain.InsertColumn(0,"Title")
        self.lstMain.InsertColumn(1,"Artist")
        self.lstMain.InsertColumn(2,"Album")
        self.lstMain.InsertColumn(3,"Location")

        for f in (self.getMusicFiles(self.cbSelectIpod.GetStringSelection()+"/iPod_Control/Music")):
            try:
                 index = self.lstMain.InsertStringItem(sys.maxint, self.removeDisallowedFilenameChars(str(f[0])))
                 self.lstMain.SetStringItem(index, 1, self.removeDisallowedFilenameChars(str(f[1])))
                 self.lstMain.SetStringItem(index, 2, self.removeDisallowedFilenameChars(str(f[2])))
                 self.lstMain.SetStringItem(index,3,str(f[3]))
                 #self.lstMain.SetItemData(index, i)
                 
            except:
                print "Fail Bus"
        
#self.btnOutputDirectorySelect.Bind(wx.EVT_BUTTON, self.onbtnDirectoryClick)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.lstMain,5,wx.ALL|wx.EXPAND,5)
        subSizer = wx.BoxSizer(wx.HORIZONTAL)
        subSizer.Add(self.lblOutput, 0, wx.ALL, 10)
        subSizer.Add(self.txtOutput, 1, wx.TOP, 5)
        subSizer.Add(self.btnOutputDirectorySelect, 0, wx.TOP, 5)
        mainSizer.Add(subSizer, 0, wx.EXPAND, 0)
        mainSizer.Add(self.btnStart, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.mainFrame.SetSizer(mainSizer)

    

    def onIpodSelected(self,event):
        self.startFrame.Hide()
        wx.MessageBox(self.cbSelectIpod.GetStringSelection())
        self.mainFrame = wx.Frame(None, -1, "RipPod", size =(400,800))
        self.createMainInterface()
        self.mainFrame.Show()


    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)



    def onbtnDirectoryClick(self,event):
        """ Displays a Popup Box to allow user to choose a directory"""
        dialog = wx.DirDialog(None, "Please choose your project directory:",style=1 , pos = (10,10))
        if dialog.ShowModal() == wx.ID_OK:
	    if(os.name == "nt"):
                self.txtOutput.SetValue(dialog.GetPath() + "\\")   
	    else:
                self.txtOutput.SetValue(dialog.GetPath() + "/") 
        else:
            dialog.Destroy()
        

    def scanForIpod(self):
        foundDrives = []
        if os.name == "nt":
            for i in range(ord('a'), ord('z')+1):
                drive = chr(i)
                if(os.path.exists(drive +":\\iPod_Control\\")):
                    foundDrives.append(drive.upper() + ":\\")
        else:
            for i in os.listdir("/media/"):
                if(os.path.isdir("/media/" + i + "/iPod_Control")):
                    foundDrives.append("/media/" +i)
                
        return foundDrives

    def getMusicFiles(self,targetDir):
        musicFiles = []
        for current, dirs, files in os.walk(targetDir,True):
            for f in files:
                
                if f.lower().endswith(".mp3"):
                    try:
                        musicFile = MP3(os.path.join(targetDir,current,f))
                                      #Song Title             #Artists               #Album                #File location
                        musicFiles.append([musicFile.get("TIT2"), musicFile.get("TPE1"), musicFile.get("TALB"),os.path.join(targetDir,current,f)])
                    except:
                        continue
                        print "Fail"
                elif f.lower().endswith(".m4a"):
                    try:
                        musicFile = MP4(os.path.join(targetDir,current,f))
                                       #Song Title                #Artists                  #Album                   #File location
                        musicFiles.append([musicFile.get("\xa9nam"), musicFile.get("\xa9ART"),  musicFile.get("\xa9alb"),os.path.join(targetDir,current,f)])
                    except:
                        continue
                        print "Fail"
        return musicFiles

    #fixes invalid characters
    def removeDisallowedFilenameChars(self,fileName):
        output =  "".join([x for x in fileName if x.isalpha() or x.isdigit() or x == " " or x =="."])
        if output[-1:] == " ":
            output = output[:-1]
        return output
    
    def onbtnStartBackup(self,event):
        sourceDirectory = self.ddSource.GetStringSelection()
        outputDirectory = self.txtOutput.Value


        musicFiles = self.getMusicFiles(sourceDirectory)

        counter = 0
        dialog = wx.ProgressDialog ( 'Progress', 'Doing nothing in a large amount of time.', maximum = len(musicFiles), style = wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME )
        for files in musicFiles:
            
            if files.lower().endswith(".mp3"):
                musicFile = MP3(files)
        
                musicTitle = musicFile.get("TIT2")
                musicArtist = musicFile.get("TPE1")
                musicAlbum = musicFile.get("TALB")
        
            elif files.lower().endswith(".m4a"):
                musicFile = M4A(files)

                musicTitle = musicFile.get("\xa9nam")
                musicArtist = musicFile.get("\xa9ART")
                musicAlbum = musicFile.get("\xa9alb")
        
            else:
                print "For some reason we included the wrong file in search. SKIPPING"
                continue

            if (musicTitle == None) or (musicTitle==""):
                musicTitle = "Unknown Track"
            if (musicArtist == None) or (musicArtist==""):
                musicArtist = "Various Artist"
            if (musicAlbum == None) or (musicAlbum == ""):
                musicAlbum = "Unknown Album"
            print musicTitle
            dialog.Update(counter, self.removeDisallowedFilenameChars(musicTitle))
            currentDirectory = os.path.join(outputDirectory,self.removeDisallowedFilenameChars(str(musicArtist)))
            if not os.path.isdir(currentDirectory):
                os.mkdir(currentDirectory)

            currentDirectory = os.path.join(currentDirectory,self.removeDisallowedFilenameChars(str(musicAlbum)))
            if not os.path.isdir(currentDirectory):
                os.mkdir(currentDirectory)
            try:
                shutil.copy(files, os.path.join(currentDirectory,self.removeDisallowedFilenameChars(str(musicTitle)+files[-4:])))
            except:
                print "File SKIPPED"
            counter = counter + 1
            
         
   
app = MainWindow()
app.MainLoop()
