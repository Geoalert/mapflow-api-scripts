# Mapflow CLI Tool

A command-line interface for managing imagery mosaics (collections) and AI-powered image processing operations. This tool allows you to create mosaics, upload imagery, and run AI model processing on satellite and aerial imagery through the Mapflow-API.

## Installation

**IMPORTANT**

> `python 3.11+` is required!

1. Create and activate virtual environment

```bash
python -m venv .venv
```
```bash
.venv/bin/activate  # On Windows: .venv\Scripts\activate
```
2. Install the project dependencies from `requirements.txt`

```bash
pip install -r requirements.txt
```
3. Use the `.env.template`  file as an example to create the `.env` in the same directory with **BASE_URL** and Whitemaps API **USER_TOKEN**

## Usage

### Mosaic operations

```
python -m scripts.mosaic COMMAND {create,upload,images} [-h] [-n NAME] [-t TAGS] [-p PATH] [--mosaic-id MOSAIC_ID]
```
`COMMAND`:
- `create` - Creates a mosaic with the specified **name** `-n` and **tags** `-t`
- `upload` - Uploads the **specified** `-p` **image** or all images from the **directory** to the specified **mosaic** `--mosaic-id`
- `mosaics` - Displays a list of all the mosaics available to user
- `images` - Displays a list of all the images in the **mosaic** `--mosaic-id`

`Arguments`:
- `-h` - Help
- `-n` - Mosaic name
- `-t` - Mosaic tags
- `-p` - Path to the uploaded image or directory with .tif images
- `--mosaic-id` - Mosaic id

#### Examples

Mosaic creation

```bash
python -m scripts.mosaic create -n "mosaic_name" -t "tag1, tag2, ..."
```

Single image uploading

```bash
python -m scripts.mosaic upload -p "/path/to/single/image.tif" --mosaic-id "UUID"
```

Bulk uploading of images from the specified directory

```bash
python -m scripts.mosaic upload -p "/path/to/directory/with/images" --mosaic-id "UUID"
```

Get list of all mosaics

```bash
python -m scripts.mosaic mosaics
```

Get list of all images in mosaic

```bash
python -m scripts.mosaic images --mosaic-id "UUID"
```
### Project operations

```
python -m scripts.project COMMAND {create,projects,processings} [-h] [-n NAME] [-d DESCRIPTION] [--project-id PROJECT_ID]
```
`COMMAND`:
- `create` - Creates a project with the specified **name** `-n` and **description** `-d`
- `projects` - Displays a list of all the projects available to user
- `processings` - Displays a list of all the processings in the **project** `--project-id`

`Arguments`:
- `-h` - Help
- `-n` - Project name
- `-d` - Project description
- `--project-id` - Project id

#### Examples

Project creation

```bash
python -m scripts.project create -n "project_name" -d "project_description"
```

Get list of all projects

```bash
python -m scripts.project projects
```

Get list of all processings in project

```bash
python -m scripts.project processings --project-id "UUID"
```

### Processing operations

```
python -m scripts.processing COMMAND {models,start,status,download} [-h] [--mosaic-id MOSAIC_ID | --image-id IMAGE_ID] [-n NAME] [--wd-id WD_ID] [--project-id PROJECT_ID] [-o OPTIONS] [-g GEOMETRY] [--processing-id PROCESSING_ID] [-p PATH]
```
`COMMAND`:
- `models` - Displays a list of all the models available to user
- `start` - Starts a processing with the specified:
    - **name** `-n`, **image/mosaic** `--image/mosaic-id` (only one of these can be passed),
    - AI **model** id `--wd-id`,
    - case-sensitive, comma-separated **options** `-o` for the selected model (None if not passed),
    - **project** `--project-id` where the processing will be stored (Default will be used automatically if other is not passed),
    - Path to the **geometry** `-g` (AOI). If not provided - the footprint of the 'image' or 'mosaic' will be used automatically.
- `status` - Shows the status and completion percentage for a given **processing** `--processing-id`
- `download` - Downloads .geojson **processing** `--processing-id` results to the **specified** `-p` path

`Arguments`:
- `-h` - Help
- `-n` - Processing name
- `--image-id` - Image id
- `--mosaic-id` - Mosaic id
- `--wd-id` - AI model id
- `-o` - Model options
- `--project-id` - Project id
- `-g` - Path to .geojson processing geometry (AOI)
- `-p` - Path for downloading the processing results

### Examples

Get list of models

```bash
python -m scripts.processing models
```

Full arguments processing start

```bash
python -m scripts.processing start -n "processing_name" --image-id "UUID" --wd-id "UUID" --project-id "UUID" -o "Classification, Simplification, ..." -g "/path/to/geometry/aoi.geojson"
```
Quick processing start

```bash
python -m scripts.processing start -n "processing_name" --mosaic-id "UUID" --wd-id "UUID"
```

Download the processing results

```bash
python -m scripts.processing download -p "/path/to/future/file/results.geojson" --processing-id "UUID"
```
Get processing status

```bash
python -m scripts.processing status --processing-id "UUID"
```