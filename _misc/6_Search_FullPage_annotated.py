import re, os, yaml, json, random
from datetime import datetime # Python library for getting a timestap

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString): # Function does a search, arguments are
                    #pathToMemex and the searchString (whatever is being searched).
    print("SEARCHING FOR: `%s`" % searchString) # Prints what's being searched as an update.
    files = functions.dicOfRelevantFiles(pathToMemex, ".json") # Gets a dictionary of all files that
                    # have OCR results (all stored in JSON files).
    results = {} # Creates an empty dictionary to collect the results.

    for citationKey, pathToJSON in files.items(): # Goes through the dictionary.
        data = json.load(open(pathToJSON)) # Opens file after file
        #print(citationKey)
        count = 0

        for pageNumber, pageText in data.items(): # Loop for a specific file within the above loop.
                                # Loads the results and starts going through the loaded dictionary. 
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE): # Flag for regular
                        # expression is to ignore the csae. Not usually recommended for searches, but 
                        # the OCR results are not necessarily accurate, so capital letters may be erroneous.
                if citationKey not in results:
                    results[citationKey] = {}

                # relative path
                a = citationKey.lower()
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber) 
                            # Gets the path to the HTML page that shows that specific page in the dicitonary 
                            # to read the context, to be able to go back and forth and check the context in the
                            # neighbouring pages.
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE)) # Counts how many
                            # of the matches actually occurs on the page with the re.findall command. 
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText, flags=re.IGNORECASE)
                        # Takes the page from the pageText on line 29, wraps the search map into a html tag <span>, 
                        # which is assigned a class called 'searchResult'. The class can then be added into a CSS file 
                        # and anythign wrapped into this tag can be defined there.

                # Collects results
                results[citationKey][pageNumber] = {} # Creates an empty entry, essentially an empty dictionary for each page.
                results[citationKey][pageNumber]["pathToPage"] = relPath # Adds the path to the page into the dictionary.
                results[citationKey][pageNumber]["matches"] = countM # Adds the number of matches into the dictionary. 
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>") # Adds the results, the 
                                                            # formatted page itself, into the dictionary.

                count  += 1 # Does a general count of the number searches that were run. Reformats the generated results.
                            # Alternative: can be done differently by doing the count either within the loop (increasing it 
                            # every time there's a match) at around line 28. Or the length of the dictionary that was created 
                            # can be calculated. 

        # Timestamp and additional information. Helps to organise the search results (can be done differently).
        if count > 0: # If count of the number of searches is more than one,...
            print("\t", citationKey, " : ", count) # Keeps track of what's going on.
            newKey = "%09d::::%s" % (count, citationKey) #... this creates a new key for each publication, which combines the 
                                    # frequency (the number of search results) and the citation key. 
                                    # Simple sorting for the HTML page based on number of searches. 
            results[newKey] = results.pop(citationKey) # The pop command removes an item from the dictionary. It removes an old 
                                # item, and simultaneously creates a new one. 
                    # Alternative: can be done in 2 lines of code: 
                                  # results[newKey] = results[citationKey]
                                  # results.pop(citationKey)

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Formatting language of timestamp python library 
                                                # creates a detailed timestamp as a string. 
            results["timestamp"] = currentTime # Adds an extra item to the dictionary, the timestamp of the current time.
            # add search string (as submitted)
            results["searchString"] = searchString # searchString creates a key called 'searchString' and then the value of
                                    # the actual search string that was submitted. 

    # Saves the results
    saveWith = re.sub("\W+", "", searchString) # Takes the search string and remeoves all of the non-word characters. 
                # Line 100 may have characters in the search string that cannot be used in the filename, so this removes
                # anything not alphanumeric (*;#). 
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith) # Creates a path where the search results are
                # in a specific subfolder, an extension called .searchResults is assigned (a unique extension will not be associated)
                # with the existing files, keeping all files separate.
    with open(saveTo, 'w', encoding='utf8') as f9c: # Saves the files...
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False) #... in a JSOn dump that automatically stores the results
                                        # and alphabetises them. Items with the highest results go at the bottom, and matches aree relative
                                        # to the page. Actual results (text of the page) is there as highlighted search results.
                    # NB: Whenever saving files make sure not to overwrite them in another search that searches for something
                    # different.

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

searchPhrase  = r"corpus\W*based" # Defines the search prhase, running the function on line 106. 
#searchPhrase  = r"corpus\W*driven" # Generates the interface of the index page with thee search results.
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], searchPhrase) # Searches the phrase. 
#exec(open("9_Interface_IndexPage.py").read())