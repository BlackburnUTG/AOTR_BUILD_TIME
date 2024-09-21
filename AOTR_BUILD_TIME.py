from lxml import etree as ET
import os
import math
import time
import re
from copy import deepcopy
import sys
import copy

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"



#BTS DIC FOR TEXT.FILE
btiw_set_global = set()
allowed_tags_global = [
    'Freighter'.lower(),
    'HeroCompany'.lower(), 
    'GroundCompany'.lower(),
    'SecondaryStructure'.lower(), 
    'SpaceUnit'.lower(), 
    'SpecialStructure'.lower(), 
    'Squadron'.lower(), 
    'StarBase'.lower(),
    'UniqueUnit'.lower(),    
    ]

allowed_root_tags_global = [
    'Containers',
    'EmpireGroundCompanies',
    'FighterUnits',
    'GenericHeroUnits',
    'GenericHeroUnits',
    'GroundInfantry_Units',
    'GroundUnits',
    'GroundVehicles',
    'HeroCompanies',
    'HeroUnits',
    'Indigenous_Units',
    'RebelGroundCompanies',
    'SpaceCorvettes',
    'SpaceUnitsCapital',
    'SpaceUnitsCruisers',
    'SpaceUnitsFreighters',
    'SpaceUnitsFrigates',
    'SpaceUnitsSupers',
    'SpecialStructures',
    'specialstructures_empire_files',
    'Specialstructures_GroundMinor',
    'specialstructures_rebel_files',
    'Squadrons',
    'StarBases',
    'Template_Data',
    'Templates_Space',
    'Templates_Ground',
    'TransportUnits',
    'UnderworldGroundCompanies',
]

#key is name, unit is value
units_dic_global = {}



def main():

    start_time = time.time()
    xml_folder = os.path.join(get_aotr_path(), r"Data\XML")
    xml_list = get_xml_list(xml_folder)
    aproved_xml_list, units_dic = aprove_xml_and_create_units_dic(xml_list)
    make_btw(units_dic)
    write_btw(units_dic, aproved_xml_list)
    
    print(f'{GREEN}Done, no errors{RESET}')
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The program took {execution_time} seconds to execute.")

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#                  FUNCTIONS
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def get_aotr_path():
    aotr_path = os.getcwd()

    # надо вернуть снять комент как будет готово
    # if os.path.basename(aotr_path) != "1397421866":
    #     raise FileNotFoundError(r"you need to place the file in Aotr directory: Steam\steamapps\workshop\content\32470\1397421866\")
    return aotr_path

def get_xml_list(xml_folder):
    xml_list_path = []
    for filename in os.listdir(xml_folder):
        path = get_xml_file_path(xml_folder, filename)
        if path:
            xml_list_path.append(path)

    units_folder = os.path.join(xml_folder, 'UNITS')         
    for dirpath, dirnames, filenames in os.walk(units_folder):
        for filename in filenames:
            path = get_xml_file_path(dirpath, filename)
            if path:
                xml_list_path.append(path)

    return xml_list_path


def get_xml_file_path(folder, filename):
    if filename.lower().endswith('.xml'):
        return os.path.join(folder, filename)
    return None



def aprove_xml_and_create_units_dic(xml_list):
    aproved_xml_list = []
    units_dic = {}
    for file in xml_list:
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            if root.tag not in allowed_root_tags_global:
                continue
            for child in root:
                if child.tag ==  ET.Comment:
                    continue
                #коменчу т.к. мне кажется что сначала лучше добавить ваще всё. А потом когда буду юзать бтс - менять только нужное       
                # lowercase_allowed_tags =  [s.lower() for s in allowed_tags_global]
                # if child.tag.lower() not in lowercase_allowed_tags:
                #     continue  

                # elements = get_elements(child)
                # if elements['bts0_attrib'] == True or elements['unique_attrib'] == True :
                #     continue 
                
                name_attrib = child.attrib.get('Name', "").strip()
                if name_attrib == 'Rebel_AllArmy_MTwilek_A280_Suppr':
                    pass
                # if '_Dummy'  in name_attrib or '_Death_Clone' in name_attrib:
                #     continue                 
                units_dic[name_attrib] = child 
            aproved_xml_list.append(file)
         
        except ET.ParseError as e:
            print(f"{RED}Error parsing file {file}: {e}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}Error processing file {file}: {e}\n Error with unit: {elements['name_attrib']}{RESET} ")
            return False
    return (aproved_xml_list, units_dic)


