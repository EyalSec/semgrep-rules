import tarfile


def unpack(path, dest):
    with tarfile.open(path) as tar:
        # ruleid: tarfile-extractall-without-filter
        tar.extractall(dest)


def unpack_one(path, dest, member):
    tar = tarfile.open(path, "r:gz")
    # ruleid: tarfile-extractall-without-filter
    tar.extract(member, dest)
    tar.close()


def unpack_inline(path, dest):
    # ruleid: tarfile-extractall-without-filter
    tarfile.open(path).extractall(dest)


def unpack_fully_trusted(path, dest):
    with tarfile.open(path) as tar:
        # ruleid: tarfile-extractall-without-filter
        tar.extractall(dest, filter="fully_trusted")


def unpack_safe(path, dest):
    with tarfile.open(path) as tar:
        # ok: tarfile-extractall-without-filter
        tar.extractall(dest, filter="data")


def unpack_safe_attr(path, dest):
    tar = tarfile.open(path)
    tar.extraction_filter = tarfile.data_filter
    # ok: tarfile-extractall-without-filter
    tar.extractall(dest)


def unpack_zip(path, dest):
    import zipfile
    with zipfile.ZipFile(path) as zf:
        # ok: tarfile-extractall-without-filter
        zf.extractall(dest)
