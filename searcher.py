import sqlite3
import sys
import os

# Set vars
path=os.getcwd()
list_of=[]

# get files, directorys
for root, dirs, files in os.walk(path):
    for file in files:
        
        # Add files to be parsed
        list_of.append(os.path.join(root,file))

# Start writing html report
with open("HTML_Report.html", "w") as f:
    
    # Hide elements
    JavascriptFunc="""
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
"""
    f.write(JavascriptFunc)
    
    # Parse files
    for fil in list_of:
        
        # Check if file is database
        try:
            conn = sqlite3.connect(fil)

            Start="""
<button onclick="hide(%s)">%s</button>

<div id="%s" style="Display:none;">
    <table>

""" % (fil,fil,fil)
            f.write(Start)
            
            # Get structure of the database
            curs = conn.execute("SELECT sql FROM sqlite_master")
            
            # Go through query results
            for i in curs:
                
                # ?
                for j in i:
                    
                    # ?
                    if j != None:
                       
                        # ?
                        for data in j.split(): 
                            
                            # Check for strings of interest
                            if 'latitude' in data or 'longitude' in data or 'location' in data:
                                
                                # Make a div with the table name?
                                Table_name = j.split()[2]
                                Table_Header="""
        <tr>
            <th> %s </th>
        </tr>

""" % (Table_name)
                                f.write(Table_Header)
                                
                                # Make a list of data
                                Table_Data="""
        <tr>
            <td> %s </td>
        </tr>
""" % (data)
                                f.write(Table_Data)
                            
        # If file is not a database
        # TODO filterout exception and only display real errors
        except Exception as e:
            print(e)
    End="""
</div>

"""
    f.write(End)
