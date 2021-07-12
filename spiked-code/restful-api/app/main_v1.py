
import os
from copy import deepcopy

from flask import Flask, request, redirect
import requests

from helpers import create_dataset_response, dict_from_trig, create_resource_dict, get_url_root, new_latest_required
from constants import RESOURCE_LOOKUP

app = Flask(__name__)

# Return simple context
@app.route("/v1/context")
def context():
    return {
        "@context": {
            "dc": "http://purl.org/dc/terms/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "schema": "https://schema.org",
            "hydra": "http://www.w3.org/ns/hydra/core#",
            "@type": "@id" 
        },
        "href": {
                "@id": "schema:url"
            },
        "id": "schema:identifier",
        "title": "dc:title",
        "landingPage": "dcat:landingPage",
        "release_date": "dc:issued",
        "creator": "dc:creator",
        "mediaType": "dcat:mediaType",
        "related_datasets": "dc:related",
        "resources": "hydra:Collection"
    }


@app.route("/v1/organisations")
def get_organisations():
    """
    Get all organizations with sub documents
    """
    org_count = 0
    final_response_dict = {'@context': [f'{get_url_root()}/v1/context', {
      "@language": "en"
    }]}
    final_response_dict["items"] = []

    for organisation_id, org_details in deepcopy(RESOURCE_LOOKUP)["organisations"].items():
        org_count += 1

        resource_list = []
        for resource_id in org_details["resources"]:
            resource_as_dict = create_resource_dict(organisation_id, resource_id)
            resource_list.append(resource_as_dict)

        final_response_dict["items"].append({
                    "@id": organisation_id,
                    "publisher": org_details["publisher"], 
                    "title": org_details["label"],
                    "resources": resource_list,
                    "self": {
                        "href": f'{get_url_root()}/v1/organisations/{organisation_id}'
                    },
                }
            )

    final_response_dict["count"] = org_count
    return final_response_dict


@app.route("/v1/organisations/<string:organisation_id>")
def get_organisation(organisation_id: str):
    """
    Get a single organization with sub documents
    """

    org_details = deepcopy(RESOURCE_LOOKUP)["organisations"][organisation_id]

    resource_list = []
    for resource_id in org_details["resources"]:
        resource_as_dict = create_resource_dict(organisation_id, resource_id)
        resource_list.append(resource_as_dict)

    return {'@context': [f'{get_url_root()}/v1/context', {
      "@language": "en"
    }],
    "@id": organisation_id,
    "publisher": org_details["publisher"], 
    "title": org_details["label"],
    "self": {
            "href": f'{get_url_root()}/v1/organisations/{organisation_id}'
        },
    "resources": resource_list
    }


@app.route("/v1/organisations/<string:organisation_id>/resources")
def get_resources(organisation_id: str):
    """
    Get all resources with sub documents
    """
    resource_list = []
    for resource_id in deepcopy(RESOURCE_LOOKUP)["organisations"][organisation_id]["resources"]:
        resource_list.append(create_resource_dict(organisation_id, resource_id))
    
    return {
            '@context': [f'{get_url_root()}/v1/context', {
            "@language": "en"
        }],
            "count": len(resource_list),
            "items": resource_list
        }


@app.route("/v1/organisations/<string:organisation_id>/resources/<string:resource_id>")
def get_resource(organisation_id, resource_id):
    """
    Get a single resource with sub documents
    """
    resource_dict = create_resource_dict(organisation_id, resource_id)

    return {
            '@context': [f'{get_url_root()}/v1/context', {
            "@language": "en"
        }]} | resource_dict


@app.route("/v1/organisations/<string:organisation_id>/resources/<string:resource_id>/datasets")
def get_datasets(organisation_id: str, resource_id: str):
    """
    Get all datasets with sub documents
    """
    resource_dict = create_resource_dict(organisation_id, resource_id)
    datasets_list = resource_dict["related_datasets"]

    return {
            '@context': [f'{get_url_root()}/v1/context', {
            "@language": "en",
        }],
            "count": len(datasets_list),
            "items": datasets_list
    }


@app.route("/v1/organisations/<string:organisation_id>/resources/<string:resource_id>/datasets/<string:dataset_id>")
def get_dataset(organisation_id: str, resource_id: str, dataset_id: str):
    """
    Get a single datasets with sub documents
    """

    backend_resource = create_dataset_response(organisation_id, resource_id, dataset_id)
    dataset_response = {'@context': [f'{get_url_root()}/v1/context', {
      "@language": "en"}], "@id": dataset_id}

    backend_resource.pop("backend_resources")
    for k, v in backend_resource.items():
        dataset_response[k] = v

    return dataset_response


@app.route("/v1/organisations/<string:organisation_id>/resources/<string:resource_id>/datasets/<string:dataset_id>/csv/latest")
def get_csv(organisation_id: str, resource_id: str, dataset_id: str):
    """
    Redirect the csv link to the corresponding jenkins artifactß
    """
    csv_download_url = create_dataset_response(organisation_id, resource_id, dataset_id)["backend_resources"]["data"]
    return redirect(csv_download_url, code=302)


@app.route("/v1/organisations/<string:organisation_id>/resources/<string:resource_id>/datasets/<string:dataset_id>/csvw/latest")
def get_csvw(organisation_id: str, resource_id: str, dataset_id: str):
    """
    Munge the csvw and trig from the latest Jenkins job into something
    more representative of the final goals of the project.
    """

    if new_latest_required():
        # TODO - this
        pass

    backend_resource = create_dataset_response(organisation_id, resource_id, dataset_id)
    this_csvw = backend_resource["backend_resources"]["csvw"]
    this_trig = backend_resource["backend_resources"]["trig"]
    this_data = backend_resource["backend_resources"]["data"]

    # Get the latest csvw output from jenkins
    r = requests.get(this_csvw)
    if r.status_code != 200:
        raise Exception(f'Failed to get csvw at {this_csvw} with error code {r.status_code}')
    csvw = r.json()

    csvw.pop("rdf:type")
    update_dict = dict_from_trig(this_trig)

    output_csvw = {}
    output_csvw["@context"] = csvw.pop("@context")
    for k, v in update_dict.items():
        output_csvw[k.split(":")[1]] = v
    for k, v in csvw.items():
        if k == "table":
            v["url"] = this_data
        output_csvw[k] = v

    return output_csvw


@app.route("/v1/landingpage")
def resource_from_landing_page():
    """
    Takes a url parameter and returns the corresponding 
    /organisations/<string:organisation_id>/resources/<string:resource_id>/datasets/<string:dataset_id>
    response.

    Or a single message if we're unaware of any such landing page resource.
    """
    wanted_landing_page = request.args.get('url')

    # Get all resource, look for the one with the matching landingPage field
    all_orgs = get_organisations()

    for org in all_orgs["items"]:
        for resource in org["resources"]:
            if resource["landingPage"] == wanted_landing_page:
                return redirect(resource["self"]["href"], code=302)
    else:
        return f'No resource for landingPage "{wanted_landing_page}" could be identified.'


if __name__ == "__main__":
    app.run(debug=True)