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


# Chart values verified by an independent iterative psychrometric solve at
# 14.696 psia (Stull 2011 agrees within ±1 °F at each point).
@pytest.mark.parametrize(
    "db, rh, expected",
    [(75, 50, 62.6), (80, 50, 66.6), (95, 40, 75.4), (70, 60, 60.9)],
)
def test_wb_matches_chart_values(db, rh, expected):
    assert approx_wet_bulb(db, rh) == pytest.approx(expected, abs=1.0)
