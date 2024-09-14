from lxml import etree as ET
import os
import math
import time
import re
from copy import deepcopy

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

xml_folder_global = None
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
    'EmpireGroundCompanies',
    'FighterUnits',
    'GenericHeroUnits',
    'GenericHeroUnits',
    'GroundInfantry_Units',
    'GroundUnits',
    'GroundVehicles',
    'HeroCompanies',
    'HeroUnits',
    'RebelGroundCompanies',
    'SpaceCorvettes',
    'SpaceUnitsCapital',
    'SpaceUnitsCruisers',
    'SpaceUnitsFreighters',
    'SpaceUnitsFrigates',
    'SpaceUnitsSupers',
    'specialstructures_empire_files',
    'SpecialStructures',
    'specialstructures_rebel_files',
    'SpecialStructures',
    'Squadrons',
    'StarBases',
    'UnderworldGroundCompanies',
]



game_files_global = [
    'GENERICHEROUNITS.XML',
    'GroundCompaniesEmpire.xml',
    'GroundCompaniesRebel.xml',
    'GroundcompaniesUnderworld.xml',
    'GroundCompaniesMinor.xml',
    'GroundVehicles_Empire.xml',
    'GroundVehicles_Rebel.xml',
    'HEROCOMPANIES.XML',
    'Heroes_Land_Empire.xml',
    'Heroes_Land_Rebels.xml',
    'Heroes_Land_Underworld.xml',
    'Heroes_Space_Empire.xml',
    'Heroes_Space_Rebels.xml',
    'Heroes_Space_Underworld.xml',
    'Heroes_Tech_Underworld.xml',
    'SPACEUNITSSUPERS.XML',
    'SPACEUNITSCAPITAL.XML',
    'SPACEUNITSCRUISERS.XML',
    'SPACEUNITSFRIGATES.XML',
    'SPACEUNITSCORVETTES.XML',
    'SPACEUNITSFIGHTERS.XML',
    'SpaceunitsFreighters.xml',
    'Specialstructures_Empire.xml',
    'SpecialStructures_GroundTechs.xml',
    'SpecialStructures_PlanetaryDefense.xml',
    'Specialstructures_Rebel.xml',
    'SpecialStructures_Shipyards.xml',
    'SpecialStructures_Space.xml',
    'SpecialStructures_SpaceTechs.xml',
    'SpecialStructures_Underworld.xml',
    'SQUADRONS.XML',
    'STARBASES.XML',
    'STARBASES_SHARED.XML',
    'TECHBUILDING.XML',
    'TEMPLATES_GROUND.XML',
    'TEMPLATES_SPACE.XML',
    ]
#    'TEMPLATES_GROUND.XML', - надо убрать

# game_files_global = [
#     'Heroes_Land_Empire.xml',
#     'SPACEUNITSCORVETTES.XML',
#     'SPACEUNITSFIGHTERS.XML',
#     'TEMPLATES_SPACE.XML',
#     ]