def make_btw(units_dic):
    for unit in units_dic.values():
        #if Build_Time_Seconds and no encyclopedia
        if (encyclopedia := unit.find('Encyclopedia_Text')) == None:
            if (bts := unit.find('Build_Time_Seconds')) == None: 
                continue
            if (unit_tag_variant := unit.find('Variant_Of_Existing_Type')) == None:
                continue
            variant_name = unit_tag_variant.text.strip()
            variant_encyclopedia = get_encyclopedia_from_variant(units_dic, variant_name)
            if variant_encyclopedia == False or variant_encyclopedia == None :
                continue
            encyclopedia = copy.deepcopy(variant_encyclopedia)
            btw = convert_bts_to_btw(bts)
            if btw == False:
                continue
            add_btw_to_encyclopedia(encyclopedia, btw)
            encyclopedia_tag = ET.Element("Encyclopedia_Text")
            encyclopedia_tag.text = encyclopedia.text
            unit.append(encyclopedia_tag)
            continue

        #if encyclopedia and Build_Time_Seconds
        if (bts := unit.find('Build_Time_Seconds')) != None:
            btw = convert_bts_to_btw(bts)
            if btw == False:
                continue            
            add_btw_to_encyclopedia(encyclopedia, btw)

        #if encyclopedia     
        elif (unit_tag_variant := unit.find('Variant_Of_Existing_Type')) == None:
            continue
        else:
            variant_name = unit_tag_variant.text.strip()
            bts = get_bts_from_variant(units_dic, variant_name, unit)
            if bts == False or bts == None:
                continue
            btw = convert_bts_to_btw(bts)
            if btw == False:
                continue            
            add_btw_to_encyclopedia(encyclopedia, btw)
                         


def get_encyclopedia_from_variant(units_dic, variant_name):
    try:
        unit = units_dic[variant_name]
    except Exception as e:
        print(f"{RED} Error: {e}\n No such key in dic: {variant_name} {RESET}")
        sys.exit()
    
    if (encyclopedia := unit.find('Encyclopedia_Text')) == None:
            unit_tag_variant = unit.find('Variant_Of_Existing_Type')
            if unit_tag_variant == None:
                print(f"{variant_name} has no variant")
                return False
            get_encyclopedia_from_variant(units_dic, unit_tag_variant.text.strip())
    else:
        return encyclopedia   




def get_bts_from_variant(units_dic, variant_name, unit):
    value = units_dic.get('AT_AT_Walker_2')
    if 'Stormtrooper_Team' in variant_name:
        pass

    try:
        unit = units_dic[variant_name]

        if (bts := unit.find('Build_Time_Seconds')) == None:
            unit_tag_variant = unit.find('Variant_Of_Existing_Type')
            if unit_tag_variant == None:
                print(f"{variant_name} has no variant")
                return False
            get_bts_from_variant(units_dic, unit_tag_variant.text.strip(), unit)
        else:
            return bts
    
    except Exception as e:
        print(f"{RED} Error: {e}\n No such key in dic: {variant_name} {RESET}")
        sys.exit()


def add_btw_to_encyclopedia(encyclopedia, btw):
    if btw == False:
        pass
    # Split the text into lines
    try:    
        lines = encyclopedia.text.splitlines()
    except AttributeError:
        return None
        
    while lines[-1].isspace():
        lines.pop()
    # Check if the last line contains BLACKBURN_BUILD_TIME_WEEKS
    if "BLACKBURN_BUILD_TIME_WEEKS" in lines[-1]:
        lines.pop()
    
    count_tab = lines[-1].count('\t')
    count_space = lines[-1].count(' ')
    while count_space > 0:
        count_tab += 1
        count_space -= 4

    # Join the filtered lines back into a single string
    lines.append("\t" * count_tab + f"BLACKBURN_BUILD_TIME_WEEKS_{btw}\n" + "\t" * (count_tab - 1))
    encyclopedia.text = "\n".join(lines)


def convert_bts_to_btw(bts_element):
    try:
        seconds = float(bts_element.text)
    except ValueError: 
        print(f"{RED}ERROR! Build_Time_Seconds is not a number{RESET}")
        return False
    except AttributeError:
        return False
    if seconds == float(0):
        return False
    # Calculate the number of weeks, adjusting and applying the ceiling to half-week precision
    rounded_weeks = math.ceil((seconds / 45) * 2 - 0.5) / 2
    if rounded_weeks % 1 == 0:
        rounded_weeks = str(int(rounded_weeks))
    else:
        rounded_weeks = str(rounded_weeks)
    return rounded_weeks

def write_btw(units_dic, aproved_xml_list):
    for file in aproved_xml_list:
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            print(f"Processing file: {file}")
            for child in root:
                if child.tag ==  ET.Comment:
                    continue
                name_attrib = child.attrib.get('Name', "").strip() 
                try:
                    new_child = units_dic[name_attrib]
                except:
                    continue
                root.replace(child, new_child)
                enyclopedia = child.find('Encyclopedia_Text')
                

            path_to_save_file = file.replace(r'\XML', r'\XML\new_files')
            path_to_folder = os.path.dirname(path_to_save_file)
            if 'CONTAINERS.XML' in file:
                pass
            if not os.path.exists(path_to_folder):
                os.makedirs(path_to_folder)
            tree.write(path_to_save_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
            print('Done')    


        except ET.ParseError as e:
            print(f"{RED}Error parsing file {file}: {e}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}Error processing file {file}: {e}{RESET} ")
            return False                




if __name__ == "__main__":
    main()



#вроде все. осталось почистить всякие лишние иф элсы
#идея для следующей проги: major hero для юнитов