import sys
import os
import shutil

from subprocess import Popen, PIPE, call





'''
Requred steps:
    1. Create mg5 param card
    2. Run mg5  OK
    3. Collect the desired event  OK
    4. Move the event from mg5 folders to cms working enviroment  OK
    5. Run cmsDriver.py with new parameters  OK
    6. Run Laurents ggll -code
    7. Run reader.c with root

'''

mg5 = "/afs/cern.ch/user/k/karjas/private/madGraphz/MG5_aMC_v2_6_2/"

combiner = "/afs/cern.ch/user/k/karjas/private/slepton_decay_analysis/combiner/"

dataFoldmg5 = "/afs/cern.ch/work/k/karjas/private/dataFold/mg5Cards/"

dataFold = "/afs/cern.ch/work/k/karjas/private/dataFold/"

oFold = "/afs/cern.ch/work/j/jmantere/public/forKristian/"
tmp = "/tmp/karjas/"

flist = "{}filelist2.txt".format(dataFold)
ggllfold = "/afs/cern.ch/work/k/karjas/private/Workspace/CMSSW_9_4_0/src/DiffractiveForwardAnalysis/GammaGammaLeptonLepton/test/"


#def createCard(m1,m2):

def runMg5(eventName):
    paramCard = "{}{}.dat".format(dataFoldmg5,eventName)
    runCard = "{}run_card.dat".format(dataFoldmg5)
    mg5param = "{}slr/Cards/param_card.dat".format(tmp)
    mg5run = "{}slr/Cards/run_card.dat".format(tmp)

    mg5exe = "{}bin/mg5_aMC".format(mg5)
    slrInit = "{}murInit.dat".format(dataFoldmg5)
    slrLaunch = "{}slrRun.dat".format(dataFoldmg5)
    
    lheOut = "{}lhe/{}.lhe.gz".format(dataFold, eventName)

    flag = checkStep("{}lhe/{}.lhe".format(dataFold,eventName))
    if not flag:
        return
    if not os.path.exists("{}slr".format(tmp)):
        print("Initializing mg5")
        call([mg5exe, slrInit])
   
    shutil.copy(paramCard, mg5param)
    shutil.copy(runCard, mg5run)
    
    print("Running mg5")

    process = Popen([mg5exe, slrLaunch], stdout=PIPE)

    (output, err) =process.communicate()
    
    runID = max(os.listdir("{}slr/Events/".format(tmp)))

    eventOut="{}slr/Events/{}/unweighted_events.lhe.gz".format(tmp,runID)

    
    print("Copying the output file as {}".format(lheOut))

    shutil.copy(eventOut, lheOut)
    call(["gunzip", lheOut])
    print("extracting cross section")
    (xsec,err) = findXsec(output)
    print("Cross-section: {}+-{}fb".format(xsec,err))
    xsecStart = output.find("Cross-section :")
    
    with open(flist, "a") as myfile:
        myfile.write("{} {} {} computed{}.root\n".format(eventName, xsec, err, eventName))

    exit_code = process.wait()

#    print(output)

def findXsec(data):
    s = data.find("Cross-section :")
    e = s
    while data[e] != '\n':
        e += 1

    substr = data[s:e]
    
    words = substr.split(" ")
    words = filter(None,words)
    print(words)
    xsec = float(words[2])*1000 #Transforming into fb
    err = float(words[4])*1000 #Transforming into fb
    print(xsec)
    print(err)
    return (xsec, err)
        

def runCMSSWFast(eventName, n = 10):
    fin = "{}lhe/{}.lhe".format(dataFold,eventName)
    fpy = "{}pythonScripts/{}.py".format(dataFold, eventName)
    fout = "{}Events/{}.root".format(dataFold, eventName)
    pup = "{}PileUps/pileUp2017.root".format(dataFold) # The pileup used in the CMSSW

    drivercmd = "cmsDriver.py testi.py -s GEN,SIM,RECOBEFMIX,DIGI:pdigi_valid,RECO --mc -n {} --conditions auto:run2_mc --era Run2_25ns --filein file:{} --filetype=LHE --python_filename {} --pileup_input file:{} --fileout file:{} --datatier GEN-SIM-RECO --eventcontent AODSIM --pileup AVE_35_BX_25ns --fast".format(n, fin, fpy, pup, fout)
    cmdArray = drivercmd.split(" ")
    call(cmdArray)

    return

