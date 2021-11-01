import codecs
import sqlite3
import os
import argparse
import traceback
import re

parser = argparse.ArgumentParser(description='DatabaseCrawler.')

parser.add_argument('-i', '--input_path', required=True, action="store", help='Path to folder with files.')
parser.add_argument('-s', '--search_for_data', required=True, action="store", help='A string or regex to search for.')
parser.add_argument('-m', '--search_for_data_mode', required=True, action="store",
                    help='Search mode, T(able) R(ow) D(ata).')
parser.add_argument('-c', '--contains', required=False, action="store_true",
                    help='Wildcard search if flag is set (Sets the query to %string%).')

args = parser.parse_args()

path = args.input_path
search_term = str(args.search_for_data)
search_mode = str(args.search_for_data_mode)
contains = str(args.contains)

print("INFO - Using arguments "+str(args))

def if_regex(input):
    """
    For a given string, check if its a regex
    :param input:
    :return:True or False
    """
    try:
        re.compile(input)
        return False
    except re.error:
        return False


def search_database_data(path, search_term, search_mode, check_type):
    """
    For a given path try to connect, then search database for a string
    :param path: path to file
    :param search_term: a string to search for
    :param search_mode: Search mode can be T(able), R(ow) or D(ata)
    :return: An array of matches [(string, [data])]
    """
    ret = []
    checked = []

    try:
        # Connect to database
        with sqlite3.connect(path) as conn:

            # Magic
            conn.row_factory = sqlite3.Row

            # Set curser
            curs = conn.cursor()
            qr = ""
            # Get all the things
            curs.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for tablerow in curs.fetchall():
                table = tablerow[0]

                # Check if mode is table
                if search_mode == "T":

                    # Check if input if regex
                    if if_regex(search_term):
                        if "".join(re.findall(search_term, str(table))) != "":
                            ret.append("".join(re.findall(search_term, str(table))))

                    # If regular string
                    elif search_term in str(table):
                        ret.append(str(table))

                # Check row count
                qr = "SELECT * FROM {t}".format(t=table)

                curs.execute(qr)
                for row in curs:
                    for field in row.keys():

                        # Check if mode is row
                        if search_mode == "R":

                            # Check if input if regex
                            if if_regex(search_term):
                                if "".join(re.findall(search_term, str(field))) != "":

                                    # Get amount of rows in column
                                    qr = '''SELECT count(%s) FROM %s ''' % (str(field), table)
                                    curs.execute(qr)
                                    for count in curs.fetchall():
                                        ret.append(("".join(re.findall(search_term, str(field))), str(count)))

                            # If regular string
                            elif search_term in str(field):

                                # Get amount of rows in column
                                qr = '''SELECT count(%s) FROM %s ''' % (str(field), table)
                                curs.execute(qr)
                                for count in curs.fetchall():
                                    for i in count:
                                        if i > 0:
                                            string = str(table) + " " + str(field) + " " + str(i)
                                            ret.append(string)

                        # Check if mode is data
                        elif search_mode == "D":
                            hit_string = str(table) + " " + str(field)

                            # Check if input is regex
                            if if_regex(search_term):

                                # If data is blob
                                if type(row[field]) is bytes:
                                    test = "".join(re.findall(search_term, row[field].decode('utf-8', 'ignore')))
                                    if test != -1:
                                        ret.append(string)
                                elif "".join(re.findall(search_term, str(row[field]))) != "":
                                    ret.append(string)

                            # Check if regular string
                            else:
                                # If data is blob
                                if type(row[field]) is bytes:
                                    test = row[field].find(search_term.encode())  # Check if string can be found
                                    if test != -1 and hit_string not in checked:  # Check if hit and if table col has already been checked
                                        checked.append(hit_string)  # Add table col to list
                                        data = get_full_query(path, str(table), str(field), search_term, row.keys(),
                                                              check_type, True)  # Get data based on string
                                        if data != []:  # Check so data is present
                                            ret.append((hit_string, data))  # add data to return list
                                elif search_term in str(row[field]):  # If data is not blob
                                    if hit_string not in checked:  # Check if table col has already been checked
                                        checked.append(hit_string)  # Add table col to list
                                        data = get_full_query(path, str(table), str(field), search_term, row.keys(),
                                                              check_type, False)  # Get data based on string
                                        if data != []:  # Check so data is present
                                            ret.append((hit_string, data))  # add data to return list

    except Exception as e:
        if str(e) != "file is not a database":
            if str(e) != "unable to open database file":
                if "no such module" not in str(e):
                    error = str(traceback.format_exc() + "\n" + str(e.__doc__))
                    write_to_log(error)
                    write_to_log(path + " " + qr)
                    write_to_log("")
                    return []
    return ret


