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

# Ensure the path does not end with a backslash
path = r'C:\Steam\steamapps\workshop\content\32470\1397421866\Data\XML'

for xml in files:
    file_path = os.path.join(path, xml)
    
    # Print the constructed file path for debugging
    print(f"Processing file: {file_path}")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        continue
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            name_attr = child.attrib.get('Name', "")
            if '_Dummy' not in name_attr and '_Death_Clone' not in name_attr:
                for element in child.iter('Build_Time_Seconds'):
                    seconds = int(element.text)
                    rounded_weeks = math.ceil((seconds / 45) * 2 - 0.5) / 2
                    if rounded_weeks % 1 == 0:
                        rounded_weeks = str(int(rounded_weeks))
                    else:
                        rounded_weeks = str(rounded_weeks)
                    for enc_element in child.iter('Encyclopedia_Text'):
                        if enc_element.text:
                            enc_element.text += f"\tBLACKBURN_NUMBER_{rounded_weeks}\n\t\t"
                        else:
                            enc_element.text = f"\t{rounded_weeks}\n\t\t"
                            # make raise error

        tree.write(file_path)
    except ET.ParseError as e:
        print(f"Error parsing file {file_path}: {e}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


