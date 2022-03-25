#-----------------------------#
#            REGEX            #
#-----------------------------#
REG_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# Change phone regex so that it picks phones from outside Spain (i.e. make the +34 generic)
#OLD_REG_TELEPHONE = r"(\+|00)?(34)?((/[^\S\r\n]/|.)?[0-9]{2,3}\.?){3,4}"
REG_TELEPHONE = r"\b(\+|00)?(34)?(( |\.)?[0-9]{2,3}\.?){3,4}\b"
REG_BANK = r"([A-Z]{2}[0-9]{2} ?)?([0-9]{4} ?){2}[0-9]{2} ?[0-9]{10}"
REG_BANK2 = r"[A-Z]{4} ?([A-Z]{2} ?){2}[0-9]{3}"
#OLD_REG_ID = r"[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}"
REG_ID = r"[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}|[a-zA-Z][0-9]{7,8}[a-zA-Z]|[0-9]{2} ?[0-9]{8}"
#OLD_REG_LICENSE_PLATE: r"[A-Z]{0,3}[ -]?[0-9]{4,6}[ -]?[A-Z]{0,3}"
REG_LICENSE_PLATE = r"[a-zA-Z] ?-? ?[0-9]{4} ?-? ?[a-zA-Z]{3}"
REG_CARD = r"\b(?:\d[ -]*?){13,16}\b"
REG_ZIP = r"\b[0-9]{5}\b"
