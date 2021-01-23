import re, os, yaml, json, random
from datetime import datetime

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString):
    print("SEARCHING FOR: `%s`" % searchString)
    files = functions.dicOfRelevantFiles(pathToMemex, ".json")
    results = {}

    for citationKey, pathToJSON in files.items():
        data = json.load(open(pathToJSON))
        print(citationKey)
        count = 0

        for pageNumber, pageText in data.items():
            if re.search(r"\b%s\b" % searchString, pageText):
                if citationKey not in results:
                    results[citationKey] = {}

                # relative path
                a = citationKey.lower()
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber)
                countM = len(re.findall(r"\b%s\b" % searchString, pageText))
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText)

                results[citationKey][pageNumber] = {}
                results[citationKey][pageNumber]["pathToPage"] = relPath
                results[citationKey][pageNumber]["matches"] = countM
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>")

                count  += 1

        if count > 0:
            print("\t", citationKey, " : ", count)
            newKey = "%09d::::%s" % (count, citationKey)
            results[newKey] = results.pop(citationKey)

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            results["timestamp"] = currentTime
            # add search string (as submitted)
            results["searchString"] = searchString

    saveWith = re.sub("\W+", "", searchString)
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith)
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False)

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

searchPhrase  = r"((bataille) des\b (E|É|é|e)perons d(’|')or)|(bataille) de\b (C|c)ourtrai"
#searchPhrase  = r"corpus\W*driven"f
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], searchPhrase)
#exec(open("9_Interface_IndexPage.py").read())