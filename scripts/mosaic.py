import argparse
import os
from pathlib import Path

from loguru import logger

from .entities import ApiClient, Mosaic

api_client = ApiClient(
    base_url=os.getenv("BASE_URL"),
    default_headers={"Authorization": f"Basic {os.getenv('USER_TOKEN')}"},
)

mosaic = Mosaic(api_client=api_client)

def create_mosaic(args: argparse.Namespace):
    if not args.name:
        logger.error('Mosaic "name" is not provided!')
        return
    mosaic.create(args.name, args.tags)


def get_mosaics():
    mosaics = mosaic.get_mosaics()
    keys = ["id", "name", "tags", "sizeInBytes"]

    if not mosaics:
        return

    for _mosaic in mosaics.json():
        for key in keys:
            print(f"{key}: {_mosaic[key]}")
        print()

def get_mosaic_images(args: argparse.Namespace):
    if not args.mosaic_id:
        logger.error('Mosaic "id" is not provided!')
        return

    images = mosaic.get_images(args.mosaic_id)
    keys = ["id", "filename", "image_url"]

    if not images:
        return

    for img in images.json():
        for key in keys:
            print(f"{key}: {img[key]}")
        print()

def upload_images(args: argparse.Namespace):
    if not args.mosaic_id:
        logger.error('Mosaic "id" is not provided!')
        return

    if not args.path:
        logger.error('"path" to image or folder with images is required!')
        return

    path = Path(args.path)

    if not path.exists():
        logger.error("No such file or directory")
        return

    if path.is_file():
        mosaic.upload_image(path, args.mosaic_id)
    else:
        print(mosaic.upload_images(mosaic.find_tiff_files(path), args.mosaic_id))


def main():
    parser = argparse.ArgumentParser(description="Basic operations with imagery mosaics")
    parser.add_argument('command', choices=['create', 'upload', 'mosaics', 'images'])
    parser.add_argument('-n', '--name', action='store')
    parser.add_argument('-t', '--tags', action='store', help='Mosaic tags with ", " separator. E.g: -t "tag1, tag2, ..."')
    parser.add_argument('-p', '--path', action='store', help='Path to the uploaded image or folder with images')
    parser.add_argument('--mosaic-id', action='store')

    args = parser.parse_args()

    if args.command == 'create':
        create_mosaic(args)

    if args.command == 'mosaics':
        get_mosaics()

    if args.command == 'images':
        get_mosaic_images(args)

    if args.command == 'upload':
        upload_images(args)


if __name__ == '__main__':
    main()
