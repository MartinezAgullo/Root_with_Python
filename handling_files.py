# -*- coding: utf-8 -*-
import sys, os

config_process_list = ['qcd', 'zdiboson', 'wjets', 'top', 'tchannel', 'data']

def humble_DB(filename):

    process = ""
    mclist  = ""
    
    if len(config_process_list) <= 6:
        mclist = {#'105985':'zdiboson',
                  #'105986':'zdiboson',
                  #'105987':'zdiboson',
                  '110503':'tchannel',
                  '110090':'tchannel',
                  '110091':'tchannel',
                  '110101':'tchannel',
                  '117788':'tchannel',
                  '117789':'tchannel',
                  '117790':'tchannel',
                  '117791':'tchannel',
                  '117792':'tchannel',
                  '110069':'tchannel',
                  '110502':'tchannel',
                  '110503':'tchannel',
                  '110504':'tchannel',
                  '110505':'tchannel',
                  '110506':'tchannel',
                  '110507':'tchannel',
                  '110508':'tchannel',
                  '110404':'top',
                  '110119':'top',
                  '110140':'top',
                  '167740':'wjets',
                  '167741':'wjets',
                  '167742':'wjets',
                  '167743':'wjets',
                  '167744':'wjets',
                  '167745':'wjets',
                  '167746':'wjets',
                  '167747':'wjets',
                  '167748':'wjets',
                  '167749':'zdiboson',
                  '167750':'zdiboson',
                  '167751':'zdiboson',
                  '167752':'zdiboson',
                  '167753':'zdiboson',
                  '167754':'zdiboson',
                  '167755':'zdiboson',
                  '167756':'zdiboson',
                  '167757':'zdiboson',
                  '183585':'zdiboson',
                  '183586':'zdiboson',
                  '183587':'zdiboson',
                  '183588':'zdiboson',
                  '183589':'zdiboson',
                  '183590':'zdiboson',
                  '183734':'zdiboson',
                  '183735':'zdiboson',
                  '183736':'zdiboson',
                  '183737':'zdiboson',
                  '183738':'zdiboson',
                  '183739':'zdiboson'}

    else:
        mclist = {'105985':'diboson',
                  '105986':'diboson',
                  '105987':'diboson',
                  '110503':'tchannel',
                  '110090':'tchannel',
                  '110091':'tchannel',
                  '110101':'tchannel',
                  '117788':'tchannel',
                  '117789':'tchannel',
                  '117790':'tchannel',
                  '117791':'tchannel',
                  '117792':'tchannel',
                  '110069':'tchannel',
                  '110404':'ttbar',
                  '110119':'schannel',
                  '110140':'wtchannel',
                  '167740':'wbb',
                  '167741':'wcc',
                  '167742':'wlight',
                  '167743':'wbb',
                  '167744':'wcc',
                  '167745':'wlight',
                  '167746':'wbb',
                  '167747':'wcc',
                  '167748':'wlight',
                  '167749':'zbb',
                  '167750':'zcc',
                  '167751':'zlight',
                  '167752':'zbb',
                  '167753':'zcc',
                  '167754':'zlight',
                  '167755':'zbb',
                  '167756':'zcc',
                  '167757':'zlight'}

    if "physics" in filename:
        if 'loose' in filename:
            process = 'qcd'
            return process
        else: 
            process = 'data'
            return process
    
    elif "protos.SM.RWT" in filename:
        return 'tchannel'
    
    else:
        try:
            identifier = filename.split('/')[-1].split('.')[1]
            process = mclist[identifier]
            return process
        except: sys.exit('\nsample %s not included in mclist\n'%(filename))


