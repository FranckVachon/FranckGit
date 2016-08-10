"""
Basis for http/api stuff from https://realpython.com/blog/python/api-integration-in-python
To work with: https://kc.kobotoolbox.org/api/v1/
"""
import requests
import csv
import json as js

# Set of keys - in a dict, the name, children, type words are keys we'll look for
# Set them as global constants so we can easily transition if it differs in Aggregate, ONA, etc
# Could be moved to variables.csv as well?
SERVER = "kobo"
HEADER_KEYS = ["name"]
GRP_KEYS = ["children"]
GRP_TYPE = {"type_key": "type", "type_names": ["group", "repeat"]}
GRP_SEPARATOR = {'kobo': '/'}
KEYS_FORMDEF = ["name"]
"""
##TODO - define main() or similar functions that do what D3 will need. Quickly would mean 1-
update the data.csv file that D3 is using, 2-update the dropdown list of forms that can be
vizualized/updated. I guess the dropdown option would wait a bit. Not such a priority.
##TODO - I've changed the location of the data.csv file where I expect it to write data, much
reflect this in the code.
##TODO - must better figure out the data structure that Kobo is sending me. Don't yet know all
the details of how that works. There's a method in the JSON lib for python that allows a clear
print of a JSON file/data block. That would help.
##TODO - some code clean-up
##TODO - I might want to consider working in JSON instead of CSV. In a way it is a more logical
data structure - e.g. the keys make sense, more than data[4] at least. Though D3 has a smart way 
of working with headered csv.
##TODO - MUST simplify the class & how the method works. If I want to write to CSV, I should be
able to just my_form.write_to_csv() & the method figures out if it needs to fetch data or no. No
need for piles of calls repeated outside the class. Class methods should be smart methods.
"""

"""
THE PLAN FOR NESTED GRPS
I think I can solve the nested grps pretty easily with recursion. Basically, in the DATA, if I get a list as a value
corresponding to a key, then it MUST be a repeat grp member. At the same level as in the key, _id would allow to link
back the grp members to the main submission, so should be added to that group's data file as well. Following it,
_uuid also is, but formhub/uuid isn't (that one is form-wide, not submission-wide uuid).

Or, I could start by saying that for the purpose of the demo, I do not yet support nested grps for this D3 thing -
only flat forms. That would allow me to have a working demo on D3 faster, and still add that support later. Actually,
yeah, screw that and let's play on D3 sooner instead.
"""


"""
Then on to other worries - how to write my CSV file in a directory that is higher up than the script. The following
should do. It may be slightly more complicated than that on the server or not - will have to test. For that worked here.

import os
path = os.path.join(os.path.dirname(__file__),"..","..","Tutorials/","test")
with open(path) as file:
    reader = csv.reader(file, delimiter=',')
    content = dict([])
    for row in reader:
        print(row)
"""


