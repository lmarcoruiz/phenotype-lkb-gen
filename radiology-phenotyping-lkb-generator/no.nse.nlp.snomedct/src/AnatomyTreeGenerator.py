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
import pandas as pd

dotenv_path = os.path.join(Path.cwd().parent,"config", ".env")
load_dotenv(dotenv_path=dotenv_path)
STATIC_PART_SNOMED_LITE_FILE = os.getenv('STATIC_PART_SNOMED_LITE_FILE')
DESCRIPTIONS_PART_SNOMED_LITE_FILE = os.getenv('DESCRIPTIONS_PART_SNOMED_LITE_FILE')
RELATIONSHIPS_PART_SNOMED_LITE_FILE = os.getenv('RELATIONSHIPS_PART_SNOMED_LITE_FILE')
CONCEPTS_PART_SNOMED_LITE_FILE = os.getenv('CONCEPTS_PART_SNOMED_LITE_FILE')
CONCEPT_TREE_FILE = os.getenv('CONCEPT_TREE_FILE')
TREE_CUI_SCT_MAPPINGS = os.getenv('TREE_CUI_SCT_MAPPINGS')
TREE_HIERARCHY_ANATOMY_ONLY = os.getenv('TREE_HIERARCHY_ANATOMY_ONLY')


    

def print_result_dic_as_csv(dic_results, file_id):
    print("The type read is: ", type(dic_results))
    umls2sct_csv = os.path.join(file_id)
    with open(umls2sct_csv, 'w') as f:
        f.write("CUI;SNOMED-CT_URIS;SNOMED-CT_CODES;FMA_URIS;FMA_CODES")
        for key in dic_results.keys():
            cui_mappings_ls = get_codes_from_url_list(key, dic_results[key])
            f.write("%s; %s; %s; %s; %s; \n" % (key, cui_mappings_ls.snomed_urls, cui_mappings_ls.snomed_codes, cui_mappings_ls.atc_urls, cui_mappings_ls.atc_codes))
        f.close()
        
def main():
    print("-------start--------")
    path_to_file = os.path.join(Path.cwd().parent,"data", TREE_CUI_SCT_MAPPINGS)
    df_cui_sct = pd.read_csv(path_to_file, sep=";", header=0)
    
    for index, row in df_cui_sct.iterrows():
        cui_umls = row["CUI"]
        sct_code = row["SNOMEDCT_URIS"]
        sct_code = sct_code.replace("[","").replace("]","").replace("'","")
        severalmaps = False
        flagnomap = False
        if len(sct_code) <= 1:
            flagnomap=True
            continue
        if sct_code.count("SNOMED") > 1:
            severalmaps=True
            for str_piece in sct_code.split():
                if str_piece!=",":
                    codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/SNOMEDCT_US/", "")
                    string_rdf = "umls:"+cui_umls+" owl:equivalentClass sct:"+codetoprint+" ."
                    print(string_rdf)
        else:
            codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/SNOMEDCT_US/", "").replace(" ","")
            string_rdf = "umls:"+cui_umls+" owl:equivalentClass sct:"+codetoprint+" ."
            print(string_rdf)
        if flagnomap:
            print("WARNING: codes without mapping were found!")
    
    # dict_mappings = query_snomed_equivalent(cuis)
    # path_to_map_file = os.path.join(Path.cwd().parent,"data", TREE_CUI_SCT_MAPPINGS)
    # print_result_dic_as_csv(dict_mappings, path_to_map_file)
    print("end of execution")       

if __name__ == '__main__':
    main()
    