from rest_framework.exceptions import ValidationError


def validate_file_type(file, exts) -> bool:
    """
    Function to validate file based on the extension.
    Input the file and a list of extenstions,
    return True if the file type is in the list of extensions.
    """
    for ext in exts:
        if file.name.lower().endswith(ext):
            return True
    return False


def validate_file_type_api(file, exts):
    """
    Function to validate file based on the extension.
    Input the file and a list of extenstions,
    raise Validation Error if the file type is not in the list of extensions.
    """
    if validate_file_type(file, exts):
        pass
    else:
        raise ValidationError({"file": "The file type inputted is not supported"})
