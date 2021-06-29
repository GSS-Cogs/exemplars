
Will be ran as its own own demand service on google run.

Database is mongoDB via a cluster provisioned via [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).

A `organisation` Document structure

```json
{
    "id": "https://www.gov.uk/government/organisations/office-for-national-statistics ??? maybe",
    "url": "https://www.gov.uk/government/organisations/office-for-national-statistics",
    "resources": [
        "<resource_document:id:>",
        "<resource_document:id:>",
        "<resource_document:id:>"
    ]
}
```

A `resource_document` Document structure:
```json
{
    "id": "<UUID>",
    "landing_page": "www.imalandingpage.com/stuff",
    "related_datasets": [
        "<dataset_document:id>"
        "<dataset_document:id>"
        "<dataset_document:id>"
    ],
    "code_repo": {
        "provider": "github",
        "source": {
            "main.py": "<commit id of this file at last time ran>",
            "info.json": "<commit id of this file at last time ran>"
        },
        "monitor_dirs": [
            "<url to dependant dirs, i.e if a file appears in /x, run the transform>"
        ]
    }
}
```

A `datasets_document` Document structure:
```json
{
    "id": "<UUID>",
    "versions": {
        "v1": {"id": "<distribution_document:id>", "created": "<TIME>"},
        "v2": {"id": "<distribution_document:id>", "created": "<TIME>"},
        "v3": {"id": "<distribution_document:id>", "created": "<TIME>"},
        "v4": {"id": "<distribution_document:id>", "created": "<TIME>"}
    }
}
```

A `distribution_document` Document structure.
```json
{
    "id": "<UUID>",
    "csvw": "<the full csvw document we'd be serving to people>",
    "transform_id": "<transform_document:id>",
    "parent_dataset": "<datset_document:id>"
}
```

A `transform_document` Document structure.
```json
{
    "id": "<UUID>",
    "parent_dataset": "<datset_document:id>",
    "details": {
        "completed": "<bool>",
        "validated": "<bool>",
        "logs": "<url to bucket with logs from this transform>",
        "notebook": "<url to the html rendering of the notebook"
    }
}
```