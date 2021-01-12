from realm.backend import BackEnd
from collections import OrderedDict

test_control_dict = OrderedDict(
    {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
)
test_output_dict = OrderedDict(
    {
        "packing_fraction": "openmc",
        "keff": "openmc",
        "num_batches": "openmc",
        "max_temp": "moltres",
    }
)


def test_extend_control_dict():
    b = BackEnd(control_dict=test_control_dict, output_dict=test_output_dict)
    ctrl_list, output_list = b.extend_control_oup_dicts(
        test_control_dict, test_output_dict
    )
    expected_ctrl_list = [
        "packing_fraction",
        "polynomial_triso_0",
        "polynomial_triso_1",
        "polynomial_triso_2",
        "polynomial_triso_3",
    ]
    expected_oup_list = ["packing_fraction", "keff", "num_batches", "max_temp"]
    assert ctrl_list == expected_ctrl_list
    assert output_list == expected_oup_list
