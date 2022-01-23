from notion_client import Client, APIErrorCode, APIResponseError
import pandas as pd

import collections
from pprint import pprint

import os
from dotenv import load_dotenv
load_dotenv()
notion = Client(auth=os.environ["NOTION_TOKEN"])

def get_all_db_entries(db_id):
    
    has_more = True
    cursor = None

    while has_more:        
        #If first iteration with no cursor
        if cursor == None:
            db = notion.databases.query( **{ "database_id": db_id})
            cursor = db["next_cursor"]
            has_more = db["has_more"]

        else:
            more_results = notion.databases.query( **{ "database_id": db_id, "start_cursor":cursor})
            db['results'].extend(more_results['results'])
            cursor = more_results['next_cursor']
            has_more = more_results["has_more"]

    return db 

def get_notion_page_title(page_id):
    notion_page = notion.pages.retrieve(page_id)
    for key, value in notion_page["properties"].items():
        if value["id"] =="title":
            return value["title"][0]["plain_text"]


def get_notion_page_icon(page_id):
    notion_page = notion.pages.retrieve(page_id)
    if notion_page["icon"] == None:
        return None
    elif notion_page["icon"]["type"] == "emoji":
        return notion_page["icon"]["emoji"]
    else:
        return notion_page["icon"]["file"]["url"]


def serialize_notion_page_icon(icon_field_value_obj):
    if icon_field_value_obj == None:
        return ''
    elif icon_field_value_obj["type"] == "emoji":
        return icon_field_value_obj["emoji"]
    else:
        return icon_field_value_obj["file"]["url"]


def serialize_notion_page_title(page_properties):
    for key, value in page_properties.items():
        if value["id"] =="title":
            return value["title"][0]["plain_text"]


def serialize_notion_relations(relation_field_value_obj, show_icon=True):
    
    relations = []

    for relation in relation_field_value_obj["relation"]:
        icon = get_notion_page_icon(relation["id"])
        title = get_notion_page_title(relation["id"])
        #If the icon contains an image only serialize the title
        if icon == None:
            relations.append(title)
        elif "https://" in  icon and show_icon:
            relations.append(title)
        #Otherwise serialize a combination of Icon + Title
        elif show_icon:
            relations.append(icon + " " + title)
    
    return relations

def serialize_notion_multiselect(multiselect_field_value_obj):
    
    selected_options = []

    for multiselect_option in multiselect_field_value_obj["multi_select"]:
        selected_options.append(multiselect_option["name"])

    return selected_options

def serialize_notion_files(files_field_value_obj):
    
    files = []

    for file_obj in files_field_value_obj["files"]:
        if file_obj["type"] == 'external':
            files.append(file_obj["external"]["url"])
        else:
            files.append(file_obj["file"]["url"])
       
    return files


def serialize_people(people_field_value_obj):
    
    people = []

    for person_obj in people_field_value_obj["people"]:
        people.append(person_obj["name"])

    return people

#Page Object Properties parsing
def parse_page_properties(properties_obj, relations=True, show_icon=True):

    obj = {}

    #TODO
    #Missing: rollup, formula and content of page with block children

    for key, value in properties_obj.items():
        if value['type'] == "title":
            #title is extracted from the page metadata
             continue
        elif value['type'] == "rich_text":
            if len(value["rich_text"]) == 0:
                obj[key] = ''
            else:
                obj[key] = value["rich_text"][0]["plain_text"]
        elif value['type'] == "select":
                if value["select"] == None:
                    obj[key] = ''
                else:
                    obj[key] = value["select"]["name"]
        elif value['type'] == "number":
            if value["number"] == None:
                obj[key] = ''
            else:
                obj[key] = value["number"]
        elif value['type'] == "url":
            obj[key] = value["url"]
        elif value['type'] == "created_by":
            obj[key] = value["created_by"]["name"]
        elif value['type'] == "email":
            obj[key] = value["email"]
        elif value['type'] == "phone_number":
            obj[key] = value["phone_number"]
        elif value['type'] == "checkbox":
            obj[key] = value["checkbox"]
        elif value['type'] == "multi_select":
            obj[key] = serialize_notion_multiselect(value)
        elif value['type'] == "files":
            obj[key] = serialize_notion_files(value)
        elif value['type'] == "people":
            obj[key] = serialize_people(value)
        elif value['type'] == "relation" and relations:
            obj[key] = serialize_notion_relations(value, show_icon)

    return(obj)

def parse_notion_page(entry, relations=True, show_icon=True):
    serialize_page_metadata = { 
    "title" : serialize_notion_page_title(entry["properties"]),
    "icon" : serialize_notion_page_icon(entry["icon"]),
    "created_time" : entry["created_time"],
    "last_edited_time" : entry["last_edited_time"],
    "page_url":entry["url"]
    }

    #Properties, unique to any page, are more complex
    properties_serialized = parse_page_properties(entry["properties"], relations, show_icon)

    #Merge bot dictionaries into a single one
    entire_page = {**serialize_page_metadata, **properties_serialized}
    entire_page_ordered = collections.OrderedDict(entire_page)

    return entire_page_ordered

def notion_db_to_df(db_id, relations=True, show_icon=True):
    notion_db = get_all_db_entries(db_id)
    pages = []
    for result in notion_db["results"]:
        pages.append(parse_notion_page(result, relations, show_icon))
    df = pd.DataFrame(pages)
    return df

def NotionToCSV(db_id, name='notion_table',relations=True, show_icon=True):
    df= notion_db_to_df(db_id, relations, show_icon)
    path = name+'.csv'
    df.to_csv(path, index=False)
    

#Taxonomy Table: 2fbdd8aba1604e2385ed7be3a59d1984
#Concepts Table: 763f8356f41c45e3934950696f00fa21
#Movies 4870a2649b6c4d3784fc8a24196ea690
#Podcasts c1f6b77ce50a47b7b1e524c923079c17

#NotionToCSV("4870a2649b6c4d3784fc8a24196ea690")

#df = notion_db_to_df("4870a2649b6c4d3784fc8a24196ea690")
#pprint(df)