def logfile():
    with open("logfile.html", "w") as f:
        f.write("")


def write_to_log(message):
    """
    Write to log file
    :param message:
    :return:
    """
    with open("logfile.html", 'a') as f:
        print(message)
        f.write(str(message) + '<br>' + "\n")


def get_full_query(path, table, row, string, keys, check_type, blob):
    """

    :param path:
    :param table:
    :return:
    """
    ret = []
    try:
        conn = sqlite3.connect(path)

        curs = conn.cursor()
        if blob:
            if check_type:
                qr = "SELECT * FROM {t} WHERE hex({r}) LIKE '%{f}%'".format(t=table, r=row, f=string)
            else:
                qr = "SELECT * FROM {t} WHERE hex({r}) LIKE '{f}'".format(t=table, r=row, f=string)
        else:
            if check_type:
                qr = "SELECT * FROM {t} WHERE {r} LIKE '%{f}%'".format(t=table, r=row, f=string)
            else:
                qr = "SELECT * FROM {t} WHERE {r} LIKE '{f}'".format(t=table, r=row, f=string)
        curs.execute(qr)
        for i in curs.fetchall():
            count = 0
            for ii in i:
                ret.append((keys[count], ii))
                count = count + 1
        # print(ret)
        return ret

    except Exception as e:
        error = str(traceback.format_exc() + "\n" + str(e.__doc__))
        write_to_log(error)
        write_to_log(qr)


def main(path, search_term, check_type, search_mode):
    """
    For a given folder, go through every file and look for the search_term
    :param path: Path to folder
    :return: None
    """

    list_of = []

    for root, dirs, files in os.walk(path):
        for file in files:
            list_of.append((root, file))

    with open("HTML_Report.html", "w") as f:
        JavascriptFunc = """
<script>
function hide(div){
    var x = document.getElementById(div);
    if(x.style.display === "none"){
        x.style.display = "block";
    }
    else{
        x.style.display = "none";
    }
}
</script>
<style>
    table{
        border: 1px solid black;
        word-wrap: break-word;
        overflow-warp: break-word;
        max-width: 1080px;
    }
    td{
        word-wrap: break-word;
        overflow-warp: break-word;
        max-width: 1080px;
    }
</style>
<body>
<table>
    <td>
       <br>Path:</br>
        %s
    </td>
    
    <td>
        <br>Search term:</br>
        %s
    </td>
    
    <td>
        <br>Search mode:</br>
        %s
    </td>
    
    <td>
        <br>If using regex:</br>
        %s
    </td>
    
    <td> 
        <br>Search type:</br>
        %s
    </td>
</table>
    """ % (path, search_term, search_mode, if_regex(search_term), check_type)
        f.write(JavascriptFunc)
        logfile()
        for path, file in list_of:
            # print("\rINFO - Searching: "+str(os.path.join(path, file)), flush=True, end='')
            data_path = search_database_data(os.path.join(path, file), search_term, search_mode, check_type)
            if data_path != []:
                print("INFO - Found: " + str(os.path.join(path, file)))
                # print(data_path)
                Start = """
    <div>
    <button onclick="hide('%s')">%s</button>
    </div>
    <div id="%s" style="Display:none;">
        

                                    """ % (file, os.path.join(path, file), file)
                f.write(Start)

                # [(string, [(row, data), (row, data)])]
                if search_mode == "D":
                    for i in data_path:
                        first = """
                    <div>
                        <table>
                            %s
                    """ % i[0]
                        f.write(first)
                        # print("File: " + path)
                        for ii in i[1]:
                            Table_Header = """
                            <tr>
                                <th> %s </th>
                                <td> %s </td>
                            </tr>
            
            """ % (str(ii[0]), str(ii[1]))
                            f.write(Table_Header)
                        f.write("""
                        </table>
                    </div>
                    """)

                    End = """
                
            </div>
                    """
                    f.write(End)
                elif search_mode == "R" or search_mode == "T":
                    for i in data_path:
                        first = """
                            <div>
                                <table>
                            """
                        f.write(first)
                        Table_Header = """
                                <tr>
                                    <td> %s </td>
                                </tr>
        
                """ % (i)
                        f.write(Table_Header)
                        f.write("""
                                </table>
                            </div>
                            """)

                    End = """
        
                    </div>
                            """
                    f.write(End)
        End = """
</body>
                """
        f.write(End)

print("INFO - Starting crawler")

main(path, search_term, contains, search_mode)
print("INFO - Done")
