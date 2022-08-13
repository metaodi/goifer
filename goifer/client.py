# -*- coding: utf-8 -*-

import requests
import muzzle
import yaml
import os
from . import errors
from . import response


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Client(object):
    def __init__(self, instance, maximum_records=10, session=None, config=None):
        self.maximum_records = maximum_records
        self.session = session

        namespaces = {
            "sd": "http://www.cmiag.ch/cdws/searchDetailResponse",
        }
        self.xmlparser = muzzle.XMLParser(namespaces)

        if isinstance(config, dict):
            full_config = config
        elif isinstance(config, str):
            full_config = self._load_yaml_file(config)
        else:
            # if no config is provided, load the default config
            path = os.path.join(__location__, "..", "config.yml")
            full_config = self._load_yaml_file(path)
        try:
            self.config = full_config[instance]
        except KeyError as e:
            raise errors.ConfigError(f"Instance '{instance}' not found in config: {e}")

    def _load_yaml_file(self, path):
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def search(self, index, query, start_record=1):
        index_url = self._get_index_url(index)
        url = f"{index_url}/searchdetails"
        params = {
            "q": query,
            "l": "de-CH",
            "m": self.maximum_records,
        }

        data_loader = DataLoader(url, params, self.xmlparser, self.session)
        return response.SearchResponse(data_loader, self.xmlparser)

    def get_indexes(self):
        return list(self.config["indexes"].keys())

    def _get_index_url(self, index):
        try:
            index = self.config["indexes"][index]

            base = self.config["api_base"]
            section = index.get("section", "")
            path = index["path"]
            if section:
                url = f"{base}/{section}{path}"
            else:
                url = f"{base}{path}"
            return url
        except KeyError as e:
            raise errors.ConfigError(f"Config error: {e}")


class DataLoader(object):
    def __init__(self, url, params, xmlparser, session=None):
        if session:
            self.session = session
        else:
            self.session = requests.Session()
        self.url = url
        self.params = params
        self.xmlparser = xmlparser
        self.response = None

    def load(self, **kwargs):
        self.params.update(kwargs)
        xml = self._get_content(self.url, self.params)
        return xml

    def _get_content(self, url, params):
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.GoiferError("HTTP error: %s" % e)
        except requests.exceptions.RequestException as e:
            raise errors.GoiferError("Request error: %s" % e)
        return self.xmlparser.parse(res.content)
