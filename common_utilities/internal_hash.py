import hashlib


def create_internal_hash(object_id, email):
    hash = hashlib.sha1(f"{object_id}{email}".encode("UTF-8")).hexdigest()
    return hash[:10]