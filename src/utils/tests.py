import xml.etree.ElementTree as ET

test_results = {}

def preblessing_test_report_results(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for suite in root:
        for k, v in suite.items():
            if k in ['tests', 'errors', 'failures']:
                test_results[k] = v
    return test_results