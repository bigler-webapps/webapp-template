from rest_framework.exceptions import ErrorDetail

from backend.exception_handler import _flatten, _is_error_object


class TestIsErrorObject:
    def test_returns_false_for_non_dict(self):
        assert _is_error_object("string") is False
        assert _is_error_object(42) is False
        assert _is_error_object(None) is False
        assert _is_error_object([]) is False

    def test_returns_false_when_no_metadata_keys(self):
        assert _is_error_object({"field": "value"}) is False
        assert _is_error_object({"type": "error"}) is False

    def test_returns_true_for_leaf_error_object_with_code(self):
        assert _is_error_object({"code": "unique", "message": "Already exists."}) is True

    def test_returns_true_for_leaf_error_object_with_i18n_key(self):
        assert _is_error_object({"i18nKey": "error.unique"}) is True

    def test_returns_true_for_leaf_error_object_with_params(self):
        assert _is_error_object({"code": "min_value", "params": {"min_value": 0}}) is True

    def test_returns_false_when_any_value_is_list(self):
        # DRF field-error dicts always have list values — even if the key is "code",
        # this is a field name, not an error code indicator.
        assert _is_error_object({"code": ["This code already exists."]}) is False
        assert _is_error_object({"code": ["err1"], "message": ["err2"]}) is False

    def test_returns_false_for_empty_dict(self):
        assert _is_error_object({}) is False


class TestFlatten:
    def test_string_error_detail_produces_single_entry(self):
        detail = ErrorDetail("Something went wrong.", code="invalid")
        result = _flatten(detail)
        assert result == [{"field": None, "code": "invalid", "message": "Something went wrong."}]

    def test_string_error_detail_with_field(self):
        detail = ErrorDetail("Required.", code="required")
        result = _flatten(detail, field="email")
        assert result == [{"field": "email", "code": "required", "message": "Required."}]

    def test_list_of_error_details_flattens_to_multiple_entries(self):
        detail = [ErrorDetail("Too short.", code="min_length"), ErrorDetail("Invalid char.", code="invalid")]
        result = _flatten(detail, field="password")
        assert result == [
            {"field": "password", "code": "min_length", "message": "Too short."},
            {"field": "password", "code": "invalid", "message": "Invalid char."},
        ]

    def test_drf_field_error_dict_recurses_into_field_names(self):
        # DRF ValidationError detail for {"email": ["Already taken."], "code": ["Duplicate."]}
        # "code" here is a field name, NOT an error code indicator.
        detail = {
            "email": [ErrorDetail("Already taken.", code="unique")],
            "code": [ErrorDetail("Duplicate.", code="unique")],
        }
        result = _flatten(detail)
        assert len(result) == 2
        fields = {item["field"] for item in result}
        assert fields == {"email", "code"}
        assert all(item["code"] == "unique" for item in result)

    def test_leaf_error_object_is_not_recursed_into(self):
        detail = {"code": "custom_error", "message": "Something custom.", "i18nKey": "errors.custom"}
        result = _flatten(detail, field="name")
        assert len(result) == 1
        assert result[0] == {
            "field": "name",
            "code": "custom_error",
            "message": "Something custom.",
            "i18nKey": "errors.custom",
        }

    def test_leaf_error_object_omits_none_message(self):
        detail = {"code": "blank", "i18nKey": "errors.blank"}
        result = _flatten(detail)
        assert result[0].get("message") is None
        assert "message" not in result[0]

    def test_leaf_error_object_includes_params_when_present(self):
        detail = {"code": "min_value", "params": {"min_value": 1}}
        result = _flatten(detail)
        assert result[0]["params"] == {"min_value": 1}

    def test_leaf_error_object_omits_params_when_not_dict(self):
        detail = {"code": "err", "params": "not-a-dict"}
        result = _flatten(detail)
        assert "params" not in result[0]

    def test_nested_field_path_is_dot_separated(self):
        detail = {"address": {"city": [ErrorDetail("Too long.", code="max_length")]}}
        result = _flatten(detail)
        assert result == [{"field": "address.city", "code": "max_length", "message": "Too long."}]

    def test_nested_field_path_with_parent_field(self):
        detail = {"city": [ErrorDetail("Required.", code="required")]}
        result = _flatten(detail, field="address")
        assert result[0]["field"] == "address.city"

    def test_empty_dict_produces_no_entries(self):
        assert _flatten({}) == []

    def test_empty_list_produces_no_entries(self):
        assert _flatten([]) == []

    def test_plain_string_falls_back_to_error_code(self):
        result = _flatten("raw error")
        assert result == [{"field": None, "code": "error", "message": "raw error"}]
