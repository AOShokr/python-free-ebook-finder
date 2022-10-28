# Free ebook Finder

#### Description:

For the final project in CS50's introduction python course I wanted to do something with APIs, as I found the concept fascinating.

I did a little digging and I discovered that there is a whole slew of open source/free to use APIs that I could use in a program. At first I was going to go with [Open Trivia](https://opentdb.com/api_config.php), an API that provides questions for Trivia games, as the name suggests, but ultimately decided it was too simplistic (though quite fun!). Other candidates were:
- [ITIS](https://www.itis.gov/ws_description.html) - a repository of taxonomic
- [Launch Library 2](https://thespacedevs.com/llapi) - a database for space flights and launches
- [Nasa](https://api.nasa.gov) - which is Nasa's own open API which anyone can access for data. I still intend to build something with that one.

Ultimately I decided to go with the [Gutendex](https://gutendex.com/), which is the open API for the library at the Gutenberg project. The Gutenberg project. [The Gutenberg project](https://www.gutenberg.org/) is a source for one of the largest collections of free ebooks online, focusing on books that had their copyright expired and moved into the public domain. I have used the Gutenberg project in the past so when I found that they offer a free/open API, I knew I was going to use it.

The program is designed to take a user's input, search the Gutenberg library for it, process and display the results, and export them to a .csv file. It's structured as a main function plus 3 others, requester, unpacker, and extractor.

## main()
The **main()** function starts by setting up 2 variables before entering a "While True" infinite loop. The user is then prompted to enter one of four possible inputs: **'Info'** which will display some info about the program, **'Name'** if the user wants to search by a book or an author name, **'Topic'** to search for a specific topic, and finally **'Exit'** to, well, exit the program. If a user inputs something outside these 4 keywords they get an 'input invalid' notification, after 3 invalid inputs the program exits via sys.exit().

In case of a search keyword (name/topic), the user is then prompted to enter the search criteria, and the requester() function is called, being passed both the keyword and the search criteria. In case the search returned 0 results the program skips all the following steps and then goes back to asking for another input for a fresh search. In case of actual results, requester() returns a json file, which is then passed to unpacker(), which in turn returns a list of dictionaries containing the actual results. The results are displayed using the tabulate module with the parameters: fmt = grid and maxgrid = None,50,50,50,None. Maxgird serves to control the width of the resulting table, since during initial versions that did not include maxgrid, the width of the 3 columns: Name (referring to book name), Author(s), and Genre(s) often ended up too wide and caused display problems. If the list returned had more than 100 results the program goes into what I call Pagination.

Pagination one of the challenges I have faced in the program. Initially I wanted to separate it into a function of its own, but that introduced a problem. There would have been 2 options, as far as I could work out; either let the would be function handle the "tabulation" and display of results, or have it divide the results then pass back the "page" of results to main() to handle the tabulation. Option one would have had a secondary function having a side which I try to avoid, and option two would have introduced futher complexities as I would have had the main() function and the would be paginator function passing back and forth page number and list of dicts, not to mention each time a page is "turned" the paginator function would be called anew, assigning variables as if for the first time. Ultimately it was probably simpler and quiker to let main() handle the pagination. The perfect solution was to create a class for the results, and each time a search is made a class object is created, and it would handle the pagination using a class method. That too felt like added complexity although I do plan on implementing that in the future, because it would solve for a feature I would like to have; saving results for later. As it stands if you run a second search the first search results are gone. I think I can use OOP/classes to save results for a bit longer.

How pagination ended up working in the final program: The first page of the results are displayed, with the final count of results at the bottom as well as a "Page # out of #" notice, and the user is prompted to enter either "Next","Prev", or "Back" to proceed. "Next" takes the user to the next page, if they're already viewing the last page they get notice informing them of that. "Prev" takes them to the previous page, similarly notifying them if there are no previous pages. "Back" ends the displaying of results, moving to the extractor phase.

After the user views the results (either a single page or multi page), they are then prompted on whether or not they want to export the results to a .csv file. If the chooses yes they are given an option to choose a name for the file, alternatively if the name isn't entered the program defaults to "Results.csv", which concludes the full cycle of a single search. Considering that we're still in a "While True" loop, the user is then to prompted for another search or to exit.

## requester()
requester() is the function that performs the requests to the API. It simply takes 2 inputs: type - which is the request type, and kw; the keyword the user wishes to search for.

The function then goes into an if/elif conditional with 3 possible outcomes. If the "type" input is "name", it'll direct the program to use the API link that makes a search by name, if the type is "topic", it uses the link that searches by topic. The third possible value for the parameter "type" is "page" which is responsible for getting to the next page of the results (more on that in the section on the unpacker method()). The first 2 options are only sent by the main() function, the last one only comes from unpacker().

In the first 2 cases that are called by main, the parameter kw is then plugged into the appropriate point in the URL and, using requests.get(), the request is sent to the Gutendex API. In the case type = "page", kw is actually the entire URL.

After the requests is performed, the returned value of requests.get() is stored in a variable called res. A quick check is done on res do determine if the results are empty (no results for the search), in which case requester() returns a value indicating no results to main() which is dealt with as described above. Otherwise, a json file is passed back to main() that then pushes it to unpacker().


## unpacker()
The main purpose of this function is to index into the json file, extract the desired values, put into a list of dicts, and pass it back to main() for display.

First a check is performed, in the case that the search yielded more than 32 results, we go into pagination. In the API docs it is described that each page of results can only carry 32 results. The results will contain the URL for the next page. The check is to simply see if the URL exists, if it is, requester() is called with the values "page" and the URL, returning the next page which then has the same check performed on it to see if there is a "next page" url or not. Each subsequent page of json is added to the first one compiling the full results in one json object.

After the collection of the full results in json format, a simple for loop is used to index into the json file. The json returned from Gutendex has 11 fields, my program is only interested in 5 of them, those are extracted, assigned into a single dict for each one of the results, and that dict is appended into a list. Repeat until no more results are left.

A note on pagination here, or rather, de-pagination. The results come in pages of 32 books each, I then collate all the pages into one, only to break them back into groups of 100 (in case they are more than 100) back in main(). It does seem to me like wasted efforts but there are reasons for that choice:
1. **Aesthetic**: The other reasons are valid but this is the main one, I did not like how it looked to have 32 books per page, it did look and feel a bit too awkward of a number.
2. **Efficiency**: For a search that yields 320 books in its results, the API is called 10 times and that's it, everything that comes after, browsing, going back and forth in the pages is done locally. If the program were to request the next page every time the page is turned, it would take longer as the API would be requested every single time, and it will potentially result in overall more requests to the API (if the user kept going back and forth). With the full results saved to the memory that would be avoided.
3. **Faster extraction**: With the full results saved to the memory the program would not need to request the API during extracting/exporting the results. If I had gone with the alternative, the extractor() function would have had to call both requester() and unpacker() which would have likely increased its operation time signficantly.

Finally after unpacking the entire json file, the list of dicts is passed back to main().

## extractor()
As described in main(), after the user is done viewing the results they are given the option to extract the results to a .csv file. That is the job of extractor().

extractor takes 2 values; "the_results" is the same list of dicts passed by unpacker() to main, it essentially holds the results of the search that was performed. And "file_name", which is the name of the .csv file the user chooses, it has a default value so if the user does not enter a name, it's automatically saved as Results.csv.

The open() function is called to open (or rather create) the .csv file, the program passes it 3 parameters; the file name, "w" to indicate it's in write mode, and encoding='utf-8', *more on that last one in a bit*.

csv.DictWriter() is then called and is given the keys of the dicts it's about to be passed, using csv.DictWriter.writeheader() to ensure that the dict keys are used as the headers. Then in a for loop iterating over the entire list of dicts, csv.DictWriter.writerow() constructs the .csv file.

In the case of a successful extraction, the extractor() function returns a confirmation message to main with the f-string: f"File {file_name} has been exported successfully"

Note on the encoding parameter of the open() function. During testing I ran into a prolem where at some point, one of the results had text in a different encoding, which my device did not recognize during extracting, this caused the error "UnicodeEncodeError: 'charmap' codec can't encode character '\u0119'". It took some googling as I am not yet well versed in text codes, but it turned out that the easiest solution was to force the encoding to utf-8. The solution worked.


## Future plans
1. Using regex to validate search parameters.
2. Handling pagination using oop. I would turn search results into a class, and one of its mehtods would handle "page turning".
3. Getting back a URL to dowload each of the books in the results. This has proved an unexpected challenge to be solved.
4. Possibility to add more libraries of free ebooks not just the Gutenberg library

And that's it :)




