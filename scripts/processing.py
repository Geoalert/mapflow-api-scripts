import argparse
import os
from json import load, loads
from pathlib import Path

import shapely
from loguru import logger

from .entities import ApiClient, Mosaic, Processing

api_client = ApiClient(
    base_url=os.getenv("BASE_URL"),
    default_headers={"Authorization": f"Basic {os.getenv('USER_TOKEN')}"},
)

processing = Processing(api_client=api_client)
mosaic = Mosaic(api_client=api_client)


def get_models_list():
    models = processing.get_wds()
    if not models:
        return

    for model in models:
        print(f"id: {model['id']}")
        print(f"name: {model['name']}")
        print(f"description: {model['description']}")
        print(
            f"options: {[block['name'] for block in model['blocks'] if block['optional']]}"
        )
        print()


def download_processing_results(args: argparse.Namespace):
    if not args.processing_id:
        logger.error('Processing "id" is not provided!')
        return

    if not args.path:
        logger.error('"path" for downloading the results is required!')
        return

    path = Path(args.path)

    if path.is_dir() or not path.suffix:
        logger.error(
            "The path to the directory has been passed, only file paths are supported"
        )
        return

    processing.download_result(path, args.processing_id)


def get_processing_status(args: argparse.Namespace):
    if not args.processing_id:
        logger.error('Processing "id" is not provided!')
        return

    _processing_response = processing.get(args.processing_id)
    if not _processing_response:
        return
    _processing = _processing_response.json()

    keys = ["id", "name", "status", "percentCompleted"]
    for key in keys:
        print(f"{key}: {_processing[key]}")
    if _processing["status"] == "FAILED":
        print("error: ", _processing["messages"])


def start_processing(args: argparse.Namespace):
    if not args.name:
        logger.error('Processing "name" is not provided')
        return

    if not args.image_id and not args.mosaic_id:
        logger.error(
            '"image-id" or "mosaic-id" is required, but nothing has been provided!'
        )
        return

    if args.mosaic_id:
        is_image = False
    else:
        is_image = True

    if not args.wd_id:
        logger.error('"wd-id" is not provided!')
        return

    if not args.options:
        blocks = None
    else:
        blocks = [
            {"name": block, "enabled": True} for block in args.options.split(", ")
        ]

    if args.geometry:
        path = Path(args.geometry)
        if not path.exists():
            logger.error(f"No such file {path}")
            return

        if path.is_dir() or not path.suffix:
            logger.error(
                "The path to the directory has been passed, only file paths are supported"
            )
            return

        with open(path) as f:
            geometry = load(f)["features"][0]["geometry"]
    else:
        if is_image:
            image = mosaic.get_image(args.image_id)
            if not image:
                return
            geometry = loads(shapely.to_geojson(shapely.from_wkt(image.json()["footprint"])))
        else:
            _mosaic = mosaic.get(args.mosaic_id)
            if not _mosaic:
                return
            geometry = loads(shapely.to_geojson(shapely.from_wkt(_mosaic.json()["footprint"])))

    processing.start(
        args.name,
        args.image_id or args.mosaic_id,
        args.wd_id,
        geometry,
        blocks,
        args.project_id,
        is_image=is_image,
    )


def main():
    parser = argparse.ArgumentParser(description="Basic operations with processings")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--mosaic-id", action="store", help='Only "mosaic-id" or "image-id" can be provided')
    group.add_argument("--image-id", action="store", help='Only "image-id" or "mosaic-id" can be provided')

    parser.add_argument("command", choices=["models", "start", "status", "download"])
    parser.add_argument("-n", "--name", action="store")
    parser.add_argument("--wd-id", action="store")
    parser.add_argument("--project-id", action="store", help="Processing will be created in the Deafault project if no other is provided")
    parser.add_argument("-o", "--options", action="store", help="[] if not provided")
    parser.add_argument("-g", "--geometry", action="store", help="Path to the geometry (AOI). If not provided - the footprint of the 'image' or 'mosaic' will be used automatically")
    parser.add_argument("--processing-id", action="store")
    parser.add_argument("-p", "--path", action="store", help="Path to download results")

    args = parser.parse_args()

    if args.command == "models":
        get_models_list()

    if args.command == "status":
        get_processing_status(args)

    if args.command == "download":
        download_processing_results(args)

    if args.command == "start":
        start_processing(args)


if __name__ == "__main__":
    main()