class Forms:
    """
    Each class instance is "one form". Will get its data, formdef, etc. Need PK to instantiate.
    """
    def __init__(self, pk=0):
        """
        :param: pk = the formId as expect by Kobo to retrieve it
        :return:
        """
        if pk != 0:
            self.raw_formdef = Forms.retrieve_formdef(pk).json()
            self.pk = pk
        else:
            self.raw_formdef = list()   # Not sure if default type should indeed be list() to verify
        self.headers = list()   # Contains the headers correctly formated for csv output
        self.resp_json = list()
        self.writable_dict = list()  # Formated for use with dictwriter
        self.extract_headers()

    @staticmethod
    def recursive_finder(iterable, keys_to_find, found=None, current_grp=""):
        """
        :param
        iterable: list, dict, iterable item
        keys_to_find: list of which keys we're looking for in the recursion
        found: list strings found so far
        current_grp: the outer_grp/inner_grp/prompt_name. Provides the "root" part
        :return: found, a list of value that matched something in HEADER_KEYS
        Recursively digs into an iterable which may contain other iterable. Stops at nesting's bottom
        """
        if found is None:
            found = list([])
        if isinstance(iterable, dict):
            # Dictionary syntax - may be type group & have children - check first
            if GRP_TYPE["type_key"] in iterable:  # The chunk of json has a "type" attribute
                if iterable[GRP_TYPE["type_key"]] in GRP_TYPE["type_names"]:
                    # "type" has group or repeat group as value
                    current_grp += iterable[HEADER_KEYS[0]] + GRP_SEPARATOR[SERVER]  # Setting the nested group prefix
            for x in iterable:
                if isinstance(iterable[x], (list, dict)) and not isinstance(iterable[x], str):
                    # The item is an iterable, recursion
                    Forms.recursive_finder(iterable[x], keys_to_find, found, current_grp)
                else:
                    # The item isn't iterable. No recursion
                    if x in keys_to_find:
                        found.append(current_grp + iterable[x])
        elif isinstance(iterable, list):
            # List syntaxe
            for i in range(0, len(iterable)):
                if isinstance(iterable[i], (list, dict)) and not isinstance(iterable[i], str):
                    Forms.recursive_finder(iterable[i], keys_to_find, found, current_grp)
                else:
                    # Members of lists should all be dicts
                    pass
        return found

    @staticmethod
    def retrieve_formdef(pk):
        # For now working on JSON. But perhaps other format could be useful, so let's set a variable form_format
        # Static because that could be useful as a method outside a class instance....
        form_format = "json"
        local_suffix = "forms/"
        resp = requests.get(_url(local_suffix + str(pk) + "/form." + form_format), auth=(USER, PASS))
        if resp.status_code != 200:
            print("Not 200 ok, instead got:")
            print(resp.status_code)
            return None
        else:
            return resp

    @staticmethod
    def read_csv_output(path):
        """
        Reads the csv file. Returns a dict
        """
        with open(path) as file:
            reader = csv.reader(file, delimiter=',')
            content = dict([])
            for row in reader:
                content[row[0]] = [row[i] for i in range(1, len(row))]
            return content

    @staticmethod
    def load_params(file):
        """
        Loads the variables neeeded (API URL, user, pass, etc). Assumes files is in current dir
        :param file:
        :return:
        """
        my_vars = Forms.read_csv_output(file)
        return my_vars

    def extract_headers(self):
        """
        Sets the self.headers attribute for CSV export.
        :return:None
        """
        if not self.raw_formdef:
            self.raw_formdef = Forms.retrieve_formdef(self.pk)
            self.headers = self.recursive_finder(self.raw_formdef, HEADER_KEYS)
        else:
            self.headers = self.recursive_finder(self.raw_formdef, HEADER_KEYS)

    def store_http_response(self, response):
        #Still needed?
        self.resp_json = response.json()
        return self.resp_json

    def create_writable_dict(self):
        """
        Formats an object directly usable by the dictwriter object for csv export
        """
        if not self.resp_json:
            self.get_form_data()
        if not self.headers:
            self.extract_headers()
        self.writable_dict = list()
        output = self.get_resp_json()
        headers = self.get_headers()
        for i in range(0, len(output)):
            self.writable_dict.append({key: output[i][key] for key in headers if key in output[i]})

    def write_to_csv(self):
        """
        This is currently not great - I have to piece toghether the code to get form def, headers, etc.
        Best would be a param or better yet the code would test itself to see if headers, formdef have been
        obtained. If yes if just writes stuff, otherwise extracts them.
        :return:
        """
        extension = ".csv"
        self.create_writable_dict()
        output = self.get_writable_dict()
        # Extract fieldnames list
        fieldnames = [keys for keys in self.get_headers()]  # Base one from the HEADERS
        test_file = open(FILE_TO_WRITE + extension, 'w')
        csvwriter = csv.DictWriter(test_file, extrasaction='ignore', delimiter=',', fieldnames=fieldnames)
        csvwriter.writeheader()
        for row in output:
            csvwriter.writerow(row)
        test_file.close()

    def write_to_tsv(self):
        extension = ".tsv"
        self.create_writable_dict()
        output = self.get_writable_dict()
        fieldnames = [keys for keys in self.get_headers()]  # Base one from the HEADERS
        # Extract fieldnames list
        test_file = open(FILE_TO_WRITE + extension, 'w')
        csvwriter = csv.DictWriter(test_file, extrasaction='ignore', delimiter='\t', fieldnames=fieldnames)
        csvwriter.writeheader()
        for row in output:
            csvwriter.writerow(row)
        test_file.close()

    def get_form_data(self, pk=None):
        """
        Gets you all the submissions for formID [pk]. Uses /data/pk endpoint
        Returns the response as per server. Returns None if server response error
        """
        if pk is None:
            pk = self.pk
        local_suffix = "data/"
        resp = requests.get(_url(local_suffix + str(pk)),  auth=(USER, PASS))

        if resp.status_code != 200:
            print("Not 200 ok")
            print(resp.status_code)
            return None
        else:
            self.resp_json = resp.json()
            return resp

    def __str__(self):
        return str("Luke, I am your form")

    def get_resp_json(self):
        return self.resp_json

    def get_headers(self):
        return self.headers

    def get_raw_formdef(self):
        return self.raw_formdef

    def get_writable_dict(self):
        return self.writable_dict

