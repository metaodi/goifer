# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
import re
from flatten_dict import flatten
import muzzle
from . import errors


class Response(object):
    def __init__(self, data_loader, index, config):
        self.data_loader = data_loader
        self.index = index
        self.config = config
        self.records = []

        self.namespaces = {
            "sd": "http://www.cmiag.ch/cdws/searchDetailResponse",
            "xsd": "http://www.w3.org/2001/XMLSchema",
        }
        self.xmlparser = muzzle.XMLParser(self.namespaces)

        xml = self.data_loader.load()
        self._parse_content(xml)

    def maybe_int(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return s

    def _tag_data(self, elem):
        if not elem:
            return {}
        dict_namespaces = self._get_xmlns(elem)
        record_data = self.xmlparser.todict(
            elem, xml_attribs=True, namespaces=dict_namespaces
        )
        if not record_data:
            return {}
        record_data.pop("xmlns", None)

        record_data = self._add_download_to_docs(record_data)

        # check if there is only one element on the top level
        keys = list(record_data.keys())
        if len(record_data) == 1 and len(keys) > 0 and len(record_data[keys[0]]) > 0:
            record_data = record_data[keys[0]]

        record_data = self._flat_dict(record_data)
        return record_data

    def _add_download_to_docs(self, rec):
        new_rec = {}
        doc_pattern = re.compile("eDo(c|k)ument")
        for k, v in rec.items():
            if doc_pattern.match(k) and isinstance(v, dict):
                v["download_url"], v["FileName"] = self._get_download_url(v)
                new_rec[k] = v
            elif isinstance(v, list):
                new_rec[k] = [self._add_download_to_docs(vi) for vi in v]
            elif isinstance(v, dict):
                new_rec[k] = self._add_download_to_docs(v)
            else:
                new_rec[k] = v
        return new_rec

    def _get_download_url(self, doc):
        try:
            latest_version = doc["Version"][-1]
        except KeyError:
            latest_version = doc["Version"]
        view = latest_version["Rendition"]["Ansicht"]
        ext = latest_version["Rendition"]["Extension"]
        filename = f"{doc['FileName']}.{ext}"
        version = latest_version["Nr"]
        file_id = doc["ID"]
        index_config = self.config["indexes"][self.index]

        if "section" in index_config:
            path = f"/{index_config['section']}{self.config['files_api']['path']}"
        else:
            path = self.config["files_api"]["path"]
        url = f"{self.config['api_base']}{path}/{file_id}/{version}/{view}"
        return (url, filename)

    def _flat_dict(self, d):
        def leaf_reducer(k1, k2):
            if k1 is None or k2.lower() in k1.lower():
                return k2
            if k2 == "text":
                return k1
            return f"{k1}_{k2}"

        flat_data = flatten(d, max_flatten_depth=2, reducer=leaf_reducer)
        flat_data = self._clean_dict(flat_data)

        # make some special cases more flat
        for k in ["person_kontakt", "position", "geschaeft"]:
            if k in flat_data and isinstance(flat_data[k], list):
                flat_list = [self._flat_dict(ik) for ik in flat_data[k]]
                flat_data[k] = flat_list
            elif k in flat_data and isinstance(flat_data[k], dict):
                flat_data.update(
                    flatten(flat_data[k], max_flatten_depth=2, reducer=leaf_reducer)
                )
                del flat_data[k]

        return flat_data

    def _get_xmlns(self, elem):
        dict_namespaces = {}
        elem_dict = flatten(self.xmlparser.todict(elem, xml_attribs=True))
        for k, v in elem_dict.items():
            if "xmlns" in k and v:
                dict_namespaces[v] = None
        return dict_namespaces

    def _clean_dict(self, records):  # noqa
        # remove namespace and make everything lowercase
        def clean_name(key):
            ns_pattern = re.compile("^.+:")
            tag_name = ns_pattern.sub("", key)
            return tag_name.lower()

        def convert_value(v):
            # datetime
            try:
                new_v = datetime.fromisoformat(v)
                return new_v
            except ValueError:
                pass

            # bool
            if v.lower() == "true":
                return True
            elif v.lower() == "false":
                return False

            return v

        # replace nil/text leafs
        clean_rec = {}
        for k, v in records.items():
            if k.startswith("xmlns"):
                continue
            clean_k = clean_name(k)
            if isinstance(v, dict):
                if "nil" in v and "text" in v:
                    if v["nil"] == "true":
                        clean_rec[clean_k] = None
                        continue
                    elif v["nil"] == "false":
                        clean_rec[clean_k] = convert_value(v["text"])
                        continue
                clean_rec[clean_k] = self._clean_dict(v)
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                clean_rec[clean_k] = [self._clean_dict(vi) for vi in v]
            elif isinstance(v, str):
                clean_rec[clean_k] = convert_value(v)
            else:
                clean_rec[clean_k] = v

        return clean_rec


class SearchResponse(Response):
    def __repr__(self):
        try:
            return f"SearchResponse(index={self.index}, count={self.count}, maximum_records={self.maximum_records}, next_start_record={self.next_start_record})"
        except AttributeError:
            return "SearchResponse(empty)"

    def _parse_content(self, xml_str):
        xml = self.xmlparser.parse(xml_str)
        self.index = xml.attrib["indexName"]
        self.count = self.maybe_int(xml.attrib["numHits"])
        self.query = xml.attrib["q"]
        self.maximum_records = self.maybe_int(xml.attrib["m"])
        self.start_record = self.maybe_int(xml.attrib["s"])
        self.next_start_record = self.start_record + self.maximum_records
        if self.next_start_record > self.count:
            self.next_start_record = None
        self._extract_records(xml)

    def __length_hint__(self):
        return self.count

    def __iter__(self):
        # use while loop since self.records could grow while iterating
        i = 0
        while True:
            # load new data when near end
            if i == len(self.records):
                try:
                    self._load_new_data()
                except errors.NoMoreRecordsError:
                    break
            yield self.records[i]
            i += 1

    def __getitem__(self, key):
        if isinstance(key, slice):
            limit = max(key.start or 0, key.stop or self.count)
            self._load_new_data_until(limit)
            count = len(self.records)
            return [self.records[k] for k in range(*key.indices(count))]

        if not isinstance(key, int):
            raise TypeError("Index must be an integer or slice")

        limit = key
        if limit < 0:
            # if we get a negative index, load all data
            limit = self.count
        self._load_new_data_until(limit)
        return self.records[key]

    def _load_new_data_until(self, limit):
        while limit >= len(self.records):
            try:
                self._load_new_data()
            except errors.NoMoreRecordsError:
                break

    def _load_new_data(self):
        if self.next_start_record is None:
            raise errors.NoMoreRecordsError()
        xml = self.data_loader.load(s=self.next_start_record)
        self._parse_content(xml)

    def _extract_records(self, xml):
        new_records = []

        xml_recs = self.xmlparser.findall(xml, "./sd:Hit")
        for xml_rec in xml_recs:
            record = defaultdict()
            guid = xml_rec.attrib["Guid"]

            rec = self.xmlparser.find(xml_rec, f"./*[@OBJ_GUID = '{guid}']")
            record.update(self._tag_data(rec))

            record = dict(record)
            new_records.append(record)
        self.records.extend(new_records)


class SchemaResponse(Response):
    def __repr__(self):
        try:
            return f"SchemaResponse(index={self.index})"
        except AttributeError:
            return "SchemaResponse(empty)"

    def _parse_content(self, xml_str):
        xml = self.xmlparser.parse(xml_str)
        record = defaultdict()
        record.update(self._tag_data(xml))
        record = dict(record)
        self.records = [record]

    def __iter__(self):
        for record in self.records:
            yield record

    def __getitem__(self, key):
        if isinstance(key, slice):
            count = len(self.records)
            return [self.records[k] for k in range(*key.indices(count))]

        if not isinstance(key, int):
            raise TypeError("Index must be an integer or slice")

        return self.records[key]
