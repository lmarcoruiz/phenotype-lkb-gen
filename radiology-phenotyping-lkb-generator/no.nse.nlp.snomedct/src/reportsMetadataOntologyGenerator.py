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
import ast

dotenv_path = os.path.join(Path.cwd().parent,"config", ".env")
load_dotenv(dotenv_path=dotenv_path)
REPORT_METADATA_MINI = os.getenv('REPORT_METADATA_MINI')
REPORT_METADATA_FULL = os.getenv('REPORT_METADATA_FULL')

prefixes = """@prefix hr:    <http://iserve.kmi.open.ac.uk/ns/hrests#> .
@prefix msm-swagger: <http://iserve.kmi.open.ac.uk/ns/msm-swagger#> .
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix msm-nfp: <http://iserve.kmi.open.ac.uk/ns/msm-nfp#> .
@prefix wl:    <http://www.wsmo.org/ns/wsmo-lite#> .
@prefix sawsdl: <http://www.w3.org/ns/sawsdl#> .
@prefix http-status-codes: <http://www.w3.org/2011/http-statusCodes#ß> .
@prefix msm:   <http://iserve.kmi.open.ac.uk/ns/msm#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dc: <http://purl.org/dc/elements/1.1> .
@prefix sioc:  <http://rdfs.org/sioc/ns#> .
@prefix schema: <http://schema.org/> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix http-methods: <http://www.w3.org/2011/http-methods#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix msm-wsdl: <http://iserve.kmi.open.ac.uk/ns/msm-wsdl#> .
@prefix cc:    <http://creativecommons.org/ns#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix si: <http://www.w3schools.com/rdf/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix scds: <http://www.telemed.no/shaman/scds#> .
@prefix scds: <http://arch.telemed.no:9001/ontology#> .
@prefix scdsft: <arch.telemed.no:9001/cdsfunctionaltaxonomy#> .
@prefix umls: <https://uts.nlm.nih.gov/uts/umls/concept/> .
@prefix fma:   <http://purl.org/sig/ont/fma/> .
@prefix hp:   <http://purl.obolibrary.org/obo/hp#> .
@prefix sct:   <http://www.ehealthresearch.no/2022/snomedct-lite#> .
@prefix icd10: <http://https://uts-ws.nlm.nih.gov/rest/content/2022AA/source/ICD10AM#> ."""

def main():
    path_concepts = os.path.join(Path.cwd().parent,"data", REPORT_METADATA_FULL)
    df_snomed_descriptions = pd.read_csv(path_concepts, sep=';',  encoding = 'latin', quoting=3)#lineterminator='\r',
    file_ttl = open("reports_chest_covid.ttl", 'w')
    file_ttl.write("%s\n" % prefixes)
    file_ttl.write("%s\n" % "")
    #Print descriptions
    for index, row in df_snomed_descriptions.iterrows():
        #print(row["LineNr"], row["ImageID"], row["ImageDir"], row["StudyDate_DICOM"], row["StudyID"], row["PatientID"], row["PatientBirth"], row["PatientSex_DICOM"], row["ViewPosition_DICOM"], row["Projection"], row["MethodProjection"], row["Pediatric"], row["Modality_DICOM"], row["Manufacturer_DICOM"], row["PhotometricInterpretation_DICOM"], row["PixelRepresentation_DICOM"],row["PixelAspectRatio_DICOM"],row["SpatialResolution_DICOM"],row["BitsStored_DICOM"],row["WindowCenter_DICOM"],row["Rows_DICOM"],row["Columns_DICOM"],row["XRayTubeCurrent_DICOM"],row["Exposure_DICOM"],row["ExposureInuAs_DICOM"],row["ExposureTime"],row["ReportID"],row["Report"],row["MethodLabel"],row["Labels"],row["Localizations"],row["LabelsLocalizationsBySentence"],row["labelCUIS"],row["LocalizationsCUIS"])
        print_report(row["ImageID"], row["StudyID"], row["PatientID"],  row["PatientBirth"], row["PatientSex_DICOM"], row["ReportID"],row["labelCUIS"],row["LocalizationsCUIS"], file_ttl)
    
    file_ttl.close()
    
def print_report(imageId, studyId, patientId,patientBirthDate, patientGender, reportId, labelCuis, localizationCuis, file_ttl):

    labelCuis=ast.literal_eval(labelCuis.replace(' ', ", "))
    list_labelCuis = [n.strip() for n in labelCuis]

    labeLoclCuis=ast.literal_eval(localizationCuis.replace(' ', ", "))
    list_labelLocCuis = labeLoclCuis

    
    triplet_str_patient = ("sct:"+str(patientId)+ 
                   " a schema:Patient ;\n" + 
                   " \t schema:birthDate " + "\""+str(patientBirthDate)+"-01-01T10:00:00"+"\"^^xsd:date ;"+ " \n"+ 
                   " \t schema:gender " + "\""+patientGender+"\"^^xsd:string ; \n"+ 
                   " \t sct:schema:identifier " +  "\"" +str(patientId)+"\"^^xsd:string"+" ." " \n"
                   )

    imageId_clean= str(imageId).replace(".","_")
    triplet_str_image = ("sct:"+str(imageId_clean)+ 
                   " a schema:ImageObject ;\n" + 
                   " \t sct:schema:identifier " +  "\"" +str(imageId_clean)+"\"^^xsd:string"+" ." " \n"
                   )
    
    triplet_str_study = ("sct:"+str(studyId)+ 
                   " a schema:MedicalStudy ;\n" + 
                   " \t sct:schema:identifier " +  "\"" +str(studyId)+"\"^^xsd:string"+" ." " \n"
                   )
    
    
    triplet_str_report = ("sct:"+str(reportId)+ 
                   " a schema:Report ;\n" + 
                   " \t  rdfs:isDefinedBy <http://www.ehealthresearch.no/2022/snomedct-lite#> ;"+ " \n"+
                   " \t  rdfs:label " + "\""+str(reportId)+"\"^^xsd:string ;"+ " \n"+ 
                   " \t  schema:identifier " +  "\"" +str(patientId)+"\"^^xsd:string"+" ;"+ " \n"+
                   " \t  ns0:term_status "+"\""+"stable"+"\""+" ;" +" \n"+
                   " \t  sct:locatedAt " + "sct:service_oncology_research ."+ " \n"
                   )
        
    #file_to_write.write(triplet_str)
    # print(triplet_str_patient)
    # print(triplet_str_image)
    # print(triplet_str_study)
    # print(triplet_str_report)
    
    file_ttl.write("%s\n" % triplet_str_patient)
    file_ttl.write("%s\n" % triplet_str_image)
    file_ttl.write("%s\n" % triplet_str_study)
    file_ttl.write("%s\n" % triplet_str_report)
    
    for refConcept in list_labelCuis:
        refs_triple = "sct:"+str(reportId)+" sct:referencesConcept umls:"+ refConcept + " ."
        #print(refs_triple)
        file_ttl.write("%s\n" % refs_triple)
        
    for refLocationConcept in list_labelLocCuis:
        refs_triple = "sct:"+str(reportId)+" sct:referencesLocationConcept umls:"+ refLocationConcept + " ."
        #print(refs_triple)
        file_ttl.write("%s\n" % refs_triple)
    
if __name__ == '__main__':
    main()        


