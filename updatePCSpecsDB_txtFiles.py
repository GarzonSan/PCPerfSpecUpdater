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
# lybraaries
import os
import glob
import sqlite3


# path for the database (for sqlite)(if using another connector, may be necessary to use and URL version to connect (MySQL))
db_path = R'D:\Documents\Databases\generic_specs_db\computerdatabase'
# directory to search for the files
directory = ''
# get a list of all .xml files in the 'directory'
dxdiag_files = glob.glob(os.path.join(directory, '*.txt'))


# FUNCTIONS FOR SPECIFIC OBJECTIVES
def extract_storage_drives(file_path) -> list:
    storage_drives = []
    is_drive_section = False
    current_drive_info = {}

    with open(file_path, 'r', encoding='latin1') as file:
        lines = file.readlines()

        for line in lines:
            # check if current line indicates drive section
            if line.strip().startswith('Drive:'):
                if current_drive_info:
                    storage_drives.append(current_drive_info)
                current_drive_info = {
                    "Drive":line.split("Drive:")[1].strip()
                }
                is_drive_section = True
            elif is_drive_section:
                # check of the end of drive section
                if line.strip() == "":
                    if current_drive_info:
                        storage_drives.append(current_drive_info)
                    is_drive_section = False
                    current_drive_info = {}
                else:
                    #split line by the first colon to separate key and value
                    key_value = line.split(":", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        current_drive_info[key.strip()] = value.strip()
        # Add the last drive info if the file ends without a blank line after the last drive
        if current_drive_info:
            storage_drives.append(current_drive_info)
    
    return storage_drives

def extract_perf_spec(file_path, key_word:str) -> str:
    extracted_data = ""
    with open(file_path, 'r', encoding='latin1') as file:
        lines = file.readlines()
    
    for line in lines:
        if line.strip().startswith(key_word):
            extracted_data = line.split(key_word, 1)[1].strip()
            break
    return extracted_data

def send_to_database(pc_info:dict):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        sql = '''INSERT INTO pcstable_2(name,mobo,cpu,memory,gpu,disks,lastreport) 
                VALUES (?,?,?,?,?,?,?)'''
        cursor.execute(sql,[pc_info["name"],pc_info["mobo"], pc_info["cpu"], pc_info["memory"], pc_info["gpu"], pc_info["disks"], pc_info["lastreport"]])
        conn.commit()
    except sqlite3.IntegrityError as err:
        try:
            sql = '''UPDATE pcstable_2
                    SET mobo = ?,cpu = ?,memory = ?, gpu = ?, disks = ?, lastreport = ?
                    WHERE name = ?'''
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
        all_storage_drivers = extract_storage_drives(pc)
        storage_drivers_string = ""

        for x in all_storage_drivers:
            storage_drivers_string += f"|| Model: {x['Model']} - Size: {x['Total Space']} ||\n"

        # put together a dictionary with all data to be send to the database
        current_pc_dict = {
        "name":str(extract_perf_spec(pc, "Machine name:")),
        "mobo":extract_perf_spec(pc, "System Model:"),
        "cpu":extract_perf_spec(pc, "Processor:"),
        "memory":extract_perf_spec(pc, "Memory:"),
        "gpu":extract_perf_spec(pc, "Card name:"),
        "disks":storage_drivers_string,
        "lastreport":extract_perf_spec(pc, "Time of this report:")
        }

        print(current_pc_dict)

        # insert the current pc data into the database
        send_to_database(current_pc_dict)




















