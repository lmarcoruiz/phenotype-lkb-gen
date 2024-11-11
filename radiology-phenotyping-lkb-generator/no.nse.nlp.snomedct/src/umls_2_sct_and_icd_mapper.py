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

#file_to_generate = "RADIO_LOC"
#file_to_generate = "CANCER"
file_to_generate = "RADIO"
api_url = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0026896/atoms?ttys=PT&sabs=SNOMEDCT_US%2CICD10AM&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"
api_url_par1 = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/"
api_url_par2 = "/atoms?ttys=PT&sabs=SNOMEDCT_US%2CICD10AM%2CHPO%2CATC%2CLNC%2CICPC2P%2CMSHSPA%2CMDRSPA%2CMEDLINEPLUS_SPA%2CNCI_PI-RADS%2CNCI_caDSR%2CFMA&apiKey=7777b32f-b86d-413a-aeee-102e2f97a5aa"
jsonpath_to_code = "$[result][*][code]"
base_path='/snomed-lite_repo/no.nse.nlp.snomedct/'
path_wd = '/home/luis/development/projects/NLP_DSIC_AVS/NLPDSIC/python_scripts/snomed-lite_repo/no.nse.nlp.snomedct/'#Path.cwd()

#dotenv_path = os.path.join(path_wd,base_path,"config", ".env")
dotenv_path = path_wd+"config/.env"
umls2sct_map_path = path_wd+"data/"+"dictionaryWithSCTCodes.json"#os.path.join(path_wd, base_path, "data", "dictionaryWithSCTCodes.json")
umls2sct_csv = path_wd+"data/"+"mappings_cancer_UMLS_SCT.csv"#os.path.join(path_wd,base_path, "data", "mappings_cancer_UMLS_SCT.csv")

load_dotenv(dotenv_path=dotenv_path)
CONCEPTS_UMLS_CANCER = os.getenv('CONCEPTS_UMLS_CANCER')
CONCEPTS_UMLS_RADIO = os.getenv('CONCEPTS_UMLS_RADIO')
CONCEPTS_UMLS_RADIO_LOC = os.getenv('CONCEPTS_UMLS_RADIO_LOC')

USE_EXTERNAL_UMLS_SERVICE = True

test_codes_subset = {'C0026896', 'C0032285', 'C0030567'}

class Cui_mappings:

    def __init__(self, umls_cui):
        self.umls_cui = umls_cui
        self.snomed_codes = []
        self.icd_codes = []
        self.atc_codes = []
        self.hpo_codes = []
        self.loinc_codes = []
        self.icpc2_codes = []
        self.mshspa_codes = []
        self.mdrspa_codes = []
        self.medlineplusspa_codes = []
        self.ncipirads_codes = []
        self.ncidsrca_codes = []
        self.fma_codes = []

        self.snomed_urls = []
        self.icd_urls = []
        self.atc_urls = []
        self.loinc_urls = []
        self.hpo_urls = []
        self.icpc2_urls = []
        self.mshspa_urls = []
        self.mdrspa_urls = []
        self.medlineplusspa_urls = []
        self.ncipirads_urls = []
        self.ncidsrca_url = []
        self.fma_url = []

    #codes
    def add_snomed(self, sct_code):
        self.snomed_codes.append(sct_code)
        
    def add_icd(self, icd_code):
        self.icd_codes.append(icd_code)
        
    def add_atc(self, atc_code):
        self.atc_codes.append(atc_code)
        
    def add_hpo(self, hpo_code):
        self.hpo_codes.append(hpo_code)
        
    def add_loinc(self, loinc_code):
        self.loinc_codes.append(loinc_code)
        
    def add_icpc2(self, icpc2_code):
        self.icpc2_codes.append(icpc2_code)
        
    def add_mshspa(self, mshspa_code):
        self.mshspa_codes.append(mshspa_code)
        
    def add_mdrspa(self, mdrspa_code):
        self.mdrspa_codes.append(mdrspa_code)
        
    def add_medlineplusspa(self, medlineplusspa_code):
        self.medlineplusspa_codes.append(medlineplusspa_code) 
    
    def add_ncipirads(self, ncipirads_code):
        self.ncipirads_codes.append(ncipirads_code)
    
    def add_ncidsrca(self, ncidsrca_code):
        self.ncidsrca_codes.append(ncidsrca_code)
    
    def add_fma(self, fma_code):
        self.fma_codes.append(fma_code)
           
    #urls     
    def add_snomed_url(self, sct_code):
        self.snomed_urls.append(sct_code)
        
    def add_icd_url(self, icd_code):
        self.icd_urls.append(icd_code)
    
    def add_atc_url(self, atc_code):
        self.atc_urls.append(atc_code)
    
    def add_loinc_url(self, loinc_code):
        self.loinc_urls.append(loinc_code)
        
    def add_hpo_url(self, hpo_code):
        self.hpo_urls.append(hpo_code)
    
    def add_icpc2_url(self, icpc2_code):
        self.icpc2_urls.append(icpc2_code)
    
    def add_mshspa_url(self, mshspa_code):
        self.mshspa_urls.append(mshspa_code)
        
    def add_mdrspa_url(self, mdrspa_code):
        self.mdrspa_urls.append(mdrspa_code)
        
    def add_medlineplus_url(self, medlineplus_code):
        self.medlineplusspa_urls.append(medlineplus_code)
        
    def add_ncipirads_url(self, ncipirads_code):
        self.ncipirads_urls.append(ncipirads_code)
        
    def add_ncidsrca_url(self, ncidsrca_code):
        self.ncidsrca_url.append(ncidsrca_code)
        
    def add_fma_url(self, fma_code):
        self.fma_url.append(fma_code)


