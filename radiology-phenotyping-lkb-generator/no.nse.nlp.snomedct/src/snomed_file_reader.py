'''
Created on Feb 24, 2022

@author: luis
'''
import pandas as pd
import math
from pathlib import Path
import os
from dotenv import load_dotenv
#from css_parser.settings import set


dotenv_path = os.path.join(Path.cwd().parent,"config", ".env")
load_dotenv(dotenv_path=dotenv_path)
STATIC_PART_SNOMED_LITE_FILE = os.getenv('STATIC_PART_SNOMED_LITE_FILE')
DESCRIPTIONS_PART_SNOMED_LITE_FILE = os.getenv('DESCRIPTIONS_PART_SNOMED_LITE_FILE')
RELATIONSHIPS_PART_SNOMED_LITE_FILE = os.getenv('RELATIONSHIPS_PART_SNOMED_LITE_FILE')
CONCEPTS_PART_SNOMED_LITE_FILE = os.getenv('CONCEPTS_PART_SNOMED_LITE_FILE')


def main2():
    to_print = print_description(845114013,    "20031031",    1,    "450829007",    100005,    "es",    900000000000013009,    "concepto de SNOMED RT",    900000000000020002, 123)
    print(to_print)
    
def main():
    print("hello world3!")
    print(STATIC_PART_SNOMED_LITE_FILE)
    path_static_part = os.path.join(Path.cwd().parent,"data", STATIC_PART_SNOMED_LITE_FILE)
    path_static_part_file = open(path_static_part,"r")
    path_concepts = os.path.join(Path.cwd().parent,"data", DESCRIPTIONS_PART_SNOMED_LITE_FILE)
    df_snomed_descriptions = pd.read_csv(path_concepts, sep='\t',  encoding = 'latin', quoting=3)#lineterminator='\r',
    
    path_relationahips = os.path.join(Path.cwd().parent,"data", RELATIONSHIPS_PART_SNOMED_LITE_FILE)
    df_snomed_rels = pd.read_csv(path_relationahips, sep='\t',  encoding = 'latin', quoting=3)
    df_snomed_rels_clean = df_snomed_rels.drop(df_snomed_rels[df_snomed_rels["typeId"] != 116680003].index)
    path_snomed_onto = os.path.join(Path.cwd().parent,"data", "snomed_lite_onto.ttl")
    
    path_concepts = os.path.join(Path.cwd().parent,"data", CONCEPTS_PART_SNOMED_LITE_FILE)
    df_snomed_concepts = pd.read_csv(path_concepts, sep='\t',  encoding = 'latin', quoting=3)
    
    #file to write the snomed-lite version
    path_snomed_onto = os.path.join(Path.cwd().parent,"data", "snomed_lite_onto_10092022.ttl")
    snomed_lite_onto_file = open(path_snomed_onto, "w")
    
    #build the ontology static part
    def_build_static_part(path_static_part_file, snomed_lite_onto_file)
    print("static part printed")
    
    #Print concepts
    for index, row in df_snomed_concepts.iterrows():
        print_concept(row["id"], row["effectiveTime"], row["active"], row["moduleId"], row["definitionStatusId"], snomed_lite_onto_file)
    print("concepts part printed")
    
    #Pring relationships
    for index, row in df_snomed_rels_clean.iterrows():
        print_relationship(row["typeId"], row["sourceId"], row["destinationId"], snomed_lite_onto_file)
    print("rels part printed")
    
    #Print descriptions
    for index, row in df_snomed_descriptions.iterrows():
        print_description(row["id"], row["effectiveTime"], row["active"], row["moduleId"], row["conceptId"], row["languageCode"], row["typeId"], row["term"], row["caseSignificanceId"], snomed_lite_onto_file)
    print("desc part printed")

    
    path_static_part_file.close()
    snomed_lite_onto_file.close()


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
    


def print_concept(concept_id, effective_time, active, module_id, definition_status, file_to_write):
    is_active = "false"
    if active ==1:
        is_active = "true"
    if math.isnan(definition_status):
        definition_status = "NotSpecified"

        
        
    triplet_str = ("sct:"+str(concept_id)+ 
                   " a sct:Concept ;\n" + 
                   " \t sct:hasEffectiveTime " + "\""+str(effective_time)+"\"^^xsd:string ;"+ " \n"+ 
                   " \t sct:isActive " + "\""+is_active+"\"^^xsd:boolean ; \n"+ 
                   " \t sct:hasModuleId " + "\""+ str(module_id)+"\"^^xsd:string ;"+ " \n"+
                   " \t sct:hasDefinitionStatus " +  "\"" +str(definition_status)+"\"^^xsd:string"+" ." " \n"
                   )
    file_to_write.write(triplet_str)


def def_build_static_part(file_with_static_part, file_to_write):
    static_part = file_with_static_part.read()
    file_to_write.write(static_part)

def print_concept_definition( source_id, file_to_write):#for is-a source_id=child concept and destination_id=parent concept
    relationship_to_string = "<http://www.ehealthresearch.no/2022/snomedct-lite#"+str(source_id)+"> a sct:Description ;\n" + "    rdfs:isDefinedBy <http://www.ehealthresearch.no/2022/snomedct-lite#> ;\n"+ "    rdfs:label"+" \""+"To-DO"+"\"@en ;\n"+ "    ns0:term_status \"stable\" ."+"\n"
    #print(relationship_to_string)
    file_to_write.write(relationship_to_string)
    
def print_relationship(relationship_type, source_id, destination_id, file_to_write):#for is-a source_id=child concept and destination_id=parent concept
    if not relationship_type == 116680003:
        raise AssertionError("Only is-a relationships (i.e. with type id equals to 116680003) are supported")
    
    relationship_to_string = "<http://www.ehealthresearch.no/2022/snomedct-lite#"+str(source_id)+">    rdfs:subClassOf <http://www.ehealthresearch.no/2022/snomedct-lite#"+ str(destination_id)+ "> ."+"\n"
    #print(relationship_to_string)
    file_to_write.write(relationship_to_string)
    
if __name__ == '__main__':
    main()        
    