# Name of csv file containing constants
CONSTANT_FILE = "variables"
VARS = Forms.load_params(CONSTANT_FILE)
# CONSTANT_FILE has the following info:
ROOTURL = VARS['ROOTURL'][0]
USER = VARS['USER'][0]
PASS = VARS['PASS'][0]
FORM_ID = VARS['FORM_IDS'][0]    # this the nested group (no repeat) test form v5
FILE_TO_WRITE = VARS['FILE_TO_WRITE'][0]


def _url(path):
    """
    :param path: the suffixes the caller needs, after the root
    :return: The full URL to call to (concatenates with root
    """
    return ROOTURL + path


def get_project_list():
    # Works fine
    """
    :return:
    """
    local_suffix = "projects"
    resp = requests.get(_url(local_suffix),  auth=(USER, PASS))
    print(USER, PASS)
    if resp.status_code != 200:
            print("Not 200 ok")
            print(resp.status_code)
    else:
        tell_it_all(resp.json())
        for my_items in resp.json():
            print("Title: ", my_items["title"], "FormID/Projec:t ", my_items["formid"])
    return resp


def api_comm(pk):
    """
    Gets you all the submissions for formID [pk]. Uses /data/pk endpoint
    Returns the response as per server. Returns None if server response error
    """
    local_suffix = "data/"
    resp = requests.get(_url(local_suffix + str(pk)),  auth=(USER, PASS))

    if resp.status_code != 200:
        print("Not 200 ok")
        print(resp.status_code)
        return None
    else:
        return resp


def get_form_list(owner=""):
    # Works fine
    """
    :return:
    """
    if owner:
        local_suffix = "forms?owner=" + owner
    else:
        local_suffix = ""
    resp = requests.get(_url(local_suffix),  auth=(USER, PASS))
    if resp.status_code != 200:
            print("Not 200 ok")
            print(resp.status_code)
    else:
        for my_items in resp.json():
            print("Title: ", my_items["title"], "FormID: ", my_items["formid"])
    return resp


def authenticate(rooturl=ROOTURL, user=USER, password=PASS):
    """
    :param rooturl: a kobo-wide URL. Could be other server with same API.
    :param user: the username of the target account
    :param password: the password of that account
    :return: the raw response from the server for now. Ultimately this could
    implement a clearer error message system than 401, 404, etc
    """
    resp = requests.get(_url(rooturl), auth=(user, password))
    local_suffix = "formlist/json"
    url = rooturl + local_suffix
    print(url)
    resp = requests.get(url, auth=(user, password))
    req_param = {'Authorization':'Token TOKEN_KEY'}
    # resp = requests.get(_url(rooturl), headers=(req_param))
    print(resp)
    if resp.status_code != 200:
        print("Return not 200")
        return resp
    else:
        for el in resp:
            print(el)
        return resp


def generic_call(url_suffix):
    """
    Takes a fully formated URL (including any pk, USER, etc) and returns the results (raw form, as returned by
    the API
    """
    resp = requests.get(_url(url_suffix), auth=(USER, PASS))
    return resp


def update_data_d3():
    """
    Main function called by Flask. Updates the data.csv file for D3 for the specified form in variables
    """
    return None


def update_formlist_d3():
    """
      Formlist update for D3, called by Flask. Allows to select different things for the dropdowns.
    """
    my_forms = get_form_list(USER)
    return my_forms

"""
Test functions, debugging, etc.
"""


def test1(pk):
    """
    Base case: get form headers
    """
    my_form = Forms(pk)
    print(my_form.get_headers())
    print(my_form.get_raw_formdef())


def test2(pk):
    """
    Get form headers & data
    """
    my_form = Forms(pk)
    print("1:", my_form.get_resp_json())
    print("2:", my_form.get_headers())
    my_form.store_http_response(api_comm(pk))
    print("3:", my_form.get_resp_json())
    print("4:", my_form.get_headers())