def main():
    print("hello world3! current directory is: ", Path.cwd())#Path.cwd().parent
    

    if file_to_generate =="RADIO":
        #Generate list of CUIs from file
        path_umls_radio = path_wd+'data/'+CONCEPTS_UMLS_RADIO#os.path.join(Path.cwd(), base_path,"data", CONCEPTS_UMLS_RADIO)
        generate_mappings(path_umls_radio, CONCEPTS_UMLS_RADIO)
    elif file_to_generate =="CANCER":
        #Generate list of CUIs from file
        path_umls_cancer = path_wd+'data/'+CONCEPTS_UMLS_CANCER#os.path.join(Path.cwd(), base_path,"data", CONCEPTS_UMLS_CANCER)
        generate_mappings(path_umls_cancer, CONCEPTS_UMLS_CANCER)
    elif file_to_generate =="RADIO_LOC":
        #Generate list of CUIs from file
        path_umls_cancer = path_wd+'data/'+CONCEPTS_UMLS_RADIO_LOC#os.path.join(Path.cwd(), base_path,"data", CONCEPTS_UMLS_RADIO_LOC)
        generate_mappings(path_umls_cancer, CONCEPTS_UMLS_RADIO_LOC)
        
    print("The option to generate the mappings is: ",file_to_generate)
    

    
def generate_mappings(path_file_with_cuis, name_of_file):
    #Generate list of CUIs from file
    df_umls_codes = pd.read_csv(path_file_with_cuis, sep=';',  encoding = 'latin', quoting=3)#lineterminator='\r',
    
    umls_codes_to_map = set()
    for index, row in df_umls_codes.iterrows():
        #print("text: "+row["Text"]+"    UMLScode: "+row["UMLS_code"])
        umls_codes_to_map.add(row["UMLS_code"])
    print("The end. The set built is: ", umls_codes_to_map)
   
    
    if USE_EXTERNAL_UMLS_SERVICE:
        dict_codes_for_cui = generate_cui_sct_dictionary(umls_codes_to_map)#(test_codes_subset)#
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
    print_result_dic_as_csv(dict_codes_for_cui, name_of_file)
    
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
    umls2sct_csv = path_wd+'data/'+str("result_"+file_id)#os.path.join(Path.cwd().parent, "data", str("result_"+file_id))
    with open(umls2sct_csv, 'w') as f:
        for key in dic_results.keys():
            cui_mappings_ls = get_codes_from_url_list(key, dic_results[key])
            f.write("%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s\n" % (key, cui_mappings_ls.snomed_urls, cui_mappings_ls.snomed_codes, cui_mappings_ls.icd_urls, cui_mappings_ls.icd_codes, cui_mappings_ls.hpo_urls, cui_mappings_ls.hpo_codes, cui_mappings_ls.atc_urls, cui_mappings_ls.atc_codes, cui_mappings_ls.loinc_urls, cui_mappings_ls.loinc_codes, cui_mappings_ls.icpc2_urls, cui_mappings_ls.icpc2_codes, cui_mappings_ls.mshspa_urls, cui_mappings_ls.mshspa_codes, cui_mappings_ls.mdrspa_urls, cui_mappings_ls.mdrspa_codes, cui_mappings_ls.medlineplusspa_urls, cui_mappings_ls.medlineplusspa_codes, cui_mappings_ls.ncipirads_urls, cui_mappings_ls.ncipirads_codes, cui_mappings_ls.ncidsrca_url, cui_mappings_ls.ncidsrca_codes, cui_mappings_ls.fma_url, cui_mappings_ls.fma_codes))
            
