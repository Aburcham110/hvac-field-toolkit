import pytest
from hvac_field_toolkit.psychrometrics import approx_wet_bulb, delta_t_airflow_note


def test_saturated_air_wb_equals_db():
    assert approx_wet_bulb(75, 100) == pytest.approx(75)


def test_wb_below_db_when_dry():
    assert approx_wet_bulb(75, 50) < 75


def test_rh_out_of_range():
    with pytest.raises(ValueError):
        approx_wet_bulb(75, 120)


def test_delta_t_notes():
    assert "Low" in delta_t_airflow_note(supply=70, return_t=75)
    assert "High" in delta_t_airflow_note(supply=45, return_t=75)
    assert "common band" in delta_t_airflow_note(supply=57, return_t=75)