def test3(pk):
    """
    Get formdef, data, then write to CSV
    """
    my_form = Forms(pk)
    my_form.store_http_response(api_comm(pk))
    my_form.write_to_csv()


def test4(pk):
    """
    Gets data, uses the cumulative method & writes a TSV
    """
    my_form = Forms(pk)
    my_form.store_http_response(api_comm(pk))
    my_form.write_to_tsv(True)


def test5():
    result = generic_call('/forms/' + str(FORM_ID)).json()
    print(result)


def tell_it_all(obj, dicts_list=list(), dicts_content=list(), lists_list=list(), lists_content=list()):
    """
    Let's try to print level per level instead
    """
    #Listing all dict, lists, from top-level to lowest level
    lists = 0
    dicts = 0
    others = 0
    current_dict = list()
    current_list = list()
    other_headers = list()
    # Count the number of lists, dicts, in each iteration - check if dict or list for syntaxe
    #Figure out if obj is a list or dict (for syntax only). We sum up content of this level here
    print("level:", obj)
    if isinstance(obj, dict) and not isinstance(obj, str):
        # It's a dict
        for items in obj:
            if isinstance(obj[items], dict) and not isinstance(obj[items], str):
                dicts += 1
                current_dict.append(obj[items])
            elif isinstance(obj[items], list) and not isinstance(obj[items], str):
                lists += 1
                current_list.append(obj[items])
            else:
                others += 1
                other_headers.append(items)
    elif isinstance(obj, list) and not isinstance(obj, str):
        # It's a lists
        for i in range(0, len(obj)):
            if isinstance(obj[i], dict) and not isinstance(obj[i], str):
                dicts += 1
                current_dict.append(obj[i])
            elif isinstance(obj[i], list) and not isinstance(obj[i], str):
                lists += 1
                current_list.append(obj[i])
            else:
                others += 1
    print("This level is ", type(obj), " and contains:")
    print("Dicts: " + str(len(current_dict)) + " Lists: " + str(len(current_list)) + " Others: " + str(len(other_headers)))
    print("headers: ", other_headers)
    #Here we iterate again, and recursively call the function to analyse one level deeper if the component is list or dict
    if isinstance(obj, dict):
        for x in obj:
            if isinstance(obj[x], (list, dict)) and not isinstance(obj[x], str):
                # tell_it_all(obj[x], dicts_list, dicts_content, lists_list, lists_content)
                pass
    elif isinstance(obj, list):
        for i in range(0, len(obj)):
            if isinstance(obj[i], (list, dict)) and not isinstance(obj[i], str):
                tell_it_all(obj[i], dicts_list, dicts_content, lists_list, lists_content)
    return (dicts_list, dicts_content, lists_list, lists_content)


def test_pretty_json_formdef():
    my_form = Forms(FORM_ID)
    my_def = my_form.retrieve_formdef(FORM_ID)
    my_def = js.dumps(my_def.json(), indent=1)
    with open("formdef.json","w") as f:
        f.write(my_def)
    return None


def test_pretty_json_data():
    my_form = Forms(FORM_ID)
    my_def = my_form.get_form_data()
    my_def = js.dumps(my_def.json(), indent=1)
    with open("formdef.json", "w") as f:
        f.write(my_def)
    return None


def test_extract_formdef():
    """
    Extracts main elements of the formdef
    :return:
    """
    my_form = Forms(FORM_ID)
    my_def = my_form.retrieve_formdef(FORM_ID)
    recursed = Forms.recursive_finder(my_def.json(), KEYS_FORMDEF)
    return None

def test_write_data_to_csv():
    my_form = Forms(FORM_ID)
    my_form.write_to_csv()
    return None

def test_get_repeatgrps():
    my_form = Forms(FORM_ID)
    data = my_form.get_form_data().json()
    recursive_iterator(data)

def recursive_iterator(iterable):
    if isinstance(iterable, list):
        for key,value in enumerate(iterable):
            print("key: ", key, " value:", value)
            recursive_iterator(iterable[key])
    elif isinstance(iterable, dict):
        for key in iterable:
            print("key: ", key, " value:", iterable[key])
            recursive_iterator(iterable[key])
    return None



"""
 End of debugging, testing, etc.
"""
# test_get_repeatgrps()
# update_formlist_d3()
# test_pretty_json()
# test_pretty_json_data()
# extract_formdef()
# test_write_data_to_csv()



