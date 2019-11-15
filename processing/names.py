

author_special_cases = {
    "Jeanette Hellgren Kotaleski": ("Jeanette", "Hellgren Kotaleski"),
    "Hellgren Kotaleski J": ("Jeanette", "Hellgren Kotaleski"),
    "João Pedro Santos": ("João Pedro", "Santos"),
    "Yi Ming Lai": ("Yi Ming", "Lai"),
    "Luis Georg Romundstad": ("Luis Georg", "Romundstad"),
    "Johanna Frost Nylen": ("Johanna", "Frost Nylen"),
    "Pål Gunnar Larsson": ("Pål Gunnar", "Larsson"),
    "André Sevenius Nilsen": ("André Sevenius", "Nilsen"),
    "Gabriel Andrés Fonseca Guerra": ("Gabriel Andrés", "Fonseca Guerra"),
    "Pier Stanislao Paolucci": ("Pier Stanislao", "Paolucci"),
    "Werner Van Geit": ("Werner", "Van Geit"),
    "Sacha van Albada": ("Sacha", "van Albada"),
    "Paolo Del Giudice": ("Paolo", "Del Giudice"),
    "Ignazio De Blasi": ("Ignazio", "De Blasi"),
    "Marc de Kamps": ("Marc", "de Kamps"),
    "José Francisco Gómez González": ("José Francisco", "Gómez González"),
    "Ivilin Peev Stoianov": ("Ivilin Peev", "Stoianov"),
    "BBP-team": ("BBP", "team")
}


def resolve_name(full_name, verbose=False):
    
    if (full_name in author_special_cases):
        first_name, last_name = author_special_cases[full_name]
    elif (full_name[1:] in author_special_cases):
        first_name, last_name = author_special_cases[full_name[1:]]
    else:
        parts = full_name.strip().split(" ")
        if len(parts) == 2:
            first_name, last_name = parts
        elif len(parts) == 3 and ("." in parts[1] or len(parts[1]) == 1 or parts[1] in ("van", "de", "di", "Del", "De")):
            first_name = " ".join(parts[0:2])
            last_name = parts[2]
        else:
            first_name, last_name = None, None
            print("ERR: {}".format(full_name))
            raise Exception(str(parts))
    if last_name and verbose:
        # logger.debug("Resolved {} to {}, {}".format(full_name, last_name, first_name))
        print("Resolved {} to {}, {}".format(full_name, last_name, first_name))
        
    return first_name, last_name
