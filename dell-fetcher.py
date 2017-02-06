#!/usr/bin/python
import os, sys, shutil, re
import xml.etree.ElementTree
import requests
import hashlib
import uuid
import argparse
scriptlocation=os.path.dirname(__file__)
server_modelarr=[]
storagelocation=""
filecontent = []
currentmd5 = open("%s/static/catalog.md5"%scriptlocation,"r")
bashheader = open("%s/static/apply_bundle.sh"%scriptlocation)
data = bashheader.read()
curentmd5 = currentmd5.read()
currentmd5.close()
filecontent.append(data)
downloadurl = "http://downloads.dell.com/"
catalogurl="http://ftp.dell.com/catalog/catalog.cab"
uuidofday=uuid.uuid1()
dailyfile="%s/static/%s.cab"%(scriptlocation, uuidofday)
config = '%s/static/config.xml'%scriptlocation
footer="""mytime=`date`
echo End time: $mytime | tee -a $logFile
echo Please see log, located at $logFile for details of the script execution
echo script exited with status $RETURN_STATUS
echo $rebootMessage
exit $RETURN_STATUS"""
nocmd = True
if os.path.exists(config):
    nocmd=False
    config = xml.etree.ElementTree.parse(config)
    root = config.getroot()
    #print confroot.iter()['models']
    for elemnt in root:
        if elemnt.tag == "storagelocation":
            storagelocation = elemnt.text
        if elemnt.tag == "models":
            for model in elemnt:
                server_modelarr.append(model.text)

parser = argparse.ArgumentParser()
if nocmd:
 parser.add_argument('--model', help='Server model code e.g. R330 or R320/NX400', required=True, nargs='*')
 parser.add_argument('--storagelocation', help='Where keep downloaded files (Default: /tmp)',
                    required=False, default='/tmp')
parser.add_argument('--repull', help='Force re-download', required=False,
                    default='True')
args = parser.parse_args()
cmdargs = vars(args)
if nocmd:
 server_modelarr = cmdargs['model']
 storagelocation = cmdargs['storagelocation']
repull = cmdargs['repull']

print server_modelarr



def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def pullfirmware(fwurl, fwversion,bundleversion):
    print ("Will try to fetch %s" % fwversion)
    profileurl = ('%s%s' % (fwurl, fwversion))
    r = requests.get(url=profileurl, verify=False,
                     stream=True)

    path = '/%s/%s/' % (storagelocation,bundleversion)
    fwversion = re.findall('.*/(.*.BIN)$', fwversion)
    fwversion = fwversion[0]
    if not os.path.exists(path):
        os.makedirs(path)
    if r.status_code == 200:
        with open('%s/%s' % (path, fwversion), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


r = requests.get(url=catalogurl, verify=False,
                     stream=True)
if r.status_code == 200:
        with open(dailyfile, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

downloadedmd5 = md5(dailyfile)
print curentmd5
print downloadedmd5
if curentmd5 == downloadedmd5:
    print "Bingo no change required see you tomorrow"
    os.unlink(dailyfile)
    if repull is False:
        sys.exit()
else:
    currentmd5 = open("%s/static/catalog.md5"%scriptlocation, "w")
    currentmd5.write(downloadedmd5)
    currentmd5.close()
    os.system("cabextract -d %s/static/ %s"%(scriptlocation,dailyfile))
    os.unlink(dailyfile)




tree = xml.etree.ElementTree.parse('%s/static/Catalog.xml'%scriptlocation)
root = tree.getroot()
repository_path = ''
software = {}


for child in root.iter('SoftwareComponent'):
    path = child.attrib['path']
    basename = os.path.basename(path)

    if child.find('ComponentType').attrib['value'] not in ['FRMW', 'APAC']:
        continue

    software[basename] = [path]
    for subchild in child:
        if subchild.tag == 'Name':
            software[basename].append((subchild.find('Display').text))
        elif subchild.tag == 'Description':
            software[basename].append((subchild.find('Display').text))
        elif subchild.tag == 'Category':
            software[basename].append((subchild.find('Display').text))
        elif subchild.tag == 'ImportantInfo':
            software[basename].append((subchild.attrib['URL']))
        elif subchild.tag == 'Criticality':
            software[basename].append((subchild.attrib['value']))
    if 'rebootRequired' in child.attrib.keys():
        i = 1
        software[basename].append(child.attrib['rebootRequired'])
    else:
        software[basename].append(False)

# print software
applyorder = ()
fetchfw = []
rebootreqdict = {}
for server_model in server_modelarr:
 for child in root.iter('SoftwareBundle'):
    target = child.find('TargetSystems/Brand/Model/Display')
    if (target.text != server_model):
        continue
    osed = child.find('TargetOSes/OperatingSystem')
    if (osed.attrib['osCode'] != "LIN"):
        continue
    bundlever = child.find('Name/Display')
    bundlever = (bundlever.text).replace('/','-')
    contents = child.find('Contents')
    for element in contents:
        applyorder += (element.attrib['path'],)
    print "## The following packages are available:"
    for package in child.iter('Package'):
        mypath = package.attrib['path']
        if mypath in software.keys():
            i = 1
            # print software[mypath]
            fwver = software[mypath][0]
            fetchfw.append(fwver)
            rebootreqdict[mypath]=software[mypath][6]
            print "File: {}\nName: {}\nDescription: {}\nCategory: {}\nInfoURL: {}\nCriticality: {}\nReboot: {}".\
                format(software[mypath][0],software[mypath][1],software[mypath][2],software[mypath][3],software[mypath][4],software[mypath][5],software[mypath][6])
            print "---"

 for fw in fetchfw:
    i=1
    pullfirmware(downloadurl,fw,bundlever)
 iteration = 1
 totaliterations=str(len(applyorder))

 for task in applyorder:
    if task in rebootreqdict.keys():
        reboot = rebootreqdict[task]
        if reboot == "true":
            reboot = "REBOOT"
        else:
            reboot = ""
    else:
        reboot = ""
    dupel = 'ExecuteDup %s %s "%s" "" "" "%s" \n' % (str(iteration), totaliterations, task,reboot)
    iteration += 1
    filecontent.append(dupel)
 filecontent.append(footer)
 executor ="/%s/%s/apply_bundle.sh"%(storagelocation,bundlever)
 writesh = open(executor,"w")
 writetask = ''.join(filecontent)

 writesh.write(writetask)
 writesh.close()
 os.chmod(executor,755)