def get_codes_from_url_list(cui, list_of_urls):
    print("the type is: ", type(list_of_urls), list_of_urls)
    list_of_codes = ""
    new_cui_map = Cui_mappings(cui)
    for url_str in list_of_urls:
        if len(list_of_codes) != 0:
            list_of_codes = list_of_codes + ","
        if "SNOMED" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('SNOMEDCT_US/', 1)[1]
            new_cui_map.add_snomed(url_str.rsplit('SNOMEDCT_US/', 1)[1])
            new_cui_map.add_snomed_url(url_str)
        elif "SCTSPA" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('SCTSPA/', 1)[1]
            new_cui_map.add_snomed(url_str.rsplit('SCTSPA/', 1)[1])
            new_cui_map.add_snomed_url(url_str) 
        elif "ICD" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('ICD10AM/', 1)[1]
            new_cui_map.add_icd(url_str.rsplit('ICD10AM/', 1)[1])
            new_cui_map.add_icd_url(url_str)
        elif "ATC" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('ATC/', 1)[1]
            new_cui_map.add_atc(url_str.rsplit('ATC/', 1)[1])
            new_cui_map.add_atc_url(url_str)
        elif "HPO" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('HPO/', 1)[1]
            new_cui_map.add_hpo(url_str.rsplit('HPO/', 1)[1])
            new_cui_map.add_hpo_url(url_str)
        elif "LNC" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('LNC/', 1)[1]
            new_cui_map.add_loinc(url_str.rsplit('LNC/', 1)[1])
            new_cui_map.add_loinc_url(url_str)
        elif "ICPC2P" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('ICPC2P/', 1)[1]
            new_cui_map.add_icpc2(url_str.rsplit('ICPC2P/', 1)[1])
            new_cui_map.add_icpc2_url(url_str)
        elif "MSHSPA" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('MSHSPA/', 1)[1]
            new_cui_map.add_mshspa(url_str.rsplit('MSHSPA/', 1)[1])
            new_cui_map.add_mshspa_url(url_str)
        elif "MDRSPA" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('MDRSPA/', 1)[1]
            new_cui_map.add_mdrspa(url_str.rsplit('MDRSPA/', 1)[1])
            new_cui_map.add_mdrspa_url(url_str)
        elif "MEDLINEPLUS_SPA" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('MEDLINEPLUS_SPA/', 1)[1]
            new_cui_map.add_medlineplusspa(url_str.rsplit('MEDLINEPLUS_SPA/', 1)[1])
            new_cui_map.add_medlineplus_url(url_str)
        elif "NCI_PI-RADS" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('NCI_PI-RADS/', 1)[1]
            new_cui_map.add_ncipirads(url_str.rsplit('NCI_PI-RADS/', 1)[1])
            new_cui_map.add_ncipirads_url(url_str)
        elif "NCI_caDSR" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('NCI_caDSR/', 1)[1]
            new_cui_map.ncidsrca_codes(url_str.rsplit('NCI_caDSR/', 1)[1])
            new_cui_map.ncidsrca_url(url_str)
        elif "FMA" in url_str:
            list_of_codes = list_of_codes + url_str.rsplit('FMA/', 1)[1]
            new_cui_map.add_fma(url_str.rsplit('FMA/', 1)[1])
            new_cui_map.add_fma_url(url_str)
        else:
            raise NameError('Terminology not supported.')
    return new_cui_map
    
if __name__ == '__main__':
    main()        


