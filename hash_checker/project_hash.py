import pickle
import checksumdir


async def CheckProjectHash():
    hash = checksumdir.dirhash(r"C:\Users\b.kopanichuk\PycharmProjects\sevsed2\apps", 'sha256')

    with open('data.pickle', 'rb') as f:
        old_hash = pickle.load(f)

    print(old_hash)
    if old_hash == hash:
        return True
    else:
        with open('data.pickle', 'wb') as f:
            pickle.dump(hash, f)
        return False

