
from copy import deepcopy
import os
import requests

from flask import request

from constants import RESOURCE_LOOKUP

# We'll need to translate some rdf prefixes to long-form along the way
namespaces = {
    "gov": "https://www.gov.uk/government/organisations/"
}

def get_url_root():
    """
    What it sounds like.
    """
    return request.url_root.split("v1/")[0][:-1]


def create_resource_dict(organisation_id: str, resource_id: str):
    """
    Create a json reponse representing a single resource
    """

    resource_dict = deepcopy(RESOURCE_LOOKUP)["organisations"][organisation_id]["resources"][resource_id]

    dataset_list = []
    for dataset_id in resource_dict["related_datasets"]:
        dataset_info = create_dataset_response(organisation_id, resource_id, dataset_id)
        trig_dict = dict_from_trig(dataset_info["backend_resources"]["trig"])
        dataset_info.pop('backend_resources')
        dataset_info["self"] = {
                    "href": f'{get_url_root()}/v1/organisations/{organisation_id}/resources/{resource_id}/datasets/{dataset_id}'
                },
        dataset_list.append(dataset_info)

    # Extra bits from the trig
    return {
        "@id": resource_id,
        "landingPage": f'http:{trig_dict["dcat:landingPage"].split(":")[1]}',
        "self": {
            "href": f'{get_url_root()}/v1/organisations/{organisation_id}/resources/{resource_id}'
        },
        "related_datasets": dataset_list
    }


def dict_from_trig(trig_url: str):
    """
    Get a few metadata fields out of the trig from jenkins and insert into the csvw from
    jenkins before returning, all we're aiming for (for now) is to mock up something a bit closer to 
    what we're actually after.

    TODO: not this.
    """
    
    # Get the trig from jenkins
    r = requests.get(trig_url)

    # TODO: rdflib? maybe
    update_dict = {}
    for line in r.text.split("\n"):

        for meta_field_wanted in ["dct:title", "dct:description", "dct:issued",
            "dct:license", "dct:modified", "dct:publisher", "dct:comment",
            "rdfs:label", "dct:creator", "dcat:landingPage"]:
            if meta_field_wanted in line:
                meta_text = line.split(meta_field_wanted)[1].strip()
                meta_text = meta_text.replace("\"", "")
                if meta_text.startswith("<") and meta_text.endswith(">;"):
                    meta_text = meta_text[1:-12]

                for namespace in namespaces:
                    if meta_text.startswith(namespace):
                        meta_text = namespaces[namespace] + meta_text[len(namespace)+1:]

                if meta_text.endswith(";"):
                    meta_text = meta_text[:-1]

                # The context for the csvw is already @en, get rid of them where they crop up
                if meta_text.endswith("@en"):
                    meta_text = meta_text[:-3]

                update_dict[meta_field_wanted] = meta_text

    return update_dict


def create_dataset_response(organisation_id: str, resource_id: str, dataset_id: str):
    """
    Create a json reponse representing a single resource
    """

    resource = deepcopy(RESOURCE_LOOKUP)["organisations"][organisation_id]["resources"].get(resource_id, None)
    if not resource:
        raise ValueError(f'Cannot find resource {resource_id}')

    for resource_dataset_id, dataset_info in resource["related_datasets"].items():
        if dataset_id == resource_dataset_id:
            break
    else:
        raise ValueError(f'Cannot find dataset {dataset_id} within resource {resource_id}')

    dataset_info["@id"] = dataset_id
    csvw = {"href": f'{get_url_root()}/v1/organisations/{organisation_id}/resources/{resource_id}/datasets/{dataset_id}/csvw/latest'}
    csv = {"href": f'{get_url_root()}/v1/organisations/{organisation_id}/resources/{resource_id}/datasets/{dataset_id}/csv/latest'}
    dataset_info["mediaType"] = {
        "csvw": csvw,
        "csv": csv
    }

    # Extra bits from the trig
    try:
        trig_dict = dict_from_trig(dataset_info["backend_resources"]["trig"])
    except KeyError as err:
        raise KeyError(f'Couldn\'t find expected key ["backend_resources"]["trig"] in {dataset_info}') from err

    try:
        dataset_info["release_date"] = trig_dict["dct:modified"]
    except KeyError:
        dataset_info["release_date"] = trig_dict["dc:issued"]

    # Get rid of RDF'ism
    dataset_info["release_date"] = dataset_info["release_date"].split('^')[0]

    return dataset_info