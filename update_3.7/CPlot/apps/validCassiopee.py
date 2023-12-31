# *Cassiopee* GUI for validation and tests
try: import Tkinter as TK
except: import tkinter as TK
try: import tkFont as Font
except: import tkinter.font as Font
import os, sys, re, signal, platform
import subprocess 
import threading
import time
import KCore
import KCore.Dist as Dist
import CPlot.Tk as CTK

# CASSIOPEE var
# doit etre le chemin des sources avec les tests unitaires
CASSIOPEE = os.getenv('CASSIOPEE_SOURCES')
if CASSIOPEE is None or CASSIOPEE == '':
    CASSIOPEE = os.getenv('CASSIOPEE')
    if CASSIOPEE is None or CASSIOPEE == '':
        print('Error: CASSIOPEE must be present in your environement.')
        sys.exit()

# CFD Base
CFDBASEPATH = '/Validation/Cases'

# Systeme
mySystem = Dist.getSystem()[0]

# Machine name
import socket
machine = socket.gethostname()

# Support MPI?
try: 
    import mpi4py
    isMpi = True
except: isMpi = False

# Check svn version
CHECKSVNVERSION = True

# Regexprs
regDiff = re.compile('DIFF')
regFailed = re.compile('FAILED')
regError = re.compile('Error')
regErreur = re.compile('Erreur') # because of french system
regAbort = re.compile('Aborted')
regSegmentation = re.compile('Segmentation')
separator = ':'
separatorl = separator+' '
expTest1 = re.compile("_t[0-9]+") # normal tests
expTest2 = re.compile(".py")
expTest3 = re.compile("\~")
expTest4 = re.compile("_m[0-9]+") # distributed tests

# Liste des tous les tests obtenue en listant les repertoires
# Un element de la liste est une string comme affichee dans la listbox
TESTS = []
# Repertoire 'module' des modules
MODULESDIR = {}

# Si THREAD est None, les test unitaires ne tournent pas
# Sinon, THREAD vaut le thread lance
THREAD = None
# Le process lance sinon None
PROCESS = None

# Est egal a 1 si on doit s'arreter
STOP = 0

# WIDGETS dict
WIDGETS = {}

# Cree sessionLog et le vide
if not os.path.exists(CASSIOPEE+'/Apps/Modules/ValidData'):
    os.mkdir(CASSIOPEE+'/Apps/Modules/ValidData')
    
f = open(CASSIOPEE+"/Apps/Modules/ValidData/session.log", "w")
f.write("")
f.close()

#==============================================================================
# Simulate check_output since it doesn't existe for early version of python
# Retourne le resultat de cmd comme une string
#==============================================================================
def check_output(cmd, shell, stderr):
    global PROCESS
    version = sys.version_info
    version0 = version[0]
    version1 = version[1]
    mode = 4

    #if (version0 == 2 and version1 >= 7) or (version0 == 3 and version1 >= 2) or version0 > 3:
    
    if mode == 0: # avec check_output
        out = subprocess.check_output(cmd, shell=shell, stderr=stderr)
        return out
    elif mode == 1: # avec run
        PROCESS = subprocess.run(cmd, check=True, shell=shell, stderr=stderr, stdout=subprocess.PIPE)
        return PROCESS.stdout
    elif mode == 2: # avec Popen + python 2.7
        import shlex
        cmd = shlex.split(cmd)
        
        wdir = '.'
        # modifie cd en working dir
        if cmd[0] == 'cd': wdir = cmd[1]; cmd = cmd[3:]
        PROCESS = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=wdir)
        out = ''
        while True:
            line = PROCESS.stdout.readline()
            if line != '': out += line
            else: break
        ti = ''
        while True:
            line = PROCESS.stderr.readline()
            if line != '': ti += line
            else: break
        # change le retour de time pour etre identique a celui du shell
        i1 = ti.find('elapsed')
        i2 = ti.find('system')
        if i1 != -1 and i2 != -1:
            ti = 'real '+ti[i2+7:i1]
            ti = ti.replace(':', 'm')
            ti += 's'
            out += ti
        return out
        
    elif mode == 3: # avec Popen + python 3
        cmd = cmd.split(' ')
        wdir = '.'
        # modifie cd en working dir
        if cmd[0] == 'cd': wdir = cmd[1]
        if mySystem == 'windows' or mySystem == 'mingw': cmd = cmd[3:]
        else: cmd = cmd[2:]
        if wdir[-1] == ';': wdir = wdir[:-1]
        PROCESS = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=wdir, shell=shell)
        out = b''
        while True:
            line = PROCESS.stdout.readline()
            if line != b'': out += line
            else: break
        ti = b''
        while True:
            line = PROCESS.stderr.readline()
            if line != b'': ti += line
            else: break
        # change le retour de time pour etre identique a celui du shell
        i1 = ti.find(b'elapsed')
        i2 = ti.find(b'system')
        if i1 != -1 and i2 != -1:
            ti = b'real '+ti[i2+7:i1]
            ti = ti.replace(b':', b'm')
            ti += b's'
            out += ti
        return out

    elif mode == 4: # inspire de python
        wdir = '.'; ossid = None
        if mySystem == 'windows' or mySystem == 'mingw': ossid = None
        else: ossid = os.setsid
        PROCESS = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=wdir, shell=shell, preexec_fn=ossid)
        
        stdout, stderr = PROCESS.communicate(None, timeout=60.*1.) # max accepted time is 1 minute for one test
        
        if PROCESS.wait() != 0: stderr += b'\nError: process FAILED (Segmentation Fault or floating point exception).'
        PROCESS = None # fini!
        return stdout+stderr

