import xml.etree.ElementTree as ET
import os
import math

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
    'SPECIALSTRUCTURES_Shared.XML',
    'SpecialStructures_Shipyards.xml',
    'SpecialStructures_Space.xml',
    'SpecialStructures_SpaceTechs.xml',
    'SpecialStructures_Underworld.xml',
    'TECHBUILDING.XML',
    'TEMPLATES_GROUND.XML',
    'TEMPLATES_SPACE.XML',
    'STARBASES.XML',
    'STARBASES_SHARED.XML',
]




aotr_path = os.getcwd()
#надо вернуть снять комент как будет готово
# if os.path.basename(aotr_path) != "1397421866":
#     raise FileNotFoundError(r"you need to place the file in Aotr directory: Steam\steamapps\workshop\content\32470\1397421866\")

xml_folder = os.path.join(aotr_path, r"Data\XML")
for xml in files:
    xml_file = os.path.join(xml_folder, xml)
    
    # Print the constructed file path for debugging
    print(f"Processing file: {xml_file}")
    
    # Check if file exists
    if not os.path.isfile(xml_file):
        print(f"File not found: {xml_file}")
        continue
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for child in root:
            name_attrib = child.attrib.get('Name', "")
            if '_Dummy' not in name_attrib and '_Death_Clone' not in name_attrib:
                for element in child.iter('Build_Time_Seconds'):
                    seconds = float(element.text)
                    # Calculate the number of weeks, adjusting and applying the ceiling to half-week precision
                    rounded_weeks = math.ceil((seconds / 45) * 2 - 0.5) / 2
                    if rounded_weeks % 1 == 0:
                        rounded_weeks = str(int(rounded_weeks))
                    else:
                        rounded_weeks = str(rounded_weeks)

                    enc_element = child.find('Encyclopedia_Text')
                    if enc_element is not None and enc_element.text:
                        # Split the text into lines
                        lines = enc_element.text.splitlines()
                        lines.pop()
                        # Check if the last line contains BLACKBURN_BUILD_TIME_WEEKS and remove it if it does
                        if lines and 'BLACKBURN_BUILD_TIME_WEEKS' in lines[-1]:
                            lines.pop()
                        # Join the filtered lines back into a single string
                        lines.append(f"\t\t\tBLACKBURN_BUILD_TIME_WEEKS_{rounded_weeks}\n\t\t")
                        enc_element.text = "\n".join(lines)


        
        tree.write(xml_file)
    except ET.ParseError as e:
        print(f"Error parsing file {xml_file}: {e}")
    except Exception as e:
        print(f"Error processing file {xml_file}: {e}")

