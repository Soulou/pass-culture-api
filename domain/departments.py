from typing import List

from models import User

DEPARTEMENT_CODE_VISIBILITY = {
    '08': ['02', '08', '51', '55', '59'],
    '25': ['21', '25', '39', '67', '68', '70', '71', '90'],
    '29': ['22', '35', '29', '56'],
    '34': ['11', '12', '13', '30', '31', '34', '48', '66', '81', '84'],
    '35': ['22', '29', '35', '44', '49', '50', '53', '56'],
    '58': ['03', '18', '21', '45', '58', '71', '89'],
    '67': ['54', '55', '57', '67', '68', '88'],
    '71': ['01', '03', '21', '39', '42', '58', '69', '71'],
    '84': ['04', '07', '13', '26', '30', '83', '84'],
    '93': ['75', '77', '78', '91', '92', '93', '94', '95'],
    '94': ['75', '77', '78', '91', '92', '93', '94', '95'],
    '97': ['97', '971', '972', '973'],
}
ILE_DE_FRANCE_DEPT_CODES = ['75', '78', '91', '94', '93', '95']


def get_departement_codes_from_user(user: User) -> List[str]:
    if user.departementCode[:2] in DEPARTEMENT_CODE_VISIBILITY:
        return DEPARTEMENT_CODE_VISIBILITY[user.departementCode[:2]]
    else:
        return [user.departementCode]