# retourne une chaine justifiee en fonction de la font et
# d'une taille voulue
def ljust(text, size):
    if generalFontFixed == 1:
        # for mono fonts (faster)
        form = '{:%d}'%size
        return form.format(text)
    else:
        l = generalFont.measure(text)*1.
        l = int(round((size*generalFontA-l)/generalFontS))
        if l > 0:
            form = '{}{:%d}'%l
            return form.format(text, ' ')
        else: return text
    
#==============================================================================
# build a test string:
# 0       1         2         3             4     5         6       7
# module, testname, CPU time, ref CPU time, date, coverage, status, tag
# IN: module, test: test concerne
# IN: CPUtime: nouveau CPU time
# IN: coverage: nouveau coverage
# IN: status: nouveau status
# Recupere les anciennes donnees dans le fichier time
#==============================================================================
def buildString(module, test, CPUtime, coverage, status):
    if module == 'CFDBase':
        path = CASSIOPEE+CFDBASEPATH
        fileTime = '%s/%s/Data/%s.time'%(path, test, test)
    else:
        modulesDir = MODULESDIR[module]
        path = CASSIOPEE+'/Apps/'+modulesDir
        testr = os.path.splitext(test)
        fileTime = '%s/%s/test/Data/%s.time'%(path, module, testr[0])
    a = os.access(fileTime, os.F_OK)
    if a:
        f = open(fileTime, 'r')
        list = f.read()
        f.close()
        list = list.split('\n')
        if len(list) > 0: refDate = list[0]
        else: refDate = '...'
        if len(list) > 1: refCPUtime = list[1]
        else: refCPUtime = '...'
        if len(list) > 3 and list[2] != '': refCoverage = list[2]
        else: refCoverage = '...%'
    else:
        refDate = '...'
        refCPUtime = '...'
        refCoverage = '...%'

    # Not very useful
    #fileStar = '%s/%s/test/Data%s.star'%(path, module, testr[0])
    #a = os.access(fileStar, os.F_OK)
    #if a:
    #    f = open(fileStar, 'r')
    #    list = f.read()
    #    f.close()
    #    list = list.split('\n')
    #    if (len(list) > 0): refStar = list[0]
    #    else: refStar = ' '
    #else: refStar = ' '
    refStar = ' '

    execTime = '../../.. ..h..'
    if status != '...': # Not First call
        execTime = time.strftime('%d/%m/%y %Hh%M', time.localtime())

    if coverage == '...%': coverage = refCoverage

    #s = module.ljust(13)+separatorl+test.ljust(40)+separatorl+\
    #    CPUtime.ljust(10)+separatorl+refCPUtime.ljust(10)+separatorl+\
    #    refDate.ljust(16)+separatorl+coverage.ljust(5)+separatorl+\
    #    status.ljust(7)+separatorl+refStar.ljust(5)
    s = ljust(module, 13)+separatorl+ljust(test, 40)+separatorl+\
        ljust(CPUtime, 10)+separatorl+ljust(refCPUtime, 10)+separatorl+\
        ljust(refDate, 16)+separatorl+ljust(coverage, 5)+separatorl+' '+\
        ljust(status, 7)
    #s = '{}{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(ljust(module, 13), separatorl,
    #    ljust(test, 40), separatorl, ljust(CPUtime, 10), separatorl,
    #    ljust(refCPUtime, 10), separatorl,
    #    ljust(refDate, 16), separatorl, ljust(coverage, 5), separatorl, ' ',
    #    ljust(status, 7))
    #s = '{:13}{}{:40}{}{:10}{}{:10}{}{:16}{}{:5}{}{}{:7}'.format(module, separatorl,
    #    test, separatorl, CPUtime, separatorl,
    #    refCPUtime, separatorl,
    #    refDate, separatorl, coverage, separatorl, ' ',
    #    status)
    
    return s

#==============================================================================
# Retourne la liste des modules situes dans Apps/Modules et dans Apps/PModules
# Eventuellement peut ajouter "CFDBase", nom referencant les tests
# de validation des solveurs (CFDBase)
#==============================================================================
def getModules():
    # Tests unitaires des modules
    print('Info: Getting tests in:%s.'%CASSIOPEE)
    modules = []

    path = CASSIOPEE+'/Apps/PModules'
    try: mods = os.listdir(path)
    except: mods = []
    notTested = ['Upmost', 'FastP']
    for i in mods:
        if i not in notTested and i not in modules:
            a = os.access('%s/%s/test'%(path,i), os.F_OK)
            if a:
                modules.append(i)
                MODULESDIR[i] = 'PModules'

    path = CASSIOPEE+'/Apps/Modules'
    try: mods = os.listdir(path)
    except: mods = []
    for i in mods:
        if i not in modules:
            a = os.access('%s/%s/test'%(path,i), os.F_OK)
            if a: 
                modules.append(i)
                MODULESDIR[i] = 'Modules'
    
    # Validation CFD
    modules.append('CFDBase')
    MODULESDIR['CFDBase'] = ''
    return modules

#==============================================================================
# Retourne la liste des tests unitaires d'un module
# si module == 'CFDBase', retourne la liste des cas de validation CFD
#==============================================================================
def getTests(module):
    a = []
    if module == 'CFDBase': a += getCFDBaseTests()
    else: a += getUnitaryTests(module)
    return a

#==============================================================================
# Retourne la liste des tests unitaires pour un module donne
# Les tests unitaires doivent etre dans module/test
#==============================================================================
def getUnitaryTests(module):
    modulesDir = MODULESDIR[module]
    path = '%s/Apps/%s/%s/test'%(CASSIOPEE, modulesDir, module)
    files = os.listdir(path)
    tests = []
    for f in files:
        m2 = expTest2.search(f)
        if m2 is None: continue
        m3 = expTest3.search(f)
        if m3 is not None: continue
        if f[0] == '#': continue
        m1 = expTest1.search(f)
        m4 = expTest4.search(f)
        if m1 is not None: tests.append(f) # test seq
        elif isMpi and m4 is not None: tests.append(f) # test mpi
    return tests

