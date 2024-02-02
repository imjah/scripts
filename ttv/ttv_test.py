import ttv

def test_user_is_live():
    user = ttv.User('kapitanbombatv')
    user.fetch()

    assert user.data['isLive']

def test_user_is_not_live():
    user = ttv.User('imjah___')
    user.fetch()

    assert user.data['isLive'] == False
