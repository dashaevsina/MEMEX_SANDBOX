import os, json

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

#############################################################
# VARIABLES #################################################
#############################################################

settings = functions.loadYmlSettings("settings.yml") # Function loads yaml settings

#############################################################
# FUNCTIONS #################################################
#############################################################

# Generates an interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile): # Function generates the HTML pages.
                                # Uses citeKey and pathToBibFile as 2 arguments
    print("="*80)
    print(citeKey)

    jsonFile = pathToBibFile.replace(".bib", ".json") # Loads JSON file, gets path by replacing .bib extension 
                                            # with .json extension
    with open(jsonFile) as jsonData:
        ocred = json.load(jsonData)
        pNums = ocred.keys() # Generates page links 

        pageDic = functions.generatePageLinks(pNums) # Page dictionary creates a table of contents with a unique
                                                    # name for each of the publications, creating links (making
                                                    # it navigable). It's the panel on the left.

        # Loads page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # Loads individual bib record (can use the functions that have already been written)
        bibFile = pathToBibFile 
        bibDic = functions.loadBib(bibFile) #LoadBib loads the entire bibliography or a single record
        bibforHTML = functions.prettifyBib(bibDic[citeKey]["complete"]) # Makes the bib file look better for 
                                                                        # this view, removing curly brackets and 
                                                                        # unnecessary fields (it's a simple find
                                                                        # and replace).

        orderedPages = list(pageDic.keys()) # Creates a list of all the keys to generate page numbers, taken from 
                                            # the page dictionary generated from the function above.

# This is just a long loop that creates every single page. 
        for o in range(0, len(orderedPages)):
            #print(o)
            k = orderedPages[o]
            v = pageDic[orderedPages[o]]

            pageTemp = template # Takes a template
            pageTemp = pageTemp.replace("@PAGELINKS@", v) # Replaces all of the items in the template with 
                                                        # different values, creating an individual page for 
                                                        # every page in the publication.
            pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            pageTemp = pageTemp.replace("@CITATIONKEY@", citekey)

# This concerns the DETAILS page
            if k != "DETAILS": # All of the pages are numbered, except for the initial page
                mainElement = '<ing src="@PAGEFILE@" width="100%" alt=">'.replace("@PAGEFILE@", "%s.png" % k)
                            # These are the regular pages
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) # Replaces it with the main element
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>")) # Removes the OCR
            else: # When the page is 'DETAILS'
                mainElement = bibForHTML.replace("\n", "<br> ") # DETAILS page has a HTML
                mainElement = '<div class="bib">%s</div>' % mainElement # Inserts element into a specific class
                # NB: class and div tags in HTML correspond to the stylesheet specifications
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">' # Word cloud element
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) # Replaces main element with the element
                                                            # that was formed before
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "") # Removes the OCR content

# Creates links to the 'previous' and 'next' pages.
            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            if k == "DETAILS": # When on the first page 'DETAILS', you won't have the one before it
                nextPage = "0001.html"
                prevPage = "" # Creates an empty element for the previous page that doesn't exist
            elif k == "0001": # When on page 1,...
                nextPage = "0002.html"
                prevPage = "DETAILS.html" # ... the page before it will be DETAILS.
            elif o == len(orderedPages)-1: # When on the last page,...
                nextPage = "" # ... there won't be a next page
                prevPage = orderedPages[o-1] + ".html"
            else: # Regular pages
                nextPage = orderedPages[o+1] + ".html" # Adds 1 for the next page
                prevPage = orderedPages[o-1] + ".html" # Subtracts 1 for previous page

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) # Find and replace, which replaces 
                                        # the next value with a given value
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage) # Replaces previous value with
                                                            # a given value.

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k) 
            # Saves the actual page.
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp)    

