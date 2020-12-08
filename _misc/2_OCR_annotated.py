# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS 
# Past functions can be reused by placing them in a separate file
# NB: Avoid naming functions after a default Python library!   
import functions

#############################################################
# VARIABLES #################################################
#############################################################

# The variables are defined
settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"] # The path to Memex is defined in the yaml settings file
langKeys = yaml.load(open(settings["language_keys"]))

#############################################################
# TRICKY FUNCTIONS ##########################################
#############################################################

# Function OCR a PDF, saving each page as an image and 
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language): # The path to Memex is given in this function,
                    # together with the citation key and the language. Language is necessary to inform
                    # Tesseract which one to use for the OCR.
                    # NB: English can be used for any latin script languages, albeit accents will be lost.
    # generate and create necessary paths 
    publPath = functions.generatePublPath(pathToMemex, citationKey) # Generates paths, which is loaded like
                        # any other external library.
    pdfFile = os.path.join(publPath, citationKey + ".pdf") # Creates a path to the PDF file.
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here in the JSON file.
    saveToPath = os.path.join(publPath, "pages") # Creates a subfolder where all the images extracted from the 
                            # PDFs will be saved.

    # First we need to check whether this publication has already been processed
    if not os.path.isfile(jsonFile): # Before running the process, this checks to see if the JSON file already exists 
                        # (which means that an OCR has already been created). If it doesn't, it starts processing.
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath): # Checks to see if a subfolder for saving the images exists
            os.makedirs(saveToPath) # If not, it creates a subfolder for the images.

        # start processing images and extract text
        print("\t>>> OCR-ing: %s" % citationKey) # Indicates that the process has started and is working

        textResults = {} # Creates an empty dictionary into which the results are saved
        images = pdf2image.convert_from_path(pdfFile) # Creates a reader, grabs the PDF and splits it into images  
        pageTotal = len(images) # Checks the total number of pages in the PDF and how many need to be processed.
        pageCount = 1 # Page count keeps track of what's going on.
        for image in images: # This loops through the images, one image at a time.
            text = pytesseract.image_to_string(image, lang=language) # Runs the OCR on that page
            textResults["%04d" % pageCount] = text # Adds the results from that page to the dictionary.

            image = image.convert('1') # Binarises image, reducing its size, but also its quality. 
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount) # Creates a path to where the Memex is saved.
            image.save(finalPath, optimize=True, quality=10) # The image is saved into that folder.

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal)) # Keeps track of the ongoing process.
            pageCount += 1 # Increases the page count to name it correctly.

        # Outside the loop there is the OCR data 
        with open(jsonFile, 'w', encoding='utf8') as f8: # OCR data is saved into a JSON file
            json.dump(textResults, f8, sort_keys=True, indent=4, ensure_ascii=False) # Dumps and loads the data into JSON.
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)

# NB: Tesseract accepts language codes in a three letter standard, which need to be specified.
def identifyLanguage(bibRecDict, fallBackLanguage): # The language function
    if "langid" in bibRecDict: # Checks the language ID in the bibliographical record.
        # NB: It's possible to use 'if else' instead of 'try except', but the former will stop executing if the condition is not met, 
        # whereas 'try except' will continue running it.
        try:
            language = langKeys[bibRecDict["langid"]] # Checks the bibliographical record against the dictionary of language codes. 
                                # Supplies 2 arguments: the dictionary of bibliographical records and the fallback language.
            message = "\t>> language has been successfully identified: %s" % language # If successful, a message is printed showing the
                        # value of the identified language. 
        except: # If the value of language ID cannot be pulled out of the language dictionary, then the except condition is triggered.
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage # Tries a pre-defined fallback language
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

# Function goes through everything step by step and processes it.
def processAllRecords(bibData): # Takes the bibData as an argument and loops through the dictionary
    for k,v in bibData.items():
        # 1. create folders, copy files 
        functions.processBibRecord(memexPath, v)

        # 2. OCR the file
        language = identifyLanguage(v, "eng") # Identifies the language as eng
        ocrPublication(memexPath, v["rCite"], language) # OCRs the publication

bibData = functions.loadBib(settings["bib_all"]) # Loads bibliographical data using the bib function
processAllRecords(bibData) # Processes all records
# Final result: file structure and pages saved as png files in the 'pages' subfolders



#############################################################
# PROCESS ALL RECORDS: APPROACH 2 ###########################
#############################################################


# Why this way? Our computers are now quite powerful; they
# often have multuple cores and we can take advantage of this;
# if we process our data in the manner coded below --- we shuffle
# our publications and process them in random order --- we can 
# run multiple instances to the same script and data will 
# be produced in parallel. You can run as many instances as 
# your machine allows (you need to check how many cores 
# your machine has). Even running two scripts will cut 
# processing time roughly in half.

def processAllRecords(bibData):
    keys = list(bibData.keys()) # Grabs the keys from the dictionary into the list
    random.shuffle(keys) # Shuffles the order of the keys in the list

    for key in keys: # Processes records based on this list (since the list will be different 
                    # every time, whenever the script is run it'll start processing another script).
        bibRecord = bibData[key]

        # 1. Create folders, copy files
        functions.processBibRecord(memexPath, bibRecord)

        # 2. OCR the file
        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(memexPath, bibRecord["rCite"], language)


bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)