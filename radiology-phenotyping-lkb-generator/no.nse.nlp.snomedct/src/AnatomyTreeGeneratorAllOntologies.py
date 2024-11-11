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
CONCEPT_OWL_LINKAGE_TREE_FILE= os.getenv('CONCEPT_OWL_LINKAGE_TREE_FILE')
ALLMAPPINGS_FILE = os.getenv('ALLMAPPINGS_FILE')
PREFIXES_KB = os.getenv('PREFIXES_KB')

    

def print_result_dic_as_csv(dic_results, file_id):
    print("The type read is: ", type(dic_results))
    umls2sct_csv = os.path.join(file_id)
    with open(umls2sct_csv, 'w') as f:
        f.write("CUI;SNOMED-CT_URIS;SNOMED-CT_CODES;FMA_URIS;FMA_CODES")
        for key in dic_results.keys():
            cui_mappings_ls = get_codes_from_url_list(key, dic_results[key])
            f.write("%s; %s; %s; %s; %s; \n" % (key, cui_mappings_ls.snomed_urls, cui_mappings_ls.snomed_codes, cui_mappings_ls.atc_urls, cui_mappings_ls.atc_codes))
        f.close()

def icd_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("icd10") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICD10AM/", "")
                string_rdf = "icd10:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICD10AM/", "").replace(" ","")
        string_rdf = "icd10:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf.replace("/","_")+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")   
        
#https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ATC/   
def atc_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("atc") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ATC/", "")
                string_rdf = "atc:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ATC/", "").replace(" ","")
        string_rdf = "atc:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")     

def lnc_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("lnc") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/LNC/", "")
                string_rdf = "lnc:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/LNC/", "").replace(" ","")
        string_rdf = "lnc:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")   

# ['https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICPC2P/A57002']        
def icpc2_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("ICPC2") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICPC2P/", "")
                string_rdf = "icpc2:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICPC2P/", "").replace(" ","")
        string_rdf = "icpc2:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")     
     
def hpo_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("hpo") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/HPO/", "")
                string_rdf = codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/HPO/", "").replace(" ","")
        string_rdf = codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")       
           
def msh_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("MSH") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/MSHSPA/", "")
                string_rdf = "msh:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICPC2P/MSHSPA/", "").replace(" ","")
        string_rdf = "msh:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")
        
def mdr_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("MDR") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/MDRSPA/", "")
                string_rdf = "mdr:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/MDRSPA/", "").replace(" ","")
        string_rdf = "mdr:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")
        
def medlineplus_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("MEDLINEPLUS") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/MEDLINEPLUS_SPA/", "")
                string_rdf = "medlineplus:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/MEDLINEPLUS_SPA/", "").replace(" ","")
        string_rdf = "medlineplus:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")
            
#https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/NCI_PI-RADS/
def ncipirads_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("NCI_PI-RADS") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/NCI_PI-RADS/", "")
                string_rdf = "ncipirads:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/NCI_PI-RADS/", "").replace(" ","")
        string_rdf = "ncipirads:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
    if flagnomap:
        print("WARNING: codes without mapping were found!")


def ncicadsr_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("NCI_caDSR") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/NCI_caDSR/", "")
                string_rdf = "ncicadrs:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/NCI_caDSR/", "").replace(" ","")
        string_rdf = "ncicadrs:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")

#https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/FMA/
def fma_print_rdf(cui_umls, sct_code, file):
    sct_code = sct_code.replace("[","").replace("]","").replace("'","")
    severalmaps = False
    flagnomap = False
    if len(sct_code) <= 1:
        flagnomap=True
        return
    if sct_code.count("NCI_PI-RADS") > 1:
        severalmaps=True
        for str_piece in sct_code.split():
            if str_piece!=",":
                codetoprint = str_piece.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/FMA/", "")
                string_rdf = "fma:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
                print(string_rdf)
                file.write(string_rdf+"\n")
    else:
        codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/FMA/", "").replace(" ","")
        string_rdf = "fma:"+codetoprint+" owl:equivalentClass umls:"+cui_umls+" ."
        print(string_rdf)
        file.write(string_rdf+"\n")
    if flagnomap:
        print("WARNING: codes without mapping were found!")
        
                    