def main():

    global xml_folder_global
    start_time = time.time()
    xml_folder_global = os.path.join(get_aotr_path(), r"Data\XML")
    for file in game_files_global:
        if file == 'TEMPLATES_SPACE.XML' or file == 'TEMPLATES_GROUND.XML':
            continue
        xml_file_path = find_file(xml_folder_global, file)
        if not xml_file_path:
            print(f'File not Found! {xml_file_path}')
            continue
        xml_tree = create_xml(xml_file_path)   
        if not xml_tree:
            continue
        #удалить и вернуть закоменченную
        xml_tree.write(r"D:\_Code\AOTR_BUILD_TIME\Data\XML\new_files\\"+file, pretty_print=True, xml_declaration=True, encoding='utf-8')
        #xml_tree.write(xml_file_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print(f"{GREEN}Successfully changed{RESET}")

    #for new units in UNITS folder
    dir_with_more_units = os.path.join(xml_folder_global, r'UNITS')
    for root, dirs, files in os.walk(dir_with_more_units):
        for file in files:
            xml_file_path = os.path.join(root, file)
            xml_tree = create_xml(xml_file_path)   
            if not xml_tree:
                continue
            path_to_file = os.path.join(r"D:\_Code\AOTR_BUILD_TIME\Data\XML\new_files", xml_file_path.replace(xml_folder_global, '')[1:])
            path_to_folder = os.path.dirname(path_to_file)
            if not os.path.exists(path_to_folder):
                os.makedirs(path_to_folder)
            xml_tree.write(path_to_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
            print(f"{GREEN}Successfully changed{RESET}")

    print(f"NEW STUFF Successfully changed")                
                # Create the dictionary
    data_dict = create_localisation_dict(btiw_set_global)

    # Create the XML file
    create_localisation_xml(data_dict)

    end_time = time.time()

    execution_time = end_time - start_time
    print(f"The program took {execution_time} seconds to execute.")
    print("\nDone")
    print("Press ENTER to exit")
    #input()


def get_aotr_path():
    aotr_path = os.getcwd()

    # надо вернуть снять комент как будет готово
    # if os.path.basename(aotr_path) != "1397421866":
    #     raise FileNotFoundError(r"you need to place the file in Aotr directory: Steam\steamapps\workshop\content\32470\1397421866\")
    return aotr_path


def find_file(xml_folder, file):
    file_path = os.path.join(xml_folder, file)
    

    
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error! File not found: {file_path}")
        return False 
    return file_path
       

#ошибка! когда делается луп фор чайлд не должно быть ретурн фолс
#т.к. я делаю трай экцепт, может не стоит делать if not rounded_weeks: и другие
def create_xml(xml_file_path):
    # Print the constructed file path for debugging
    print(f"Processing file: {xml_file_path}")
    changes_will_be_made = False
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for child in root:
            if child.tag ==  ET.Comment:
                continue

            name_attrib = child.attrib.get('Name', "")
            if name_attrib == "General_Kalani":
                pass 
            tag = child.tag.lower() 
            if tag not in allowed_tags_global:
                continue
            if tag == 'SpaceUnit':
                pass

            # if child.tag == 'UniqueUnit':
            #     continue
            # if child.tag == 'GenericHeroUnit':
            #     continue     
            name_attrib = child.attrib.get('Name', "")
            if '_Dummy'  in name_attrib or '_Death_Clone' in name_attrib or '_Template' in name_attrib:
                continue
            if name_attrib == 'General_Veers':
                pass   

            elements = get_elements(child)
            if tag == 'UniqueUnit'.lower():
                if elements['category_mask_attrib'] == None:
                    continue
                if 'SpaceHero' not in elements['category_mask_attrib'].text:
                    continue


            # if elements['dummy_attrib'] != None or elements['bts0_attrib'] == True or elements['tech99_attrib'] == True or elements['unique_attrib'] == True :
            #     continue
            # if elements['bts0_attrib'] == True or elements['tech99_attrib'] == True or elements['unique_attrib'] == True :
            #     continue
            #похоже elements['tech99_attrib'] не нужен и тока мешает
            if elements['bts0_attrib'] == True or elements['unique_attrib'] == True :
                continue
            if elements['build_time_element'] != None and elements['encyclopedia_element'] != None:
                set_elements(elements)
                while changes_will_be_made == False:
                    changes_will_be_made = True
                    print('Changes will be made in the file')
                continue
            variansts_list = get_all_variants(root, elements)
            var_el_dic = get_variants_elements_dic(variansts_list)
            if not get_enc_element_from_variant(elements, root, child, var_el_dic, variansts_list):
                continue
            if not get_bts_from_variant(elements, root, variansts_list, child):
                continue
            set_elements(elements)
            while changes_will_be_made == False:
                changes_will_be_made = True
                print('Changes will be made in the file')

        if changes_will_be_made == True:
             return tree
        else: 
            print(f'{YELLOW} Skip - no units to change{RESET}')
            return False
    except ET.ParseError as e:
        print(f"{RED}Error parsing file {xml_file_path}: {e}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Error processing file {xml_file_path}: {e}\n Error with unit: {elements['name_attrib']}{RESET} ")
        return False
    

def get_enc_element_from_variant(elements, root, child, var_el_dic, variansts_list):
    if elements['encyclopedia_element'] != None:
        return True
    for variant in variansts_list:
        enc = variant.find('Encyclopedia_Text')
        if enc != None:
            enc_copy = deepcopy(enc)
            child.append(enc_copy)
            elements["encyclopedia_element"] = enc_copy
            return True
        else: return False

def get_bts_from_variant(elements, root, variansts_list, child):
    if elements['build_time_element'] != None:
        return True
    for variant in variansts_list:
        bts = variant.find('Build_Time_Seconds')
        if bts != None:
            bts_copy = deepcopy(bts)
            child.append(bts_copy)
            elements["build_time_element"] = bts_copy
            return True
        else: return False


def get_variants_elements_dic(variansts_list):
    variants_dic = {}
    for variant in variansts_list:
        name_attrib = variant.attrib.get('Name', "")
        enc_attrib = variant.find('Encyclopedia_Text')
        bts_attrib = variant.find('Build_Time_Seconds')
        var_attrib= variant.find('Variant_Of_Existing_Type')
        variants_dic[name_attrib] = {'enc_attrib': enc_attrib, 'bts_attrib': bts_attrib, 'var_attrib': var_attrib}
    return variants_dic


              





def get_all_variants(root, elements, variants_list=None, next_variant_name=None):
    if variants_list == None:
        variants_list = []
        next_variant_name = elements["variant_of_existing_type"].text
    child_of_variant = get_child_of_variant(root, elements, next_variant_name)
    
    if child_of_variant is None:
        # If no variant is found in the current root, search in all files
        child_of_variant = find_variant_in_all_files(elements, next_variant_name)
        if child_of_variant is None:
            print(f"{RED}Error with unit {elements['name_attrib']} || Variant_of_existing_type: {next_variant_name} is not found{RESET}")
            return variants_list  # No variants found in any file, return the list
    
    # If we found a variant, add it to the list
    variants_list.append(child_of_variant)
    
    # Check for the next variant in the found child
    next_variant_name = child_of_variant.find('Variant_Of_Existing_Type')
    if next_variant_name is not None:
        next_variant_name = next_variant_name.text
        if next_variant_name == 'Company_Spawner_Template':
            pass

        # Continue searching with the current root or across files
        return get_all_variants(root, elements, variants_list, next_variant_name)
    
    return variants_list  # Return the list of variants after processing


#ф-я находит в файле юнит, которого мы ищем по "variant_of_existing_type"    
def get_child_of_variant(root, elements, next_variant_name):
    for child in root:
        name_attrib = child.attrib.get('Name', "")
        if name_attrib == next_variant_name:
            return child  # Return the child if found
    return None  # Return None if no child matches

def find_variant_in_all_files(elements, next_variant_name):
    for file in game_files_global:
        if file == 'TEMPLATES_GROUND.XML':
            pass
        xml_file_path = os.path.join(xml_folder_global, file)
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        child_of_variant = get_child_of_variant(root, elements, next_variant_name)
        if child_of_variant is not None:
            return child_of_variant  # Return the found child
    return None  # Return None if no match in any file






        


def get_child_of_variant_from_all_files(elements):
    for file in game_files_global:
        xml_file_path = os.path.join(xml_folder_global, file)
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        child_variant = get_child_of_variant(root, elements)
        if child_variant != None:
            return child_variant


def get_elements(child):
    build_time_element = child.find('Build_Time_Seconds')
    encyclopedia_element = child.find('Encyclopedia_Text')
    category_mask_element = child.find('CategoryMask')

    name_attrib = child.attrib.get('Name', "")
    dummy_attrib = child.find('Is_Dummy')
    ishero_attrib = child.find('Is_Named_Hero')
    tech99_attrib = child.find('Tech_Level')
    #костыли капец
    if name_attrib == 'U_Beast_Master_AntiVehicle':
        pass
    variant_of_existing_type = child.find('Variant_Of_Existing_Type')
    if name_attrib == 'CommanderFulik_Team':
        variant_of_existing_type = child.find('Variant_of_Existing_Type')
    # if variant_of_existing_type == None:
    #     search_tag = 'Variant_Of_Existing_Type'.lower()
    #     for tag_name in child:
    #         if tag_name.tag.lower() == search_tag:
    #             variant_of_existing_type = tag_name
    #             break
            

    if (variant_of_existing_type == None and build_time_element == None):
        unique_attrib = True
    else:
        unique_attrib = False
    try:
        bts0_attrib = build_time_element.text == '0'
    except AttributeError:
        bts0_attrib = False
    if bts0_attrib == True:
        pass
    try:
        tech99_attrib = tech99_attrib.text == '99'
    except AttributeError:
        tech99_attrib = False
    return {"build_time_element": build_time_element, 
            "encyclopedia_element": encyclopedia_element, 
            "variant_of_existing_type": variant_of_existing_type,
            "name_attrib": name_attrib,
            "dummy_attrib": dummy_attrib,
            "ishero_attrib": ishero_attrib,
            'tech99_attrib': tech99_attrib,
            'bts0_attrib': bts0_attrib,
            'unique_attrib': unique_attrib,
            'category_mask_attrib': category_mask_element,
            }


def get_rounded_weeks(element):
    try:
        seconds = float(element.text)
    except ValueError: 
        print(f"{RED}ERROR! Build_Time_Seconds is not a number{RESET}")
        return False
    except AttributeError:
        return False
    # Calculate the number of weeks, adjusting and applying the ceiling to half-week precision
    rounded_weeks = math.ceil((seconds / 45) * 2 - 0.5) / 2
    if rounded_weeks % 1 == 0:
        rounded_weeks = str(int(rounded_weeks))
    else:
        rounded_weeks = str(rounded_weeks)
    return rounded_weeks



def add_lines(encyclopedia_element_text, rounded_weeks):
        # Split the text into lines
    lines = encyclopedia_element_text.splitlines()
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
    lines.append("\t" * count_tab + f"BLACKBURN_BUILD_TIME_WEEKS_{rounded_weeks}\n" + "\t" * (count_tab - 1))
    return lines






def set_elements(elements):
    try:
        elements["build_time_element"].text
    except AttributeError:
        print(f'{BLUE} unit {elements["name_attrib"]} do not have tag Build_Time_Seconds  {RESET}')
        return

    rounded_weeks = get_rounded_weeks(elements["build_time_element"])
    if not rounded_weeks:
        print(f"{RED}Error in func get_rounded_weeks: unit : {elements['name_attrib']} {RESET}")
    lines = add_lines(elements["encyclopedia_element"].text, rounded_weeks)
    #сработает если в файле уже есть btiw.. Теперь никогда не сработает
    if not lines:
        print(f"{RED}Error! in func add_lines{RESET}")
        #btiw(root) 
        return False
    elements["encyclopedia_element"].text = "\n".join(lines)
    btiw_set_global.add(re.sub(r'\s+', '', lines[-1]))


#-----------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#заносит все найденные btis в глобал сет. Из которого будет делаться отдельны хмл файл
def btiw(root):
    xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
    pattern = r"BLACKBURN_BUILD_TIME_WEEKS_[^\n]+"
    matches = set(re.findall(pattern, xml_string))
    btiw_set_global.update(matches)


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

#можно использовать фичи из modify_xml.py сделано в чатгпт - оно пишет лог
#SpecialStructures_Space.xml - bug in aotr  два билд тайм секондс
#мне кажется надо сделать чтобы для _Dummy тоже писался блекберн викс. Ибо это же юниты-станций на карте галактики 
#можно все же сделать бекап перед строчкой где я записываю изменения. - просто копи пейст исходного файла (хотя зачем если есть воркшоп)
#можно сделать чтобы в мастер лангуаге файл записывалисть только те кий-валью, который по факту я записываю в хмльки... но есть загвоздка - тогда при следующих установках не будут учитывать не измененные данные которые в файлах которые не были изменены патчем
#загвоздку можно решить если: когда файл алреадчи ченджд, просто пройтись по нему и выписать все блекберн_билд_тайм

#create_xml ф-я помимо того что она возвращает будет возвращать еще лист стр BLACKBURN_BUILD_TIME_WEEKS_{rounded_weeks}..
#эта функция будет принимать аргумент lines[-1]. только надо убрать табуляцию и новую строку через РЕ
#result = re.sub(r'\n', '', s)
#3 доп функции как минимум - с пайтестом
#отдельный документ с  перечислением используемых библиотек

#загвоздка в теге энциклопедии и теге времени строительства
#к примеру у стар дестроера3 нет энциклопедии но есть время строительства
#у E_Dreadnaught_Cruiser и E_Preybird_S - есть энциклопедия но нет время строительства
# и у всех у них есть тег  Variant_Of_Existing_Type - т.е. если этого тега нет, значит 100% все будет нормально
#сложность: если у юнита нет инциклопедии - придется копипастой копировать инциклопедию у Variant_Of_Existing_Type а затем
#менять в ней существующий блебен билд тайм(если есть).. потому что значения в секундах могут отличаться

#строка 105 if name_attrib != 'Field_Com_Empire_Team':
#не понимаю почему всё ломается на нем.
#дело было в том что я не правильно вызывал кеи у диктионари

#оказывается у некоторых юник юнитов нету времени строительства - оно берется из шаблона другого файла
#ну и похрен

#можно сделать чтобы в диктионари писалось не только имя исходного юнита. но и имя его шаблона

#нужно добавить что если поиск в Variant_Of_Existing_Type не находит bts или энциклопедию - надо проверить
#если ли у этого чайлда свой Variant_Of_Existing_Type - и искать там.
#далее если такого чайлда нет - тогда искать во всех файлах
#прикол в том что в случае когда я ищу сразу и энциклопедию и bts - в найденном чайлде может быть одно но не быть другого

# я думаю в ф-и которую я только что создал надо сделать чтобы в конце вместо ретурна сета надо сделать из этого диктионари
#кей:имя валью:дик-дик(енциклопедия,bts)

#как же сложно с неймингом. очень много вложенных функций. свой следующий проект попробую зделать в классах
# возможно из списка юнитов надо исключить Field_Com_Empire_Team
# у меня не понятки. А могу ли я спокойно менять то что уже есть в элементс? наппример:
#         найти эту строку: elements['variant_of_existing_type'] = name_of_another_variant
                #когда я делаю этот код ошибка в том, что var_el_dic должен содержать variant с помощью которого
#можно было отследить кто на что ссылается. (Хотя вроде это можно сделать и сейчас, но мне кажется потеряна
#ссылка с основного чайлда на его variant)
                # set_enc_element_from_variant(elements, root, child, var_el_dic)
                # set_bts_from_variant(elements, root)
                # set_elements(elements)

#!!!!!! в set_enc_element_from_variant написана полная ересь - логика не верна, не верные переменные
#всё не правильно

#почему-то в TEMPLATES_GROUND.XML не может найти юнит Company_Spawner_Template

#!! сделать поиск по имени тага GroundCompany и SpaceUnit SpecialStructure - я уже сделал
#! 09.09.2024 - почему-то ошибка с U_Beast_Master_AntiVehicle - ругается на ловер
# SPACEUNITSCRUISERS.XML: 'NoneType' object has no attribute 'splitlines' Error with unit: T_Captor_Carrier
#cделать  на 140 проверку если есть элемент бтс и энк - то можно не искать варианты
#кажется все готово. можно проверять
#почему то некоторые юниты такие как тай дефендер - без изменений. E_TIE_Defender_S
#проблема: для новых юнитов надо глянуть.. мне кажется не нужно перезаписывать файл если там нечего изменять
#мне кажется сейчас идет скип тех файлов где уже есть изменения - это хорошо.. а если скип не из-за этого то это 
#писец как плохо
#для новых файлов надо вписать в принт какой файл обрабатывается в данный момент.. и результат
#новый файлы теперь рабтают нормально..
#
# возможно надо будет включить GenericHeroUnit
#я добавил тег HeroCompany чтобы герои были
# Калани - UniqueUnit, придется добавить тег
#
#вроде у всех всё работает как надо
#надо изменить ф-ю по по поиску всех экзистинг тайп на:
# добавил экзистинг тайп, просмотрел его.. если там нет потерянных тегов - ищешь его экзистинг
#возможно для UniqueUnit надо будет сделать проверку Is_Named_Hero - если No - то тогда ниче не менять (но это не точно)
# или сделать проверку на тег <Encyclopedia_Unit_Class> - чтобы был TEXT_ENCYCLOPEDIA_CLASS_FIELD_COMMANDER
# а ваще самый лучший вариант это забить UniqueUnit для всех файлов кроме того где Калани и компаниия (т.е. оставить тока космос)
#предлагаю сделать это проверкой на наличие тега <Space_Model_Name> - но есть риск если там вариан оф экзистинг тайп место этого
# не вариант
# лучше по тегу <CategoryMask> - там есть space hero (блин, а у <UniqueUnit Name="Fighter_Merc_Commander"> нет такого тега - но есть у варианта)
# а что такое <Is_Generic_Hero>Yes</Is_Generic_Hero> ????
#похоже единственный вариант это сделать проверку на имя файла. и если файл это блексан спейс хероес, тогда разрешить UniqueUnit
#еще вариант - <Population_Value> - если 1 то земной юнит, если больше - космос
#на самом деле можно испольовать маск - он покрывает все места где у меня был написано билд тайм для всех героев бс в списке
#внес изменения. надо проверить работает и. и еще нужно что-то сделать с уникальными юнитами из новых файлов
#во всех файлах есть главный тег к примеру <FighterUnits> или <SpaceUnitsCapital> - может только по нему искать