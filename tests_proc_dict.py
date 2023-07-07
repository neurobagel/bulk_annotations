import json

import pandas as pd
import pytest

from process_annotation_to_dict import process_dict, get_transform_heuristic, describe_continuous, load_annotations, main


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
def participant_annotation():
    return {
        "dataset": {10: "ds000002"},
        "column": {10: "participant_id"},
        "type": {10: "str"},
        "value": {10: ""},
        "is_row": {10: True},
        "description": {10: ""},
        "controlled_term": {10: "nb:ParticipantID"},
        "isPartOf": {10: ""},
        "Decision": {10: "keep"},
    }


@pytest.fixture
def continuous_annotation():
    return {
        "dataset": {10: "ds000002"},
        "column": {10: "age"},
        "type": {10: "float64"},
        "value": {10: ""},
        "is_row": {10: True},
        "description": {10: ""},
        "controlled_term": {10: "nb:Age"},
        "isPartOf": {10: ""},
        "Decision": {10: "keep"},
    }



@pytest.fixture
def missing_file(tmp_path):
    header = "\t".join(["dataset", "column", "type", "value", "is_row", "description", "controlled_term", "isPartOf", "Decision"])
    row1 = "\t".join(["ds000002", "sex", "object", "n/a", "True", "", "nb:Sex", "", "keep"])
    row2 = "\t".join(["ds000002", "sex", "n/a", "nan", "False", "", "nb:MissingValue", "", "keep"])
    row3 = "\t".join(["ds000002", "sex", "n/a", "m", "False", "", "snomed:248153007", "", "keep"])
    with open(tmp_path / "missing.tsv", "w") as f:
        f.write("\n".join([header, row1, row2, row3]))

    return tmp_path / "missing.tsv"


@pytest.fixture
def tool_annotation():
    return {
        "dataset": {102: "ds000009"},
        "column": {102: "tool1"},
        "value": {102: ""},
        "is_row": {102: True},
        "description": {102: ""},
        "controlled_term": {102: "nb:Assessment"},
        "isPartOf": {102: "cogatlas:trm_56a9137d9dce1"},
        "Decision": {102: "keep"},
    }


@pytest.fixture
def drop_annotation(continuous_annotation):
    continuous_annotation.update(**{"Decision": {10: "drop"}})
    return continuous_annotation


@pytest.fixture
def user_dict():
    return {
        "age": {"Description": "age of the participant", "Units": "years"},
        "sex": {
            "Description": "gender of the participant",
            "Levels": {"M": "male", "F": "female"},
        },
    }


def test_original_data_unchanged_when_no_annotation(
    drop_annotation, user_dict
):
    """Dropped annotations should not be added to the generated data dictionary"""
    data = pd.DataFrame(drop_annotation)
    result = process_dict(data, user_dict)
    assert result == user_dict


def test_original_data_augmented_by_annotation(
    continuous_annotation, user_dict
):
    data = pd.DataFrame(continuous_annotation)
    result = process_dict(data, user_dict)

    assert result.get("age", {}).get("Annotations") is not None
    assert result.get("sex") is not None


def test_good_continuous_has_transformation(continuous_annotation, user_dict):
    data = pd.DataFrame(continuous_annotation)
    result = process_dict(data, user_dict)

    assert (
        result.get("age").get("Annotations").get("Transformation") is not None
    )


def test_bad_continuous_lacks_transformation(continuous_annotation, user_dict):
    continuous_annotation.update(**{"type": {10: "nonsense_heuristic"}})
    data = pd.DataFrame(
        continuous_annotation
    )
    result = process_dict(data, user_dict)

    assert result.get("age").get("Annotations") is None


def test_describe_continuous(continuous_annotation):
    result = describe_continuous(pd.DataFrame(continuous_annotation))
    assert result == {"Annotations": {
        "IsAbout": {
            "TermURL": "nb:Age",
            "Label": "",
        },
        "Transformation": {
            "TermURL": "nb:float",
            "Label": "float data",
            },
    }}


def test_partof_annotation_is_processed(tool_annotation, user_dict):
    data = pd.DataFrame(tool_annotation)
    result = process_dict(data, user_dict)

    assert result.get("tool1") is not None
    assert (
        result.get("tool1").get("Annotations", {}).get("IsPartOf") is not None
    )


@pytest.mark.parametrize(
    "annotation,expected",
    [
        ({"type": {10: "float64"}}, "nb:float"),
        ({"type": {10: "int64"}}, "nb:int"),
        ({"type": {10: "nb:bounded"}}, "nb:bounded"),
        ({"type": {10: "nb:euro"}}, "nb:euro"),
    ],
)
def test_get_transform_heuristic(annotation, expected, continuous_annotation):
    continuous_annotation.update(**annotation)
    df = pd.DataFrame(continuous_annotation)
    result = get_transform_heuristic(df)
    assert result[0] == expected
    
    
def test_participant_id_column_goes_through(participant_annotation, user_dict):
    df = pd.DataFrame(participant_annotation)
    result = process_dict(df, user_dict)
    assert result.get("participant_id") is not None
    assert result.get("participant_id").get("Annotations") is not None
    assert result.get("participant_id").get("Annotations").get("Identifies") is not None


def test_nan_is_read_as_string(missing_file):
    result = load_annotations(missing_file)
    assert result.isPartOf[0] == ""
    assert result.value[0] == "n/a"
    assert result.type[0] == "object"


def test_missing_value_is_parsed_correctly(missing_file, tmp_path):
    """
    Ensure that values annotated with nb:MissingValue end up in "MissingValues"
    and are not treated like normal controlled term mappings (i.e. end up in "Levels")
    """
    out_path = tmp_path / "ds000002.json"
    main(missing_file, tmp_path)
    result = json.loads(out_path.read_text())
    
    annotations = result["sex"]["Annotations"]
    
    assert "m" in annotations["Levels"]
    assert "nan" not in annotations["Levels"]
    assert "nan" in annotations["MissingValues"]