#==============================================================================
# Retourne la liste des cas de validation CFD (CFDBase)
# Il doivent etre dans Validation/Cases
#==============================================================================
def getCFDBaseTests():
    path = CASSIOPEE+CFDBASEPATH
    try: reps = os.listdir(path)
    except: reps = []
    out = []
    for r in reps: # a terme a supprimer
        if r == 'NACA': out.append(r) # MB 2D Euler
        elif r == 'NACA_IBC': out.append(r) # IBC 2D Euler
        elif r == 'DAUPHIN': out.append(r) # MB 3D Euler
        elif r == 'FLATPLATE': out.append(r) # MB 3D SA
        elif r == 'RAE2822': out.append(r) # MB 2D SA
        elif r == 'RAE2822_IBC': out.append(r) # IBC 2D SA
        elif r == 'CUBE_IBC': out.append(r) # IBC 3D SA
    return out

#==============================================================================
# Ecrit un fichier contenant date, CPUtime, coverage
#==============================================================================
def writeTime(file, CPUtime, coverage):
    try:
        execTime = time.strftime('%d/%m/%y %Hh%M',time.localtime())
        f = open(file, 'w')
        f.write(execTime+'\n')
        f.write(CPUtime+'\n')
        f.write(coverage+'\n')
        f.close()
    except: pass

#==============================================================================
# Ecrit un fichier contenant date, machine, nbre de threads, svnVersion 
# et logTxt
#==============================================================================
def writeFinal(file, svnVersion=None, logTxt=None, append=False):
    execTime = time.strftime('%d/%m/%y %Hh%M', time.localtime())
    machine = platform.uname()
    if len(machine) > 1: machine = machine[1]
    else: machine = 'Unkwown'
    nthreads = Threads.get()
    mode = 'w'
    if append: mode = 'a'
    f = open(file, 'w')
    f.write(execTime+'\n')
    f.write(machine+'\n')
    f.write(nthreads+'\n')
    if svnVersion is not None: f.write(svnVersion+'\n')
    if logTxt is not None: f.write(logTxt+'\n')
    f.close()

#==============================================================================
# Update star dans un fichier star
# Star est cense etre a la quatrieme et derniere ligne
#==============================================================================
def writeStar(file, star):
    try:
        f = open(file, 'w')
        f.write(star+'\n')
        f.close()
    except: pass

#==============================================================================
# Lance un seul test unitaire ou un cas de la base de validation
#==============================================================================
def runSingleTest(no, module, test):
    if module == 'CFDBase': return runSingleCFDTest(no, module, test)
    else: return runSingleUnitaryTest(no, module, test)

#==============================================================================
# extrait le temps CPU d'un chaine output (utile sur windows)
# retourne le temps CPU comme une chaine
#==============================================================================
def extractCPUTime(output1, output2):
    CPUtime = 'Unknown'
    split1 = output1.split(':')
    h1 = int(split1[0])
    m1 = int(split1[1])
    s1 = split1[2]; s1 = s1.split(',')
    ms1 = int(s1[1])
    s1 = int(s1[0])
    t1 = h1*3600. + m1*60. + s1 + 0.01*ms1
    split2 = output2.split(':')
    h2 = int(split2[0])
    m2 = int(split2[1])
    s2 = split2[2]; s2 = s2.split(',')
    ms2 = int(s2[1])
    s2 = int(s2[0])
    t2 = h2*3600. + m2*60. + s2 + 0.01*ms2
    tf = t2-t1
    hf = int(tf/3600.)
    tf = tf - 3600*hf
    mf = int(tf/60.)
    tf = tf - 60*mf
    sf = int(tf*100)/100.
    if hf > 0: CPUtime = '%dh%dm%gs'%(hf,mf,sf)
    else: CPUtime = '%dm%gs'%(mf,sf)
    return CPUtime

#=============================================================================
# Extrait le temps CPU d'une sortie time -p (unix)
#=============================================================================
def extractCPUTime2(output):
    i1 = output.find('real')
    output = output[i1+4:]
    output = output.replace(',', '.')
    output = output.lstrip()
    i2 = output.find(' ')
    if i2 != -1: output = output[:i2]
    i3 = output.find('\n')
    if i3 != -1: output = output[:i3]
    i1 = output.find('h')
    hf = 0; mf = 0; sf = 0
    if i1 != -1:
        hf = output[:i1]
        try: hf = float(hf)
        except: hf = 0.
        output = output[i1+1:]
    i1 = output.find('m')
    if i1 != -1:
        mf = output[:i1]
        try: mf = float(mf)
        except: mf = 0.
        output = output[i1+1:]
    sf = output.replace('s', '')
    try: sf = float(sf)
    except: sf = 0.
    tf = hf*3600.+mf*60.+sf
    hf = int(tf/3600.)
    tf = tf - 3600*hf
    mf = int(tf/60.)
    tf = tf - 60*mf
    sf = int(tf*100)/100.
    if hf > 0: CPUtime = '%dh%dm%gs'%(hf,mf,sf)
    else: CPUtime = '%dm%gs'%(mf,sf)
    return CPUtime

