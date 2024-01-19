from typing import Any
import json, time

from models.app import AppModel
from models.contact import ContactModel
from models.scan import ScanModel
from models.engine import EngineModel
from models.tech import TechModel
from utils.libs.defectdojo.defectdojo import DefectDojo
from utils.enums import ResultFormat

def populate_dojo_scan(defect_dojo: DefectDojo, app: AppModel, tech: TechModel, owner: ContactModel, scan: ScanModel):
    #PRODUCT AND PRODUCT TYPE
    product_id = populate_dojo_product(defect_dojo=defect_dojo, app=app, tech=tech, owner=owner)

    #ENGAGEMENT
    engagement_id = populate_dojo_engagement(defect_dojo=defect_dojo, app=app, scan=scan, product_id=product_id)
    
    return engagement_id

def populate_dojo_group(defect_dojo: DefectDojo, owner: ContactModel):
    #Obtain group from Dojo
    res = defect_dojo.get_first_group_by_name(name=owner.area)
    if res and "id" in res: 
        group_id = res["id"]
    else:
        #Create group on Dojo
        group_id = defect_dojo.create_group(name=owner.area)

        #Try to obtain again the group_id if not created
        if group_id == None:
            res = defect_dojo.get_first_group_by_name(name=owner.area)
            if res and "id" in res: 
                group_id = res["id"]

    return group_id

def populate_dojo_user(defect_dojo: DefectDojo, owner: ContactModel, group_id: int):
    #Obtain user from Dojo
    res = defect_dojo.get_first_user_by_username(username=owner.id)
    if res and "id" in res: 
        user_id = res["id"]
    else:
        #Create user on Dojo
        user_id = defect_dojo.create_user(username=owner.id, name=owner.name, email=owner.email, is_active=False)

        #Try to obtain again the user_id if not created
        if user_id == None:
            res = defect_dojo.get_first_user_by_username(username=owner.id)
            if res and "id" in res: 
                user_id = res["id"]

        #If user and group, assign product_type to group --> Role 4 (Owner)
        if user_id and group_id: defect_dojo.add_user_to_group(user_id=user_id, group_id=group_id, role=4)

        #If not user generated, use default
        if user_id == None:
            res = defect_dojo.get_first_user_by_username(username=defect_dojo.username)
            if res and "id" in res: 
                user_id = res["id"]
            else:
                user_id = None
    return user_id

def populate_dojo_product_type(defect_dojo: DefectDojo, app: AppModel, user_id: int, group_id: int):
    #Obtain product_type from Dojo
    res = defect_dojo.get_first_product_type_by_name(name=app.app_name)
    if res and "id" in res: 
        prod_type_id = res["id"]
    else:
        #Create product_type on Dojo
        prod_type_id = defect_dojo.create_product_type(name=app.app_name)

        #Try to obtain again the prod_type_id if not created
        if prod_type_id == None:
            res = defect_dojo.get_first_product_type_by_name(name=app.app_name)
            if res and "id" in res: 
                prod_type_id = res["id"]

        #If prod_type and user, assign product_type to user --> Role 4 (Owner)
        if prod_type_id and user_id: defect_dojo.add_product_type_to_user(product_type_id=prod_type_id, user_id=user_id, role=4)

        #If prod_type and group, assign product_type to group --> Role 4 (Owner)
        if prod_type_id and group_id: defect_dojo.add_product_type_to_group(product_type_id=prod_type_id, group_id=group_id, role=4)
        
        #If not prod type generated, use default
        if prod_type_id == None:
            res = defect_dojo.get_first_product_type_by_name(name="default")
            if res and "id" in res: 
                prod_type_id = res["id"]
            else:
                prod_type_id = None

    return prod_type_id

def populate_dojo_product(defect_dojo: DefectDojo, app: AppModel, tech: TechModel, owner: ContactModel):
    #Obtain product from Dojo
    res = defect_dojo.get_first_product_by_name(name=app.id)
    if res and "id" in res: 
        product_id = res["id"]
    else:
        #Obtain group
        group_id = populate_dojo_group(defect_dojo=defect_dojo, owner=owner)

        #Obtain user and group
        user_id = populate_dojo_user(defect_dojo=defect_dojo, owner=owner, group_id=group_id)

        #Obtain product type
        prod_type_id = populate_dojo_product_type(defect_dojo=defect_dojo, app=app, user_id=user_id, group_id=group_id)

        #Add repo url link on dojo description
        repo_url = app.repo_url
        if not repo_url.startswith("https://"): repo_url = "https://" + repo_url
        description = "<a href='" + repo_url + "'>Repo URL</a>"

        #Tags
        tags = [tech.id, tech.group]

        #Create product on Dojo
        product_id = defect_dojo.create_product(name=app.id, description=description, prod_type_id=prod_type_id, tags=tags, external=False, user_id=user_id)

        #If product and user, assign product to user --> Role 4 (Owner)
        if product_id and user_id: defect_dojo.add_product_to_user(product_id=product_id, user_id=user_id, role=4)

        #If product and group, assign product to group --> Role 4 (Owner)
        if product_id and group_id: defect_dojo.add_product_to_group(product_id=product_id, group_id=group_id, role=4)

        #Try to obtain again the product_id if not created
        if product_id == None:
            res = defect_dojo.get_first_product_by_name(name=app.id)
            if res and "id" in res: 
                product_id = res["id"]

    return product_id
        
def populate_dojo_engagement(defect_dojo: DefectDojo, app: AppModel, scan: ScanModel, product_id: int):
    engagement_name = "Manager Scan " + str(scan.id)

    #TODO Add exception link as tracker url
    base_path_exception = "https://demoappsec.dev.srv.mercadona.com/demoappsec"
    tracker = base_path_exception + "?" + "scan=" + str(scan.id)

    #Add commit hash and branch to description
    description = "<b>Commit hash: </b>" + str(scan.commit) + "\n\n<b>Commit branch: </b>" + str(scan.branch)

    #Add repo url
    repo_url = app.repo_url
    if not repo_url.startswith("https://"): repo_url = "https://" + repo_url

    #Add client on tags
    tags = [scan.client_id]

    #If there is bulk_scan_id, add on tags
    if scan.bulk_scan_id != None: tags.append(str(scan.bulk_scan_id))

    #Create engagement on Dojo
    engagement_id = defect_dojo.create_engagement(product_id=product_id, name=engagement_name, description=description, repo_url=repo_url, tracker=tracker, tags=tags)

    return engagement_id

def populate_dojo_report(defect_dojo: DefectDojo, engine: EngineModel, engagement_id: int, result: Any):
    #Report type
    if "scan_type" in engine.config_dojo and "scan_ext" in engine.config_dojo and any(engine.config_dojo["scan_ext"] == ext.value for ext in ResultFormat):
        report_type = engine.config_dojo["scan_type"]
        report_ext = engine.config_dojo["scan_ext"]
        report_file_name = engine.id + "." + report_ext
        report_tags = [engine.id]

        if report_ext == ResultFormat.JSON.value or report_ext == ResultFormat.SARIF.value:
            report_data = bytes(json.dumps(result), encoding='utf-8')
        elif report_ext == ResultFormat.XML.value:
            report_data = bytes(result, encoding='utf-8')
        else:
            return False
        
        return defect_dojo.upload_report_to_engagement(engagement_id=engagement_id, report_type=report_type, report_data=report_data, report_file_name=report_file_name, report_tags=report_tags)
    
    #If scan_type not on config of this engine, DO NOT upload to Dojo
    else:
        return False


    