# Generates the INDEX and the CONTENTS pages
def generateMemexStartingPages(pathToMemex):
    # Loads index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template =ft.read()

    # Adds index.html
    with open(settings["content_index"], "r", encoding="utf8") as fi:
        indexData = fi.read()
        with open(os.path.join(pathToMemex, "index.html"), "w", encoding="utf8") as f9:
            f9.write(template.replace("@MAINCONTENT@", indexData))

    # Loads bibliographical data for processing by looping through all of the bibliographical records, 
    # collecting information from each one and placing it into another template.
    publicationDic = {} # key = citationKey; value = recordDic

    for subdir, dirs, files in os.walk(pathToMemex): # Loops through all the bib files 
        for fiel in files:
            if file.endswith(".bib"):
                pathWhereBibIs = os.path.join(subdir, file)
                tempDic = functions.loadBib(pathWhereBibIs)
                publicationDic.update(tempDic) # Adds each record to the empty publication dictionary

    # Generates data for the main CONTENTS
    singleItemTemplate = '<li><a href="@RELATIVEPATH/pages/DETAILS.html">[@CITATIONKEY@]</a> @AUTHOROREDITOR@ (@DATE@) - <i>@TITLE@</i>'
    # Formatting is not crucial, but there must be a link to the first page of the publication, which is placed around the citation key, 
    # but it can be placed anywhere. The tag around the title makes it italic. 
    contentsList = [] # Builds a contents list with specific values for each and every publication.

    for citeKey.bibRecord in publicationDic.items(): # Loops through the publication dictionary
        relativePath = functions.generatePublPath(pathToMemex, citeKey).replace(pathToMemex, "") # Gets the relative path, which takes the
                    # pathToMemex and the citation key as values and generates the path, then it makes the link relative.

        authorOrEditor = "[No data]" # Pulls out the editor or the author from the create, creates this value that, by default, has no data.
        if "editor" in bibRecord: # Checks if it has the field 'editor'
            authorOrEditor = bibRecord("editor") # Updates the field
        if "author" in bibRecord: # Checks if it has the field 'author'
            authorOrEditor = bibRecord("author") # Updates it

        date = bibRecord["date"][:4] # Gets the date and indexes it to get the first 4 digits (data in the year-month-format will only take 
                                # the first four numbers).

        title = bibRecord["title"] # Gets the title of the bib record

        # Forming a record
        recordToAdd = singleItemTemplate # The temporary record in the beginning is just a template
        recordToAdd = recordToAdd.replace("@RELATIVEPATH@", relativePath) # Generates the appropriate relative path
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", citeKey) # Updates the citation key
        recordToAdd = recordToAdd.replace("@AUTHOROREDITOR@", authorOrEditor) # Updates the author and/or editor
        recordToAdd = recordToAdd.replace("@DATE@", date) # Updates the date
        recordToAdd = recordToAdd.replace("@TITLE@", title) # Updates the title

        recordToAdd = recordToAdd.replace(", ").replace("}", "") # Removes the curly brackets

        contentsList.append(recordToAdd) # Appends the record to the contents list.

    contents = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(contentsList)) # Contents file. Since it's an unordered list it 
                # cannot be joined, so there's an opening and closing tag of a list <ul> in HTML. Inserts all of the 
                # data collected between the opening and closing tag.
    mainContent = "<h1>CONTENTS of MEMEX</h1>\n\n" + contents # Makes the main content into a header (not obligatory).

    # Saves the CONTENTS page
    with open(os.path.join(pathToMemex, "contents.html"), "w", encoding="utf8") as f9: # Opens the template and replaces
                            # the main content with the content that has just been created.
        f9.write(template.replace("@MAINCONTENT@", mainContent))

#############################################################
# PROCESS ALL RECORDS #######################################
#############################################################

def processAllRecords(pathToMemex): # Last function processes all of the records, uses pathToMemex as an argument
    files = functions.dicOfRelevantFiles(pathToMemex, ".bib") # Gets all of the bib files and loops through the dictionary
    for citekey, pathToBibFile in files.items(): # The citation key and the pathToBibFile are given
        #print(citeKey)
        generatePublicationInterface(citeKey, pathToBibFile)
    generateMemexStartingPages(pathToMemex) # Generates the starting pages.

processAllRecords(settings["path_to_memex"]) # Runs the code