#==============================================================================
# Lance un seul test unitaire de module
#==============================================================================
def runSingleUnitaryTest(no, module, test):
    testr = os.path.splitext(test)
    modulesDir = MODULESDIR[module]
    path = '%s/Apps/%s/%s/test'%(CASSIOPEE, modulesDir, module)

    m1 = expTest1.search(test) # seq ou distribue

    pythonExec = os.getenv('PYTHONEXE', 'python')
    nthreads = KCore.kcore.getOmpMaxThreads()

    if mySystem == 'mingw' or mySystem == 'windows':
        # Commande Dos (sans time)
        path = path.replace('/', '\\')
        if m1 is not None: cmd = 'cd %s && %s %s'%(path, pythonExec, test)
        else: cmd = 'cd %s && set OMP_NUM_THREADS=%d && mpiexec -np 2 %s %s'%(path, nthreads//2, pythonExec, test)
        cmd2 = 'echo %time%'
    else:
        # Unix - le shell doit avoir l'environnement cassiopee
        #sformat = r'"real\t%E\nuser\t%U\nsys\t%S"'
        if m1 is not None: cmd = 'cd %s; time %s %s'%(path, pythonExec, test)
        else: cmd = 'cd %s; time kpython -n 2 -t %d %s'%(path, nthreads//2, test)
    try:
        if mySystem == 'mingw' or mySystem == 'windows':
            output1 = check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
            if sys.version_info[0] == 3: output1 = output1.decode()
        output = check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        if sys.version_info[0] == 3: output = output.decode()
        
        if mySystem == 'mingw' or mySystem == 'windows':
            output2 = check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
            if sys.version_info[0] == 3: output2 = output2.decode()
        
        print(output)
        
        # Recupere success/failed
        success = True
        if regDiff.search(output) is not None: success = False
        if regFailed.search(output) is not None: success = False
        if regError.search(output) is not None: success = False
        if regErreur.search(output) is not None: success = False
        if regAbort.search(output) is not None: success = False
        if regSegmentation.search(output) is not None: success = False

        # Recupere le CPU time
        if mySystem == 'mingw' or mySystem == 'windows':
            try: CPUtime = extractCPUTime(output1, output2)
            except: CPUtime = 'Unknown'
        else:
            i1 = output.find('\nreal')
            if i1 == -1: CPUtime = 'Unknown'
            else:
                try: CPUtime = extractCPUTime2(output)
                except: CPUtime = 'Unknown'
                #CPUtime = output[i1+5:i1+15]; CPUtime = CPUtime.strip()

        # Recupere le coverage
        i1 = output.find('coverage=')
        if i1 == -1: coverage = '0%'
        else:
            sub = output[i1+9:i1+13]
            i1 = sub.find('%')
            coverage = sub[:i1+1]
            coverage = coverage.strip()

    except subprocess.TimeoutExpired:
        # killed here because timeout of communicate doesnt kill child processes
        if mySystem == 'mingw' or mySystem == 'windows':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(PROCESS.pid)])
        else: # unix
            # try soft, then hard
            os.killpg(os.getpgid(PROCESS.pid), signal.SIGTERM)
            os.kill(PROCESS.pid, signal.SIGTERM)
            os.killpg(os.getpgid(PROCESS.pid), signal.SIGKILL)
            os.kill(PROCESS.pid, signal.SIGKILL)
        print('\nError: process TIMED OUT (killed).')
        success = False; CPUtime = 'Unknown'; coverage='0%' # Core dump/error

    except Exception as e:
        print(e)
        success = False; CPUtime = 'Unknown'; coverage='0%' # Core dump/error

    # update le fichier .time (si non present)
    fileTime = '%s/Data/%s.time'%(path, testr[0])
    if not os.access(fileTime, os.F_OK):
        writeTime(fileTime, CPUtime, coverage)

    # update status
    if success: status = 'OK'
    else: status = 'FAILED'
    s = buildString(module, test, CPUtime, coverage, status)
    c = 0
    regTest = re.compile(' '+test+' ')
    regModule = re.compile(module+' ')
    for tt in TESTS:
        if regTest.search(tt) is not None:
            if regModule.search(tt) is not None: TESTS[c] = s
        c += 1
    listbox.delete(no, no)
    listbox.insert(no, s)
    listbox.update()
    CPUtime = string2Time(CPUtime)
    return CPUtime

#==============================================================================
# Lance un seul test de la base CFD (CFDBase)
# module = 'CFDBase'
# test = nom du repertoire du cas CFD
#==============================================================================
def runSingleCFDTest(no, module, test):

    print('Info: Running CFD test %s.'%test)
    path = CASSIOPEE+CFDBASEPATH+'/'+test

    m1 = None # si None=seq
    if test == 'RAE2822_IBC': m1 = True
    try: import mpi4py
    except: m1 = None

    if mySystem == 'mingw' or mySystem == 'windows':
        # Commande Dos (sans time)
        path = path.replace('/', '\\')
        if m1 is None: cmd = 'cd %s && ./valid check'%(path)
        else: cmd = 'cd %s && ./valid check 0 0 0 2 4'%(path)
        cmd2 = 'echo %time%'
    else:
        # Unix - le shell doit avoir l'environnement cassiopee
        if m1 is None: cmd = 'cd %s; ./valid check'%(path)
        else: cmd = 'cd %s; ./valid check 0 0 0 2 4'%(path)
    try:
        if mySystem == 'mingw' or mySystem == 'windows':
            output1 = check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
            output1 = output1.decode()
        output = check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        output = output.decode()
        if mySystem == 'mingw' or mySystem == 'windows':
            output2 = check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
            output2 = output2.decode()
        
        print(output)

        # Recupere success/failed
        success = True
        if regDiff.search(output) is not None: success = False
        if regFailed.search(output) is not None: success = False
        if regError.search(output) is not None: success = False
        if regErreur.search(output) is not None: success = False
        if regAbort.search(output) is not None: success = False
        if regSegmentation.search(output) is not None: success = False

        # Recupere le CPU time
        if mySystem == 'mingw' or mySystem == 'windows':
            CPUtime = extractCPUTime(output1, output2)
        else:
            i1 = output.find('real')
            if i1 == -1: CPUtime = 'Unknown'
            else:
                try: CPUtime = extractCPUTime2(output)
                except: CPUtime = 'Unknown'
                #CPUtime = output[i1+4:i1+14]; CPUtime = CPUtime.strip()
        # Recupere le coverage
        coverage = '100%'
    except Exception as e:
        print(e)
        success = False; CPUtime = 'Unknown'; coverage='0%' # Core dump/error

    # update le fichier .time (si non present)
    fileTime = '%s/Data/%s.time'%(path, test)
    if not os.access(fileTime, os.F_OK):
        writeTime(fileTime, CPUtime, coverage)

    # update status
    if success: status = 'OK'
    else: status = 'FAILED'
    s = buildString(module, test, CPUtime, coverage, status)
    c = 0
    regTest = re.compile(' '+test+' ')
    regModule = re.compile(module+' ')
    for tt in TESTS:
        if regTest.search(tt) is not None:
            if regModule.search(tt) is not None: TESTS[c] = s
        c += 1
    listbox.delete(no, no)
    listbox.insert(no, s)
    listbox.update()
    CPUtime = string2Time(CPUtime)
    return CPUtime

