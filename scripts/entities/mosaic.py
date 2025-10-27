from pathlib import Path
from typing import Optional

from loguru import logger

from .api_client import ApiClient


class Mosaic:
    def __init__(self, api_client: ApiClient = None, id: Optional[str] = None):
        self.api_client = api_client
        self.id = id

    def get(self, mosaic_id: Optional[str] = None):
        mosaic_id = mosaic_id or self.id
        if not mosaic_id:
            logger.error('Mosaic "id" is required!')
            return None

        response = self.api_client.get(f"/rasters/mosaic/{mosaic_id}")
        if response.status_code == 200:
            logger.info("Mosaic succesfully received")
            return response
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting mosaic: {_msg}")
            return None

    def get_mosaics(self):
        response = self.api_client.get("/rasters/mosaic")
        if response.status_code == 200:
            if response.json() != []:
                logger.info("Mosaics succesfully received")
                return response
            else:
                logger.error("There are no mosaics")
                return None
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting mosaics: {_msg}")
            return None

    def get_image(self, image_id: str):
        response = self.api_client.get(f"/rasters/image/{image_id}")
        if response.status_code == 200:
            logger.info("Image succesfully received")
            return response
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting image: {_msg}")
            return None

    def get_images(self, mosaic_id: Optional[str] = None):
        mosaic_id = mosaic_id or self.id
        if not mosaic_id:
            logger.error('Mosaic "id" is required!')
            return None

        response = self.api_client.get(f"/rasters/mosaic/{mosaic_id}/image")
        if response.status_code == 200:
            if response.json() != []:
                logger.info("Images succesfully received")
                return response
            else:
                logger.error("No images in mosaic")
                return None
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting images: {_msg}")
            return None

    def create(self, name: str, tags: Optional[str] = None):
        logger.info("Creating mosaic...")
        if tags:
            _tags = tags.split(", ")
        else:
            _tags = []

        response = self.api_client.post(
            "/rasters/mosaic", json={"name": name, "tags": _tags}
        )

        if response.status_code == 200:
            logger.info(f"Successfully created mosaic {response.json()['id']}")
            return response
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when creating mosaic: {_msg}")
            return None

    def upload_image(self, image_path: Path, mosaic_id: Optional[str] = None):
        mosaic_id = mosaic_id or self.id
        if not mosaic_id:
            logger.error('Mosaic "id" is required!')
            return None

        if not image_path.exists():
            logger.error(f"No such file {image_path}")
            return None

        if image_path.suffix.lower() not in (".tif", ".tiff"):
            logger.error(
                f"Invalid file format: {image_path.suffix}. Only .tif and .tiff files are supported"
            )
            return None

        try:
            with open(image_path, "rb") as f:
                logger.info("Uploading file...")
                files = {"file": f}
                response = self.api_client.post(
                    f"/rasters/mosaic/{mosaic_id}/image", files=files
                )
        except OSError as e:
            logger.error(f"Failed to read file {image_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return None

        if response.status_code == 200:
            logger.info("Successfully uploaded image")
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when uploading image: {_msg}")

        return response

    def upload_images(self, image_paths: list[Path], mosaic_id: Optional[str] = None):
        results = {
            "total": len(image_paths),
            "successful": 0,
            "failed": 0,
            "failed_files": [],
        }

        for image_path in image_paths:
            if self.upload_image(image_path, mosaic_id):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["failed_files"].append(str(image_path))
        return results

    def find_tiff_files(self, directory: Path) -> list[Path]:
        tiff_files = []

        if not directory.exists():
            logger.error(f"No such directory {directory}")
            return None

        for ext in [".tif", ".tiff", ".TIF", ".TIFF"]:
            found_files = list(directory.glob(f"*{ext}"))
            tiff_files.extend(found_files)
        if tiff_files:
            logger.info(f"Found {len(set(tiff_files))} images")
            return sorted(set(tiff_files))
        else:
            logger.warning(f"No images in directory {str(directory)}")
        exit()