def identifyFiles(optiondict):

    print "===> In identify files"
    process    = ""
    channel = [optiondict.channel]
    if optiondict.channel == 'both': channel = ['el', 'mu']
    folder  = optiondict.inputdir
    retval  = {'el': {}, 'mu': {}}
    #print folder
    files   = [ os.path.join(folder,f) for f in sorted(os.listdir(folder)) if os.path.isfile(os.path.join(folder,f)) ]
    sizename = 0
    temp_process = []
    
    systype = optiondict.systematic
    
    if optiondict.listfiles:
        with open(optiondict.listfiles) as myfile:
            for l in myfile :
                l = l.strip()
                if l.startswith('systematic'):
                    systype = l.split("=")[-1].strip()
                    break

    print systype
    
    retval['el'] = {systype: []}
    retval['mu'] = {systype: []}
    
    if optiondict.listfiles:
        
        with open(optiondict.listfiles) as myfile:
            for f in myfile :
                f = f.strip()
                if f.startswith("#"): continue
                if f.endswith('el.root'):
                    process = humble_DB(f)
                    if process not in temp_process: temp_process.append(process)
                    if sizename < len(f): sizename = len(f)+1
                    if systype != 'nominal' and not f.startswith('data'):
                        f = f.replace('.root', '.'+systype+'.root')
                    retval['el'][systype].append((process, os.path.join(folder, f)))

                if f.endswith('mu.root'):
                    process = humble_DB(f)
                    if process not in temp_process: temp_process.append(process)
                    if sizename < len(f): sizename = len(f)+1
                    if systype != 'nominal' and not f.startswith('data'):
                        f = f.replace('.root', '.'+systype+'.root')
                    retval['mu'][systype].append((process, os.path.join(folder, f)))

        for c in retval:
            
            print "\n==> Channel: ",c
            for s in retval[c] :
                print "\n==> type: ",s
                if len(retval[c][s]) == 0: continue
                
                print repr('process:').rjust(10), repr('file name:').ljust(sizename)
                for p, f in sorted(retval[c][s]):
                    print repr(p).rjust(10), repr(f.split('/')[-1]).ljust(sizename)
        
        return retval
    
    
    for c in channel:
        for file in files:
            ending = '.root'
            tempch = '.%s.'%(c)
            nominal = '.%s.root'%(c)
           
            if optiondict.sample:
                if not optiondict.sample in file:
                    if optiondict.includedata and ('data' in file)   : pass
                    elif optiondict.includeqcd and ('loose' in file) : pass
                    else: continue 

            if not file.endswith(ending) : continue
            if not tempch in file : continue

            if nominal in file:
                systype = 'nominal'
                if 'nominal' in retval[c].keys(): pass
                else: retval[c]['nominal'] = []

            else:
                systype = file.split('.')[-2]
                if systype in retval[c].keys(): pass
                else: retval[c][systype] = []
            
            #if 'data' in file and not 'periodL' in file: continue
            #if '110404' in file: continue
            #if '167740' in file: continue
            #if 'data' in file and 'loose' not in file: continue
            #if 'mc12' in file: continue
            #if 'data' not in file: continue

            process = humble_DB(file)

            if process not in temp_process: temp_process.append(process)
            if sizename < len(file.split("/")[-1]): sizename = len(file.split("/")[-1])+1
            #if not options.sample in file: continue
            retval[c][systype].append((process, file))
        
        if len(retval[c][systype]) == 0: sys.exit('No files retrieved in %s'%(folder))
        
    if optiondict.analysis in ['migration', 'closure', 'efficiency'] : config_process_list = ['tchannel']
    
    for c in retval:

        if optiondict.systematic == 'all': pass
        else:
            keys = retval[c].keys()
            for k in keys:
                if k == optiondict.systematic: pass
                else: del retval[c][k]
        
        print "\n==> Channel: ",c
        for s in retval[c] :
            print "\n==> type: ",s
            if len(retval[c][s]) == 0: continue
        
            print repr('process:').rjust(10), repr('file name:').ljust(sizename)
            for p, f in sorted(retval[c][s]):
                print repr(p).rjust(10), repr(f.split('/')[-1]).ljust(sizename)
    
    
    return retval        