#==============================================================================
# Recupere le nbre de tests selectionnes et le temps total correspondant
#==============================================================================
def getTestsTime():
    selection = listbox.curselection()
    total = len(selection)
    remaining = 0.
    for s in selection:
        t = listbox.get(s)
        splits = t.split(separator)
        remaining += string2Time(splits[3])
    return (total, remaining)

#==============================================================================
# Run selected tests
# Update TESTS, update listbox, update progression
#==============================================================================
def runTests():
    global STOP, THREAD
    selection = listbox.curselection()
    displayStatus(1)
    current = 0
    (total, remaining) = getTestsTime()
    elapsed = 0.

    for s in selection:
        no = int(s)
        t = listbox.get(s)
        splits = t.split(separator)
        module = splits[0]
        test = splits[1]
        module = module.strip()
        test = test.strip()
        current += 1; displayProgress(current, total, remaining, elapsed)
        remaining -= string2Time(splits[3])
        CPUtime = runSingleTest(no, module, test)
        elapsed += CPUtime # real elapsed time
        if STOP == 1: STOP = 0; displayStatus(0); return
    displayStatus(0)
    THREAD=None
    if len(selection) == len(TESTS): notifyValidOK()
    finalizeRun()
    
def runTestsInThread():
    global THREAD, STOP
    if THREAD is not None: return
    STOP = 0
    THREAD = threading.Thread(target=runTests)
    THREAD.start()

#==============================================================================
# Update the data base for selected tests
#==============================================================================
def updateTests():
    # Supprime les references
    selection = listbox.curselection()
    for s in selection:
        t = listbox.get(s)
        splits = t.split(separator)
        module = splits[0]
        test = splits[1]
        module = module.strip()
        test = test.strip()
        if module == 'CFDBase':
            pathl = CASSIOPEE+CFDBASEPATH+'/'+test
            test2 = test+'.time'
            test = 'post.ref*'
        else:
            modulesDir = MODULESDIR[module]
            path = CASSIOPEE+'/Apps/'+modulesDir
            d = os.path.splitext(test)
            test = d[0]+'.ref*'
            test2 = d[0]+'.time'
            pathl = '%s/%s/test'%(path,module)
        rmFile(pathl, test)
        rmFile(pathl, test2)
    # Run les tests
    runTests()

def updateTestsInThread():
    global THREAD
    if THREAD is not None: return
    THREAD = threading.Thread(target=updateTests)
    THREAD.start()

#==============================================================================
# Supprime un fichier
# IN: path: file path
# IN: file: file name
#==============================================================================
def rmFile(path, fileName):
    if mySystem == 'mingw' or mySystem == 'windows':
        path = path.replace('/', '\\')
        cmd = 'cd '+path+' && del Data\\'+fileName
    else:
        cmd = 'cd '+path+'; rm -f Data/'+fileName
    try:
        subprocess.call(cmd, shell=True, stderr=subprocess.STDOUT)
    except: pass

#==============================================================================
# Construit la liste des tests
# Update TESTS et la listBox
#==============================================================================
def buildTestList():
    global TESTS
    TESTS = []
    listbox.delete(0, TK.END)
    modules = getModules()
    for m in modules:
        tests = getTests(m)
        for t in tests:
            s = buildString(m, t, '...', '...%', '...')
            TESTS.append(s)
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

#==============================================================================
# Filtre la liste des tests avec la chaine de filter
# Update la listbox
#==============================================================================
def filterTestList(event=None):
    filter = Filter.get()
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is not None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    return True

#==============================================================================
# Ouvre un editeur sur le test (emacs)
#==============================================================================
def viewTest(event=None):
    selection = listbox.curselection()
    for s in selection:
        t = listbox.get(s)
        splits = t.split(separator)
        module = splits[0]
        test = splits[1]
        module = module.strip()
        test = test.strip()
        if module == 'CFDBase':
            pathl = CASSIOPEE+CFDBASEPATH+'/'+test
            test = 'compute.py'
        else:
            modulesDir = MODULESDIR[module]
            path = CASSIOPEE+'/Apps/'+modulesDir
            pathl = '%s/%s/test'%(path,module)
        if mySystem == 'mingw' or mySystem == 'windows':
            pathl = pathl.replace('/', '\\')
            cmd = 'cd '+pathl+' && emacs '+test
        else:
            cmd = 'cd '+pathl+'; emacs '+test
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

#==============================================================================
# Selectionne les tests affiche
# Met a jour les infos de progression
#==============================================================================
def selectAll(event=None):
    listbox.selection_set(0, TK.END)
    (total, remaining) = getTestsTime()
    displayProgress(0, total, remaining, 0.)

