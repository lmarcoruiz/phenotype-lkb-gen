'''
Created on Feb 24, 2022

@author: luis
'''
import re
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
import json
from jsonpath_ng import jsonpath, parse
from umls_2_sct_and_icd_mapper import  Cui_mappings, get_codes_from_url_list

dotenv_path = os.path.join(Path.cwd().parent,"config", ".env")
load_dotenv(dotenv_path=dotenv_path)
STATIC_PART_SNOMED_LITE_FILE = os.getenv('STATIC_PART_SNOMED_LITE_FILE')
DESCRIPTIONS_PART_SNOMED_LITE_FILE = os.getenv('DESCRIPTIONS_PART_SNOMED_LITE_FILE')
RELATIONSHIPS_PART_SNOMED_LITE_FILE = os.getenv('RELATIONSHIPS_PART_SNOMED_LITE_FILE')
CONCEPTS_PART_SNOMED_LITE_FILE = os.getenv('CONCEPTS_PART_SNOMED_LITE_FILE')
CONCEPT_TREE_FILE = os.getenv('CONCEPT_TREE_FILE')
TREE_CUI_SCT_MAPPINGS = os.getenv('TREE_CUI_SCT_MAPPINGS')
TREE_HIERARCHY_ANATOMY_ONLY = os.getenv('TREE_HIERARCHY_ANATOMY_ONLY')
TREE_CUI_SCT_MAPPINGS_ANATOMY = os.getenv('TREE_CUI_SCT_MAPPINGS_ANATOMY')
TREE2_HIERARCHY_ESSENTIAL = os.getenv('TREE2_HIERARCHY_ESSENTIAL')
TREE2_HIERARCHY_ESSENTIAL_TOWRITE = os.getenv('TREE2_HIERARCHY_ESSENTIAL_TOWRITE')
api_url_par1 = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/"
#api_url_par2 = "/atoms?ttys=PT&sabs=SNOMEDCT_US%2CFMA&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"
api_url_par2 = "/atoms?ttys=PT&sabs=SNOMEDCT_US%2CICD10AM%2CHPO%2CATC%2CLNC%2CICPC2P%2CMSHSPA%2CMDRSPA%2CMEDLINEPLUS_SPA%2CNCI_PI-RADS%2CNCI_caDSR%2CFMA&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"

jsonpath_to_code = "$[result][*][code]"


def read_tree_file(path_to_file):
    with open(path_to_file, "r") as f:
        treeFileContent = f.read()
        cuis = re.findall('[C][0-9]{7}',treeFileContent)
        return cuis
    
def query_snomed_equivalent(cui_list):
    dict_sct_mapping = {}
    for cui in cui_list:
        dict_sct_mapping[cui] = get_atom_for_code(cui)
    return dict_sct_mapping

def get_atom_for_code(umls_cui):
    print("/****************************************/")
    print("GET from UMLS server with CUI: ", umls_cui)
    api_url_full = api_url_par1 + str(umls_cui) + api_url_par2
    print("The URL in use is: ", api_url_full)
    response = requests.get(api_url_full)
    print("Request received from UMLS service: ", response.json())
    jsonpath_expression = parse(jsonpath_to_code)
    set_codes_for_cui = set()
    for match in jsonpath_expression.find(response.json()):
        #print(f'Code is: {match.value}')
        set_codes_for_cui.add(match.value)
    return list(set_codes_for_cui)

def print_result_dic_as_csv(dic_results, file_id):
    print("The type read is: ", type(dic_results))
    umls2sct_csv = os.path.join(file_id)
    with open(umls2sct_csv, 'w') as f:
        for key in dic_results.keys():
            cui_mappings_ls = get_codes_from_url_list(key, dic_results[key])
            f.write("%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s\n" % (key, cui_mappings_ls.snomed_urls, cui_mappings_ls.snomed_codes, cui_mappings_ls.icd_urls, cui_mappings_ls.icd_codes, cui_mappings_ls.hpo_urls, cui_mappings_ls.hpo_codes, cui_mappings_ls.atc_urls, cui_mappings_ls.atc_codes, cui_mappings_ls.loinc_urls, cui_mappings_ls.loinc_codes, cui_mappings_ls.icpc2_urls, cui_mappings_ls.icpc2_codes, cui_mappings_ls.mshspa_urls, cui_mappings_ls.mshspa_codes, cui_mappings_ls.mdrspa_urls, cui_mappings_ls.mdrspa_codes, cui_mappings_ls.medlineplusspa_urls, cui_mappings_ls.medlineplusspa_codes, cui_mappings_ls.ncipirads_urls, cui_mappings_ls.ncipirads_codes, cui_mappings_ls.ncidsrca_url, cui_mappings_ls.ncidsrca_codes, cui_mappings_ls.fma_url, cui_mappings_ls.fma_codes))
            #"%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s\n" % (key, cui_mappings_ls.snomed_urls, cui_mappings_ls.snomed_codes, cui_mappings_ls.icd_urls, cui_mappings_ls.icd_codes, cui_mappings_ls.hpo_urls, cui_mappings_ls.hpo_codes, cui_mappings_ls.atc_urls, cui_mappings_ls.atc_codes, cui_mappings_ls.loinc_urls, cui_mappings_ls.loinc_codes, cui_mappings_ls.icpc2_urls, cui_mappings_ls.icpc2_codes, cui_mappings_ls.mshspa_urls, cui_mappings_ls.mshspa_codes, cui_mappings_ls.mdrspa_urls, cui_mappings_ls.mdrspa_codes, cui_mappings_ls.medlineplusspa_urls, cui_mappings_ls.medlineplusspa_codes, cui_mappings_ls.ncipirads_urls, cui_mappings_ls.ncipirads_codes, cui_mappings_ls.ncidsrca_url, cui_mappings_ls.ncidsrca_codes, cui_mappings_ls.fma_url, cui_mappings_ls.fma_codes)
        f.close()
        
def main():
    path_to_file = os.path.join(Path.cwd().parent,"data", TREE2_HIERARCHY_ESSENTIAL)#CONCEPT_TREE_FILE)
    cuis = read_tree_file(path_to_file)
    dict_mappings = query_snomed_equivalent(cuis)
    path_to_map_file = os.path.join(Path.cwd().parent,"data", TREE2_HIERARCHY_ESSENTIAL_TOWRITE)#TREE_CUI_SCT_MAPPINGS)
    print_result_dic_as_csv(dict_mappings, path_to_map_file)
    print("end of execution")       

if __name__ == '__main__':
    main()
    