import pickle
import checksumdir


def CheckProjectHash():
    hash = checksumdir.dirhash(r"apps", 'sha256')

    with open('config/data.pickle', 'rb') as f:
        old_hash = pickle.load(f)

    if old_hash == hash:
        return True
    else:
        with open('config/data.pickle', 'wb') as f:
            pickle.dump(hash, f)
        return False

