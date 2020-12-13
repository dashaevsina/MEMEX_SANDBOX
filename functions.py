import os, re, shutil, yaml

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

#############################################################
# FUNCTIONS #################################################
#############################################################

# load bibTex Data into a dictionary 
def loadBib(bibTexFile):

    bibDic = {}
    recordsNeedFixing = []

    with open(bibTexFile, "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            if ".pdf" in record.lower():  
                completeRecord = "\n@" + record

                record = record.strip().split("\n")[:-1] 

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord

                for r in record[1:]:
                    key = r.split("=")[0].strip() 
                    val = r.split("=")[1].strip()
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    if key == "file":
                        if ";" in val:
                            temp = val.split(";")

                            for t in temp: 
                                if ".pdf" in t: 
                                    val = t

                            bibDic[rCite][key] = val

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)                        

# Loading function removes all non-YAML elemnts, splits the cleaned text into units that
# contain key-value pairs, splits these units into keys and values, adds them into a 
# dictionary, which is then 'returned'.
def loadYmlSettings(ymlFile):
    with open(ymlFile, "r", encoding="utf8") as f1:
        data = f1.read()
        data = re.sub(r"#.*", "", data) # remove comments
        data = re.sub(r"\n+", "\n", data) # remove extra linebreaks used for readability
        data = re.split(r"\n(?=\w)", data) # splitting
        dic = {}
        for d in data:
            if ":" in d:
                d = re.sub(r"\s+", " ", d.strip())
                d = re.split(r"^([^:]+) *:", d)[1:]
                key = d[0].strip()
                value = d[1].strip()
                dic[key] = value
    return(dic)

# Generate path from bibtex citation key: for example, if the key is 'SavantMuslims2017',
# the path will be pathToMemex+ '/s/sa/SavantMuslims2017/'
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    return(directory)

# Process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath):
        os.makedirs(tempPath) 

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) 
        with open(bibFilePath, "w", encoding="utf8") as f9:  
            f9.write(bibRecDict["complete"])

        pdfFileSRC = bibRecDict["file"]
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) 
        if not os.path.isfile(pdfFileDST):
            shutil.copyfile(pdfFileSRC, pdfFileDST)

# Process all the records 
def processAllRecords(bibData):
    for k,v in bibData.items():
        processBibRecord(memexPath, v)

bibData = loadBib(settings["bib_all"])
processAllRecords(bibData)

print("Done!")

# TOC Links: function generates links to all pages in a given publication to make 
# navigation and moving around easier. Each page in the publication receives its own
# list of links where the current page is coloured red.
def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)

# HTML-Friendly BIB: function makes a bib record look more readable, more HTML friendly.
# It removes excessive curly brackets and fields that are unnecessary for the display
def prettifyBib(bibText):
    bibText = bibText.replace("{{", "").replace("}}", "")
    bibText = re.sub(r"\n\s+file = [^\n]+", "", bibText)
    bibText = re.sub(r"\n\s+abstract = [^\n]+", "", bibText)
    return(bibText)

# Extra function: function generates a dictionary of citation keys and paths to specify 
# types of files.
def dicOfRelevantFiles(pathToMemex, extension):
    dic = {}
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication of data
            if file.endswith(extension):
                key = file.replace(extension, "")
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)