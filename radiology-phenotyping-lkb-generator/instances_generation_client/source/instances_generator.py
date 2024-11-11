'''
Created on 25 ene 2023

@author: luis
'''
# import requests module
import requests
from requests.auth import HTTPBasicAuth
import os
from pathlib import Path
import codecs
import json

url_ehrbase = 'http://localhost:8080/ehrbase/rest/ecis/v1'
url_ehr_scape = 'https://rest.ehrscape.com/rest/v1'
url_ehrbase_new_ehr = 'http://localhost:8080/ehrbase/rest/openehr/v1/ehr'
url_ehr_scape_new_ehr =  'https://rest.ehrscape.com/rest/openehr/v1/ehr'
url_ehr_base_new_template = 'http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/?'
url_ehr_scape_upload_template = "https://rest.ehrscape.com/rest/v1/template/"
url_get_existing_compo_ehrbase = url_ehrbase+"/composition/"
#url_get_existing_compo_scape = "https://rest.ehrscape.com/rest/openehr/v1/ehr/"+ehr_id+"/composition/"+compositionUid

url_get_existing_compo = url_get_existing_compo_ehrbase
url_to_new_ehr =url_ehrbase_new_ehr
base_url_openehr_repo = url_ehrbase
url_new_template = url_ehr_base_new_template

class EhrCreationError(Exception):
    pass
class TemplateCreationError(Exception):
    pass
class ExampleCompositionCreationError(Exception):
    pass
class CompositionStorageError(Exception):
    pass

def generateSampleInstanceAndReturnUID(template_id, ehrId):
    # Making a get request to generate a sample instance
    #url_ehr_base = 'localhost:8080/ehrbase/rest/ecis/v1/template/'+template_id+'/example?format=FLAT'
    #url_ehr_scape = base_url_openehr_repo
    url_to_generate_compo = base_url_openehr_repo+'/template/'+template_id+'/example?format=FLAT'

    #url_ehrbase = 'localhost:8080/ehrbase/rest/ecis/v1/template/Corona_Anamnese/example?format=FLAT'
    
    try:
        response = requests.get(url_to_generate_compo,
                    auth = HTTPBasicAuth('luismarcoruiz', 'luis2ruiz'))
    except Exception as e:
        print(e)
        raise ExampleCompositionCreationError(f'An error occurred when creating example instance from template {template_id} and EHR id {ehrId}')

          
    # print request object
    dataToPost = response.json()
    
    return dataToPost

def preprocess_for_ehrbase(data_to_post):
    del data_to_post["valkyrie_depresion_assessment/setting|code"]
    del data_to_post["valkyrie_depresion_assessment/_health_care_facility|name"]
    del data_to_post["valkyrie_depresion_assessment/_end_time"]
    del data_to_post["valkyrie_depresion_assessment/setting|terminology"]
    del data_to_post["valkyrie_depresion_assessment/start_time"]
    del data_to_post["valkyrie_depresion_assessment/setting|value"]

    data_to_post["valkyrie_depresion_assessment/category|terminology"]="openehr"
    data_to_post["valkyrie_depresion_assessment/category|value"]="event"
    data_to_post["valkyrie_depresion_assessment/category|code"]="433"

    # data_to_post["valkyrie_depresion_assessment/language|code"]="en"
    # data_to_post["valkyrie_depresion_assessment/language|terminology"] = "ISO_639-1"
    # data_to_post["valkyrie_depresion_assessment/language|code"]="en"
    return data_to_post

def save_instance_in_flat_format(data_to_post, ehr_id, template_id):
    #preprocess data to avoid validation errors in ehrbase
    data_to_post = preprocess_for_ehrbase(data_to_post)
    #now store in flat format, get its uid and  retrieve in XML
    paramss = {'templateId' : template_id, 'ehrId':ehr_id, 'format':'FLAT'}
    payload = json.dumps(data_to_post)
    print("data to post is:", payload)
   # try:
    #url_to_post_compo="http://localhost:8080/ehrbase/rest/ecis/v1/composition/?format=FLAT&ehrId=2755733a-fdf3-4a33-8449-9bbeea6836ae&templateId=Valkyrie_depresion_assessment"
    url_to_post_compo = base_url_openehr_repo+'/composition/'#+'?format=FLAT'&ehrId=4204576d-c8fb-4227-8182-aea926a1f9c3&templateId=Valkyrie_depresion_assessment'
    print("The problematic EHR id is: ", ehr_id)
    response = requests.post(url=url_to_post_compo, json=payload, 
    auth = HTTPBasicAuth('luismarcoruiz', 'luis2ruiz'), headers={'Content-Type': 'application/json','Accept': 'application/json'}, params=paramss)
   # except Exception as e:
    #    print(e)
     #   raise CompositionStorageError(f'An error occurred when creating example instance from template {template_id} and EHR id {ehr_id}')
    
    print(response.json)
    print(response.content)
    request_get_compo = response.json()
    compositionUid = request_get_compo["compositionUid"]
    return compositionUid

