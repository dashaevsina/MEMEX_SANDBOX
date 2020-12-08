import os, shutil, re
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml" # Main settings are stored in a yaml file, which is
            # better than defining each variable in the header of the script.
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"] # Defines the memexPath.

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile): # Function loadBib takes a bibliographical file as an argument

    bibDic = {}
    recordsNeedFixing = []

    with open(bibTexFile, "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            # ONLY processes the records that have PDFs
            if ".pdf" in record.lower(): # Checks if the record has a PDF file in it. 
                # NB: This can either be placed here or later when processing all the records. 
                completeRecord = "\n@" + record # Adds what the record was split on, which 
                    # creates a complete record.

                record = record.strip().split("\n")[:-1] # Records are split on new line, so 
                            # the '}' character is the last element in the bibliogrpahy, which is
                            # unnecessary (contains no data). [:-1] drops the last element.

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord # Saves the complete record into the 
                            # dictionary with the key 'complete'. 

                for r in record[1:]: # Processes each line of the recrod.
                    key = r.split("=")[0].strip() # Gets the key (element before the '=' sign).
                    val = r.split("=")[1].strip() # Gets the value (element after the '=' sign).
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # Fixes the path to the PDF file.
                    # NB: The mulitple attachments in Zotero have paths that are crammed together. 
                    # There may be a html file associated with it, which is not a proper path 
                    # (generates an error). This splits the code on the semicolon and keeps the PDF.
                    if key == "file":
                        if ";" in val: # Checks if the 'file' key has a semicolon. 
                            #print(val)
                            temp = val.split(";") # If it does, it splits on the ';'.

                            for t in temp: 
                                if ".pdf" in t: # Checks if the .pdf is in that path.
                                    # Alternative code: if t.endswith(".pdf"): 
                                    val = t # If it has a PDF then that key is assigned to the value  
                                            # and back to the dictionary

                            bibDic[rCite][key] = val # Overrides old messy path with a new usable path.

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# generate path from bibtex code, and create a folder, if it does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode): # This function processes the entire record
                    # The path is directed to the memex folder. 
    temp = bibTexCode.lower() # Changes the bibTex code to lowercase letters.
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode) 
                            # Grabs the first character, then the first two characters, 
                            # then the citation itself. This generates the path.
    return(directory)

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict): # Function processBibRecord processes every
                    # single bibliographical record (the dictionary) as its argument.
                    # It takes its arguments as pathToMemex and the single bibRecDict.
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"]) # Function generates a path to
        # the publication, which, again, takes the citation key (rCite) and the pathToMemex.

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath): # Checks if the path exists, if not,...
        os.makedirs(tempPath) # ...the path is created.

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) # Creates a path 
            # for the bibliographical record from the system settings. 
            # Alternative: a path can also be built in the following manner: folder + "/" +
            # subfolder + "/" + file. But this is incompatible between systems (Windows slashes
            # are different). Hence, the easiest way to create a path is to use the function 
            # os.path.join, which passes the arguments as elements of the path. 
            # The bib file is created from the citation key and adds the extension .bib
        with open(bibFilePath, "w", encoding="utf8") as f9: # Creates a file 
            f9.write(bibRecDict["complete"]) # Writes a complete record by grabbing the 
                # entire bib record.

        pdfFileSRC = bibRecDict["file"] # Saves the path to the PDF in the dictionary, in
                                        # the field with the key 'file'. Grabs the path, which
                                        #  will be the source file (in the Zotero system).
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) # Creates a path 
            # to where it should go. The .bib extension is replaced with a PDF. 
        if not os.path.isfile(pdfFileDST): # Checks to see if the file already exists to avoid 
                                           # copying whatever has already been copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST) # If it doesn't exist, shutil creates the 
                                                    # file.


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData): # Function processes all the records
    for k,v in bibData.items(): # Looks through every item in the dictionary by calling the 'items'
                        # element. 
        processBibRecord(memexPath, v) # Passes the memexPath and records to the bibRecord.

bibData = loadBib(settings["bib_all"]) # Processes every single record, creates a transparent structure
processAllRecords(bibData)

print("Done!")