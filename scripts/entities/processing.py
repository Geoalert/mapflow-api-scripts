from pathlib import Path
from typing import Optional

from loguru import logger

from .api_client import ApiClient


class Processing:
    def __init__(self, api_client: ApiClient = None, id: Optional[str] = None):
        self.api_client = api_client
        self.id = id

    def get(self, processing_id: Optional[str] = None):
        processing_id = processing_id or self.id
        if not processing_id:
            logger.error('Processing "id" is required!')
            return None

        response = self.api_client.get(f"/processings/{processing_id}/v2")
        if response.status_code == 200:
            logger.info("Processing succesfully received")
            return response
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting processing: {_msg}")
            return None

    def start(
        self,
        name: str,
        source_id: str,
        wd_id: str,
        geometry: dict,
        blocks: Optional[list[dict]] = None,
        project_id: Optional[str] = None,
        is_image: bool = True,
    ):

        source_params = {"imageIds": [source_id]} if is_image else {"mosaicId": source_id}

        _json = {
            "name": name,
            "projectId": project_id,
            "wdId": wd_id,
            "params": {"sourceParams": {"myImagery": source_params}},
            "blocks": blocks,
            "geometry": geometry
        }

        if not project_id:
            del _json["projectId"]

        if not blocks:
            del _json["blocks"]

        response = self.api_client.post("/processings/v2", json=_json)

        if response.status_code == 200:
            logger.info(f"Successfully created processing {response.json()['id']}")
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when creating processing: {_msg}")

        return response

    def download_result(self, destination: Path, processing_id: Optional[str] = None):
        processing_id = processing_id or self.id
        if not processing_id:
            logger.error('Processing "id" is required!')
            return False

        _processing = self.get(processing_id)

        if not _processing:
            return False

        _processing_status = _processing.json()["status"]
        if _processing_status != "OK":
            logger.warning(f"Unable to download results. Processing status is {_processing_status}")
            return False

        if not destination.parent.exists():
            logger.error(f"No such directory {destination.parent}")
            return False

        try:
            response = self.api_client.get(f"/processings/{processing_id}/result")

            if response.status_code == 200:
                logger.debug("Results successfully received")
            else:
                _msg = f"{response.status_code} {response.reason} {response.text}"
                logger.error(f"Error when getting results: {_msg}")
                return False

            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            logger.info(f"Results successfully downloaded to: {destination}")
            return True

        except Exception as e:
            logger.error(f"Error when downloading results: {e}")
            return False

    def get_wds(self):
        response = self.api_client.get("/user/status")

        if response.status_code == 200:
            logger.info("Successfully recieved user info")
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting user info: {_msg}")
            return None

        return response.json()["models"]
