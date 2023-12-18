from app.validate import validate_secret_label
import pytest


@pytest.mark.parametrize(
    "dictionary, labels, error, expected",
    [
        # all empty
        ({}, {}, "", {}),
        # at least one valid label name
        (
            {},
            {"redeployable-1-namespace": "test-namespace"},
            "",
            {1: {"namespace": "test-namespace"}},
        ),
        # two valid label names
        (
            {},
            {
                "redeployable-1-namespace": "test-namespace",
                "redeployable-2-name": "test-name",
            },
            "",
            {1: {"namespace": "test-namespace"}, 2: {"name": "test-name"}},
        ),
        # add label to existing dictionary
        (
            {1: {"namespace": "test-namespace"}},
            {"redeployable-2-name": "test-name"},
            "",
            {1: {"namespace": "test-namespace"}, 2: {"name": "test-name"}},
        ),
        # does not start with redeployable
        (
            {},
            {"redeploy-1-namespace": "test-namespace"},
            "",
            {},
        ),
        # does not have 3 parts
        (
            {},
            {"redeployable-1": "test-namespace"},
            ".*Invalid redeployment label.*",
            {},
        ),
        # does not have integer as second part
        (
            {},
            {"redeployable-a-namespace": "test-namespace"},
            ".*Invalid number.*",
            {},
        ),
        # does not have valid key
        (
            {},
            {"redeployable-1-invalidkey": "test-namespace"},
            ".*Invalid redeployment key.*",
            {},
        ),
        # duplicate key
        (
            {1: {"namespace": "test-namespace"}},
            {"redeployable-1-namespace": "test-namespace"},
            ".*Duplicate redeployment key.*",
            {},
        ),
    ],
)
def test_labels_validation(
    dictionary,
    labels,
    error,
    expected,
):
    result = {}
    for label_name, label_value in labels.items():

        def validation():
            return validate_secret_label(
                label_name,
                label_value,
                dictionary,
            )

        if error:
            with pytest.raises(ValueError, match=error):
                validation()
        else:
            result.update(validation())
    if not error:
        assert result == expected
