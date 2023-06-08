import pandas as pd
import pytest

from process_annotation_to_dict import process_dict


@pytest.fixture
def discrete_annotation():
    return {
        "dataset": {
            1: "ds000001",
            2: "ds000001",
            3: "ds000001",
            4: "ds000001",
        },
        "column": {1: "sex", 2: "sex", 3: "sex", 4: "sex"},
        "value": {1: "", 2: "F", 3: "M", 4: "M,"},
        "is_row": {1: True, 2: False, 3: False, 4: False},
        "description": {1: "", 2: "", 3: "", 4: ""},
        "controlled_term": {
            1: "nb:Sex",
            2: "snomed:248152002",
            3: "snomed:248153007",
            4: "snomed:248153007",
        },
        "isPartOf": {1: "", 2: "", 3: "", 4: ""},
        "Decision": {1: "keep", 2: "keep", 3: "keep", 4: "keep"},
    }


@pytest.fixture
def continuous_annotation():
    return {
        "dataset": {10: "ds000002"},
        "column": {10: "age"},
        "value": {10: ""},
        "is_row": {10: True},
        "description": {10: ""},
        "controlled_term": {10: "nb:Age"},
        "isPartOf": {10: ""},
        "Decision": {10: "keep"},
    }


@pytest.fixture
def tool_annotation():
    return {
        "dataset": {102: "ds000009"},
        "column": {102: "BIS/BAS_BAS"},
        "value": {102: ""},
        "is_row": {102: True},
        "description": {102: ""},
        "controlled_term": {102: "nb:Assessment"},
        "isPartOf": {102: "cogatlas:trm_56a9137d9dce1"},
        "Decision": {102: "keep"},
    }


def test_assessment_goes_through(discrete_annotation):
    pass
    annotated = pd.DataFrame(discrete_annotation)

    assert False


def test_we_dont_lose_existing_info():
    assert False


def test_everything_annotated_is_in():
    assert False
