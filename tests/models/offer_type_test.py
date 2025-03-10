from models.offer_type import ProductType, ThingType, EventType


class ProductTypeTest:
    class IsThingTest:
        def test_if_name_is_empty_return_False(self):
            # When
            is_thing = ProductType.is_thing('')

            # Then
            assert is_thing is False

        def test_if_name_is_ThingType_AUDIOVISUEL_return_True(self):
            # When
            is_thing = ProductType.is_thing(str(ThingType.AUDIOVISUEL))

            # Then
            assert is_thing is True

        def test_if_name_is_EventType_PRATIQUE_ARTISTIQUE_return_False(self):
            # When
            is_thing = ProductType.is_thing(str(EventType.PRATIQUE_ARTISTIQUE))

            # Then
            assert is_thing is False

    class IsEventTest:
        def test_if_name_is_empty_return_False(self):
            # When
            is_event = ProductType.is_event('')

            # Then
            assert is_event is False

        def test_if_name_is_EventType_MUSEES_PATRIMOINE_return_True(self):
            # When
            is_event = ProductType.is_event(str(EventType.MUSEES_PATRIMOINE))

            # Then
            assert is_event is True

        def test_if_name_is_ThingType_JEUX_VIDEO_return_False(self):
            # When
            is_event = ProductType.is_event(str(ThingType.JEUX_VIDEO))

            # Then
            assert is_event is False
