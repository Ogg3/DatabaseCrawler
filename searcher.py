import sqlite3
import sys
import os
import argparse
import traceback

parser = argparse.ArgumentParser(description='CheckArroyo: Snapchat chat parser.')

# Point to where snapchat dmp is
parser.add_argument('-i', '--input_path', required=True, action="store", help='Path to folder with files.')

# Point to where snapchat dmp is
parser.add_argument('-s', '--search_for_data', required=True, action="store", help='A string to search for.')

# Point to where snapchat dmp is
parser.add_argument('-M', '--search_for_data', required=True, action="store", help='A string to search for.')

args = parser.parse_args()

path = args.input_path
search_term = str(args.search_for)


def search_database_data(path, search_term):
    """
    For a given path try to connect, then search database for a string
    :param path: path to file
    :param search_term: a string to search for
    :return: An array of matches
    """
    ret = []

    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            curs.execute("SELECT name FROM sqlite_master WHERE type='table'")
            with open("Out.txt", "a") as f:
                for tablerow in curs.fetchall():
                    table = tablerow[0]
                    curs.execute("SELECT * FROM {t}".format(t=table))
                    for row in curs:
                        for field in row.keys():
                            string = str(table)+" "+str(field)+" "+str(row[field])
                            if type(row[field]) is bytes:
                                test = row[field].find(search_term.encode())
                                if test != -1:
                                    ret.append(string)
                            try:
                                if search_term in row[field]:
                                    ret.append(string)
                            except Exception as e:
                                #print(e)
                                pass
    except Exception as e:
        if str(e) != "file is not a database":
            if str(e) != "unable to open database file":
                error = str(traceback.format_exc() + "\n" + e.__doc__)
                print(error)
                return []

    return ret


def main(path, search_term):
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
<body>
    """
        f.write(JavascriptFunc)
        for path, file in list_of:
            data_path = search_database_data(os.path.join(path, file), search_term)
            #print(data_path)
            if data_path != []:
                Start = """
    <div>
    <button onclick="hide('%s')">%s</button>
    </div>
    <div id="%s" style="Display:none;">
        <table>

                                    """ % (file, os.path.join(path, file), file)
                f.write(Start)
                for i in data_path:
                    print("File: " + path)
                    Table_Header = """
            <tr>
                <th> %s </th>
            </tr>
    
    """ % (i)
                    f.write(Table_Header)
                    print(i)

            End = """
        </table>
    </div>
            """
            f.write(End)

        End = """
</body>
                """
        f.write(End)
main(path, search_term)