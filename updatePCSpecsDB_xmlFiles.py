'''
STARTS WITH:::
Machine name:
System Model:
Processor:
Memory:
Card name:
Time of this report:

NEEDS CUSTOM PARSER:::
Disks:
'''
# ltbraries
import os
import glob
import xmltodict
import sqlite3

# path for the database (for sqlite)(if using another connector, may be necessary to use and URL version to connect (MySQL))
db_path = 'D:\Documents\Databases\generic_specs_db\genspecdb'
# directory to search for the files
directory = ''
# get a list of all .xml files in the 'directory'
dxdiag_files = glob.glob(os.path.join(directory, '*.xml'))

def send_to_database(pc_info:dict):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        sql = '''INSERT INTO pcstable(NAME,MOBO,CPU,MEMORY,GPU,DISKS,LASTREPORT) 
                VALUES (?,?,?,?,?,?,?)'''
        cursor.execute(sql,[pc_info["name"],pc_info["mobo"], pc_info["cpu"], pc_info["memory"], pc_info["gpu"], pc_info["disks"], pc_info["lastreport"]])
        conn.commit()
    except sqlite3.IntegrityError as err:
        try:
            sql = '''UPDATE pcstable 
                    SET MOBO = ?,CPU = ?,MEMORY = ?, GPU = ?, DISKS = ?, LASTREPORT = ?
                    WHERE NAME = ?'''
            cursor.execute(sql,[pc_info["mobo"], pc_info["cpu"], pc_info["memory"], pc_info["gpu"], pc_info["disks"], pc_info["lastreport"], pc_info["name"]])
            conn.commit()
        except Exception as err:
            print(err)
    finally:
        conn.close()
        print("finished connection")
# ----------------------------------------------------------------------------------------- #

# iterate over the dxdaig_files, put the info on a dictionary, extract the data and send to the data base
for pc in dxdiag_files:
    with open(pc, encoding='utf8') as file:
        tdict = xmltodict.parse(file.read())
        all_storage_drivers = ""

        # extract the storage disks information and calculate the size for each one
        for x in tdict['DxDiag']['LogicalDisks']['LogicalDisk']:
            all_storage_drivers += f"|| Model: {x['Model']} - Size: {str(int(x['MaxSpace']) / 1024)} ||\n"

        # put together a dictionary with all data to be send to the database
        current_pc_dict = {
        "name":str(tdict['DxDiag']['SystemInformation']['MachineName']),
        "mobo":str(tdict['DxDiag']['SystemInformation']['SystemModel']),
        "cpu":str(tdict['DxDiag']['SystemInformation']['Processor']),
        "memory":str(tdict['DxDiag']['SystemInformation']['Memory']),
        "gpu":str(tdict['DxDiag']['DisplayDevices']['DisplayDevice']['CardName']),
        "disks":str(all_storage_drivers),
        "lastreport":str(tdict['DxDiag']['SystemInformation']['Time'])
        }

        #print(current_pc_dict)

        # insert the current pc data into the database
        send_to_database(current_pc_dict)
        
            
    































