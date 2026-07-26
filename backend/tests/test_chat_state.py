from chat import (
    apply_extracted_fields,
    canned_ack,
    canned_question,
    empty_state,
    has_pricing_inputs,
    next_missing_field,
)


def test_next_missing_field_starts_with_destination():
    assert next_missing_field(empty_state()) == "destination"


def test_next_missing_field_follows_required_order():
    state = empty_state()
    state["destination"] = "Tokyo"
    state["num_days"] = 7
    assert next_missing_field(state) == "travel_month"


def _filled_state(companions: str) -> dict:
    state = empty_state()
    state.update(
        destination="Tokyo",
        num_days=7,
        travel_month="October",
        total_budget=80000,
        interests=[{"interest": "Food", "rating": 5}],
        companions=companions,
        pace="Moderate",
    )
    return state


def test_next_missing_field_asks_child_ages_only_for_family():
    assert next_missing_field(_filled_state("Family")) == "child_ages"


def test_next_missing_field_skips_child_ages_when_not_family():
    assert next_missing_field(_filled_state("Solo")) is None


def test_has_pricing_inputs_requires_first_four_fields():
    state = empty_state()
    state["destination"] = "Tokyo"
    assert has_pricing_inputs(state) is False
    state["num_days"] = 7
    state["travel_month"] = "October"
    state["total_budget"] = 80000
    assert has_pricing_inputs(state) is True


def test_apply_extracted_fields_coerces_numeric_strings():
    updated = apply_extracted_fields(empty_state(), {"num_days": "7", "total_budget": "80000"})
    assert updated["num_days"] == 7
    assert updated["total_budget"] == 80000.0


def test_apply_extracted_fields_ignores_invalid_numeric_values():
    updated = apply_extracted_fields(empty_state(), {"num_days": "a week"})
    assert updated["num_days"] == 0


def test_apply_extracted_fields_rejects_unknown_companions_value():
    updated = apply_extracted_fields(empty_state(), {"companions": "Friends"})
    assert updated["companions"] == ""


def test_apply_extracted_fields_accepts_known_companions_value_case_insensitively():
    updated = apply_extracted_fields(empty_state(), {"companions": "family"})
    assert updated["companions"] == "Family"


def test_apply_extracted_fields_defaults_interest_rating_to_three():
    updated = apply_extracted_fields(empty_state(), {"interests": [{"interest": "Hiking"}]})
    assert updated["interests"] == [{"interest": "Hiking", "rating": 3}]


def test_apply_extracted_fields_clamps_interest_rating_to_valid_range():
    updated = apply_extracted_fields(empty_state(), {"interests": [{"interest": "Hiking", "rating": 9}]})
    assert updated["interests"] == [{"interest": "Hiking", "rating": 5}]


def test_apply_extracted_fields_ignores_unknown_keys():
    updated = apply_extracted_fields(empty_state(), {"unrelated_key": "value"})
    assert "unrelated_key" not in updated


def test_apply_extracted_fields_preserves_existing_values_not_in_patch():
    state = empty_state()
    state["destination"] = "Tokyo"
    updated = apply_extracted_fields(state, {"num_days": "7"})
    assert updated["destination"] == "Tokyo"
    assert updated["num_days"] == 7


def test_canned_ack_formats_value():
    assert canned_ack("companions", "Family") == "Got it — Family."


def test_canned_ack_falls_back_to_generic_for_unknown_field():
    assert canned_ack("dining", "Street food") == "Got it."


def test_canned_question_returns_fixed_copy():
    assert canned_question("destination") == "Where are you thinking of traveling?"
