def site_code_from_patient_id(id):
    splitted = id.split('/',1)
    if len(splitted)==1:
        raise ValueError
    return splitted[0]

