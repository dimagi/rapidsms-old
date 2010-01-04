def site_code_from_patient_id(id):
    id = id.strip()
    if id is None or len(id)<=3:
        raise ValueError
    return id[:3]