#==============================================================================
# Affiche les test FAILED dans la listbox
#==============================================================================
def showFailed():
    filter = 'FAILED'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is not None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#==============================================================================
# Affiche les test qui ont deja tournes dans la listbox
#==============================================================================
def showRunCases():
    filter = '\.\.\.'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#==============================================================================
# Affiche les test qui n'ont deja tournes dans la listbox
#==============================================================================
def showUnrunCases():
    filter = '\.\.\.'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is not None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#=============================================================================
# Affiche les tests couverts
#==============================================================================
def showCovered():
    filter = '100%'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is not None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#=============================================================================
# Affiche les tests non couverts (0%)
#==============================================================================
def showUncovered():
    filter = ' 0%'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if re.search(filter, s) is not None:
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#==============================================================================
# Affiche les tests partiellement couverts
#==============================================================================
def showPartialCovered():
    filter1 = '100%'
    filter2 = ' 0%'
    filter3 = '\.%'
    listbox.delete(0, TK.END)
    for s in TESTS:
        if (re.search(filter1, s) is None and re.search(filter2, s) is None
            and re.search(filter3, s) is None):
            listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#==============================================================================
# Converti une chaine de type 0m0.12s (CPU time) en secondes
#==============================================================================
def string2Time(s):
    s = s.split('m')
    if len(s) != 2: return 0. # fail
    m1 = s[0]; s1 = s[1]; s1 = s1.replace('s', '')
    try: ret = float(m1)*60.+float(s1)
    except: ret = 0.
    return ret

#==============================================================================
# Converti un temps en secondes en une chaine 0h00m00s
#==============================================================================
def time2String(time):
    secs = time
    hours = int(secs / 3600)
    secs = secs - hours*3600
    mins = int(secs / 60)
    secs = secs - mins*60
    secs = int(secs)
    return "%1dh%2dm%2ds"%(hours,mins,secs)

#==============================================================================
# Affiche les tests plus rapide que ref CPUtime dans la listbox
#==============================================================================
def showFaster():
    listbox.delete(0, TK.END)
    for s in TESTS:
        s1 = s.split(separator)
        t1 = s1[2]; t2 = s1[3]
        t1 = string2Time(t1) # new time
        t2 = string2Time(t2)
        if t1 > 0 and t2 > 0:
            if t1 < t2-0.15*t2: listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True
def showFasterP():
    listbox.delete(0, TK.END)
    for s in TESTS:
        s1 = s.split(separator)
        t1 = s1[2]; t2 = s1[3]
        t1 = string2Time(t1) # new time
        t2 = string2Time(t2)
        if t1 > 0 and t2 > 0:
            if t1 < t2-0.5*t2: listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True

#==============================================================================
# Affiche les tests plus lent que la reference de 15%
#==============================================================================
def showSlower():
    listbox.delete(0, TK.END)
    for s in TESTS:
        s1 = s.split(separator)
        t1 = s1[2]; t2 = s1[3]
        t1 = string2Time(t1) # new time
        t2 = string2Time(t2)
        if t1 > 0 and t2 > 0:
            if (t1 > t2+0.15*t2): listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True
def showSlowerP():
    listbox.delete(0, TK.END)
    for s in TESTS:
        s1 = s.split(separator)
        t1 = s1[2]; t2 = s1[3]
        t1 = string2Time(t1) # new time
        t2 = string2Time(t2)
        if t1 > 0 and t2 > 0:
            if t1 > t2+0.5*t2: listbox.insert(TK.END, s)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    Filter.set(''); text.update()
    return True


#==============================================================================
# Affiche tous les tests
#==============================================================================
def showAll():
    Filter.set(''); text.update()
    filterTestList()

#==============================================================================
# Stop l'execution des tests
#==============================================================================
def stopTests():
    global STOP, THREAD, PROCESS
    STOP = 1

    if PROCESS is not None: 
        if mySystem == 'mingw' or mySystem == 'windows':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(PROCESS.pid)])
        else: # unix
            # try soft, then hard
            os.killpg(os.getpgid(PROCESS.pid), signal.SIGTERM)
            os.kill(PROCESS.pid, signal.SIGTERM)
            os.killpg(os.getpgid(PROCESS.pid), signal.SIGKILL)
            os.kill(PROCESS.pid, signal.SIGKILL)
            
        PROCESS = None
        displayStatus(0)

    if THREAD is not None:
        print("Info: stopping thread...")
        #THREAD._stop() # kill?
        #THREAD.join() # wait
        #THREAD.terminate()
        THREAD = None
        displayStatus(0)

#==============================================================================
# Affiche le status: running/stopped
#==============================================================================
def displayStatus(status):
    if status == 0: Status.set('Stopped'); label.config(bg='red')
    else: Status.set('Running'); label.config(bg='green')
    label.update()

#==============================================================================
# Affiche la progression
# IN: current: le nbre de tests restants
# IN: total: nbre total de tests
# IN: remaining: temps restant avant la fin
# IN: elapsed: temps passe
#==============================================================================
def displayProgress(current, total, remaining, elapsed):
    Progress.set("%3d/%3d [%s/%s]"%
                 (current,total,time2String(remaining),time2String(elapsed)))
    progressLabel.update()

#==============================================================================
# Modifie le nbre de threads utilises pour la valid
#==============================================================================
def setThreads(event=None):
    nt = Threads.get()
    try:
        nti = int(nt)
        KCore.kcore.setOmpMaxThreads(nti)
        print('Info: Num threads set to %d.\n'%nti)
    except:
        print('Info: Bad thread number.\n')

#==============================================================================
# Recupere le nbre de threads (OMP_NUM_THREADS)
#==============================================================================
def getThreads():
    nt = KCore.kcore.getOmpMaxThreads()
    Threads.set(str(nt))
    text.update()

