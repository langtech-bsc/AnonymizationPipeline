#-----------------------------#
#            REGEX            #
#-----------------------------#
#REG_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
REG_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}' # We don't ask for the end of word because people forget the space after the email and keep on writing.
# Change phone regex so that it picks phones from outside Spain (i.e. make the +34 generic)
#OLD_REG_TELEPHONE = r"(\+|00)?(34)?((/[^\S\r\n]/|.)?[0-9]{2,3}\.?){3,4}"
#REG_TELEPHONE = r"\b(\+|00)?(34)?(( |\.)?[0-9]{2,3}\.?){3,4}\b" # Porblem with capturing white space before
REG_TELEPHONE = r"(?:(?<=^)|(?<=\s)|(?<=:)|(?<=\())\b(\+|00)?(34 |34)?([0-9]{2,3}(\s|\.|\.\s)?){3,4}[0-9]{1,3}\b"
REG_BANK = r"(?:(?<=^)|(?<=\s)|(?<=:))([A-Z]{2}[0-9]{2} ?)?([0-9]{4} ?){2}[0-9]{2} ?[0-9]{10}\b"
REG_BANK2 = r"(?:(?<=^)|(?<=\s)|(?<=:))[A-Z]{4} ?([A-Z]{2} ?){2}[0-9]{3}\b"
#OLD_REG_ID = r"[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}"
REG_ID_OLD = r"\b(\d{2}(\s|\.)?\d{3}(\s|\.)?\d{3}(\s|\.)?[a-zA-Z]{1}|[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}|[a-zA-Z][0-9]{7,8}[a-zA-Z]|[0-9]{2} ?[0-9]{8})\b" # NIE, DNI, CIF
REG_ID = REG_ID_OLD + "|" + r"[A-Z]{3}[0-9]{4}" + "|" + r"[-A-Z]{2} ?[0-9]{10,15}" + "|" + r"\d{8}(\s|\-)?[0-9]{2}\b" + "|" + r"[0-9]{4} ?[a-zA-Z]{3}\b" + "|" + r"[0-9]{4} ?[A-Z]{4} ?[0-9]{7}" + "|" + r"[0-9]{7}[A-Z]{2}[0-9]{4}[A-Z][0-9]{4}[A-Z]{2}" + "|" + r"\d{16}-[0-9]\b" + "|" + r"AUT(\s|-)?\d{2}(\s|-)?\d{4}(\s|-)?([A-Z]|\d)\d{4}\b" + "|" + r"\d{2}(\s|-)\d{4}[A-Z]{2}\d{5}" + "|" + r"\d{4}-\d{7}" + "|" + r"[-A-Z]{2}(\s|-)?\d{4}(\s|-)?\d(\s|-)?\d{2}(\s|-)?\d{8}" # prev + government ID + ibi identifier + Ajuntament tramit id + SMOU id + Multa id + Catastro id + Ajuntament expedient 2 + Expediente AUTORITAS + Licencia de obreas + registro de alegación + Multa tránsito
#OLD_REG_LICENSE_PLATE: r"[A-Z]{0,3}[ -]?[0-9]{4,6}[ -]?[A-Z]{0,3}"
#REG_LICENSE_PLATE = r"\b[a-zA-Z] ?-? ?[0-9]{4} ?-? ?[a-zA-Z]{3}\b"
REG_LICENSE_PLATE = r"\b((([a-zA-Z]{1,2})? ?-? ?[0-9]{4} ?-? ?[a-zA-Z]{2,3})|([a-zA-Z]{3} ?-? ?[0-9]{4}))\b" # Licence plates in Spain don't have the first letters of the EU format
#REG_CARD = r"\b(?:\d[ -]*?){13,16}\b" # Need to make sure that "AX-756956896789" doesn't partially match
#REG_CARD = r"(?:\b(^|\s))(?:\d[ -]*?){13,16}\b"
REG_CARD = r"(?:(?<=^)|(?<=\s)|(?<=:))((\d[ -]*){12,15})(\d)\b(?!-)"
REG_ZIP = r"\b[0-9]{5}\b"