def get_composition_in_non_flat_format(ehr_id, compositionUid):
      #get the composition in JSON (not FLAT) or XML
      #http://localhost:8080/ehrbase/rest/ecis/v1/composition/901e7910-4805-4e29-8d66-ca505424c550::local.ehrbase.org::1?format=JSON
    #url_get_existing_compo = "https://rest.ehrscape.com/rest/openehr/v1/ehr/"+ehr_id+"/composition/"+compositionUid
    url_get_existing_compo = url_get_existing_compo+compositionUid+'?format=JSON'
    full_compo_json = requests.get(url_get_existing_compo,
                auth = HTTPBasicAuth('luismarcoruiz', 'luis2ruiz'))
    return Composition_instance_wrapper(compositionUid, full_compo_json.json())
  

class Composition_instance_wrapper:
    def __init__(self, openehr_uid, composition_body):
        self.openehr_uid = openehr_uid
        self.composition_body = composition_body
    
def upload_template(template_name: str):
    #f = open(template_file_name, "r")
    #print(f.read())
    #invocar la creacion de la template en el openehr repo
    try:
        
        url_upload_template = url_new_template
        paramss = {'templateId' : template_name}
        response = ""
        template_file_name = "../resources/"+template_name+".opt"
        with open("snomed-lite_repo/instances_generation_client/resources/"+template_name+".opt", "r") as f:
            payload = f.read()
        #with open(template_file_name, "r") as payload:
            response = requests.post(url=url_upload_template, data=payload.encode('utf-8'), 
                   auth = HTTPBasicAuth('luismarcoruiz', 'luis2ruiz'), headers={'Content-Type': 'application/xml','Accept': 'application/xml'}, params=paramss)
             #print(payload.encode())
    except Exception as e:
        print(e)
        raise TemplateCreationError(f'An error occurred when creating the template with id {template_name}')

        
    return response

def create_new_ehr():
    try:
        response = requests.post(url_to_new_ehr,
                    auth = HTTPBasicAuth('luismarcoruiz', 'luis2ruiz'), headers={'Content-Type': 'application/json','Accept': 'application/json'})
    except Exception as e:
        print(e)
        raise EhrCreationError(f'An error occurred when creating the new EHR: '+e)

    return response

def generate_instances_for_template(template_id, number_of_instances):
    """Generated the specified number of instances for the provided template for a single newly created EHR"""
    
    dict_new_compos = {}
    for x in range(0, number_of_instances):
        
        #Upload template
        template_name = template_id+".opt"
        response = upload_template(template_id)
        
        #create EHR
        ehr_creation_response = create_new_ehr()
        headers_res = ehr_creation_response.headers
        print("type: ", headers_res["Etag"])

        print("the ehr response is: ", ehr_creation_response.text)
        new_ehrId =""
        if "ehrbase" in url_to_new_ehr:
            new_ehrId = headers_res["Etag"]
        else:
            new_ehrId = str(ehr_creation_response.headers['openEHR-uri']).replace("ehr:/","")
        new_ehrId=new_ehrId.replace('"', '')
        #create instances
        new_instance = generateSampleInstanceAndReturnUID(template_id, new_ehrId)
        
        #save instance in flat format to get it in hierarchical JSON or XML
        compositionId = save_instance_in_flat_format(new_instance, new_ehrId, template_id)
        non_flat_compo = get_composition_in_non_flat_format(new_ehrId, compositionId)
        dict_new_compos[non_flat_compo.openehr_uid]=non_flat_compo
        
        try:
            file_name=template_id + non_flat_compo.openehr_uid+".json"
            file_with_instance =  open(file_name, "w")
            file_with_instance.write(json.dumps(non_flat_compo.composition_body))
        except Exception as e:
            print(e)
            raise EhrCreationError(f'An error occurred when writing new generated composition to a file:'+file_name)
    
    return dict_new_compos

        
def main():
    print("==========Start of execution============!")
    print("Current directory is: ",os.getcwd())
    ehrId = '6ef67515-99d6-4d3b-b7d1-84138a52032b'
    template_sample_patient =  "sample_patient"
    templateId_valkyrie_assessment = "Valkyrie_depresion_assessment"

    dic_composition_wrapper = generate_instances_for_template(templateId_valkyrie_assessment, 5) #generateSampleInstanceAndReturnUID(template_sample_patient, ehrId)
    print("The compositions created are: ", dic_composition_wrapper.keys())
    print("==========End of  execution 1============!")


    

if __name__ == "__main__":
    main()
    
    