def main():
    print("-------start--------")
    path_to_file = os.path.join(Path.cwd().parent,"data", ALLMAPPINGS_FILE)
    path_to_file_to_write = os.path.join(Path.cwd().parent,"data", CONCEPT_OWL_LINKAGE_TREE_FILE)
    path_to_file_prefixes = os.path.join(Path.cwd().parent,"data", PREFIXES_KB)


    df_cui_sct = pd.read_csv(path_to_file, sep=";", header=0)
    
    prefixes = ""
    with open(path_to_file_prefixes,"r") as f:
        prefixes = f.read()
    
    with open(path_to_file_to_write, 'w') as f_output:
        f_output.write(prefixes+"\n")
        
        for index, row in df_cui_sct.iterrows():
            cui_umls = row["CUI"]
            sct_code = row["SNOMED-CT_URIS"]
            icd_code = row["ICD10_URLS"]
            atc_code = row["ATC_URLS"]
            hpo_code = row["HPO_URLS"]
            lnc_code = row["LNC_URLS"]
            icpd2_code = row["ICPC2_URLS"]
            mshspa_code = row["MSHSPA URIS"]
            mdrspa_code = row["MDRSPA URIS"]
            medlineplus_code = row["MEDLINEPLUS_SPA_URI"]
            ncipirads_code = row["NCI_PI-RADS_URI"]
            ncicadsr_code = row["NCI_caDSR_URI"]
            fma_code = row["FMA_URI"]
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
                        f_output.write(string_rdf.replace("’", "")+"\n")
            else:
                codetoprint = sct_code.replace(",","").replace("https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/SNOMEDCT_US/", "").replace(" ","")
                string_rdf = "umls:"+cui_umls+" owl:equivalentClass sct:"+codetoprint+" ."
                print(string_rdf)
                f_output.write(string_rdf.replace("’", "").replace("=", "_")+"\n")#parsingRDF messesup BASE 64 postcoordinations that contain =
            if flagnomap:
                print("WARNING: codes without mapping were found!")
                
            icd_print_rdf(cui_umls, icd_code, f_output)
            hpo_print_rdf(cui_umls, hpo_code, f_output)
            atc_print_rdf(cui_umls, atc_code, f_output)
            lnc_print_rdf(cui_umls, lnc_code, f_output)
            icpc2_print_rdf(cui_umls, icpd2_code, f_output)
            msh_print_rdf(cui_umls, mshspa_code, f_output)
            mdr_print_rdf(cui_umls, mdrspa_code, f_output)
            medlineplus_print_rdf(cui_umls, medlineplus_code, f_output)
            ncipirads_print_rdf(cui_umls, ncipirads_code, f_output)
            ncicadsr_print_rdf(cui_umls, ncicadsr_code, f_output)
            fma_print_rdf(cui_umls, fma_code, f_output)
    # dict_mappings = query_snomed_equivalent(cuis)
    # path_to_map_file = os.path.join(Path.cwd().parent,"data", TREE_CUI_SCT_MAPPINGS)
    # print_result_dic_as_csv(dict_mappings, path_to_map_file)
    f_output.close()
    print("end of execution-> put stdout in a fila and add prefixes to upload to the triple store") 
    
    # dict_mappings = query_snomed_equivalent(cuis)
    # path_to_map_file = os.path.join(Path.cwd().parent,"data", TREE_CUI_SCT_MAPPINGS)
    # print_result_dic_as_csv(dict_mappings, path_to_map_file)
    print("end of execution") 
    
if __name__ == '__main__':
    main()
    