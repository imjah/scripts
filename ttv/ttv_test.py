import ttv

def test_is_live():
    assert ttv.Channel('kapitanbombatv')._get_status()

def test_is_not_live():
    assert not ttv.Channel('imjah___')._get_status()

def test_channels_get_status():
    channels = ttv.Channels(['kapitanbombatv', 'imjah___']).get_status()

    assert channels[0].live
    assert channels[1].live == False