def runCMSSWFull(eventName, n = 10):
    #Bad code, hyi hyi 
    #call(["cd","/afs/cern.ch/user/k/karjas/private/CMSSW/CMSSW_9_2_3/src"])
    #call(["cmsenv"])
    
    finGEN = "{}lhe/{}.lhe".format(dataFold,eventName)
    fpyGEN = "{}pythonScripts/{}FullGEN.py".format(dataFold, eventName)
    foutGEN = "{}fullGen/{}GEN.root".format(dataFold, eventName)
    #pup = "{}PileUps/pileUp2017.root".format(dataFold)
    pup ="/store/mc/RunIIFall17GS/MinBias_TuneCP5_inelasticON_13TeV-pythia8/GEN-SIM/93X_mc2017_realistic_v3-v1/30010/6654F7F1-12C4-E711-9C3A-1866DA7F93A3.root" 
    f1 = checkStep(foutGEN)

    if f1:

        driverCmdGEN = "cmsDriver.py testi.py -n {} --filein file:{} --python_filename {} --fileout file:{} --filetype=LHE --conditions auto:phase1_2017_realistic --era Run2_2017 --beamspot Realistic25ns13TeVEarly2017Collision -s GEN,SIM --mc --eventcontent RAWSIM".format(n,finGEN,fpyGEN,foutGEN)
        cmd1 = driverCmdGEN.split(" ")
        call(cmd1)

    finS1 = foutGEN
    fpyS1 = "{}pythonScripts/{}FullS1.py".format(dataFold, eventName)
    foutS1 = "{}fullStep1/{}S1.root".format(dataFold, eventName)

    f2 = checkStep(foutS1)

    if f2:

        driverCmdStep1 = "cmsDriver.py step1 --mc --eventcontent RAWSIM --pileup AVE_35_BX_25ns --datatier GEN-SIM --conditions 94X_mc2017_realistic_v11 --step DIGI,L1,DIGI2RAW,HLT --nThreads 8 --geometry DB:Extended --era Run2_2017 --filein file:{} --fileout file:{} -n {} --python_filename {}".format(finS1, foutS1, n, fpyS1)
      #  driverCmdStep1 = "cmsDriver.py -s DIGI,L1,DIGI2RAW,HLT --datatier GEN-SIM-RAW --conditions auto:phase1_2017_realistic --eventcontent RAWSIM --filein file:{} --python_filename {} --fileout file:{} -n -1 --era Run2_2017 --mc".format(finS1, fpyS1, foutS1) 
    
#--pileup_input file:{} --pileup AVE_35_BX_25ns
        cmd2 = driverCmdStep1.split(" ")
        call(cmd2)


    finS2 = foutS1
    fpyS2 = "{}pythonScripts/{}FullS2.py".format(dataFold, eventName)
    foutS2 = "{}Events/{}Full.root".format(dataFold, eventName)

    f3 = checkStep(foutS2)

    if f3:
        driverCmdStep2 = "cmsDriver.py step2 -n -1 -s RAW2DIGI,L1Reco,RECO --datatier RECO --conditions 94X_mc2017_realistic_v11 -nThreads 8 --eventcontent AODSIM --era Run2_2017 --filein file:{} --python_filename {} --fileout file:{} -n -1 --mc".format(finS2, fpyS2, foutS2)

        cmd3 = driverCmdStep2.split(" ")
        call(cmd3)

    return

def updateRunFile(fin, fout,eventName):
    runTemp = open("{}RunGammaGammaLeptonLepton_cfg.py".format(ggllfold),'r').read()
    runTemp = runTemp.replace("FILEIN","\"file:"+fin+"\"")
    runTemp = runTemp.replace("FILEOUT", "\"file:"+fout+"\"")
    
    tmpRun = "{}{}runtemp.py".format(ggllfold,eventName)

    tmp = open(tmpRun,'w')
    tmp.write(runTemp)
    tmp.close()
    return tmpRun
    #print(runTemp)

def runOskari(eventName):
    

    preparedRoot = "{}{}.root".format(oFold, eventName)
    computedOut = "{}Computed/computed{}.root".format(dataFold, eventName)
    reader = "{}reader.C(\"{}\",\"{}\")".format(ggllfold,preparedRoot,computedOut)
    call(["root","-l", "-q",reader])

    return

def prepareComputed(eventName):

    eventRoot = "{}Events/{}.root".format(dataFold, eventName)
    ggOut = "{}GammaGammaOutput/{}.root".format(dataFold, eventName)
    
    flag = checkStep(ggOut)
    if flag:
        tmpRun=updateRunFile(eventRoot,ggOut,eventName)

        call(["cmsRun",tmpRun])

        os.remove(tmpRun)

    return

def runComputed(eventName):
    preparedRoot = "{}GammaGammaOutput/{}.root".format(dataFold, eventName)
    computedOut = "{}Computed/computed{}.root".format(dataFold, eventName)
    reader = "{}reader.C(\"{}\",\"{}\")".format(ggllfold,preparedRoot,computedOut)
    call(["root","-l", "-q",reader])

    return

def checkStep(fpath):
    if os.path.exists(fpath):
        flag = raw_input(fpath+" already exists\nSkip to next step? [y/n]")
        
        if flag == "y":
            return False
        else:
            return True
    else:
        return True

def updateParameters():
    compL = []
    with open(flist, 'r') as f:
        
        line = f.readline()

        while line:
            if line[0]!='#':
                comp = line.split(" ")[3].replace('\n',"").replace("computed","")
                compL.append(comp)
            

            line = f.readline()
        compL = list(set(compL))

        f.close()
    for c in compL:
        print(c)
        cc = c.replace(".root","")
        print("{}GammaGammaOutput/{}.root".format(dataFold,cc))
        if os.path.exists("{}GammaGammaOutput/{}.root".format(dataFold,cc)):
            print("Updating " + cc)
            runComputed(cc)

    return

def ggll(fnam):
    prepareComputed(fnam)
    return

if __name__ == '__main__':
    


    eventName = sys.argv[1]
    N = 1000
    
    if eventName == "-update":
        updateParameters()

        sys.exit(1)

    if eventName == "-Oskari":
        evt = sys.argv[2]
        runOskari(evt)
        sys.exit(1)

    if eventName == "-ggll":
        ggll(sys.argv[2])
        sys.exit(1)

    fullFlag = sys.argv[2]
    if len(sys.argv)==4:
        N = sys.argv[3]
#    runMg5(eventName)
#    if fullFlag == "Full":
#        runCMSSWFull(eventName, n = 10)
#        eventName = eventName + "Full"
#    else:
        #!!!!!!!!!!
        # Works only with CMSSW 9_2_3   
#        runCMSSWFast(eventName, n = 1000)

    prepareComputed(eventName)
    runComputed(eventName)































#asdasd
