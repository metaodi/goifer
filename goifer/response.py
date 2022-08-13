# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime
import re
from flatten_dict import flatten
from . import errors


class Response(object):
    def __init__(self, data_loader, xmlparser):
        self.data_loader = data_loader
        self.xmlparser = xmlparser
        self.records = []
        xml = self.data_loader.load()
        self._parse_content(xml)

    def maybe_int(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return s


class SearchResponse(Response):
    def __repr__(self):
        try:
            return f"SearcheResponse(count={self.count})"
        except AttributeError:
            return "SearchRetrieveResponse(empty)"

    def _parse_content(self, xml):
        self.index = xml.attrib["indexName"]
        self.count = self.maybe_int(xml.attrib["numHits"])
        self.query = xml.attrib["q"]
        self.maximum_records = self.maybe_int(xml.attrib["m"])
        self.start_record = self.maybe_int(xml.attrib["s"])
        self.next_start_record = self.start_record + self.maximum_records
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
        if self.next_start_record > self.count:
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

    def _tag_data(self, elem):
        if not elem:
            return None
        dict_namespaces = self._get_xmlns(elem)
        record_data = self.xmlparser.todict(
            elem, xml_attribs=True, namespaces=dict_namespaces
        )
        if not record_data:
            return None

        # check if there is only one element on the top level
        keys = list(record_data.keys())
        if len(record_data) == 1 and len(keys) > 0 and len(record_data[keys[0]]) > 0:
            record_data = record_data[keys[0]]

        record_data.pop("xmlns", None)

        def leaf_reducer(k1, k2):
            # only use key of leaf element
            if k2 == "text":
                return k1
            return k2

        try:
            record_data = flatten(record_data, reducer=leaf_reducer)
        except ValueError:
            # if the keys of the leaf elements are not unique
            # the dict will not be flattened
            pass

        record_data = self._clean_dict(record_data)

        return record_data

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
            elif isinstance(v, str):
                clean_rec[clean_k] = convert_value(v)
            else:
                clean_rec[clean_k] = v

        return clean_rec
