import mechanize
import cookielib
import re
import sys
# Browser
browserObject = mechanize.Browser()
# Cookie Jar
cj = cookielib.LWPCookieJar()
browserObject.set_cookiejar(cj)
# Browser options
browserObject.set_handle_equiv(True)
browserObject.set_handle_gzip(True)
browserObject.set_handle_redirect(True)
browserObject.set_handle_referer(True)
browserObject.set_handle_robots(False)
# Follows refresh 0 but not hangs on refresh > 0
browserObject.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
# Want debugging messages?
#browserObject.set_debug_http(True)
#browserObject.set_debug_redirects(True)
#browserObject.set_debug_responses(True)
# User-Agent (this is cheating, ok?)
browserObject.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
if len(sys.argv) < 2:
    print("Fool, you need to include the out put file!")
    print("This script will delete anything already in that out put file")
    quit()
outFileNameBase = sys.argv[1]
outFileNameBase = outFileNameBase.replace('.txt','')


#finds and writes the title and abstract to the outFile
def scraper(url):
    outFile = open(outFileName, 'a')
    r = browserObject.open(url)
    string = r.read()
    titlePattern =  re.compile('<TITLE>.*</TITLE>')
    title = re.search(titlePattern,string)
    if title:
        title = title.group(0)
        title = title.replace('<TITLE>','')
        title = title.replace('</TITLE>','')
    else:
        outFile.close()
        return
    moneyPattern = "\$[\d,\.]+"
    money = re.search(moneyPattern,string)
    if money:
        money = money.group(0)
        title = title + "\t" + money
    else:
        outFile.close()
        return
    #being able to pick out the largest match from the following patter, in the the example it matches with two sections, the largest is the abstract
    abPattern = "\s*\w[^\n]{320,}"
    orgPattern = '<td align="right" valign="top" class="tabletext2" nowrap><strong>NSF Program\(s\):</strong></td>\r\s*<td class="tabletext2" valign="top">\r\s*\w.*'
    org = re.search(orgPattern,string)
    if org:
        org = org.group(0)
        org = org.replace('<td align="right" valign="top" class="tabletext2" nowrap><strong>NSF Program(s):</strong></td>',"")
        org = org.replace('<td class="tabletext2" valign="top">',"")
        org = org.replace("\r","")
        org = org.replace("\n","")
        org = org.replace('  ',"")
    else:
        outFile.close()
        return
    abstract = re.search(abPattern,string)
    if abstract:
        abstract = abstract.group(0)
        abstract = abstract.replace("<BR/><BR/>","\n")
        abstract = abstract.replace("<br/><br/>","\n")
    else:
        outFile.close()
        return
    #writes title and abstract to file, includes 3 new lines a the end of the file
    writeMe = title + "\n" + url + "\n" + org + "\n" + abstract + "\n\n\n"
    if writeMe == '':
        outFile.close()
        return
    outFile.write(writeMe)
    outFile.close()
#-----end scraper function


def getUrl(regexedUrl):
    basicUrl = "https://dellweb.bfa.nsf.gov/AwdLst2/"
    regexedUrl = regexedUrl.replace('<a HREF="','')
    regexedUrl = regexedUrl.replace('" Target="OptTable">','')
    newURL = basicUrl + regexedUrl
    return newURL
    #return a url with the new ending

def getFinalUrl(regexedUrl):
    basicUrl = "https://dellweb.bfa.nsf.gov/AwdLst2/"
    regexedUrl = regexedUrl.replace('<a href=','')
    regexedUrl = regexedUrl.replace(' target=_top >','')
    print(regexedUrl)
    return regexedUrl

def navagateTheState(stateUrl):
    print(stateUrl)
    r = browserObject.open(stateUrl)
    r = browserObject.open("https://dellweb.bfa.nsf.gov/AwdLst2/State.asp")
    readed = r.read()
    href = re.compile('<a HREF=".*" Target="OptTable">')
    #instate contains the urls for all of the Aware ID URLS, ingornre the first
    inStateMatches = re.findall(href,readed)
    for i in range(1,len(inStateMatches)):
        navagateID(getUrl(inStateMatches[i]))

def navagateID(idURL):
    r = browserObject.open(idURL)
    r = browserObject.open("https://dellweb.bfa.nsf.gov/AwdLst2/Awd.asp")
    readed = r.read()
    href1 = re.compile('<a HREF=".*" Target="OptTable">')
    #instate contains the urls for all of the Aware ID URLS, ingornre the first
    orginizationMatches = re.findall(href,readed)
    for i in range(1,len(orginizationMatches)):
        navagateOrganization(getUrl(orginizationMatches[i]))

def navagateOrganization(orgURL):
    r = browserObject.open(orgURL)
    r = browserObject.open('https://dellweb.bfa.nsf.gov/AwdLst2/Abst.asp')
    readed = r.read()
    href = re.compile('<a href=.* target=_top >')
    #instate contains the urls for all of the Aware ID URLS, ingornre the first
    organizationAwardMatches = re.findall(href,readed)
    for i in range(0,len(organizationAwardMatches)):

        #if getFinalUrl(organizationAwardMatches[i]) == '':
        #    print('stopped')
        #    continue
        scraper(getFinalUrl(organizationAwardMatches[i]))


#start the scraping
r = browserObject.open("https://dellweb.bfa.nsf.gov/AwdLst2/default.asp")
r = browserObject.open("https://dellweb.bfa.nsf.gov/AwdLst2/Bottom.asp")
r = browserObject.open("https://dellweb.bfa.nsf.gov/AwdLst2/Install.asp")
href = re.compile('<a HREF=".*" Target="OptTable">')
readed = r.read()
#matches contains all the state urls, the first one needs to be ingored, it returns you to the original page
matches = href.findall(readed)
#starting at 1 to skip the first url which is a back tract

for i in range(1,len(matches)):
    tempState = matches[i].replace
    tempState = matches[i].replace('<a HREF="','')
    tempState = matches[i].replace('" Target="OptTable">','')
    outFileName = outFileNameBase + tempState[-2:] + ".txt"
    navagateTheState(getUrl(matches[i]))
