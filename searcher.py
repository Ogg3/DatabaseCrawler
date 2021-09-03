import sqlite3
import sys
import os

path=r'C:\Users\Forensic\Desktop\Research\DAtabase\testing\databases'
list_of=[]

for root, dirs, files in os.walk(path):
    for file in files:
        list_of.append(os.path.join(root,file))

with open("HTML_Report.html", "w") as f:
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
    for fil in list_of:    
        try:
            conn = sqlite3.connect(fil)

            Start="""
<button onclick="hide(%s)">%s</button>

<div id="%s" style="Display:none;">
    <table>

""" % (fil,fil,fil)
            f.write(Start)
        
            curs = conn.execute("SELECT sql FROM sqlite_master")

            for i in curs:
                for j in i:
                    if j != None:
                       for y in j.split(): 
                            if 'latitude' in y or 'longitude' in y or 'location' in y:
                                Table_Header="""
        <tr>
            <th> %s </th>
        </tr>

""" % (j.split()[2])
                                f.write(Table_Header)
                                Table_Data="""
        <tr>
            <td> %s </td>
        </tr>
""" % (y)
                                f.write(Table_Data)
                            
                                     
        except Exception as e:
            print(e)
    End="""
</div>

"""
    f.write(End)
