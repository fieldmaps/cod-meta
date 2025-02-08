from io import BytesIO, StringIO

import yaml
from dict2xml import dict2xml
from fastapi import APIRouter, Response
from pandas import DataFrame, ExcelWriter

from app.utils import get_meta, process_dict, process_long, process_wide

router = APIRouter()


def get_csv(iso3: str = "") -> Response:
    meta_list = get_meta(iso3)
    meta_long = process_long(meta_list)
    file = StringIO()
    DataFrame(meta_long).to_csv(file, encoding="utf-8-sig", index=False)
    data = file.getvalue()
    return Response(content=data, media_type="text/plain")


def get_json(iso3: str = "") -> dict:
    meta_list = get_meta(iso3)
    meta_long = process_long(meta_list)
    return process_dict(meta_long, iso3)


def get_xml(iso3: str = "") -> Response:
    meta_list = get_meta(iso3)
    meta_long = process_long(meta_list)
    meta_dict = process_dict(meta_long, iso3)
    data = dict2xml({"root": meta_dict})
    return Response(content=data, media_type="application/xml")


def get_yaml(iso3: str = "") -> Response:
    meta_list = get_meta(iso3)
    meta_long = process_long(meta_list)
    meta_dict = process_dict(meta_long, iso3)
    file = StringIO()
    yaml.dump(meta_dict, file, allow_unicode=True, sort_keys=False)
    data = file.getvalue()
    if data.startswith("{}"):
        data = ""
    return Response(content=data, media_type="text/plain")


def get_xlsx(iso3: str = "") -> Response:
    meta_list = get_meta(iso3)
    meta_long = process_long(meta_list)
    meta_wide = process_wide(meta_long)
    file = BytesIO()
    with ExcelWriter(file, engine="xlsxwriter") as writer:
        for sheet_name, sheet in meta_wide.items():
            df_sheet = DataFrame(sheet)
            if sheet_name == "dataset" and not df_sheet.empty:
                df_sheet = df_sheet.pivot(
                    index="iso3",
                    columns="key",
                    values="value",
                ).reset_index()
            if sheet_name == "level" and not df_sheet.empty:
                df_sheet = df_sheet.pivot(
                    index=["iso3", "lvl"],
                    columns="key",
                    values="value",
                ).reset_index()
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
            writer.sheets[sheet_name].autofit()
    file.seek(0)
    return Response(
        file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/csv", tags=["Metadata"])
def get_csv_all() -> Response:
    return get_csv()


@router.get("/csv/{iso3}", tags=["Metadata"])
def get_csv_iso3(iso3: str) -> Response:
    return get_csv(iso3)


@router.get("/json", tags=["Metadata"])
def get_json_all() -> dict:
    return get_json()


@router.get("/json/{iso3}", tags=["Metadata"])
def get_json_iso3(iso3: str = "") -> dict:
    return get_json(iso3)


@router.get("/xml", tags=["Metadata"])
def get_xml_all() -> Response:
    return get_xml()


@router.get("/xml/{iso3}", tags=["Metadata"])
def get_xml_iso3(iso3: str = "") -> Response:
    return get_xml(iso3)


@router.get("/yaml", tags=["Metadata"])
def get_yaml_all() -> Response:
    return get_yaml()


@router.get("/yaml/{iso3}", tags=["Metadata"])
def get_yaml_iso3(iso3: str) -> Response:
    return get_yaml(iso3)


@router.get("/xlsx", tags=["Metadata"])
def get_xlsx_all() -> Response:
    return get_xlsx()


@router.get("/xlsx/{iso3}", tags=["Metadata"])
def get_xlsx_iso3(iso3: str) -> Response:
    return get_xlsx(iso3)
