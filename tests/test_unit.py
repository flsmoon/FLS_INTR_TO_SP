from app import get_flower_stage


def test_flower_zero():
    assert get_flower_stage(0) == "🌰"


def test_flower_one():
    assert get_flower_stage(1) == "🌱"


def test_flower_two():
    assert get_flower_stage(2) == "🌱"


def test_flower_three():
    assert get_flower_stage(3) == "🌿"


def test_flower_five():
    assert get_flower_stage(5) == "🌿"


def test_flower_six():
    assert get_flower_stage(6) == "🌸"


def test_flower_ten():
    assert get_flower_stage(10) == "🌸"


def test_flower_eleven():
    assert get_flower_stage(11) == "🌻"


def test_flower_big():
    assert get_flower_stage(50) == "🌻"
