from lxml import etree as ET
import os
import math
import time
import sys
import copy

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

#how many seconds in 1 game week
seconds_in_week_global = 45
#right now there is a bug in aotr, build time is decreased on 20% for every unit. If it will be fixed - this  var should be changed to 1.0
aotr_speed_bonus_bug_global = 0.8

#BTS DIC FOR TEXT.FILE
btiw_set_global = set()

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

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#                  MAIN
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def main():

    start_time = time.time()
    lover_tags()
    xml_folder = os.path.join(get_aotr_path(), r"Data\XML")
    xml_list = get_xml_list(xml_folder)
    aproved_xml_list, units_dic = aprove_xml_and_create_units_dic(xml_list)
    make_btw(units_dic)
    write_btw(units_dic, aproved_xml_list)
    
    print(f'{GREEN}BTW was successfully added to all files, no errors{RESET}')
    print('create_localisation_xml has started..')
    
    data_dict = create_localisation_dict(btiw_set_global)

    # Create the XML file
    create_localisation_xml(data_dict)
    print(f'{GREEN}XML file was created{RESET}')

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The program took {execution_time} seconds to execute.")

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#                  FUNCTIONS
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def lover_tags():
    global allowed_root_tags_global
    allowed_root_tags_global = [_.lower() for _ in allowed_root_tags_global]

    

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
            if root.tag.lower() not in allowed_root_tags_global:
                continue
            for child in root:
                if child.tag ==  ET.Comment:
                    continue
                name_attrib = child.attrib.get('Name', "").strip()              
                units_dic[name_attrib] = child 
            aproved_xml_list.append(file)
         
        except ET.ParseError as e:
            print(f"{RED}Error parsing file {file}: {e}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}Error processing file {file}: {e}\n Error with unit: {name_attrib} {RESET} ")
            return False
    return (aproved_xml_list, units_dic)


def make_btw(units_dic):
    for unit in units_dic.values():
        name_attrib = unit.attrib.get('Name', "").strip()
        if name_attrib == 'E_Shipyard_CapitalModule':
            pass
        #if Build_Time_Seconds and no encyclopedia
        if (encyclopedia := unit.find('Encyclopedia_Text')) == None:
            add_btw_to_encyclopedia_from_variant(unit, units_dic)
            continue

        #if Build_Time_Seconds and encyclopedia 
        elif (bts := unit.find('Build_Time_Seconds')) != None:
            btw = convert_bts_to_btw(bts)
            if btw == False:
                continue            
            add_btw_to_encyclopedia(encyclopedia, btw)

        #if encyclopedia     
        else:
            if (unit_tag_variant := unit.find('Variant_Of_Existing_Type')) == None:
                continue            
            variant_name = unit_tag_variant.text.strip()
            bts = get_bts_from_variant(units_dic, variant_name, unit)
            if bts == None:
                continue
            btw = convert_bts_to_btw(bts)
            if btw == None:
                continue            
            add_btw_to_encyclopedia(encyclopedia, btw)
                         

def add_btw_to_encyclopedia_from_variant(unit, units_dic):
    if (bts := unit.find('Build_Time_Seconds')) == None: 
        return
    if (unit_tag_variant := unit.find('Variant_Of_Existing_Type')) == None:
        return
    variant_name = unit_tag_variant.text.strip()
    variant_encyclopedia = get_encyclopedia_from_variant(units_dic, variant_name)
    if variant_encyclopedia == None :
        return
    encyclopedia = copy.deepcopy(variant_encyclopedia)
    btw = convert_bts_to_btw(bts)
    if btw == False:
        return
    if add_btw_to_encyclopedia(encyclopedia, btw) == False:
        return
    encyclopedia_tag = ET.Element("Encyclopedia_Text")
    encyclopedia_tag.text = encyclopedia.text
    unit.append(encyclopedia_tag)
    

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
                return None
            get_encyclopedia_from_variant(units_dic, unit_tag_variant.text.strip())
    else:
        return encyclopedia   




def get_bts_from_variant(units_dic, variant_name, unit):
    try:
        unit = units_dic[variant_name]

        if (bts := unit.find('Build_Time_Seconds')) == None:
            unit_tag_variant = unit.find('Variant_Of_Existing_Type')
            if unit_tag_variant == None:
                print(f"{variant_name} has no variant")
                return None
            get_bts_from_variant(units_dic, unit_tag_variant.text.strip(), unit)
        else:
            return bts
    
    except Exception as e:
        print(f"{RED} Error: {e}\n No such key in dic: {variant_name} {RESET}")
        sys.exit()


def add_btw_to_encyclopedia(encyclopedia, btw):
    # Split the text into lines
    try:
        #this is done because of stupid comment line inside encyclopedia tag for some units   
        text_content = encyclopedia.xpath('string()')
        lines = [line for line in text_content.splitlines() if line]
    except AttributeError:
        return False
    try:    
        while lines[-1].isspace():
            lines.pop()
    except IndexError:
        return False
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
    encyclopedia.clear()
    encyclopedia.text = "\n".join(lines)
    btiw_set_global.add(f"BLACKBURN_BUILD_TIME_WEEKS_{btw}")







def convert_bts_to_btw(bts_element):
    try:
        seconds = float(bts_element.text)
    except ValueError: 
        print(f"{RED}ERROR! Build_Time_Seconds is not a number{RESET}")
        return None
    except AttributeError:
        return None
    
    if seconds == float(0):
        return None
    # Calculate the number of weeks, adjusting and applying the ceiling to half-week precision
    rounded_weeks = math.ceil(((seconds * aotr_speed_bonus_bug_global) / seconds_in_week_global) * 2 - 0.5) / 2
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
                
            path_to_save_file = file.replace(r'\XML', r'\XML\new_files')
            path_to_folder = os.path.dirname(path_to_save_file)
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


def create_localisation_dict(key_set):
    data_dict = {}
    for key in key_set:
        # Extract the numeric part from the key
        numeric_part = key.split('_')[-1]
        # Form the corresponding value
        value = f"BUILD TIME IN WEEKS: {numeric_part}"
        # Add the key-value pair to the dictionary
        data_dict[key] = value
    return data_dict

def create_localisation_xml(data_dict):
    # Define namespaces
    nsmap = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsd': "http://www.w3.org/2001/XMLSchema"
    }
    
    # Create the root element with namespaces
    root = ET.Element('LocalisationData', nsmap=nsmap)
    
    # Generate the localisation entries from the dictionary
    for key, value in data_dict.items():
        localisation = ET.SubElement(root, 'Localisation', Key=key)
        translation_data = ET.SubElement(localisation, 'TranslationData')
        translation = ET.SubElement(translation_data, 'Translation', Language='ENGLISH')
        
        # Add CDATA section
        translation.text = ET.CDATA(value)

    # Create the XML tree
    tree = ET.ElementTree(root)
    
    # Write the XML tree to a file
    xml_file = 'BLACKBURN_BUILD_TIME.xml'
    tree.write(xml_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
    
    print(f"XML file '{xml_file}' created.")


if __name__ == "__main__":
    main()



#надо научить прогу пропускать изменения файлов есть там уже есть блекберн викс
#или не надо. ибо я просто срезаю блекберн если он есть в add_btw_to_encyclopedia
#идея для следующей проги: major hero для юнитов

