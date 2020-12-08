# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS    
import functions

#############################################################
# VARIABLES #################################################
#############################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
langKeys = yaml.load(open(settings["language_keys"]))

#############################################################
# TRICKY FUNCTIONS ##########################################
#############################################################

# Function OCR a PDF, saving each page as an image and 
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language):
    # generate and create necessary paths 
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # first we need to check whether this publication has already been processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)

        # start processing images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}
        images = pdf2image.convert_from_path(pdfFile)
        pageTotal = len(images)
        pageCount = 1
        for image in images:
            text = pytesseract.image_to_string(image, lang=language)
            textResults["%04d" % pageCount] = text

            image = image.convert('1') # binarises image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            image.save(finalPath, optimize=True, quality=10)

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1

        with open(jsonFile, 'w', encoding='utf8') as f8:
            json.dump(textResults, f8, sort_keys=True, indent=4, ensure_ascii=False)
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)

def identifyLanguage(bibRecDict, fallBackLanguage):
    if "langid" in bibRecDict:
        try:
            language = langKeys[bibRecDict["langid"]]
            message = "\t>> language has been successfully identified: %s" % language
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage
            language = fallBackLanguage
    else:
        message = "\t>> No data on the language of the publication"
        message += "\t>> For now, trying `%s`..." % fallBackLanguage
        language = fallBackLanguage
    print(message)
    return(language)

#############################################################
# PROCESS ALL RECORDS: APPROACH 1 ###########################
#############################################################

def processAllRecords(bibData):
    for k,v in bibData.items():
        # 1. create folders, copy files 
        functions.processBibRecord(memexPath, v)

        # 2. OCR the file
        language = identifyLanguage(v, "eng")
        ocrPublication(memexPath, v["rCite"], language)

bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)


#############################################################
# PROCESS ALL RECORDS: APPROACH 2 ###########################
#############################################################





# # Why this way? Our computers are now quite powerful; they
# # often have multuple cores and we can take advantage of this;
# # if we process our data in the manner coded below --- we shuffle
# # our publications and process them in random order --- we can 
# # run multiple instances to the same script and data will 
# # be produced in parallel. You can run as many instances as 
# # your machine allows (you need to check how many cores 
# # your machine has). Even running two scripts will cut 
# # processing time roughly in half.

# def processAllRecords(bibData):
#     keys = list(bibData.keys())
#     random.shuffle(keys)

#     for key in keys:
#         bibRecord = bibData[key]

#         # 1. Create folders, copy files
#         functions.processBibRecord(memexPath, bibRecord)

#         # 2. OCR the file
#         language = identifyLanguage(bibRecord, "eng")
#         ocrPublication(memexPath, bibRecord["rCite"], language)


# bibData = functions.loadBib(settings["bib_all"])
# processAllRecords(bibData)