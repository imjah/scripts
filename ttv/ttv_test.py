import ttv

def test_user_is_live():
    user = ttv.User('kapitanbombatv')

    assert user.data['isLive']

def test_user_is_not_live():
    user = ttv.User('imjah___')

    assert user.data['isLive'] == False
