'''
Created on Feb 24, 2022

@author: luis
'''
import pandas as pd
import math
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
import json
from jsonpath_ng import jsonpath, parse
#from css_parser.settings import set
api_url = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0033572/atoms?ttys=PT&sabs=SNOMEDCT_US%2CICD9CM&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"
api_url_par1 = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/"
api_url_par2 = "/atoms?ttys=PT&sabs=SNOMEDCT_US%2CICD9CM&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"
jsonpath_to_code = "$[result][*][code]"

dotenv_path = os.path.join(Path.cwd().parent,"config", ".env")
umls2sct_map_path = os.path.join(Path.cwd().parent, "data", "dictionaryWithSCTCodes.json")
umls2sct_csv = os.path.join(Path.cwd().parent, "data", "mappings_cancer_UMLS_SCT.csv")

load_dotenv(dotenv_path=dotenv_path)
CONCEPTS_UMLS_CANCER = os.getenv('CONCEPTS_UMLS_CANCER')

USE_EXTERNAL_UMLS_SERVICE = True

test_codes_subset = {'C0175895', 'C0205183', 'C0227960', 'C0227979', 'C0558762'}

def main():
    print("hello world3!")
    print(CONCEPTS_UMLS_CANCER)
    
    #Generate list of CUIs from file
    path_umls_cancer = os.path.join(Path.cwd().parent,"data", CONCEPTS_UMLS_CANCER)
    df_umls_cancer = pd.read_csv(path_umls_cancer, sep=';',  encoding = 'latin', quoting=3)#lineterminator='\r',
    
    umls_codes_to_map = set()
    for index, row in df_umls_cancer.iterrows():
        #print("text: "+row["Text"]+"    UMLScode: "+row["UMLS_code"])
        umls_codes_to_map.add(row["UMLS_code"])
    print("The end. The set built is: ", umls_codes_to_map)
   
    
    #Generate dictioary of atoms linked to one CUI
    # dict_codes_for_cui = {}
    # for umls_cui in umls_codes_to_map:
    #     dict_codes_for_cui[umls_cui] = get_atom_for_code(umls_cui)
    
    if USE_EXTERNAL_UMLS_SERVICE:
        dict_codes_for_cui = generate_cui_sct_dictionary(test_codes_subset)#(umls_codes_to_map)#(test_codes_subset)
        print("type is:  ",type(dict_codes_for_cui))
        json_object = json.dumps(dict_codes_for_cui, indent = 4)
        #save to file to do the process locally without network lag
        with open(umls2sct_map_path, "w") as outfile:
            outfile.write(json_object)
    else:
        #use the local file to avoid network lag
        dict_codes_for_cui = generate_cui_sct_dictionary_locally()
    
    print("The dictionary is: ", dict_codes_for_cui)
    json_object = json.dumps(dict_codes_for_cui, indent = 4) 
    print("In JSON the dictionary is: ", json_object )
    print_result_dic_as_csv(dict_codes_for_cui)
    
    print("script finished execution!")

def generate_cui_sct_dictionary(umls_codes_to_map):
    dict_codes_for_cui = {}
    for umls_cui in umls_codes_to_map:
        dict_codes_for_cui[umls_cui] = get_atom_for_code(umls_cui)
    return dict_codes_for_cui

def generate_cui_sct_dictionary_locally():
    f = open(umls2sct_map_path, "rt")
    dict_umls2sct = json.load(f)
    f.close()
    return dict_umls2sct
        
def print_description(description_id, effective_time, active, module_id, concept_id, language_code, type_id, term, case_sig_id, file_to_write):
    is_active = "false"
    if active ==1:
        is_active = "true"
    if math.isnan(case_sig_id):
        case_sig_id = "NotSpecified"

        
    term = str(term).replace("\"", "")   
    triplet_str = ("sct:"+str(description_id)+ 
                   " a sct:Description ;\n" + 
                   " \t sct:hasEffectiveTime " + "\""+str(effective_time)+"\"^^xsd:string ;"+ " \n"+ 
                   " \t sct:isActive " + "\""+is_active+"\"^^xsd:boolean ; \n"+ 
                   " \t sct:hasModuleId " + "\""+ str(module_id)+"\"^^xsd:string ;"+ " \n"+
                   " \t sct:hasConceptId " +"sct:"+ str(concept_id)+" ;"+ " \n"+
                   " \t sct:hasLanguageCode " + "\"" + str(language_code)+"\"^^xsd:string ;"+ " \n"+
                   " \t sct:hasTypeId " + str(type_id)+" ;"+ " \n"+
                   " \t sct:hasTerm " + "\"" + str(term)+"\"^^xsd:string ;"+ " \n"+
                   " \t sct:hasCaseSignificanceId " +  "\"" +str(case_sig_id)+"\"^^xsd:string"+" ." " \n"
                   )
    file_to_write.write(triplet_str)

def get_atom_for_code(umls_cui):
    print("/****************************************/")
    print("GET from UMLS server with CUI: ", umls_cui)
    api_url_full = api_url_par1 + umls_cui + api_url_par2
    print("The URL in use is: ", api_url_full)
    response = requests.get(api_url_full)
    print("Request received from UMLS service")
    jsonpath_expression = parse(jsonpath_to_code)
    set_codes_for_cui = set()
    for match in jsonpath_expression.find(response.json()):
        #print(f'Code is: {match.value}')
        set_codes_for_cui.add(match.value)
    return list(set_codes_for_cui)

def print_result_dic_as_csv(dic_results):
    print("The type read is: ", type(dic_results))
    with open(umls2sct_csv, 'w') as f:
        for key in dic_results.keys():
            codes_only = get_codes_from_url_list(dic_results[key])
            f.write("%s; %s; %s\n" % (key, dic_results[key], codes_only))
            
def get_codes_from_url_list(list_of_urls):
    print("the type is: ", type(list_of_urls), list_of_urls)
    list_of_codes = ""
    for url_str in list_of_urls:
        if len(list_of_codes) != 0:
            list_of_codes = list_of_codes + ","
        list_of_codes = list_of_codes + url_str.rsplit('SNOMEDCT_US/', 1)[1]
    return list_of_codes
    
if __name__ == '__main__':
    main()        
    
