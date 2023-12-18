from core.validate import validate_secret_label
import pytest


@pytest.mark.parametrize(
    "dictionary, labels, error, expected",
    [
        # all empty
        ({}, {}, "", False),
        # at least one valid label name
        (
            {},
            {"redeployable-1-namespace": "test-namespace"},
            "",
            True,
        ),
        # two valid label names
        (
            {},
            {
                "redeployable-1-namespace": "test-namespace",
                "redeployable-2-name": "test-name",
            },
            "",
            True,
        ),
        # add label to existing dictionary
        (
            {1: {"namespace": "test-namespace"}},
            {"redeployable-2-name": "test-name"},
            "",
            True,
        ),
        # does not start with redeployable
        (
            {},
            {"redeploy-1-namespace": "test-namespace"},
            "",
            False,
        ),
        # does not have 3 parts
        (
            {},
            {"redeployable-1": "test-namespace"},
            ".*Invalid redeployment label.*",
            False,
        ),
        # does not have integer as second part
        (
            {},
            {"redeployable-a-namespace": "test-namespace"},
            ".*Invalid number.*",
            False,
        ),
        # does not have valid key
        (
            {},
            {"redeployable-1-invalidkey": "test-namespace"},
            ".*Invalid redeployment key.*",
            False,
        ),
        # duplicate key
        (
            {1: {"namespace": "test-namespace"}},
            {"redeployable-1-namespace": "test-namespace"},
            ".*Duplicate redeployment key.*",
            False,
        ),
    ],
)
def test_labels_validation(
    dictionary,
    labels,
    error,
    expected,
):
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
            assert validation() == expected
