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

dataFoldmg5 = "/afs/cern.ch/user/k/karjas/private/CMSSW/dataFold/mg5Cards/"

dataFold = "/afs/cern.ch/user/k/karjas/private/CMSSW/dataFold/"

tmp = "/tmp/karjas/"

flist = "{}filelist.txt".format(dataFold)
ggllfold = "/afs/cern.ch/user/k/karjas/private/CMSSW/CMSSW_9_4_0/src/DiffractiveForwardAnalysis/GammaGammaLeptonLepton/test/"


#def createCard(m1,m2):

def runMg5(eventName):
    paramCard = "{}{}.dat".format(dataFoldmg5,eventName)
    runCard = "{}run_card.dat".format(dataFoldmg5)
    mg5param = "{}slr/Cards/param_card.dat".format(tmp)
    mg5run = "{}slr/Cards/run_card.dat".format(tmp)

    mg5exe = "{}bin/mg5_aMC".format(mg5)
    slrInit = "{}slrInit.dat".format(dataFoldmg5)
    slrLaunch = "{}slrRun.dat".format(dataFoldmg5)

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

    lheOut = "{}lhe/{}.lhe.gz".format(dataFold, eventName)
    
    print("Copying the output file as {}".format(lheOut))

    shutil.copy(eventOut, lheOut)
    call(["gunzip", lheOut])
    print("extracting cross section")
    (xsec,err) = findXsec(output)
    print("Cross-section: {}+-{}fb".format(xsec,err))
    xsecStart = output.find("Cross-section :")
    
    with open(flist, "a") as myfile:
        myfile.write("{} {} {} coputed{}.root\n".format(eventName, xsec, err, eventName))

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

    driverCmdGEN = "cmsDriver.py testi.py -n {} --filein file:{} --python_filename {} --fileout file:{} --filetype=LHE --conditions auto:phase1_2017_realistic --era Run2_2017 --beamspot Realistic25ns13TeVEarly2017Collision -s GEN,SIM --mc --eventcontent RAWSIM".format(n,finGEN,fpyGEN,foutGEN)
    cmd1 = driverCmdGEN.split(" ")
    call(cmd1)

    finS1 = foutGEN
    fpyS1 = "{}pythonScripts/{}FullS1.py".format(dataFold, eventName)
    foutS1 = "{}fullStep1/{}S1.root".format(dataFold, eventName)

    driverCmdStep1 = "cmsDriver.py -s DIGI,L1,DIGI2RAW,HLT --datatier GEN-SIM-RAW --conditions auto:phase1_2017_realistic --eventcontent RAWSIM --filein file:{} --python_filename {} --fileout file:{} -n -1 --era Run2_2017 --mc".format(finS1, fpyS1, foutS1)
    
    cmd2 = driverCmdStep1.split(" ")
    call(cmd2)


    finS2 = foutS1
    fpyS2 = "{}pythonScripts/{}FullS2.py".format(dataFold, eventName)
    foutS2 = "{}Events/{}Full.root".format(dataFold, eventName)


    driverCmdStep2 = "cmsDriver.py -s RAW2DIGI,L1Reco,RECO --datatier RECO --conditions auto:phase1_2017_realistic --eventcontent AODSIM --era Run2_2017 --filein file:{} --python_filename {} --fileout file:{} -n -1 --mc".format(finS2, fpyS2, foutS2)

    cmd3 = driverCmdStep2.split(" ")
    call(cmd3)

    return

def updateRunFile(fin, fout):
    runTemp = open("{}RunGammaGammaLeptonLepton_cfg.py".format(ggllfold),'r').read()
    runTemp = runTemp.replace("FILEIN","\"file:"+fin+"\"")
    runTemp = runTemp.replace("FILEOUT", "\"file:"+fout+"\"")
    
    tmpRun = "{}runtemp.py".format(ggllfold)

    tmp = open(tmpRun,'w')
    tmp.write(runTemp)
    tmp.close()
    return tmpRun
    #print(runTemp)

def prepareComputed(eventName):

    eventRoot = "{}Events/{}.root".format(dataFold, eventName)
    ggOut = "{}GammaGammaOutput/{}.root".format(dataFold, eventName)
    tmpRun=updateRunFile(eventRoot,ggOut)

    call(["cmsRun",tmpRun])

    os.remove(tmpRun)

def runComputed(eventName):

    preparedRoot = "{}GammaGammaOutput/{}.root".format(dataFold, eventName)
    computedOut = "{}Computed/computed{}.root".format(dataFold, eventName)
    reader = "{}reader.C(\"{}\",\"{}\")".format(ggllfold,preparedRoot,computedOut)
    call(["root","-l", "-q",reader])


if __name__ == '__main__':
    


    eventName = sys.argv[1]
    fullFlag = sys.argv[2]
    N = 1000
    if len(sys.argv)==4:
        N = sys.argv[3]
    #runMg5(eventName)
    if fullFlag == "Full":
        runCMSSWFull(eventName, n = 1000)
        eventName = eventName + "Full"
    else:
        #!!!!!!!!!!
        # Works only with CMSSW 9_2_3   
        runCMSSWFast(eventName, n = 1000)

    prepareComputed(eventName)
    runComputed(eventName)































#asdasd
