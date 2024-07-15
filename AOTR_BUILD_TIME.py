from lxml import etree as ET
import os
import math

def get_aotr_path():
    aotr_path = os.getcwd()
    #надо вернуть снять комент как будет готово
    # if os.path.basename(aotr_path) != "1397421866":
    #     raise FileNotFoundError(r"you need to place the file in Aotr directory: Steam\steamapps\workshop\content\32470\1397421866\")
    return aotr_path

def get_xml(xml_folder, file):
    file_path = os.path.join(xml_folder, file)
    
    # Print the constructed file path for debugging
    print(f"Processing file: {file_path}")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error! File not found: {file_path}")
        return False 
    return file_path
       

def add_lines(encyclopedia_element, rounded_weeks):
        # Split the text into lines - ну какая-то ерись с тем что у меня может быть пустая строка в
    lines = encyclopedia_element.text.splitlines()
    if lines[-1].isspace():
        lines.pop()
    # Check if the last line contains BLACKBURN_BUILD_TIME_WEEKS and remove it if it does
    if "BLACKBURN_BUILD_TIME_WEEKS" in lines[-1]:
        print("File is already changed. Skip")
        return False
    # Join the filtered lines back into a single string
    lines.append(f"\t\t\tBLACKBURN_BUILD_TIME_WEEKS_{rounded_weeks}\n\t\t")
    return lines


#ошибка! когда делается луп фор чайлд не должно быть ретурн фолс
#т.к. я делаю трай экцепт, может не стоит делать if not rounded_weeks: и другие
def write_weeks(xml_file_path):        
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
                    lines = add_lines(encyclopedia_element, rounded_weeks)
                    if not lines:
                        return False
                    encyclopedia_element.text = "\n".join(lines)

        tree.write(xml_file_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    except ET.ParseError as e:
        print(f"Error parsing file {xml_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing file {xml_file_path}: {e}")
        return False
    return True



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


    
    xml_folder = os.path.join(get_aotr_path(), r"Data\XML")
    for file in files:
        xml_file_path = get_xml(xml_folder, file)
        if not xml_file_path:
            continue 
        if not write_weeks(xml_file_path):
            continue
        print(f"file is sucessfuly changed")



    print("Done")
    print("Press ENTER to continue")
    input()
    

if __name__ == "__main__":
    main()
#можно использовать фичи из modify_xml.py сделано в чатгпт - оно пишет лог
#SpecialStructures_Space.xml не работает должным образом потому что там два билд тайм секондс (уже убрал из списка)
#мне кажется надо сделать чтобы для _Dummy тоже писался блекберн викс. Ибо это же юниты-станций на карте галактики 
#можно все же сделать бекап перед строчкой где я записываю изменения. - просто копи пейст исходного файла
#можно сделать чтобы в мастер лангуаге файл записывалисть только те кий-валью, который по факту я записываю в хмльки... но есть загвоздка - тогда при следующих установках не будут учитывать не измененные данные которые в файлах которые не были изменены патчем
#