#==============================================================================
# Exporte les resultats de la valid dans un fichier texte
#==============================================================================
def export2Text():
    try: import tkFileDialog
    except: import tkinter.filedialog as tkFileDialog 
    ret = tkFileDialog.asksaveasfilename()
    if ret == '' or ret is None or ret == (): # user cancel
        return

    file = open(ret, 'w')
    for t in TESTS: file.write(t); file.write('\n')
    file.close()

#=======================================
# Finalize run : write log and baseTime
#=======================================
def finalizeRun():
    svnVersion = 'Unknown'
    if CHECKSVNVERSION:
        try:
            CASSIOPEEL = CASSIOPEE.replace('D:', '/d/') # patch pour msys2/CB
            svnInfo = subprocess.check_output("svn info %s/Apps/Modules"%CASSIOPEEL, shell=True)
            svnInfo = svnInfo.decode('utf-8', 'ignore')
            ss = svnInfo.split('\n')
            for s in ss:
                t = s.split(':')
                if 'vision' in t[0]: svnVersion = t[1]
        except: pass

    messageText = 'Base from'+CASSIOPEE+'\n'
    messageText += 'Based on version %s (can be locally modified).\n'%svnVersion
    for t in TESTS:
        messageText += t+'\n'

    # Write time stamp dans ValidData/base.time et
    # log dans ValidData/session.log
    cassiopee = os.getenv("CASSIOPEE")
    if not os.path.exists(cassiopee+'/Apps/Modules/ValidData'):
        os.mkdir(cassiopee+'/Apps/Modules/ValidData')
    writeFinal(cassiopee+'/Apps/Modules/ValidData/base.time', svnVersion)

    writeFinal(cassiopee+'/Apps/Modules/ValidData/session.log', svnVersion, 
               messageText, append=True)


#=======================================
# Notify "Commit ready" 
#=======================================
def notifyValidOK():
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    except: return
    svnVersion = 'Unknown'
    if CHECKSVNVERSION:
        try:
            CASSIOPEEL = CASSIOPEE.replace('D:', '/d/') # patch pour msys2/CB
            svnInfo = subprocess.check_output("svn info %s/Apps/Modules"%CASSIOPEEL, shell=True)
            svnInfo = svnInfo.decode('utf-8', 'ignore')
            ss = svnInfo.split('\n')
            for s in ss:
                t = s.split(':')
                if 'vision' in t[0]: svnVersion = t[1]
        except: pass

    messageText = 'Base from'+CASSIOPEE+'\n'
    messageText += 'Based on version %s (can be locally modified).\n'%svnVersion
    for t in TESTS:
        messageText += t+'\n'

    try:
        me = os.getenv('USER')+'@onera.fr'
        if me is None: me = ''
        to = 'Christophe.Benoit@onera.fr'
        msg = MIMEMultipart()
        msg['Subject'] = '[Cassiopee] Ready to commit'
        msg['From'] = me
        msg['To'] = to
        msg.preamble = 'Send by Cassiopee.'
        if messageText != '':
            msg.attach(MIMEText(messageText, 'plain'))
        s = smtplib.SMTP('localhost')
        s.sendmail(me, to, msg.as_string())
        s.quit()
    except: pass
    
#==============================================================================
def Quit(event=None):
    import os; os._exit(0)

#==============================================================================
# Ajoute une etoile a la selection
#==============================================================================
def tagSelection(event=None):
    selection = listbox.curselection()

    for s in selection:
        no = int(s)
        t = listbox.get(s)
        splits = t.split(separator)
        star = splits[7]
        star = star.strip()
        star += '*'
        test = splits[1]
        test = test.strip()
        module = splits[0]
        module = module.strip()
        modulesDir = MODULESDIR[module]
        path = CASSIOPEE+'/Apps/'+modulesDir+'/'+module+'/test'
        testr = os.path.splitext(test)
        fileStar = path+'/Data/'+testr[0]+'.star'
        writeStar(fileStar, star)
        star = ' '+star
        splits[7] = star.ljust(4)
        s = ''
        for i in splits[:-1]: s += i+separator
        s += splits[-1]
        listbox.delete(no, no)
        listbox.insert(no, s)
        listbox.update()
    return

def untagSelection(event=None):
    selection = listbox.curselection()
    for s in selection:
        no = int(s)
        t = listbox.get(s)
        splits = t.split(separator)
        star = splits[7]
        star = star.strip()
        test = splits[1]
        test = test.strip()
        module = splits[0]
        module = module.strip()
        modulesDir = MODULESDIR[module]
        path = CASSIOPEE+'/Apps/'+modulesDir+'/'+module+'/test'
        testr = os.path.splitext(test)
        fileStar = path+'/Data/'+testr[0]+'.star'
        ls = len(star)
        star = ''
        if ls > 1:
            for i in range(ls-1): star += '*'
            writeStar(fileStar, star)
        else:
            rmFile(path, testr[0]+'.star')
            star = ' '

        star = ' '+star
        splits[7] = star.ljust(4)
        s = ''
        for i in splits[:-1]: s += i+separator
        s += splits[-1]
        listbox.delete(no, no)
        listbox.insert(no, s)
        listbox.update()
    return

#===================================
# Setup for use of global data base
#===================================
def setupGlobal():
    global CASSIOPEE
    CASSIOPEE = os.getenv('CASSIOPEE')
    # Create Local directory for valid products
    if not os.path.exists(CASSIOPEE+'/Apps/Modules/ValidData'):
        os.mkdir(CASSIOPEE+'/Apps/Modules/ValidData')
    os.environ['VALIDLOCAL'] = CASSIOPEE+'/Apps/Modules/ValidData'
    # Change to global ref
    CASSIOPEE = '/stck/benoit/Cassiopee'
    # No update on global ref!
    WIDGETS['updateButton'].configure(state=TK.DISABLED)
    # Change also to match the numthreads of global
    try:
        file = open('/stck/benoit/Cassiopee/Apps/Modules/ValidData/base.time')
        d = file.read(); d = d.split('\n')
        Threads.set(d[2])
        setThreads()
    except: pass

    buildTestList()

