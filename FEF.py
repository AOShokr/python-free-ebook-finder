import requests
import json
from tabulate import tabulate
import sys
import csv
from math import ceil

def main():
    print("\nWELCOME\n")
    inv_inp = 0
    no_results = False
    while True:

        # Give the user options proceed
        print("-=To search by author name or book name please type 'Name'\n\n-=To search by Topic please type 'Topic'\n\n-=For info on this index and the Gutenberg Project, please type 'Info'\n\n-=To exit please type 'Exit'\n".center(20))
        where_to = input("How can I help you today? ").strip().lower()

        # For first time user, explanation of program usage
        if where_to == "info" or where_to == "i":
            print("\n\nThe Gutenberg project, found at gutenberg.org, is a project to collect\nfree ebooks, mostly books that no longer fall under copyright and have\nmoved into the public domain.\n\nin this program you will be able to search the index of the gutenberg\nproject by using a book's name, the author's name, or a specific topic.\n\n")

        # When the user wishes to search with the author's name or a book name or a topic
        elif where_to == "name" or where_to == "topic":
            inv_inp = 0 # resets any invalid inputs

            # procures the serch criteria from customer
            search_cri = input("What are you looking for? ")

            # calls unpacker and requester
            resp = requester(where_to,search_cri)
            if resp == "0results":
                print("\nZero Results returned, please refine your search\n")
                no_results = True
            else:
                results = unpacker(resp)

            # prints out the results and number of results
            if no_results == True:
                pass
            else:
                # pagination in case of more than 100 results
                if len(results) <= 100:
                    print(tabulate(results,headers = "keys",tablefmt = "grid",maxcolwidths = [None,50,20,20,None]))
                    print("Number of results = ",len(results))
                else:
                    no_of_pages = ceil(len(results)/100)
                    page = 0
                    keep_alive = True
                    while keep_alive:
                        print(f"\nPage: {page + 1} out of {no_of_pages}\n")
                        this_page = results[page*100:((page + 1)*100-1)]
                        print(tabulate(this_page,headers = "keys",tablefmt = "grid",maxcolwidths = [None,50,20,20,None]))
                        print(f"\nPage: {page + 1} out of {no_of_pages}\n")
                        print("Number of results = ",len(results))
                        proc = True
                        while proc == True:
                            whats_next = input("\nFor next page please enter 'Next', for the previous page please enter 'Prev', and to go back please enter 'Back' \n").strip().lower()
                            if whats_next == "next" and page < (no_of_pages - 1):
                                page += 1
                                proc = False
                            elif whats_next == "next" and page == (no_of_pages -1):
                                print("We're at the last page, please try again.")
                            elif whats_next == "prev" and page > 0:
                                page = page - 1
                                proc = False
                            elif whats_next == "prev" and page == 0:
                                print("We're at the first page, please try again.")
                            elif whats_next == "back":
                                proc = False
                                keep_alive = False

            # exporting
            if no_results == True:
                pass
            else:
                check_print = input("Do you wish to export the results? (yes/no)").strip().lower()
                if  check_print == "y" or check_print == "yes":
                    file_name = input("What do you want to call the file? (if left blank default name will be 'Results') ")
                    extract = extractor(results,file_name)
                    print(f"\n{extract}\n")

        #exits
        elif where_to == "exit":
            sys.exit()

        #exits after 3 invalid inputs
        else:
            print("Invalid Input")
            inv_inp += 1
            if inv_inp == 3:
                sys.exit("Three invalid inputs")



# Makes the API requests, retrieves a JSON file
def requester(type,kw):

    # chooses which API to call
    if type == "name":
        res = requests.get(f"https://gutendex.com/books?search={kw}")
    elif type == "topic":
        res = requests.get(f"https://gutendex.com/books?topic={kw}")
    elif type == "page":
        res = requests.get(kw)

    #checks if there are no results
    if res.json()["count"] == 0:
        return "0results"
    return res



# unpacks json file into a list of dicts
def unpacker(jfile):

    # the list where the results will be compiled
    res_list = []

    # the list of results returned
    results = jfile.json()["results"]

    # solving for multipage results - each page contains 32 results
    if jfile.json()["next"] != None:
        nxt_pg_lnk = jfile.json()["next"]
        multi_page = True
    else:
        multi_page = False
    while multi_page == True:
        next_page = requester("page",nxt_pg_lnk)
        nxt_pg_lnk = next_page.json()["next"]
        for item in range(len(next_page.json()["results"])):
            results.append(next_page.json()["results"][item])
        if nxt_pg_lnk == None:
            multi_page = False


    # extracting the results values
    for result in range(len(results)):
        # getting the booking id
        id = results[result]["id"]

        # getting the book title
        title = results[result]["title"]

        # getting the author(s)
        auth_list = []
        for auth in results[result]["authors"]:
            auth_list.append(auth["name"])
        author = " & ".join(auth_list)

        # getting the genre
        shelves = []
        for shelf in results[result]["bookshelves"]:
            shelves.append(shelf)
        genre = " & ".join(shelves)

        # getting the languages
        langs = []
        for lang in results[result]["languages"]:
            langs.append(lang)
        language = " & ".join(langs)

        #creating a dict
        one_row = {"Book ID":id,"Name":title,"Author(s)":author,"Genre(s)":genre,"Available Language(s)":language}
        res_list.append(one_row)


    return res_list


# extracts the results to a .csv file
def extractor(the_results,file_name="Results"):
    file_name = file_name + ".csv"
    with open(file_name,"w",newline = "",encoding='utf-8') as the_file: # encoding = 'utf-8' to force the encoiding
        dict_writer = csv.DictWriter(the_file,fieldnames = ["Book ID","Name","Author(s)","Genre(s)","Available Language(s)"])
        dict_writer.writeheader()
        for row in the_results:
            dict_writer.writerow({"Book ID":row['Book ID'],"Name":row['Name'],"Author(s)":row['Author(s)'],"Genre(s)":row['Genre(s)'],"Available Language(s)":row['Available Language(s)']})
    return f"File {file_name} has been exported successfully"








if __name__ == '__main__':
    main()