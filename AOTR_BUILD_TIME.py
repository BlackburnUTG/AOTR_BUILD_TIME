from lxml import etree as ET
import os
import math
import time
import re

btiw_set_global = set()

def main():
    files = [
    'GroundCompaniesEmpire.xml',
    'GroundCompaniesRebel.xml',
    'GroundcompaniesUnderworld.xml',
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
    'SQUADRONS.XML',
    'SpaceunitsFreighters.xml',
    'Specialstructures_Empire.xml',
    'SpecialStructures_GroundTechs.xml',
    'SpecialStructures_PlanetaryDefense.xml',
    'Specialstructures_Rebel.xml',
    'SpecialStructures_Shipyards.xml',
    'SpecialStructures_Space.xml',
    'SpecialStructures_SpaceTechs.xml',
    'SpecialStructures_Underworld.xml',
    'TECHBUILDING.XML',
    'STARBASES.XML',
    'STARBASES_SHARED.XML',
    ]
    start_time = time.time()
    xml_folder = os.path.join(get_aotr_path(), r"Data\XML")
    for file in files:
        xml_file_path = find_file(xml_folder, file)
        if not xml_file_path:
            print(f'File not Found! {xml_file_path}')
            continue
        xml_tree = create_xml(xml_file_path)   
        if not xml_tree:
            continue
        #удалить и вернуть закоменченную
        xml_tree.write(r"D:\_Code\AOTR_BUILD_TIME\Data\XML\new_files\\"+file, pretty_print=True, xml_declaration=True, encoding='utf-8')
        #xml_tree.write(xml_file_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print(f"Successfully changed")
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
    #надо вернуть снять комент как будет готово
    # if os.path.basename(aotr_path) != "1397421866":
    #     raise FileNotFoundError(r"you need to place the file in Aotr directory: Steam\steamapps\workshop\content\32470\1397421866\")
    return aotr_path


def find_file(xml_folder, file):
    file_path = os.path.join(xml_folder, file)
    
    # Print the constructed file path for debugging
    print(f"Processing file: {file_path}")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error! File not found: {file_path}")
        return False 
    return file_path
       

#ошибка! когда делается луп фор чайлд не должно быть ретурн фолс
#т.к. я делаю трай экцепт, может не стоит делать if not rounded_weeks: и другие
def create_xml(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for child in root:
            name_attrib = child.attrib.get('Name', "")
            if '_Dummy' not in name_attrib and '_Death_Clone' not in name_attrib:
                build_time_element = child.find('Build_Time_Seconds')
                rounded_weeks = get_rounded_weeks(build_time_element)
                if not rounded_weeks:
                    continue
                encyclopedia_element = child.find('Encyclopedia_Text')
                #этот иф проверяет есть ли вообще энциклопедия. может тогда добавить внизу элсе: принт у юнита нет энциклопедии? на всякий
                if encyclopedia_element is not None and encyclopedia_element.text:
                    lines = add_lines(encyclopedia_element.text, rounded_weeks)
                    if not lines:
                        btiw(root) 
                        return False
                    encyclopedia_element.text = "\n".join(lines)
                    btiw_set_global.add(re.sub(r'\s+', '', lines[-1]))
        return tree
    except ET.ParseError as e:
        print(f"Error parsing file {xml_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing file {xml_file_path}: {e}")
        return False
    



def get_rounded_weeks(element):
    try:
        seconds = float(element.text)
    except ValueError: 
        print("ERROR! Build_Time_Seconds is not a number")
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
        print("SKIP - File is already changed")
        return False
    
    count_tab = lines[-1].count('\t')
    count_space = lines[-1].count(' ')
    while count_space > 0:
        count_tab += 1
        count_space -= 4

    # Join the filtered lines back into a single string
    lines.append("\t" * count_tab + f"BLACKBURN_BUILD_TIME_WEEKS_{rounded_weeks}\n" + "\t" * (count_tab - 1))
    return lines


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
        value = f"Build time in weeks: {numeric_part}"
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

