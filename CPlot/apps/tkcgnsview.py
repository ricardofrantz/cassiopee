# -- cassiopee cgnsview main app --
import Converter.PyTree as C
import CPlot.Tk as CTK
import os, os.path, sys

#==============================================================================
# To be called when CTK.t is set
def run():
    
    # Set cassiopee prefs
    CTK.loadPrefFile(); CTK.setPrefs()

    # Passe la dimension par une pseudo pref
    CTK.PREFS['tkTreeWidth'] = 380
    CTK.PREFS['tkTreeHeight'] = 290

    # Main window
    (win, frames, menu, menus, file, tools) = CTK.minimal2('kcgnsview '+C.__version__,
                                                           show=False)
    fileName = os.path.split(CTK.FILE)
    CTK.changeWindowTitle(fileName[1], fileName[0])

    # Add some apps
    auto = {}
    auto['tkTreeOps'] = True
    auto['tkMeshInfo'] = True
    auto['tkPlotXY'] = False
    submenus = {}
    for app in ['tkTreeOps']: CTK.addMenuItem(app, menus[0], frames[0], submenus, auto)
    submenus = {}
    for app in ['tkMeshInfo']: CTK.addMenuItem(app, menus[4], frames[4], submenus, auto)
    try:
        import tkPlotXY
        submenus = {}
        for app in ['tkPlotXY']: CTK.addMenuItem(app, menus[10], frames[10], submenus, auto)
    except: pass
    
    # Place win devant les autres fenetres
    win.deiconify(); win.focus_set()

    # - Update apps -    
    CTK.TKTREE.updateApp()
    #if 'tkContainers' in CTK.TKMODULES: CTK.TKMODULES['tkContainers'].updateApp()
    
    # - Main loop -
    win.mainloop()

    # Del photos
    CTK.PHOTOS = []

#==============================================================================
if __name__ == "__main__":
    # Ouverture du fichier de la ligne de commande
    import sys
    if len(sys.argv) >= 2:
        files = sys.argv[1:]
        import Converter.Filter as Filter
        CTK.HANDLE = Filter.Handle(files[0])
        CTK.t = CTK.HANDLE.loadSkeleton(maxDepth=-1)
        CTK.FILE = files[0]
    run()