def setupLocal():
    global CASSIOPEE
    os.environ['VALIDLOCAL'] = '.'
    CASSIOPEE = os.getenv('CASSIOPEE')
    WIDGETS['updateButton'].configure(state=TK.NORMAL)
    buildTestList()

#==============================================================================
# Main
#==============================================================================

# Main window
master = TK.Tk()
master.title('*Cassiopee* valid @ '+machine)
master.columnconfigure(0, weight=1)
master.rowconfigure(0, weight=1)
#GENERALFONT = ('Courier', 9)
GENERALFONT = ('Andale Mono', 9)

master.option_add('*Font', GENERALFONT)
generalFont = Font.Font(family=GENERALFONT[0], size=GENERALFONT[1])
generalFontS = generalFont.measure(' ')*1.
generalFontA = generalFont.measure('a')*1.
generalFontFixed = generalFont.metrics('fixed')

# Main menu
menu = TK.Menu(master)
file = TK.Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=file)
tools = TK.Menu(menu, tearoff=0)
menu.add_cascade(label='Tools', menu=tools)
view = TK.Menu(menu, tearoff=0)
menu.add_cascade(label='View', menu=view)

file.add_command(label='Export to text file', command=export2Text)
file.add_command(label='Notify Ready for commit', command=notifyValidOK)
file.add_command(label='Quit', command=Quit, accelerator='Ctrl+Q')
view.add_command(label='Show FAILED', command=showFailed)
view.add_command(label='Show ALL tests', command=showAll)
view.add_separator()
view.add_command(label='Show run cases', command=showRunCases)
view.add_command(label='Show unrun cases', command=showUnrunCases)
view.add_separator()
view.add_command(label='Show covered (100%)', command=showCovered)
view.add_command(label='Show partially covered (x%)',
                 command=showPartialCovered)
view.add_command(label='Show uncovered (0%)', command=showUncovered)
view.add_separator()
view.add_command(label='Show faster (-15%)', command=showFaster)
view.add_command(label='Show slower (+15%)', command=showSlower)
view.add_command(label='Show faster (-50%)', command=showFasterP)
view.add_command(label='Show slower (+50%)', command=showSlowerP)
view.add_separator()
view.add_command(label='Select all visible tests', command=selectAll,
                 accelerator='Ctrl+A')

tools.add_command(label='Tag selection', command=tagSelection)
tools.add_command(label='Untag selection', command=untagSelection)

try:
    file = open('/stck/benoit/Cassiopee/Apps/Modules/ValidData/base.time')
    d = file.read(); d = d.split('\n')
    d = ' ['+d[0]+'/'+d[1]+'/'+d[2]+' threads]'
except: d = ''

tools.add_command(label='Switch to global data base'+d, command=setupGlobal)
tools.add_command(label='Switch to local data base', command=setupLocal)

master.config(menu=menu)
master.bind_all("<Control-q>", Quit)
master.bind_all("<Control-a>", selectAll)

# Main frame
frame = TK.Frame(master)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.grid(row=0, column=0, sticky=TK.EW)

listbox = TK.Listbox(frame, selectmode=TK.EXTENDED, width=120, height=39,
                     background='White')
listbox.grid(row=0, column=0, columnspan=10, sticky=TK.NSEW)

scrollbar = TK.Scrollbar(frame, orient=TK.VERTICAL)
scrollbar.grid(row=0, column=10, sticky=TK.NSEW)

Status = TK.StringVar(master)
label = TK.Label(frame, textvariable=Status)
Status.set('Stopped'); label.config(bg='red')
label.grid(row=1, column=0, sticky=TK.EW)

Progress = TK.StringVar(master)
progressLabel = TK.Label(frame, textvariable=Progress)
Progress.set('  0/  0 [0h 0m 0s/0h 0m 0s]')
progressLabel.grid(row=1, column=1, sticky=TK.EW)

Filter = TK.StringVar(master)
text = TK.Entry(frame, textvariable=Filter, background='White', width=50)
text.bind('<KeyRelease>', filterTestList)
text.grid(row=1, column=2, columnspan=3, sticky=TK.EW)
BB = CTK.infoBulle(parent=text, text='Filter tests by this regexp.')

button = TK.Button(frame, text='Run', command=runTestsInThread, fg='blue')
BB = CTK.infoBulle(parent=button, text='Run selected tests.')
button.grid(row=1, column=5, sticky=TK.EW)
button = TK.Button(frame, text='Stop', command=stopTests, fg='red')
button.grid(row=1, column=6, sticky=TK.EW)
button = TK.Button(frame, text='Update', command=updateTestsInThread, fg='blue')
BB = CTK.infoBulle(parent=button, text='Update tests (replace data base files).')
WIDGETS['updateButton'] = button
button.grid(row=1, column=7, sticky=TK.EW)
button = TK.Button(frame, text='Edit', command=viewTest)
button.grid(row=1, column=8, sticky=TK.EW)

Threads = TK.StringVar(master)
text = TK.Entry(frame, textvariable=Threads, background='White', width=3)
text.grid(row=1, column=9, sticky=TK.EW)
text.bind('<Return>', setThreads)
getThreads()
BB = CTK.infoBulle(parent=text, text='Number of threads.')
frame.grid(sticky=TK.NSEW)

buildTestList()

TK.mainloop()
