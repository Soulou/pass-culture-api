from domain.music_types import music_types
from domain.show_types import show_types
from domain.types import get_formatted_event_or_thing_types
from models.offer_type import EventType
from models.pc_object import PcObject
from sandboxes.scripts.mocks.event_mocks import MOCK_ACTIVATION_DESCRIPTION, \
                                                MOCK_ACTIVATION_NAME, \
                                                MOCK_DESCRIPTIONS, \
                                                MOCK_NAMES
from sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES, \
                                               MOCK_LAST_NAMES
from utils.logger import logger
from tests.test_utils import create_product_with_event_type


EVENT_COUNTS_PER_TYPE = 7

def create_industrial_event_products():
    logger.info('create_industrial_event_products')

    event_products_by_name = {}

    event_type_dicts = [
        t for t in get_formatted_event_or_thing_types(with_activation_type=True)
        if t['type'] == 'Event'
    ]

    activation_index = 0

    for type_index in range(0, EVENT_COUNTS_PER_TYPE):

        for (event_type_dict_index, event_type_dict) in enumerate(event_type_dicts):

            mock_index = (type_index + event_type_dict_index) % len(MOCK_NAMES)
            if event_type_dict['value'] == str(EventType.ACTIVATION):
                event_name = '{} {}'.format(MOCK_ACTIVATION_NAME, activation_index)
                description = MOCK_ACTIVATION_DESCRIPTION
                activation_index += 1
            else:
                event_name = MOCK_NAMES[mock_index]
                description = MOCK_DESCRIPTIONS[mock_index]

            event_type = event_type_dict['value']

            name = "{} / {}".format(event_type_dict['value'], event_name)
            event_product = create_product_with_event_type(
                description=description,
                duration_minutes=60,
                event_name=event_name,
                event_type=event_type,
                thumb_count=0
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField in event_product.offerType['conditionalFields']:
                conditional_index = type_index + event_type_dict_index + extra_data_index
                if conditionalField in ['author', 'performer', 'speaker', 'stageDirector']:
                    mock_first_name_index = conditional_index % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = conditional_index % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = '{} {}'.format(mock_first_name, mock_last_name)
                    extraData[conditionalField] = mock_name
                elif conditionalField == "musicType":
                    music_type_index = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extraData[conditionalField] = str(music_type['code'])
                    music_sub_type_index = conditional_index % len(music_type['children'])
                    music_sub_type = music_type['children'][music_sub_type_index]
                    extraData["musicSubType"] = str(music_sub_type['code'])
                elif conditionalField == "showType":
                    show_type_index = conditional_index % len(show_types)
                    show_type = show_types[show_type_index]
                    extraData[conditionalField] = str(show_type['code'])
                    show_sub_type_index = conditional_index % len(show_type['children'])
                    show_sub_type = show_type['children'][show_sub_type_index]
                    extraData["showSubType"] = str(show_sub_type['code'])
                elif conditionalField == "visa":
                    pass
                extra_data_index += 1
            event_product.extraData = extraData

            event_products_by_name[name] = event_product

        type_index += len(event_type_dicts)

    PcObject.save(*event_products_by_name.values())

    logger.info('created {} event products'.format(len(event_products_by_name)))

    return event_products_by_name
